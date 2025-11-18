import Hero from '@/components/Hero';
import Features from '@/components/Features';
import HowItWorks from '@/components/HowItWorks';
import Demo from '@/components/Demo';
import InteractiveDemo from '@/components/InteractiveDemo';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800">
      <Hero />
      <main className="bg-white rounded-t-3xl -mt-12 relative z-10">
        <Features />
        <HowItWorks />
        <Demo />
        <InteractiveDemo />
      </main>
      <Footer />
    </div>
  );
}
