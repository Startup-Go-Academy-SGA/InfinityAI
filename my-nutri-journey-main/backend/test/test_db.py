import sys
import os
import unittest
import json
from datetime import datetime, timedelta
import uuid
import warnings

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_service import SQLiteService, SupabaseService, get_db_service
from settings import ACTIVE_DB_SERVICE

# Helper function to generate a unique email for tests
def generate_test_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

class BaseDBServiceTest:
    """Base test class with tests that should work on any database service implementation"""
    
    def setUp(self):
        # This will be implemented by subclasses
        self.db_service = None
        self.test_user_ids = []
        self.test_meal_ids = []
    
    def tearDown(self):
        # Clean up created test users and meals
        # Implementation will depend on the specific database service
        pass
    
    def test_create_and_get_user(self):
        """Test creating a user and then retrieving it"""
        # Create a test user
        test_email = generate_test_email()
        user_data = {
            "name": "Test User",
            "email": test_email,
            "password_hash": "hashed_password",
            "birthdate": "1990-01-01",
            "weight": 70,
            "height": 170,
            "country": "Test Country",
            "targetWeight": 65,
            "activityLevel": "Moderate",
            "allergies": ["Peanuts", "Shellfish"],
            "dislikes": ["Broccoli"],
            "favoriteFoods": ["Pasta", "Chicken"],
            "nutritionGoal": "Weight loss",
            "daily_target_calories": 2000,
            "daily_target_carbs": 200,
            "daily_target_protein": 150,
            "daily_target_fats": 70,
            "gender": "male"
        }
        
        # Create the user
        created_user = self.db_service.create_user(user_data)
        self.assertIsNotNone(created_user)
        self.assertIsNotNone(created_user.get("id"))
        user_id = created_user["id"]
        self.test_user_ids.append(user_id)
        
        # Retrieve the user
        retrieved_user = self.db_service.get_user(user_id)
        self.assertEqual(retrieved_user["name"], "Test User")
        self.assertEqual(retrieved_user["email"], test_email)
        
        # Check that list fields were properly serialized and deserialized
        self.assertIsInstance(retrieved_user["allergies"], list)
        self.assertIn("Peanuts", retrieved_user["allergies"])
        self.assertIsInstance(retrieved_user["dislikes"], list)
        self.assertIn("Broccoli", retrieved_user["dislikes"])
        self.assertIsInstance(retrieved_user["favoriteFoods"], list)
        self.assertIn("Pasta", retrieved_user["favoriteFoods"])
    
    def test_update_user(self):
        """Test updating a user"""
        # First create a user
        test_email = generate_test_email()
        user_data = {
            "name": "Update Test",
            "email": test_email,
            "password_hash": "hashed_password",
            "birthdate": "1990-01-01",
            "weight": 70,
            "height": 170,
            "country": "Test Country",
            "targetWeight": 65,
            "activityLevel": "Moderate",
            "allergies": ["Peanuts"],
            "dislikes": ["Broccoli"],
            "favoriteFoods": ["Pasta"],
            "nutritionGoal": "Weight loss",
            "gender": "female"
        }
        
        created_user = self.db_service.create_user(user_data)
        user_id = created_user["id"]
        self.test_user_ids.append(user_id)
        
        # Update the user
        update_data = {
            "name": "Updated Name",
            "weight": 75,
            "allergies": ["Peanuts", "Milk"],
            "favoriteFoods": ["Pasta", "Rice"]
        }
        
        updated_user = self.db_service.update_user(user_id, update_data)
        self.assertEqual(updated_user["name"], "Updated Name")
        self.assertEqual(updated_user["weight"], 75)
        self.assertIn("Milk", updated_user["allergies"])
        self.assertIn("Rice", updated_user["favoriteFoods"])
        
        # Verify other fields weren't changed
        self.assertEqual(updated_user["email"], test_email)
        self.assertEqual(updated_user["gender"], "female")
    
    def test_get_user_by_email(self):
        """Test retrieving a user by email"""
        # Create a user with a known email
        test_email = generate_test_email()
        user_data = {
            "name": "Email Test",
            "email": test_email,
            "password_hash": "hashed_password",
            "birthdate": "1990-01-01",
            "weight": 70,
            "height": 170,
            "country": "Test Country",
            "targetWeight": 65,
            "activityLevel": "Moderate",
            "allergies": [],
            "dislikes": [],
            "favoriteFoods": [],
            "nutritionGoal": ""
        }
        
        created_user = self.db_service.create_user(user_data)
        user_id = created_user["id"]
        self.test_user_ids.append(user_id)
        
        # Retrieve by email
        retrieved_user = self.db_service.get_user_by_email(test_email)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user["name"], "Email Test")
        
        # Test with non-existent email
        non_existent = self.db_service.get_user_by_email("nonexistent@example.com")
        self.assertIsNone(non_existent)
    
    def test_insert_and_get_meal(self):
        """Test inserting a meal and retrieving it by date"""
        # First create a user
        test_email = generate_test_email()
        user_data = {
            "name": "Meal Test User",
            "email": test_email,
            "password_hash": "hashed_password",
            "birthdate": "1990-01-01",
            "weight": 70,
            "height": 170,
            "country": "Test Country",
            "targetWeight": 65,
            "activityLevel": "Moderate",
            "allergies": [],
            "dislikes": [],
            "favoriteFoods": [],
            "nutritionGoal": ""
        }
        
        created_user = self.db_service.create_user(user_data)
        user_id = created_user["id"]
        self.test_user_ids.append(user_id)
        
        # Create a meal
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meal_data = {
            "user_id": user_id,
            "meal_type": "lunch",
            "meal_json": {
                "name": "Test Meal",
                "ingredients": [
                    {"name": "Chicken", "amount": "100g"},
                    {"name": "Rice", "amount": "150g"}
                ],
                "macronutrients": {
                    "calories": 400,
                    "protein": 30,
                    "carbs": 45,
                    "fat": 10
                }
            },
            "uploaded_at": today,
            "health_score": 8.5
        }
        
        created_meal = self.db_service.insert_meal(meal_data)
        self.assertIsNotNone(created_meal)
        if isinstance(created_meal, dict) and "id" in created_meal:
            self.test_meal_ids.append(created_meal["id"])
        
        # Get meals for today
        today_date = datetime.now().strftime("%Y-%m-%d")
        meals = self.db_service.get_meals_by_date(user_id, today_date)
        
        self.assertTrue(len(meals) > 0)
        found_meal = False
        for meal in meals:
            # Check if this is our test meal
            if isinstance(meal["meal_json"], dict) and meal["meal_json"].get("name") == "Test Meal":
                found_meal = True
                self.assertEqual(meal["meal_type"], "lunch")
                self.assertEqual(meal["health_score"], 8.5)
                self.assertEqual(meal["meal_json"]["macronutrients"]["calories"], 400)
        
        self.assertTrue(found_meal, "Could not find the test meal in the retrieved meals")
    
    def test_get_meals_by_timeframe(self):
        """Test retrieving meals within a specific timeframe"""
        # First create a user
        test_email = generate_test_email()
        user_data = {
            "name": "Timeframe Test User",
            "email": test_email,
            "password_hash": "hashed_password",
            "birthdate": "1990-01-01",
            "weight": 70,
            "height": 170,
            "allergies": [],
            "dislikes": [],
            "favoriteFoods": []
        }
        
        created_user = self.db_service.create_user(user_data)
        user_id = created_user["id"]
        self.test_user_ids.append(user_id)
        
        # Create meals for different dates
        now = datetime.now()
        dates = [
            (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
            now.strftime("%Y-%m-%d %H:%M:%S")
        ]
        
        for i, date in enumerate(dates):
            meal_data = {
                "user_id": user_id,
                "meal_type": "dinner",
                "meal_json": {
                    "name": f"Timeframe Meal {i}",
                    "ingredients": [{"name": "Test Ingredient"}],
                    "macronutrients": {"calories": 400}
                },
                "uploaded_at": date,
                "health_score": 7.0
            }
            created_meal = self.db_service.insert_meal(meal_data)
            if isinstance(created_meal, dict) and "id" in created_meal:
                self.test_meal_ids.append(created_meal["id"])
        
        # Get meals from 7 days ago
        seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        recent_meals = self.db_service.get_meals_by_timeframe(user_id, seven_days_ago)
        
        # Should find 2 meals (from 5 days ago and today)
        self.assertEqual(len(recent_meals), 2)
        
        # Check meal names
        meal_names = [meal["meal_json"]["name"] for meal in recent_meals]
        self.assertIn("Timeframe Meal 1", meal_names)
        self.assertIn("Timeframe Meal 2", meal_names)
        
        # Get all meals
        far_past = "2000-01-01"
        all_meals = self.db_service.get_meals_by_timeframe(user_id, far_past)
        self.assertEqual(len(all_meals), 3)
    
    def test_recommended_meals(self):
        """Test inserting and retrieving recommended meals"""
        # First create a user
        test_email = generate_test_email()
        user_data = {
            "name": "Recommendations Test User",
            "email": test_email,
            "password_hash": "hashed_password",
            "birthdate": "1990-01-01",
            "weight": 70,
            "height": 170,
            "allergies": [],
            "dislikes": [],
            "favoriteFoods": []
        }
        
        created_user = self.db_service.create_user(user_data)
        user_id = created_user["id"]
        self.test_user_ids.append(user_id)
        
        # Create some recommended meals
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        
        recommendations = [
            {
                "user_id": user_id,
                "planned_date": today,
                "meal_type": "breakfast",
                "dish_name": "Oatmeal with Berries",
                "macronutrients_json": {
                    "calories": 350,
                    "protein": 10,
                    "carbs": 60,
                    "fat": 5
                },
                "ingredients_json": [
                    {"name": "Rolled oats", "amount": "50g"},
                    {"name": "Mixed berries", "amount": "100g"},
                    {"name": "Almond milk", "amount": "200ml"}
                ]
            },
            {
                "user_id": user_id,
                "planned_date": today,
                "meal_type": "lunch",
                "dish_name": "Chicken Salad",
                "macronutrients_json": {
                    "calories": 450,
                    "protein": 35,
                    "carbs": 15,
                    "fat": 25
                },
                "ingredients_json": [
                    {"name": "Chicken breast", "amount": "150g"},
                    {"name": "Mixed greens", "amount": "100g"},
                    {"name": "Olive oil", "amount": "15ml"}
                ]
            },
            {
                "user_id": user_id,
                "planned_date": tomorrow,
                "meal_type": "breakfast",
                "dish_name": "Protein Smoothie",
                "macronutrients_json": {
                    "calories": 300,
                    "protein": 25,
                    "carbs": 30,
                    "fat": 10
                },
                "ingredients_json": [
                    {"name": "Protein powder", "amount": "30g"},
                    {"name": "Banana", "amount": "1 medium"},
                    {"name": "Milk", "amount": "250ml"}
                ]
            }
        ]
        
        # Insert the recommendations
        inserted_recommendations = self.db_service.insert_recommended_meals(recommendations)
        self.assertEqual(len(inserted_recommendations), 3)
        
        # Get recommendations for today
        today_recommendations = self.db_service.get_recommended_meals_by_date(user_id, today)
        self.assertEqual(len(today_recommendations), 2)
        
        # Check meal types
        meal_types = [meal["meal_type"] for meal in today_recommendations]
        self.assertIn("breakfast", meal_types)
        self.assertIn("lunch", meal_types)
        
        # Get recommendations for tomorrow
        tomorrow_recommendations = self.db_service.get_recommended_meals_by_date(user_id, tomorrow)
        self.assertEqual(len(tomorrow_recommendations), 1)
        self.assertEqual(tomorrow_recommendations[0]["dish_name"], "Protein Smoothie")


class TestSQLiteService(unittest.TestCase, BaseDBServiceTest):
    """Test the SQLite implementation of the database service"""
    
    def setUp(self):
        self.db_service = SQLiteService()
        self.test_user_ids = []
        self.test_meal_ids = []
    
    def tearDown(self):
        # Clean up test data - delete test users and their meals
        for user_id in self.test_user_ids:
            try:
                with self.db_service.get_user_db() as conn:
                    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            except Exception as e:
                print(f"Error cleaning up test user {user_id}: {e}")
        
        # Clean up test meals if we have their IDs
        for meal_id in self.test_meal_ids:
            try:
                with self.db_service.get_meal_db() as conn:
                    conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
            except Exception as e:
                print(f"Error cleaning up test meal {meal_id}: {e}")


class TestSupabaseService(unittest.TestCase, BaseDBServiceTest):
    """Test the Supabase implementation of the database service"""
    
    def setUp(self):
        # Skip Supabase tests if credentials are not available
        try:
            self.db_service = SupabaseService()
            self.test_user_ids = []
            self.test_meal_ids = []
        except Exception as e:
            self.skipTest(f"Supabase service initialization failed: {e}")
    
    def tearDown(self):
        # Clean up test data - delete test users and their meals
        for user_id in self.test_user_ids:
            try:
                self.db_service.get_user_db().delete().eq("id", user_id).execute()
            except Exception as e:
                print(f"Error cleaning up test user {user_id}: {e}")
        
        # Clean up test meals if we have their IDs
        for meal_id in self.test_meal_ids:
            try:
                self.db_service.get_meal_db().delete().eq("id", meal_id).execute()
            except Exception as e:
                print(f"Error cleaning up test meal {meal_id}: {e}")


class TestActiveDBService(unittest.TestCase):
    """Test the active database service selection function"""
    
    def test_get_db_service(self):
        """Test that get_db_service returns the appropriate service"""
        service = get_db_service()
        
        if ACTIVE_DB_SERVICE == "sqlite":
            self.assertIsInstance(service, SQLiteService)
        elif ACTIVE_DB_SERVICE == "supabase":
            self.assertIsInstance(service, SupabaseService)
        else:
            self.fail(f"Unknown active DB service: {ACTIVE_DB_SERVICE}")


if __name__ == "__main__":
    unittest.main()