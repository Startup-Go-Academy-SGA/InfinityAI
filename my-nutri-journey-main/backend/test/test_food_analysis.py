import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from food_analysis import food_analysis
import json

def main():
    test_cases = [
        {"food": "Cows' milk", "g": 100},                     # Only g
        {"food": "Milk skim", "g": 200},                      # Only g
        {"food": "Buttermilk", "portions": 2},                # Only portions
        {"food": "teryaki", "portions": 1},                   # Only portions, fuzzy match
        {"food": "Powdered milk", "g": 50},                   # Only g
        {"food": "Blue egg", "g": 50},                        # Only g, fuzzy match
        {"food": "lasagne", "g": 50},                         # Only g, fuzzy match
        {"food": "Tuna", "g": 50},                            # Only g, fuzzy match
        {"food": "Cows' milk", "g": 100, "portions": 3},      # Both g and portions
        {"food": "Buttermilk"},                               # Neither g nor portions
    ]

    for case in test_cases:
        print(f"Input: {case}")
        result = food_analysis(**case)
        print("Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("-" * 40)

if __name__ == "__main__":
    main()