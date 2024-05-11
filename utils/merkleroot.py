import hashlib

def merkle_root(ser_txids):
    # Compute Merkle root hash using the extracted txids
    if len(ser_txids) == 0:
        return None

    while len(ser_txids) > 1:
        next_level = []
        # Pair and hash the txids
        for i in range(0, len(ser_txids), 2):
            if i + 1 < len(ser_txids):  # Ensure we have pairs
                hash_pair = hash2(ser_txids[i], ser_txids[i+1])
            else:  # If odd number of txids, hash with itself
                hash_pair = hash2(ser_txids[i], ser_txids[i])
            next_level.append(hash_pair)
        ser_txids = next_level  # Update txids to next level
    
    return ser_txids[0] if ser_txids else None

def hash2(a, b):
    # Reverse inputs before and after hashing due to endian issues
    a1 = bytes.fromhex(a)[::-1]
    b1 = bytes.fromhex(b)[::-1]
    concat_bytes = a1 + b1
    first_hash = hashlib.sha256(concat_bytes).digest()
    second_hash = hashlib.sha256(first_hash).digest()
    final_hash_hex = second_hash[::-1].hex()
    
    return final_hash_hex