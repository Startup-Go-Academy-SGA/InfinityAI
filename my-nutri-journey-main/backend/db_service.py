from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import os
import ast
from fastapi import HTTPException
from settings import ACTIVE_DB_SERVICE

# Import only when needed based on chosen DB service
try:
    from supabase import create_client, Client
except ImportError:
    # This will only cause an error if Supabase is selected as the service
    pass

try:
    import sqlite3
except ImportError:
    # This will only cause an error if SQLite is selected as the service
    pass

# The active database service (can be changed to 'sqlite' or 'supabase')
ACTIVE_DB_SERVICE = ACTIVE_DB_SERVICE

class DatabaseService:
    """Abstract base class for database services"""
    
    def get_user_db(self):
        """Get a reference to the users table"""
        raise NotImplementedError
        
    def get_meal_db(self):
        """Get a reference to the meals table"""
        raise NotImplementedError
        
    def get_recommended_meal_db(self):
        """Get a reference to the recommended_meals table"""
        raise NotImplementedError
        
    def get_user(self, user_id: int) -> Dict:
        """Get a user by ID"""
        raise NotImplementedError
        
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        raise NotImplementedError
        
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        """Update a user"""
        raise NotImplementedError
        
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get a user by email"""
        raise NotImplementedError
        
    def insert_meal(self, meal_data: Dict) -> Dict:
        """Insert a meal"""
        raise NotImplementedError
        
    def get_meals_by_date(self, user_id: int, date: str) -> List[Dict]:
        """Get meals for a user on a specific date"""
        raise NotImplementedError
        
    def insert_recommended_meals(self, meals_data: List[Dict]) -> List[Dict]:
        """Insert recommended meals"""
        raise NotImplementedError
        
    def get_recommended_meals_by_date(self, user_id: int, date: str) -> List[Dict]:
        """Get recommended meals for a user on a specific date"""
        raise NotImplementedError

    def get_meals_by_timeframe(self, user_id: int, start_date: str) -> List[Dict]:
        """Get all meals for a user after a specific date"""
        raise NotImplementedError
    
    def get_meal_by_id(self, meal_id: int) -> Dict:
        """Get a meal by ID"""
        raise NotImplementedError
        
    def delete_meal(self, meal_id: int) -> bool:
        """Delete a meal by ID"""
        raise NotImplementedError
    
    def get_meals_by_upload_date(self, user_id: int, date: str) -> List[Dict]:
        """Get meals where consumed_date is missing but uploaded_at starts with the date."""
        pass  # This will be implemented in the specific service classes


class SupabaseService(DatabaseService):
    """Supabase implementation of the database service"""
    
    def __init__(self):
        from supabase import create_client, Client
        from settings import SUPABASE_URL, SUPABASE_KEY
        
        # Initialize with timeout configuration
        self.supabase = create_client(
            SUPABASE_URL, 
            SUPABASE_KEY,
        )
        
    def get_user_db(self):
        return self.supabase.table("users")
        
    def get_meal_db(self):
        return self.supabase.table("meals")
        
    def get_recommended_meal_db(self):
        return self.supabase.table("recommended_meals")
        
    def get_user(self, user_id: int) -> Dict:
        response = self.get_user_db().select("*").eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = response.data[0]
        
        # Process the user data
        user_dict = dict(user)
        # Convert string arrays to Python lists
        user_dict["allergies"] = json.loads(user["allergies"]) if user["allergies"] else []
        user_dict["dislikes"] = json.loads(user["dislikes"]) if user["dislikes"] else []
        user_dict["favoriteFoods"] = json.loads(user["favoriteFoods"]) if user["favoriteFoods"] else []
        
        return user_dict
        
    def create_user(self, user_data: Dict) -> Dict:
        # Ensure lists are serialized to JSON strings for Supabase
        user_data_copy = user_data.copy()
        for field in ["allergies", "dislikes", "favoriteFoods"]:
            if field in user_data_copy and isinstance(user_data_copy[field], list):
                user_data_copy[field] = json.dumps(user_data_copy[field])
                
        response = self.get_user_db().insert(user_data_copy).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return response.data[0]
        
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        # Ensure lists are serialized to JSON strings for Supabase
        user_data_copy = user_data.copy()
        for field in ["allergies", "dislikes", "favoriteFoods"]:
            if field in user_data_copy and isinstance(user_data_copy[field], list):
                user_data_copy[field] = json.dumps(user_data_copy[field])
                
        response = self.get_user_db().update(user_data_copy).eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to update user")
        
        return response.data[0]
        
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        response = self.get_user_db().select("*").eq("email", email).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]
        
    def insert_meal(self, meal_data: Dict) -> Dict:
        response = self.get_meal_db().insert(meal_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to insert meal")
        
        return response.data[0]
        
    def get_meals_by_date(self, user_id: int, date: str) -> List[Dict]:
        # For Supabase service
        response = self.get_meal_db().select("*").eq("user_id", user_id).eq("consumed_date", date).order("uploaded_at").execute()
        return response.data
        
    def insert_recommended_meals(self, meals_data: List[Dict]) -> List[Dict]:
        if not meals_data:
            return []
            
        response = self.get_recommended_meal_db().insert(meals_data).execute()
        return response.data
        
    def get_recommended_meals_by_date(self, user_id: int, date: str) -> List[Dict]:
        response = self.get_recommended_meal_db().select("*").eq("user_id", user_id).eq("planned_date", date).execute()
        return response.data

    def get_meals_by_timeframe(self, user_id: int, start_date: str) -> List[Dict]:
        """Get all meals for a user after a specific date"""
        try:
            print(f"Fetching meals from {start_date} for user {user_id}")
            
            # First try with consumed_date field
            response = self.get_meal_db() \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("consumed_date", start_date) \
                .execute()
            
            meals_by_consumed_date = response.data
            print(f"Found {len(meals_by_consumed_date)} meals with consumed_date >= {start_date}")
            
            # Then try with uploaded_at field
            response = self.get_meal_db() \
                .select("*") \
                .eq("user_id", user_id) \
                .gte("uploaded_at", start_date) \
                .execute()
            
            meals_by_uploaded_at = response.data
            print(f"Found {len(meals_by_uploaded_at)} meals with uploaded_at >= {start_date}")
            
            # Combine the results, avoiding duplicates by ID
            all_meals = {}
            for meal in meals_by_consumed_date:
                all_meals[meal["id"]] = meal
                
            for meal in meals_by_uploaded_at:
                if meal["id"] not in all_meals:
                    all_meals[meal["id"]] = meal
            
            meals = list(all_meals.values())
            
            # Parse the meal_json field if it's stored as a string
            for meal in meals:
                if isinstance(meal.get("meal_json"), str):
                    try:
                        meal["meal_json"] = json.loads(meal["meal_json"])
                    except:
                        meal["meal_json"] = {}
                        
            # Sort by date
            meals.sort(key=lambda m: m.get("uploaded_at", "") or m.get("consumed_date", ""), reverse=True)
            
            return meals
        except Exception as e:
            print(f"Error fetching meals by timeframe: {e}")
            return []
    
    def get_meal_by_id(self, meal_id: int) -> Dict:
        response = self.get_meal_db().select("*").eq("id", meal_id).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        return response.data[0]
        
    def delete_meal(self, meal_id: int) -> bool:
        response = self.get_meal_db().delete().eq("id", meal_id).execute()
        
        # Return True if the deletion was successful
        return len(response.data) > 0

    def get_meals_by_upload_date(self, user_id: int, date: str) -> List[Dict]:
        # For Supabase, we use the LIKE operator to match the date prefix
        response = self.get_meal_db().select("*") \
            .eq("user_id", user_id) \
            .is_("consumed_date", "null") \
            .like("uploaded_at", f"{date}%") \
            .execute()
        return response.data


class SQLiteService(DatabaseService):
    """SQLite implementation of the database service"""
    
    def __init__(self):
        from settings import USER_DB_PATH, MEAL_DB_PATH, RECOMMENDED_MEALS_DB_PATH
        # Ensure the database files exist and have the proper schema
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite databases if they don't exist"""
        # Create users table
        with sqlite3.connect(USER_DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    birthdate TEXT,
                    weight INTEGER,
                    height INTEGER,
                    country TEXT,
                    targetWeight INTEGER,
                    activityLevel TEXT,
                    allergies TEXT,
                    dislikes TEXT,
                    favoriteFoods TEXT,
                    nutritionGoal TEXT,
                    userProfile TEXT,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    daily_target_calories INTEGER,
                    daily_target_carbs INTEGER,
                    daily_target_protein INTEGER,
                    daily_target_fats INTEGER,
                    num_meals_per_day INTEGER DEFAULT 3,
                    gender TEXT DEFAULT 'other'
                )
            """)
            
        # Create meals table
        with sqlite3.connect(MEAL_DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    meal_type TEXT,
                    meal_json TEXT,
                    uploaded_at TEXT  # Removed extra comma
                )
            """)
            
        # Create recommended_meals table
        with sqlite3.connect(RECOMMENDED_MEALS_DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommended_meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    planned_date TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    dish_name TEXT NOT NULL,
                    macronutrients_json TEXT NOT NULL,
                    ingredients_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def get_user_db(self):
        return sqlite3.connect(USER_DB_PATH)
        
    def get_meal_db(self):
        return sqlite3.connect(MEAL_DB_PATH)
        
    def get_recommended_meal_db(self):
        return sqlite3.connect(RECOMMENDED_MEALS_DB_PATH)
        
    def get_user(self, user_id: int) -> Dict:
        with self.get_user_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        user_dict = dict(user)
        user_dict["allergies"] = ast.literal_eval(user_dict["allergies"])
        user_dict["dislikes"] = ast.literal_eval(user_dict["dislikes"])
        user_dict["favoriteFoods"] = ast.literal_eval(user_dict["favoriteFoods"])
        return user_dict
        
    def create_user(self, user_data: Dict) -> Dict:
        user_data_copy = user_data.copy()
        # Convert lists to JSON strings
        for field in ["allergies", "dislikes", "favoriteFoods"]:
            if field in user_data_copy and isinstance(user_data_copy[field], list):
                user_data_copy[field] = json.dumps(user_data_copy[field])
                
        with self.get_user_db() as conn:
            cursor = conn.cursor()
            
            # Build the INSERT query dynamically
            fields = list(user_data_copy.keys())
            placeholders = ", ".join(["?"] * len(fields))
            field_names = ", ".join(fields)
            
            query = f"INSERT INTO users ({field_names}) VALUES ({placeholders})"
            cursor.execute(query, list(user_data_copy.values()))
            
            # Get the ID of the newly inserted user
            user_id = cursor.lastrowid
            
        # Return the full user record
        return self.get_user(user_id)
        
    def update_user(self, user_id: int, user_data: Dict) -> Dict:
        user_data_copy = user_data.copy()
        # Convert lists to JSON strings
        for field in ["allergies", "dislikes", "favoriteFoods"]:
            if field in user_data_copy and isinstance(user_data_copy[field], list):
                user_data_copy[field] = json.dumps(user_data_copy[field])
                
        with self.get_user_db() as conn:
            cursor = conn.cursor()
            
            # Build the UPDATE query dynamically
            set_clause = ", ".join([f"{field} = ?" for field in user_data_copy.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            
            values = list(user_data_copy.values())
            values.append(user_id)
            
            cursor.execute(query, values)
            
        # Return the updated user record
        return self.get_user(user_id)
        
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        with self.get_user_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
        if user is None:
            return None
            
        return dict(user)
        
    def insert_meal(self, meal_data: Dict) -> Dict:
        meal_data_copy = meal_data.copy()
        
        # Ensure meal_json is a JSON string
        if "meal_json" in meal_data_copy and not isinstance(meal_data_copy["meal_json"], str):
            meal_data_copy["meal_json"] = json.dumps(meal_data_copy["meal_json"])
            
        with self.get_meal_db() as conn:
            cursor = conn.cursor()
            
            # Build the INSERT query dynamically
            fields = list(meal_data_copy.keys())
            placeholders = ", ".join(["?"] * len(fields))
            field_names = ", ".join(fields)
            
            query = f"INSERT INTO meals ({field_names}) VALUES ({placeholders})"
            cursor.execute(query, list(meal_data_copy.values()))
            
            # Get the ID of the newly inserted meal
            meal_id = cursor.lastrowid
            
        return {"id": meal_id, **meal_data}
        
    def get_meals_by_date(self, user_id: int, date: str) -> List[Dict]:
        with self.get_meal_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM meals WHERE user_id = ? AND consumed_date = ? ORDER BY uploaded_at",
                (user_id, date)
            )
            rows = cursor.fetchall()
            
        meals = []
        for row in rows:
            meal = dict(row)
            # Parse JSON fields
            if "meal_json" in meal and meal["meal_json"]:
                meal["meal_json"] = json.loads(meal["meal_json"])
            meals.append(meal)
            
        return meals
        
    def insert_recommended_meals(self, meals_data: List[Dict]) -> List[Dict]:
        if not meals_data:
            return []
            
        inserted_ids = []
        with self.get_recommended_meal_db() as conn:
            cursor = conn.cursor()
            
            for meal_data in meals_data:
                meal_data_copy = meal_data.copy()
                
                # Ensure JSON fields are strings
                if "macronutrients_json" in meal_data_copy and not isinstance(meal_data_copy["macronutrients_json"], str):
                    meal_data_copy["macronutrients_json"] = json.dumps(meal_data_copy["macronutrients_json"])
                    
                if "ingredients_json" in meal_data_copy and not isinstance(meal_data_copy["ingredients_json"], str):
                    meal_data_copy["ingredients_json"] = json.dumps(meal_data_copy["ingredients_json"])
                
                # Build the INSERT query dynamically
                fields = list(meal_data_copy.keys())
                placeholders = ", ".join(["?"] * len(fields))
                field_names = ", ".join(fields)
                
                query = f"INSERT INTO recommended_meals ({field_names}) VALUES ({placeholders})"
                cursor.execute(query, list(meal_data_copy.values()))
                
                inserted_ids.append(cursor.lastrowid)
                
        return [{"id": id, **meal} for id, meal in zip(inserted_ids, meals_data)]
        
    def get_recommended_meals_by_date(self, user_id: int, date: str) -> List[Dict]:
        with self.get_recommended_meal_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM recommended_meals WHERE user_id = ? AND planned_date = ?",
                (user_id, date)
            )
            rows = cursor.fetchall()
            
        meals = []
        for row in rows:
            meal = dict(row)
            # Parse JSON fields
            if "macronutrients_json" in meal and meal["macronutrients_json"]:
                meal["macronutrients_json"] = json.loads(meal["macronutrients_json"])
                
            if "ingredients_json" in meal and meal["ingredients_json"]:
                meal["ingredients_json"] = json.loads(meal["ingredients_json"])
                
            meals.append(meal)
            
        return meals

    def get_meals_by_timeframe(self, user_id: int, start_date: str) -> List[Dict]:
        with self.get_meal_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM meals WHERE user_id = ? AND uploaded_at >= ? ORDER BY uploaded_at",
                (user_id, start_date)
            )
            rows = cursor.fetchall()
            
        meals = []
        for row in rows:
            meal = dict(row)
            # Parse JSON fields
            if "meal_json" in meal and meal["meal_json"]:
                meal["meal_json"] = json.loads(meal["meal_json"])
            meals.append(meal)
            
        return meals
    
    def get_meal_by_id(self, meal_id: int) -> Dict:
        with self.get_meal_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM meals WHERE id = ?", (meal_id,))
            meal = cursor.fetchone()
            
        if meal is None:
            return None
            
        meal_dict = dict(meal)
        # Parse JSON fields
        if "meal_json" in meal_dict and meal_dict["meal_json"]:
            meal_dict["meal_json"] = json.loads(meal_dict["meal_json"])
            
        return meal_dict
        
    def delete_meal(self, meal_id: int) -> bool:
        with self.get_meal_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
            
        # Return True if rows were affected
        return cursor.rowcount > 0

    def get_meals_by_upload_date(self, user_id: int, date: str) -> List[Dict]:
        with self.get_meal_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM meals WHERE user_id = ? AND consumed_date IS NULL AND uploaded_at LIKE ?",
                (user_id, f"{date}%")
            )
            rows = cursor.fetchall()
            
        meals = []
        for row in rows:
            meal = dict(row)
            # Parse JSON fields
            if "meal_json" in meal and meal["meal_json"]:
                meal["meal_json"] = json.loads(meal["meal_json"])
            meals.append(meal)
            
        return meals
    

def get_db_service() -> DatabaseService:
    """Get the active database service based on configuration"""
    if ACTIVE_DB_SERVICE == "sqlite":
        return SQLiteService()
    elif ACTIVE_DB_SERVICE == "supabase":
        return SupabaseService()
    else:
        raise ValueError(f"Unsupported database service: {ACTIVE_DB_SERVICE}")