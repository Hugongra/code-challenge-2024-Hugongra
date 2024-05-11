This repo is a solution to the [2024 Summer of Bitcoin challenge](https://github.com/SummerOfBitcoin/code-challenge-2024-Nesopie/blob/main/README.md).

## Setup

1. Clone the repo.
2. Install `pnpm` if you don't already have it installed.
3. Run `pnpm install` to install all dependencies.
4. Run `make run` to start mining a block!

## Project structure

Before we move on to talking about the project, here's the project structure to make you familiar with it.
All the main functionality is organized in the `src/features` directory and includes:

- `block`: This folder handles all functionality related to creating and mining a block.
- `encoding`: The encoding utilities for serializing transactions.
- `script`: Contains a minimalistic implementation of `script`.
- `transaction`: Contains the transactions classes that are used throughout the transactions.
- `validator`: Finally the validator folder consists of multiple validators that are used on a transaction before it is put into a block.

```
├── src
│   ├── constants.ts
│   ├── features
│   │   ├── block
│   │   ├── encoding
│   │   ├── script
│   │   ├── transaction
│   │   └── validator
│   ├── index.ts // entry point
│   ├── types.ts
│   └── utils.ts
```

## Encoding

```
├── compactSize.ts
├── errors.ts
├── serializer.ts
└── witnessTemplates.ts
```

The main functionality of `src/features/encoding` resides in `src/features/encoding/serializer.ts`. The Serializer class consists of only static methods that serializes transactions, their inputs and outputs for the raw hex format. Serialization for generating a message for signature verification is currently being handled by the `Transaction` class itself. Apart from this the encoding folder also exports utilities for handling Bitcoin `varint`s in the `src/features/encoding/compactSize.ts` folder.

## Transaction

```
├── components
│   ├── input.ts
│   ├── output.ts
│   └── transaction.ts
├── errors.ts
├── index.ts
├── types.ts
└── utils.ts
```

The `src/features/transaction/components` folder consists of a `Transaction` class, `Input` class and `Output` class. The `Transaction` class follows the `Builder` pattern. It first accepts just the `version` and `locktime` and the `inputs` and `outputs` can be incrementally added later on. It also follows a `Singleton`-like pattern to cache the results of expensive calculations such as:

- `txid`: The transaction id of a transaction requires the serialization of the entire transaction along with it's `hash256` in reverse byte order.
- `wtxid`: The witness transaction id used in the generation of the block.
- `serializedTx`: The raw non-segwit transaction hex.
- `serializedWTx`: The raw segwit transaction hex.
- `weight`: The weight of the transaction. A `4x` multiplier is used for non segwit parts of the transaction and a `1x` multiplier for the segwit parts of the transaction.
- `hashPrevouts`: Used in the generation of a signature verification message as outlined in BIP143.
- `hashSequences`: Used in the generation of a signature verification message as outlined in BIP143.
- `hashOuputs`: Used in the generation of a signature verification message as outlined in BIP143.

For example, `txid` is cached as follows:

```
get txid() {
    if (this._txid) return this._txid;
    const txid = reversify(sha256(sha256(this.serializedTx)));
    this._txid = txid;
    return this._txid;
}
```

This gives us `O(1)` time complexity for calculating the `txid` if we've already generated it once.

The `.signWith` method on the `Transaction` class is the method responsible for generating a message for signature verification for various `SigHash` types. Currently, signature message verification for non-segwit transactions is only implemented for `SIGHASH_ALL` and `SIGHASH_ALL | ANYONECANPAY`. For segwit transactions all `Sighash` types are implemented.

## Validator

```
├── hash.ts
├── length.ts
├── script.ts
└── signature.ts
```

### Metadata validator

The metadata validator checks for details specific to a transaction. It checks:

- `sum(inputs.values) - sum(outputs.values) >= 1000`. That is, fees must be atleast 1000 sats.
- Checks if the length of the `scriptpubkey` is correct. For example in `p2wpkh`, the length of the `scriptpubkey` is 22 bytes. (1 byte for `OP_0`, 1 byte for `OP_PUSHBYTES_20` and another is the 20 byte hash of the `pubkey`).
- If the `scriptpubkey address` is valid or not. For example non segwit transactions' address should be equal to `base58` of the pubkey, `bech32` for v0_segwit transactions and `bech32m` for v1_segwit (p2tr) transactions.

### Hash validator

The hash validator checks if the hash of the pubkey or the script matches that in the index.

#### p2pkh:

- Get the pubkey from the `scriptSig`.
- Check if `hash160(pubkey)` matches the one in the `scriptpubkey`.

#### p2sh:

- Get the redeem script from the `scriptSig`.
- Check if `hash160(redeem_script)` matches the one in the `scriptpubkey`.
  - If p2wpkh
    - get the pubkey from the witness (last element).
    - `hash160(pubkey)` is equal to the one in `scriptSig`
  - If p2wsh
    - get the witness script from the witness (last element).
    - `hash160(pubkey)` is equal to the one in `scriptSig`.

#### p2wpkh:

- Get the pubkey from the witness (second element).
- Check if `hash160(pubkey)` is equal to the one in the `scriptPubkey`.

#### p2wsh:

- Get the script from the witness (last element).
- Check if `hash160(script)` is equal to the one in the `scriptpubkey`.

### Signature validator

The signature validator is implemented for `p2pkh`, `p2sh-p2wpkh`, `p2wpkh` and `p2tr` transactions.

#### p2pkh:

- Check if the signature in scriptSig can be verified with the pubkey in the `scriptSig`.

#### p2wpkh, p2sh-p2wpkh:

- Check if the signature in the witness can be verified with the pubkey in the `scriptSig`.

#### p2tr:

- If key path spend
  - Take the signaure
  - If there's no sighash, use the default one (0x00).
  - `msg = taprootHash(TAP_SIG_HASH, "00" tx.signWith(index, sighash))`
  - Verify with the tweaked pubkey in the `scriptpubkey`.
- If script path spend:
  - Get the internal public key from the control bock
  - Find the merkle root with the provided merkle proofs in the control block.
  - calculate the tweak using `tweak = taprootHash(TAP_TWEAK, p + merkle_root)`.
  - tweak the internal pubkey with the tweak and check if the result is equal to the pubkey in the `scriptpubkey`.

### Script validator

The script validator simply runs the script for `p2sh` and `p2wsh` payment types and returns if the top of the stack is true or not.

## Script

```
├── Script.ts
├── constants.ts
├── error.ts
├── executor.ts
├── op_codes.ts
├── stack.ts
└── utils.ts
```

Almost all of the script execution logic is handled in `src/features/script/executor.ts`. The executor is a long list of `if-else` statements to handle each op*code. The reason `if-else` was used was so that multiple op_codes can be handled in a single statement. For example, the op_codes for `OP_PUSHBYTES*<NUM>` are defined as:

```
else if (
    opcode >= OP_CODES.OP_PUSHBYTES_1 &&
    opcode <= OP_CODES.OP_PUSHBYTES_75
)
```

where as, in the case of switch statements each op_code has to be handled in each `case statement`.

The most difficult part of the `executor`, however was the handling of control flow statements. Here's how I solved it.

The general algorithm is to keep track of an 'execution stack' that tells you the depth of the `if-else` nesting and whether the current op_code can be executed or not. Consider the following script:

```
OP_NOTIF
	OP_IF
		OP_1
	OP_ELSE
		OP_2
	OP_ENDIF
OP_ELSE
	OP_3
OP_ENDIF
```

If there's a true statement on the witness stack then then the outer `OP_ELSE` branch is executed and otherwise if there's one false, one true statement then 1 should be push on the stack and if there's two false statements then a 2 must be pushed onto the stack. Let's take a look at the first and second case.

##### CASE: False, True on stack

```
SHOULD_EXECUTE  True      ----      True      ----      False      ----
STACK           [0]
		        [2]	      [2]       []        [1]       [1]        [1]
OP_CODE         OP_NOTIF  OP_IF     OP_1      OP_ELSE   OP_2       OP_ENDIF

EXECUTION_STACK [True]    [True]    [True]    [True]    [False]    [False]
					      [True]    [True]    [True]    [True]     [True]
								    [True]    [True]    [True]     [True]

```

```
Continued...
SHOULD_EXECUTE  ----      False      ----       ----
STACK           [1]       [1]        [1]        [1]
OP_CODE         OP_ELSE   OP_2       OP_ENDIF   ----
EXECUTION_STACK [True]    [False]    [False]    [True]
				[True]    [True]     [True]
```

##### CASE: True, True on stack

```
SHOULD_EXECUTE  ----      ----       False      ----       False       ----
STACK           [1]       [1]        [1]        [1]        [1]         [1]
		        [2]	      [2]        [2]        [2]        [2]         [2]
OP_CODE         OP_NOTIF  OP_IF      OP_1       OP_ELSE    OP_2        OP_ENDIF

EXECUTION_STACK [True]    [False]    [True]     [True]     [False]     [True]
					      [True]     [False]    [False]    [False]     [False]
								     [True]     [True]     [True]      [True]

```

```
Continued...
SHOULD_EXECUTE  ----       False      ----       ----
								   	  [2]        [2]
				[1]        [1]        [1]        [1]
STACK           [2]        [2]        [2]        [2]
OP_CODE         OP_ELSE    OP_2       OP_ENDIF   ----
EXECUTION_STACK [False]    [False]    [False]    [True]
				[True]     [True]     [True]
```

- Initially, the execution stack has a single `[True]` statement.
- The `condition` is pushed on to the `execution stack` whenever an `OP_IF` is encountered.
- `!condition` is pushed whenever an `OP_NOTIF` is encountered.
- When an `OP_ELSE` is encountered then the value on top of the stack is simply toggled. This also works with multiple `OP_ELSE` statements.
- `OP_ENDIF` simply pops the top value off the stack.
- If there's a single `False` on the execution stack then the current op_code is not executed.
- If at the end, the size of the execution stack is not 1 then throw an error since there are mismatched `if-else`s.

## Block

```
├── coinbaseTransaction.ts
├── fee.ts
├── merkleRoot.ts
└── mine.ts
```

The main functionality is in `src/features/block/mine.ts`. The block is mined as follows:

```
for (let nonce = 0; nonce < 0xffffffff; nonce++) {
    const nonceBuf = Buffer.alloc(4);
    nonceBuf.writeUInt32LE(nonce);
    const serializedBlock = `${version.toString(
      "hex"
    )}${prevBlockHash}${merkleRootHash}${time.toString("hex")}${nbits.toString(
      "hex"
    )}${nonceBuf.toString("hex")}`;
	const blockHash = reversify(sha256(sha256(serializedBlock)));
    if (
      Buffer.from(difficulty, "hex").compare(Buffer.from(blockHash, "hex")) < 0
    )
      continue;
    return { serializedBlock, blockHash, coinbaseTransaction };
  }
```

## index.ts

The main entrypoint file loads all these transactions and validates them. If they're valid then double spending is checked. Once these are done then transactions are sorted based on their fee/weight ratio. A block size of 4 mb is considered and transactions until the block has reached it's capacity. These transactions are then sent to the miner who calculates the merkle root and generates the block.

## References

1. [Raw transaction serialization](https://developer.bitcoin.org/reference/transactions.html#raw-transaction-format).
2. [Weight Calculation](https://learnmeabitcoin.com/technical/transaction/size/)
3. [BIP 340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)
4. [BIP 341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)
5. [BIP 143](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)
6. [Script Opcodes](https://en.bitcoin.it/wiki/Script)
7. [OP_CHECKSIG](https://en.bitcoin.it/wiki/OP_CHECKSIG)
