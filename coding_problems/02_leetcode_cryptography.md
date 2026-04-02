# Level 2: Cryptography & Security Primitives (Problems 11-20)

These problems focus on the underlying math and data manipulation required for Blockchain platforms. You will practice bitwise operations, hashing, arrays, and standard cryptographic schemas.

---

### Problem 11: Implement Proof of Work (Brute Force Hashing)
**Difficulty:** Medium | **Topic:** Cryptography, Loops

**Description:**
Bitcoin secures its network by forcing miners to find a specific hash. Given a string `block_data` and an integer `difficulty` (which represents the number of leading zeros required), find the lowest positive integer `nonce` (starting from 0) such that the SHA-256 hash of `block_data + str(nonce)` starts with exactly `difficulty` zeros.

**Constraints:**
- `1 <= difficulty <= 5`
- `1 <= len(block_data) <= 100`

**Example 1:**
```python
Input: block_data = "hello_world", difficulty = 2
Output: 260
Explanation: hash("hello_world" + "260") = "008b...". Since it starts with two zeros, 260 is the winning nonce.
```

**Starter Code:**
```python
import hashlib

def find_nonce(block_data: str, difficulty: int) -> int:
    pass
```

**Auditor Hint:** Use a `while True` loop, incrementing `nonce` by 1. Hash the string `(block_data + str(nonce)).encode('utf-8')` using `hashlib.sha256()`. Call `.hexdigest()` and check `.startswith('0' * difficulty)`.

---

### Problem 12: Big Endian vs Little Endian Flipper
**Difficulty:** Easy | **Topic:** String Manipulation, Hex

**Description:**
Ethereum outputs certain hex values in Big Endian format, but you might need it in Little Endian to process properly in an AI data pipeline. 
Given a hexadecimal string `hex_str` (without the '0x' prefix) whose length is always a multiple of 2 (representing consecutive bytes), reverse the order of the bytes.

**Constraints:**
- `2 <= len(hex_str) <= 10^4`
- `len(hex_str) % 2 == 0`
- The string contains only characters `0-9` and `a-f`.

**Example 1:**
```python
Input: hex_str = "12345678"
Output: "78563412"
Explanation: The bytes are [12, 34, 56, 78]. Reversed, they are [78, 56, 34, 12].
```

**Starter Code:**
```python
def reverse_endianness(hex_str: str) -> str:
    pass
```

**Auditor Hint:** Do not just reverse the whole string (which would make `12` into `21`). Split the string into chunks of 2 characters, reverse the list of chunks, and join them back together.

---

### Problem 13: The Replay Attack Nonce Cache
**Difficulty:** Easy | **Topic:** Hash Maps / Sets

**Description:**
You are processing incoming transactions to your smart contract. An attacker might capture a valid transaction and re-submit it exactly to duplicate the effect (Replay Attack). 
To prevent this, every transaction must have a `nonce` (a unique ID). 
Given a list of tuples `(user_id, nonce)`, return a list of booleans indicating if the transaction is `True` (Valid/New) or `False` (Invalid/Replayed).

**Constraints:**
- `1 <= len(transactions) <= 10^5`
- `1 <= user_id <= 10^4`
- `1 <= nonce <= 10^9`

**Example 1:**
```python
Input: transactions = [(1, 100), (2, 50), (1, 100), (1, 101)]
Output: [True, True, False, True]
Explanation: Transaction 1 (User 1, Nonce 100) is accepted. Transaction 2 is accepted. Transaction 3 is a replay of Nonce 100 from User 1, so it is rejected.
```

**Starter Code:**
```python
def validate_transactions(transactions: list[tuple[int, int]]) -> list[bool]:
    pass
```

**Auditor Hint:** Track used nonces per user. A dictionary mapping `user_id` to a `set` of used `nonces` is perfect here.

---

### Problem 14: DAO Multi-Sig Threshold Voting
**Difficulty:** Medium | **Topic:** Dictionaries, System Design

**Description:**
A Multi-Sig (Multiple Signature) wallet requires `M` out of `N` owners to approve a transaction before it executes.
Implement the `MultiSig` class:
- `MultiSig(int threshold)` Initializes the contract requiring `threshold` approvals.
- `submit_tx(str tx_id) -> None` Proposes a new transaction.
- `approve_tx(str tx_id, str owner) -> bool` An owner approves a transaction. Returns `True` if it successfully reached the threshold and executed just now, otherwise `False`. (If already executed, ignore and return `False`).

**Constraints:**
- `1 <= threshold <= 10`
- Owners can only vote once per transaction.

**Example 1:**
```python
Input: 
wallet = MultiSig(2)
wallet.submit_tx("buy_server")
wallet.approve_tx("buy_server", "Alice") # Returns False (1/2 votes)
wallet.approve_tx("buy_server", "Alice") # Returns False (Alice already voted)
wallet.approve_tx("buy_server", "Bob")   # Returns True (2/2 votes, Executed!)
```

**Starter Code:**
```python
class MultiSig:
    def __init__(self, threshold: int):
        pass

    def submit_tx(self, tx_id: str) -> None:
        pass

    def approve_tx(self, tx_id: str, owner: str) -> bool:
        pass
```

**Auditor Hint:** Use a dictionary where `tx_id` maps to another object `{ "approvals": set(), "executed": bool }`.

---

### Problem 15: Storage Slot Data Packer (Bitwise Simulation)
**Difficulty:** Medium | **Topic:** Bit Manipulation

**Description:**
Storing data on the Ethereum blockchain is incredibly expensive. To save gas, auditors pack multiple small integers into a single large integer.
You have 4 small integers (ranging from 0 to 255). Pack them into a single 32-bit integer. 
The 1st integer goes into the highest 8 bits, the 2nd into the next 8, and so on.

**Constraints:**
- `0 <= a, b, c, d <= 255`

**Example 1:**
```python
Input: a = 1, b = 2, c = 3, d = 4
Output: 16909060
Explanation: 
1 in binary: 00000001
2 in binary: 00000010
3 in binary: 00000011
4 in binary: 00000100
Combined: 00000001000000100000001100000100 (which is 16909060 in base 10)
```

**Starter Code:**
```python
def pack_variables(a: int, b: int, c: int, d: int) -> int:
    pass
```

**Auditor Hint:** Use the left shift operator `<<` to push the bits, and the bitwise OR operator `|` to combine them. `(a << 24) | (b << 16)...`

---

### Problem 16: Checksum Data Validator
**Difficulty:** Easy | **Topic:** Hashing

**Description:**
When an AI downloads an enormous data file, it must verify the file wasn't corrupted or maliciously altered.
Given a list of strings `chunks` (pieces of a file) and an `expected_md5` hex string, return `True` if the combined chunks perfectly hash to the expected MD5 value.

**Constraints:**
- `1 <= len(chunks) <= 10^3`
- `1 <= expected_md5.length() <= 32`

**Example 1:**
```python
Input: chunks = ["abc", "def"], expected_md5 = "e80b5017098950fc58aad83c8c14978e"
Output: True
```

**Starter Code:**
```python
import hashlib

def verify_checksum(chunks: list[str], expected_md5: str) -> bool:
    pass
```

**Auditor Hint:** `''.join(chunks).encode('utf-8')` into `hashlib.md5()`.

---

### Problem 17: Vulnerable Simple Signature Forgery
**Difficulty:** Hard | **Topic:** Strings, Hash Reversal Logic

**Description:**
A lazy blockchain developer created a terrible signature algorithm: `signature = hash(message + secret_key)`.
As an attacker, if you know the `message`, the resulting `signature`, and the length of the `secret_key` (say, length 3), and you know the `secret_key` is strictly lowercase english letters, write an attacker function that finds the `secret_key`.

**Constraints:**
- `secret_key` is length 3, lowercase letters only (`a-z`).
- `message` length <= 10.
- Hash used is MD5.

**Example 1:**
```python
Input: message = "send10", signature = "59dc5c2... (md5 of send10cat)"
Output: "cat"
```

**Starter Code:**
```python
import hashlib
import itertools
import string

def forge_signature(message: str, signature: str) -> str:
    pass
```

**Auditor Hint:** Use `itertools.product(string.ascii_lowercase, repeat=3)`. Iterate through all permutations, build the string, hash it, and compare it to the signature constraint.

---

### Problem 18: Time-Locked Cryptography Token
**Difficulty:** Easy | **Topic:** Math, Logic

**Description:**
Tokens in smart contracts are often "time-locked" preventing teams from dumping their shares immediately. 
Given an array of `investors` where each is `[tokens_owned, unlock_time]`, and a generic `current_time`, return the total sum of tokens that are currently unlocked and eligible to be sold.

**Constraints:**
- `1 <= len(investors) <= 10^4`
- `0 <= unlock_time, current_time <= 10^9`

**Example 1:**
```python
Input: investors = [[100, 5000], [200, 3000], [300, 8000]], current_time = 4000
Output: 200
Explanation: Only investor 2's tokens are unlocked (3000 <= 4000). 
```

**Starter Code:**
```python
def calculate_unlocked_supply(investors: list[list[int]], current_time: int) -> int:
    pass
```

**Auditor Hint:** An incredibly fast O(N) list comprehension. `sum(tokens for tokens, unlock in investors if unlock <= current_time)`.

---

### Problem 19: Implement Symmetric XOR Encryption
**Difficulty:** Medium | **Topic:** Bitwise Simulation

**Description:**
A fundamental cryptographic block. Given a string `message` and an integer `key` (0-255), perform a bitwise XOR on every character's ASCII value to encrypt it. Return a list of the resulting integers.

**Constraints:**
- `1 <= len(message) <= 1000`
- `0 <= key <= 255`

**Example 1:**
```python
Input: message = "ab", key = 5
Output: [92, 95]
Explanation: ascii 'a' is 97. 97 XOR 5 = 92. ascii 'b' is 98. 98 XOR 5 = 95.
```

**Starter Code:**
```python
def xor_encrypt(message: str, key: int) -> list[int]:
    pass
```

**Auditor Hint:** Iterate through `message`, convert character to point with `ord(c)`, perform `^ key`, and append.

---

### Problem 20: Base58 Address Encoder
**Difficulty:** Hard | **Topic:** Math / Base Conversion

**Description:**
Bitcoin doesn't use standard Hexadecimal (Base16) or Base64. It uses Base58, removing ambiguous characters (`0, O, I, l`).
Given a large integer `num`, convert it into a Base58 string using this exact alphabet: 
`123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`

**Constraints:**
- `1 <= num <= 10^18`

**Example 1:**
```python
Input: num = 100
Output: "2i"
Explanation: 100 divided by 58 is 1 remainder 42. In the alphabet, index 1 is "2", and index 42 is "i".
```

**Starter Code:**
```python
def encode_base58(num: int) -> str:
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    pass
```

**Auditor Hint:** Use a `while num > 0:` loop. Find the remainder using `num % 58` to map to the character string, then divide using `num //= 58`. Don't forget to reverse the resulting string!
