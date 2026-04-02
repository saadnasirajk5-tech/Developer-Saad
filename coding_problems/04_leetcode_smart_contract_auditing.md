# Level 4: Smart Contract Security & Auditing (Problems 31-40)

To become a top-tier Blockchain Security Auditor, you must be able to spot vulnerabilities like Reentrancy, Logic Bypasses, and Economic Manipulations immediately. These problems simulate the core state machines of DeFi Hacks.

---

### Problem 31: The Reentrancy Simulation
**Difficulty:** Hard | **Topic:** State Updates, Recursion

**Description:**
"Reentrancy" occurs when a contract calls an external untrusted contract before updating its own balances, allowing the untrusted contract to recursively call back into the original function and drain it.
You are given a simplistic state dictionary `vault_balances` and an `attacker_request_limit` (how many recursive calls the attacker makes).
Implement `drain_vault(vault_balances, user, attacker_request_limit)`:
1. Check if `vault_balances[user] > 0`.
2. Simulate the "Transfer" by decrementing the `attacker_request_limit`. If the limit > 0, recursively call `drain_vault()` again.
3. Finally, set `vault_balances[user] = 0`.
4. Return the total amount of money the attacker mathematically stole (Original balance * number of times the check passed).

**Constraints:**
- `1 <= attacker_request_limit <= 100`

**Example 1:**
```python
Input: vault_balances = {"Attacker": 10}, user = "Attacker", attacker_request_limit = 3
Output: 30
Explanation: 
Call 1: balance is 10. Calls transfer.
  Call 2: balance is 10. Calls transfer.
    Call 3: balance is 10. Calls transfer (limit reached).
      balance set to 0. 
      returns 3 x 10 = 30 stolen!
```

**Starter Code:**
```python
def drain_vault(vault_balances: dict[str, int], user: str, attacker_request_limit: int) -> int:
    pass
```

**Auditor Hint:** Notice how setting the balance to 0 happens *after* the recursive loop. That is the vulnerability! Count how many times the recursive function executes while the balance is > 0.

---

### Problem 32: The Checks-Effects-Interactions Pattern
**Difficulty:** Medium | **Topic:** Logic Refactoring

**Description:**
Fix the vulnerability from Problem 31! 
Rewrite the withdrawal function using the CEI pattern:
1. **Checks**: Verify balance > 0.
2. **Effects**: Deduct the balance `vault_balances[user] = 0`.
3. **Interactions**: Perform the recursive calls.
Return the total amount stolen using the same attacker parameters. If CEI is implemented correctly, the output should exactly equal their original balance (they stole 0 extra tokens).

**Example 1:**
```python
Input: vault_balances = {"Attacker": 10}, user = "Attacker", attacker_request_limit = 3
Output: 10
Explanation: The attacker tries to reenter 3 times, but on Call 2, the balance is already 0, so the check fails! They only get their original 10.
```

**Starter Code:**
```python
def secure_withdraw(vault_balances: dict[str, int], user: str, attacker_request_limit: int) -> int:
    pass
```

**Auditor Hint:** Standard Python recursion. Deduct the state, store the "amount to send" in a temporary local variable, do the recursive loop, then return the temporary variable.

---

### Problem 33: Integer Underflow Sandbox
**Difficulty:** Easy | **Topic:** Math Boundaries

**Description:**
Older smart contracts stored tokens in an unsigned 8-bit integer (`uint8`), which holds values from `0` to `255`. If a balance drops below 0, it wraps around to 255.
Given an initial `balance` (uint8) and a `transfer_amount`, calculate the new balance simulating this strict 8-bit wrap-around behavior.

**Constraints:**
- `0 <= balance <= 255`
- `0 <= transfer_amount <= 1000`

**Example 1:**
```python
Input: balance = 5, transfer_amount = 6
Output: 255
Explanation: 5 - 6 = -1. Wrapping around an 8-bit boundary makes it 255.
```

**Starter Code:**
```python
def simulate_uint8_underflow(balance: int, transfer_amount: int) -> int:
    pass
```

**Auditor Hint:** Use the modulo operator: `(balance - transfer_amount) % 256`.

---

### Problem 34: Access Control Hijack
**Difficulty:** Easy | **Topic:** Classes, Overriding

**Description:**
A contract has an `init_wallet(owner)` function that supposedly initializes the wallet. However, the developer forgot to check if the wallet was *already* initialized.
You are given a list of `actions`. Each action is `[caller, function_name, argument]`.
Keep track of the `current_owner`.
- If `init_wallet` is called, update the `current_owner` to `argument`.
- If `withdraw` is called, check if `caller == current_owner`. Return `True` if successful, else `False`.
Process the list of actions and return a list of booleans representing the success of any `withdraw` calls.

**Example 1:**
```python
Input: actions = [
  ["Alice", "init_wallet", "Alice"],
  ["Bob", "init_wallet", "Bob"],  # Hijack!
  ["Alice", "withdraw", "100"],
  ["Bob", "withdraw", "100"]
]
Output: [False, True]
Explanation: Bob hijacks the wallet. Alice's withdraw fails. Bob's withdraw succeeds.
```

**Starter Code:**
```python
def process_hijack_actions(actions: list[list[str]]) -> list[bool]:
    pass
```

**Auditor Hint:** Iterate through the actions. If it's an init, overwrite the owner. If it's a withdraw, append to the output array.

---

### Problem 35: Flash Loan Oracle Manipulation
**Difficulty:** Medium | **Topic:** Economics Math

**Description:**
A DeFi lending platform calculates the price of a token as `Price = Total_Reserve_A / Total_Reserve_B`.
An attacker takes a massive "Flash Loan" of `loan_amount` Token A, deposits it completely into the reserve (pumping the reserve A balance), and then borrows Token B at the newly manipulated skewed price.

Given `reserve_A`, `reserve_B`, and `loan_amount`, return the manipulated `Price` *after* the attacker dumps their loan into Reserve A. Return the float.

**Constraints:**
- `1 <= reserve_A, reserve_B <= 10^6`
- `1 <= loan_amount <= 10^9`

**Example 1:**
```python
Input: reserve_A = 100, reserve_B = 100, loan_amount = 900
Output: 10.0
Explanation: Initial price is 1. Attacker dumps 900 into reserve A. New A = 1000. Price = 1000/100 = 10.0.
```

**Starter Code:**
```python
def manipulated_oracle_price(reserve_A: int, reserve_B: int, loan_amount: int) -> float:
    pass
```

**Auditor Hint:** Simple arithmetic, but it demonstrates why automated market maker reserves cannot be used as secure price oracles!

---

### Problem 36: Front-Running the Mempool
**Difficulty:** Medium | **Topic:** Linked Lists / Arrays

**Description:**
When you submit a transaction, it goes to the "mempool". Miners pick transactions with the highest `gas_price`. 
You are given `mempool_txs`, a list of dictionaries `{"tx_id": str, "gas_price": int}`.
A victim submitted a highly profitable arbitrage transaction. You want to front-run it by submitting the exact same transaction but with `gas_price + 1`. 
Return a new list of transactions sorted descending by `gas_price` (this simulates the order the miner processes them).

**Constraints:**
- `1 <= len(mempool_txs) <= 1000`

**Example 1:**
```python
Input: mempool_txs = [{"tx_id": "victim", "gas_price": 50}], attacker_tx_id = "attacker"
Output: [{"tx_id": "attacker", "gas_price": 51}, {"tx_id": "victim", "gas_price": 50}]
```

**Starter Code:**
```python
def simulate_front_run(mempool_txs: list[dict], attacker_tx_id: str) -> list[dict]:
    pass
```

**Auditor Hint:** Find the max gas price in the list. Append a new dictionary with the attacker ID and `max_gas + 1`. Return `sorted(mempool, key=lambda x: x["gas_price"], reverse=True)`.

---

### Problem 37: Unbounded Loop Gas Exhaustion
**Difficulty:** Easy | **Topic:** Loop Conditionals

**Description:**
A contract loops through an array `users` to pay dividends. Running a line of code costs `gas`. If the gas used exceeds `block_gas_limit`, the transaction immediately crashes.
Given an array `users`, a `gas_per_user` cost, and `block_gas_limit`, return exactly how many users get paid before the transaction crashes. If it crashes, return `-1`. If everyone gets paid safely, return the `len(users)`.

**Example 1:**
```python
Input: len(users) = 100, gas_per_user = 50, block_gas_limit = 4000
Output: -1
Explanation: Total gas needed is 5000. It exceeds 4000, so the entire transaction crashes and reverts. No one gets paid!
```

**Starter Code:**
```python
def check_gas_exhaustion(num_users: int, gas_per_user: int, block_gas_limit: int) -> int:
    pass
```

**Auditor Hint:** Calculate `total = num_users * gas_per_user`. Keep an eye on the requirement: if it strictly exceeds the limit, return `-1`.

---

### Problem 38: Phishing via tx.origin
**Difficulty:** Medium | **Topic:** Class Hierarchies / Trees

**Description:**
In Solidity, `msg.sender` is the immediate caller, while `tx.origin` is the original human who started the chain of calls.
If a wallet checks `if tx.origin == owner: allow_transfer()`, an attacker can trick the owner into calling a malicious contract, which forwards the call to the wallet.

Given a list `call_chain` (e.g., `["Alice_Human", "Malicious_Contract", "Alice_Wallet"]`), and `owner_name`, evaluate if the transfer succeeds under two conditions:
1. It validates by checking `call_chain[0] == owner_name` (tx.origin).
2. It validates by checking `call_chain[-2] == owner_name` (msg.sender).
Return `[bool_origin, bool_sender]`.

**Example 1:**
```python
Input: call_chain = ["Alice", "Malware", "Wallet"], owner_name = "Alice"
Output: [True, False]
Explanation: tx_origin is Alice (True, vulnerable!). msg_sender is Malware (False, secure!).
```

**Starter Code:**
```python
def check_origin_vuln(call_chain: list[str], owner_name: str) -> list[bool]:
    pass
```

**Auditor Hint:** Python array indexing. The caller to the final contract is the second-to-last item `[-2]`.

---

### Problem 39: The Honeypot Reentrancy Trap
**Difficulty:** Medium | **Topic:** State flags

**Description:**
Scammers sometimes create "Honeypots": contracts that look deliberately vulnerable to trick hackers into attacking them, only to trap their money!
Write a `Honeypot` class simulator. 
It has `try_exploit()`. If `try_exploit` is called for the *very first time*, it seems to work (returns 100). But if it is recursively called *again* during the same execution flow, it flips a `trap_sprung` boolean to True, permanently returning 0 for all future outputs.

**Example 1:**
```python
Input: calls = 3
Output: [100, 0, 0]
```

**Starter Code:**
```python
class Honeypot:
    def __init__(self):
        pass

    def try_exploit(self) -> int:
        pass
```

**Auditor Hint:** Use an instance variable `self.entered = False`. If `self.entered` is True, trip the trap! Otherwise, set `self.entered = True` and return 100.

---

### Problem 40: Predictable Randomness Manipulation
**Difficulty:** Easy | **Topic:** Modulo Math

**Description:**
Blockchains cannot easily generate random numbers. If a casino contract uses `block_timestamp % 10` to decide if you win (win if == 7).
You are an attacker. You can see the `upcoming_timestamps` (a list of integers representing the exact times the next blocks will be mined).
Return a list of strictly the block timestamps you should submit your transaction on to guarantee a 100% win rate.

**Constraints:**
- `1 <= len(upcoming_timestamps) <= 100`

**Example 1:**
```python
Input: upcoming_timestamps = [1234560, 1234567, 1234569, 1234577]
Output: [1234567, 1234577]
Explanation: Only timestamps ending in 7 will result in `ts % 10 == 7`. 
```

**Starter Code:**
```python
def exploit_casino(upcoming_timestamps: list[int]) -> list[int]:
    pass
```

**Auditor Hint:** List comprehension. `[ts for ts in upcoming_timestamps if ts % 10 == 7]`.
