# Solution for Summer of Bitcoin 2024 Challenge

## Introduction

Welcome to the documentation for the "Summer of Bitcoin 2024: Mine your first block" challenge. This challenge is designed to simulate the process of mining a Bitcoin block, emphasizing the validation and inclusion of transactions into a newly mined block. The task requires processing a set of transactions, validating their legitimacy, and constructing a valid block that adheres to Bitcoin's mining constraints.

The core challenge lies in the meticulous simulation of the mining process, from selecting the right transactions out of a pool (mempool), validating transaction integrity, constructing a block header, to performing the proof-of-work necessary to mine a block. The aim is to produce an output that mirrors the real-world process miners undertake to extend the blockchain with a new block.

This document (`SOLUTION.md`) is intended to provide a comprehensive overview of the approach, design decisions, and technical details that underpin the mining simulation implemented in this repository.

## Challenge Overview

In this exercise, the simulation revolves around processing transactions contained within JSON files in a directory named `mempool`. These transactions vary in validity, and it is incumbent upon the mining script to filter out invalid transactions effectively. The successful execution of the script results in the creation of an `output.txt` file that includes the block header, the serialized coinbase transaction, and the transaction IDs of the processed transactions, with the coinbase transaction ID leading the sequence.

### Objectives

The objectives of this script are as follows:

- **Validation**: To sift through the `mempool` and validate transactions based on predefined criteria.
- **Block Construction**: To assemble a valid block by including only the legitimate transactions.
- **Mining Simulation**: To implement the proof-of-work algorithm and mine the block with a hash that is less than the specified difficulty target.
- **Output Generation**: To produce a correctly formatted `output.txt` file that encapsulates the results of the mining process.

## Solution

Ensure that you have a directory containing valid transaction JSON files. The default directory is set to mempool.
Run the script using the following command: `python main.py`

The script will read the transactions from the specified directory, validate them, select transactions for the block, create a coinbase transaction, mine the block, and write the output to a file named output.txt.
Check the output.txt file for the block details, including the block header, serialized coinbase transaction, transaction IDs, total fee collected, block subsidy, and total miner's reward.

### Imports and Global Variables

- **Modules Imported**:
  - `os`, `json`, `hashlib`, `time`, `random`: Standard Python modules for file operations, data serialization, cryptographic functions, and time manipulation.
  - `ecdsa`: Used for cryptographic operations related to blockchain transactions.

- **Global Variables**:
  - `mempool_dir`: String representing the directory holding pending transactions.
  - `previous_block_hash`: String initialized with sixty-four zeros, representing the hash of the previous block.
  - `block_height`: Integer starting at 1, indicating the current block height.
  - `timestamp_variation`: Integer, random time variation to simulate real block times.
  - `current_time`: Adjusted current UNIX timestamp including the `timestamp_variation`.

### Functions

#### `double_sha256(hex_str)`
Calculates the double SHA-256 hash of a hexadecimal string.
- **Parameters**:
  - `hex_str (str)`: Hexadecimal string to hash.
- **Returns**:
  - The double SHA-256 hash as a string.

#### `calculate_merkle_root(tx_hashes)`
Computes the Merkle root from a list of transaction hashes.
- **Parameters**:
  - `tx_hashes (list)`: List of transaction hashes.
- **Returns**:
  - The Merkle root hash as a string.

#### `calculate_txid(transaction)`
Generates a transaction ID from the transaction details.
- **Parameters**:
  - `transaction (dict)`: Dictionary with transaction details.
- **Returns**:
  - Transaction ID as a string.

#### `receive_transactions()`
Simulates the receiving of new transactions. Assumes transactions are validated.
- **Details**:
  - Iterates through transactions, appending valid ones to `mempool_dir`.

#### `validate_transaction(transaction)`
Validates a transaction based on Bitcoin's required transaction fields.
- **Parameters**:
  - `transaction (dict)`: The transaction to validate.
- **Returns**:
  - `True` if valid, `False` otherwise.

#### `calculate_fee(transaction)`
Calculates the fee of a transaction.
- **Parameters**:
  - `transaction (dict)`: Transaction for which to calculate the fee.
- **Returns**:
  - Fee as an integer.

#### `select_transactions_for_block(mempool)`
Selects transactions for block inclusion.
- **Parameters**:
  - `mempool (list)`: List of transactions.
- **Returns**:
  - Tuple containing selected transactions and total fee collected.

### New Constant
- `MAX_BLOCK_SIZE`: Set to 4,000,000 weight units, this simplified maximum block weight simulates the actual Bitcoin block size limit which is also measured in weight units.

### Extended Functions

#### `calculate_total_bytes(tx)`
Calculates the total byte size of a serialized transaction.
- **Parameters**:
  - `tx (dict)`: The transaction to be serialized.
- **Returns**:
  - The total byte count of the serialized transaction.

#### `calculate_vsize(tx)`
Calculates the virtual size (vsize) of a transaction, accounting for the SegWit discount which affects transaction fees and block space efficiency.
- **Parameters**:
  - `tx (dict)`: The transaction for which the vsize is calculated.
- **Returns**:
  - The virtual size of the transaction.

#### `select_transactions(transactions)`
Selects transactions for inclusion in a block based on fee rate per vsize, optimizing for block space and fee maximization.
- **Parameters**:
  - `transactions (list)`: A list of transactions to select from.
- **Returns**:
  - A tuple containing the list of selected transactions and the total fee collected.

#### `create_block_header(version, previous_block_hash, merkle_root, timestamp, nonce, target)`
Creates the block header with necessary details for the block validation process in blockchain networks.
- **Parameters**:
  - Various parameters such as `version`, `previous_block_hash`, `merkle_root`, `timestamp`, `nonce`, and `target` which are essential for the block's identity and linkage.
- **Returns**:
  - A dictionary representing the block header.

#### `create_coinbase_transaction(block_height, total_fee_collected)`
Generates the coinbase transaction which includes the mining reward (block subsidy plus fees).
- **Parameters**:
  - `block_height (int)`: Current block height used to calculate the subsidy based on halving events.
  - `total_fee_collected (float)`: Total fees collected from the transactions included in the block.
- **Returns**:
  - The coinbase transaction as a dictionary.

#### `prepare_data_to_sign(transaction, vin)`
Prepares the specific data to be signed for a transaction, excluding witness information which is crucial for implementing SegWit.
- **Parameters**:
  - `transaction (dict)`: The original transaction data.
  - `vin (dict)`: The input of the transaction to be signed.
- **Returns**:
  - The data ready to be signed as a byte string.
    
### Function `read_transactions(mempool_dir)`
Reads and validates transactions from a specified directory containing transaction files in JSON format.
- **Parameters**:
  - `mempool_dir (str)`: The directory containing the transaction files.
- **Returns**:
  - A list of validated transactions.
- **Description**:
  - This function attempts to read transaction data from `.json` files in the specified directory. It validates each transaction using `verify_segwit_transaction` and accumulates valid transactions. The function also handles JSON decoding errors and reports on the validity and total count of transactions processed.

### Function `verify_segwit_transaction(transaction)`
Verifies if a transaction complies with Segregated Witness (SegWit) rules.
- **Parameters**:
  - `transaction (dict)`: The transaction data to verify.
- **Returns**:
  - `True` if the transaction is valid under SegWit rules, otherwise `False`.
- **Description**:
  - This function checks the presence and format of the `vin` key for witness data. It validates the digital signature using ECDSA with the SECP256k1 curve and ensures the public key and signature are correctly formatted and valid.

### Function `mine_block(transactions, previous_block_hash, timestamp)`
Attempts to mine a block using a proof-of-work algorithm.
- **Parameters**:
  - `transactions (list)`: A list of valid transactions.
  - `previous_block_hash (str)`: The hash of the previous block in the chain.
  - `timestamp (int)`: The timestamp for the new block.
- **Returns**:
  - A tuple containing the JSON-formatted block header and the successful block hash.
- **Description**:
  - This function filters valid transactions, calculates their Merkle root, and then attempts to find a nonce such that the hash of the block header is below the difficulty target. The process iterates through nonces until a valid hash is found, demonstrating the mining process.

### Additional Considerations
- **Error Handling**: The script includes robust error handling, particularly for JSON decoding errors and cryptographic verification issues, ensuring that invalid data does not compromise the blockchain simulation.
- **Diagnostic Outputs**: Diagnostic prints are included to aid in debugging and understanding the flow of data through the transaction verification process.
### Function `write_output(block_header, coinbase_transaction, transactions, total_fee_collected, block_subsidy)`
Writes detailed block and transaction information to an output file.
- **Parameters**:
  - `block_header (str)`: The string representation of the block header.
  - `coinbase_transaction (dict)`: The coinbase transaction, serialized into JSON.
  - `transactions (list)`: A list of transactions included in the block.
  - `total_fee_collected (int)`: The total fees collected from the transactions in satoshis.
  - `block_subsidy (float)`: The subsidy given to the miner for creating the block, in BTC.
- **Functionality**:
  - This function outputs the block header, serialized coinbase transaction, transaction IDs, total fees collected, block subsidy, and total miner's reward to a file named `output.txt`.
- **Error Handling**:
  - Catches and reports any exceptions encountered during file operations.

### Main Execution Flow (`main()`)
Coordinates all steps from reading transactions to writing the final output.
- **Steps**:
  - Reads transactions from the specified `mempool_dir`.
  - Validates each transaction and computes their transaction IDs.
  - Selects valid transactions for inclusion in the block based on criteria such as fees.
  - Creates the coinbase transaction and computes its transaction ID.
  - Mines the block by calculating the appropriate nonce that meets the difficulty target.
  - Writes all relevant information to `output.txt`.
- **Block Subsidy Calculation**:
  - Assumes a predefined block subsidy of 6.25 BTC, which should be dynamically calculated based on the block height in a real-world scenario.

### Usage

To use this script in a blockchain simulation environment:
1. Ensure that all dependent functions (`read_transactions`, `validate_transaction`, etc.) are correctly defined and accessible.
2. Run the script through a command-line interface using a command like `python main.py`.
3. Review the `output.txt` for detailed information on the mined block and the transactions included.

# Blockchain Mining Simulation

This repository contains a Python script designed to simulate the mining process in a blockchain system. The script covers reading, validating, and processing transactions, as well as mining them into a new block and writing the results to an output file.

## Project Overview

The blockchain mining simulation script demonstrates the following key functionalities:

- **Transaction Reading**: Transactions are read from JSON files in a specified directory, validated, and processed.
- **Transaction Validation**: Ensures that transactions meet specific criteria for format and completeness.
- **Mining Simulation**: Implements a simulated proof-of-work mining process, including nonce finding to meet a difficulty target.
- **Output Generation**: Detailed information about mined blocks, including headers and transaction details, is written to an output file.



