# Block Construction Program Documentation

## Design Approach

The block construction program simulates the process of constructing a valid block in a blockchain system. It involves several key steps and concepts:

### 1. Transaction Validation

Transactions are validated to ensure they meet specified criteria:

- **Structure Check**: Validate the presence of required fields (`vin`, `vout`) in each transaction.
- **Size Limitation**: Ensure transactions do not exceed a predefined maximum size (`MAX_BLOCK_SIZE_BYTES`) to prevent oversized blocks.
- **Script Validation**: Perform specific validations based on `scriptpubkey_type` to enforce transaction rules (e.g., `p2pkh`, `p2wsh`).

### 2. Transaction Selection

Selected transactions are included in the block based on their weight:

- **Weight Calculation**: Compute the weight of each transaction considering base size and witness data (if present).
- **Weight Sorting**: Sort transactions by weight and select a subset that collectively do not exceed a specified `max_total_weight`.

### 3. Merkle Root Calculation

The Merkle root hash summarizes included transactions for integrity:

- **Transaction Serialization**: Serialize transaction IDs of selected transactions.
- **Merkle Tree Construction**: Build a Merkle tree using a pairwise hashing function (`hash2`) to compute the Merkle root hash.

### 4. Block Mining

Simulates the mining process to find a valid block hash meeting the `difficulty_target`:

- **Nonce Iteration**: Adjust the `nonce` in the block header iteratively to find a hash satisfying the difficulty target.
- **Block Header Assembly**: Construct the block header with version, previous block hash, Merkle root, timestamp, bits, and nonce.
- **Hash Computation**: Compute the double SHA-256 hash of the block header and validate against the difficulty target.

## Implementation Details

### Transaction Validation

The `validate_transaction` function checks transactions for validity:

- Ensures necessary fields (`vin`, `vout`) are present.
- Validates transaction size and enforces script-specific rules (`p2pkh`, `p2wsh`).

### Transaction Selection

The `trim_transactions` function filters and selects transactions by weight:

- Calculates and sorts transactions by weight.
- Selects a subset of transactions to meet the `max_total_weight` constraint.

### Merkle Root Calculation

The `merkle_root` function computes the Merkle root hash of included transactions:

- Serializes transaction IDs and constructs a Merkle tree using a recursive pairwise hashing technique (`hash2`).
- Returns the root of the Merkle tree for transaction integrity.

### Block Mining

The `mine_block` function simulates block mining to find a valid block hash:

- Iteratively adjusts the `nonce` in the block header to meet the `difficulty_target`.
- Constructs the block header and computes the block hash using double SHA-256 hashing.

## Results and Performance

The block construction program successfully constructs a valid block based on selected transactions:

- Efficiently filters and selects transactions to optimize block size and weight.
- Computes the Merkle root hash to ensure transaction integrity.
- Simulates the block mining process to find a valid block hash within the defined difficulty target.

### Performance Analysis

- **Validation Efficiency**: Transaction validation and selection are optimized for handling a large number of transactions.
- **Merkle Root Computation**: The Merkle root calculation is performed efficiently using recursive hashing.
- **Block Mining Optimization**: The block mining process iteratively adjusts the `nonce` to find a valid block hash meeting the difficulty target.

## Conclusion

In conclusion, the block construction program demonstrates core blockchain concepts:

- Transaction validation and selection based on weight and size.
- Merkle tree construction for summarizing and securing transactions.
- Block mining to secure the blockchain and maintain consensus.

## Future Improvements

Potential areas for future enhancement and research include:

- Mining algorithm optimization for faster block discovery.
- Enhanced validation rules and script execution for improved transaction security.
- Integration with a larger blockchain network to test scalability and interoperability.

## References

- Bitcoin Whitepaper: Satoshi Nakamoto (2008)
- Python Standard Library Documentation: hashlib, json
- ECDSA Documentation: Cryptographic Operations
- Learn me bitcoin: [https://learnmeabitcoin.com/](https://learnmeabitcoin.com/)
- Ken Shirriff's blog: [Ken Shirriff's blog](https://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html)
