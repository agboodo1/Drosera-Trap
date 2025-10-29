// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FlashSandwichTrap {
    uint256 public minPriceImpact = 5; // 5%
    uint256 public minLoanSize = 100000 * 1e18; // 100k
    
    struct BlockData {
        uint256 maxFlashLoan;
        uint256 maxPriceImpact;
        uint256 blockNumber;
    }
    
    function collect() external view returns (BlockData memory) {
        // Would collect from actual events
        return BlockData(0, 0, block.number);
    }
    
    function shouldRespond(BlockData[] memory history) 
        external 
        view 
        returns (bool) 
    {
        if (history.length < 1) return false;
        
        // Check last 2 blocks
        uint256 start = history.length > 2 ? history.length - 2 : 0;
        
        for (uint256 i = start; i < history.length; i++) {
            // If large loan AND high price impact = attack
            if (history[i].maxFlashLoan >= minLoanSize && 
                history[i].maxPriceImpact >= minPriceImpact) {
                return true;
            }
        }
        
        return false;
    }
}
