# Level 1: Foundational Logic & State Security (Problems 1-10)

These are complete, Leetcode-style challenges. You must handle constraints, account for edge cases (like negative numbers or massive arrays), and structure your code safely. Try to write the solution in Python!

---

### Problem 1: The Token Bank Vulnerability
**Difficulty:** Medium | **Topic:** State Management & Edge Cases

**Description:**
You are hired to build the core balance tracking system for a new smart contract bank. Write a class `TokenBank` that securely tracks balances. You must prevent users from withdrawing more than they have, or depositing negative amounts (which simulates an integer underflow vulnerability).

Implement the `TokenBank` class:
- `TokenBank()` Initializes the object with an empty state.
- `deposit(str user, int amount) -> bool` Adds `amount` to the user's balance. Returns `True` if successful, or `False` if the amount is malicious (<= 0).
- `withdraw(str user, int amount) -> bool` Subtracts `amount` from the user's balance. Returns `False` if they don't have enough tokens, or if the amount is <= 0. Otherwise returns `True`.

**Constraints:**
- `1 <= Number of API calls <= 10^4`
- `-10^9 <= amount <= 10^9`

**Example 1:**
```python
Input: 
calls = ["deposit", "withdraw", "withdraw", "deposit"]
values = [("Alice", 100), ("Alice", 50), ("Alice", 100), ("Bob", -50)]

Output: [True, True, False, False]

Explanation: 
- Alice deposits 100 (Success)
- Alice withdraws 50 (Success)
- Alice attempts to withdraw 100 (Fails: Currently has 50)
- Bob attempts to deposit -50 (Fails: Malicious negative amount)
```

**Starter Code:**
```python
class TokenBank:
    def __init__(self):
        pass
        
    def deposit(self, user: str, amount: int) -> bool:
        pass
        
    def withdraw(self, user: str, amount: int) -> bool:
        pass
```

**Auditor Hint:** Use a dictionary. Always check `if amount <= 0:` BEFORE touching state!

---

### Problem 2: Double-Spend Mempool Preventer
**Difficulty:** Easy | **Topic:** Sets, O(1) Lookups

**Description:**
In a blockchain, transactions sit in a "mempool" before being mined. Hackers often try to submit the exact same transaction ID (a "nonce") twice to trick the network into sending funds twice. 

Given a list of incoming string `transaction_ids`, write a function that returns a list of only the *new, unprocessesed* transactions in exactly the order they first appeared. Duplicate subsequent transactions should be completely ignored.

**Constraints:**
- `1 <= len(transaction_ids) <= 10^5`
- Transaction IDs are 64-character hexadecimal strings.

**Example 1:**
```python
Input: transaction_ids = ["0xabc", "0x123", "0xabc", "0x890"]
Output: ["0xabc", "0x123", "0x890"]
Explanation: The second "0xabc" is a double-spend attempt and is removed.
```

**Starter Code:**
```python
def filter_double_spends(transaction_ids: list[str]) -> list[str]:
    pass
```

**Auditor Hint:** Do not use `if i in result_list` because checking a list is O(N). For 10^5 items, your algo will timeout! Use a Python `set()` for O(1) lookups.

---

### Problem 3: Sliding Window API Rate Limiter
**Difficulty:** Medium | **Topic:** Sliding Window, Queues, AI APIs

**Description:**
LLM API endpoints need strict rate limiting to prevent DDOS attacks. You need to implement a rate limiter that prevents any single IP address from making more than `K` requests within the last `T` milliseconds.

Implement the `RateLimiter` class:
- `RateLimiter(int K, int T)` Initializes the object with the maximum requests `K` per time window `T`.
- `should_allow(str ip, int timestamp) -> bool` Returns `True` if the request is allowed, `False` otherwise. (Timestamps are strictly increasing).

**Constraints:**
- `1 <= K <= 100`
- `1000 <= T <= 60000`
- `1 <= timestamp <= 10^9`

**Example 1:**
```python
Input: 
K = 2, T = 1000  # Max 2 requests per 1000ms
calls = [
  ("should_allow", "1.1.1.1", 100),
  ("should_allow", "1.1.1.1", 500),
  ("should_allow", "1.1.1.1", 600),
  ("should_allow", "1.1.1.1", 1200)
]
Output: [True, True, False, True]
Explanation: 
At 100ms: Allowed (1st request).
At 500ms: Allowed (2nd request).
At 600ms: Denied (Limit is 2 per 1000ms. Since 100ms, we already have 2).
At 1200ms: Allowed (The 100ms request expired because 1200 - 1000 = 200. Only the 500ms request is active).
```

**Starter Code:**
```python
from collections import deque

class RateLimiter:
    def __init__(self, K: int, T: int):
        pass
        
    def should_allow(self, ip: str, timestamp: int) -> bool:
        pass
```

**Auditor Hint:** Keep a dictionary where the key is the `ip` and the value is a `collections.deque()` of timestamps. Pop old timestamps from the left of the deque!

---

### Problem 4: Circular Smart Contract Dependency
**Difficulty:** Hard | **Topic:** Graph Traversal, Cycle Detection

**Description:**
Smart Contract A calls Contract B, which calls Contract C. If Contract C accidentally calls Contract A, the blockchain enters an infinite loop, draining all gas! 

You are given a dictionary `dependencies` where `dependencies[i]` is a list of contracts that contract `i` calls. Return `True` if there is a circular dependency (an infinite loop) in the system, and `False` if it is safe.

**Constraints:**
- `1 <= Number of contracts <= 10^4`
- The input is represented as an adjacency list.

**Example 1:**
```python
Input: dependencies = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["E"],
    "D": ["A"],
    "E": []
}
Output: True
Explanation: A calls B -> B calls D -> D calls A. This forms a cycle. 
```

**Starter Code:**
```python
def has_infinite_loop(dependencies: dict[str, list[str]]) -> bool:
    pass
```

**Auditor Hint:** Use Depth First Search (DFS). Keep track of a `visited` set and a `currently_in_stack` set. If you visit a node that is already in your `currently_in_stack`, you have found a loop.

---

### Problem 5: The Merkle Leaf Pairer
**Difficulty:** Medium | **Topic:** Recursion, Trees

**Description:**
Blockchains summarize transactions by putting them in pairs and hashing them up a "Merkle Tree". 
You are given a list of strings `leaves`. You must group adjacent leaves together as strings `"(leaf1 + leaf2)"`. If there is an odd number of leaves, the last leaf pairs with itself! You repeat this process floor-by-floor until only 1 string remains.

Write a function that accepts `leaves` and returns the final Merkle Root string.

**Constraints:**
- `1 <= len(leaves) <= 100`
- Elements are small alphanumeric strings.

**Example 1:**
```python
Input: leaves = ["T1", "T2", "T3"]
Output: "((T1 + T2) + (T3 + T3))"

Explanation: 
Round 1: T1 and T2 pair -> "(T1 + T2)". T3 is alone, so it pairs with itself -> "(T3 + T3)". 
Round 2: The remaining two pair together to form the final root.
```

**Starter Code:**
```python
def calculate_merkle_root(leaves: list[str]) -> str:
    pass
```

**Auditor Hint:** Use recursion or a while loop `while len(current_layer) > 1:`. Build the next layer by walking in steps of 2. 

---

### Problem 6: Sybil Attack Connected Components
**Difficulty:** Medium | **Topic:** Union-Find / DSU

**Description:**
Airdrop hunters create thousands of wallets to claim free crypto. However, they are sloppy: Wallet A sends 0.01 ETH to Wallet B to pay for gas. Wallet B sends to Wallet C. 

You are given an integer `n` (number of wallets, labelled `0` to `n-1`), and a list `transfers` where `transfers[i] = [walletA, walletB]`. 
Return the total number of "Sybil Clusters" (distinct connected components). A cluster is any group of wallets connected directly or indirectly by transfers.

**Constraints:**
- `1 <= n <= 10^5`
- `0 <= len(transfers) <= 2 * 10^5`

**Example 1:**
```python
Input: n = 5, transfers = [[0,1], [1,2], [3,4]]
Output: 2
Explanation: Wallets {0, 1, 2} are one cluster. Wallets {3, 4} are another.
```

**Starter Code:**
```python
def count_sybil_clusters(n: int, transfers: list[list[int]]) -> int:
    pass
```

**Auditor Hint:** Implement a Disjoint Set Union (DSU) or run Breadth-First Search (BFS) from every unvisited wallet to count the separate groups!

---

### Problem 7: DEX Slippage Optimizer
**Difficulty:** Medium | **Topic:** Array Processing, Greedy Algo

**Description:**
You are routing a large trade through multiple Decentralized Exchanges (DEXs). You have a list of `pools`, where each `pool[i]` represents how much of Token X you will get for 1 Token Y on exchange `i`.
However, because of "slippage", every time you trade on the *same* pool sequentially, the exchange rate drops by `1.0`!

Given `pools` (a list of initial rates) and `K`, the number of trades you want to execute, find the maximum total Token X you can receive.

**Constraints:**
- `1 <= len(pools) <= 10^5`
- `1 <= K <= 10^5`
- `rates` are integers.

**Example 1:**
```python
Input: pools = [5, 10], K = 3
Output: 24
Explanation: 
- Trade 1: Pick pool 1 (Rate 10). Pool 1 drops to 9. Total = 10.
- Trade 2: Pick pool 1 (Rate 9). Pool 1 drops to 8. Total = 10 + 9 = 19.
- Trade 3: Pick pool 1 (Rate 8). Pool 1 drops to 7. Total = 19 + 8 = 27. Wait, pool 0 is 5. So we just pick the max available.
Actually, 10 + 9 + 8 = 27. (Let's assume the pool drops exactly by 1). 
If it was pools = [5, 10], K = 6. We would take 10, 9, 8, 7, 6, and then Pool 0 holds 5, Pool 1 holds 5. We can pick either.
```

**Starter Code:**
```python
def max_trade_output(pools: list[int], K: int) -> int:
    pass
```

**Auditor Hint:** If you sort the array or scan it `K` times, you will hit O(N*K) and timeout. Use Python's `heapq` (a Max-Heap). Multiply values by -1 to use Python's min-heap as a max-heap!

---

### Problem 8: The Reentrancy Audit (Valid Parentheses Variation)
**Difficulty:** Easy | **Topic:** Stacks

**Description:**
An EVM auditor is looking at a trace of contract calls. An external call entering a contract is noted as `[`, `{`, or `(`. The function successfully closing and returning is noted as `]`, `}`, or `)`. 

If a contract does not close perfectly in the right order, it means there is a reentrancy flow vulnerability. Given a string `trace`, return `True` if it is perfectly balanced, and `False` otherwise.

**Constraints:**
- `1 <= len(trace) <= 10^4`
- `trace` consists only of brackets `()[]{}`.

**Example 1:**
```python
Input: trace = "{[()]}"
Output: True
```

**Starter Code:**
```python
def is_secure_trace(trace: str) -> bool:
    pass
```

**Auditor Hint:** Standard Leetcode 20. Use a `list` as a Stack. Iterate through `trace`. Push open brackets. On closing bracket, pop and ensure they match!

---

### Problem 9: AI Context Window Truncator
**Difficulty:** Easy | **Topic:** String Manipulation

**Description:**
Large Language Models have a strict maximum "context window" limit measured in words. 
Given a string `prompt` and an integer `max_words`, return the truncated string containing exactly the first `max_words` words. If the prompt is shorter than `max_words`, return the original prompt.

**Constraints:**
- Words are separated by exactly one space.
- `1 <= max_words <= 1000`

**Example 1:**
```python
Input: prompt = "Determine the vulnerability in this smart contract logic", max_words = 4
Output: "Determine the vulnerability in"
```

**Starter Code:**
```python
def truncate_prompt(prompt: str, max_words: int) -> str:
    pass
```

**Auditor Hint:** Use `prompt.split(' ')` to turn it into an array, slice it `[:max_words]`, and then `' '.join()` it back together!

---

### Problem 10: EVM Gas Knapsack (0/1 Knapsack)
**Difficulty:** Hard | **Topic:** Dynamic Programming

**Description:**
You are a blockchain miner. You have a strict block gas limit of `max_gas`. You have a list of transactions waiting to be mined. Each transaction has a `gas_cost[i]` and a `bribe[i]` (how much ETH the user paid to prioritize it).

Find the maximum total `bribe` you can collect without exceeding `max_gas`. (You cannot take a fraction of a transaction; you either include it or you don't).

**Constraints:**
- `1 <= num_transactions <= 100`
- `1 <= max_gas <= 10^4`

**Example 1:**
```python
Input: max_gas = 10, gas_cost = [2, 3, 5, 7], bribe = [1, 5, 2, 4]
Output: 9
Explanation: We take transaction 1 (gas 3, bribe 5) and transaction 3 (gas 7, bribe 4). Total gas = 10, total bribe = 9.
```

**Starter Code:**
```python
def max_miner_bribe(max_gas: int, gas_cost: list[int], bribe: list[int]) -> int:
    pass
```

**Auditor Hint:** This is the famous 0/1 Knapsack algorithm! Use a 2D array or a 1D array of size `max_gas + 1` to track the maximum bribe possible at every gas capacity from 0 up to `max_gas`.
