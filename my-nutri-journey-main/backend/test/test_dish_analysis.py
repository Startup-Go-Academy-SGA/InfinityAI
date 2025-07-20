import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from food_analysis import dish_analysis

def main():
    images_dir = os.path.join(os.path.dirname(__file__), "dishes")
    image_files = [
        f for f in os.listdir(images_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    if not image_files:
        print("No images found in test/dishes.")
        return

    for fname in image_files:
        image_path = os.path.join(images_dir, fname)
        print(f"\n=== {fname} ===")
        try:
            result = dish_analysis(image_path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error processing {fname}: {e}")

if __name__ == "__main__":
    main()