import hashlib

def satoshis_to_hex(amount_satoshis):
    hex_amount = format(amount_satoshis, '016x')  # 16 characters for 64-bit (8 bytes) little-endian format
    hex_amount_le = ''.join(reversed([hex_amount[i:i+2] for i in range(0, len(hex_amount), 2)]))
    return hex_amount_le

def compute_witness_commitment(witness_root_hash):

    reserved_value = "0000000000000000000000000000000000000000000000000000000000000000"
    # Convert witness root hash and reserved value to bytes
    witness_root_hash_bytes = bytes.fromhex(witness_root_hash)
    reserved_value_bytes = bytes.fromhex(reserved_value)

    # Concatenate witness root hash and reserved value
    concatenated_data = witness_root_hash_bytes + reserved_value_bytes

    # Perform SHA-256 hashing twice (SHA-256d)
    sha256_hash = hashlib.sha256(concatenated_data).digest()
    sha256d_hash = hashlib.sha256(sha256_hash).digest()

    # Derive the wTXID commitment (hexadecimal representation)
    wtxid_commitment = sha256d_hash.hex()  # Reverse bytes for little-endian

    return wtxid_commitment

def create_coinbase(wTXID_commit, coinbase_fees):
     '''
       def serialize_coinbase(transactions):
 for transaction in transactions:
    version = transaction['version']
    locktime = transaction['locktime']
    inputs = transaction['vin']
    outputs = transaction['vout']

    tx_data = (
        little_endian_bytes(version, 4) 
    )

    has_witness = any('witness' in vin for vin in inputs)
    if has_witness :
     tx_data += bytes.fromhex('00')
     tx_data += bytes.fromhex('01')
    # Process each input

    tx_data += varint_encode(len(inputs))
    for input in inputs:
        txid = bytes.fromhex(input['txid'])[::-1]  # Reverse txid for little-endian
        prev_tx_out_index = bytes.fromhex(input['vout'])
        scriptsig = bytes.fromhex(input['scriptsig'])
        sequence = input['sequence']

        # Append txid, prev_tx_out_index, scriptsig
        tx_data += (
            txid +
            prev_tx_out_index +
            varint_encode(len(scriptsig)) +
            scriptsig +
            little_endian_bytes(sequence, 4)
        )

    # Output count
    tx_data += varint_encode(len(outputs))

    # Process each output
    for output in outputs:
        value = output['value']
        script_pubkey = bytes.fromhex(output['scriptpubkey'])

        # Append output value, script_pubkey
        tx_data += (
            little_endian_bytes(value, 8) +
            varint_encode(len(script_pubkey)) +
            script_pubkey
        )
    
    if has_witness:
        for input in inputs:
            if 'witness' in input:
                witness = input['witness']
                tx_data += varint_encode(len(witness))
                for witness_item in input['witness']:
                    tx_data += varint_encode(len(bytes.fromhex(witness_item)))  # Length of witness item
                    tx_data += bytes.fromhex(witness_item)


    # Calculate wtxid (hash of tx_data with marker and flag)
    tx_data += little_endian_bytes(locktime, 4)
    wtxid_hash = hashlib.sha256(hashlib.sha256(tx_data).digest()).digest()

 
 return tx_data.hex(), wtxid_hash[::-1].hex()
     '''
     serialize_coinbase = f"010000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff2503233708184d696e656420627920416e74506f6f6c373946205b8160a4256c0000946e0100ffffffff02{coinbase_fees}1976a914edf10a7fac6b32e24daa5305c723f3de58db1bc888ac0000000000000000266a24aa21a9ed{wTXID_commit}0120000000000000000000000000000000000000000000000000000000000000000000000000"
     return serialize_coinbase