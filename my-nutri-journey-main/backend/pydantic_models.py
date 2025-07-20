from pydantic import BaseModel
from typing import Optional, List

class UserProfile(BaseModel):
    id: Optional[int] = None
    name: str
    birthdate: str  # ISO format: YYYY-MM-DD
    weight: int
    height: int
    country: str
    targetWeight: int
    activityLevel: str
    allergies: List[str]
    dislikes: List[str]
    favoriteFoods: List[str] = []
    nutritionGoal: str = ""
    userProfile: str = ""
    daily_target_calories: Optional[int] = None
    daily_target_carbs: Optional[int] = None
    daily_target_protein: Optional[int] = None
    daily_target_fats: Optional[int] = None
    num_meals_per_day: int = 3
    gender: str = "other"

class ChatRequest(BaseModel):
    user_id: int
    message: str
    chat_history: Optional[List[dict]] = []

class RecommendedMealsRequest(BaseModel):
    user_id: int
    date: str

class MealLogRequest(BaseModel):
    user_id: int
    meal_type: str
    meal_json: dict
    health_score: Optional[float] = None
    uploaded_at: str  # ISO string
    consumed_date: Optional[str] = None  # Add consumed_date field (YYYY-MM-DD)