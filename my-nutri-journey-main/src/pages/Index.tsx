import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import HomePage from '../components/HomePage';
import MealDetails from '../components/SuggestedMealDetails';
import MealUpload from '../components/MealUpload';
import UserProfile from '../components/UserProfile';
import ProgressAnalytics from '../components/ProgressAnalytics';
import ChatBot from '../components/ChatBot';
import Navigation from '../components/Navigation';
import Login from '../components/Login';
import SignUp from '../components/SignUp';

const Index = () => {
  const [currentView, setCurrentView] = useState('home');
  const [selectedMeal, setSelectedMeal] = useState(null);
  const [userId, setUserId] = useState(() => localStorage.getItem("userId"));
  const [showSignUp, setShowSignUp] = useState(false);

  const handleLogin = (id) => {
    setUserId(id);
    localStorage.setItem("userId", id);
  };

  const handleLogout = () => {
    setUserId(null);
    localStorage.removeItem("userId");
  };

  if (!userId) {
    if (showSignUp) {
      return (
        <SignUp
          onSignUp={() => setShowSignUp(false)}
          onSwitchToLogin={() => setShowSignUp(false)}
        />
      );
    }
    return (
      <Login
        onLogin={handleLogin}
        onSwitchToSignUp={() => setShowSignUp(true)}
      />
    );
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'home':
        return <HomePage onMealClick={setSelectedMeal} onViewChange={setCurrentView} />;
      case 'meal-upload':
        return <MealUpload onBack={() => setCurrentView('home')} />;
      case 'profile':
        return <UserProfile userId={userId} onBack={() => setCurrentView('home')} onLogout={handleLogout} />;
      case 'progress':
        return <ProgressAnalytics onBack={() => setCurrentView('home')} />;
      case 'chatbot':
        return <ChatBot userId={userId} userProfile={null} onBack={() => setCurrentView('home')} />;
      default:
        return <HomePage onMealClick={setSelectedMeal} onViewChange={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-orange-50">
      {renderCurrentView()}
      <Navigation currentView={currentView} onViewChange={setCurrentView} onLogout={handleLogout} />
    </div>
  );
};

export default Index;
