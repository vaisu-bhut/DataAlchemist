import { Bot, Shield, Search, Network, TrendingUp, Container } from 'lucide-react';

const features = [
  {
    icon: Bot,
    title: 'AI-Powered Intelligence',
    description: "Uses Google's Gemini LLM to extract canonical issues and solutions from your chat logs automatically."
  },
  {
    icon: Shield,
    title: 'PII Protection',
    description: 'Automatically detects and redacts sensitive customer information to ensure privacy compliance.'
  },
  {
    icon: Search,
    title: 'Semantic Search',
    description: 'Vector-based similarity search finds relevant solutions even when customers phrase questions differently.'
  },
  {
    icon: Network,
    title: 'Graph Knowledge Base',
    description: 'Neo4j graph database stores relationships between issues, solutions, and customer interactions.'
  },
  {
    icon: TrendingUp,
    title: 'Continuous Learning',
    description: 'Human review workflow ensures quality control and continuous improvement of responses.'
  },
  {
    icon: Container,
    title: 'Production Ready',
    description: 'Fully containerized with Docker, ready for deployment with monitoring and scaling capabilities.'
  }
];

export default function Features() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Why DataAlchemist?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Turn your historical customer conversations into a powerful AI knowledge base that learns and improves over time.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-50 p-8 rounded-2xl hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
            >
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
                <feature.icon className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}