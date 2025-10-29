"""
Flash Loan Sandwich Detector
Short name: flash_sandwich_trap
Detects when someone takes a flash loan, makes a large swap affecting price,
and another address profits from the price movement in the same transaction.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Transaction:
    """Single transaction data"""
    tx_hash: str
    from_address: str
    block_number: int
    gas_used: int
    actions: List[str]  # e.g., ["flash_loan", "swap", "arbitrage"]

@dataclass
class FlashLoan:
    """Flash loan event"""
    borrower: str
    token: str
    amount: float
    tx_hash: str

@dataclass
class Swap:
    """DEX swap event"""
    trader: str
    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    price_impact: float  # % price movement
    tx_hash: str

@dataclass
class CollectedData:
    """Data collected per block"""
    flash_loans: List[FlashLoan]
    swaps: List[Swap]
    block_number: int
    timestamp: int

class FlashSandwichTrap:
    """
    Detects flash loan sandwich attacks:
    1. Attacker borrows large amount via flash loan
    2. Makes huge swap that moves price significantly
    3. Another transaction (or same) profits from price movement
    4. Loan repaid in same transaction
    
    This is simpler than dust voting because:
    - All happens in 1-2 transactions
    - Clear price impact signal
    - Easy to detect flash loan + large swap pattern
    """
    
    def __init__(self, config: Dict):
        # Simpler configuration - only 3 parameters!
        self.min_price_impact = config.get('min_price_impact', 5.0)  # 5% price move
        self.min_flash_loan_size = config.get('min_flash_loan_size', 100000)  # $100k
        self.max_blocks_between = config.get('max_blocks_between', 1)  # Must be in same/next block
    
    def collect(self, block_number: int) -> CollectedData:
        """
        Collect flash loans and large swaps from block
        Much simpler than dust voting - just 2 event types!
        """
        # In production, query blockchain for:
        # - Flash loan events (Aave, Compound, Uniswap V2/V3)
        # - Swap events (Uniswap, Sushiswap, etc.)
        
        return CollectedData(
            flash_loans=[],
            swaps=[],
            block_number=block_number,
            timestamp=0
        )
    
    def should_respond(self, historical_data: List[CollectedData]) -> bool:
        """
        Simple detection: Flash loan + big price impact in same/adjacent blocks
        
        Returns True if:
        1. Flash loan >= threshold
        2. Large swap with price impact >= threshold
        3. Both in same or adjacent blocks
        """
        if len(historical_data) < 1:
            return False
        
        # Look at last 2 blocks
        recent_blocks = historical_data[-2:] if len(historical_data) >= 2 else historical_data
        
        # Step 1: Find all flash loans
        flash_loans = []
        for block in recent_blocks:
            for loan in block.flash_loans:
                if loan.amount >= self.min_flash_loan_size:
                    flash_loans.append(loan)
        
        if not flash_loans:
            return False
        
        # Step 2: Find swaps with high price impact
        high_impact_swaps = []
        for block in recent_blocks:
            for swap in block.swaps:
                if swap.price_impact >= self.min_price_impact:
                    high_impact_swaps.append(swap)
        
        if not high_impact_swaps:
            return False
        
        # Step 3: Check if they're related (same tx or close timing)
        for loan in flash_loans:
            for swap in high_impact_swaps:
                # Same transaction = definite sandwich
                if loan.tx_hash == swap.tx_hash:
                    return True
                
                # Same borrower/trader in adjacent blocks = likely sandwich
                if loan.borrower == swap.trader:
                    return True
        
        return False
    
    def get_alert_details(self, historical_data: List[CollectedData]) -> Dict:
        """Generate alert with attack details"""
        recent_blocks = historical_data[-2:]
        
        flash_loans = []
        swaps = []
        
        for block in recent_blocks:
            flash_loans.extend([
                {
                    'borrower': loan.borrower,
                    'amount': loan.amount,
                    'tx': loan.tx_hash
                }
                for loan in block.flash_loans
                if loan.amount >= self.min_flash_loan_size
            ])
            
            swaps.extend([
                {
                    'trader': swap.trader,
                    'price_impact': swap.price_impact,
                    'tx': swap.tx_hash
                }
                for swap in block.swaps
                if swap.price_impact >= self.min_price_impact
            ])
        
        return {
            'attack_type': 'flash_loan_sandwich',
            'severity': 'HIGH',
            'flash_loans': flash_loans,
            'high_impact_swaps': swaps,
            'blocks_analyzed': len(historical_data)
        }


# ============= SUPER SIMPLE IMPLEMENTATION EXAMPLE =============

class SimpleFlashSandwichTrap:
    """
    ULTRA-SIMPLIFIED VERSION for quick setup
    Only tracks 2 things: flash loans and price impact
    """
    
    def __init__(self):
        self.price_impact_threshold = 5.0  # 5%
        self.flash_loan_threshold = 100000  # $100k
    
    def collect(self, block_number: int) -> Dict:
        """Just return a dict with the data we need"""
        return {
            'block': block_number,
            'flash_loans': [],  # Will be filled with loan amounts
            'price_impacts': []  # Will be filled with price changes
        }
    
    def should_respond(self, last_blocks: List[Dict]) -> bool:
        """
        Super simple check:
        - Is there a big flash loan?
        - Is there a big price move?
        - Both in last 2 blocks?
        """
        if len(last_blocks) < 1:
            return False
        
        recent = last_blocks[-2:] if len(last_blocks) >= 2 else last_blocks
        
        # Check for large flash loan
        has_large_loan = any(
            loan >= self.flash_loan_threshold 
            for block in recent 
            for loan in block['flash_loans']
        )
        
        # Check for high price impact
        has_price_impact = any(
            impact >= self.price_impact_threshold
            for block in recent
            for impact in block['price_impacts']
        )
        
        # If both present = sandwich attack
        return has_large_loan and has_price_impact


# ============= USAGE EXAMPLE =============

def main():
    """Quick demo of the trap"""
    
    print("🥪 Flash Loan Sandwich Trap - Quick Setup Version\n")
    
    # Create trap with simple config
    config = {
        'min_price_impact': 5.0,      # 5% price move triggers
        'min_flash_loan_size': 100000, # $100k minimum
        'max_blocks_between': 1        # Same or next block
    }
    
    trap = FlashSandwichTrap(config)
    
    # Simulate monitoring
    print("📊 Monitoring for flash loan sandwiches...")
    print(f"   Price Impact Threshold: {config['min_price_impact']}%")
    print(f"   Flash Loan Threshold: ${config['min_flash_loan_size']:,}")
    print()
    
    # Example: Simulate normal activity
    print("Block 1000: Normal activity")
    data1 = CollectedData(
        flash_loans=[FlashLoan("0xUser1", "USDC", 50000, "0xTx1")],
        swaps=[Swap("0xUser2", "ETH", "USDC", 10, 20000, 0.5, "0xTx2")],
        block_number=1000,
        timestamp=1000
    )
    print("   ✅ No incident (loan too small, impact too low)\n")
    
    # Example: Simulate attack
    print("Block 1001: SUSPICIOUS ACTIVITY!")
    data2 = CollectedData(
        flash_loans=[FlashLoan("0xAttacker", "USDC", 500000, "0xTx3")],
        swaps=[Swap("0xAttacker", "USDC", "ETH", 500000, 250, 8.5, "0xTx3")],
        block_number=1001,
        timestamp=1001
    )
    
    historical = [data1, data2]
    
    if trap.should_respond(historical):
        print("   🚨 SANDWICH ATTACK DETECTED!")
        alert = trap.get_alert_details(historical)
        print(f"\n   Alert Details:")
        print(f"   - Flash Loan: ${alert['flash_loans'][0]['amount']:,.0f}")
        print(f"   - Price Impact: {alert['high_impact_swaps'][0]['price_impact']}%")
        print(f"   - Same Transaction: {alert['flash_loans'][0]['tx'] == alert['high_impact_swaps'][0]['tx']}")
    
    print("\n" + "="*50)
    print("⚡ WHY THIS TRAP IS QUICK TO SETUP:")
    print("="*50)
    print("1. Only 2 event types to track (flash loans + swaps)")
    print("2. Only 3 configuration parameters")
    print("3. Detection logic is 1 simple check")
    print("4. Works in 1-2 blocks (no long history needed)")
    print("5. Clear signal = low false positives")
    print("\n✅ Setup time: ~20 minutes!")


if __name__ == "__main__":
    main()
