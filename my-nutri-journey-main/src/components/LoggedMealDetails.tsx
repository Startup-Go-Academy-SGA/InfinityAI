import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog';
import { toast } from '@/hooks/use-toast';
import MealAnalysis from './MealAnalysis';
import MealOverview from './MealOverview';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const LoggedMealDetails = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { meal } = location.state || {};
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  if (!meal) {
    // If no meal data is available, redirect back to home
    navigate('/');
    return null;
  }

  const mealJson = meal.meal_json || {};
  
  // Create analysis object with all available data from meal_json
  const analysis = {
    dish_name: mealJson.dish_name || meal.name,
    macronutrients: mealJson.macronutrients || {
      calories: meal.calories || 0,
      protein: meal.protein || 0,
      fats: meal.fats || 0,
      carbs: meal.carbs || 0
    },
    ingredients: mealJson.ingredients || [],
    health_score: mealJson.health_score || meal.health_score || 7,
    health_benefits: mealJson.health_benefits || [],
    health_explanation: mealJson.health_explanation || ''
  };

  // Use IMAGES_URL for meal image if available
  const imageUrl = mealJson.img_path || meal.image || '/images/meal.png';

  // Function to handle meal deletion
  const handleDeleteMeal = async () => {
    if (!meal.id) {
      toast({
        title: "Error",
        description: "Cannot delete this meal: Missing meal ID",
        variant: "destructive"
      });
      return;
    }

    setIsDeleting(true);
    
    try {
      const userId = localStorage.getItem('user_id') || localStorage.getItem('userId');
      
      // Determine if it's a recommended meal or logged meal
      const endpoint = meal.planned_date 
        ? `${API_BASE_URL}/api/recommended-meals/${meal.id}?user_id=${userId}`
        : `${API_BASE_URL}/api/meals/${meal.id}?user_id=${userId}`;
      
      const response = await fetch(
        endpoint, 
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete meal');
      }

      toast({
        title: "Success",
        description: "Meal deleted successfully"
      });
      
      // Navigate back to home page
      navigate('/');
    } catch (error) {
      console.error("Error deleting meal:", error);
      toast({
        title: "Error",
        description: typeof error === 'object' && error.message ? error.message : "Failed to delete meal. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsDeleting(false);
      setIsDeleteDialogOpen(false);
    }
  };

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto">
      {/* Header with Back and Delete buttons */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/')}
            className="rounded-full"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </div>
        
        {/* Always show delete button */}
        <Button 
          variant="outline" 
          size="sm"
          className="text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
          onClick={() => setIsDeleteDialogOpen(true)}
          disabled={isDeleting}
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Meal
        </Button>
      </div>

      {/* Meal Analysis */}
      <MealAnalysis
        analysis={analysis}
        imageUrl={imageUrl}
      />

      {/* Meal Overview - without duplicate ingredients and health benefits */}
      <div className="mt-8">
        <MealOverview 
          ingredients={analysis.ingredients}
          healthBenefits={analysis.health_benefits}
          estimatedPrice={analysis.macronutrients.calories ? analysis.macronutrients.calories / 20 : 12.99}
          showIngredients={false}
          showHealthBenefits={false}
        />
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to delete this meal?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the meal from your logs.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteMeal}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default LoggedMealDetails;