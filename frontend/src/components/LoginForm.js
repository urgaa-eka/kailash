import { useState } from "react";
import { User, Lock, Shield, Check, Zap, ArrowRight, Loader2 } from "lucide-react";
import { Button } from "./UI/button";
import { Input } from "./UI/input";
import { Label } from "./UI/label";
import { toast } from "sonner";

export const LoginForm = ({ onLogin, isLoading }) => {
  const [credentials, setCredentials] = useState({
    kailashCode: "",
    decode: ""
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!credentials.kailashCode || !credentials.decode) {
      toast.error("Please enter both Kailash Code and Decode");
      return;
    }
    
    toast.success("Credentials validated!");
    onLogin(credentials);
  };

  return (
    <div className="w-full max-w-[480px] animate-slide-up" style={{ animationDelay: "300ms" }}>
      {/* Branding */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-2">
          <div className="text-sm font-semibold text-[hsl(var(--g4g-purple))] tracking-[0.15em]">CHARGING POINT</div>
        </div>
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="h-px w-16 bg-gradient-to-r from-transparent via-[hsl(var(--g4g-purple))] to-[hsl(var(--g4g-bright-green))] animate-gradient-slide" />
        </div>
        <h1 className="text-4xl font-bold mb-2">
          <span className="bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-orange))] to-[hsl(var(--g4g-purple))] bg-clip-text text-transparent animate-gradient-slide">Kailash</span>
          {" "}
          <span className="text-[hsl(var(--g4g-purple))]">HUB</span>
        </h1>
        <div className="h-0.5 w-32 mx-auto bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-green))] to-[hsl(var(--g4g-orange))] animate-gradient-slide rounded-full" />
        <p className="text-sm text-[hsl(var(--g4g-purple))] italic mt-3">AI-Powered Charging Infrastructure Management</p>
      </div>

      {/* Login Card */}
      <div className="glass border border-[hsl(var(--g4g-purple)_/_0.1)] rounded-[20px] p-12 relative"
           style={{ boxShadow: 'var(--shadow-elegant), inset 0 0 0 1px hsl(var(--g4g-purple) / 0.05)' }}>
        
        {/* Form Header */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-[hsl(var(--g4g-purple))] mb-2">Welcome to Kailash</h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Access Your Charging Command Center</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Kailash Code Input */}
          <div className="space-y-2">
            <Label htmlFor="kailashCode" className="flex items-center gap-2 text-[hsl(var(--g4g-purple))] font-semibold">
              <User className="w-4 h-4" strokeWidth={2} />
              Kailash Code
            </Label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[hsl(var(--g4g-purple)_/_0.5)]" strokeWidth={1.5} />
              <Input
                id="kailashCode"
                type="text"
                placeholder="Enter your unique code"
                value={credentials.kailashCode}
                onChange={(e) => setCredentials({...credentials, kailashCode: e.target.value})}
                className="h-[52px] pl-12 pr-4 border-2 border-[hsl(var(--g4g-purple)_/_0.2)] rounded-lg focus:border-[hsl(var(--g4g-purple))] focus:ring-2 focus:ring-[hsl(var(--g4g-purple)_/_0.1)] transition-all duration-200"
              />
            </div>
          </div>

          {/* Decode Input */}
          <div className="space-y-2">
            <Label htmlFor="decode" className="flex items-center gap-2 text-[hsl(var(--g4g-purple))] font-semibold">
              <Lock className="w-4 h-4" strokeWidth={2} />
              Decode
            </Label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[hsl(var(--g4g-purple)_/_0.5)]" strokeWidth={1.5} />
              <Input
                id="decode"
                type="password"
                placeholder="Enter your secure key"
                value={credentials.decode}
                onChange={(e) => setCredentials({...credentials, decode: e.target.value})}
                className="h-[52px] pl-12 pr-4 border-2 border-[hsl(var(--g4g-purple)_/_0.2)] rounded-lg focus:border-[hsl(var(--g4g-purple))] focus:ring-2 focus:ring-[hsl(var(--g4g-purple)_/_0.1)] transition-all duration-200"
              />
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-14 text-base font-bold rounded-xl relative overflow-hidden group"
            style={{
              background: 'var(--gradient-primary)',
              boxShadow: '0 4px 20px hsl(var(--g4g-purple) / 0.3)'
            }}
          >
            {/* Shimmer overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 ease-out" />
            
            {/* Button content */}
            <span className="relative flex items-center justify-center gap-2">
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" strokeWidth={2} />
                  Validating...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" strokeWidth={2} />
                  ACCESS Kailash
                  <ArrowRight className="w-5 h-5" strokeWidth={2} />
                </>
              )}
            </span>
          </Button>
        </form>

        {/* Security Badge */}
        <div className="mt-6 rounded-lg p-4 border-l-3 border-[hsl(var(--g4g-bright-green))]" 
             style={{ 
               background: 'linear-gradient(90deg, hsl(var(--g4g-bright-green) / 0.05), transparent)',
               borderLeft: '3px solid hsl(var(--g4g-bright-green))'
             }}>
          <div className="flex items-start gap-3 mb-3">
            <Shield className="w-6 h-6 text-[hsl(var(--g4g-purple))] flex-shrink-0" strokeWidth={1.5} />
            <div>
              <h4 className="font-semibold text-sm text-[hsl(var(--g4g-purple))] mb-1">Secured Access</h4>
              <div className="h-px w-full bg-gradient-to-r from-[hsl(var(--g4g-purple))] to-transparent mb-2" />
              <p className="text-xs text-[hsl(var(--muted-foreground))] mb-2">Multi-Factor & AI Agent Validation</p>
            </div>
          </div>
          <div className="space-y-1 ml-9">
            <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
              <Check className="w-3 h-3 text-[hsl(var(--g4g-bright-green))]" strokeWidth={2} />
              Enterprise-grade encryption
            </div>
            <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
              <Check className="w-3 h-3 text-[hsl(var(--g4g-bright-green))]" strokeWidth={2} />
              Session timeout: 60 minutes
            </div>
          </div>
        </div>

        {/* Forgot Password */}
        <div className="mt-4 text-right">
          <button 
            type="button"
            className="text-sm text-[hsl(var(--g4g-purple)_/_0.7)] hover:text-[hsl(var(--g4g-purple))] transition-colors duration-200 font-medium"
          >
            Forgot Decode? <ArrowRight className="inline w-3 h-3 ml-1" strokeWidth={2} />
          </button>
        </div>

        {/* Mascot */}
        <div className="absolute -bottom-5 -right-5 w-20 h-20 animate-bounce-mascot cursor-pointer hover:scale-110 transition-transform duration-300"
             style={{ filter: 'drop-shadow(0 4px 12px hsl(var(--g4g-purple) / 0.2))' }}>
          
        </div>
      </div>
    </div>
  );
};

export default LoginForm;