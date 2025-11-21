'use client';

import { Network, ArrowDown } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function Hero() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const scrollToArchitecture = () => {
    document.getElementById('architecture')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-teal-50">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-teal-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-float"></div>
        <div className="absolute top-40 right-10 w-96 h-96 bg-teal-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float-delayed"></div>
        <div className="absolute -bottom-20 left-1/2 w-96 h-96 bg-teal-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
      </div>

      <div className={`relative z-10 max-w-6xl mx-auto px-4 text-center transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
        <div className="flex items-center justify-center mb-8 animate-scale-in">
          <div className="relative">
            <Network className="w-20 h-20 text-teal-600" strokeWidth={1.5} />
            <div className="absolute inset-0 bg-teal-400 rounded-full blur-2xl opacity-20 animate-pulse-slow"></div>
          </div>
        </div>
        
        <h1 className="text-6xl md:text-8xl font-bold mb-6 text-teal-900 animate-fade-in">
          Agentic Workflow System
        </h1>
        
        <p className="text-2xl md:text-3xl text-gray-800 mb-4 animate-slide-up font-light">
          Multi-Agent Architecture for Intelligent Customer Support
        </p>
        
        <p className="text-lg md:text-xl text-gray-700 mb-12 max-w-3xl mx-auto animate-slide-up" style={{ animationDelay: '0.2s' }}>
          Autonomous agents communicating through pub/sub messaging with LangGraph orchestration, 
          Neo4j graph database, and Google Gemini AI
        </p>
        
        <button
          onClick={scrollToArchitecture}
          className="group inline-flex items-center gap-3 bg-teal-600 hover:bg-teal-700 text-white px-8 py-4 rounded-full text-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-2xl shadow-lg animate-scale-in"
          style={{ animationDelay: '0.4s' }}
        >
          Explore Architecture
          <ArrowDown className="w-5 h-5 group-hover:translate-y-1 transition-transform duration-300" />
        </button>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-teal-600 rounded-full flex items-start justify-center p-2">
          <div className="w-1 h-3 bg-teal-600 rounded-full animate-pulse"></div>
        </div>
      </div>
    </section>
  );
}
