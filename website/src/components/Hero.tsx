'use client';

import { Brain, ArrowRight } from 'lucide-react';

export default function Hero() {
  const scrollToDemo = () => {
    document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center text-white px-4">
      <div className="max-w-6xl mx-auto text-center">
        <div className="flex items-center justify-center mb-6">
          <Brain className="w-16 h-16 mr-4 text-blue-200" />
          <h1 className="text-5xl md:text-7xl font-bold">
            DataAlchemist
          </h1>
        </div>
        
        <h2 className="text-2xl md:text-4xl font-light mb-6 text-blue-100">
          Transform Customer Conversations into Knowledge
        </h2>
        
        <p className="text-xl md:text-2xl mb-8 text-blue-200 max-w-4xl mx-auto">
          AI-powered knowledge engine that converts chat logs into searchable, intelligent responses
        </p>
        
        <button
          onClick={scrollToDemo}
          className="inline-flex items-center bg-red-500 hover:bg-red-600 text-white px-8 py-4 rounded-full text-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
        >
          Try It Now
          <ArrowRight className="ml-2 w-5 h-5" />
        </button>
      </div>
      
      {/* Floating elements */}
      <div className="absolute top-20 left-10 w-20 h-20 bg-white/10 rounded-full animate-pulse"></div>
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-white/5 rounded-full animate-bounce"></div>
      <div className="absolute top-1/2 left-20 w-16 h-16 bg-white/10 rounded-full animate-ping"></div>
    </section>
  );
}