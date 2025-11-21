import ComingSoonBanner from '@/components/ComingSoonBanner';
import Hero from '@/components/Hero';
import Architecture from '@/components/Architecture';
import AgentDetails from '@/components/AgentDetails';
import TechStack from '@/components/TechStack';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen">
      <ComingSoonBanner />
      <div className="pt-12">
        <Hero />
        <Architecture />
        <AgentDetails />
        <TechStack />
      </div>
      <Footer />
    </div>
  );
}
