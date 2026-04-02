# Level 5: Expert System Architecture (Problems 41-50)

System Architecture problems blend Blockchain mechanics with advanced algorithmic logic. You'll build simulations of real-world protocols like Uniswap DEXs, DAO Governance voting, and AI Consensus mechanisms.

---

### Problem 41: Automated Market Maker (AMM) Constant Product Swap
**Difficulty:** Medium | **Topic:** Math, Simulation

**Description:**
Decentralized Exchanges (like Uniswap) don't use order books. They use the Constant Product Formula: `x * y = k`.
You are given a Liquidity Pool with `reserve_x` and `reserve_y` tokens. A user wants to swap `amount_in` of Token X for Token Y. 
The exchange charges a **0.3% fee** on the incoming `amount_in` BEFORE calculating the swap. 
Calculate exactly how much Token Y the user will receive such that `(reserve_x + amount_in_after_fee) * (reserve_y - amount_out) == (reserve_x * reserve_y)`.
*(Assume integer truncation for simplicity, return the integer amount_out).*

**Constraints:**
- `1000 <= reserve_x, reserve_y <= 10^9`
- `1 <= amount_in <= reserve_x`

**Example 1:**
```python
Input: reserve_x = 10000, reserve_y = 10000, amount_in = 1000
Output: 906
Explanation: Fee is 0.3% of 1000 = 3. amount_in_after_fee = 997.
New reserve_x = 10997.
K = 10000 * 10000 = 100,000,000.
New reserve_y = 100,000,000 / 10997 = 9093.389
amount_out = 10000 - 9093.389 = 906.61
Truncated to integer: 906.
```

**Starter Code:**
```python
def swap_amm(reserve_x: int, reserve_y: int, amount_in: int) -> int:
    pass
```

**Auditor Hint:** `amount_in_after_fee = amount_in * 997 // 1000`. `k = reserve_x * reserve_y`. `new_x = reserve_x + amount_in_after_fee`. `new_y = k // new_x`. Return `reserve_y - new_y`.

---

### Problem 42: Voting Escrow (veToken) Decay
**Difficulty:** Medium | **Topic:** Time-based simulation

**Description:**
Many DAOs use a "Vote-Escrow" system (like veCRV) where users lock their tokens to get voting power. The longer you lock, the more power you get. However, this power decays linearly over time as your unlock date approaches.
Given an initial `lock_amount` (max 4 years multiplier = 4x power), a `lock_timestamp`, and an `unlock_timestamp`, calculate the user's current voting power exactly at `current_timestamp`.
Assume max lock is exactly `4 * 365 * 24 * 60 * 60` seconds. Return 0 if `current_timestamp > unlock_timestamp`.

**Constraints:**
- `0 <= lock_amount <= 10^6`
- Timestamps are standard Unix ints.

**Example 1:**
```python
Input: lock_amount = 100, lock_timestamp = 0, unlock_timestamp = 126144000 (4 years), current_timestamp = 63072000 (2 years)
Output: 200
Explanation: At 4 years remaining they get 4x power (400). At 2 years remaining, power linearly decays to 2x (200).
```

**Starter Code:**
```python
def calculate_ve_power(lock_amount: int, lock_timestamp: int, unlock_timestamp: int, current_timestamp: int) -> int:
    pass
```

**Auditor Hint:** Find `time_remaining = unlock_timestamp - current_timestamp`. Use cross-multiplication. `multiplier = (time_remaining / MAX_LOCK_TIME) * 4.0`.

---

### Problem 43: Model Ensembling (The AI Jury)
**Difficulty:** Easy | **Topic:** Weighted Averages

**Description:**
A single AI Model might hallucinate. To protect users, you query 3 different models. 
Each model returns a `confidence_score` (0.0 to 1.0) predicting if a smart contract is a scam.
You are given an array of tuples `[(score, weight)]`. Calculate the final weighted average score. If the weighted average is `>= 0.85`, return `True` (Scam), else `False`.

**Constraints:**
- `len(models) == 3`
- `0.0 <= score <= 1.0`
- `1 <= weight <= 10`

**Example 1:**
```python
Input: models = [(0.9, 10), (0.1, 1), (0.95, 5)]
Output: True
Explanation: Total weighted score = (0.9*10 + 0.1*1 + 0.95*5) / (10 + 1 + 5) = (9 + 0.1 + 4.75) / 16 = 13.85 / 16 = 0.865. Since 0.865 >= 0.85, return True.
```

**Starter Code:**
```python
def is_scam_weighted(models: list[tuple[float, int]]) -> bool:
    pass
```

**Auditor Hint:** Standard sum of (score*weight) divided by sum of (weights).

---

### Problem 44: Flashbots Sealed-Bid Batch Matcher
**Difficulty:** Hard | **Topic:** Arrays, Two Pointers (Greedy)

**Description:**
Flashbots allows developers to privately bid on transaction insertion bundles to avoid public mempool front-running.
You have `N` empty slots in a block. You receive `M` bundled bids as an array `bids` where each bid is `[slots_required, ether_bribe]`.
Your goal is to accept exactly the combination of bids that maximizes total ETH bribe while ensuring the total `slots_required` <= `N`. You cannot split a bid! This is an optimized version of Problem 10.

**Constraints:**
- `1 <= N <= 1000`
- `1 <= M <= 500`

**Example 1:**
```python
Input: N = 5, bids = [[3, 10], [2, 5], [4, 15], [1, 2]]
Output: 17
Explanation: Pick index 2 (requires 4 slots, bribe 15) and index 3 (requires 1 slot, bribe 2). Total slots = 5. Total Bribe = 17. 
```

**Starter Code:**
```python
def optimize_flashbot_bundle(N: int, bids: list[list[int]]) -> int:
    pass
```

**Auditor Hint:** Standard 0/1 Knapsack dynamic programming. Build an array `dp` of size `N+1` initialized to 0. For each bid, iterate backwards through `dp` and update max bribes.

---

### Problem 45: DAO Governance Tally (Quorum Control)
**Difficulty:** Medium | **Topic:** Logic Arrays

**Description:**
A DAO Proposal only passes if `< 50%` of the votes are NOT "Against" AND the total voter turnout (quorum) is `>= minimum_quorum`.
You are given total `circulating_supply`, `minimum_quorum` tokens, and an array of `votes` shaped `{"voter_id": int, "balance": int, "choice": "FOR" | "AGAINST" | "ABSTAIN"}`.
A user can only vote once. Return `True` if it passes, `False` otherwise.

**Constraints:**
- `1 <= len(votes) <= 10^4`

**Example 1:**
```python
Input: circulating = 1000, minimum_quorum = 200
votes = [{"voter": 1, "balance": 100, "choice": "FOR"}, {"voter": 2, "balance": 50, "choice": "AGAINST"}, {"voter": 3, "balance": 60, "choice": "ABSTAIN"}]
Output: True
Explanation: Total turnout = 100 + 50 + 60 = 210. 210 >= 200 (Quorum met). 
"FOR" = 100. "AGAINST" = 50. Since 100 > 50, it passes. "ABSTAIN" counts towards turnout but not towards the For/Against ratio.
```

**Starter Code:**
```python
def process_dao_proposal(circulating: int, minimum_quorum: int, votes: list[dict]) -> bool:
    pass
```

**Auditor Hint:** Use a dictionary to prevent double voting. Add balances conditionally based on the choice string. Check the math at the end!

---

### Problem 46: Gossip Protocol Node Propagation (Graph BFS)
**Difficulty:** Medium | **Topic:** Graphs, BFS

**Description:**
Blockchains use a "Gossip Protocol". A node gets a block and randomly whispers it to its peers, causing exponential spread.
Given `n` nodes (0 to n-1), an array of `connections` (undirected edges), and a `start_node`. Each node takes exactly `1 tick` to send the block to ALL its direct connections simultaneously.
Find the minimum number of `ticks` it takes for ALL `n` nodes to receive the block. If a node is isolated and can never be reached, return `-1`.

**Constraints:**
- `1 <= n <= 1000`

**Example 1:**
```python
Input: n = 4, connections = [[0,1], [1,2], [2,3]], start_node = 0
Output: 3
Explanation: 
Tick 1: 0 sends to 1.
Tick 2: 1 sends to 2.
Tick 3: 2 sends to 3. All secure!
```

**Starter Code:**
```python
def find_gossip_time(n: int, connections: list[list[int]], start_node: int) -> int:
    pass
```

**Auditor Hint:** Build an adjacency list. Use a queue initialized with `(start_node, 0)` containing the node and the tick depth. Breadth First Search (BFS) guarantee shortest paths.

---

### Problem 47: Slashing Un-Synced Validators (Proof of Stake)
**Difficulty:** Medium | **Topic:** Hash Maps, Grouping

**Description:**
Validators in Ethereum 2.0 must sign blocks. If a Validator signs two *different* blocks at the exact same `block_height`, they are malicious and get "Slashed" (their funds are destroyed).
Given an array `signatures` where each element is `[validator_id, block_height, block_hash]`, return a sorted list of all `validator_id`s that must be slashed.

**Constraints:**
- `1 <= len(signatures) <= 10^5`

**Example 1:**
```python
Input: signatures = [
  [1, 100, "hashA"], 
  [2, 100, "hashA"], 
  [1, 101, "hashB"], 
  [1, 100, "hashX"]
]
Output: [1]
Explanation: Validator 1 signed both "hashA" and "hashX" for block height 100. Slashed! Validator 2 only signed once.
```

**Starter Code:**
```python
def find_slashable_validators(signatures: list[list]) -> list[int]:
    pass
```

**Auditor Hint:** Use a dictionary like `tracker[validator_id][block_height] = set([block_hash])`. Iterate through the results and if any set length is > 1, add them to the slashed list.

---

### Problem 48: ZK-Rollup Proof Simulator
**Difficulty:** Easy | **Topic:** Trees, State Roots

**Description:**
Zero-Knowledge rollups bundle data for cheap verification. 
Instead of sending 10 transaction balances, you send the final "State Root Hash".
Given a list of strings `balances` representing a rollup state, generate the final "State Root". To do this cleanly, sort the list alphabetically, concatenate it exactly as one string, and return the `md5` hash.

**Constraints:**
- `1 <= len(balances) <= 10^4`

**Example 1:**
```python
Input: balances = ["Alice:100", "Bob:20", "Charlie:50"]
Output: "dc2b1d3d63c434... (md5 of 'Alice:100Bob:20Charlie:50')"
```

**Starter Code:**
```python
import hashlib

def generate_rollup_root(balances: list[str]) -> str:
    pass
```

**Auditor Hint:** `.sort()`, `"".join()`, and `.encode('utf-8')` to `.hexdigest()`.

---

### Problem 49: Yield Farming Vault Router
**Difficulty:** Medium | **Topic:** Comparison Logic

**Description:**
You are the Yearn Finance router. You have `capital` to invest.
You have an array of `vaults` where each is `[vault_id, apy_percentage, gas_fee_to_enter]`.
Calculate the absolute projected profit for 1 year for each vault: `(capital * apy_percentage / 100) - gas_fee_to_enter`.
Return the `vault_id` that yields the highest absolute profit. If all yield a negative profit (due to high gas fees), return `-1`. If there is a tie, return the vault with the lowest `vault_id`.

**Constraints:**
- `1 <= len(vaults) <= 100`

**Example 1:**
```python
Input: capital = 1000, vaults = [[1, 10, 50], [2, 5, 10], [3, 20, 250]]
Output: 1
Explanation: 
Vault 1: (1000 * 0.1) - 50 = 100 - 50 = 50 profit.
Vault 2: (1000 * 0.05) - 10 = 50 - 10 = 40 profit.
Vault 3: (1000 * 0.20) - 250 = 200 - 250 = -50 profit.
Vault 1 is the winner.
```

**Starter Code:**
```python
def find_best_vault(capital: int, vaults: list[list[int]]) -> int:
    pass
```

**Auditor Hint:** Standard loop tracking `max_profit` and `best_id`.

---

### Problem 50: Exponential Backoff (RPC Failures)
**Difficulty:** Easy | **Topic:** Loops, Retries

**Description:**
When an AI bot tries to scrape data from a busy blockchain node, the connection often drops.
You must implement standard "Exponential Backoff". 
You are given a list `endpoints` which are booleans (True = online, False = offline).
You start with a `wait_time` of 1 second. You try `endpoints[0]`. If it is `False`, you "wait" (add `wait_time` to `total_time`), then double the `wait_time`. Then move to the next endpoint `endpoints[1]`.
Return the `total_time` accumulated until you hit your first `True`. If you finish the array without hitting `True`, return `-1`.

**Example 1:**
```python
Input: endpoints = [False, False, False, True, False]
Output: 7
Explanation: 
Try 0: False. Wait 1s. total = 1. wait_time = 2.
Try 1: False. Wait 2s. total = 3. wait_time = 4.
Try 2: False. Wait 4s. total = 7. wait_time = 8.
Try 3: True! Return total (7).
```

**Starter Code:**
```python
def exponential_backoff_timer(endpoints: list[bool]) -> int:
    pass
```

**Auditor Hint:** `total_time`, `wait_time = 1`, loop through the array. If `True`, break and return. Else, add, multiply, and continue.
