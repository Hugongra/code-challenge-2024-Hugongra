from .fees import calculate_transaction_fees

def calculate_base_size(transaction):
    base_size = 8  # version (4 bytes) + locktime (4 bytes)

    # Calculate size for each input
    for vin in transaction['vin']:
        base_size += 32  # txid (32 bytes)
        base_size += 4   # vout (4 bytes)

        # Calculate ScriptSig length
        script_sig_length = len(vin.get('scriptsig', '')) // 2  # Convert hex string length to bytes
        base_size += script_sig_length + 1  # scriptsig length (1 byte) + scriptSig length

        base_size += 4   # sequence (4 bytes)

    # Calculate size for each output
    for vout in transaction['vout']:
        base_size += 8   # value (8 bytes)
        base_size += 1   # scriptpubkey length (1 byte)
        base_size += len(vout['scriptpubkey']) // 2  # scriptpubkey length (variable)

    return base_size

def calculate_total_size(transaction):
    total_size = 0

    # Add witness data size for SegWit transactions
    for vin in transaction['vin']:
        if 'witness' in vin and vin['witness']:
            # Include witness marker (1 byte) and flag (1 byte)
            total_size += 2
            # Add witness stack size
            total_size += len(vin['witness']) * 64  # Assuming witness stack items are 64 bytes each

    return total_size

def calculate_transaction_weight(transaction):
    base_size = calculate_base_size(transaction)
    total_size = calculate_total_size(transaction)

    weight = 4 * base_size + total_size
    return weight

def calculate_transaction_weights(transactions):
  transaction_weights = []
  for transaction in transactions:
    weight = calculate_transaction_weight(transaction)
    transaction_weights.append((transaction, weight))
  
  transaction_weights.sort(key=lambda x: x[1])
  return transaction_weights

def trim_transactions(transactions, max_weight):
    sorted_transaction_weights = calculate_transaction_weights(transactions)
    selected_transactions = []
    current_weight = 0
    Total_fees=0

    for transaction, weight in sorted_transaction_weights:
        fee = calculate_transaction_fees(transaction)
        if current_weight + weight <= max_weight:
            selected_transactions.append((transaction, weight))
            current_weight += weight
            Total_fees += fee
        else:
            break

    return selected_transactions, current_weight, Total_fees