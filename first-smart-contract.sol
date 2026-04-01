// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// This is a simple "Piggy Bank" smart contract
contract PiggyBank {
    
    // STATE VARIABLES (stored permanently on blockchain)
    address public owner;          // Who created this piggy bank
    uint256 public totalSaved;     // How much is saved
    
    // CONSTRUCTOR (runs ONCE when contract is deployed)
    constructor() {
        owner = msg.sender;  // whoever deploys this becomes owner
    }
    
    // FUNCTION: Anyone can deposit ETH
    function deposit() public payable {
        // 'payable' means this function can receive ETH
        // msg.value = how much ETH was sent with this call
        totalSaved += msg.value;
    }
    
    // FUNCTION: Only owner can withdraw everything
    function withdraw() public {
        // Check: only owner can withdraw
        require(msg.sender == owner, "Not the owner!");
        
        // Send all ETH to owner
        uint256 amount = address(this).balance;
        
        // Transfer the ETH
        (bool success, ) = owner.call{value: amount}("");
        require(success, "Transfer failed!");
        
        totalSaved = 0;
    }
    
    // FUNCTION: Check balance
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
    




















