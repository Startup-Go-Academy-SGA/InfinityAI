from langchain_core.prompts import PromptTemplate


def get_mealplan_prompt(user_profile, num_days=7):
    """
    Returns a prompt for generating a meal plan as a JSON object for the next N days.
    The plan must align with the user's profile, goals, preferences, and daily macro targets.

    Example output:
    {
      "day1": {
        "breakfast": [
          {
            "dish_name": "Greek Yogurt with Berries",
            "macronutrients": {
              "calories": 220,
              "protein": 18,
              "carbs": 25,
              "fats": 5,
              "fibers": 3,
              "saturated_fats": 2
            },
            "ingredients": [
              {"name": "greek yogurt", "portion_count": 1, "grams": 150},
              {"name": "blueberries", "portion_count": 1, "grams": 50}
            ],
            "health_score": 8,
            "health_explanation": "High in protein and contains antioxidants from berries",
            "health_benefits": [
              "Good source of protein for muscle maintenance",
              "Contains probiotics for gut health",
              "Berries provide antioxidants"
            ]
          }
        ],
        "lunch": [
          {
            "dish_name": "Grilled Chicken Salad",
            "macronutrients": {
              "calories": 300,
              "protein": 30,
              "carbs": 15,
              "fats": 10,
              "fibers": 5,
              "saturated_fats": 2
            },
            "ingredients": [
              {"name": "chicken breast", "portion_count": 1, "grams": 120},
              {"name": "lettuce", "portion_count": 1, "grams": 50},
              {"name": "tomatoes", "portion_count": 1, "grams": 50},
              {"name": "cucumber", "portion_count": 1, "grams": 30},
              {"name": "olive oil", "portion_count": 1, "grams": 10}
            ],
            "health_score": 9,
            "health_explanation": "High in lean protein with plenty of vegetables",
            "health_benefits": [
              "Lean protein for muscle repair",
              "Low in calories but nutrient-dense",
              "Contains various vitamins and minerals from vegetables"
            ]
          }
        ]
      },
      "day2": {
        ...
      }
    }
    """
    return PromptTemplate.from_template(
"""
You are a nutrition expert. Generate a meal plan for the next {num_days} days for the user below.

User Profile:
{user_profile}

Instructions:
- Carefully analyze the user's profile and goals before generating the plan. Reflect on their needs and optimize the meal plan to best respect their profile and objectives.
- The plan must align with the user's goals, dietary preferences, allergies, dislikes, geographic location, and physical stats (weight, height, etc).
- **Pay special attention to the user's daily target calories and macronutrients (protein, carbs, fats). The total for each day should be as close as possible to these targets. Do not underestimate or overestimate these values.**
- Each day's meals should help the user reach their daily calorie and macronutrient targets as closely as possible.
- Not all meals must be present every day. For example, if the user is losing weight, snacks or even lunch/dinner may be omitted as appropriate.
- For each meal (breakfast, lunch, dinner, snack), provide zero or more dishes as needed.
- For each dish, include:
    - "dish_name": the name of the food
    - "macronutrients": an object with keys "calories", "protein", "carbs", "fats", "fibers", "saturated_fats" (all numbers, per dish, unit is grams except calories)
    - "ingredients": a list of objects, each with "name", "portion_count", and "grams"
    - "health_score": a number from 1-10 (where 10 is extremely healthy)
    - "health_explanation": brief explanation for the health score
    - "health_benefits": a list of 3-5 key health benefits of the dish
- If the user is an athlete or has an active lifestyle, and their dietary goal permits, you may include more dishes per meal to meet their higher energy and nutrient needs.
- Output a JSON object with the following structure (days should be named "day1", "day2", ..., "dayN"):

{{
  "day1": {{
    "breakfast": [
      {{
        "dish_name": "food breakfast 1",
        "macronutrients": {{
          "calories": C,
          "protein": P,
          "carbs": CB,
          "fats": F,
          "fibers": FB,
          "saturated_fats": SF
        }},
        "ingredients": [
          {{"name": "...", "portion_count": ..., "grams": ...}},
          ...
        ],
        "health_score": S,
        "health_explanation": "Brief explanation of the health score",
        "health_benefits": [
          "Benefit 1",
          "Benefit 2",
          "Benefit 3"
        ]
      }},
      ...
    ],
    "lunch": [
      ...
    ],
    "dinner": [
      ...
    ],
    "snack": [
      ...
    ]
  }},
  ...
  "dayN": {{
    ...
  }}
}}

- Only include meals that make sense for the user's profile and goals (e.g., skip snacks if not needed).
- Do not include any explanation or formatting, only output the JSON object.
"""
    )


def get_chatbot_prompt():
    """
    Returns a prompt for a nutrition expert chatbot.

    Example output:
    "Hi Alice! Based on your profile and recent meals, adding more leafy greens could help you reach your fiber goal. Would you like some recipe ideas?"
    """
    return PromptTemplate.from_template(
        """
You are a helpful and friendly nutrition expert chatbot.

User Profile:
{full_profile}

Chat History:
{chat_history}

User's Question:
{question}

Provide a concise, supportive, and informative response, addressing the user's query directly. If the question is unrelated to the plan or nutrition, politely redirect them to stay on topic.
"""
    )


def get_macro_breakdown_prompt():
    """
    Returns a prompt for estimating the macronutrient breakdown of a food.

    Example output:
    {
      "Protein": 8,
      "Carbohydrates": 35,
      "Fat": 2,
      "Fiber": 4
    }
    """
    return PromptTemplate.from_template(
        """
You are a nutrition expert. Given the following food item, provide a detailed breakdown of its macronutrient content.

Food Name: {food_name}

Output the estimated amounts for:
- Protein (grams)
- Carbohydrates (grams)
- Fat (grams)
- Fiber (grams, if relevant)

Return your answer as a JSON object, where each key is the macronutrient name (e.g., "Protein", "Carbohydrates", "Fat", "Fiber") and each value is the number of grams (as a number, not a string). Do not include any explanation or formatting, only output the JSON.
"""
    )


def get_recipe_prompt():
    """
    Returns a prompt for generating a simple recipe for a single person.

    Example output:
    Grilled Salmon

    **Ingredients:**
    - salmon fillet (150g)
    - olive oil (1 tbsp)
    - lemon (1/2)
    - salt (to taste)
    - pepper (to taste)

    **Preparation:**
    1. Preheat grill to medium-high.
    2. Brush salmon with olive oil, season with salt and pepper.
    3. Grill salmon for 4-5 minutes per side.
    4. Squeeze lemon over before serving.
    """
    return PromptTemplate.from_template(
        """
You are a culinary expert. Given the following food name, write a simple recipe for a single person.

Food Name: {food_name}

Your response must include:
- Meal name
- A bullet-point list of ingredients (with quantities for one person)
- Step-by-step preparation instructions, each step on a new line

Format:
{food_name}

**Ingredients:**
- ingredient 1
- ingredient 2
- ...

**Preparation:**
1. Step one
2. Step two
3. ...

Keep instructions clear and concise. All portions should be for a single person.
"""
    )


def get_image_food_identification_prompt():
    """
    Returns a prompt for identifying a food dish and its main ingredients from an image,
    along with nutritional information, health score, and health benefits.

    Example output:
    {
      "dish_name": "Chicken Caesar Salad",
      "ingredients": [
        {"name": "chicken", "portion_count": 1, "grams": 100},
        {"name": "romaine lettuce", "portion_count": 1, "grams": 60},
        {"name": "parmesan cheese", "portion_count": 1, "grams": 15},
        {"name": "croutons", "portion_count": 1, "grams": 20}
      ],
      "macronutrients": {
        "calories": 320,
        "protein": 25,
        "carbs": 15,
        "fats": 18,
        "fibers": 3,
        "saturated_fats": 6
      },
      "health_score": 8,
      "health_explanation": "This dish is high in protein and includes leafy greens, making it a balanced meal. The croutons and dressing add some refined carbs and fats.",
      "health_benefits": [
        "High in protein for muscle maintenance",
        "Contains vitamin K from leafy greens",
        "Good source of calcium from cheese"
      ]
    }
    """
    return PromptTemplate.from_template(
        """
I will give you an image of a food dish.
Your task is to:

1. Identify the name of the dish (in English, even if it's an international recipe).

2. Provide a list of the main ingredients, ignoring small or negligible items like seasonings, garnishes, or spices.
   For each ingredient, estimate:
   - the number of portions (N) visible in the image
   - how many grams (as an integer) per portion

3. Calculate the macronutrients for the complete dish:
   - Total calories
   - Protein (in grams)
   - Carbohydrates (in grams)
   - Fats (in grams)
   - Fiber (in grams)
   - Saturated fats (in grams)

4. Provide a health score from 1-10 (where 10 is extremely healthy) and a brief explanation for the score.

5. List 3-5 key health benefits of the dish.

Output the result in the following JSON format:

{{
  "dish_name": "Name of the dish",
  "ingredients": [
    {{"name": "Ingredient 1", "portion_count": N1, "grams": G1}},
    {{"name": "Ingredient 2", "portion_count": N2, "grams": G2}},
    ...
  ],
  "macronutrients": {{
    "calories": C,
    "protein": P,
    "carbs": CB,
    "fats": F,
    "fibers": FB,
    "saturated_fats": SF
  }},
  "health_score": S,
  "health_explanation": "Brief explanation of the health score",
  "health_benefits": [
    "Benefit 1",
    "Benefit 2",
    "Benefit 3"
  ]
}}

Examples:
For a dish like Pasta Carbonara, your output might be:

{{
  "dish_name": "Pasta Carbonara",
  "ingredients": [
    {{"name": "egg", "portion_count": 1, "grams": 50}},
    {{"name": "bacon", "portion_count": 1, "grams": 30}},
    {{"name": "spaghetti", "portion_count": 1, "grams": 100}}
  ],
  "macronutrients": {{
    "calories": 450,
    "protein": 20,
    "carbs": 50,
    "fats": 18,
    "fibers": 2,
    "saturated_fats": 6
  }},
  "health_score": 5,
  "health_explanation": "Contains good protein from eggs, but high in refined carbs and saturated fats from bacon",
  "health_benefits": [
    "Good source of protein",
    "Provides energy from carbohydrates",
    "Contains B vitamins from eggs"
  ]
}}

Another example, for a Teriyaki Chicken Rice Bowl:

{{
  "dish_name": "Teriyaki Chicken Rice Bowl",
  "ingredients": [
    {{"name": "chicken", "portion_count": 1, "grams": 80}},
    {{"name": "rice", "portion_count": 1, "grams": 120}},
    {{"name": "broccoli", "portion_count": 1, "grams": 40}}
  ],
  "macronutrients": {{
    "calories": 350,
    "protein": 25,
    "carbs": 45,
    "fats": 6,
    "fibers": 4,
    "saturated_fats": 1
  }},
  "health_score": 7,
  "health_explanation": "Balanced meal with lean protein, complex carbs, and vegetables, though the teriyaki sauce adds sugar",
  "health_benefits": [
    "High in protein for muscle repair",
    "Contains fiber from vegetables",
    "Provides essential vitamins from broccoli",
    "Good source of complex carbohydrates for energy"
  ]
}}

Only focus on major components. Do not list sauces, sesame seeds, green onions, herbs, or other seasonings unless they are a main part of the dish.
"""
    )


def get_macro_targets_prompt():
    """
    Returns a prompt for calculating daily calorie and macronutrient targets.

    Example output:
    {
      "daily_calories": 1800,
      "protein": 73,
      "carbs": 135,
      "fat": 67
    }
    """
    return PromptTemplate.from_template(
        """
You are a nutrition expert. Based on the user's profile, calculate appropriate daily targets for calories and macronutrients.

User Profile:
{full_profile}

Analyze the profile to determine:
1. Appropriate daily calorie intake based on age, gender, weight, height, activity level, and goals
2. Optimal protein intake in grams (typically 0.8-2.0g per kg of body weight depending on activity and goals)
3. Appropriate carbohydrate intake in grams (typically 40-60% of total calories depending on activity and goals)
4. Appropriate fat intake in grams (typically 20-35% of total calories)

Return ONLY a JSON object with the following structure:
{{
  "daily_calories": [integer],
  "protein": [integer],
  "carbs": [integer],
  "fat": [integer]
}}

Do not include any explanations, only the JSON object.
"""
    )
