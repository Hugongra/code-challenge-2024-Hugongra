import hashlib

def calculate_block_header(version, prev_block_hash, merkle_root, timestamp, bits, nonce):
    block_header = version + prev_block_hash + merkle_root + timestamp + bits + nonce
    return block_header

def calculate_block_hash(block_header):
    try:

        blockhash = hashlib.sha256(hashlib.sha256(bytes.fromhex(block_header)).digest()).digest()
        # Return the hash 
        return blockhash
    except Exception as e:
        print(f"Error calculating block hash: {str(e)}")
        return None