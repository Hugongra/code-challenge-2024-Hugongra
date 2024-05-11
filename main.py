import os
import json
from ecdsa import VerifyingKey, SECP256k1
import hashlib
import binascii
import time
import sys

from utils.header import calculate_block_header, calculate_block_hash
from utils.coinbase import compute_witness_commitment, create_coinbase, satoshis_to_hex
from utils.weight import trim_transactions
from utils.serialize import serialize_transaction, wit_serialize_transaction
from utils.merkleroot import merkle_root



MAX_BLOCK_SIZE_BYTES = 1000000
# Path to mempool folder containing transaction files
MEMPOOL_FOLDER = "./mempool"

PUBLIC_KEYS_DIR = "./public_keys"




def load_public_key(address):
    """ Load public key from file based on address """
    filename = os.path.join(PUBLIC_KEYS_DIR, f"{address}.pub")
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as file:
        public_key_hex = file.read().strip()
        return VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)


def convert_timestamp_to_hex(timestamp):
    # Convert the timestamp integer to a little-endian hexadecimal format (4 bytes)
    timestamp_hex = timestamp.to_bytes(4, byteorder='little', signed=False).hex()
    return timestamp_hex

def convert_version_to_hex(version):
    # Convert version string to an integer
    version_int = int(version)

    # Convert integer to little-endian byte representation (4 bytes)
    version_bytes = version_int.to_bytes(4, byteorder='little', signed=False)

    # Convert byte sequence to hexadecimal string (little-endian format)
    version_hex = version_bytes.hex()

    return version_hex

def convert_bits_to_hex(bits):
    # Convert bits field to hexadecimal format (reverse byte order)
    # Extract precision and shift information
    precision = int(bits[-6:], 16)
    shift = int(bits[:2], 16)

    # Construct the new bits value in desired format
    new_bits = f"{precision:06x}{shift:02x}"

    return new_bits




def validate_transaction(transaction):
    try:
        # Check transaction structure
        if not transaction.get('vin') or not transaction.get('vout'):
            return False
        
        vin = transaction.get('vin', [])
        vout = transaction.get('vout', [])
        total_input_value = 0
        total_output_value = 0
        spent_outputs = set()  # Set to track spent outputs
        
        transaction_size_bytes = sys.getsizeof(json.dumps(transaction))

        # Check transaction size against MAX_BLOCK_SIZE_BYTES
        if transaction_size_bytes > MAX_BLOCK_SIZE_BYTES or transaction_size_bytes < 100:
            return False
        
        # Validate each input (vin)
        for input in vin:
            if input.get('hash') == '0' and input.get('N') == -1:
                return False  # Reject coinbase transactions
            
            txid = input['txid']
            vout_index = input['vout']
            prevout = input.get('prevout', {})
            scriptpubkey_type = prevout.get('scriptpubkey_type', '')
            scriptpubkey_address = prevout.get('scriptpubkey_address', '')
            input_value = prevout.get('value', 0)
            
            # Ensure 'txid' is present in the input
            if 'txid' not in input:
                return False
            # Check for double spend (already spent outputs)
            if (txid, vout_index) in spent_outputs:
                return False
            
            # Validate input based on scriptpubkey type
            if scriptpubkey_type not in ['v1_p2tr', 'v0_p2wpkh', 'p2sh', 'p2pkh', 'p2wsh']:
                return False
            
            # Calculate total input value
            total_input_value += input_value
            
            # Mark the input's previous output as spent
            spent_outputs.add((txid, vout_index))
            # Additional validation rules based on scriptpubkey type can be added here
            
            # Verify signature (if applicable)
            if scriptpubkey_type == 'p2pkh' or scriptpubkey_type == 'p2wpkh':
                signature = input.get('signature', '')
                public_key = load_public_key(scriptpubkey_address)
                if not public_key:
                    return False
                if not public_key.verify(signature, bytes.fromhex(input['txid'])):
                    return False
            
            # Validate output based on scriptpubkey type
            if scriptpubkey_type == 'v1_p2tr':
                # Validation logic for v1_p2tr (Taproot) outputs
                # Specific validation rules for Taproot outputs (v1_p2tr) can be added here
                pass
            
            elif scriptpubkey_type == 'v0_p2wpkh':
                # Validation logic for v0_p2wpkh (SegWit) outputs
                if not scriptpubkey_address.startswith('bc1'):
                    return False
                if input_value <= 0:
                    return False
            
            elif scriptpubkey_type == 'p2sh':
                # Validation logic for p2sh (Pay to Script Hash) outputs
                # Specific validation rules for P2SH outputs can be added here
                pass
            
            
            elif scriptpubkey_type == 'p2pkh':
                # Validation logic for p2pkh (Pay to Public Key Hash) outputs
                if not scriptpubkey_address.startswith('1'):
                    return False
                if input_value <= 0:
                    return False
            
            elif scriptpubkey_type == 'p2wsh':
                # Validation logic for p2wsh (SegWit) outputs
                if not scriptpubkey_address.startswith('bc1'):
                    return False
                if input_value <= 0:
                    return False
                
        # Validate each output (vout)
        for output in vout:
            scriptpubkey_type = output.get('scriptpubkey_type', '')
            scriptpubkey_address = output.get('scriptpubkey_address', '')
            output_value = output.get('value', 0)
            
            # Validate output based on scriptpubkey type
            if scriptpubkey_type not in ['v1_p2tr', 'v0_p2wpkh', 'p2sh', 'p2pkh', 'p2wsh']:
                return False
            
            # Calculate total output value
            total_output_value += output_value

            # Check input-output balance condition
            if total_input_value < total_output_value:
             return False
            
            # Validate output based on scriptpubkey type
            if scriptpubkey_type == 'v1_p2tr':
                # Validation logic for v1_p2tr (Taproot) outputs
                # Specific validation rules for Taproot outputs (v1_p2tr) can be added here
                pass
            
            elif scriptpubkey_type == 'v0_p2wpkh':
                # Validation logic for v0_p2wpkh (SegWit) outputs
                if not scriptpubkey_address.startswith('bc1'):
                    return False
                if output_value <= 0:
                    return False
            
            elif scriptpubkey_type == 'p2sh':
                # Validation logic for p2sh (Pay to Script Hash) outputs
                # Specific validation rules for P2SH outputs can be added here
                pass
            
            
            elif scriptpubkey_type == 'p2pkh':
                # Validation logic for p2pkh (Pay to Public Key Hash) outputs
                if not scriptpubkey_address.startswith('1'):
                    return False
                if output_value <= 0:
                    return False
            
            elif scriptpubkey_type == 'p2wsh':
                # Validation logic for p2wsh (SegWit) outputs
                if not scriptpubkey_address.startswith('bc1'):
                    return False
                if output_value <= 0:
                    return False
            # Additional validation rules based on scriptpubkey type can be added here
        
        return True  # Transaction is valid if all checks pass
    
    except Exception as e:
        print(f"Error validating transaction: {str(e)}")
        return False

def write_transaction_ids(output_file, trxn_ids):
    for trxn_id in trxn_ids:
            output_file.write(f"{trxn_id}\n")


def reverse_byte_order(hex_string):
    # Convert the hexadecimal string to bytes
    byte_sequence = bytes.fromhex(hex_string)

    # Reverse the byte order
    reversed_byte_sequence = byte_sequence[::-1]

    # Convert the reversed byte sequence back to hexadecimal
    reversed_hex_string = reversed_byte_sequence.hex()

    return reversed_hex_string


    
    
def mine_block(txids, prev_block_hash, difficulty_target, merkle_root, ser_coinbase_trxn):
   # Convert version and bits to hexadecimal format
    version_hex = "00000004"
    bits = "ffff001f"
    timestamp = int(time.time())  # Current Unix timestamp
    timestamp_hex = timestamp.to_bytes(4, byteorder='little').hex()
    nonce = 0

    while True:
        nonce_hex = nonce.to_bytes(4, byteorder='little', signed=False).hex()

        # Construct the block header
        block_header = calculate_block_header(version_hex, prev_block_hash, merkle_root, timestamp_hex, bits, nonce_hex)
    
        # Calculate the block hash
        block_hash = calculate_block_hash(block_header)
         # Check if the block hash meets the difficulty target
        if int.from_bytes(block_hash[::-1], byteorder='big') < int(difficulty_target, 16):
            print(f"Block mined! Nonce: {nonce}")

            # Write block header, serialized coinbase transaction, and txids to output file
            with open('output.txt', 'w') as output_file:
                output_file.write(block_header + '\n')
                output_file.write(ser_coinbase_trxn + '\n')
                write_transaction_ids(output_file, txids)  # Write transaction IDs to output file
            return block_header, block_hash[::-1].hex()

        # Increment the nonce and try again
        nonce += 1
def main():
    transactions = []

    try:
        # Read all transaction files from mempool folder
        for filename in os.listdir(MEMPOOL_FOLDER):
            with open(os.path.join(MEMPOOL_FOLDER, filename), 'r') as file:
                transaction_data = json.load(file)
                transactions.append(transaction_data)
        
        print(f"Number of transactions read from mempool: {len(transactions)}")


        # Filter transactions to include only those with valid 'vin' and 'txid'
        valid_transactions = [tx for tx in transactions if validate_transaction(tx)]
        print(f"Number of valid transactions read from mempool: {len(valid_transactions)}")
        
        max_total_weight = 3200000  # Maximum cumulative weight allowed (4 million weight units)

        # Trim transactions to meet the weight constraint
        selected_transactions, total_weight, total_fees = trim_transactions(valid_transactions, max_total_weight)
        print(f"Total Cumulative Weight: {total_weight}")
        block_trxns = []
        for transaction, weight in selected_transactions:
          block_trxns.append(transaction)

        
        print(f"Number of valid transactions in block: {len(block_trxns)}")

        txids, rev_trxn_ids, ser_trxn, ser_tx_id = serialize_transaction(block_trxns)
        rev_wtxids, ser_wit_trxn, wtxid, rev_wtxid = wit_serialize_transaction(block_trxns)
        print(f"{len(rev_wtxids)}")
        wit_hash = reverse_byte_order(merkle_root(rev_wtxids))
        print(f"{wit_hash}")
        wit_commitment = compute_witness_commitment(wit_hash)
        print(f"{wit_commitment}")
        coinbase_fees = total_fees + 315000000
        coinbase_fees_hex = satoshis_to_hex(coinbase_fees)
        ser_coinbase_trxn = create_coinbase(wit_commitment, coinbase_fees_hex)

        rev_ser_coinbase_trxn_id = hashlib.sha256(hashlib.sha256(bytes.fromhex(ser_coinbase_trxn)).digest()).digest()[::-1].hex()
        rev_trxn_ids.insert(0, rev_ser_coinbase_trxn_id)

        
        calc_merkle_root = merkle_root(rev_trxn_ids)
        print(f"mekle root:{calc_merkle_root}")
        nat_order_merkle_root = reverse_byte_order(calc_merkle_root)
        print(f"nat mekle root:{nat_order_merkle_root}")
        # Placeholder values for previous block hash and difficulty target
        prev_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        difficulty_target = "0000ffff00000000000000000000000000000000000000000000000000000000"
        
        # Mine the block using transactions from the mempool
        block_header, block_hash = mine_block(rev_trxn_ids, prev_block_hash, difficulty_target, nat_order_merkle_root, ser_coinbase_trxn)


        print(f"Block Header: {block_header}")
        print(f"Block Hash: {block_hash}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
