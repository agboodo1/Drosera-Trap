from flash_sandwich_trap import FlashSandwichTrap, CollectedData, FlashLoan, Swap
from blockchain_simple import SimpleConnector
import json

# Load config
with open('config.json') as f:
    config = json.load(f)['parameters']

# Initialize
trap = FlashSandwichTrap(config)
connector = SimpleConnector()

print("🥪 Flash Sandwich Trap Running...")
print(f"   Min Price Impact: {config['min_price_impact']}%")
print(f"   Min Flash Loan: ${config['min_flash_loan_size']:,}")
print()

# Monitor recent blocks
current_block = connector.w3.eth.block_number
start_block = current_block - 10

historical_data = []

for block_num in range(start_block, current_block):
    # Collect data
    loans_data = connector.get_flash_loans(block_num)
    swaps_data = connector.get_swaps(block_num)
    
    # Convert to trap format
    loans = [
        FlashLoan(l['borrower'], 'USDC', l['amount'], l['tx_hash'])
        for l in loans_data
    ]
    
    swaps = [
        Swap(s['trader'], 'ETH', 'USDC', s['amount_in'], 
             s['amount_out'], s['price_impact'], s['tx_hash'])
        for s in swaps_data
    ]
    
    collected = CollectedData(loans, swaps, block_num, 0)
    historical_data.append(collected)
    
    # Check for attack
    if trap.should_respond(historical_data):
        alert = trap.get_alert_details(historical_data)
        print(f"🚨 SANDWICH ATTACK at block {block_num}!")
        print(f"   {alert}")
        break
    else:
        print(f"✅ Block {block_num}: No incidents")

print("\n✅ Monitoring complete")
