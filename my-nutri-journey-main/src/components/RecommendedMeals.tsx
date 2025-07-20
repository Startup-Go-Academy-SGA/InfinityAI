import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const macroEmojis = {
  calories: '🔥',
  protein: '🥚',
  fats: '🧈',
  carbs: '🥔',
};
const macroLabels = {
  calories: 'Calories',
  protein: 'Protein',
  fats: 'Fat',
  carbs: 'Carbs',
};

const mealTypeBorders = {
  breakfast: 'border-yellow-400',
  lunch: 'border-blue-400',
  dinner: 'border-green-400',
  snack: 'border-purple-400',
};

const getHealthScoreColor = (score) => {
  if (score >= 8.5) return "bg-green-50 text-green-700 border-green-300";
  if (score >= 7) return "bg-emerald-50 text-emerald-700 border-emerald-300";
  if (score >= 5.5) return "bg-yellow-50 text-yellow-700 border-yellow-300";
  if (score >= 4) return "bg-orange-50 text-orange-700 border-orange-300";
  return "bg-red-50 text-red-700 border-red-300";
};

const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);

const RecommendedMeals = ({ meals, loading, onMealClick }) => {
  
  const handleMealClick = (meal) => {
    // We now have a consistent structure with meal_json
    const mealJson = meal.meal_json || {};
    const dishName = mealJson.dish_name || meal.dish_name || "Meal";
    
    // Format the meal to match LoggedMealDetails expectations
    const formattedMeal = {
      id: meal.id,
      name: dishName,
      meal_type: meal.meal_type,
      // Direct reference to meal_json which now has a consistent structure
      meal_json: mealJson
    };
    
    onMealClick(formattedMeal);
  };
  
  return (
    <div>
      {loading ? (
        <Card>
          <CardContent className="p-8 text-center">
            <span className="text-gray-500">Loading recommendations...</span>
          </CardContent>
        </Card>
      ) : meals.length === 0 ? (
        <Card className="border-dashed border-2 border-gray-300">
          <CardContent className="p-8 text-center">
            <span className="text-gray-500">No recommendations for this day.</span>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {meals.map((meal) => {
            const mealJson = meal.meal_json || {};
            const macros = mealJson.macronutrients || {};
            const dishName = mealJson.dish_name || meal.dish_name || "Meal";
            
            const mealType = (meal.meal_type || '').toLowerCase();
            const mealBorderClass = mealTypeBorders[mealType] || 'border-gray-400';
            const imageUrl = mealJson.img_path || '/images/meal.png';
            
            // Get health score from meal_json
            const healthScore = mealJson.health_score || 0;
            const healthScoreColor = getHealthScoreColor(healthScore);

            return (
              <Card
                key={meal.id}
                className={`border-l-4 ${mealBorderClass} transition-all duration-200 hover:shadow-md cursor-pointer`}
                onClick={() => handleMealClick(meal)}
              >
                <CardContent className="p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex gap-4 items-start">
                      <img
                        src={imageUrl}
                        alt={dishName}
                        className="w-16 h-16 object-cover rounded-lg border"
                      />
                      <div className="flex flex-col gap-1">
                        <h3 className="font-medium text-lg">{dishName}</h3>
                        <div className="flex flex-wrap gap-2">
                          {["calories", "protein", "carbs", "fats"].map((key) => (
                            <span
                              key={key}
                              className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800"
                            >
                              {macroEmojis[key] || ''} {macroLabels[key] || key}:{" "}
                              <span className="font-bold">
                                {macros[key] !== undefined ? String(macros[key]) : "-"}
                              </span>
                              {key !== "calories" && "g"}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold border ${mealBorderClass} bg-gray-100 text-gray-800`}
                      >
                        {capitalize(mealType)}
                      </span>
                      <div className="mt-auto">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${healthScoreColor}`}
                          style={{ whiteSpace: 'nowrap' }}
                        >
                          <span role="img" aria-label="heart">❤️</span>
                          {healthScore.toFixed(1)}/10
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecommendedMeals;