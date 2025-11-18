# DataAlchemist Website

A modern Next.js website showcasing the DataAlchemist Customer Conversation Knowledge Engine API.

## Features

- **Modern Design**: Built with Next.js 15, TypeScript, and Tailwind CSS
- **Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Demo**: Live API integration to test endpoints
- **API Documentation**: Clear documentation of all available endpoints
- **Performance Optimized**: Fast loading with modern web standards

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## API Integration

The website integrates with the DataAlchemist API at `https://api.datalchemist.clestiq.com`:

- **Ingest Endpoint**: `POST /api/v1/ingest` - Upload conversation data
- **Chat Endpoint**: `POST /api/v1/chat` - Query the knowledge base
- **Health Check**: `GET /health` - Monitor API status

## Project Structure

```
website/
├── src/
│   ├── app/                 # Next.js app router
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Home page
│   ├── components/          # React components
│   │   ├── Hero.tsx         # Hero section
│   │   ├── Features.tsx     # Features grid
│   │   ├── HowItWorks.tsx   # Process steps
│   │   ├── ApiDocs.tsx      # API documentation
│   │   ├── Demo.tsx         # Static demo examples
│   │   ├── InteractiveDemo.tsx # Live API demo
│   │   └── Footer.tsx       # Footer component
│   └── lib/
│       └── api.ts           # API client and types
├── public/                  # Static assets
└── package.json
```

## Customization

### Styling
- Uses Tailwind CSS for styling
- Custom colors and animations defined in components
- Responsive design with mobile-first approach

### API Configuration
- API base URL configured in `src/lib/api.ts`
- Easy to switch between development and production endpoints
- Type-safe API client with TypeScript interfaces

### Content Updates
- All content is in React components for easy editing
- Sample data and examples in `src/lib/api.ts`
- Metadata and SEO settings in `src/app/layout.tsx`

## Deployment

### Vercel (Recommended)
```bash
# Deploy to Vercel
npx vercel

# Or connect your GitHub repo to Vercel dashboard
```

### Other Platforms
```bash
# Build static export (if needed)
npm run build
npm run export
```

## Technologies Used

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **React Hooks**: Modern React patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the DataAlchemist suite.