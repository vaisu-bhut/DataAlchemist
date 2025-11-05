'use client';

import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

const ingestExample = {
  conversations: [
    {
      conversation_id: "conv_001",
      customer_id: "customer_123",
      agent_id: "agent_456",
      messages: [
        {
          role: "customer",
          content: "I can't log into my account",
          timestamp: "2024-11-01T10:00:00Z"
        },
        {
          role: "agent",
          content: "I can help you reset your password...",
          timestamp: "2024-11-01T10:01:00Z"
        }
      ],
      metadata: {
        channel: "chat",
        category: "account_access"
      }
    }
  ]
};

const chatExample = {
  query: "I cannot log into my account",
  customer_id: "customer_123"
};

const chatResponse = {
  response: "It sounds like you're having trouble accessing your account. Based on similar cases, this is often due to a temporarily locked account from multiple failed login attempts. Try using the 'Forgot Password' link on the login page to reset your password.",
  confidence: 0.92,
  sources: [
    {
      conversation_id: "conv_001",
      similarity: 0.95
    }
  ]
};

export default function Demo() {
  const [activeTab, setActiveTab] = useState<'ingest' | 'chat'>('ingest');
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <section id="demo" className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Try It Out
          </h2>
        </div>
        
        <div className="bg-white rounded-3xl p-8 shadow-xl">
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => setActiveTab('ingest')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                activeTab === 'ingest'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Ingest Data
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Chat Query
            </button>
          </div>
          
          {activeTab === 'ingest' && (
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                Sample Ingest Request
              </h3>
              <p className="text-gray-600 mb-6">
                Upload conversation data to build your knowledge base:
              </p>
              <div className="relative">
                <button
                  onClick={() => copyToClipboard(JSON.stringify(ingestExample, null, 2), 'ingest')}
                  className="absolute top-4 right-4 p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                >
                  {copied === 'ingest' ? (
                    <Check className="w-4 h-4 text-green-600" />
                  ) : (
                    <Copy className="w-4 h-4 text-gray-600" />
                  )}
                </button>
                <pre className="bg-gray-900 text-green-400 p-6 rounded-xl overflow-x-auto text-sm">
                  {JSON.stringify(ingestExample, null, 2)}
                </pre>
              </div>
            </div>
          )}
          
          {activeTab === 'chat' && (
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                Sample Chat Query
              </h3>
              <p className="text-gray-600 mb-6">
                Ask questions and get intelligent responses:
              </p>
              <div className="space-y-6">
                <div className="relative">
                  <h4 className="text-lg font-medium text-gray-900 mb-3">Request:</h4>
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(chatExample, null, 2), 'chat-request')}
                    className="absolute top-0 right-4 p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                  >
                    {copied === 'chat-request' ? (
                      <Check className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-600" />
                    )}
                  </button>
                  <pre className="bg-gray-900 text-green-400 p-6 rounded-xl overflow-x-auto text-sm">
                    {JSON.stringify(chatExample, null, 2)}
                  </pre>
                </div>
                
                <div className="relative">
                  <h4 className="text-lg font-medium text-gray-900 mb-3">Response:</h4>
                  <button
                    onClick={() => copyToClipboard(JSON.stringify(chatResponse, null, 2), 'chat-response')}
                    className="absolute top-0 right-4 p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                  >
                    {copied === 'chat-response' ? (
                      <Check className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-600" />
                    )}
                  </button>
                  <pre className="bg-gray-900 text-blue-400 p-6 rounded-xl overflow-x-auto text-sm">
                    {JSON.stringify(chatResponse, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}