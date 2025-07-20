# Backend Setup and Run Guide

## 1. Prerequisites

- Python 3.10 or higher

## 2. Project Structure

Below is the structure of the backend project:

```
backend/
├── data/                  # SQL scripts for database setup
│   ├── create_tables.sql  # Script to create database tables
│   ├── seed_data.sql      # Script to seed initial data (optional)
├── pydantic_models.py     # Pydantic models for request/response validation
├── db_service.py          # Database service for interacting with Supabase
├── llm_provider.py        # Logic for interacting with the LLM (e.g., OpenAI)
├── prompts.py             # Prompt templates for LLM interactions
├── settings.py            # Configuration settings (API keys, constants, etc.)
├── user_api.py            # Main FastAPI application
└── requirements.txt       # Python dependencies
```

## 3. Environment Setup

### Step 1: Clone the Repository

Clone the repository to your local machine:

```sh
git clone <YOUR_REPOSITORY_URL>
cd my-nutri-journey-main/backend
```

### Step 2: Install Dependencies

Install the required Python dependencies:

```sh
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the `backend` directory by copying the `.env.example` file:

```sh
cp .env.example .env
```

Edit the `.env` file and replace the placeholder values (`...`) with your actual API keys and other configuration values.

Example `.env` file:
```env
OPENAI_API_KEY=your-openai-api-key
SUPABASE_KEY=your-supabase-key
```

## 4. Initialize the Supabase Database

Run `create_tables.sql` and `populate_tables.sql` in Supabase SQL console

## 5. Running the Backend API

Start the FastAPI server using the following command:

```sh
uvicorn user_api:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## 6. Explanation of `settings.py`

The `settings.py` file contains configuration constants and environment variables used throughout the project. Key settings include:

- **OPENAI_MODEL**: The OpenAI model to use for LLM interactions.
- **LLM_PROVIDER**: The provider for LLM services (e.g., OpenAI).
- **OPENAI_KEY**: API key for OpenAI.
- **TEMP_UPLOAD_DIR**: Directory for temporarily storing uploaded files.
- **NUM_RECOMMENDATION_DAYS**: Number of days for meal recommendations.
- **BUCKET_NAME**: Name of the Supabase storage bucket.

Make sure to update the `.env` file with the correct values for these settings.

## 8. Troubleshooting

- Ensure all dependencies are installed correctly.
- Verify that the `.env` file contains valid API keys and configuration values.
- Check the terminal for error logs if the server fails to start.

For further assistance, refer to the codebase or contact the project maintainers.