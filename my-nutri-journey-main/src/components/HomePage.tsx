import React, { useEffect, useState } from 'react';
import { Calendar, User, TrendingUp, MessageCircle, Plus, ShoppingCart, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';
import LoggedMeals from './LoggedMeals';
import RecommendedMeals from './RecommendedMeals';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const HomePage = ({ onMealClick, onViewChange }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [loggedMeals, setLoggedMeals] = useState([]);
  const [userId, setUserId] = useState<string | null>(null);
  const [userProfile, setUserProfile] = useState(null);
  const [dailyNutrients, setDailyNutrients] = useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fats: 0
  });
  const [recommendedMeals, setRecommendedMeals] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  const navigate = useNavigate();

  // Fetch user ID from localStorage
  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    setUserId(storedUserId);
  }, []);

  // Fetch user profile for target nutrients
  useEffect(() => {
    if (!userId) return;
    
    const fetchUserProfile = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/users/${userId}`);
        if (res.ok) {
          const data = await res.json();
          setUserProfile(data);
        }
      } catch (error) {
        console.error("Error fetching user profile:", error);
      }
    };
    
    fetchUserProfile();
  }, [userId]);

  // Fetch meals for selected date
  useEffect(() => {
    if (!userId || !selectedDate) return;
    
    const fetchMeals = async () => {
      // Fix: Format date directly without timezone conversion
      // This ensures we get the exact date shown in the UI
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      
      console.log(`Fetching meals for date: ${dateStr}`);
      try {
        const res = await fetch(`${API_BASE_URL}/api/meals?user_id=${userId}&date=${dateStr}`);
        if (res.ok) {
          const data = await res.json();
          console.log(`Received ${data.length} meals for ${dateStr}`);
          setLoggedMeals(data.map(m => ({
            id: m.id,
            type: m.meal_type,
            name: m.meal_json.dish_name || 'Meal',
            calories: m.meal_json.macronutrients?.calories || 0,
            protein: m.meal_json.macronutrients?.protein || 0,
            carbs: m.meal_json.macronutrients?.carbs || 0,
            fats: m.meal_json.macronutrients?.fats || m.meal_json.macronutrients?.fat || 0,
            time: m.uploaded_at ? new Date(m.uploaded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
            meal_json: m.meal_json
          })));
        }
      } catch (error) {
        console.error("Error fetching meals:", error);
      }
    };
    
    fetchMeals();
  }, [userId, selectedDate]);

  // Fetch recommended meals for selected date
  useEffect(() => {
    if (!userId || !selectedDate) return;

    const fetchRecommendedMeals = async () => {
      setLoadingRecommendations(true);
      
      // Fix: Format date directly without timezone conversion
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      
      console.log(`Fetching recommended meals for date: ${dateStr}`);
      try {
        const res = await fetch(`${API_BASE_URL}/api/recommended-meals`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, date: dateStr }),
        });
        if (res.ok) {
          const data = await res.json();
          console.log(`Received ${data.length} recommended meals for ${dateStr}`);
          setRecommendedMeals(data);
        } else {
          setRecommendedMeals([]);
        }
      } catch (error) {
        console.error("Error fetching recommended meals:", error);
        setRecommendedMeals([]);
      } finally {
        setLoadingRecommendations(false);
      }
    };

    fetchRecommendedMeals();
  }, [userId, selectedDate]);

  // Calculate daily nutrients from logged meals
  useEffect(() => {
    if (!loggedMeals.length) {
      setDailyNutrients({
        calories: 0,
        protein: 0,
        carbs: 0,
        fats: 0
      });
      return;
    }

    const totals = loggedMeals.reduce((acc, meal) => {
      return {
        calories: acc.calories + (meal.calories || 0),
        protein: acc.protein + (meal.protein || 0),
        carbs: acc.carbs + (meal.carbs || 0),
        fats: acc.fats + (meal.fats || 0)
      };
    }, {
      calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0
    });

    // Round to 1 decimal place
    for (const key in totals) {
      totals[key] = Math.round(totals[key] * 10) / 10;
    }

    setDailyNutrients(totals);
  }, [loggedMeals]);

  // Get daily targets from user profile or use fallbacks
  const getDailyTargets = () => {
    if (!userProfile) {
      return {
        calories: { current: 0, target: 2000 },
        protein: { current: 0, target: 150 },
        carbs: { current: 0, target: 250 },
        fats: { current: 0, target: 67 }
      };
    }

    return {
      calories: { 
        current: dailyNutrients.calories, 
        target: userProfile.daily_target_calories || 2000 
      },
      protein: { 
        current: dailyNutrients.protein, 
        target: userProfile.daily_target_protein || 150 
      },
      carbs: { 
        current: dailyNutrients.carbs, 
        target: userProfile.daily_target_carbs || 250 
      },
      fats: { 
        current: dailyNutrients.fats, 
        target: userProfile.daily_target_fats || 67 
      }
    };
  };

  const dailyTargets = getDailyTargets();

  const isToday = selectedDate.toDateString() === new Date().toDateString();

  const goToPreviousDay = () => {
    const previousDay = new Date(selectedDate);
    previousDay.setDate(selectedDate.getDate() - 1);
    setSelectedDate(previousDay);
  };

  const goToNextDay = () => {
    const nextDay = new Date(selectedDate);
    nextDay.setDate(selectedDate.getDate() + 1);
    setSelectedDate(nextDay);
  };

  const handleDateSelect = (date) => {
    if (date) {
      setSelectedDate(date);
    }
  };

  // Calculate percentage safely (avoid division by zero)
  const calculatePercentage = (current, target) => {
    if (!target || target === 0) return 0;
    return Math.min(Math.round((current / target) * 100), 100);
  };

  // Handle logged meal click
  const handleLoggedMealClick = (meal) => {
    navigate(`/meal/${meal.id}`, { state: { meal } });
  };

  function goToToday() {
    setSelectedDate(new Date());
  }

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            {isToday ? 'Good Morning!' : format(selectedDate, 'EEEE, MMM d')}
          </h1>
          <p className="text-gray-600">
            {isToday ? "Let's make today nutritious" : 'Your nutrition overview'}
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onViewChange('profile')}
          className="rounded-full"
        >
          <User className="h-6 w-6" />
        </Button>
      </div>

      {/* Date Navigation */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="outline"
          size="icon"
          onClick={goToPreviousDay}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        
        <div className="flex items-center gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-[200px] justify-center">
                <Calendar className="h-4 w-4 mr-2" />
                {format(selectedDate, 'MMM d, yyyy')}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="center">
              <CalendarComponent
                mode="single"
                selected={selectedDate}
                onSelect={handleDateSelect}
                initialFocus
                className="p-3 pointer-events-auto"
                disabled={(date) => date > new Date()}
              />
            </PopoverContent>
          </Popover>
          
          {!isToday && (
            <Button variant="outline" size="sm" onClick={goToToday}>
              Today
            </Button>
          )}
        </div>

        <Button
          variant="outline"
          size="icon"
          onClick={goToNextDay}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Daily Overview Card */}
      <Card className="mb-6 bg-gradient-to-r from-green-100 to-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-green-600" />
            {isToday ? "Today's Overview" : `${format(selectedDate, 'MMM d')} Overview`}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {dailyTargets.calories.current}
              </div>
              <div className="text-sm text-gray-600">
                / {dailyTargets.calories.target} cal
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {dailyTargets.protein.current}
              </div>
              <div className="text-sm text-gray-600">
                / {dailyTargets.protein.target}g protein
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {dailyTargets.carbs.current}
              </div>
              <div className="text-sm text-gray-600">
                / {dailyTargets.carbs.target}g carbs
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {dailyTargets.fats.current}
              </div>
              <div className="text-sm text-gray-600">
                / {dailyTargets.fats.target}g fats
              </div>
            </div>
          </div>
          
          {/* Progress Bars */}
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-green-700 font-medium">Calories</span>
                <span>{calculatePercentage(dailyTargets.calories.current, dailyTargets.calories.target)}%</span>
              </div>
              <Progress 
                value={calculatePercentage(dailyTargets.calories.current, dailyTargets.calories.target)} 
                className="h-2 [&>div]:bg-green-500"
              />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-blue-700 font-medium">Protein</span>
                <span>{calculatePercentage(dailyTargets.protein.current, dailyTargets.protein.target)}%</span>
              </div>
              <Progress 
                value={calculatePercentage(dailyTargets.protein.current, dailyTargets.protein.target)} 
                className="h-2 [&>div]:bg-blue-500"
              />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-orange-700 font-medium">Carbs</span>
                <span>{calculatePercentage(dailyTargets.carbs.current, dailyTargets.carbs.target)}%</span>
              </div>
              <Progress 
                value={calculatePercentage(dailyTargets.carbs.current, dailyTargets.carbs.target)} 
                className="h-2 [&>div]:bg-orange-500"
              />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-purple-700 font-medium">Fats</span>
                <span>{calculatePercentage(dailyTargets.fats.current, dailyTargets.fats.target)}%</span>
              </div>
              <Progress 
                value={calculatePercentage(dailyTargets.fats.current, dailyTargets.fats.target)} 
                className="h-2 [&>div]:bg-purple-500"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommended Meals */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            Today's Suggested Meals
          </h2>
          {isToday && (
            <Button 
              variant="outline" 
              size="sm"
              className="text-green-600 border-green-300 hover:bg-green-50"
            >
              <ShoppingCart className="h-4 w-4 mr-2" />
              Buy All
            </Button>
          )}
        </div>
        <div className="space-y-4">
          <RecommendedMeals
            meals={recommendedMeals}
            loading={loadingRecommendations}
            onMealClick={(meal) => navigate('/meal/' + meal.id, { state: { meal } })}
          />
        </div>
      </div>

      {/* Logged Meals */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            {isToday ? "Today's Logged Meals" : 'Logged Meals'}
          </h2>
          {isToday && (
            <Button
              onClick={() => onViewChange('meal-upload')}
              size="sm"
              className="bg-green-600 hover:bg-green-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Log Meal
            </Button>
          )}
        </div>
        <LoggedMeals
          meals={loggedMeals}  // Changed from loggedMeals to meals to match the component props
          isToday={isToday}
          onMealClick={(meal) => navigate('/meal/' + meal.id, { state: { meal } })}
        />
      </div>

      {/* Quick Actions */}
      {isToday && (
        <div className="grid grid-cols-2 gap-4">
          <Button
            variant="outline"
            className="h-16 flex-col gap-2"
            onClick={() => onViewChange('chatbot')}
          >
            <MessageCircle className="h-5 w-5" />
            Nutrition Expert
          </Button>
          <Button
            variant="outline"
            className="h-16 flex-col gap-2"
            onClick={() => onViewChange('progress')}
          >
            <TrendingUp className="h-5 w-5" />
            View Progress
          </Button>
        </div>
      )}
    </div>
  );
};

export default HomePage;