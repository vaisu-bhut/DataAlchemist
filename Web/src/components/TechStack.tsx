'use client';

import { useEffect, useRef, useState } from 'react';
import { Code, Database, Cpu, Container, Zap, Shield } from 'lucide-react';

export default function TechStack() {
  const [isVisible, setIsVisible] = useState(false);
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

  const techCategories = [
    {
      icon: Code,
      title: 'Core Framework',
      color: 'bg-teal-600',
      technologies: [
        { name: 'Python 3.11', description: 'Async/await for concurrent processing' },
        { name: 'FastAPI', description: 'High-performance async web framework' },
        { name: 'LangGraph', description: 'State machine workflow orchestration' },
        { name: 'Pydantic', description: 'Data validation and type safety' }
      ]
    },
    {
      icon: Database,
      title: 'Data Layer',
      color: 'bg-teal-700',
      technologies: [
        { name: 'Neo4j 5.14+', description: 'Graph database with vector search' },
        { name: 'Vector Embeddings', description: '768-dimensional semantic search' },
        { name: 'Cypher Query', description: 'Graph traversal and analytics' },
        { name: 'Async Driver', description: 'Non-blocking database operations' }
      ]
    },
    {
      icon: Cpu,
      title: 'AI & ML',
      color: 'bg-teal-800',
      technologies: [
        { name: 'Google Gemini', description: 'LLM for extraction and synthesis' },
        { name: 'text-embedding-004', description: 'Embedding model (768-dim)' },
        { name: 'Cosine Similarity', description: 'Vector comparison for search' },
        { name: 'Composite Ranking', description: 'Multi-factor relevance scoring' }
      ]
    },
    {
      icon: Container,
      title: 'Infrastructure',
      color: 'bg-teal-900',
      technologies: [
        { name: 'Docker', description: 'Containerization for each agent' },
        { name: 'Docker Compose', description: 'Local development orchestration' },
        { name: 'Cloud Run', description: 'Serverless container platform' },
        { name: 'GCP Secrets', description: 'Secure credential management' }
      ]
    },
    {
      icon: Zap,
      title: 'Messaging',
      color: 'bg-teal-700',
      technologies: [
        { name: 'Async Queues', description: 'In-memory pub/sub with deque' },
        { name: 'Correlation IDs', description: 'Request tracking across agents' },
        { name: 'Peek/Acknowledge', description: 'Reliable message delivery' },
        { name: 'Topic Routing', description: 'Event-driven communication' }
      ]
    },
    {
      icon: Shield,
      title: 'Security & Quality',
      color: 'bg-teal-800',
      technologies: [
        { name: 'PII Redaction', description: 'Automatic sensitive data removal' },
        { name: 'Structured Logging', description: 'Debugging with structlog' },
        { name: 'Type Safety', description: 'Full TypeScript/Pydantic coverage' },
        { name: 'Health Checks', description: 'Service monitoring endpoints' }
      ]
    }
  ];

  const benefits = [
    {
      title: 'Independent Scaling',
      description: 'Each agent scales based on its workload (10 chat agents, 2 ingest agents)',
      icon: '📈'
    },
    {
      title: 'Fault Isolation',
      description: 'One agent failure doesn\'t affect others - graceful degradation',
      icon: '🛡️'
    },
    {
      title: 'Zero Downtime',
      description: 'Update agents independently without system-wide redeployment',
      icon: '🔄'
    },
    {
      title: 'Cost Efficient',
      description: 'Cloud Run scales to zero - pay only for actual usage',
      icon: '💰'
    },
    {
      title: 'Easy Testing',
      description: 'Test agents in isolation with clear pub/sub contracts',
      icon: '🧪'
    },
    {
      title: 'Extensible',
      description: 'Add new agent types without modifying existing code',
      icon: '🔌'
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
            Technology Stack
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Production-ready technologies powering the agentic architecture
          </p>
        </div>

        {/* Tech Categories */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {techCategories.map((category, index) => (
            <div
              key={index}
              className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
              style={{ transitionDelay: `${index * 0.1}s` }}
            >
              <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden group hover:-translate-y-2">
                <div className="bg-teal-600 p-6 text-white">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                      <category.icon className="w-5 h-5" />
                    </div>
                    <h3 className="text-xl font-bold">{category.title}</h3>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  {category.technologies.map((tech, idx) => (
                    <div key={idx} className="group/item">
                      <h4 className="font-semibold text-gray-900 mb-1 group-hover/item:text-teal-600 transition-colors">
                        {tech.name}
                      </h4>
                      <p className="text-sm text-gray-600">{tech.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Architecture Benefits */}
        <div className={`transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12">
            <h3 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-900">
              Why This Architecture?
            </h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {benefits.map((benefit, index) => (
                <div
                  key={index}
                  className="group p-6 bg-teal-50 rounded-2xl hover:shadow-lg transition-all duration-300 border-2 border-teal-100 hover:border-teal-300"
                >
                  <div className="text-4xl mb-4">{benefit.icon}</div>
                  <h4 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-teal-700 transition-colors">
                    {benefit.title}
                  </h4>
                  <p className="text-gray-700">{benefit.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Performance Stats */}
        <div className={`mt-16 grid md:grid-cols-4 gap-6 transition-all duration-1000 delay-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="bg-teal-600 rounded-2xl p-6 text-white text-center shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="text-4xl font-bold mb-2">10-30s</div>
            <div className="text-sm opacity-90">Ingest Processing Time</div>
          </div>
          <div className="bg-teal-700 rounded-2xl p-6 text-white text-center shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="text-4xl font-bold mb-2">5-15s</div>
            <div className="text-sm opacity-90">Chat Response Time</div>
          </div>
          <div className="bg-teal-800 rounded-2xl p-6 text-white text-center shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="text-4xl font-bold mb-2">&lt;100ms</div>
            <div className="text-sm opacity-90">Master Agent Overhead</div>
          </div>
          <div className="bg-teal-900 rounded-2xl p-6 text-white text-center shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="text-4xl font-bold mb-2">&lt;10ms</div>
            <div className="text-sm opacity-90">Pub/Sub Latency</div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className={`mt-16 text-center transition-all duration-1000 delay-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="bg-teal-600 rounded-3xl p-12 text-white shadow-2xl">
            <h3 className="text-3xl md:text-4xl font-bold mb-4">
              Production-Ready Agentic System
            </h3>
            <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
              Built for scale, reliability, and maintainability with modern cloud-native technologies
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <div className="px-6 py-3 bg-white/20 rounded-full backdrop-blur-sm">
                <span className="font-semibold">5 Independent Agents</span>
              </div>
              <div className="px-6 py-3 bg-white/20 rounded-full backdrop-blur-sm">
                <span className="font-semibold">Async Messaging</span>
              </div>
              <div className="px-6 py-3 bg-white/20 rounded-full backdrop-blur-sm">
                <span className="font-semibold">Vector Search</span>
              </div>
              <div className="px-6 py-3 bg-white/20 rounded-full backdrop-blur-sm">
                <span className="font-semibold">LangGraph Orchestration</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
