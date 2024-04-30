import os
import json
import hashlib
import time
import random
from ecdsa import VerifyingKey, SECP256k1, BadSignatureError, util

mempool_dir = 'mempool'

previous_block_hash = '0' * 64
block_height = 1
timestamp_variation = random.randint(-3600, 3600)
current_time = int(time.time()) + timestamp_variation

def double_sha256(hex_str):
    return hashlib.sha256(hashlib.sha256(bytes.fromhex(hex_str)).digest()).hexdigest()

def calculate_merkle_root(tx_hashes):

    if len(tx_hashes) == 1:
        return tx_hashes[0]
    if len(tx_hashes) % 2 == 1:
        tx_hashes.append(tx_hashes[-1])
    parent_level = []
    for i in range(0, len(tx_hashes), 2):
        parent_hash = double_sha256(tx_hashes[i] + tx_hashes[i + 1])
        parent_level.append(parent_hash)
    return calculate_merkle_root(parent_level)

def calculate_txid(transaction):
    transaction_string = json.dumps(transaction, sort_keys=True)
    return hashlib.sha256(hashlib.sha256(transaction_string.encode()).digest()).hexdigest()

def receive_transactions():
    new_transactions = mempool_dir  # Placeholder function
    for transaction in new_transactions:
        if verify_segwit_transaction(transaction):
            mempool_dir.append(transaction)  # Assuming mempool is a list of transactions

def validate_transaction(transaction):
    # Check for required fields in the transaction
    required_fields = ["vin", "vout", "version", "locktime"]
    if not all(field in transaction for field in required_fields):
        print("Missing required fields in transaction.")
        return False

    # Check for at least one input and one output
    if not transaction["vin"] or not transaction["vout"]:
        print("Transaction must have at least one input and one output.")
        return False

    # Check for positive values in all outputs
    for output in transaction["vout"]:
        if output["value"] <= 0:
            return False

    # Check for the presence of necessary script fields in inputs and outputs
    for input_tx in transaction["vin"]:
        if "scriptsig" not in input_tx or "txid" not in input_tx or "vout" not in input_tx:
            print("Inputs must contain 'scriptsig', 'txid', and 'vout'.")
            return False

    for output in transaction["vout"]:
        if "scriptpubkey" not in output:
            print("Outputs must contain 'scriptpubkey'.")
            return False
    return True

def calculate_fee(transaction):
    total_input = sum(input["prevout"]["value"] for input in transaction["vin"])
    total_output = sum(output["value"] for output in transaction["vout"])
    return total_input - total_output


def select_transactions_for_block(mempool):
    # Filter to get only valid transactions
    valid_transactions = [tx for tx in mempool if verify_segwit_transaction(tx)]

    # Use your existing function to select transactions based on fee and size
    selected_transactions, total_fee_collected = select_transactions(valid_transactions)
    return selected_transactions, total_fee_collected

MAX_BLOCK_SIZE = 4000000  # Simplified maximum block weight in weight units (actual Bitcoin block size limit is 4 MB in weight units)

def calculate_total_bytes(tx):
    # Serialize the transaction to a JSON string
    serialized_tx = json.dumps(tx, separators=(',', ':'))

    # Return the length of the serialized transaction as the total bytes
    return len(serialized_tx.encode('utf-8'))

def calculate_vsize(tx):
    if 'is_segwit' in tx and tx['is_segwit']:
        # Assuming 'non_witness_bytes' are calculated and available in the transaction dict
        # total_bytes now comes from the serialized transaction length
        non_witness_bytes = len(json.dumps(tx, separators=(',', ':')).encode('utf-8')) - len(json.dumps(tx['vin'][0]['witness'], separators=(',', ':')).encode('utf-8'))
        witness_bytes = len(json.dumps(tx['vin'][0]['witness'], separators=(',', ':')).encode('utf-8'))
        transaction_weight = (non_witness_bytes * 4) + witness_bytes
        return (transaction_weight + 3) // 4  # Uses integer division to round up
    else:
        return calculate_total_bytes(tx)

def select_transactions(transactions):
    # Set the total_bytes for each transaction using the total_bytes calculation
    for tx in transactions:
        tx['total_bytes'] = calculate_total_bytes(tx)
        tx['fee'] = calculate_fee(tx)
        tx['vsize'] = calculate_vsize(tx)

    # Sort transactions by fee rate per vsize, not physical size, for efficiency
    transactions.sort(key=lambda tx: tx['fee'] / tx['vsize'], reverse=True)

    selected_transactions = []
    block_weight = 0
    total_fee_collected = 0

    for tx in transactions:
        if block_weight + tx['vsize'] * 4 <= MAX_BLOCK_SIZE:
            selected_transactions.append(tx)
            block_weight += tx['vsize'] * 4
            total_fee_collected += tx['fee']
        else:
            break

    return selected_transactions, total_fee_collected

def create_block_header(version, previous_block_hash, merkle_root, timestamp, nonce, target):
    return {
        "version": version,
        "prev_block_hash": previous_block_hash,
        "merkle_root": merkle_root,
        "timestamp": timestamp,
        "target": target,
        "nonce": nonce
    }

def create_coinbase_transaction(block_height, total_fee_collected):
    # Calculate the current block subsidy based on halving events
    # Halving occurs every 210,000 blocks, starting with a subsidy of 50 bitcoins
    subsidy = 50 / (2 ** (block_height // 210000))
    # The coinbase transaction awards the miner the subsidy plus the total fees collected from other transactions
    total_reward = subsidy + total_fee_collected
    coinbase_tx = {
        "inputs": [{"block_height": block_height}],
        "outputs": [{"value": total_reward}],
    }
    coinbase_tx['txid'] = calculate_txid(coinbase_tx)
    return coinbase_tx

def prepare_data_to_sign(transaction, vin):
    # This function recreates the data that was signed, excluding the witness information.
    tx_copy = json.loads(json.dumps(transaction))  # Deep copy the transaction

    # Clear scriptSig and witness data of all inputs
    for inp in tx_copy['vin']:
        inp['scriptsig'] = ''
        inp['witness'] = []

    # Include the scriptPubKey in the scriptSig of the input being signed
    vin_index = transaction['vin'].index(vin)
    tx_copy['vin'][vin_index]['scriptsig'] = vin['prevout']['scriptpubkey']

    # Serialize the transaction data for signing
    data_to_sign = json.dumps(tx_copy, sort_keys=True).encode('utf-8')
    return data_to_sign

def read_transactions(mempool_dir):
    transactions = []
    valid_transactions = []
    invalid_count = 0  # Counter for invalid transactions
    total_count = 0   # Counter for total transactions attempted to read

    if not os.path.exists(mempool_dir) or not os.path.isdir(mempool_dir):
        print(f"Directory {mempool_dir} does not exist or is not a directory.")
        return transactions  # This should possibly return valid_transactions for consistency

    for filename in os.listdir(mempool_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(mempool_dir, filename)
            with open(file_path, 'r') as f:
                total_count += 1
                try:
                    transaction = json.load(f)
                    # Correct: Verify each transaction individually
                    if verify_segwit_transaction(transaction):
                        valid_transactions.append(transaction)
                    else:
                        invalid_count += 1
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {filename}")
                    invalid_count += 1  # Count decoding errors as invalid transactions

    # Reporting results
    valid_count = len(valid_transactions)
    total_transactions = total_count
    if total_transactions > 0:
        valid_percentage = (valid_count / total_transactions) * 100
        invalid_percentage = (invalid_count / total_transactions) * 100
        print(f"Valid transactions: {valid_percentage:.2f}%")
        print(f"Invalid transactions: {invalid_percentage:.2f}%")
    else:
        print("No transactions processed.")

    print(f"Read {valid_count} valid transactions.")
    return valid_transactions

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError, util
from ecdsa.errors import MalformedPointError

def verify_segwit_transaction(transaction):
    try:
        # Check if 'vin' key exists in the transaction dictionary
        if 'vin' not in transaction:
            print("Transaction does not contain 'vin' key.")
            return False

        for vin in transaction["vin"]:
            if 'witness' in vin and len(vin['witness']) == 2:
                public_key_hex = vin['witness'][1]
                signature_hex = vin['witness'][0]

                try:
                    public_key_bytes = bytes.fromhex(public_key_hex)
                    signature_bytes = bytes.fromhex(signature_hex[:-2])  # Remove the hash type suffix
                    print(f"Public Key: {public_key_hex}, Length: {len(public_key_bytes)}")  # Diagnostic print
                except ValueError as e:
                    print(f"Hexadecimal encoding error: {e}")
                    return False

                data_to_sign = prepare_data_to_sign(transaction, vin)

                try:
                    vk = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
                except MalformedPointError as e:
                    print(f"Malformed public key: {e}, Key: {public_key_hex}")
                    return False

                if not vk.verify(signature_bytes, data_to_sign, hashfunc=hashlib.sha256, sigdecode=util.sigdecode_der):
                    print("Signature verification failed")
                    return False
        return True
    except BadSignatureError:
        print("Signature verification failed with BadSignatureError")
        return False


def mine_block(transactions, previous_block_hash, timestamp):
    version = 1
    # Validate transactions before mining
    valid_transactions = [tx for tx in transactions if verify_segwit_transaction(tx)]
    tx_hashes = [tx['txid'] for tx in valid_transactions]
    merkle_root = calculate_merkle_root(tx_hashes)
    difficulty_target = "0000ffff00000000000000000000000000000000000000000000000000000000"
    nonce = 0

    while True:
        # Use the create_block_header function to make the header
        block_header = create_block_header(version, previous_block_hash, merkle_root, timestamp, nonce, difficulty_target)

        # Convert block header dictionary to a string for hashing
        block_header_str = f"{block_header['version']:08x}{block_header['prev_block_hash']}{block_header['merkle_root']}{block_header['timestamp']:08x}{block_header['nonce']:08x}"
        block_hash = hashlib.sha256(hashlib.sha256(block_header_str.encode()).digest()).hexdigest()

        if int(block_hash, 16) < int(difficulty_target, 16):
            print(f"Block mined! Nonce: {nonce}, Hash: {block_hash}")
            # Return the JSON formatted block header and hash for better integration with other parts of the program
            return json.dumps(block_header), block_hash
        nonce += 1

# Assuming calculate_merkle_root and create_block_header are defined elsewhere in your script
def write_output(block_header, coinbase_transaction, transactions, total_fee_collected, block_subsidy):
    try:
        with open('output.txt', 'w') as f:
            f.write("Block Header:\n")
            f.write(block_header + '\n\n')

            f.write("Serialized Coinbase Transaction:\n")
            serialized_coinbase_tx = json.dumps(coinbase_transaction, indent=4)
            f.write(serialized_coinbase_tx + '\n\n')

            f.write("Transaction IDs (txids) of the transactions mined in the block:\n")
            for tx in transactions[1:]:  # Skipping the first transaction as it is the coinbase transaction
                f.write(tx['txid'] + '\n')

            # Report total fee collected
            f.write(f"\nTotal Fee Collected: {total_fee_collected} satoshis\n")

            # Now, let's include the block subsidy in the output file
            f.write(f"Block Subsidy: {block_subsidy} BTC\n")

            # Calculate the total miner's reward (block subsidy + total fees)
            total_miners_reward = block_subsidy + total_fee_collected / 100000000  # converting satoshis to BTC
            f.write(f"Total Miner's Reward: {total_miners_reward} BTC\n")

        print("Output with block details and miner's reward written to output.txt")
    except Exception as e:
        print(f"Failed to write output: {e}")

def main():
    transactions = read_transactions(mempool_dir)
    if not transactions:
        print("No transactions to process. Exiting.")
        return

    valid_transactions = [tx for tx in transactions if validate_transaction(tx)]
    for tx in valid_transactions:
        tx['txid'] = calculate_txid(tx)

    selected_transactions, total_fee_collected = select_transactions(valid_transactions)
    if not selected_transactions:
        print("No transactions were selected for the block. Exiting.")
        return

    # Pass the `total_fee_collected` as an argument to `create_coinbase_transaction`
    coinbase_transaction = create_coinbase_transaction(block_height, total_fee_collected)
    coinbase_transaction['txid'] = calculate_txid(coinbase_transaction)

    selected_transactions.insert(0, coinbase_transaction)
    block_header, _ = mine_block(selected_transactions, previous_block_hash, current_time)
   
    block_subsidy = 3.125  
    write_output(block_header, coinbase_transaction, selected_transactions, total_fee_collected,
                 block_subsidy)  # Adjusted to include block subsidy

if __name__ == "__main__":
    main()

