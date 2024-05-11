def calculate_transaction_fees(transaction):
    inputs = transaction.get('vin', [])
    outputs = transaction.get('vout', [])

    total_input_value = sum(input.get('prevout', {}).get('value', 0) for input in inputs)

    total_output_value = sum(output.get('value', 0) for output in outputs)

    fee = total_input_value - total_output_value
  
    return fee