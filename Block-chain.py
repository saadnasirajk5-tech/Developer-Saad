import hashlib 
import json  
import time  

class Block:
    def __init__(self, index, transactions, previous_has):
        self.index = index 
        self.timestamp = time.time() 
        self.transactions = transactions 
        self.previous_hash = previous_hash
        self.nonce = 0 
        self.hash = self.calculate_hash() 
        
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,                   
            "timestamp": self.timestamp,           
            "transactions": self.transactions,    
            "previous_hash": self.previous_hash,   
            "nonce": self.nonce                    
        }, sort_keys=True) 
        return hashlib.sha256(
            block_string.encode()
        ).hexdigest()
        
    def mine_block(self, difficulty):
        target = "0" * difficulty 
        print(f"\n Mining block #{self.index}...")  
        start_time - time.time() 
        while self.hash[:difficulty] != target:
            self.nonce += 1 
            self.hash = self.calculate_hash() 
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            print(f"  Block #{self.index} mined!")
            print(f"  Nonce found  : {self.nonce}")  
            print(f"     Hash         : {self.hash}")
            print(f"     Time taken   : {time_taken} seconds") 
            
    def __repr__(self):
        return (
            f"\n{'='*60}\n"                                          # Separator line
            f"   Block #{self.index}\n"                            # Block number
            f"{'='*60}\n"                                            # Separator line
            f"  Timestamp      : {time.ctime(self.timestamp)}\n"     # Human-readable time
            f"  Transactions   : {json.dumps(self.transactions, indent=2)}\n"  # Pretty transactions
            f"  Previous Hash  : {self.previous_hash}\n"             # Link to previous block
            f"  Nonce          : {self.nonce}\n"                     # The nonce that was found
            f"  Hash           : {self.hash}\n"                      # This block's hash
            f"{'='*60}"                                              # Separator line
        )

class Blockchain: 
    def __init__(self, difficulty=4):
        self.chains = []
        self.difficulty = difficulty   
        self.pending_transactions = []
        self.mining_reward = 6.25
        self.create_genesis_block() 
        def create_genesis_block(self):
            genesis_block = Block(
                index=0,
                transactions=[{               
                "sender": "GOD",
                "receiver": "Satoshi",
                "amount": 50,
                "message": "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"
                }],
                previous_hash="0" * 64 
            )
            genesis_block.mine_block(self.difficulty)
            self.chain.append(genesis_block)
            
        def get_latest_block(self):
             return self.chain[-1]  
         
        def add_transaction(self, sender, receiver, amount):
            if not sender or not receiver:
                  print("   ERROR: Transaction must have a sender and receiver!")
                  return False 
            if amount <= 0:                            # Amount must be positive
                print("   ERROR: Transaction amount must be greater than zero!")
                return False                           # Reject the transaction
        # --- If valid, create the transaction and add to pending list ---
            transaction = {                            # Create a transaction dictionary
               "sender": sender,                      # Who is sending the Bitcoin
               "receiver": receiver,                  # Who is receiving the Bitcoin
               "amount": amount,                      # How much Bitcoin is being sent
               "timestamp": time.time()               # When the transaction was created
            }
            self.pending_transactions.append(transaction)  # Add to the waiting list
            print(f"   Transaction added: {sender} → {receiver} : {amount} BTC")
            return True                                # Transaction accepted!  
        
        def mine_pending_transactions(self, miner_address):
            reward_tx = {
                "sender":"NETWORK",
                "receiver": miner_address,
                "amount":self.mining_reward,
                "time_stamp": time.time(),
                "type": "MINING_REWARD"
                }
            self.pending_transactions.append(reward_tx) 
            new_block = Block(
                index =len(self.chain),
                transactions=self.pending_transactions,
                previous_hash=self.get_latest_block().hash
            )
            new_block.mine_block(self.difficulty)
            self.chain.append(new_block)
            print(f" Block #{new_block.index} added to the blockchain!")
            print(f" Mining reward of {self.mining_reward} BTC sent to {miner_address}")
            self.pending_transactions = [] 
        
        def get_balance(self, address):
            balance = 0.0 
            for block in self.chain:
                for tx in block.transactions:
                    if tx["sender"] == address:
                        balance -= tx["amount"] 
                    if tx["receiver"] == address::
                        balance += tx["amount"]
            return balance 
        def is_chain_valid(self):
            print("\n🔍 Validating blockchain integrity...\n")
            for i in range(1, len(self.chain)):
                current_block = self.chain[i] 
                previous_block = self.chain[i-1] 
                if current_block.hash != current_block.calculate_hash():
                    print(f"     Block #{i} has been TAMPERED with! Hash is invalid!")
                    print(f"     Stored hash    : {current_block.hash}")
                    print(f"     Calculated hash: {current_block.calculate_hash()}")
                    return False  
                if current_block.previous_hash != previous_block.hash:
                    print(f"     Block #{i} chain link is BROKEN!")
                    print(f"     Points to      : {current_block.previous_hash}")
                    print(f"     Should point to: {previous_block.hash}")
                    return False   
                if current_block.hash[:self.difficulty] != "0" * self.difficulty:
                    print(f"   Block #{i} was not properly mined!")
                    return False                       # Chain is BROKEN!

            print(f"   Block #{i} is valid")     # This block passed all checks
        print("\n   BLOCKCHAIN IS VALID! All blocks verified.\n")
        return True 
            
        def print_chain(self):
            print("\n" + "🔗" * 30)
            print("       ⛓️  COMPLETE BLOCKCHAIN  ⛓️")
            print("🔗" * 30)
            for block in self.chain:        
                # Loop through each block
                print(block)    
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




















