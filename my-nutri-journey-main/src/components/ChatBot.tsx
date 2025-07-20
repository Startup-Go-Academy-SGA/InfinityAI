import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, Send, MessageCircle, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const ChatBot = ({ onBack, userId, userProfile }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      message: "Hello! I'm your personal nutrition expert. I can help you with meal planning, nutrition questions, and dietary advice. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickQuestions = [
    "What's a healthy breakfast for weight loss?",
    "How much protein should I eat daily?",
    "What are good pre-workout snacks?",
    "How to increase fiber intake?",
    "Best foods for muscle building?"
  ];

  const getBotResponse = async (userMessage) => {
    const body = {
      user_id: userId,
      message: userMessage,
      chat_history: messages.map(m => ({
        type: m.type,
        message: m.message
      }))
    };
    //console.log("Sending to /api/chatbot:", body); // <-- Print body for debug
    try {
      const res = await fetch(`${API_BASE_URL}/api/chatbot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      return data.response;
    } catch (e) {
      return "Sorry, I couldn't process your request. Please try again.";
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      message: inputMessage,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);
    setInputMessage('');

    // Call backend for LLM response
    const botReply = await getBotResponse(inputMessage);
    const botResponse = {
      id: messages.length + 2,
      type: 'bot',
      message: botReply,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, botResponse]);
  };

  const handleQuickQuestion = async (question) => {
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      message: question,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);

    const botReply = await getBotResponse(question);
    const botResponse = {
      id: messages.length + 2,
      type: 'bot',
      message: botReply,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, botResponse]);
  };

  // Add reset handler
  const handleReset = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        message: "Hello! I'm your personal nutrition expert. I can help you with meal planning, nutrition questions, and dietary advice. What would you like to know?",
        timestamp: new Date()
      }
    ]);
    setInputMessage('');
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-green-50 via-white to-orange-50">
      <div className="flex-1 flex flex-col items-center">
        <div className="w-full max-w-4xl flex flex-col flex-1 mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between gap-4 p-4 bg-white border-b">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={onBack}
                className="rounded-full"
                title="Back"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <MessageCircle className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-800">Nutrition Expert</h1>
                  <p className="text-sm text-green-600">Online • Ready to help</p>
                </div>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="rounded-full flex items-center gap-2"
              title="Reset Conversation"
            >
              <RotateCcw className="h-4 w-4" />
              <span>New Conversation</span>
            </Button>
          </div>

          {/* Quick Questions */}
          {messages.length === 1 && (
            <div className="p-4 bg-white border-b">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Questions:</h3>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question, index) => (
                  <Badge
                    key={index}
                    variant="secondary"
                    className="cursor-pointer hover:bg-green-100 hover:text-green-700 transition-colors px-3 py-1"
                    onClick={() => handleQuickQuestion(question)}
                  >
                    {question}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 flex flex-col pb-28">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-green-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.message}</p>
                  <p className={`text-xs mt-2 ${
                    message.type === 'user' ? 'text-green-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input bar - fixed above navigation, centered */}
      <div className="fixed bottom-16 left-0 right-0 z-30 flex justify-center">
        <div className="w-full max-w-4xl bg-white border-t px-4 py-3">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type any nutrition question or topic here…"
              className="flex-1"
            />
            <Button
              type="submit"
              size="icon"
              className="bg-green-600 hover:bg-green-700"
              disabled={!inputMessage.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;
