import os
from dotenv import load_dotenv
load_dotenv()

# OpenAI model to use (if LLM is enabled)
OPENAI_MODEL = "gpt-4o"  # Main LLM model for production
OPENAI_MODEL_2 = "gpt-3.5-turbo"  # Alternative LLM model for production
LLM_TIMEOUT = 20  # Timeout for LLM requests in seconds

TEST_OPENAI_MODEL = "gpt-4o"  # LLM model for testing or development

# LLM provider settings
LLM_PROVIDER = "openai"  # Main LLM provider
TEST_LLM_PROVIDER = "openai"  # LLM provider for testing

# OpenAI API key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")  # API key for OpenAI, loaded from environment

UPLOADED_MEALS_DIR = "data/uploaded_meals"  # Directory for storing uploaded meal images/files
TEMP_UPLOAD_DIR = "data/temp_upload"  # Directory for temporary uploads
#FOOD_DB_PATH = "data/food_db.csv"  # Path to the food database CSV

os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)  # Ensure temp upload directory exists

#USER_DB_PATH = "data/users.db"  # Path to the user database
#MEAL_DB_PATH = "data/meals.db"  # Path to the meals database
#RECOMMENDED_MEALS_DB_PATH = "data/recommended_meals.db"  # Path to the recommended meals database
NUM_RECOMMENDATION_DAYS = 3  # Number of days to generate meal recommendations for

SUPABASE_URL = "https://dydwkwjpuubiyyboiqcy.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "dish-images"

ACTIVE_DB_SERVICE='supabase'  # Active database service, can be 'sqlite' or 'supabase'




