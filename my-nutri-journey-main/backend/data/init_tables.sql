-- Create all required tables for My Nutri Journey app
-- Run this in the Supabase SQL Editor

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT,
    birthdate TEXT,
    weight INTEGER,
    height INTEGER,
    country TEXT,
    "targetWeight" INTEGER,
    "activityLevel" TEXT,
    allergies TEXT,
    dislikes TEXT,
    "favoriteFoods" TEXT,
    "nutritionGoal" TEXT,
    "userProfile" TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    daily_target_calories INTEGER,
    daily_target_carbs INTEGER,
    daily_target_protein INTEGER,
    daily_target_fats INTEGER,
    num_meals_per_day INTEGER DEFAULT 3,
    gender TEXT DEFAULT 'other'
);

-- 2. Meals Table - Fix the syntax error (extra comma)
CREATE TABLE IF NOT EXISTS meals (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INTEGER,
    meal_type TEXT,
    consumed_date TEXT NOT NULL,
    meal_json JSONB,
    uploaded_at TEXT
);

-- 3. Recommended Meals Table
CREATE TABLE IF NOT EXISTS recommended_meals (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INTEGER NOT NULL,
    planned_date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    meal_json JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraints (optional but recommended)
ALTER TABLE meals 
ADD CONSTRAINT fk_meals_user 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE;

ALTER TABLE recommended_meals 
ADD CONSTRAINT fk_recommended_meals_user 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE;

-- Add indexes for performance (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_meals_user_id ON meals(user_id);
CREATE INDEX IF NOT EXISTS idx_recommended_meals_user_id ON recommended_meals(user_id);
CREATE INDEX IF NOT EXISTS idx_recommended_meals_planned_date ON recommended_meals(planned_date);