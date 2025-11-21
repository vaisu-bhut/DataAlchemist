'use client';

import React, { useState, useRef, useEffect } from 'react';

export default function AgenticArchitecture() {
  const [status, setStatus] = useState('System Ready.');
  const [isRunning, setIsRunning] = useState(false);

  // Refs for direct DOM manipulation (Performant for animation frames)
  const svgRef = useRef<SVGSVGElement>(null);
  const packetGroupRef = useRef<SVGGElement>(null);
  const packetBodyRef = useRef<SVGCircleElement>(null);

  // Helper to toggle active class on nodes
  const highlight = (id: string, on: boolean) => {
    if (!svgRef.current) return;
    // We look for the group element with the specific ID
    const el = svgRef.current.querySelector(`#node-${id}`);
    if (el) {
      if (on) el.classList.add('active');
      else el.classList.remove('active');
    }
  };

  // Packet visual state helper
  const setPacketState = (state: 'request' | 'enriched') => {
    if (!packetBodyRef.current) return;
    if (state === 'request') {
      packetBodyRef.current.style.fill = 'var(--pkt-req)';
      packetBodyRef.current.setAttribute('r', '8');
      packetBodyRef.current.style.filter = 'none';
    } else {
      packetBodyRef.current.style.fill = 'var(--pkt-data)';
      packetBodyRef.current.setAttribute('r', '12');
      packetBodyRef.current.style.filter = 'url(#glow)';
    }
  };

  // The Physics/Animation Engine
  const move = (pathId: string, duration: number) => {
    return new Promise<void>((resolve) => {
      if (!svgRef.current || !packetGroupRef.current) {
        resolve();
        return;
      }

      const path = svgRef.current.querySelector(`#${pathId}`) as SVGPathElement;
      if (!path) {
        console.error(`Path ${pathId} not found`);
        resolve();
        return;
      }

      const len = path.getTotalLength();
      const start = performance.now();

      // Ensure packet is visible
      packetGroupRef.current.style.opacity = '1';

      const step = (time: number) => {
        const elapsed = time - start;
        const progress = Math.min(elapsed / duration, 1);

        // Calculate position
        const pt = path.getPointAtLength(progress * len);

        // Direct DOM update for performance
        if (packetGroupRef.current) {
          packetGroupRef.current.setAttribute('transform', `translate(${pt.x}, ${pt.y})`);
        }

        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          resolve();
        }
      };

      requestAnimationFrame(step);
    });
  };

  // --- WORKFLOWS ---

  const flowIngest = async () => {
    setStatus("User: Sending Data...");
    highlight('public', true);
    await move('p-public-master', 1000);
    highlight('public', false);

    setStatus("Master: Routing to PubSub...");
    highlight('master', true);
    await new Promise(r => setTimeout(r, 500));
    await move('p-master-pubsub', 800);
    highlight('master', false);

    setStatus("PubSub: Queuing Task...");
    highlight('pubsub', true);
    await new Promise(r => setTimeout(r, 400));

    setStatus("Ingest Agent: Polling...");
    await move('p-pubsub-ingest', 1000);
    highlight('pubsub', false);
    highlight('ingest', true);

    setStatus("Ingest Agent: Writing to Neo4j...");
    setPacketState('enriched');
    await move('p-ingest-neo', 1000);
    highlight('neo', true);
    await new Promise(r => setTimeout(r, 500));
    highlight('neo', false);

    setStatus("Ingest Agent: Task Complete.");
    highlight('ingest', false);
    setPacketState('request');

    // Return
    await move('p-ingest-pubsub', 1000);
    highlight('pubsub', true);
    await move('p-pubsub-master', 800);
    highlight('pubsub', false);
    highlight('master', true);
    await new Promise(r => setTimeout(r, 300));

    setStatus("User: 200 OK Received.");
    await move('p-master-public', 1000);
    highlight('master', false);
    highlight('public', true);
    await new Promise(r => setTimeout(r, 1000));
    highlight('public', false);
  };

  const flowChat = async () => {
    setStatus("User: Sending Query...");
    highlight('public', true);
    await move('p-public-master', 1000);
    highlight('public', false);

    setStatus("Master: Routing...");
    highlight('master', true);
    await move('p-master-pubsub', 800);
    highlight('master', false);
    highlight('pubsub', true);

    setStatus("Chat Agent: Picking up Query...");
    await move('p-pubsub-chat', 1000);
    highlight('pubsub', false);
    highlight('chat', true);

    // Neo4j
    setStatus("Chat Agent: Fetching Context (Neo4j)...");
    await move('p-chat-neo', 800);
    highlight('neo', true);
    await new Promise(r => setTimeout(r, 500));

    setPacketState('enriched');
    setStatus("Context Retrieved!");
    await move('p-neo-chat', 800);
    highlight('neo', false);

    // Gemini
    setStatus("Chat Agent: Synthesizing (Gemini)...");
    await move('p-chat-gemini', 1000);
    highlight('gemini', true);
    await new Promise(r => setTimeout(r, 800));

    setStatus("Answer Generated!");
    await move('p-gemini-chat', 1000);
    highlight('gemini', false);

    // Return
    setStatus("Chat Agent: Sending Response...");
    highlight('chat', false);
    await move('p-chat-pubsub', 1000);
    highlight('pubsub', true);
    await move('p-pubsub-master', 800);
    highlight('pubsub', false);
    highlight('master', true);
    await move('p-master-public', 1000);
    highlight('master', false);

    setStatus("User: Answer Received.");
    highlight('public', true);
    await new Promise(r => setTimeout(r, 1000));
    highlight('public', false);
  };

  const flowAnalytics = async () => {
    setStatus("Admin: Requesting Dashboard...");
    highlight('corp', true);
    await move('p-corp-master', 1000);
    highlight('corp', false);

    setStatus("Master: Checking Permissions...");
    highlight('master', true);
    await move('p-master-pubsub', 800);
    highlight('master', false);

    setStatus("Analytics Agent: Calculating Stats...");
    await move('p-pubsub-analytics', 1000);
    highlight('analytics', true);

    // Neo4j
    setStatus("Analytics: Aggregating Data...");
    await move('p-analytics-neo', 1000);
    highlight('neo', true);
    await new Promise(r => setTimeout(r, 600));

    setPacketState('enriched');
    await move('p-neo-analytics', 1000);
    highlight('neo', false);

    // Return
    setStatus("Analytics: Report Ready.");
    highlight('analytics', false);
    await move('p-analytics-pubsub', 1000);
    await move('p-pubsub-master', 800);
    highlight('master', true);
    await move('p-master-corp', 1000);
    highlight('master', false);

    setStatus("Admin: Dashboard Updated.");
    highlight('corp', true);
    await new Promise(r => setTimeout(r, 1000));
    highlight('corp', false);
  };

  // Master Runner
  const runSimulation = async (mode: 'ingest' | 'chat' | 'analytics') => {
    if (isRunning) return;
    setIsRunning(true);
    setPacketState('request');

    if (mode === 'ingest') await flowIngest();
    if (mode === 'chat') await flowChat();
    if (mode === 'analytics') await flowAnalytics();

    if (packetGroupRef.current) packetGroupRef.current.style.opacity = '0';
    setStatus("System Ready.");
    setIsRunning(false);

    // Cleanup any stuck highlights
    if (svgRef.current) {
      svgRef.current.querySelectorAll('.active').forEach(el => el.classList.remove('active'));
    }
  };

  return (
    <section id="architecture" className="py-24 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-5xl md:text-6xl font-bold mb-4 text-teal-900">
            Interactive Architecture Simulation
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Watch real-time data flow through our multi-agent system. Click any simulation button to see how requests are processed across different workflows.
          </p>
        </div>

        <div className="flex flex-col items-center justify-center w-full">
          <style jsx>{`
        :root {
          --c-public: #14b8a6;
          --c-corp: #0d9488;
          --c-master: #14b8a6;
          --c-pubsub: #0f766e;
          --c-ingest: #14b8a6;
          --c-chat: #0d9488;
          --c-analytics: #115e59;
          --c-neo: #0f172a;
          --c-gemini: #134e4a;
          --pkt-req: #14b8a6;
          --pkt-data: #2dd4bf;
        }
        
        .node-box { fill: #fff; stroke-width: 3px; rx: 12; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05)); transition: all 0.3s ease; }
        .node-label { font-weight: 800; font-size: 13px; text-anchor: middle; pointer-events: none; fill: #fff; font-family: sans-serif; }
        .node-sub { font-size: 10px; text-anchor: middle; pointer-events: none; fill: rgba(255,255,255,0.85); font-family: sans-serif; }
        .node-detail { font-size: 9px; text-anchor: middle; pointer-events: none; fill: rgba(255,255,255,0.75); font-family: sans-serif; font-style: italic; }

        /* Type Colors - Complementary palette with teal theme */
        .type-public { fill: #06b6d4; stroke: #06b6d4; }
        .type-corp { fill: #8b5cf6; stroke: #8b5cf6; }
        .type-master { fill: #f59e0b; stroke: #f59e0b; }
        .type-pubsub { fill: #14b8a6; stroke: #14b8a6; }
        .type-ingest { fill: #10b981; stroke: #10b981; }
        .type-chat { fill: #3b82f6; stroke: #3b82f6; }
        .type-analytics { fill: #ec4899; stroke: #ec4899; }
        .type-neo { fill: #1e293b; stroke: #1e293b; }
        .type-gemini { fill: #6366f1; stroke: #6366f1; }

        .connector { fill: none; stroke: #cbd5e1; stroke-width: 2; stroke-dasharray: 6; opacity: 0.6; }
        
        /* Active State */
        .active { transform-origin: center; animation: pulse 1s infinite; }
        .node-box.active { transform: scale(1.05); filter: drop-shadow(0 10px 20px rgba(0,0,0,0.15)); }
        
        @keyframes pulse {
            0% { filter: drop-shadow(0 0 0px rgba(0,0,0,0)); }
            50% { filter: drop-shadow(0 0 15px rgba(0,0,0,0.2)); }
            100% { filter: drop-shadow(0 0 0px rgba(0,0,0,0)); }
        }
      `}</style>

          <div className="flex gap-4 mb-6 z-10">
            <button
              onClick={() => runSimulation('ingest')}
              disabled={isRunning}
              className="bg-white border-2 border-slate-300 text-slate-600 px-6 py-2 rounded-full font-bold uppercase text-xs tracking-wide transition hover:-translate-y-1 hover:shadow-lg hover:text-slate-900 disabled:opacity-50 disabled:cursor-not-allowed border-b-4 border-b-teal-500"
            >
              Simulate Ingest
            </button>
            <button
              onClick={() => runSimulation('chat')}
              disabled={isRunning}
              className="bg-white border-2 border-slate-300 text-slate-600 px-6 py-2 rounded-full font-bold uppercase text-xs tracking-wide transition hover:-translate-y-1 hover:shadow-lg hover:text-slate-900 disabled:opacity-50 disabled:cursor-not-allowed border-b-4 border-b-teal-600"
            >
              Simulate Chat
            </button>
            <button
              onClick={() => runSimulation('analytics')}
              disabled={isRunning}
              className="bg-white border-2 border-slate-300 text-slate-600 px-6 py-2 rounded-full font-bold uppercase text-xs tracking-wide transition hover:-translate-y-1 hover:shadow-lg hover:text-slate-900 disabled:opacity-50 disabled:cursor-not-allowed border-b-4 border-b-teal-700"
            >
              Simulate Analytics
            </button>
          </div>

          <div className="relative w-full max-w-5xl aspect-[11/8] bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
            <svg ref={svgRef} viewBox="0 0 1100 700" className="w-full h-full">
              <defs>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              {/* CONNECTORS */}
              <path id="p-public-master" d="M 150 100 C 300 100, 400 100, 550 100" className="connector" />
              <path id="p-master-public" d="M 550 100 C 400 100, 300 100, 150 100" className="connector" />

              <path id="p-corp-master" d="M 950 100 C 800 100, 700 100, 550 100" className="connector" />
              <path id="p-master-corp" d="M 550 100 C 700 100, 800 100, 950 100" className="connector" />

              <path id="p-master-pubsub" d="M 550 140 L 550 220" className="connector" />
              <path id="p-pubsub-master" d="M 550 220 L 550 140" className="connector" />

              <path id="p-pubsub-ingest" d="M 550 260 C 550 320, 200 300, 200 380" className="connector" />
              <path id="p-ingest-pubsub" d="M 200 380 C 200 320, 530 320, 530 260" className="connector" />

              <path id="p-pubsub-chat" d="M 550 280 L 550 380" className="connector" />
              <path id="p-chat-pubsub" d="M 550 380 L 550 280" className="connector" />

              <path id="p-pubsub-analytics" d="M 550 260 C 550 320, 900 300, 900 380" className="connector" />
              <path id="p-analytics-pubsub" d="M 900 380 C 900 320, 570 320, 570 260" className="connector" />

              <path id="p-ingest-neo" d="M 200 440 C 200 500, 400 550, 450 550" className="connector" />

              <path id="p-chat-neo" d="M 550 440 L 550 520" className="connector" />
              <path id="p-neo-chat" d="M 550 520 L 550 440" className="connector" />

              <path id="p-analytics-neo" d="M 900 440 C 900 500, 700 550, 650 550" className="connector" />
              <path id="p-neo-analytics" d="M 650 550 C 700 550, 900 500, 900 440" className="connector" />

              <path id="p-chat-gemini" d="M 550 440 C 600 500, 730 620, 730 620" className="connector" />
              <path id="p-gemini-chat" d="M 730 620 C 730 620, 600 500, 550 440" className="connector" />


              {/* NODES */}
              <g id="node-public" transform="translate(40, 50)">
                <rect width="180" height="90" className="node-box type-public" />
                <text x="90" y="25" className="node-label">PUBLIC USER</text>
                <text x="90" y="42" className="node-sub">Browser / Mobile</text>
                <text x="90" y="58" className="node-detail">HTTP Requests</text>
                <text x="90" y="72" className="node-detail">REST API Client</text>
              </g>

              <g id="node-corp" transform="translate(880, 50)">
                <rect width="180" height="90" className="node-box type-corp" />
                <text x="90" y="25" className="node-label">LEADERSHIP</text>
                <text x="90" y="42" className="node-sub">Admin Dashboard</text>
                <text x="90" y="58" className="node-detail">Analytics View</text>
                <text x="90" y="72" className="node-detail">Metrics & Reports</text>
              </g>

              <g id="node-master" transform="translate(460, 60)">
                <rect width="180" height="90" className="node-box type-master" />
                <text x="90" y="25" className="node-label">MASTER AGENT</text>
                <text x="90" y="42" className="node-sub">LangGraph Orchestrator</text>
                <text x="90" y="58" className="node-detail">Port 8000</text>
                <text x="90" y="72" className="node-detail">State Management</text>
              </g>

              <g id="node-pubsub" transform="translate(460, 200)">
                <rect width="180" height="90" className="node-box type-pubsub" />
                <text x="90" y="25" className="node-label">PUB/SUB</text>
                <text x="90" y="42" className="node-sub">Async Message Bus</text>
                <text x="90" y="58" className="node-detail">Port 8001</text>
                <text x="90" y="72" className="node-detail">Event Distribution</text>
              </g>

              <g id="node-ingest" transform="translate(90, 350)">
                <rect width="180" height="90" className="node-box type-ingest" />
                <text x="90" y="25" className="node-label">INGEST AGENT</text>
                <text x="90" y="42" className="node-sub">Data Processing</text>
                <text x="90" y="58" className="node-detail">Port 8002</text>
                <text x="90" y="72" className="node-detail">PII Redaction</text>
              </g>

              <g id="node-chat" transform="translate(460, 350)">
                <rect width="180" height="90" className="node-box type-chat" />
                <text x="90" y="25" className="node-label">CHAT AGENT</text>
                <text x="90" y="42" className="node-sub">RAG + Synthesis</text>
                <text x="90" y="58" className="node-detail">Port 8003</text>
                <text x="90" y="72" className="node-detail">Vector Search</text>
              </g>

              <g id="node-analytics" transform="translate(830, 350)">
                <rect width="180" height="90" className="node-box type-analytics" />
                <text x="90" y="25" className="node-label">ANALYTICS AGENT</text>
                <text x="90" y="42" className="node-sub">Metrics Aggregator</text>
                <text x="90" y="58" className="node-detail">Port 8004</text>
                <text x="90" y="72" className="node-detail">Data Insights</text>
              </g>

              <g id="node-neo" transform="translate(460, 500)">
                <rect width="180" height="90" className="node-box type-neo" />
                <text x="90" y="28" className="node-label">NEO4J DB</text>
                <text x="90" y="45" className="node-sub">Graph Database</text>
                <text x="90" y="61" className="node-detail">Vector Index</text>
                <text x="90" y="75" className="node-detail">Knowledge Graph</text>
              </g>

              <g id="node-gemini" transform="translate(740, 590)">
                <rect width="160" height="80" className="node-box type-gemini" />
                <text x="80" y="24" className="node-label">GEMINI 2.5</text>
                <text x="80" y="40" className="node-sub">LLM Processing</text>
                <text x="80" y="55" className="node-detail">Text Generation</text>
                <text x="80" y="68" className="node-detail">Embeddings</text>
              </g>

              {/* DATA PACKET */}
              <g ref={packetGroupRef} id="packet-group" style={{ opacity: 0, pointerEvents: 'none' }}>
                <circle cx="0" cy="0" r="10" fill="#14b8a6" opacity="0.3" />
                <circle ref={packetBodyRef} cx="0" cy="0" r="8" fill="#14b8a6" stroke="#fff" strokeWidth="2.5" />
                <circle cx="0" cy="0" r="4" fill="#5eead4" opacity="0.8" />
              </g>

            </svg>
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-slate-50 px-6 py-3 mt-4 rounded-xl border border-slate-200 text-slate-700 font-mono font-bold shadow-sm min-w-[400px] text-center">
              {status}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}