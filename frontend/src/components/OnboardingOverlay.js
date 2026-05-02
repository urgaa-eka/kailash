import { ArrowDown, ArrowRight } from "lucide-react";
import { Button } from "./UI/button";

export const OnboardingOverlay = ({ onComplete }) => {
  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center glass-dark animate-modal-enter"
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
    >
      <div className="text-center text-white space-y-8 max-w-4xl px-8">
        <div>
          <h2 id="onboarding-title" className="text-4xl font-bold mb-3">
            Welcome to Kailash
          </h2>
          <p className="text-lg text-white/80">
            India's Complete EV Infrastructure Command Center
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-3xl mx-auto">
          {/* Point to wheel */}
          <div className="flex flex-col items-center text-center space-y-4">
            <div 
              className="w-20 h-20 rounded-full flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, hsl(var(--g4g-purple)), hsl(var(--g4g-green)))' }}
            >
              <ArrowDown className="w-10 h-10 animate-bounce" strokeWidth={2} />
            </div>
            <div>
              <h3 className="text-xl font-bold mb-2">Explore Our Ecosystem</h3>
              <p className="text-white/70 text-sm">
                Interactive wheel showcasing our integrated<br />
                Products, Programs, Services & Intelligence
              </p>
            </div>
          </div>
          
          {/* Point to login */}
          <div className="flex flex-col items-center text-center space-y-4">
            <div 
              className="w-20 h-20 rounded-full flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, hsl(var(--g4g-bright-green)), hsl(var(--g4g-orange)))' }}
            >
              <ArrowRight className="w-10 h-10 animate-bounce" strokeWidth={2} />
            </div>
            <div>
              <h3 className="text-xl font-bold mb-2">Access Command Center</h3>
              <p className="text-white/70 text-sm">
                Secure login with enterprise-grade<br />
                encryption & two-factor authentication
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col items-center gap-4 pt-4">
          <Button
            onClick={onComplete}
            className="px-8 py-6 text-lg font-bold rounded-xl"
            style={{ background: 'linear-gradient(135deg, hsl(var(--g4g-purple)), hsl(var(--g4g-bright-green)))' }}
          >
            Get Started
          </Button>
          <p className="text-xs text-white/50">
            This tutorial won't show again
          </p>
        </div>
      </div>
    </div>
  );
};

export default OnboardingOverlay;