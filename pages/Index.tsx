import Navigation from "@/components/Navigation";
import HeroSection from "@/components/HeroSection";
import HowItWorks from "@/components/HowItWorks";
import DemoSection from "@/components/DemoSection";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <HeroSection />
      <HowItWorks />
      <DemoSection />
      <Footer />
    </div>
  );
};

export default Index;
