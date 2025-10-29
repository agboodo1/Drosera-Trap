from flash_sandwich_trap import SimpleFlashSandwichTrap

def test_attack():
    trap = SimpleFlashSandwichTrap()
    
    # Normal block
    block1 = {
        'block': 1000,
        'flash_loans': [50000],  # Small loan
        'price_impacts': [1.0]    # Small impact
    }
    
    # Attack block
    block2 = {
        'block': 1001,
        'flash_loans': [500000],  # LARGE loan
        'price_impacts': [8.5]    # HIGH impact
    }
    
    # Should not trigger on block 1
    assert not trap.should_respond([block1])
    print("✅ Test 1: Normal activity - PASSED")
    
    # Should trigger on block 2
    assert trap.should_respond([block1, block2])
    print("✅ Test 2: Attack detected - PASSED")

if __name__ == "__main__":
    test_attack()
    print("\n🎉 All tests passed!")
