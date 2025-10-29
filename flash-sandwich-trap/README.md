# Flash Loan Sandwich Attack Trap

Detects flash loan sandwich attacks in real-time.

## How It Works
1. Monitor flash loan events
2. Track large price-impact swaps
3. Alert if both occur in same/adjacent blocks

## Quick Start
\`\`\`bash
pip install web3
python flash_sandwich_trap.py
\`\`\`

## Why This Matters
Flash loan attacks have stolen $1B+ from DeFi protocols.
This trap provides sub-minute detection.

## Configuration
Only 3 parameters:
- Price impact threshold: 5%
- Min loan size: $100k
- Block window: 1-2 blocks
