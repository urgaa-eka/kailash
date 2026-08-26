import { useState } from "react";
import { User, Lock, Eye, EyeOff, Shield, Zap, ArrowRight, Check } from "lucide-react";
import { Button } from "./UI/button";
import { Input } from "./UI/input";
import { Label } from "./UI/label";
import { toast } from "sonner";

export const LoginCard = ({ onLogin, isLoading }) => {
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!credentials.username || !credentials.password) {
      toast.error("Please enter both username and password");
      return;
    }
    toast.success("Credentials validated!");
    onLogin(credentials);
  };

  return (
    <div className="absolute inset-0 flex items-start justify-end p-6 pointer-events-none">
      <div className="glass border rounded-[20px] p-12 w-full max-w-[480px] pointer-events-auto" style={{ borderColor: 'rgba(87, 6, 131, 0.1)', boxShadow: '0 8px 32px rgba(87, 6, 131, 0.12), inset 0 0 0 1px rgba(87, 6, 131, 0.05)' }}>
        {/* Branding */}
        <div className="text-center mb-6">
          <div className="text-sm font-semibold text-[hsl(var(--g4g-purple))] tracking-[0.15em] mb-1">CHARGING POINT</div>
          <div className="flex items-center justify-center gap-2 mb-2">
            <h1 className="text-[32px] font-bold bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-orange))] to-[hsl(var(--g4g-purple))] bg-clip-text text-transparent">Kailash</h1>
            <h1 className="text-[32px] font-bold text-[hsl(var(--g4g-purple))]">HUB</h1>
          </div>
          <div className="h-0.5 w-32 mx-auto mb-3 bg-gradient-to-r from-[hsl(var(--g4g-purple))] via-[hsl(var(--g4g-green))] to-[hsl(var(--g4g-orange))] animate-underline-cycle" />
          <p className="text-[13px] text-[hsl(var(--g4g-purple-light))] italic">AI-Powered Charging Infrastructure Management</p>
        </div>

        {/* Form Header */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-[hsl(var(--g4g-purple))] mb-1">Welcome to Kailash</h2>
          <p className="text-sm text-[hsl(var(--g4g-text-gray))]">Access Your Charging Command Center</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Kailash Code */}
          <div className="space-y-2">
            <Label htmlFor="username" className="flex items-center gap-2 text-[hsl(var(--g4g-purple))] font-semibold text-xs">
              <User className="w-4 h-4" strokeWidth={1.5} />
              Kailash Code
            </Label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[hsl(var(--g4g-gray))]" strokeWidth={1.5} />
              <Input id="username" type="text" value={credentials.username} onChange={(e) => setCredentials({...credentials, username: e.target.value})} className="h-[52px] pl-12 pr-4 border-2 input-glow transition-all duration-200" style={{ borderColor: 'rgba(87, 6, 131, 0.2)' }} placeholder="Enter your unique code" />
            </div>
          </div>

          {/* Decode */}
          <div className="space-y-2">
            <Label htmlFor="password" className="flex items-center gap-2 text-[hsl(var(--g4g-purple))] font-semibold text-xs">
              <Lock className="w-4 h-4" strokeWidth={1.5} />
              Decode
            </Label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[hsl(var(--g4g-gray))]" strokeWidth={1.5} />
              <Input id="password" type={showPassword ? "text" : "password"} value={credentials.password} onChange={(e) => setCredentials({...credentials, password: e.target.value})} className="h-[52px] pl-12 pr-12 border-2 input-glow transition-all duration-200" style={{ borderColor: 'rgba(87, 6, 131, 0.2)' }} placeholder="Enter your secure key" />
              <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-[hsl(var(--g4g-gray))] hover:text-[hsl(var(--g4g-purple))] transition-colors">
                {showPassword ? <EyeOff className="w-5 h-5" strokeWidth={1.5} /> : <Eye className="w-5 h-5" strokeWidth={1.5} />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <Button type="submit" disabled={isLoading} className="w-full h-14 text-base font-bold rounded-xl btn-lift shimmer relative overflow-hidden" style={{ background: 'linear-gradient(135deg, hsl(var(--g4g-purple)) 0%, hsl(var(--g4g-green)) 60%, hsl(var(--g4g-bright-green)) 100%)' }}>
            <span className="relative z-10 flex items-center justify-center gap-2">
              <Zap className="w-5 h-5" strokeWidth={1.5} />
              {isLoading ? "VALIDATING..." : "ACCESS Kailash"}
              <ArrowRight className="w-5 h-5" strokeWidth={1.5} />
            </span>
          </Button>
        </form>

        {/* Security Badge */}
        <div className="mt-6 rounded-lg p-4" style={{ background: 'linear-gradient(90deg, rgba(13, 163, 78, 0.05), transparent)', borderLeft: '3px solid hsl(var(--g4g-bright-green))' }}>
          <div className="flex items-start gap-3 mb-2">
            <Shield className="w-6 h-6 text-[hsl(var(--g4g-purple))] flex-shrink-0" strokeWidth={1.5} />
            <div>
              <h4 className="font-semibold text-sm text-[hsl(var(--g4g-purple))] mb-1">Secured Access</h4>
              <div className="h-px w-full bg-gradient-to-r from-[hsl(var(--g4g-purple))] to-transparent mb-2" />
              <p className="text-xs text-[hsl(var(--g4g-text-gray))] mb-2">Multi-Factor & AI Agent Validation</p>
            </div>
          </div>
          <div className="space-y-1 ml-9">
            <div className="flex items-center gap-2 text-xs text-[hsl(var(--g4g-text-gray))]">
              <Check className="w-3 h-3 text-[hsl(var(--g4g-bright-green))]" strokeWidth={2} />
              Enterprise-grade encryption
            </div>
            <div className="flex items-center gap-2 text-xs text-[hsl(var(--g4g-text-gray))]">
              <Check className="w-3 h-3 text-[hsl(var(--g4g-bright-green))]" strokeWidth={2} />
              Session timeout: 60 minutes
            </div>
          </div>
        </div>

        {/* Forgot Password */}
        <div className="mt-4 text-right">
          <button type="button" className="text-sm text-[hsl(var(--g4g-purple))] hover:underline font-medium transition-colors">Forgot Decode?</button>
        </div>

        {/* Mascot peek */}
        <div className="absolute -bottom-5 -right-5 w-20 h-20 animate-mascot-bounce pointer-events-none" style={{ filter: 'drop-shadow(0 4px 12px rgba(87, 6, 131, 0.2))' }}>
          <img src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png" alt="Mascot" className="w-full h-full object-contain" />
        </div>
      </div>
    </div>
  );
};

export default LoginCard;