import React from 'react';
import { Home, Plus, TrendingUp, User, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

type NavigationProps = {
  currentView: any;
  onViewChange: any;
  onLogout: () => void;
};

const Navigation = ({ currentView, onViewChange, onLogout }: NavigationProps) => {
  const navItems = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'meal-upload', icon: Plus, label: 'Log Meal' },
    { id: 'progress', icon: TrendingUp, label: 'Progress' },
    { id: 'chatbot', icon: MessageCircle, label: 'Expert' },
    { id: 'profile', icon: User, label: 'Profile' }
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
      <div className="flex justify-around items-center max-w-4xl mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <Button
              key={item.id}
              variant="ghost"
              size="sm"
              onClick={() => onViewChange(item.id)}
              className={`flex flex-col items-center gap-1 h-auto py-2 px-3 transition-colors ${
                isActive 
                  ? 'text-green-600 bg-green-50' 
                  : 'text-gray-600 hover:text-green-600 hover:bg-green-50'
              }`}
            >
              <Icon className={`h-5 w-5 ${isActive ? 'fill-current' : ''}`} />
              <span className="text-xs font-medium">{item.label}</span>
            </Button>
          );
        })}
        {/* Logout button removed */}
      </div>
    </div>
  );
};

export default Navigation;
