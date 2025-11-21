export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-xl font-bold text-white mb-4">Agentic Workflow System</h3>
            <p className="text-sm leading-relaxed">
              Multi-agent architecture for intelligent customer support powered by LangGraph, Neo4j, and Google Gemini AI.
            </p>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Technology Stack</h4>
            <ul className="space-y-2 text-sm">
              <li>• Python 3.11 + FastAPI</li>
              <li>• LangGraph Orchestration</li>
              <li>• Neo4j Graph Database</li>
              <li>• Google Gemini AI</li>
              <li>• Docker + Cloud Run</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Architecture</h4>
            <ul className="space-y-2 text-sm">
              <li>• Master Agent (Port 8000)</li>
              <li>• Pub/Sub Bus (Port 8001)</li>
              <li>• Ingest Agent (Port 8002)</li>
              <li>• Chat Agent (Port 8003)</li>
              <li>• Analytics Agent (Port 8004)</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 pt-8 text-center">
          <p className="text-sm">
            © {new Date().getFullYear()} Agentic Workflow System. Built with Next.js, TypeScript, and Tailwind CSS.
          </p>
          <p className="text-xs mt-2 text-gray-500">
            Interactive simulation demonstrating real-time multi-agent communication patterns
          </p>
        </div>
      </div>
    </footer>
  );
}
