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

### Design and Execution

Reads transactions from a specified directory in JSON format
Validates transactions based on required fields and script types
Selects transactions for a block based on their fees and virtual sizes (vsize)
Creates a coinbase transaction rewarding the miner with the block subsidy and transaction fees
Mines the block by finding a valid nonce that satisfies the difficulty target
Writes the block header, serialized coinbase transaction, transaction IDs, total fee collected, block subsidy, and total miner's reward to an output fileç

## Usage

Ensure that you have a directory containing valid transaction JSON files. The default directory is set to mempool.
Run the script using the following command: `python main.py`

The script will read the transactions from the specified directory, validate them, select transactions for the block, create a coinbase transaction, mine the block, and write the output to a file named output.txt.
Check the output.txt file for the block details, including the block header, serialized coinbase transaction, transaction IDs, total fee collected, block subsidy, and total miner's reward.

pythonCopy codeimport os
import json
import hashlib
import time
import random
from ecdsa import VerifyingKey, SECP256k1, BadSignatureError, util
This part of the code imports the necessary libraries and modules:

os: Provides a way to interact with the operating system.
json: Allows working with JSON data.
hashlib: Provides hash functions for cryptographic purposes.
time: Allows working with timestamps and time-related functions.
random: Generates random numbers.
ecdsa: Provides support for Elliptic Curve Digital Signature Algorithm (ECDSA).

pythonCopy codemempool_dir = 'mempool'
This line sets the directory name for the mempool, which is a directory where unconfirmed transactions are stored.
pythonCopy codeprevious_block_hash = '0' * 64
block_height = 1
timestamp_variation = random.randint(-3600, 3600)
current_time = int(time.time()) + timestamp_variation
These lines initialize some variables:

previous_block_hash: Represents the hash of the previous block. It is initially set to a string of 64 zeros.
block_height: Represents the height or index of the current block. It starts at 1.
timestamp_variation: Generates a random timestamp variation between -3600 and 3600 seconds.
current_time: Calculates the current timestamp by adding the timestamp variation to the current time.

pythonCopy codedef double_sha256(hex_str):
    return hashlib.sha256(hashlib.sha256(bytes.fromhex(hex_str)).digest()).hexdigest()
This function takes a hexadecimal string as input, performs a double SHA-256 hash on it, and returns the resulting hash as a hexadecimal string.
def calculate_merkle_root(tx_hashes):
  
This function calculates the Merkle root of a list of transaction hashes using a recursive approach. It concatenates pairs of hashes, calculates their double SHA-256 hash, and repeats the process until a single hash (the Merkle root) is obtained.

pythonCopy codedef calculate_txid(transaction):
    
This function calculates the transaction ID (TXID) of a given transaction. It converts the transaction to a JSON string with sorted keys, performs a double SHA-256 hash on the encoded string, and returns the resulting hash as a hexadecimal string.
These are the initial parts of the code that set up the necessary imports, variables, and helper functions for the blockchain implementation.
