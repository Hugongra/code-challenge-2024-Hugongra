import hashlib

def little_endian_bytes(value, length):
    return value.to_bytes(length, byteorder='little')

def varint_encode(value):
    if value < 0xfd:
        return value.to_bytes(1, 'little')
    elif value <= 0xffff:
        return b'\xfd' + value.to_bytes(2, 'little')
    elif value <= 0xffffffff:
        return b'\xfe' + value.to_bytes(4, 'little')
    else:
        return b'\xff' + value.to_bytes(8, 'little')

def serialize_transaction(transactions):
  txid_array = []
  rev_txid_array = []
  for transaction in transactions:
    version = transaction['version']
    locktime = transaction['locktime']
    inputs = transaction['vin']
    outputs = transaction['vout']

    # Start building the transaction byte array
    tx_data = (
        little_endian_bytes(version, 4) +
        varint_encode(len(inputs))
    )

    # Process each input
    for input in inputs:
        txid = bytes.fromhex(input['txid'])[::-1]  # Reverse txid for little-endian
        prev_tx_out_index = input['vout']
        scriptsig = bytes.fromhex(input['scriptsig'])
        sequence = input['sequence']

        # Append txid, prev_tx_out_index, scriptsig
        tx_data += (
            txid +
            little_endian_bytes(prev_tx_out_index, 4) +
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

    # Calculate wtxid (hash of tx_data with marker and flag)
    tx_data += little_endian_bytes(locktime, 4)
    ser_tx_hash = hashlib.sha256(hashlib.sha256(tx_data).digest()).digest()
    txid_array.append(ser_tx_hash.hex())
    rev_txid_array.append(ser_tx_hash[::-1].hex())

  return txid_array, rev_txid_array, tx_data.hex(), ser_tx_hash[::-1].hex()


def wit_serialize_transaction(transactions):
  wtxid_array = ['0000000000000000000000000000000000000000000000000000000000000000']
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
        prev_tx_out_index = input['vout']
        scriptsig = bytes.fromhex(input['scriptsig'])
        sequence = input['sequence']

        # Append txid, prev_tx_out_index, scriptsig
        tx_data += (
            txid +
            little_endian_bytes(prev_tx_out_index, 4) +
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

    wtxid_array.append(wtxid_hash[::-1].hex())

  return wtxid_array, tx_data.hex(), wtxid_hash.hex(), wtxid_hash[::-1].hex()