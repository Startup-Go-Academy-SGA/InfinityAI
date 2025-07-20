import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const macroEmojis = {
  calories: '🔥',
  protein: '🥚',  // Changed from "proteins" to "protein"
  fats: '🧈',
  fat: '🧈',
  saturated_fats: '🧀',
  fibers: '🥦',
  fiber: '🥦',
  carbs: '🥔',
};

const macroLabels = {
  calories: 'Calories',
  protein: 'Protein',  // Changed from "proteins" to "protein"
  fats: 'Fat',
  fat: 'Fat',
  saturated_fats: 'Sat.Fat',
  'sat.fat': 'Sat.Fat',
  fibers: 'Fiber',
  fiber: 'Fiber',
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

const LoggedMeals = ({ meals, isToday, onMealClick }) => (
  <div>
    {meals && meals.length > 0 ? (
      <div className="space-y-3">
        {meals.map((meal) => {
          // Get data from meal_json structure
          const mealJson = meal.meal_json || {};
          const macros = mealJson.macronutrients || {};
          const dishName = mealJson.dish_name || meal.name || "Meal";
          
          // Get image URL from meal_json
          const imageUrl = mealJson.img_path || '';
          
          // Get meal type and style
          const mealType = meal.meal_type || meal.type || 'other';
          const mealBorderClass = mealTypeBorders[mealType.toLowerCase()] || 'border-gray-400';
          
          // Get health score from meal_json
          const healthScore = mealJson.health_score || 0;
          const healthScoreColor = getHealthScoreColor(healthScore);

          return (
            <Card 
              key={meal.id} 
              className={`border-l-4 ${mealBorderClass} cursor-pointer transition-all duration-200 hover:shadow-md`}
              onClick={() => onMealClick(meal)}
            >
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div className="flex gap-4 items-start">
                    {imageUrl && (
                      <img
                        src={imageUrl}
                        alt={dishName}
                        className="w-16 h-16 object-cover rounded-lg border"
                      />
                    )}
                    <div className="flex flex-col gap-1">
                      <h3 className="font-medium text-lg">{dishName}</h3>
                      <div className="flex flex-wrap gap-2">
                        {["calories", "protein", "carbs", "fats"].map((key) => {  // Changed from "proteins" to "protein"
                          // Check for alternate names too (fat/fats)
                          let value = macros[key];
                          
                          // Handle different naming conventions
                          if (value === undefined || value === null) {
                            if (key === "fats") value = macros["fat"];
                          }
                          
                          if (value === undefined || value === null) return null;
                          
                          return (
                            <span
                              key={key}
                              className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800"
                            >
                              {macroEmojis[key] || ''} {macroLabels[key] || key}:{" "}
                              <span className="font-bold">
                                {String(value)}
                              </span>
                              {key !== "calories" && "g"}
                            </span>
                          );
                        })}
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
    ) : (
      <Card className="border-dashed border-2 border-gray-300">
        <CardContent className="p-8 text-center">
          <p className="text-gray-500 mb-4">
            {isToday ? 'No meals logged yet today' : 'No meals logged for this day'}
          </p>
        </CardContent>
      </Card>
    )}
  </div>
);

export default LoggedMeals;
