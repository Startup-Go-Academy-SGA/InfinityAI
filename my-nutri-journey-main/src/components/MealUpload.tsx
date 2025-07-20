import React, { useState, useEffect } from 'react';
import { ArrowLeft, Camera, Upload, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/hooks/use-toast';
import MealAnalysis from './MealAnalysis';
import { format } from 'date-fns';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const MealUpload = ({ onBack, selectedDate }) => {
  const [uploadMethod, setUploadMethod] = useState('photo');
  const [mealData, setMealData] = useState({
    type: '',
    name: '',
    description: '',
    photo: null,
    consumedDate: new Date() // Default to today
  });
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [dateOption, setDateOption] = useState('today'); // 'today', 'selected', 'custom'

  // Fetch userId from localStorage
  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    setUserId(storedUserId);
  }, []);

  // Update consumed date when dateOption changes
  useEffect(() => {
    if (dateOption === 'today') {
      setMealData(prev => ({ ...prev, consumedDate: new Date() }));
    } else if (dateOption === 'selected' && selectedDate) {
      setMealData(prev => ({ ...prev, consumedDate: new Date(selectedDate) }));
    }
    // For 'custom', the date is set when user selects from calendar
  }, [dateOption, selectedDate]);

  // Handle file selection
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setMealData(prev => ({
        ...prev,
        photo: file
      }));
    }
  };

  // Handle custom date selection
  const handleDateSelect = (date) => {
    setMealData(prev => ({ ...prev, consumedDate: date }));
  };

  // Handle photo analysis
  const handlePhotoAnalysis = async (e) => {
    e.preventDefault();
    if (!mealData.photo) {
      toast({ title: "No photo selected", description: "Please select a photo first." });
      return;
    }
    
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append("file", mealData.photo);
      
      if (userId) {
        formData.append("user_id", userId);
      }
      
      const res = await fetch(`${API_BASE_URL}/api/analyze-meal-image`, {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        // Handle error from the backend
        if (data.error === "No dish recognized") {
          // Switch to manual entry mode if dish not recognized
          setUploadMethod("manual");
          toast({ 
            title: "No food detected", 
            description: data.message || "Please enter the meal details manually."
          });
        } else {
          throw new Error(data.message || "Failed to analyze photo");
        }
      } else {
        // Success case
        setAnalysis(data);
        setMealData(prev => ({
          ...prev,
          name: data.dish_name || prev.name
        }));
      }
    } catch (err) {
      console.error("Analysis error:", err);
      toast({ title: "Analysis failed", description: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (uploadMethod === 'photo' && !analysis) {
      toast({ 
        title: "Analysis required", 
        description: "Please analyze the photo before submitting." 
      });
      return;
    }
    
    if (!userId || !mealData.type) {
      toast({ 
        title: "Missing data", 
        description: "Please select a meal type." 
      });
      return;
    }
    
    try {
      // For photo method, use the analysis data
      // For manual method, construct data from form inputs
      const mealJsonData = uploadMethod === 'photo' 
        ? analysis 
        : {
            dish_name: mealData.name,
            description: mealData.description,
            // Add other manual fields as needed
          };
      
      // Format the consumed date as ISO string, ensuring we use local date
      // This preserves the exact date selected without timezone adjustments
      const consumedDate = format(mealData.consumedDate, 'yyyy-MM-dd');
      
      console.log("Selected date for upload:", consumedDate); // Debug log
      
      const res = await fetch(`${API_BASE_URL}/api/log-meal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          meal_type: mealData.type,
          meal_json: mealJsonData,
          uploaded_at: new Date().toISOString(),
          consumed_date: consumedDate // Fixed date format
        }),
      });
      
      if (!res.ok) throw new Error("Failed to log meal");
      
      toast({
        title: "Meal Logged Successfully!",
        description: `Your meal has been added to ${
          consumedDate === format(new Date(), 'yyyy-MM-dd')
            ? "today's" 
            : format(new Date(consumedDate), "MMMM d, yyyy")
        } log.`,
      });
      
      onBack();
    } catch (err) {
      toast({ title: "Log failed", description: err.message });
    }
  };

  const handleDiscard = () => {
    setAnalysis(null);
    setMealData(prev => ({ ...prev, photo: null }));
    setUploadMethod('photo');
  };

  const mealImageUrl = mealData.photo ? URL.createObjectURL(mealData.photo) : null;
  const formattedDate = mealData.consumedDate 
    ? format(mealData.consumedDate, 'MMMM d, yyyy')
    : 'Select date';

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
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Log Your Meal</h1>
          <p className="text-gray-600">Track what you eat to reach your goals</p>
        </div>
      </div>

      {/* Upload Method Selection */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>How would you like to log your meal?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <Button
              variant={uploadMethod === 'photo' ? 'default' : 'outline'}
              className="h-20 flex-col gap-2"
              onClick={() => setUploadMethod('photo')}
            >
              <Camera className="h-6 w-6" />
              Take Photo
            </Button>
            <Button
              variant={uploadMethod === 'manual' ? 'default' : 'outline'}
              className="h-20 flex-col gap-2"
              onClick={() => setUploadMethod('manual')}
            >
              <Upload className="h-6 w-6" />
              Manual Entry
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Photo Upload */}
      {uploadMethod === 'photo' && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Upload Meal Photo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg">
              {mealImageUrl ? (
                <div className="w-full">
                  <img 
                    src={mealImageUrl} 
                    alt="Meal preview" 
                    className="max-h-64 mx-auto mb-4 rounded-lg object-contain" 
                  />
                  <div className="flex justify-center gap-2">
                    <Button 
                      variant="secondary" 
                      onClick={() => setMealData(prev => ({ ...prev, photo: null }))}
                    >
                      Remove
                    </Button>
                    <Button 
                      onClick={handlePhotoAnalysis}
                      disabled={loading}
                    >
                      {loading ? "Analyzing..." : "Analyze"}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <Camera className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-4">Upload a photo of your meal</p>
                  <Button asChild variant="outline" className="w-48">
                    <label className="cursor-pointer">
                      <Upload className="h-4 w-4 mr-2" />
                      Choose Photo
                      <Input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleFileSelect}
                      />
                    </label>
                  </Button>
                </div>
              )}
            </div>
            
            {/* Error and loading states */}
            {loading && (
              <div className="text-center mt-4">
                <div className="animate-pulse mb-2">Analyzing your meal photo...</div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-green-500 rounded-full animate-pulse" style={{ width: '100%' }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Form for submission */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Manual Entry Form */}
        {uploadMethod === 'manual' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Meal Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="meal-name">Meal Name</Label>
                  <Input
                    id="meal-name"
                    placeholder="e.g., Grilled Chicken Salad"
                    value={mealData.name}
                    onChange={(e) => setMealData({ ...mealData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="meal-description">Description (Optional)</Label>
                  <Textarea
                    id="meal-description"
                    placeholder="Describe your meal, ingredients, cooking method..."
                    rows={3}
                    value={mealData.description}
                    onChange={(e) => setMealData({ ...mealData, description: e.target.value })}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Nutrition Information (Optional)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="calories">Calories</Label>
                    <Input id="calories" type="number" placeholder="0" />
                  </div>
                  <div>
                    <Label htmlFor="protein">Protein (g)</Label>
                    <Input id="protein" type="number" placeholder="0" />
                  </div>
                  <div>
                    <Label htmlFor="carbs">Carbs (g)</Label>
                    <Input id="carbs" type="number" placeholder="0" />
                  </div>
                  <div>
                    <Label htmlFor="fats">Fats (g)</Label>
                    <Input id="fats" type="number" placeholder="0" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Photo Analysis Result */}
        {analysis && (
          <MealAnalysis analysis={analysis} imageUrl={mealImageUrl} />
        )}

        {/* Meal Type Selection - Always show this */}
        <Card>
          <CardHeader>
            <CardTitle>Meal Type</CardTitle>
          </CardHeader>
          <CardContent>
            <Select 
              value={mealData.type} 
              onValueChange={(value) => setMealData(prev => ({ ...prev, type: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select meal type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="breakfast">Breakfast</SelectItem>
                <SelectItem value="lunch">Lunch</SelectItem>
                <SelectItem value="dinner">Dinner</SelectItem>
                <SelectItem value="snack">Snack</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Meal Date Selection - Moved after Meal Type */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>When did you eat this meal?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={dateOption === 'today' ? 'default' : 'outline'}
                  onClick={() => setDateOption('today')}
                >
                  Today
                </Button>
                {selectedDate && selectedDate !== format(new Date(), 'yyyy-MM-dd') && (
                  <Button
                    variant={dateOption === 'selected' ? 'default' : 'outline'}
                    onClick={() => setDateOption('selected')}
                  >
                    {format(new Date(selectedDate), 'MMMM d')}
                  </Button>
                )}
                <Button
                  variant={dateOption === 'custom' ? 'default' : 'outline'}
                  onClick={() => setDateOption('custom')}
                >
                  Custom Date
                </Button>
              </div>
              
              {dateOption === 'custom' && (
                <div>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button 
                        variant="outline"
                        className="w-full justify-start text-left font-normal"
                      >
                        <Calendar className="mr-2 h-4 w-4" />
                        {formattedDate}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <CalendarComponent
                        mode="single"
                        selected={mealData.consumedDate}
                        onSelect={handleDateSelect}
                        initialFocus
                        disabled={(date) => date > new Date()}
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Submit and Discard Buttons */}
        <div className="space-y-4">
          <Button
            type="submit"
            className="w-full h-12 bg-green-600 hover:bg-green-700 text-lg font-medium"
            disabled={
              !mealData.type || 
              (uploadMethod === 'manual' && !mealData.name) ||
              (uploadMethod === 'photo' && !analysis)
            }
          >
            Log Meal for {formattedDate}
          </Button>
          
          {analysis && (
            <Button
              type="button"
              variant="outline"
              className="w-full h-12 text-red-600 border-red-200 hover:bg-red-50 text-lg font-medium"
              onClick={handleDiscard}
            >
              Discard Analysis
            </Button>
          )}
        </div>
      </form>
    </div>
  );
};

export default MealUpload;
