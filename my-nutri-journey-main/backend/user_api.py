from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import date, datetime, timedelta
import os
import json
import bcrypt
from prompts import get_chatbot_prompt, get_macro_targets_prompt
from llm_provider import LLMProvider
from settings import (OPENAI_MODEL, LLM_PROVIDER, OPENAI_KEY, OPENAI_MODEL_2,
                     TEMP_UPLOAD_DIR, NUM_RECOMMENDATION_DAYS, BUCKET_NAME)
import shutil
from food_analysis import dish_analysis, compute_health_score
import time
from fastapi.staticfiles import StaticFiles
from db_service import get_db_service
import time
import uuid
from collections import Counter
from pydantic_models import UserProfile, ChatRequest, RecommendedMealsRequest, MealLogRequest

# Initialize database service
db_service = get_db_service()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def compute_age(birthdate_str):
    try:
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    except ValueError:
        return 0

def generate_user_profile(user_dict):
    name = user_dict.get("name", "The user")
    gender = user_dict.get('gender', 'other')
    age = user_dict.get("age") or compute_age(user_dict.get("birthdate", "2000-01-01"))
    country = user_dict.get("country", "")
    activity = user_dict.get("activityLevel", "")
    nutrition_goal = user_dict.get("nutritionGoal", "")
    weight = user_dict.get("weight", "")
    height = user_dict.get("height", "")
    target_weight = user_dict.get("targetWeight", "")
    allergies = ", ".join(user_dict.get("allergies", []))
    dislikes = ", ".join(user_dict.get("dislikes", []))
    favorites = ", ".join(user_dict.get("favoriteFoods", []))
    num_meals_per_day = user_dict.get('num_meals_per_day', 3)

    if gender and gender.lower() != "other":
        summary = (
            f"{name} is a {gender} of {age} years old from {country} with a {activity.lower()} lifestyle. "
        )
    else:
        summary = (
            f"{name} is {age} years old from {country} with a {activity.lower()} lifestyle. "
        )
    summary += (
        f"They currently weigh {weight}kg at {height}cm tall, with a target weight of {target_weight}kg. "
        f"Nutrition goal: {nutrition_goal}. They aim to eat {num_meals_per_day} meals per day. "
        f"Allergies: {allergies if allergies else 'None'}. "
        f"Dislikes: {dislikes if dislikes else 'None'}. "
        f"Favorite foods: {favorites if favorites else 'None'}."
    )
    # Add daily macro targets if available
    macro_targets = []
    if user_dict.get("daily_target_calories"):
        macro_targets.append(f"Calories: {user_dict['daily_target_calories']} kcal")
    if user_dict.get("daily_target_protein"):
        macro_targets.append(f"Protein: {user_dict['daily_target_protein']}g")
    if user_dict.get("daily_target_carbs"):
        macro_targets.append(f"Carbs: {user_dict['daily_target_carbs']}g")
    if user_dict.get("daily_target_fats"):
        macro_targets.append(f"Fats: {user_dict['daily_target_fats']}g")
    if macro_targets:
        summary += " Daily targets — " + ", ".join(macro_targets) + "."

    return summary


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    print(f"Fetching user profile for user_id: {user_id}")
    # Get user from the database service
    user_dict = db_service.get_user(user_id)
    user_dict["userProfile"] = user_dict["userProfile"] or ""
    user_dict["age"] = compute_age(user_dict["birthdate"])
    return user_dict


@app.post("/api/users", response_model=UserProfile)
def create_user(profile: UserProfile):
    user_dict = profile.dict()
    user_dict.pop("userProfile", None)
    user_profile_summary = generate_user_profile(user_dict)
    
    # Generate macro targets
    llm = LLMProvider(provider=LLM_PROVIDER, model=OPENAI_MODEL_2, openai_api_key=OPENAI_KEY)
    macro_prompt = get_macro_targets_prompt().format(full_profile=user_profile_summary)
    macro_result = llm.ask(macro_prompt)
    macro_json = macro_result.get("response")
    
    try:
        macro_targets = json.loads(macro_json)
        print(f"Macro targets: {macro_targets}")
    except Exception as e:
        print(f"Error parsing macro JSON: {e}")
        print(f"Raw JSON: {macro_json}")
        macro_targets = {}
    
    # Extract values with proper fallbacks
    daily_calories = macro_targets.get("daily_calories", 0)
    daily_protein = macro_targets.get("protein", 0)
    daily_carbs = macro_targets.get("carbs", 0)
    daily_fats = macro_targets.get("fat", 0)
    
    # Prepare user data
    user_data = {
        "name": profile.name,
        "birthdate": profile.birthdate,
        "weight": profile.weight,
        "height": profile.height,
        "country": profile.country,
        "targetWeight": profile.targetWeight,
        "activityLevel": profile.activityLevel,
        "allergies": profile.allergies,  # The service will handle JSON conversion if needed
        "dislikes": profile.dislikes,
        "favoriteFoods": profile.favoriteFoods,
        "nutritionGoal": profile.nutritionGoal,
        "userProfile": user_profile_summary,
        "daily_target_calories": daily_calories,
        "daily_target_carbs": daily_carbs,
        "daily_target_protein": daily_protein,
        "daily_target_fats": daily_fats,
        "num_meals_per_day": profile.num_meals_per_day,
        "gender": profile.gender
    }
    
    # Create user using the database service
    created_user = db_service.create_user(user_data)
    
    # Get the complete user record
    return get_user(created_user["id"])

@app.put("/api/users/{user_id}", response_model=UserProfile)
def update_user(user_id: int, profile: UserProfile):
    # Get existing user
    existing_user = db_service.get_user(user_id)
    
    # Generate new profile summary
    user_dict = profile.dict()
    user_dict.pop("userProfile", None)
    user_profile_summary = generate_user_profile(user_dict)
    
    # Check if relevant profile data has changed
    existing_profile_summary = existing_user.get("userProfile", "")
    
    # Only recalculate macros if the profile summary has changed
    if existing_profile_summary != user_profile_summary:
        print("Profile changed, recalculating macros")
        # Generate macro targets
        llm = LLMProvider(provider=LLM_PROVIDER, model=OPENAI_MODEL_2, openai_api_key=OPENAI_KEY)
        macro_prompt = get_macro_targets_prompt().format(full_profile=user_profile_summary)
        macro_result = llm.ask(macro_prompt)
        macro_json = macro_result.get("response")
        print(f"Macro JSON: {macro_json}")
        
        try:
            macro_targets = json.loads(macro_json)
            print(f"Macro targets: {macro_targets}")
        except Exception as e:
            print(f"Error parsing macro JSON: {e}")
            print(f"Raw JSON: {macro_json}")
            macro_targets = {}
        
        # Extract values with proper fallbacks
        daily_calories = macro_targets.get("daily_calories", 0)
        daily_protein = macro_targets.get("protein", 0)
        daily_carbs = macro_targets.get("carbs", 0)
        daily_fats = macro_targets.get("fat", 0)
    else:
        print("Profile unchanged, keeping existing macro targets")
        # Keep existing values
        daily_calories = existing_user.get("daily_target_calories", 0)
        daily_protein = existing_user.get("daily_target_protein", 0)
        daily_carbs = existing_user.get("daily_target_carbs", 0)
        daily_fats = existing_user.get("daily_target_fats", 0)
    
    # Prepare updated user data
    user_data = {
        "name": profile.name,
        "birthdate": profile.birthdate,
        "weight": profile.weight,
        "height": profile.height,
        "country": profile.country,
        "targetWeight": profile.targetWeight,
        "activityLevel": profile.activityLevel,
        "allergies": profile.allergies,  # The service will handle JSON conversion if needed
        "dislikes": profile.dislikes,
        "favoriteFoods": profile.favoriteFoods,
        "nutritionGoal": profile.nutritionGoal,
        "userProfile": user_profile_summary,
        "daily_target_calories": daily_calories,
        "daily_target_carbs": daily_carbs,
        "daily_target_protein": daily_protein,
        "daily_target_fats": daily_fats,
        "num_meals_per_day": profile.num_meals_per_day,
        "gender": profile.gender
    }
    
    # Update user using the database service
    db_service.update_user(user_id, user_data)
    
    # Return the updated user
    return get_user(user_id)

@app.post("/api/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    
    # Get user by email
    user = db_service.get_user_by_email(username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return {"success": True, "user_id": user["id"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/signup")
def signup(data: dict):
    email = data.get("email")
    password = data.get("password")
    
    if not (email and password):
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    # Check if email already exists
    existing_user = db_service.get_user_by_email(email)
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    user_data = {
        "email": email,
        "password_hash": hashed_password,
        "name": "",
        "birthdate": "",
        "weight": 0,
        "height": 0,
        "country": "",
        "targetWeight": 0,
        "activityLevel": "",
        "allergies": [],  # The service will handle JSON conversion if needed
        "dislikes": [],
        "favoriteFoods": [],
        "nutritionGoal": "",
        "userProfile": ""
    }
    
    db_service.create_user(user_data)
    
    return {"success": True}

@app.post("/api/chatbot")
def chatbot_endpoint(req: ChatRequest):
    # Get user from database service instead of direct SQLite connection
    try:
        user = db_service.get_user(req.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found: {str(e)}")
    
    # Get user profile from user object
    user_profile = user.get("userProfile", "")
    
    # Format chat history as a string
    chat_history_str = ""
    for msg in req.chat_history or []:
        role = "User" if msg.get("type") == "user" else "Bot"
        chat_history_str += f"{role}: {msg.get('message')}\n"
    
    # Format the prompt using the template
    prompt_template = get_chatbot_prompt()
    prompt = prompt_template.format(
        full_profile=user_profile,
        chat_history=chat_history_str,
        question=req.message
    )
    
    # Use LLM provider to get response
    llm = LLMProvider(provider=LLM_PROVIDER, model=OPENAI_MODEL_2, openai_api_key=OPENAI_KEY)
    result = llm.ask(prompt)  # Returns dict with 'response' and 'tokens'
    
    # Log token usage
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] User {req.user_id} | Tokens used: {result.get('tokens')}")
    
    return {"response": result.get("response"), "tokens": result.get("tokens")}

@app.post("/api/log-meal")
def log_meal(data: MealLogRequest):
    if not (data.user_id and data.meal_type and data.meal_json and data.uploaded_at):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Make sure health_score is included in the meal_json
    if data.health_score and isinstance(data.meal_json, dict):
        data.meal_json["health_score"] = data.health_score
    
    # Set consumed_date to uploaded_at date if not provided
    consumed_date = data.consumed_date
    if not consumed_date:
        # Extract date part from uploaded_at
        consumed_date = data.uploaded_at.split("T")[0]
    
    meal_data = {
        "user_id": data.user_id,
        "meal_type": data.meal_type,
        "meal_json": data.meal_json,
        "uploaded_at": data.uploaded_at,
        "consumed_date": consumed_date  # Add consumed_date to database
    }
    
    db_service.insert_meal(meal_data)
    
    return {"success": True}

@app.post("/api/analyze-meal-image")
async def analyze_meal_image(
    file: UploadFile = File(...),
    user_id: int = Form(None),
):
    # Generate a unique filename to avoid collisions
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    
    # Save uploaded file to a temporary path first
    temp_ext = os.path.splitext(file.filename)[-1] or ".jpg"
    temp_path = os.path.join(TEMP_UPLOAD_DIR, f"meal_{timestamp}_{unique_id}{temp_ext}")
    
    # Save the file locally for analysis
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Analyze the image using your existing function
    result = dish_analysis(temp_path)
    if result is None:
        # Clean up the temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # Return an error response that the frontend can handle
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "No dish recognized",
                "message": "The system couldn't recognize any food in this image. Please try another image or enter meal details manually."
            }
        )
    
    # Remove ingredients with error or not found
    filtered_ingredients = [
        ing for ing in result.get("ingredients", [])
        if not ing.get("error")
    ]
    result["ingredients"] = filtered_ingredients

    # Use analyzed dish name for saving, all lowercase
    dish_name = result.get("dish_name", "meal").replace(" ", "_").lower()
    
    # Create a Supabase-friendly filename
    save_name = f"meals/{user_id}/log_{dish_name}_{timestamp}_{unique_id}{temp_ext}"
    
    # Upload to Supabase Storage
    try:
        # Read the file content
        with open(temp_path, "rb") as f:
            file_content = f.read()
        
        # Use the database service to determine which storage method to use
        if hasattr(db_service, "supabase"):
            # Using Supabase
            print(f"Uploading image to Supabase bucket: {BUCKET_NAME}/{save_name}")
            # Get storage reference
            storage = db_service.supabase.storage.from_(BUCKET_NAME)
            # Upload file
            response = storage.upload(
                path=save_name,
                file=file_content,
                file_options={"content-type": f"image/{temp_ext.lstrip('.')}"}
            )
            
            # Generate the public URL
            image_url = storage.get_public_url(save_name)
            result["img_path"] = image_url
            print(f"Image uploaded to Supabase: {image_url}")
    except Exception as e:
        print(f"Error uploading image: {e}")
    finally:
        # Clean up the temp file if it still exists
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # Create a structured meal_json similar to recommended meals
    meal_json = {
        "dish_name": result.get("dish_name", "Unknown Meal"),
        "macronutrients": {
            "calories": result.get("macronutrients", {}).get("calories", 0),
            "protein": result.get("macronutrients", {}).get("protein", 0), 
            "carbs": result.get("macronutrients", {}).get("carbs", 0),
            "fats": result.get("macronutrients", {}).get("fats", 0),
            "fibers": result.get("macronutrients", {}).get("fibers", 0),
            "saturated_fats": result.get("macronutrients", {}).get("saturated_fats", 0)
        },
        "ingredients": result.get("ingredients", []),
        "health_score": result.get("health_score", compute_health_score(result)),
        "health_benefits": result.get("health_benefits", []),
        "health_explanation": result.get("health_explanation", ""),
        "img_path": result.get("img_path", "")
    }
    
    # Add user_id to the result
    result["user_id"] = user_id
    
    # Replace the original result with the structured meal_json format
    result["meal_json"] = meal_json
    
    print(f"Meal analyzed with health score: {meal_json['health_score']}")

    return JSONResponse(content=result)

@app.get("/api/meals")
def get_meals(user_id: int = Query(...), date: str = Query(...)):
    """
    Get all meals for a user on a specific date (YYYY-MM-DD).
    """
    # First try to get meals by consumed_date
    meals_data = db_service.get_meals_by_date(user_id, date)
    
    # Also get meals where consumed_date is missing but uploaded_at matches the date
    # This requires modifying the database service to handle this case
    if hasattr(db_service, "get_meals_by_upload_date"):
        # If your service has a specialized method
        additional_meals = db_service.get_meals_by_upload_date(user_id, date)
        meals_data.extend(additional_meals)
    else:
        # General fallback approach
        all_meals = db_service.get_all_meals_for_user(user_id)
        for meal in all_meals:
            # If meal has no consumed_date but uploaded_at matches the requested date
            if (not meal.get("consumed_date") and 
                meal.get("uploaded_at") and 
                meal.get("uploaded_at").startswith(date)):
                meals_data.append(meal)
    
    meals = []
    for meal in meals_data:
        meal_dict = dict(meal)
        
        # Set consumed_date to uploaded_at date if missing
        if not meal_dict.get("consumed_date") and meal_dict.get("uploaded_at"):
            meal_dict["consumed_date"] = meal_dict["uploaded_at"].split("T")[0]
        
        # Include health score
        if "health_score" in meal_dict and meal_dict["health_score"]:
            pass  # Keep the existing health score
        elif "macronutrients" in meal_dict.get("meal_json", {}):
            meal_dict["health_score"] = compute_health_score(meal_dict["meal_json"])
            
        meals.append(meal_dict)
        
    return meals

@app.get("/api/analytics")
def get_analytics(user_id: int = Query(...), timeframe: str = Query("week")):
    """
    Get analytics data for a user based on the specified timeframe.
    Timeframes: 'week', 'month', 'quarter', 'overall'
    """
    # Helper functions for extracting meal data
    def get_meal_calories(meal):
        return meal.get("meal_json", {}).get("macronutrients", {}).get("calories", 0)
        
    def get_meal_protein(meal):
        return meal.get("meal_json", {}).get("macronutrients", {}).get("protein", 0)
        
    def get_meal_carbs(meal):
        return meal.get("meal_json", {}).get("macronutrients", {}).get("carbs", 0)
        
    def get_meal_fats(meal):
        macros = meal.get("meal_json", {}).get("macronutrients", {})
        return macros.get("fats", macros.get("fat", 0))
        
    def get_meal_health_score(meal):
        return meal.get("meal_json", {}).get("health_score", 0)
    
    # Calculate date range based on timeframe
    today = datetime.now().date()
    
    if timeframe == "week":
        start_date = today - timedelta(days=6)  # Last 7 days including today
        date_format = "%a"  # Day of week abbr (Mon, Tue, etc.)
    elif timeframe == "month":
        start_date = today - timedelta(days=29)  # Last 30 days including today
        date_format = "%b %d"  # Month abbr + day (Jan 01, etc.)
    elif timeframe == "quarter":
        start_date = today - timedelta(days=89)  # Last 90 days including today
        date_format = "%b %d"  # Month abbr + day
    elif timeframe == "overall":
        # For overall, get all meals and find the earliest date
        all_meals = db_service.get_meals_by_timeframe(user_id, "0001-01-01")
        
        if all_meals:
            earliest_dates = []
            for meal in all_meals:
                try:
                    if meal.get("consumed_date"):
                        earliest_dates.append(datetime.strptime(meal["consumed_date"], "%Y-%m-%d").date())
                    elif meal.get("uploaded_at"):
                        if "T" in meal["uploaded_at"]:
                            earliest_dates.append(datetime.fromisoformat(meal["uploaded_at"].replace("Z", "")).date())
                        else:
                            earliest_dates.append(datetime.strptime(meal["uploaded_at"], "%Y-%m-%d").date())
                except:
                    continue
            
            if earliest_dates:
                start_date = min(earliest_dates)
                print(f"Found earliest meal date: {start_date}")
            else:
                start_date = today - timedelta(days=29)  # Default to 30 days if no valid dates
        else:
            start_date = today - timedelta(days=29)  # Default to 30 days if no meals
            
        date_format = "%b %d"  # Month abbr + day
    else:
        start_date = today - timedelta(days=6)  # Default to week
        date_format = "%a"
    
    # Format for query
    start_date_str = start_date.strftime("%Y-%m-%d")
    print(f"Analytics date range: {start_date_str} to {today.strftime('%Y-%m-%d')}")
    
    # Get all meals in the time range
    meals = db_service.get_meals_by_timeframe(user_id, start_date_str)
    print(f"Retrieved {len(meals)} meals for user {user_id}")
    
    # Group meals by date
    meals_by_date = {}
    for meal in meals:
        # Extract date from various possible sources
        meal_date = None
        
        # Try consumed_date first
        if meal.get("consumed_date"):
            try:
                meal_date = datetime.strptime(meal["consumed_date"], "%Y-%m-%d").date()
            except:
                pass
        
        # Try uploaded_at if consumed_date not available or invalid
        if not meal_date and meal.get("uploaded_at"):
            try:
                if "T" in meal["uploaded_at"]:
                    meal_date = datetime.fromisoformat(meal["uploaded_at"].replace("Z", "")).date()
                else:
                    meal_date = datetime.strptime(meal["uploaded_at"], "%Y-%m-%d").date()
            except:
                pass
        
        # Skip meals with no valid date
        if not meal_date:
            continue
            
        meal_date_str = meal_date.strftime("%Y-%m-%d")
        
        # Skip meals outside our timeframe
        if meal_date < start_date or meal_date > today:
            continue
        
        if meal_date_str not in meals_by_date:
            meals_by_date[meal_date_str] = []
            
        meals_by_date[meal_date_str].append(meal)
    
    # Generate daily stats for the chart - include ALL dates in the range
    daily_stats = []
    
    # Create a date range to ensure all dates are included (even those without meals)
    current_date = start_date
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        display_date = current_date.strftime(date_format)
        
        day_meals = meals_by_date.get(date_str, [])
        
        # Calculate daily totals
        daily_calories = sum(get_meal_calories(meal) for meal in day_meals)
        daily_protein = sum(get_meal_protein(meal) for meal in day_meals)
        daily_carbs = sum(get_meal_carbs(meal) for meal in day_meals)
        daily_fats = sum(get_meal_fats(meal) for meal in day_meals)
        
        # Calculate average health score if meals exist
        health_scores = [get_meal_health_score(meal) for meal in day_meals if get_meal_health_score(meal) > 0]
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
        
        daily_stats.append({
            "date": date_str,
            "display_date": display_date,
            "calories": daily_calories,
            "protein": daily_protein,
            "carbs": daily_carbs,
            "fats": daily_fats,
            "health_score": avg_health_score,
            "meals": day_meals
        })
        
        current_date += timedelta(days=1)
    
    # Calculate overall statistics
    all_meal_dates = set(meals_by_date.keys())
    days_tracked = len(all_meal_dates)
    total_meals = sum(len(meals) for meals in meals_by_date.values())
    
    # Calculate averages for days that have meals
    if total_meals > 0:
        avg_calories = sum(get_meal_calories(meal) for meals_list in meals_by_date.values() for meal in meals_list) / total_meals
        avg_protein = sum(get_meal_protein(meal) for meals_list in meals_by_date.values() for meal in meals_list) / total_meals
        avg_carbs = sum(get_meal_carbs(meal) for meals_list in meals_by_date.values() for meal in meals_list) / total_meals
        avg_fats = sum(get_meal_fats(meal) for meals_list in meals_by_date.values() for meal in meals_list) / total_meals
        
        # Health score average
        all_health_scores = [get_meal_health_score(meal) for meals_list in meals_by_date.values() for meal in meals_list if get_meal_health_score(meal) > 0]
        avg_health_score = sum(all_health_scores) / len(all_health_scores) if all_health_scores else 0
    else:
        avg_calories = 0
        avg_protein = 0
        avg_carbs = 0
        avg_fats = 0
        avg_health_score = 0
    
    # Calculate macro distribution
    total_protein_cals = avg_protein * 4
    total_carbs_cals = avg_carbs * 4
    total_fats_cals = avg_fats * 9
    total_macros_cals = total_protein_cals + total_carbs_cals + total_fats_cals
    
    # Avoid division by zero
    if total_macros_cals > 0:
        protein_pct = round((total_protein_cals / total_macros_cals) * 100)
        carbs_pct = round((total_carbs_cals / total_macros_cals) * 100)
        fats_pct = round((total_fats_cals / total_macros_cals) * 100)
        
        # Ensure percentages add up to 100%
        total = protein_pct + carbs_pct + fats_pct
        if total != 100:
            # Adjust the largest value
            if protein_pct >= carbs_pct and protein_pct >= fats_pct:
                protein_pct += (100 - total)
            elif carbs_pct >= protein_pct and carbs_pct >= fats_pct:
                carbs_pct += (100 - total)
            else:
                fats_pct += (100 - total)
    else:
        protein_pct = 33
        carbs_pct = 34
        fats_pct = 33
    
    # Find most frequent foods
    all_foods = []
    for meal_list in meals_by_date.values():
        for meal in meal_list:
            for ingredient in meal.get("meal_json", {}).get("ingredients", []):
                if isinstance(ingredient, dict):
                    food_name = ingredient.get("name") or ingredient.get("food") or ingredient.get("matched_food")
                elif isinstance(ingredient, str):
                    food_name = ingredient
                else:
                    food_name = None
                    
                if food_name:
                    all_foods.append(food_name.lower())
    
    food_counter = Counter(all_foods)
    most_frequent = [{"name": name.title(), "count": count} for name, count in food_counter.most_common(10)]
    
    # Generate response
    return {
        "summary": {
            "days_tracked": days_tracked,
            "avg_calories": round(avg_calories),
            "avg_health_score": round(avg_health_score, 1),
            "total_meals": total_meals,
            "avg_protein": round(avg_protein),
            "avg_carbs": round(avg_carbs),
            "avg_fats": round(avg_fats)
        },
        "daily_stats": daily_stats,
        "macro_distribution": [
            {"name": "Protein", "value": protein_pct, "color": "#3B82F6"},
            {"name": "Carbs", "value": carbs_pct, "color": "#F97316"},
            {"name": "Fats", "value": fats_pct, "color": "#8B5CF6"}
        ],
        "frequent_foods": most_frequent
    }

def generate_and_store_mealplan(user_id, user_profile, num_days=NUM_RECOMMENDATION_DAYS):
    from prompts import get_mealplan_prompt

    llm = LLMProvider(provider=LLM_PROVIDER, model=OPENAI_MODEL, openai_api_key=OPENAI_KEY)
    prompt = get_mealplan_prompt(user_profile, num_days).format(
        user_profile=user_profile,
        num_days=num_days
    )
    mealplan_json = llm.ask(prompt).get("response")
    mealplan_json = json.loads(mealplan_json)  # Should return a dict as per prompt spec

    today = datetime.now().date()
    
    # Prepare meals for insertion
    meals_to_insert = []
    
    for day_idx in range(num_days):
        planned_date = (today + timedelta(days=day_idx)).isoformat()
        day_key = f"day{day_idx+1}"
        day_meals = mealplan_json.get(day_key, {})
        
        for meal_type, dishes in day_meals.items():
            for dish in dishes:
                # Format meal data similar to logged meals
                meal_data = {
                    "user_id": user_id,
                    "meal_type": meal_type,
                    "planned_date": planned_date,
                    "meal_json": {
                        "dish_name": dish["dish_name"],
                        "macronutrients": dish["macronutrients"],
                        "ingredients": dish["ingredients"],
                        "health_score": dish.get("health_score", 7),
                        "health_benefits": dish.get("health_benefits", []),
                        "health_explanation": dish.get("health_explanation", "")
                    }
                }
                meals_to_insert.append(meal_data)
    
    if meals_to_insert:
        db_service.insert_recommended_meals(meals_to_insert)
    
    return mealplan_json

def get_recommended_meals_for_date(user_id, date):
    return db_service.get_recommended_meals_by_date(user_id, date)

@app.post("/api/recommended-meals")
def generate_recommended_meals(req: RecommendedMealsRequest):
    user_id = req.user_id
    date = req.date
    
    # Get recommended meals for the date
    meals = get_recommended_meals_for_date(user_id, date)
    
    # If no meals for today, generate new recommendations
    today_str = datetime.now().date().isoformat()
    if not meals and date == today_str:
        # Get user profile
        user_data = db_service.get_user(user_id)
        user_profile = user_data.get("userProfile", "")
        
        if len(user_profile) > 10:  # Make sure we have a valid profile
            print(f"[recommended-meals] User {user_id} requested recommendations for {date}")
            generate_and_store_mealplan(user_id, user_profile, num_days=NUM_RECOMMENDATION_DAYS)
            meals = get_recommended_meals_for_date(user_id, date)
            print(f"[recommended-meals] Generated new meal plan for user {user_id} on {date}")
            
    return meals

@app.delete("/api/meals/{meal_id}")
def delete_meal(meal_id: int, user_id: int = Query(...)):
    """
    Delete a meal by ID.
    Requires the user_id for security to ensure users can only delete their own meals.
    """
    try:
        # First, check if the meal exists and belongs to the user
        meal = db_service.get_meal_by_id(meal_id)
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
            
        if meal.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this meal")
            
        # Delete the meal from the database
        db_service.delete_meal(meal_id)
        
        return {"success": True, "message": "Meal deleted successfully"}
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        print(f"Error deleting meal: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete meal: {str(e)}")