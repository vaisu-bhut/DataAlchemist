import { Upload, Cpu, Database, MessageSquare } from 'lucide-react';

const steps = [
  {
    number: 1,
    icon: Upload,
    title: 'Ingest Conversations',
    description: 'Upload your historical customer-agent chat logs in JSON format through our secure API.'
  },
  {
    number: 2,
    icon: Cpu,
    title: 'AI Processing',
    description: 'Our AI extracts canonical issues and solutions while automatically redacting sensitive information.'
  },
  {
    number: 3,
    icon: Database,
    title: 'Knowledge Storage',
    description: 'Issues and solutions are stored in a graph database with vector embeddings for semantic search.'
  },
  {
    number: 4,
    icon: MessageSquare,
    title: 'Intelligent Responses',
    description: 'When customers ask questions, the system finds relevant solutions and synthesizes personalized responses.'
  }
];

export default function HowItWorks() {
  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            How It Works
          </h2>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              <div className="relative mb-8">
                <div className="w-20 h-20 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {step.number}
                </div>
                <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto">
                  <step.icon className="w-8 h-8 text-blue-600" />
                </div>
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-10 left-full w-full h-0.5 bg-blue-200 transform -translate-y-1/2"></div>
                )}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                {step.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}