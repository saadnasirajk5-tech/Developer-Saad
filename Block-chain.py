# ======================================================================
# 🔗 BITCOIN-STYLE BLOCKCHAIN — Built from Scratch in Python
# ======================================================================
# This program simulates how Bitcoin's blockchain works:
#   1. Blocks hold transactions (like a page in a ledger)
#   2. Each block is linked to the previous one via a hash (a chain!)
#   3. Mining uses "Proof of Work" — finding a special number (nonce)
#   4. Tampering with ANY block breaks the entire chain
# ======================================================================

# --- IMPORTS -----------------------------------------------------------
import hashlib  # Used for SHA-256 hashing (same algorithm Bitcoin uses!)
import json     # Used to convert block data into a string format
import time     # Used to timestamp each block (when it was created)

# ======================================================================
# 🧱 CLASS: Block
# Represents a SINGLE block in the blockchain (like one page in a ledger)
# ======================================================================
class Block:

    # ------------------------------------------------------------------
    # CONSTRUCTOR: Called when a new Block is created
    # ------------------------------------------------------------------
    def __init__(self, index, transactions, previous_hash):
        self.index = index                  # The block's position in the chain (0, 1, 2, ...)
        self.timestamp = time.time()        # Exact time the block was created (Unix timestamp)
        self.transactions = transactions    # List of transactions stored in this block
        self.previous_hash = previous_hash  # Hash of the PREVIOUS block (this creates the "chain")
        self.nonce = 0                      # A number miners change to find a valid hash (Proof of Work)
        self.hash = self.calculate_hash()   # This block's own hash (its unique fingerprint)

    # ------------------------------------------------------------------
    # METHOD: calculate_hash
    # Creates a SHA-256 hash of all the block's contents
    # Think of it as a unique FINGERPRINT for the block
    # If you change even ONE character, the hash completely changes!
    # ------------------------------------------------------------------
    def calculate_hash(self):
        # Step 1: Combine ALL block data into one big string
        block_string = json.dumps({                # json.dumps converts dict -> string
            "index": self.index,                   # Include the block number
            "timestamp": self.timestamp,           # Include the timestamp
            "transactions": self.transactions,     # Include all transactions
            "previous_hash": self.previous_hash,   # Include previous block's hash
            "nonce": self.nonce                     # Include the nonce (changes during mining)
        }, sort_keys=True)                         # sort_keys=True ensures consistent ordering

        # Step 2: Feed that string into SHA-256 and return the hex digest
        return hashlib.sha256(                     # SHA-256 = Secure Hash Algorithm (256-bit)
            block_string.encode()                  # .encode() converts string to bytes (required by hashlib)
        ).hexdigest()                              # .hexdigest() returns hash as a readable hex string

    # ------------------------------------------------------------------
    # METHOD: mine_block
    # This is PROOF OF WORK — the core of Bitcoin mining!
    # The miner must find a nonce that makes the hash start with
    # a certain number of zeros (the "difficulty")
    # Higher difficulty = more zeros needed = harder to mine
    # ------------------------------------------------------------------
    def mine_block(self, difficulty):
        # Create the target: a string of zeros the hash must START with
        target = "0" * difficulty                  # e.g., difficulty=4 means hash must start with "0000"

        # Keep trying different nonce values until we find a valid hash
        print(f"\n  ⛏️  Mining block #{self.index}...")  # Let the user know mining has started
        start_time = time.time()                           # Record when mining started

        while self.hash[:difficulty] != target:    # Loop until hash starts with enough zeros
            self.nonce += 1                        # Try the next nonce (0, 1, 2, 3, ... millions!)
            self.hash = self.calculate_hash()      # Recalculate hash with new nonce

        end_time = time.time()                     # Record when mining finished
        time_taken = round(end_time - start_time, 2)  # Calculate how long mining took

        # Mining is done! Print the results
        print(f"  ✅ Block #{self.index} mined!")
        print(f"     Nonce found  : {self.nonce}")           # The magic number that worked
        print(f"     Hash         : {self.hash}")            # The valid hash
        print(f"     Time taken   : {time_taken} seconds")   # How long it took

    # ------------------------------------------------------------------
    # METHOD: __repr__
    # This controls how the block looks when you print it
    # ------------------------------------------------------------------
    def __repr__(self):
        return (
            f"\n{'='*60}\n"                                          # Separator line
            f"  📦 Block #{self.index}\n"                            # Block number
            f"{'='*60}\n"                                            # Separator line
            f"  Timestamp      : {time.ctime(self.timestamp)}\n"     # Human-readable time
            f"  Transactions   : {json.dumps(self.transactions, indent=2)}\n"  # Pretty transactions
            f"  Previous Hash  : {self.previous_hash}\n"             # Link to previous block
            f"  Nonce          : {self.nonce}\n"                     # The nonce that was found
            f"  Hash           : {self.hash}\n"                      # This block's hash
            f"{'='*60}"                                              # Separator line
        )


# ======================================================================
# ⛓️ CLASS: Blockchain
# Represents the ENTIRE chain of blocks
# This is the "distributed ledger" — the heart of Bitcoin
# ======================================================================
class Blockchain:

    # ------------------------------------------------------------------
    # CONSTRUCTOR: Initialize the blockchain
    # ------------------------------------------------------------------
    def __init__(self, difficulty=4):
        self.chain = []                    # The list that holds ALL blocks in order
        self.difficulty = difficulty        # Mining difficulty (how many leading zeros needed)
        self.pending_transactions = []     # Transactions waiting to be added to the next block
        self.mining_reward = 6.25          # Reward for mining a block (like Bitcoin's block reward!)
        self.create_genesis_block()        # Create the very first block (Genesis Block)

    # ------------------------------------------------------------------
    # METHOD: create_genesis_block
    # The Genesis Block is the FIRST block in any blockchain
    # It has no previous hash (because there's no block before it!)
    # Bitcoin's genesis block was created by Satoshi Nakamoto on Jan 3, 2009
    # ------------------------------------------------------------------
    def create_genesis_block(self):
        genesis_block = Block(             # Create a new Block object
            index=0,                       # It's block #0 (the first one)
            transactions=[{                # A special message, just like Bitcoin's genesis block
                "sender": "GOD",
                "receiver": "Satoshi",
                "amount": 50,
                "message": "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"
            }],
            previous_hash="0" * 64         # No previous block, so we use 64 zeros
        )
        genesis_block.mine_block(self.difficulty)  # Mine it (find a valid hash)
        self.chain.append(genesis_block)           # Add it to the chain

    # ------------------------------------------------------------------
    # METHOD: get_latest_block
    # Returns the most recent block in the chain
    # We need this to get the previous_hash for the next block
    # ------------------------------------------------------------------
    def get_latest_block(self):
        return self.chain[-1]              # [-1] gets the LAST item in the list

    # ------------------------------------------------------------------
    # METHOD: add_transaction
    # Adds a new transaction to the pending list
    # Transactions wait here until a miner includes them in a block
    # ------------------------------------------------------------------
    def add_transaction(self, sender, receiver, amount):
        # --- VALIDATION: Make sure the transaction is legit ---
        if not sender or not receiver:             # Sender and receiver must exist
            print("  ❌ ERROR: Transaction must have a sender and receiver!")
            return False                           # Reject the transaction

        if amount <= 0:                            # Amount must be positive
            print("  ❌ ERROR: Transaction amount must be greater than zero!")
            return False                           # Reject the transaction

        # --- If valid, create the transaction and add to pending list ---
        transaction = {                            # Create a transaction dictionary
            "sender": sender,                      # Who is sending the Bitcoin
            "receiver": receiver,                  # Who is receiving the Bitcoin
            "amount": amount,                      # How much Bitcoin is being sent
            "timestamp": time.time()               # When the transaction was created
        }
        self.pending_transactions.append(transaction)  # Add to the waiting list
        print(f"  📝 Transaction added: {sender} → {receiver} : {amount} BTC")
        return True                                # Transaction accepted!

    # ------------------------------------------------------------------
    # METHOD: mine_pending_transactions
    # A miner takes all pending transactions, puts them in a block,
    # and mines it (finds a valid hash through Proof of Work)
    # The miner gets a REWARD for their work (new Bitcoin is created!)
    # ------------------------------------------------------------------
    def mine_pending_transactions(self, miner_address):
        # Step 1: Add the mining reward transaction
        # This is how NEW Bitcoin enters the system! (called a "coinbase transaction")
        reward_tx = {
            "sender": "NETWORK",                   # The Bitcoin network itself sends the reward
            "receiver": miner_address,             # The miner who did the work gets paid
            "amount": self.mining_reward,           # The reward amount (currently 6.25 BTC in real Bitcoin)
            "timestamp": time.time(),              # When the reward was given
            "type": "MINING_REWARD"                # Label it as a reward
        }
        self.pending_transactions.append(reward_tx)  # Add reward to pending transactions

        # Step 2: Create a new block with all pending transactions
        new_block = Block(
            index=len(self.chain),                     # Block number = current chain length
            transactions=self.pending_transactions,    # Include ALL pending transactions
            previous_hash=self.get_latest_block().hash # Link to the previous block's hash
        )

        # Step 3: Mine the block (find a valid Proof of Work)
        new_block.mine_block(self.difficulty)       # This is where the heavy computation happens!

        # Step 4: Add the mined block to the chain
        self.chain.append(new_block)               # The block is now part of the permanent chain!
        print(f"  🎉 Block #{new_block.index} added to the blockchain!")
        print(f"  💰 Mining reward of {self.mining_reward} BTC sent to {miner_address}")

        # Step 5: Clear pending transactions (they're now in a block)
        self.pending_transactions = []             # Reset the pending list

    # ------------------------------------------------------------------
    # METHOD: get_balance
    # Calculates the balance of any address by scanning ALL transactions
    # in the ENTIRE blockchain (just like Bitcoin does!)
    # ------------------------------------------------------------------
    def get_balance(self, address):
        balance = 0.0                              # Start with zero balance

        # Loop through EVERY block in the chain
        for block in self.chain:
            # Loop through EVERY transaction in each block
            for tx in block.transactions:
                if tx["sender"] == address:        # If this address SENT money...
                    balance -= tx["amount"]         # ...subtract the amount (money going OUT)
                if tx["receiver"] == address:      # If this address RECEIVED money...
                    balance += tx["amount"]         # ...add the amount (money coming IN)

        return balance                             # Return the final balance

    # ------------------------------------------------------------------
    # METHOD: is_chain_valid
    # Checks if the ENTIRE blockchain is valid and hasn't been tampered with
    # This is what makes blockchain SECURE — you can't cheat!
    # ------------------------------------------------------------------
    def is_chain_valid(self):
        print("\n🔍 Validating blockchain integrity...\n")

        # Loop through every block (skip genesis block at index 0)
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]          # The block we're checking
            previous_block = self.chain[i - 1]     # The block before it

            # CHECK 1: Recalculate the hash and see if it still matches
            # If someone changed data in the block, the hash would be different!
            if current_block.hash != current_block.calculate_hash():
                print(f"  ❌ Block #{i} has been TAMPERED with! Hash is invalid!")
                print(f"     Stored hash    : {current_block.hash}")
                print(f"     Calculated hash: {current_block.calculate_hash()}")
                return False                       # Chain is BROKEN!

            # CHECK 2: Verify the chain link — does this block correctly
            # point to the previous block's hash?
            if current_block.previous_hash != previous_block.hash:
                print(f"  ❌ Block #{i} chain link is BROKEN!")
                print(f"     Points to      : {current_block.previous_hash}")
                print(f"     Should point to: {previous_block.hash}")
                return False                       # Chain is BROKEN!

            # CHECK 3: Verify the hash meets the difficulty requirement
            if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                print(f"  ❌ Block #{i} was not properly mined!")
                return False                       # Chain is BROKEN!

            print(f"  ✅ Block #{i} is valid")     # This block passed all checks

        print("\n  🏆 BLOCKCHAIN IS VALID! All blocks verified.\n")
        return True                                # Entire chain is legit!

    # ------------------------------------------------------------------
    # METHOD: print_chain
    # Displays the entire blockchain in a readable format
    # ------------------------------------------------------------------
    def print_chain(self):
        print("\n" + "🔗" * 30)
        print("       ⛓️  COMPLETE BLOCKCHAIN  ⛓️")
        print("🔗" * 30)
        for block in self.chain:                   # Loop through each block
            print(block)                           # Print it (uses __repr__ method)


# ======================================================================
# 🚀 MAIN PROGRAM — Let's run the blockchain!
# ======================================================================
if __name__ == "__main__":

    # --------------------------------------------------
    # STEP 1: Create a new blockchain
    # --------------------------------------------------
    print("\n" + "🌟" * 30)
    print("   CREATING A NEW BLOCKCHAIN")
    print("🌟" * 30)

    btc = Blockchain(difficulty=4)                 # Create blockchain with difficulty of 4
                                                   # (hash must start with "0000")

    # --------------------------------------------------
    # STEP 2: Add some transactions
    # --------------------------------------------------
    print("\n" + "💸" * 30)
    print("   ADDING TRANSACTIONS")
    print("💸" * 30)

    # Simulate people sending Bitcoin to each other
    btc.add_transaction("Alice", "Bob", 5.0)       # Alice sends 5 BTC to Bob
    btc.add_transaction("Bob", "Charlie", 2.5)     # Bob sends 2.5 BTC to Charlie
    btc.add_transaction("Charlie", "Alice", 1.0)   # Charlie sends 1 BTC back to Alice

    # --------------------------------------------------
    # STEP 3: Mine the first block of transactions
    # --------------------------------------------------
    print("\n" + "⛏️ " * 20)
    print("   MINING BLOCK #1")
    print("⛏️ " * 20)

    btc.mine_pending_transactions("Miner_Joe")     # Miner Joe mines the block and gets rewarded

    # --------------------------------------------------
    # STEP 4: Add more transactions and mine again
    # --------------------------------------------------
    print("\n" + "💸" * 30)
    print("   MORE TRANSACTIONS")
    print("💸" * 30)

    btc.add_transaction("Alice", "David", 3.0)     # Alice sends 3 BTC to David
    btc.add_transaction("David", "Bob", 1.0)       # David sends 1 BTC to Bob
    btc.add_transaction("Eve", "Alice", 7.5)       # Eve sends 7.5 BTC to Alice

    print("\n" + "⛏️ " * 20)
    print("   MINING BLOCK #2")
    print("⛏️ " * 20)

    btc.mine_pending_transactions("Miner_Sara")    # Miner Sara mines the next block

    # --------------------------------------------------
    # STEP 5: Check balances
    # --------------------------------------------------
    print("\n" + "💰" * 30)
    print("   ACCOUNT BALANCES")
    print("💰" * 30)

    # Print everyone's balance
    people = ["Alice", "Bob", "Charlie", "David", "Eve", "Miner_Joe", "Miner_Sara"]
    for person in people:                          # Loop through each person
        balance = btc.get_balance(person)          # Calculate their balance
        print(f"  👤 {person:12s} : {balance:>10.2f} BTC")  # Print formatted balance

    # --------------------------------------------------
    # STEP 6: Print the entire blockchain
    # --------------------------------------------------
    btc.print_chain()                              # Display all blocks

    # --------------------------------------------------
    # STEP 7: Validate the blockchain
    # --------------------------------------------------
    btc.is_chain_valid()                           # Check if everything is legit

    # --------------------------------------------------
    # STEP 8: Try to HACK the blockchain! 😈
    # --------------------------------------------------
    print("\n" + "🏴‍☠️ " * 20)
    print("   ATTEMPTING TO HACK THE BLOCKCHAIN!")
    print("🏴‍☠️ " * 20)

    print("\n  😈 Changing Block #1 transaction: Bob now 'received' 1000 BTC...")
    btc.chain[1].transactions[0]["amount"] = 1000  # Tamper with a transaction!

    # Now validate again — it should FAIL!
    btc.is_chain_valid()                           # This will detect the tampering!

    print("  🛡️  The blockchain detected the hack! That's the power of hashing!\n")



















