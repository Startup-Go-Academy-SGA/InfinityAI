import React from 'react';
import { ShoppingCart, Play, BookOpen, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Ingredient {
  name: string;
  quantity?: string;
  amount?: string | number;
  unit?: string;
  food?: string;
  grams?: number;
  portions?: number;
  portion_count?: number;
}

interface Restaurant {
  name: string;
  rating: number;
  reviewCount: number;
  price: number;
}

interface MealOverviewProps {
  ingredients: string[] | Ingredient[];
  healthBenefits?: string[];
  estimatedPrice?: number;
  restaurants?: Restaurant[];
  hasVideo?: boolean;
  hasRecipe?: boolean;
  showIngredients?: boolean;
  showHealthBenefits?: boolean;
}

// Helper function to capitalize first letter of string
function capitalizeFirst(str: string) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

const MealOverview: React.FC<MealOverviewProps> = ({
  ingredients,
  healthBenefits = [],
  estimatedPrice = 12.5,
  restaurants = [],
  hasVideo = true,
  hasRecipe = true,
  showIngredients = false,
  showHealthBenefits = false,
}) => {
  // Default restaurants if none provided
  const defaultRestaurants: Restaurant[] = [
    {
      name: 'Green Garden Cafe',
      rating: 4.8,
      reviewCount: 124,
      price: 15.99,
    },
    {
      name: 'Healthy Bites',
      rating: 4.2,
      reviewCount: 87,
      price: 13.5,
    },
  ];

  const displayRestaurants = restaurants.length > 0 ? restaurants : defaultRestaurants;

  return (
    <div className="space-y-6">
      {/* Ingredients - only show if showIngredients is true */}
      {showIngredients && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Ingredients</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {ingredients.map((ing, index) => {
                if (typeof ing === 'string') {
                  return (
                    <li key={index} className="flex items-center gap-3 py-2">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
                      <span className="text-gray-700">1 x {ing}</span>
                    </li>
                  );
                }
                const name = capitalizeFirst(ing.name || ing.food || '');
                const qty = ing.portions ?? ing.portion_count ?? ing.amount ?? 1;
                const prefix = `${qty} x `;
                return (
                  <li key={index} className="flex items-center gap-3 py-2">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
                    <span className="text-gray-700">{prefix}{name}</span>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Health Benefits - only show if showHealthBenefits is true */}
      {showHealthBenefits && healthBenefits.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Health Benefits</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {healthBenefits.map((benefit, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-gray-700">{benefit}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="space-y-4">
        <Button className="w-full h-14 bg-green-600 hover:bg-green-700 text-lg font-medium">
          <ShoppingCart className="h-5 w-5 mr-3" />
          Buy Ingredients (${estimatedPrice.toFixed(2)})
        </Button>
        
        <div className="grid grid-cols-2 gap-4">
          {hasRecipe && (
            <Button variant="outline" className="h-12">
              <BookOpen className="h-4 w-4 mr-2" />
              View Recipe
            </Button>
          )}
          {hasVideo && (
            <Button variant="outline" className="h-12">
              <Play className="h-4 w-4 mr-2" />
              Watch Video
            </Button>
          )}
        </div>

        {/* Restaurant Options */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">Order from Local Restaurants</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {displayRestaurants.map((restaurant, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-medium">{restaurant.name}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star 
                          key={i} 
                          className={`h-4 w-4 ${i < Math.floor(restaurant.rating) 
                            ? "fill-yellow-400 text-yellow-400" 
                            : "text-gray-300"}`} 
                        />
                      ))}
                    </div>
                    <span className="text-sm text-gray-600">
                      {restaurant.rating} ({restaurant.reviewCount} reviews)
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-green-600">${restaurant.price.toFixed(2)}</div>
                  <Button size="sm" className="mt-2">Order</Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MealOverview;