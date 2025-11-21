'use client';

import { useEffect, useRef, useState } from 'react';
import { Workflow, Upload, MessageSquare, BarChart3, Server, ChevronRight } from 'lucide-react';

export default function AgentDetails() {
  const [isVisible, setIsVisible] = useState(false);
  const [activeAgent, setActiveAgent] = useState(0);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const agents = [
    {
      icon: Workflow,
      name: 'Master Agent',
      port: '8000',
      color: 'teal-500',
      role: 'API Gateway & LangGraph Orchestrator',
      description: 'Receives HTTP requests and orchestrates workflows using LangGraph state machines',
      workflow: [
        'Receives client HTTP requests',
        'Creates correlation IDs for tracking',
        'Publishes requests to pub/sub topics',
        'Manages state: route → wait_response → complete',
        'Polls for responses using peek/acknowledge',
        'Returns results to clients'
      ],
      features: [
        'Stateful workflow management',
        'Non-blocking async handling',
        'Timeout management (300s)',
        'Proxies analytics requests'
      ],
      dependencies: 'FastAPI, LangGraph, httpx, structlog'
    },
    {
      icon: Upload,
      name: 'Ingest Agent',
      port: '8002',
      color: 'teal-600',
      role: 'Conversation Processing Worker',
      description: 'Processes customer conversations and extracts canonical knowledge using AI',
      workflow: [
        'Polls ingest.request topic continuously',
        'Redacts PII (emails, phones, SSN, etc.)',
        'Chunks text if needed (2000 char chunks)',
        'Calls Gemini to extract issues & solutions',
        'Generates 768-dim vector embeddings',
        'Stores in Neo4j with relationships',
        'Publishes result to ingest.response'
      ],
      features: [
        'Automatic PII redaction',
        'LLM-based extraction',
        'Vector similarity deduplication',
        'Graceful degradation'
      ],
      dependencies: 'Neo4j, Google Gemini AI, FastAPI'
    },
    {
      icon: MessageSquare,
      name: 'Chat Agent',
      port: '8003',
      color: 'teal-700',
      role: 'Query Response Worker',
      description: 'Handles customer queries with intelligent vector search and AI synthesis',
      workflow: [
        'Polls chat.request topic continuously',
        'Generates query embedding using Gemini',
        'Performs vector similarity search in Neo4j',
        'Ranks candidates with composite scoring',
        'Filters by confidence threshold (0.7)',
        'Synthesizes response with LLM',
        'Determines escalation need',
        'Publishes to chat.response'
      ],
      features: [
        'Vector similarity search',
        'Multi-factor ranking (40% similarity, 30% quality)',
        'Source citation with snippets',
        'Automatic escalation logic'
      ],
      dependencies: 'Neo4j Vector Search, Gemini AI, FastAPI'
    },
    {
      icon: BarChart3,
      name: 'Analytics Agent',
      port: '8004',
      color: 'teal-800',
      role: 'Metrics & Statistics API',
      description: 'Provides comprehensive analytics and insights from the knowledge base',
      workflow: [
        'Exposes REST API endpoints',
        'Queries Neo4j for metrics',
        'Aggregates conversation data',
        'Calculates performance stats',
        'Tracks issue distribution',
        'Monitors agent performance',
        'Returns formatted analytics'
      ],
      features: [
        'Summary metrics dashboard',
        'Issue distribution analysis',
        'Agent performance tracking',
        'Resolution time statistics',
        'Escalation analytics'
      ],
      dependencies: 'Neo4j, FastAPI, Pydantic'
    },
    {
      icon: Server,
      name: 'Pub/Sub Service',
      port: '8001',
      color: 'cyan-600',
      role: 'Message Bus for Inter-Agent Communication',
      description: 'Enables asynchronous communication between all agents',
      workflow: [
        'Maintains in-memory async queues',
        'Handles publish operations',
        'Supports peek without removal',
        'Acknowledges message delivery',
        'Filters by correlation ID',
        'Auto-cleanup expired messages (5min TTL)'
      ],
      features: [
        'Peek/acknowledge pattern',
        'Correlation ID filtering',
        'Message TTL management',
        'Topic-based routing'
      ],
      dependencies: 'FastAPI, asyncio, deque'
    }
  ];

  return (
    <section
      ref={sectionRef}
      className="py-24 px-4 bg-gray-50 relative overflow-hidden"
    >
      <div className="max-w-7xl mx-auto relative z-10">
        <div className={`text-center mb-16 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 text-gray-900">
            Agent Deep Dive
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Explore each autonomous agent's role, workflow, and capabilities
          </p>
        </div>

        {/* Agent Selector */}
        <div className={`flex flex-wrap justify-center gap-4 mb-12 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          {agents.map((agent, index) => (
            <button
              key={index}
              onClick={() => setActiveAgent(index)}
              className={`flex items-center gap-3 px-6 py-3 rounded-full font-semibold transition-all duration-300 ${
                activeAgent === index
                  ? 'bg-teal-600 text-white shadow-lg scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow'
              }`}
            >
              <agent.icon className="w-5 h-5" />
              {agent.name}
            </button>
          ))}
        </div>

        {/* Active Agent Details */}
        <div className={`transition-all duration-500 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
          {agents.map((agent, index) => (
            <div
              key={index}
              className={`transition-all duration-500 ${
                activeAgent === index ? 'block' : 'hidden'
              }`}
            >
              <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="bg-teal-600 p-8 text-white">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                      <agent.icon className="w-8 h-8" />
                    </div>
                    <div>
                      <h3 className="text-3xl font-bold">{agent.name}</h3>
                      <p className="text-lg opacity-90">Port {agent.port}</p>
                    </div>
                  </div>
                  <p className="text-xl font-semibold mb-2">{agent.role}</p>
                  <p className="text-lg opacity-90">{agent.description}</p>
                </div>

                {/* Content */}
                <div className="p-8 grid md:grid-cols-2 gap-8">
                  {/* Workflow */}
                  <div>
                    <h4 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <ChevronRight className="w-6 h-6 text-teal-600" />
                      Workflow
                    </h4>
                    <div className="space-y-3">
                      {agent.workflow.map((step, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-3 p-3 bg-teal-50 rounded-xl hover:bg-teal-100 transition-colors duration-200"
                        >
                          <div className="w-6 h-6 bg-teal-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                            {idx + 1}
                          </div>
                          <p className="text-gray-700">{step}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Features & Dependencies */}
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <ChevronRight className="w-6 h-6 text-teal-600" />
                        Key Features
                      </h4>
                      <div className="space-y-2">
                        {agent.features.map((feature, idx) => (
                          <div
                            key={idx}
                            className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors duration-200"
                          >
                            <div className="w-2 h-2 bg-teal-600 rounded-full"></div>
                            <p className="text-gray-700">{feature}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <ChevronRight className="w-6 h-6 text-teal-600" />
                        Dependencies
                      </h4>
                      <div className="p-4 bg-gray-900 rounded-xl">
                        <code className="text-teal-400 text-sm font-mono">
                          {agent.dependencies}
                        </code>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
