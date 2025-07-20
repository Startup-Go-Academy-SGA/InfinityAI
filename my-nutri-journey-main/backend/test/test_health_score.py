import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from food_analysis import compute_health_score
import json

def test_health_score():
    """Test the health score computation with synthetic meal data."""
    
    # Test cases with synthetic meal data representing various dietary patterns
    test_cases = [
        {
            "name": "Very Healthy Meal (High protein, high fiber, low sat fat)",
            "data": {
                "dish_name": "Grilled Salmon with Vegetables",
                "macronutrients": {
                    "calories": 450,
                    "protein": 35,
                    "fat": 20,
                    "sat.fat": 3,
                    "fiber": 12,
                    "carbs": 30
                }
            },
            "expected_range": (8.0, 10.0)
        },
        {
            "name": "Good Balanced Meal (Good macros, moderate calories)",
            "data": {
                "dish_name": "Chicken and Quinoa Bowl",
                "macronutrients": {
                    "calories": 550,
                    "protein": 28,
                    "fat": 15,
                    "sat.fat": 3.5,
                    "fiber": 8,
                    "carbs": 65
                }
            },
            "expected_range": (7.0, 8.5)
        },
        {
            "name": "Average Meal (Decent protein, lower fiber)",
            "data": {
                "dish_name": "Turkey Sandwich",
                "macronutrients": {
                    "calories": 450,
                    "protein": 20,
                    "fat": 15,
                    "sat.fat": 4,
                    "fiber": 4,
                    "carbs": 55
                }
            },
            "expected_range": (5.0, 7.0)
        },
        {
            "name": "Below Average Meal (Low protein, high carbs, moderate fat)",
            "data": {
                "dish_name": "Pasta with Cream Sauce",
                "macronutrients": {
                    "calories": 700,
                    "protein": 15,
                    "fat": 25,
                    "sat.fat": 12,
                    "fiber": 3,
                    "carbs": 90
                }
            },
            "expected_range": (3.5, 5.5)
        },
        {
            "name": "Unhealthy Meal (High calories, high sat fat, low fiber)",
            "data": {
                "dish_name": "Double Cheeseburger with Fries",
                "macronutrients": {
                    "calories": 1200,
                    "protein": 35,
                    "fat": 65,
                    "sat.fat": 25,
                    "fiber": 4,
                    "carbs": 120
                }
            },
            "expected_range": (1.0, 4.0)
        },
        {
            "name": "Very Unhealthy Meal (Extreme values)",
            "data": {
                "dish_name": "Loaded Milkshake with Fried Dessert",
                "macronutrients": {
                    "calories": 1500,
                    "protein": 12,
                    "fat": 80,
                    "sat.fat": 40,
                    "fiber": 1,
                    "carbs": 180
                }
            },
            "expected_range": (0.0, 2.5)
        },
        {
            "name": "High Protein Low Carb",
            "data": {
                "dish_name": "Steak and Eggs",
                "macronutrients": {
                    "calories": 600,
                    "protein": 50,
                    "fat": 40,
                    "sat.fat": 15,
                    "fiber": 0,
                    "carbs": 2
                }
            },
            "expected_range": (5.0, 8.0)
        },
        {
            "name": "Vegan High Fiber",
            "data": {
                "dish_name": "Lentil and Vegetable Stew",
                "macronutrients": {
                    "calories": 400,
                    "protein": 18,
                    "fat": 5,
                    "sat.fat": 0.5,
                    "fiber": 15,
                    "carbs": 70
                }
            },
            "expected_range": (7.0, 9.5)
        },
        {
            "name": "Empty Data",
            "data": {
                "dish_name": "Unknown",
                "macronutrients": {}
            },
            "expected_range": (5.0, 5.0)  # Default score when no data
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        name = test_case["name"]
        data = test_case["data"]
        expected_min, expected_max = test_case["expected_range"]
        
        health_score = compute_health_score(data)
        
        # Check if the score falls within the expected range
        is_valid = expected_min <= health_score <= expected_max
        
        result = {
            "name": name,
            "dish": data["dish_name"],
            "health_score": health_score,
            "expected_range": f"{expected_min}-{expected_max}",
            "passed": is_valid
        }
        
        results.append(result)
        
        # Print individual test results
        print(f"Test: {name}")
        print(f"  Dish: {data['dish_name']}")
        print(f"  Health Score: {health_score}")
        print(f"  Expected Range: {expected_min}-{expected_max}")
        print(f"  Passed: {'✅' if is_valid else '❌'}")
        print()
    
    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print(f"Summary: {passed}/{total} tests passed")
    
    # Return overall success status
    return all(r["passed"] for r in results)

def test_ingredient_impact():
    """Test how individual ingredients impact the overall health score."""
    
    # Base dish with moderate health
    base_dish = {
        "dish_name": "Base Dish",
        "macronutrients": {
            "calories": 500,
            "protein": 25,
            "fat": 20,
            "sat.fat": 5,
            "fiber": 6,
            "carbs": 60
        }
    }
    
    # Modifications to test
    modifications = [
        {
            "name": "Add Protein",
            "change": {"protein": 10},  # Add 10g protein
            "expected_direction": "increase"
        },
        {
            "name": "Add Saturated Fat",
            "change": {"sat.fat": 10},  # Add 10g sat fat
            "expected_direction": "decrease"
        },
        {
            "name": "Add Fiber",
            "change": {"fiber": 8},  # Add 8g fiber
            "expected_direction": "increase"
        },
        {
            "name": "Add Calories",
            "change": {"calories": 500},  # Add 500 calories
            "expected_direction": "decrease"
        },
        {
            "name": "Balance Improvement",
            "change": {"protein": 5, "fiber": 4, "sat.fat": -2},  # Better balance
            "expected_direction": "increase"
        }
    ]
    
    # Get baseline score
    base_score = compute_health_score(base_dish)
    print(f"Base dish '{base_dish['dish_name']}' health score: {base_score}\n")
    
    results = []
    
    for mod in modifications:
        # Create a copy of the base dish
        modified_dish = {
            "dish_name": f"{base_dish['dish_name']} with {mod['name']}",
            "macronutrients": base_dish["macronutrients"].copy()
        }
        
        # Apply modifications
        for nutrient, change in mod["change"].items():
            modified_dish["macronutrients"][nutrient] += change
        
        # Compute new score
        new_score = compute_health_score(modified_dish)
        
        # Determine if the score changed in the expected direction
        if mod["expected_direction"] == "increase":
            passed = new_score > base_score
        else:  # "decrease"
            passed = new_score < base_score
            
        result = {
            "modification": mod["name"],
            "base_score": base_score,
            "new_score": new_score,
            "change": new_score - base_score,
            "expected_direction": mod["expected_direction"],
            "passed": passed
        }
        
        results.append(result)
        
        # Print individual test results
        print(f"Test: {mod['name']}")
        print(f"  Base Score: {base_score}")
        print(f"  New Score: {new_score}")
        print(f"  Change: {new_score - base_score:+.1f}")
        print(f"  Expected Direction: {mod['expected_direction']}")
        print(f"  Passed: {'✅' if passed else '❌'}")
        print()
    
    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print(f"Summary: {passed}/{total} tests passed")
    
    # Return overall success status
    return all(r["passed"] for r in results)

def main():
    """Run all tests and report results."""
    print("=" * 50)
    print("TESTING HEALTH SCORE COMPUTATION")
    print("=" * 50)
    
    print("\nTEST 1: Basic Health Score Calculation")
    test1_result = test_health_score()
    
    print("\nTEST 2: Ingredient Impact on Health Score")
    test2_result = test_ingredient_impact()
    
    print("\nOVERALL RESULTS:")
    if test1_result and test2_result:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return test1_result and test2_result

if __name__ == "__main__":
    main()