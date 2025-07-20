import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import React, { useState } from "react";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Login from "./components/Login";
import UserProfile from "./components/UserProfile";
import LoggedMealDetails from "./components/LoggedMealDetails";

const queryClient = new QueryClient();

const App = () => {
  const [userId, setUserId] = useState(localStorage.getItem("userId"));
  const [view, setView] = useState("home");
  const [selectedMeal, setSelectedMeal] = useState(null);

  const handleLogin = (user_id) => {
    setUserId(user_id);
    localStorage.setItem("userId", user_id);
  };

  const handleLogout = () => {
    setUserId(null);
    localStorage.removeItem("userId");
  };

  const handleViewChange = (newView, data = null) => {
    if (newView === "meal-analysis" && data) {
      setSelectedMeal(data);
    }
    setView(newView);
  };

  if (!userId) {
    return <Login onLogin={handleLogin} onSwitchToSignUp={() => {}} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/meal/:id" element={<LoggedMealDetails />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
