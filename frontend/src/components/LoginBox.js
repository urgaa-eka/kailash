import { useState } from "react";
import { Mail, Lock, Eye, EyeOff, Shield } from "lucide-react";
import { Button } from "./UI/button";
import { Input } from "./UI/input";
import { Label } from "./UI/label";
import { Checkbox } from "./UI/checkbox";
import { toast } from "sonner";

export const LoginBox = ({ onLogin, isLoading }) => {
  const [credentials, setCredentials] = useState({
    username: "",
    password: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

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
    <div 
      className="absolute top-6 right-6 w-[420px] bg-white rounded-2xl p-8"
      style={{ boxShadow: 'var(--shadow-card)' }}
    >
      {/* Title */}
      <div className="text-center mb-6">
        <div className="text-sm font-semibold text-[hsl(var(--g4g-purple))] tracking-wider mb-1">
          CHARGING POINT
        </div>
        <div className="flex items-center justify-center gap-1 mb-2">
          <h1 className="text-[28px] font-bold text-[hsl(var(--g4g-orange))]">Kailash</h1>
          <h1 className="text-[28px] font-bold text-[hsl(var(--g4g-purple))]">HUB</h1>
        </div>
        <div className="h-1 w-24 mx-auto bg-gradient-to-r from-[hsl(var(--g4g-bright-green))] to-[hsl(var(--g4g-green))] rounded-full" />
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email/Username Input */}
        <div className="space-y-2">
          <Label htmlFor="username" className="text-xs font-semibold text-[hsl(var(--g4g-purple))]">
            Email or Username
          </Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[hsl(var(--g4g-gray))]" strokeWidth={1.5} />
            <Input
              id="username"
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="pl-10 h-12 border-2 border-[hsl(var(--g4g-gray))] input-glow transition-all duration-200"
              placeholder="Enter your email or username"
            />
          </div>
        </div>

        {/* Password Input */}
        <div className="space-y-2">
          <Label htmlFor="password" className="text-xs font-semibold text-[hsl(var(--g4g-purple))]">
            Password
          </Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[hsl(var(--g4g-gray))]" strokeWidth={1.5} />
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="pl-10 pr-10 h-12 border-2 border-[hsl(var(--g4g-gray))] input-glow transition-all duration-200"
              placeholder="Enter your password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(var(--g4g-gray))] hover:text-[hsl(var(--g4g-purple))] transition-colors"
            >
              {showPassword ? (
                <EyeOff className="w-5 h-5" strokeWidth={1.5} />
              ) : (
                <Eye className="w-5 h-5" strokeWidth={1.5} />
              )}
            </button>
          </div>
        </div>

        {/* Remember Me */}
        <div className="flex items-center space-x-2">
          <Checkbox 
            id="remember" 
            checked={rememberMe}
            onCheckedChange={setRememberMe}
            className="border-[hsl(var(--g4g-purple))] data-[state=checked]:bg-[hsl(var(--g4g-purple))] data-[state=checked]:text-[hsl(var(--g4g-bright-green))]"
          />
          <label
            htmlFor="remember"
            className="text-sm text-[hsl(var(--g4g-text-gray))] cursor-pointer"
          >
            Remember Me
          </label>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full h-12 text-base font-bold rounded-lg btn-lift transition-all duration-200"
          style={{ background: 'var(--gradient-primary)' }}
        >
          <Shield className="w-5 h-5 mr-2" strokeWidth={2} />
          {isLoading ? "VALIDATING..." : "ACCESS Kailash"}
        </Button>
      </form>

      {/* Footer Links */}
      <div className="flex items-center justify-between mt-4 text-xs">
        <button 
          type="button"
          className="text-[hsl(var(--g4g-text-gray))] hover:text-[hsl(var(--g4g-purple))] transition-colors"
        >
          Need Help?
        </button>
        <button 
          type="button"
          className="text-[hsl(var(--g4g-purple))] hover:underline font-medium"
        >
          Forgot Password?
        </button>
      </div>
    </div>
  );
};

export default LoginBox;