# Agentic Workflow System - Documentation Website

A heavily animated, modern Next.js website showcasing the multi-agent architecture with a **teal color palette** and smooth transitions.

## 🎨 Design Philosophy

- **Teal Color Palette**: Primary colors from teal-50 to teal-900
- **Heavy Animations**: Smooth transitions, floating elements, slide-ups, fade-ins
- **No Gradients**: Clean, solid backgrounds with teal accents
- **Agent-Focused**: Exclusively about the services/agents architecture

## 📋 Sections

### 1. Hero Section
- Animated background with floating teal circles
- Large heading with gradient text
- Smooth scroll to architecture section
- Animated scroll indicator

### 2. Architecture Overview
- Visual system diagram showing all 5 agents
- Interactive agent cards with hover effects
- Flow visualization: Client → Master → Pub/Sub → Workers → Database
- Color-coded by agent type

### 3. Agent Deep Dive
- Tabbed interface to explore each agent
- Detailed workflow steps (numbered)
- Key features and capabilities
- Technology dependencies
- Smooth transitions between agents

### 4. Data Flow
- Toggle between Ingestion Flow and Chat Query Flow
- Step-by-step visualization with icons
- Horizontal flow on desktop, vertical on mobile
- Animated arrows between steps
- Key architectural concepts highlighted

### 5. Technology Stack
- 6 categories: Core Framework, Data Layer, AI & ML, Infrastructure, Messaging, Security
- Technology cards with descriptions
- Architecture benefits grid
- Performance statistics
- Production-ready CTA

## 🎭 Animations

### Custom Animations
- `animate-float`: Floating effect (6s loop)
- `animate-float-delayed`: Delayed floating (6s loop, 2s delay)
- `animate-slide-up`: Slide up with fade-in (0.8s)
- `animate-fade-in`: Simple fade-in (1s)
- `animate-scale-in`: Scale up with fade-in (0.6s)
- `animate-pulse-slow`: Slow pulsing effect (3s loop)

### Intersection Observer
- Sections animate in when scrolled into view
- Staggered delays for multiple elements
- Smooth opacity and transform transitions

## 🎨 Color Palette

```css
--teal-50: #f0fdfa   /* Lightest backgrounds */
--teal-100: #ccfbf1  /* Light backgrounds */
--teal-200: #99f6e4  /* Subtle accents */
--teal-300: #5eead4  /* Borders, highlights */
--teal-400: #2dd4bf  /* Secondary elements */
--teal-500: #14b8a6  /* Primary brand color */
--teal-600: #0d9488  /* Primary buttons, links */
--teal-700: #0f766e  /* Hover states */
--teal-800: #115e59  /* Dark accents */
--teal-900: #134e4a  /* Darkest elements */
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Development
Open [http://localhost:3000](http://localhost:3000) to see the website.

## 📁 Project Structure

```
web/
├── src/
│   ├── app/
│   │   ├── globals.css       # Custom animations & teal palette
│   │   ├── layout.tsx        # Root layout with metadata
│   │   └── page.tsx          # Main page composition
│   └── components/
│       ├── Hero.tsx          # Hero section with animations
│       ├── Architecture.tsx  # System architecture diagram
│       ├── AgentDetails.tsx  # Detailed agent information
│       ├── DataFlow.tsx      # Request/response flow visualization
│       └── TechStack.tsx     # Technology stack & benefits
├── public/                   # Static assets
├── package.json
└── README.md
```

## 🎯 Key Features

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Adaptive layouts for all screen sizes

### Performance
- Next.js 15 with App Router
- Optimized animations with CSS
- Lazy loading with Intersection Observer
- Minimal JavaScript bundle

### Accessibility
- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- High contrast ratios

## 🛠️ Technologies

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS 4**: Utility-first styling
- **Lucide React**: Beautiful icon library
- **React Hooks**: Modern state management

## 🎨 Customization

### Changing Colors
Edit `src/app/globals.css` to modify the teal palette:

```css
:root {
  --teal-500: #your-color;
  /* ... other shades */
}
```

### Adding Sections
1. Create new component in `src/components/`
2. Import in `src/app/page.tsx`
3. Add to page composition

### Modifying Animations
Edit animation keyframes in `src/app/globals.css`:

```css
@keyframes yourAnimation {
  from { /* start state */ }
  to { /* end state */ }
}
```

## 📊 Content Focus

This website exclusively covers:
- ✅ Master Agent (LangGraph orchestration)
- ✅ Ingest Agent (conversation processing)
- ✅ Chat Agent (query responses)
- ✅ Analytics Agent (metrics & stats)
- ✅ Pub/Sub Service (message bus)
- ✅ System architecture & data flow
- ✅ Technology stack & benefits

**Not included:**
- ❌ API demos or interactive features
- ❌ User authentication
- ❌ Backend integration
- ❌ Data visualization dashboards

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Deploy to Vercel
npx vercel

# Or connect GitHub repo to Vercel dashboard
```

### Other Platforms
```bash
# Build static export
npm run build

# Output in .next/ directory
```

## 📝 License

Part of the Agentic Workflow System suite.
