-- Insert a sample user into the users table
INSERT INTO users (
    name,
    birthdate,
    weight,
    height,
    country,
    "targetWeight",
    "activityLevel",
    allergies,
    dislikes,
    "favoriteFoods",
    "nutritionGoal",
    "userProfile",
    email,
    password_hash,
    daily_target_calories,
    daily_target_carbs,
    daily_target_protein,
    daily_target_fats,
    num_meals_per_day,
    gender
) VALUES (
    'John Doe',                                 -- name
    '1990-01-15',                               -- birthdate
    80,                                         -- weight (kg)
    180,                                        -- height (cm)
    'United States',                            -- country
    75,                                         -- targetWeight (kg)
    'Athlete',                                  -- activityLevel
    'Peanuts, Shellfish',                       -- allergies
    'Brussels sprouts, Liver',                  -- dislikes
    'Chicken, Rice, Avocado, Greek yogurt',     -- favoriteFoods
    'Weight loss, Increase protein intake',     -- nutritionGoal
    '',                                         -- userProfile
    'test@example.com',                         -- email
    '$2b$12$1tCQ0uzKmuPGxEYpxT4MouMqMXW0N2Ys8JdO3o9kvdOVWMmUqQz9y',
    2200,                                       -- daily_target_calories
    225,                                        -- daily_target_carbs (g)
    150,                                        -- daily_target_protein (g)
    70,                                         -- daily_target_fats (g)
    3,                                          -- num_meals_per_day
    'Male'                                      -- gender
);