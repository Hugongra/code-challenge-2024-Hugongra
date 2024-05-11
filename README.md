[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/bWLxfecg)
# Summer of Bitcoin 2024: Mine your first block

## Overview
In this challenge, you are tasked with the simulation of mining process of a block, which includes validating and including transactions from a given set of transactions.
The repository contains a folder `mempool` which contains JSON files. 
These files represent individual transactions, some of which may be invalid. Your goal is to successfully mine a block by including only the valid transactions, following the specific requirements outlined below.

## Objective
Your primary objective is to write a script that processes a series of transactions, validates them, and then mines them into a block. The output of your script should be a file named `output.txt` that follows a specific format.

## Requirements
### Input
- You are provided with a folder named `mempool` containing several JSON files. Each file represents a transaction that includes all necessary information for validation.
- Among these transactions, some are invalid. Your script should be able to discern valid transactions from invalid ones.

### Output
Your script must generate an output file named `output.txt` with the following structure:
- First line: The block header.
- Second line: The serialized coinbase transaction.
- Following lines: The transaction IDs (txids) of the transactions mined in the block, in order. The first txid should be that of the coinbase transaction

### Difficulty Target
The difficulty target is `0000ffff00000000000000000000000000000000000000000000000000000000`. This is the value that the block hash must be less than for the block to be successfully mined.

## Execution
- Create a file named `run.sh` that contains the command to execute your script. This file should ideally contain a single command like `python main.py` or `node index.js`.
- Your script should autonomously perform all tasks when `run.sh` is executed, without requiring any manual intervention.

## Evaluation Criteria
Your submission will be evaluated based on the following criteria:

- **Score**: Your code output will be scored bases on the fee collected and the amount of available block space utilised. **You must score at least 60 points to pass the challenge.**
- **Correctness**: The `output.txt` file must be correctly formatted in the manner described above.
- **Code Quality**: Your code should be well-organized, commented, and follow best practices.
- **Efficiency**: Your solution should process transactions and mine the block efficiently.

## Document your work

Apart from the code, you must also publish a `SOLUTION.md` file explaining your solution in the following format:
- **Design Approach:** Describe the approach you took to design your block construction program, explain all the key concepts of creating a valid block.
- **Implementation Details:** Provide pseudo code of your implementation, including sequence of logic, algorithms and variables used etc.
- **Results and Performance:** Present the results of your solution, and analyze the efficiency of your solution.
- **Conclusion:** Discuss any insights gained from solving the problem, and outline potential areas for future improvement or research. Include a list of references or resources consulted during the problem-solving process.

## What NOT to Do

In this challenge, it's crucial to understand and adhere to the following restrictions. These are put in place to ensure that you engage with the core concepts of bitcoin and apply your problem-solving skills to implement the solution from first principles.

- **Do Not Use Bitcoin Libraries for Transaction Validation:** You must not use any Bitcoin-specific libraries or frameworks that automate transaction validation processes. The intent of this challenge is for you to understand and implement the validation logic manually.
- **Permissible Libraries:** The use of standard cryptographic libraries, such as secp256k1 for elliptic curve cryptography, and standard hashing libraries (e.g., for SHA-256) is allowed and encouraged. These libraries are essential for implementing the cryptographic underpinnings of bitcoin without reinventing the wheel.
 - **Implement the Mining Algorithm Yourself:** You are required to implement the mining algorithm on your own. This includes creating a way to correctly form a block header, calculate the hash, and meet the challenge of finding a hash below a certain target.

### Plagiarism Policy:
Our plagiarism detection checker thoroughly identifies any instances of copying or cheating. Participants are required to publish their solutions in the designated repository, which is private and accessible only to the individual and the administrator. Solutions should not be shared publicly or with peers. In case of plagiarism, both parties involved will be directly disqualified to maintain fairness and integrity.

### AI Usage Disclaimer:
You may use AI tools like ChatGPT to gather information and explore alternative approaches, but avoid relying solely on AI for complete solutions. Verify and validate any insights obtained and maintain a balance between AI assistance and independent problem-solving.

## Why These Restrictions?
These restrictions are designed to deepen your understanding of bitcoin technicals.
By completing this assignment, you will gain hands-on experience with the technology that make bitcoin secure and trustless.
Remember, the goal of this challenge is not just to produce a working solution but to engage critically with the fundamental components of bitcoin. This is an opportunity to showcase your problem-solving skills and your ability to implement complex algorithms from scratch.

## Additional Information
- This challenge is designed to test your understanding of bitcoin fundamentals, including transaction validation and block mining processes.
- While the challenge focuses on the simulation of these processes, you are encouraged to implement your solution in a way that demonstrates depth of understanding and creativity.
