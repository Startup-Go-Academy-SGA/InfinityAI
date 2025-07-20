import React from 'react';

const macroEmojis: Record<string, string> = {
  calories: '🔥',
  protein: '🥚',  
  fats: '🧈',
  saturated_fats: '🧀',
  fibers: '🥦',
  carbs: '🥔',
};

const macroLabels: Record<string, string> = {
  calories: 'Calories',
  protein: 'Protein',
  fat: 'Fats',
  saturated_fats: 'Sat.Fats',
  fibers: 'Fibers',
  carbs: 'Carbs',
};

// Function to determine health score color
const getHealthScoreColor = (score: number) => {
  if (score >= 8.5) return "from-green-100 to-green-50 border-green-200 text-green-600";
  if (score >= 7) return "from-emerald-100 to-emerald-50 border-emerald-200 text-emerald-600";
  if (score >= 5.5) return "from-yellow-100 to-yellow-50 border-yellow-200 text-yellow-600";
  if (score >= 4) return "from-orange-100 to-orange-50 border-orange-200 text-orange-600";
  return "from-red-100 to-red-50 border-red-200 text-red-600";
};

// Function to get health score description
const getHealthScoreDescription = (score: number) => {
  if (score >= 8.5) return "Excellent nutritional quality";
  if (score >= 7) return "Very good nutritional quality";
  if (score >= 5.5) return "Average nutritional quality";
  if (score >= 4) return "Below average nutritional quality";
  return "Poor nutritional quality";
};

function capitalizeFirst(str: string) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

const MealAnalysis = ({ analysis, imageUrl }) => {
  if (!analysis) return null;
  const { dish_name, macronutrients, ingredients, health_score, health_benefits, health_explanation } = analysis;
  const healthScore = health_score || 0;
  const healthScoreColor = getHealthScoreColor(healthScore);
  const healthScoreDescription = health_explanation || getHealthScoreDescription(healthScore);
  const benefits = health_benefits || [];

  return (
    <div className="rounded-xl shadow-lg bg-white p-6 mb-6">
      <div className="flex flex-col md:flex-row items-start gap-6 mb-4">
        {imageUrl && (
          <img
            src={imageUrl}
            alt={dish_name}
            className="w-56 h-56 object-cover rounded-lg border"
          />
        )}
        <div className="flex flex-col justify-start w-full">
          <h2 className="text-2xl font-bold mb-2">{dish_name}</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            {Object.entries(macronutrients).map(([key, value]) => (
              <span
                key={key}
                className="inline-block px-3 py-1 rounded-full text-sm font-semibold bg-gray-100 text-gray-800"
              >
                {macroEmojis[key] || ''} {macroLabels[key] || key.charAt(0).toUpperCase() + key.slice(1)}: <span className="font-bold">{String(value)}</span>
                {key !== "calories" && "g"}
              </span>
            ))}
          </div>
          
          {/* Health Score Card - Moved here to show on left under macronutrients */}
          <div className={`p-4 rounded-lg border bg-gradient-to-r ${healthScoreColor}`}>
            <div className="flex justify-between items-center">
              <div>
                <h3 className={`text-md font-semibold mb-1 ${healthScoreColor.split(' ')[2].replace('border-', 'text-').replace('200', '800')}`}>
                  Health Score
                </h3>
                <p className={`${healthScoreColor} text-sm`}>{healthScoreDescription}</p>
              </div>
              <div className="text-right">
                <div className={`text-3xl font-bold ${healthScoreColor}`}>{healthScore.toFixed(1)}</div>
                <div className={`${healthScoreColor} text-xs`}>/10</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Ingredients List */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">Ingredients</h3>
        <ul className="space-y-2">
          {ingredients.map((ing, idx) => {
            const name = capitalizeFirst(ing.name || ing.food || '');
            const portions = ing.portions || ing.portion_count || 1;
            const grams = ing.grams || 0;
            
            return (
              <li key={idx} className="flex items-start gap-2">
                <div className="mt-1.5 w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                <span>
                  {portions} {name} ({grams}g)
                </span>
              </li>
            );
          })}
        </ul>
      </div>
      
      {/* Health Benefits */}
      {benefits.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">Health Benefits</h3>
          <ul className="space-y-2">
            {benefits.map((benefit, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <div className="mt-1.5 w-2 h-2 rounded-full bg-green-500 flex-shrink-0"></div>
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MealAnalysis;