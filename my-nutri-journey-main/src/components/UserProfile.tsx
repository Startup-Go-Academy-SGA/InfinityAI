import React, { useState, useEffect } from 'react';
import { ArrowLeft, User, Target, Heart } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const COUNTRY_OPTIONS = [
  "United States", "Canada", "United Kingdom", "Australia", "Germany", "France",
  "Italy", "Spain", "India", "China", "Japan", "South Korea", "Brazil", "Mexico",
  "Netherlands", "Sweden", "Norway", "Finland", "Denmark", "Switzerland", "New Zealand"
];

const UserProfile = ({ onBack, userId, onLogout }) => {
  const [profile, setProfile] = useState({
      name: '',
      birthdate: '',
      weight: 0,
      height: 0,
      country: '',
      gender: '',
      num_meals_per_day: 3,
      targetWeight: 0,
      activityLevel: '',
      allergies: [],
      dislikes: [],
      favoriteFoods: [],
      nutritionGoal: '',
      userProfile: '',
      daily_target_calories: null,
      daily_target_carbs: null,
      daily_target_protein: null,
      daily_target_fats: null,
    });
  const [isEditing, setIsEditing] = useState(false);
  const [newAllergy, setNewAllergy] = useState('');
  const [newDislike, setNewDislike] = useState('');
  const [newFavorite, setNewFavorite] = useState('');
  const [age, setAge] = useState<number | null>(null);

  // Fetch the user profile from backend using userId
  useEffect(() => {
    if (!userId) return;
    fetch(`${API_BASE_URL}/api/users/${userId}`)
      .then(res => res.json())
      .then(data => {
        setProfile(data);
        setAge(data.age);
      });
  }, [userId]);

  const calculateBMI = () => {
    const heightInM = profile.height / 100;
    return (profile.weight / (heightInM * heightInM)).toFixed(1);
  };

  const handleSave = async () => {
    await fetch(`${API_BASE_URL}/api/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    });
    // Fetch the updated profile (including the new generated userProfile)
    const res = await fetch(`${API_BASE_URL}/api/users/${userId}`);
    const data = await res.json();
    setProfile(data);
    setAge(data.age);
    toast({
      title: "Profile Updated!",
      description: "Your nutrition recommendations have been refreshed.",
    });
    setIsEditing(false);
  };

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
          <h1 className="text-2xl font-bold text-gray-800">Your Profile</h1>
          <p className="text-gray-600">Personalize your nutrition journey</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setIsEditing(!isEditing)}
            variant={isEditing ? "default" : "outline"}
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </Button>
          <Button
            onClick={onLogout}
            variant="outline"
            className="text-red-600 border-red-200"
          >
            Logout
          </Button>
        </div>
      </div>

      {/* Profile Summary */}
      <Card className="mb-6 bg-gradient-to-r from-blue-100 to-purple-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-gray-800">{profile.name}</h2>
              <div className="flex gap-4 mt-2">
                <Badge variant="secondary">Height: {profile.height}cm</Badge>
                <Badge variant="secondary">Weight: {profile.weight}kg</Badge>
                <Badge variant="secondary">BMI: {calculateBMI()}</Badge>
                <Badge variant="secondary">Age: {age}</Badge>
                <Badge variant="secondary">Country: {profile.country}</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Personal Information */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Personal Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={profile.name}
                disabled={!isEditing}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="birthdate">Birthdate</Label>
              <Input
                id="birthdate"
                type="date"
                value={profile.birthdate}
                disabled={!isEditing}
                onChange={(e) => setProfile({ ...profile, birthdate: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="weight">Weight (kg)</Label>
              <Input
                id="weight"
                type="number"
                value={profile.weight}
                disabled={!isEditing}
                onChange={(e) => setProfile({ ...profile, weight: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <Label htmlFor="height">Height (cm)</Label>
              <Input
                id="height"
                type="number"
                value={profile.height}
                disabled={!isEditing}
                onChange={(e) => setProfile({ ...profile, height: parseInt(e.target.value) })}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="country">Country</Label>
            <Select
              value={profile.country}
              disabled={!isEditing}
              onValueChange={(value) => setProfile({ ...profile, country: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {COUNTRY_OPTIONS.map((country) => (
                  <SelectItem key={country} value={country}>{country}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="gender">Gender</Label>
            <Select
              value={profile.gender || "other"}
              disabled={!isEditing}
              onValueChange={value => setProfile({ ...profile, gender: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="num-meals-per-day">Meals Per Day</Label>
            <Select
              value={profile.num_meals_per_day?.toString() || "3"}
              disabled={!isEditing}
              onValueChange={value => setProfile({ ...profile, num_meals_per_day: parseInt(value) })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select number" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1</SelectItem>
                <SelectItem value="2">2</SelectItem>
                <SelectItem value="3">3</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Goals & Targets */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Goals & Targets
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="nutrition-goal">Nutrition Goal</Label>
            <Input
              id="nutrition-goal"
              value={profile.nutritionGoal}
              disabled={!isEditing}
              onChange={e => setProfile({ ...profile, nutritionGoal: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="target-weight">Target Weight (kg)</Label>
              <Input
                id="target-weight"
                type="number"
                value={profile.targetWeight}
                disabled={!isEditing}
                onChange={(e) => setProfile({ ...profile, targetWeight: parseInt(e.target.value) })}
              />
            </div>
            <div>
              <Label htmlFor="activity-level">Activity Level</Label>
              <Select
                value={profile.activityLevel || ""}
                disabled={!isEditing}
                onValueChange={(value) => setProfile({ ...profile, activityLevel: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select activity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Sedentary">Sedentary</SelectItem>
                  <SelectItem value="Active">Active</SelectItem>
                  <SelectItem value="Athlete">Athlete</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label htmlFor="user-profile">User Profile</Label>
            <Textarea
              id="user-profile"
              value={profile.userProfile}
              disabled
              readOnly
              className="bg-gray-100"
            />
          </div>
          <div>
            <Label>Daily Macronutrient Targets</Label>
            <div className="flex gap-4 mt-2">
              <Badge variant="outline">
                🔥 Calories: {profile.daily_target_calories > 0 ? profile.daily_target_calories : '—'} kcal
              </Badge>
              <Badge variant="outline">
                🥚 Protein: {profile.daily_target_protein > 0 ? profile.daily_target_protein : '—'} g
              </Badge>
              <Badge variant="outline">
                🥔 Carbs: {profile.daily_target_carbs > 0 ? profile.daily_target_carbs : '—'} g
              </Badge>
              <Badge variant="outline">
                🧈 Fat: {profile.daily_target_fats > 0 ? profile.daily_target_fats : '—'} g
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dietary Preferences */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5" />
            Dietary Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Allergies */}
          <div>
            <Label>Allergies & Intolerances</Label>
            <div className="flex flex-wrap gap-2 mt-2 mb-2">
              {profile.allergies.map((allergy, idx) => (
                <Badge key={allergy} variant="destructive" className="flex items-center gap-1 px-3 py-1 text-sm rounded-full shadow">
                  {allergy}
                  {isEditing && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="p-0 ml-1 text-red-700 hover:bg-red-100"
                      onClick={() =>
                        setProfile({
                          ...profile,
                          allergies: profile.allergies.filter((_, i) => i !== idx),
                        })
                      }
                      aria-label="Remove allergy"
                    >
                      ×
                    </Button>
                  )}
                </Badge>
              ))}
            </div>
            {isEditing && (
              <form
                onSubmit={e => {
                  e.preventDefault();
                  if (newAllergy.trim()) {
                    setProfile({
                      ...profile,
                      allergies: [...profile.allergies, newAllergy.trim().toLowerCase()],
                    });
                    setNewAllergy('');
                  }
                }}
                className="flex gap-2 items-center mt-1"
              >
                <Input
                  size={8}
                  placeholder="Add allergy"
                  value={newAllergy}
                  onChange={e => setNewAllergy(e.target.value)}
                  className="h-8 text-sm rounded-full px-3 border-gray-300"
                />
                <Button type="submit" size="sm" className="h-8 rounded-full bg-red-500 hover:bg-red-600 text-white px-4">
                  Add
                </Button>
              </form>
            )}
          </div>
          {/* Dislikes */}
          <div>
            <Label>Foods You Dislike</Label>
            <div className="flex flex-wrap gap-2 mt-2 mb-2">
              {profile.dislikes.map((dislike, idx) => (
                <Badge key={dislike} variant="secondary" className="flex items-center gap-1 px-3 py-1 text-sm rounded-full shadow">
                  {dislike}
                  {isEditing && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="p-0 ml-1 text-gray-700 hover:bg-gray-100"
                      onClick={() =>
                        setProfile({
                          ...profile,
                          dislikes: profile.dislikes.filter((_, i) => i !== idx),
                        })
                      }
                      aria-label="Remove dislike"
                    >
                      ×
                    </Button>
                  )}
                </Badge>
              ))}
            </div>
            {isEditing && (
              <form
                onSubmit={e => {
                  e.preventDefault();
                  if (newDislike.trim()) {
                    setProfile({
                      ...profile,
                      dislikes: [...profile.dislikes, newDislike.trim().toLowerCase()],
                    });
                    setNewDislike('');
                  }
                }}
                className="flex gap-2 items-center mt-1"
              >
                <Input
                  size={8}
                  placeholder="Add dislike"
                  value={newDislike}
                  onChange={e => setNewDislike(e.target.value)}
                  className="h-8 text-sm rounded-full px-3 border-gray-300"
                />
                <Button type="submit" size="sm" className="h-8 rounded-full bg-gray-500 hover:bg-gray-600 text-white px-4">
                  Add
                </Button>
              </form>
            )}
          </div>
          {/* Favorites */}
          <div>
            <Label>Favorite Foods</Label>
            <div className="flex flex-wrap gap-2 mt-2 mb-2">
              {profile.favoriteFoods.map((food, idx) => (
                <Badge key={food} variant="outline" className="flex items-center gap-1 px-3 py-1 text-sm rounded-full shadow">
                  {food}
                  {isEditing && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="p-0 ml-1 text-green-700 hover:bg-green-100"
                      onClick={() =>
                        setProfile({
                          ...profile,
                          favoriteFoods: profile.favoriteFoods.filter((_, i) => i !== idx),
                        })
                      }
                      aria-label="Remove favorite"
                    >
                      ×
                    </Button>
                  )}
                </Badge>
              ))}
            </div>
            {isEditing && (
              <form
                onSubmit={e => {
                  e.preventDefault();
                  if (newFavorite.trim()) {
                    setProfile({
                      ...profile,
                      favoriteFoods: [...profile.favoriteFoods, newFavorite.trim().toLowerCase()],
                    });
                    setNewFavorite('');
                  }
                }}
                className="flex gap-2 items-center mt-1"
              >
                <Input
                  size={8}
                  placeholder="Add favorite"
                  value={newFavorite}
                  onChange={e => setNewFavorite(e.target.value)}
                  className="h-8 text-sm rounded-full px-3 border-gray-300"
                />
                <Button type="submit" size="sm" className="h-8 rounded-full bg-green-500 hover:bg-green-600 text-white px-4">
                  Add
                </Button>
              </form>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      {isEditing && (
        <Button
          onClick={handleSave}
          className="w-full h-12 bg-green-600 hover:bg-green-700 text-lg font-medium"
        >
          Save Profile
        </Button>
      )}
    </div>
  );
};

export default UserProfile;
