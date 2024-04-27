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

The script is designed with efficiency and clarity in mind. It utilizes a structured approach to navigate through the challenge's requirements, ensuring that each step, from reading transactions to mining the block, is both logical and optimized for performance.

The `run.sh` file is the entry point for executing the script, invoking the main mining program, which is capable of autonomously performing all necessary tasks to mine a block.

## Solution Execution

To execute the solution:

```bash
./run.sh

