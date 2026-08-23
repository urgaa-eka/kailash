import { useState } from "react";
import { User, Eye, EyeOff, Shield, Zap, ArrowRight, Check, Loader2 } from "lucide-react";
import { Button } from "./UI/button";
import { Input } from "./UI/input";
import { Label } from "./UI/label";
import { toast } from "sonner";

export const LoginCardOverlay = ({ onLogin, isLoading }) => {
  const [loginId, setLoginId] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rippleEffect, setRippleEffect] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!loginId) {
      toast.error("Please enter your Login ID");
      return;
    }
    
    // Call backend authentication API
    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          login_id: loginId
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success("Login successful! Access granted.");
        onLogin({ loginId, token: data.access_token, user: data.user });
      } else {
        const error = await response.json();
        toast.error(error.detail || "Invalid Login ID. Access denied.");
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error("Authentication error. Please try again.");
    }
  };

  const handleButtonClick = (e) => {
    const button = e.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setRippleEffect({ x, y });
    setTimeout(() => setRippleEffect(null), 600);
  };

  return (
    <div className="absolute right-4 w-full max-w-[380px] pointer-events-auto z-20" style={{ top: 'calc(8vh + 20px)', bottom: '60px', display: 'flex', alignItems: 'center' }}>
      <div 
        className="p-6 relative w-full" 
        style={{ 
          background: 'rgba(15, 15, 25, 0.95)',
          border: '1px solid rgba(129, 114, 173, 0.3)'
        }}
        role="form"
        aria-labelledby="login-title"
      >
        {/* Branding */}
        <div className="text-center mb-4">
          <div className="text-xs font-semibold text-[#8172AD] tracking-[0.15em] mb-1">Go4Garage CHARGING POINT</div>
          <div className="flex items-center justify-center gap-2 mb-1">
            <h1 className="text-[24px] font-bold bg-gradient-to-r from-[#8172AD] via-[#DF8C4D] to-[#8172AD] bg-clip-text text-transparent">Kailash</h1>
            <h1 className="text-[24px] font-bold text-[#8172AD]">HUB</h1>
          </div>
          <div className="h-0.5 w-20 mx-auto mb-2 bg-gradient-to-r from-[#8172AD] via-[#4CAF50] to-[#DF8C4D]" />
          <p className="text-[10px] text-white font-bold">KAILASH "THE DEVINE AI"</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Login ID */}
          <div className="space-y-1">
            <Label htmlFor="loginId" className="flex items-center gap-2 text-[#8172AD] font-semibold text-xs">
              <User className="w-3.5 h-3.5" strokeWidth={1.5} />
              Login ID
            </Label>
            <div className="relative group">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 transition-colors group-focus-within:text-[#8172AD]" strokeWidth={1.5} />
              <Input 
                id="loginId" 
                type="text" 
                value={loginId} 
                onChange={(e) => setLoginId(e.target.value)} 
                className="h-10 pl-10 pr-3 bg-[rgba(30,30,45,0.8)] border border-[rgba(129,114,173,0.3)] text-white placeholder:text-gray-500 focus:border-[#8172AD]" 
                style={{ borderRadius: '0' }} 
                placeholder="Enter your login ID" 
              />
            </div>
          </div>

          {/* Submit Button */}
          <Button 
            type="submit" 
            disabled={isLoading} 
            onClick={handleButtonClick}
            className="w-full h-10 text-sm font-bold relative overflow-hidden transition-all duration-200 hover:opacity-90 disabled:opacity-70 disabled:cursor-not-allowed group"
            style={{ 
              background: 'linear-gradient(135deg, #8172AD 0%, #4CAF50 100%)',
              borderRadius: '0'
            }}
            aria-busy={isLoading}
          >
            {/* Ripple effect */}
            {rippleEffect && (
              <span
                className="absolute bg-white/30 animate-ping"
                style={{
                  left: rippleEffect.x,
                  top: rippleEffect.y,
                  width: '20px',
                  height: '20px',
                  transform: 'translate(-50%, -50%)'
                }}
              />
            )}
            
            {/* Button content */}
            <span className="relative z-10 flex items-center justify-center gap-2">
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} />
                  <span>VALIDATING...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" strokeWidth={1.5} />
                  <span>ACCESS Kailash</span>
                  <ArrowRight className="w-4 h-4" strokeWidth={1.5} />
                </>
              )}
            </span>
          </Button>
        </form>

        {/* Security Badge - Compact */}
        <div className="mt-3 p-2 border-l-2 border-[#4CAF50] bg-[rgba(76,175,80,0.1)]">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#4CAF50]" strokeWidth={2} />
            <span className="text-xs text-gray-400">Secured Access</span>
          </div>
          <div className="mt-1 flex items-center gap-3 text-[10px] text-gray-500">
            <span className="flex items-center gap-1">
              <Check className="w-3 h-3 text-[#4CAF50]" strokeWidth={2.5} />
              Enterprise encryption
            </span>
            <span className="flex items-center gap-1">
              <Check className="w-3 h-3 text-[#4CAF50]" strokeWidth={2.5} />
              60 min timeout
            </span>
          </div>
        </div>

        {/* Forgot Password */}
        <div className="mt-2 text-right">
          <button 
            type="button" 
            className="text-[10px] text-gray-500 hover:text-[#8172AD] font-medium transition-colors"
          >
            Forgot Decode? <ArrowRight className="inline w-2.5 h-2.5 ml-0.5" strokeWidth={2} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginCardOverlay;