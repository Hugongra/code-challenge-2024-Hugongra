import os
import json
import hashlib
import time
import random

# Ensure this path points to the correct directory containing your transaction JSON files
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

def read_transactions():
    transactions = []
    if not os.path.exists(mempool_dir) or not os.path.isdir(mempool_dir):
        print(f"Directory {mempool_dir} does not exist or is not a directory.")
        return transactions
    for filename in os.listdir(mempool_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(mempool_dir, filename)
            with open(file_path, 'r') as f:
                try:
                    transaction = json.load(f)
                    transactions.append(transaction)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file {filename}")
    print(f"Read {len(transactions)} transactions.")
    return transactions

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
            print("All outputs must have positive values.")
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

def calculate_txid(transaction):
    transaction_string = json.dumps(transaction, sort_keys=True)
    return hashlib.sha256(hashlib.sha256(transaction_string.encode()).digest()).hexdigest()

MAX_BLOCK_SIZE = 1000000  # Simplified maximum block size in bytes (actual Bitcoin block size limit is 1 MB)

def calculate_fee(transaction):
    total_input = sum(input["prevout"]["value"] for input in transaction["vin"])
    total_output = sum(output["value"] for output in transaction["vout"])
    return total_input - total_output

def calculate_transaction_size(transaction):
    # Simplified transaction size estimation based on the JSON string length
    # In reality, transaction size is determined by its serialized form in bytes
    transaction_string = json.dumps(transaction)
    return len(transaction_string.encode('utf-8'))

def select_transactions(transactions):
    # Calculate fees and sizes for all transactions
    for tx in transactions:
        tx["fee"] = calculate_fee(tx)
        tx["size"] = calculate_transaction_size(tx)

    transactions.sort(key=lambda tx: tx["fee"] / tx["size"], reverse=True)

    selected_transactions = []
    block_size = 0
    total_fee_collected = 0  # Track total fee collected from selected transactions
    for tx in transactions:
        if block_size + tx["size"] <= MAX_BLOCK_SIZE:
            selected_transactions.append(tx)
            block_size += tx["size"]
            total_fee_collected += tx["fee"]  # Accumulate fees
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

def mine_block(transactions, previous_block_hash, timestamp):
    version = 1
    tx_hashes = [tx['txid'] for tx in transactions]
    merkle_root = calculate_merkle_root(tx_hashes)
    difficulty_target = "0000ffff00000000000000000000000000000000000000000000000000000000"
    nonce = 0

    while True:
        # Use the create_block_header function to make the header
        block_header = create_block_header(version, previous_block_hash, merkle_root, timestamp, nonce,
                                           difficulty_target)

        # Convert block header dictionary to a string for hashing, mirroring the previous structure for consistency
        block_header_str = f"{block_header['version']:08x}{block_header['prev_block_hash']}{block_header['merkle_root']}{block_header['timestamp']:08x}{block_header['nonce']:08x}"
        block_hash = hashlib.sha256(hashlib.sha256(block_header_str.encode()).digest()).hexdigest()

        if int(block_hash, 16) < int(difficulty_target, 16):
            print(f"Block mined! Nonce: {nonce}, Hash: {block_hash}")
            # Return the JSON formatted block header and hash for better integration with other parts of the program
            return json.dumps(block_header), block_hash
        nonce += 1

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
    transactions = read_transactions()
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
    # Assuming you have updated the `write_output` function to accept and process the `block_subsidy`,
    # you would need to calculate or define `block_subsidy` before passing it to `write_output`.
    # For simplicity, let's assume it's predefined or calculated elsewhere in your script.
    block_subsidy = 6.25  # This is an example; you'll need to calculate this based on the actual block height
    write_output(block_header, coinbase_transaction, selected_transactions, total_fee_collected,
                 block_subsidy)  # Adjusted to include block subsidy

if __name__ == "__main__":
    main()

