import pandas as pd
import difflib
from prompts import get_image_food_identification_prompt
from llm_provider import LLMProvider
from settings import OPENAI_MODEL, LLM_PROVIDER, OPENAI_KEY


def dish_analysis(image_path):
    prompt = get_image_food_identification_prompt().format()
    llm = LLMProvider(provider=LLM_PROVIDER, model=OPENAI_MODEL, openai_api_key=OPENAI_KEY)
    result = llm.ask_with_image(prompt, image_path, json_response=True)
    data = result["response"]
    if data is None:
        return None
    return data


def compute_health_score(dish_data):
    """
    Compute a health score (0-10) based on dish nutritional data.
    Higher score means healthier dish.
    
    Parameters:
    - dish_data: Dictionary containing dish analysis with macronutrients
    
    Returns:
    - health_score: Float between 0 and 10
    """
    macros = dish_data.get('macronutrients', {})
    
    if not macros:
        return 5.0  # Default middle score if no data
    
    # Extract key nutritional values
    calories = macros.get('calories', 0)
    protein = macros.get('protein', 0)
    fat = macros.get('fat', 0)
    sat_fat = macros.get('sat.fat', 0)
    fiber = macros.get('fiber', 0)
    carbs = macros.get('carbs', 0)
    
    # Calculate protein ratio (protein calories / total calories)
    # Protein is 4 calories per gram
    total_calories = max(calories, 1)  # Avoid division by zero
    protein_ratio = (protein * 4) / total_calories
    
    # Calculate fiber to carb ratio
    carb_ratio = fiber / max(carbs, 1)  # Avoid division by zero
    
    # Calculate saturated fat ratio to total fat
    sat_fat_ratio = sat_fat / max(fat, 1)  # Avoid division by zero
    
    # Scoring components (0-10 scale for each)
    protein_score = min(10, protein_ratio * 50)  # Higher protein ratio is good
    fiber_score = min(10, carb_ratio * 30)  # Higher fiber to carb ratio is good
    fat_quality_score = max(0, 10 - (sat_fat_ratio * 15))  # Lower sat fat ratio is good
    
    # Calorie density factor (penalty for very high calorie dishes)
    calorie_factor = max(0.5, min(1.0, 1000 / max(calories, 1)))
    
    # Calculate final score as weighted average
    health_score = (protein_score * 0.4 + 
                   fiber_score * 0.3 + 
                   fat_quality_score * 0.3) * calorie_factor
    
    # Ensure score is between 0 and 10
    health_score = max(0, min(10, health_score))
    
    # Round to 1 decimal place
    return round(health_score, 1)
