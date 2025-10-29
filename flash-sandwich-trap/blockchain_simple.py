from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

class SimpleConnector:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))
        
        # Flash loan event signature (Aave V2/V3)
        # Borrow(address,address,address,uint256,uint256,uint256,uint16)
        self.flash_loan_topic = self.w3.keccak(text="Borrow(address,address,address,uint256,uint256,uint256,uint16)")
        
        # Swap event signature (Uniswap V2)
        # Swap(address,uint256,uint256,uint256,uint256,address)
        self.swap_topic = self.w3.keccak(text="Swap(address,uint256,uint256,uint256,uint256,address)")
    
    def get_flash_loans(self, block_number):
        """Get flash loans from block"""
        loans = []
        
        try:
            logs = self.w3.eth.get_logs({
                'fromBlock': block_number,
                'toBlock': block_number,
                'topics': [self.flash_loan_topic.hex()]
            })
            
            for log in logs:
                # Decode amount (simplified)
                amount = int(log['data'].hex()[2:66], 16) / 1e18
                borrower = '0x' + log['topics'][1].hex()[-40:]
                
                loans.append({
                    'borrower': borrower,
                    'amount': amount,
                    'tx_hash': log['transactionHash'].hex()
                })
        except:
            pass
        
        return loans
    
    def get_swaps(self, block_number):
        """Get large swaps from block"""
        swaps = []
        
        try:
            logs = self.w3.eth.get_logs({
                'fromBlock': block_number,
                'toBlock': block_number,
                'topics': [self.swap_topic.hex()]
            })
            
            for log in logs:
                # Decode amounts (simplified)
                data = log['data'].hex()[2:]
                amount_in = int(data[0:64], 16) / 1e18
                amount_out = int(data[64:128], 16) / 1e18
                
                # Calculate price impact (simplified)
                if amount_in > 0:
                    price_impact = (amount_out / amount_in - 1) * 100
                else:
                    price_impact = 0
                
                swaps.append({
                    'trader': '0x' + log['topics'][1].hex()[-40:],
                    'amount_in': amount_in,
                    'amount_out': amount_out,
                    'price_impact': abs(price_impact),
                    'tx_hash': log['transactionHash'].hex()
                })
        except:
            pass
        
        return swaps

# Quick test
if __name__ == "__main__":
    connector = SimpleConnector()
    print("✅ Connected to blockchain:", connector.w3.is_connected())
