'use client';

import { Rocket, X } from 'lucide-react';
import { useState } from 'react';

export default function ComingSoonBanner() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-teal-600 via-teal-500 to-cyan-600 text-white py-4 px-4 shadow-2xl animate-slide-down border-b-4 border-teal-700">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          <div className="bg-white/20 p-2 rounded-full backdrop-blur-sm">
            <Rocket className="w-6 h-6 flex-shrink-0 animate-bounce" />
          </div>
          <div>
            <p className="text-lg md:text-xl font-bold mb-1">
              🎉 Coming Soon: Fully operable Data Alchemist paltform!
            </p>
            <p className="text-sm md:text-base opacity-95">
              Experience the full agentic workflow system with real-time API integration and live data processing. Till then , explore the architecture and share your feedback.
            </p>
          </div>
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="p-2 hover:bg-white/20 rounded-full transition-all duration-200 flex-shrink-0 hover:rotate-90"
          aria-label="Close banner"
        >
          <X className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
