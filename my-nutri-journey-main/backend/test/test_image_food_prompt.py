import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prompts import get_image_food_identification_prompt
from llm_provider import LLMProvider
from settings import TEST_OPENAI_MODEL, TEST_LLM_PROVIDER, OPENAI_KEY

def main():
    prompt = get_image_food_identification_prompt().format()
    images_dir = os.path.join(os.path.dirname(__file__), "dishes")
    image_files = [
        f for f in os.listdir(images_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    if not image_files:
        print("No images found in test/dishes.")
        return

    llm = LLMProvider(provider=TEST_LLM_PROVIDER, model=TEST_OPENAI_MODEL, openai_api_key=OPENAI_KEY)

    for fname in image_files:
        image_path = os.path.join(images_dir, fname)
        print(f"\n=== {fname} ===")
        try:
            result = llm.ask_with_image(prompt, image_path, json_response=True)
            data = result["response"]
            if not data or "ingredients" not in data:
                print("No valid ingredients found.")
            else:
                print(f"Dish: {data.get('dish_name', 'Unknown')}")
                print("Ingredients:")
                for ing in data["ingredients"]:
                    name = ing.get("name", "Unknown")
                    portions = ing.get("portion_count", "N/A")
                    grams = ing.get("grams", "N/A")
                    print(f"  - {name}: {portions} portion(s), {grams}g per portion")
            print(f"Tokens used: {result['tokens']}")
        except Exception as e:
            print(f"Error processing {fname}: {e}")

if __name__ == "__main__":
    main()