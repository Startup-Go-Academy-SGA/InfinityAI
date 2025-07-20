import React, { useState, useEffect } from 'react';
import { ArrowLeft, TrendingUp, Calendar, Utensils, PieChart as PieChartIcon, Activity } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Helper function to format date range display
const getDateRangeDisplay = (timeframe) => {
  const today = new Date();
  const endDateStr = today.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  
  let startDate;
  if (timeframe === 'week') {
    startDate = new Date(today);
    startDate.setDate(today.getDate() - 7);
  } else if (timeframe === 'month') {
    startDate = new Date(today);
    startDate.setDate(today.getDate() - 30);
  } else if (timeframe === 'quarter') {
    startDate = new Date(today);
    startDate.setDate(today.getDate() - 90);
  } else if (timeframe === 'overall') {
    return "All Time";
  }
  
  const startDateStr = startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return `${startDateStr} - ${endDateStr}`;
};

// Custom tooltip formatter for macronutrients
const MacroTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border rounded shadow-md">
        <p className="font-medium mb-1">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span>{entry.name}: {entry.value}g</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const ProgressAnalytics = ({ onBack }) => {
  const [timeframe, setTimeframe] = useState('week');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userId, setUserId] = useState(null);
  const dateRangeDisplay = getDateRangeDisplay(timeframe);

  // Fetch user ID from localStorage
  useEffect(() => {
    const storedUserId = localStorage.getItem('userId') || localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(storedUserId);
    }
  }, []);

  // Fetch analytics data based on selected timeframe and userId
  useEffect(() => {
    if (!userId) return;

    const fetchAnalytics = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE_URL}/api/analytics?user_id=${userId}&timeframe=${timeframe}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        let data = await response.json();
        
        // Fix days tracked calculation if needed
        if (data.daily_stats && data.daily_stats.length > 0) {
          // Count unique dates that have data, regardless of meals array
          const uniqueDatesWithData = new Set(
            data.daily_stats
              .filter(day => {
                // Consider a day valid if it has meals OR it has calories/macros directly
                return (day.meals && day.meals.length > 0) || 
                       day.calories > 0 || 
                       day.protein > 0 || 
                       day.carbs > 0 || 
                       day.fats > 0;
              })
              .map(day => day.date)
          );
          
          // Update the summary with the correct days tracked count
          data.summary.days_tracked = uniqueDatesWithData.size;
          console.log("Unique dates with data:", [...uniqueDatesWithData]); // Debug output
        }
        
        // Process daily stats to extract data from meal_json field if needed
        if (data.daily_stats) {
          data.daily_stats = data.daily_stats.map(stat => {
            try {
              // Create a date object from the date string
              const dateObj = new Date(stat.date);
              // Format as "MMM d" (e.g., "Jan 5")
              const formattedDate = dateObj.toLocaleDateString('en-US', { 
                month: 'short',
                day: 'numeric'
              });
              
              // Extract data from meal_json field if it exists
              let calories = 0, protein = 0, carbs = 0, fats = 0, health_score = 0;
              
              // If stat.meals exists and is an array of meals
              if (stat.meals && Array.isArray(stat.meals)) {
                // Calculate averages from all meals for the day
                let mealCount = stat.meals.length;
                let totalHealthScore = 0;
                
                stat.meals.forEach(meal => {
                  const mealJson = meal.meal_json || {};
                  const macros = mealJson.macronutrients || {};
                  
                  // Add up macros
                  calories += macros.calories || 0;
                  protein += macros.protein || macros.proteins || 0;  // Check both for compatibility
                  carbs += macros.carbs || 0;
                  fats += macros.fats || macros.fat || 0;
                  
                  // Add health score to total
                  totalHealthScore += mealJson.health_score || 0;
                });
                
                // Calculate average health score
                health_score = mealCount > 0 ? totalHealthScore / mealCount : 0;
              } else {
                // Use the legacy data structure if meal_json is not available
                calories = stat.calories || 0;
                protein = stat.protein || 0;
                carbs = stat.carbs || 0;
                fats = stat.fats || 0;
                health_score = stat.health_score || 0;
              }
              
              return {
                ...stat,
                display_date: formattedDate,
                calories: calories,
                protein: protein,  // Changed from "proteins" to "protein"
                carbs: carbs,
                fats: fats,
                health_score: health_score
              };
            } catch (e) {
              console.error(`Error processing stat for date ${stat.date}:`, e);
              // Return a fallback object with the original date if parsing fails
              return {
                ...stat,
                display_date: stat.date,
                calories: 0,
                protein: 0,
                carbs: 0,
                fats: 0,
                health_score: 0
              };
            }
          });
        }
        
        // Format frequent foods for histogram display (limit to 10 items)
        if (data.frequent_foods) {
          // Limit to 10 items
          data.frequent_foods = data.frequent_foods.slice(0, 10);
          
          // Format for histogram
          data.frequent_foods = data.frequent_foods.map(food => ({
            name: food.name,
            count: food.count
          }));
        }
        
        // Add after receiving the data but before updating state
        // Ensure we have entries for all days in the selected timeframe
        if (data.daily_stats) {
          // Generate a complete array of dates for the selected timeframe
          const today = new Date();
          const dates = [];
          let daysToInclude = 7;
          let startFromDate = null;
          
          if (timeframe === 'week') {
            daysToInclude = 7;
          } else if (timeframe === 'month') {
            daysToInclude = 30;
          } else if (timeframe === 'quarter') {
            daysToInclude = 90;
          } else if (timeframe === 'overall') {
            // For "overall", find the oldest meal date and use that
            if (data.daily_stats.length > 0) {
              // Sort dates to find the oldest one with data
              const datesWithData = data.daily_stats
                .filter(day => (day.meals && day.meals.length > 0) || 
                        day.calories > 0 || day.protein > 0 || day.carbs > 0 || day.fats > 0)
                .map(day => new Date(day.date).getTime());
              
              if (datesWithData.length > 0) {
                // Find oldest date with data
                const oldestTimestamp = Math.min(...datesWithData);
                startFromDate = new Date(oldestTimestamp);
                
                // Calculate days to include from oldest date to today
                const diffTime = today.getTime() - startFromDate.getTime();
                daysToInclude = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
              } else {
                // If no dates with data, just show the last 30 days
                daysToInclude = 30;
              }
            } else {
              // If no daily stats, just show the last 30 days
              daysToInclude = 30;
            }
          }
          
          // Create a map of existing stats by date
          const statsMap = {};
          data.daily_stats.forEach(stat => {
            statsMap[stat.date] = stat;
          });
          
          // Generate entries for all days in the timeframe
          if (daysToInclude > 0) {
            const completeStats = [];
            
            for (let i = 0; i < daysToInclude; i++) {
              // If startFromDate is set (for overall view), start from that date
              // Otherwise, count back from today
              let date;
              if (timeframe === 'overall' && startFromDate) {
                date = new Date(startFromDate);
                date.setDate(startFromDate.getDate() + i);
                
                // Don't go beyond today
                if (date > today) break;
              } else {
                date = new Date(today);
                date.setDate(today.getDate() - (daysToInclude - 1 - i));
              }
              
              const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
              
              // Format for display
              const formattedDate = date.toLocaleDateString('en-US', { 
                month: 'short',
                day: 'numeric'
              });
              
              if (statsMap[dateStr]) {
                // We have data for this date
                statsMap[dateStr].display_date = formattedDate;
                completeStats.push(statsMap[dateStr]);
              } else {
                // Create an empty entry for this date
                completeStats.push({
                  date: dateStr,
                  display_date: formattedDate,
                  calories: 0,
                  protein: 0,
                  carbs: 0,
                  fats: 0,
                  health_score: 0,
                  meals: []
                });
              }
            }
            
            // Sort by date (oldest to newest)
            completeStats.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
            data.daily_stats = completeStats;
          }
        }
        
        setAnalyticsData(data);
      } catch (err) {
        console.error("Error fetching analytics:", err);
        setError("Failed to load analytics data. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [userId, timeframe]);

  // Helper function to get appropriate color for health score
  const getHealthScoreColor = (score) => {
    if (score >= 8.5) return 'bg-green-500';
    if (score >= 7) return 'bg-emerald-500';
    if (score >= 5.5) return 'bg-yellow-500';
    if (score >= 4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  // If loading or error, show appropriate message
  if (isLoading) {
    return (
      <div className="p-4 max-w-4xl mx-auto text-center py-20">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
        <p className="mt-4 text-gray-600">Loading your nutrition analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 max-w-4xl mx-auto text-center py-20">
        <div className="bg-red-50 p-6 rounded-lg border border-red-200">
          <h3 className="text-red-700 font-medium text-lg mb-2">Error Loading Data</h3>
          <p className="text-red-600">{error}</p>
          <Button 
            variant="outline" 
            onClick={() => window.location.reload()}
            className="mt-4"
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // If no data is available yet
  if (!analyticsData || !analyticsData.daily_stats || analyticsData.daily_stats.length === 0) {
    return (
      <div className="p-4 max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={onBack}
            className="rounded-full"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-800">Progress & Analytics</h1>
            <p className="text-gray-600">Track your nutrition journey</p>
          </div>
        </div>
        
        <Card className="mb-6 p-8 text-center">
          <CardContent>
            <h3 className="text-lg font-medium mb-2">No data available yet</h3>
            <p className="text-gray-600 mb-4">
              Start logging your meals to see nutrition analytics.
            </p>
            <Button onClick={onBack}>Go Back</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Extract data from the API response
  const { summary, daily_stats, macro_distribution } = analyticsData;

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={onBack}
          className="rounded-full"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-800">Progress & Analytics</h1>
          <p className="text-gray-600">Track your nutrition journey</p>
        </div>
      </div>

      {/* Time Filter */}
      <div className="flex flex-col gap-2 mb-6">
        <div className="flex flex-wrap gap-2">
          {['week', 'month', 'quarter', 'overall'].map((period) => (
            <Button
              key={period}
              variant={timeframe === period ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTimeframe(period)}
              className="capitalize"
            >
              {period}
            </Button>
          ))}
        </div>
        <div className="text-sm text-gray-500 ml-1">
          {dateRangeDisplay}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card className="bg-gradient-to-r from-green-100 to-green-50">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{summary.days_tracked}</div>
            <div className="text-sm text-gray-600">Days Tracked</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-r from-blue-100 to-blue-50">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{summary.avg_calories}</div>
            <div className="text-sm text-gray-600">Avg Calories</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-r from-orange-100 to-orange-50">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">
              {summary.avg_health_score ? summary.avg_health_score.toFixed(1) : "0.0"}
            </div>
            <div className="text-sm text-gray-600">Avg Health Score</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-r from-purple-100 to-purple-50">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">{summary.total_meals}</div>
            <div className="text-sm text-gray-600">Meals Logged</div>
          </CardContent>
        </Card>
      </div>

      {/* Calorie Trend Chart */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Daily Calorie Intake
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={daily_stats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="display_date" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value} calories`, 'Calories']} />
              <Line 
                type="monotone" 
                dataKey="calories" 
                stroke="#16A34A" 
                strokeWidth={3}
                dot={{ fill: '#16A34A', strokeWidth: 2, r: 4 }}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Daily Macronutrients Chart - As Line Chart */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            Daily Macronutrients
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={daily_stats}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="display_date" />
              <YAxis unit="g" />
              <Tooltip content={MacroTooltip} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="protein"  // Changed from "proteins" to "protein"
                name="Protein" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6', r: 3 }}
              />
              <Line 
                type="monotone" 
                dataKey="carbs" 
                name="Carbs" 
                stroke="#F97316" 
                strokeWidth={2}
                dot={{ fill: '#F97316', r: 3 }}
              />
              <Line 
                type="monotone" 
                dataKey="fats" 
                name="Fats" 
                stroke="#8B5CF6" 
                strokeWidth={2}
                dot={{ fill: '#8B5CF6', r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Macro Distribution and Health Score Trend */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChartIcon className="h-5 w-5" />
              Macronutrient Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={macro_distribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {macro_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Health Score Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="display_date" />
                <YAxis domain={[0, 10]} />
                <Tooltip formatter={(value) => [`${value}/10`, 'Health Score']} />
                <Line 
                  type="monotone" 
                  dataKey="health_score"
                  name="Health Score"
                  stroke="#DC2626" /* Changed to red */
                  strokeWidth={3}
                  dot={{ fill: '#DC2626', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProgressAnalytics;
