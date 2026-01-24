# Test Suite for Bill of Lading NFT Contract Functions
# Run this after minting an NFT to test all contract interactions

import os
from dotenv import load_dotenv
from web3 import Web3
import json

load_dotenv()

# Configuration
SEPOLIA_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# Contract ABI
CONTRACT_ABI = [
    {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getBillData","outputs":[{"components":[{"internalType":"string","name":"billNumber","type":"string"},{"internalType":"string","name":"ipfsHash","type":"string"},{"internalType":"string","name":"dataHash","type":"string"},{"internalType":"string","name":"tokenURI","type":"string"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"bool","name":"isFinanced","type":"bool"},{"internalType":"address","name":"financier","type":"address"},{"internalType":"uint256","name":"financedAmount","type":"uint256"},{"internalType":"bool","name":"isReleased","type":"bool"}],"internalType":"struct BillOfLadingNFT.BillData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"isTransferable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"shipper","type":"address"},{"internalType":"string","name":"billNumber","type":"string"},{"internalType":"string","name":"ipfsHash","type":"string"},{"internalType":"string","name":"dataHash","type":"string"},{"internalType":"string","name":"_tokenURI","type":"string"}],"name":"mintBill","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"financier","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"pledgeForFinancing","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"releaseOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]

class ContractTester:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
        if not self.w3.is_connected():
            raise Exception("Cannot connect to Sepolia RPC")
        
        self.contract = self.w3.eth.contract(
            address=CONTRACT_ADDRESS,
            abi=CONTRACT_ABI
        )
        
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        print(f"✅ Connected to Sepolia")
        print(f"📍 Contract: {CONTRACT_ADDRESS}")
        print(f"👤 Account: {self.account.address}\n")
    
    def test_get_bill_data(self, token_id):
        """Test 1: Query Bill Data"""
        print(f"\n{'='*60}")
        print(f"🧪 Test 1: Get Bill Data (Token ID: {token_id})")
        print(f"{'='*60}")
        
        try:
            bill_data = self.contract.functions.getBillData(token_id).call()
            
            print(f"✅ Success!")
            print(f"📋 Bill Number: {bill_data[0]}")
            print(f"☁️  IPFS Hash: {bill_data[1]}")
            print(f"🔢 Data Hash: {bill_data[2]}")
            print(f"🔗 Token URI: {bill_data[3]}")
            print(f"⏰ Timestamp: {bill_data[4]}")
            print(f"💰 Is Financed: {bill_data[5]}")
            print(f"🏦 Financier: {bill_data[6]}")
            print(f"💵 Financed Amount: {self.w3.from_wei(bill_data[7], 'ether')} ETH")
            print(f"🔓 Is Released: {bill_data[8]}")
            
            return bill_data
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_is_transferable(self, token_id):
        """Test 2: Check Transferability"""
        print(f"\n{'='*60}")
        print(f"🧪 Test 2: Check Transferability (Token ID: {token_id})")
        print(f"{'='*60}")
        
        try:
            transferable = self.contract.functions.isTransferable(token_id).call()
            print(f"✅ Result: {'Can Transfer ✓' if transferable else 'Cannot Transfer ✗'}")
            return transferable
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_token_uri(self, token_id):
        """Test 3: Get Token URI"""
        print(f"\n{'='*60}")
        print(f"🧪 Test 3: Get Token URI (Token ID: {token_id})")
        print(f"{'='*60}")
        
        try:
            uri = self.contract.functions.tokenURI(token_id).call()
            print(f"✅ Token URI: {uri}")
            return uri
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_owner_of(self, token_id):
        """Test 4: Get Owner"""
        print(f"\n{'='*60}")
        print(f"🧪 Test 4: Get Owner (Token ID: {token_id})")
        print(f"{'='*60}")
        
        try:
            owner = self.contract.functions.ownerOf(token_id).call()
            print(f"✅ Owner: {owner}")
            print(f"🔍 Is current account: {owner.lower() == self.account.address.lower()}")
            return owner
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_pledge_for_financing(self, token_id, financier_address, amount_eth):
        """Test 5: Pledge for Financing (Transaction)"""
        print(f"\n{'='*60}")
        print(f"🧪 Test 5: Pledge for Financing")
        print(f"{'='*60}")
        print(f"Token ID: {token_id}")
        print(f"Financier: {financier_address}")
        print(f"Amount: {amount_eth} ETH")
        
        try:
            # Convert amount to Wei
            amount_wei = self.w3.to_wei(amount_eth, 'ether')
            
            # Build transaction
            txn = self.contract.functions.pledgeForFinancing(
                token_id,
                financier_address,
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            print(f"📤 Transaction sent: {tx_hash.hex()}")
            print(f"⏳ Waiting for confirmation...")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Transaction confirmed!")
                print(f"⛽ Gas used: {receipt.gasUsed}")
                print(f"🔗 Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                return receipt
            else:
                print(f"❌ Transaction failed!")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_release_ownership(self, token_id):
        """Test 6: Release Ownership (Transaction)"""
        print(f"\n{'='*60}")
        print(f"🧪 Test 6: Release Ownership")
        print(f"{'='*60}")
        print(f"Token ID: {token_id}")
        
        try:
            # Build transaction
            txn = self.contract.functions.releaseOwnership(token_id).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            print(f"📤 Transaction sent: {tx_hash.hex()}")
            print(f"⏳ Waiting for confirmation...")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Transaction confirmed!")
                print(f"⛽ Gas used: {receipt.gasUsed}")
                print(f"🔗 Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                return receipt
            else:
                print(f"❌ Transaction failed!")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def run_full_test_suite(self, token_id, financier_address=None):
        """Run all tests"""
        print("\n" + "="*60)
        print("🚀 Starting Full Contract Test Suite")
        print("="*60)
        
        # Read-only tests
        self.test_owner_of(token_id)
        self.test_get_bill_data(token_id)
        self.test_token_uri(token_id)
        self.test_is_transferable(token_id)
        
        # Transaction tests (optional)
        if financier_address:
            print("\n⚠️  Transaction tests will modify blockchain state!")
            response = input("Continue with transaction tests? (yes/no): ")
            
            if response.lower() == 'yes':
                # Test pledge
                self.test_pledge_for_financing(token_id, financier_address, 1.0)
                
                # Recheck transferability
                self.test_is_transferable(token_id)
                
                # Test release (must be called by financier, will fail if wrong account)
                # self.test_release_ownership(token_id)
        
        print("\n" + "="*60)
        print("✅ Test Suite Complete!")
        print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("🧪 Bill of Lading NFT Contract Test Suite")
    print("="*60)
    
    # Get token ID from user
    token_id = input("\nEnter Token ID to test (or press Enter for Token 1): ").strip()
    token_id = int(token_id) if token_id else 1
    
    # Optional: Get financier address for transaction tests
    financier = input("\nEnter financier address for transaction tests (or press Enter to skip): ").strip()
    financier = financier if financier else None
    
    # Run tests
    tester = ContractTester()
    tester.run_full_test_suite(token_id, financier)
