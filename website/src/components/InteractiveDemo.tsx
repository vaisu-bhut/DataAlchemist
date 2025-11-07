'use client';

import { useState } from 'react';
import { Send, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { apiClient, sampleIngestData, sampleChatQuery, type ChatResponse } from '@/lib/api';

export default function InteractiveDemo() {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState(sampleChatQuery.query);
  const [customerId, setCustomerId] = useState(sampleChatQuery.customer_id);

  const handleIngest = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiClient.ingestConversations(sampleIngestData);
      setResponse(null);
      alert('Sample data ingested successfully! You can now try the chat query.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to ingest data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatQuery = async () => {
    setIsLoading(true);
    setError(null);
    setResponse(null);
    
    try {
      const result = await apiClient.chatQuery({
        query,
        customer_id: customerId
      });
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Live API Demo
          </h2>
          <p className="text-xl text-gray-700">
            Test the actual API endpoints with real data
          </p>
        </div>
        
        <div className="bg-white rounded-3xl p-8 shadow-xl">
          {/* Step 1: Ingest Data */}
          <div className="mb-8 p-6 bg-blue-50 rounded-2xl">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Step 1: Ingest Sample Data
            </h3>
            <p className="text-black mb-4">
              First, let's upload some sample conversation data to the knowledge base.
            </p>
            <button
              onClick={handleIngest}
              disabled={isLoading}
              className="inline-flex items-center bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-xl font-semibold transition-colors duration-200"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              Ingest Sample Data
            </button>
          </div>
          
          {/* Step 2: Chat Query */}
          <div className="mb-8 p-6 bg-green-50 rounded-2xl">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Step 2: Ask a Question
            </h3>
            <p className="text-black mb-4">
              Now ask a question and get an AI-powered response based on the ingested data.
            </p>
            
            <div className="space-y-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Customer Query
                </label>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your question..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Customer ID
                </label>
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="customer_123"
                />
              </div>
            </div>
            
            <button
              onClick={handleChatQuery}
              disabled={isLoading || !query.trim()}
              className="inline-flex items-center bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-6 py-3 rounded-xl font-semibold transition-colors duration-200"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              Ask Question
            </button>
          </div>
          
          {/* Results */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
              <div className="flex items-center text-red-800">
                <XCircle className="w-5 h-5 mr-2" />
                <span className="font-medium">Error:</span>
              </div>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          )}
          
          {response && (
            <div className="p-6 bg-gray-50 rounded-2xl">
              <div className="flex items-center text-green-800 mb-4">
                <CheckCircle className="w-5 h-5 mr-2" />
                <span className="font-medium">Response received!</span>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">AI Response:</h4>
                  <p className="text-gray-700 bg-white p-4 rounded-xl border">
                    {response.response}
                  </p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Confidence:</h4>
                    <div className="bg-white p-3 rounded-xl border">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-gray-900">Confidence Score</span>
                        <span className="font-medium text-gray-900">{(response.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${response.confidence * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Sources:</h4>
                    <div className="bg-white p-3 rounded-xl border">
                      {response.sources.map((source, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-sm text-gray-900">{source.conversation_id}</span>
                          <span className="text-sm font-medium text-gray-900">{(source.similarity * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}