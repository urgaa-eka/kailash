import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import MinimalHeader from "../components/MinimalHeader";
import LoginCardOverlay from "../components/LoginCardOverlay";
import VideoBackground from "../components/VideoBackground";
import MinimalFooter from "../components/MinimalFooter";
import TwoFactorModal from "../components/TwoFactorModal";
import OnboardingOverlay from "../components/OnboardingOverlay";
import LoadingState from "../components/LoadingState";

export const LoginPage = () => {
  const [show2FA, setShow2FA] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isFirstVisit, setIsFirstVisit] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if first visit
    const hasVisited = localStorage.getItem('kailash_has_visited');
    if (!hasVisited) {
      setIsFirstVisit(true);
    }
    
    // Simulate initialization
    const timer = setTimeout(() => {
      setIsInitializing(false);
    }, 2000);
    
    return () => clearTimeout(timer);
  }, []);

  const handleLogin = async (credentials) => {
    setIsLoading(true);
    
    if (isFirstVisit) {
      localStorage.setItem('kailash_has_visited', 'true');
      setIsFirstVisit(false);
    }
    
    if (credentials.token && credentials.user) {
      const user = credentials.user;
      const has2FAEnabled = user.two_factor_enabled || user.is_2fa_enabled || false;
      
      if (has2FAEnabled) {
        sessionStorage.setItem('temp_token', credentials.token);
        sessionStorage.setItem('temp_user', JSON.stringify(user));
        setIsLoading(false);
        setShow2FA(true);
      } else {
        const authData = {
          'kailash-auth': JSON.stringify({
            state: {
              accessToken: credentials.token,
              refreshToken: credentials.token,
              user: user,
              isAuthenticated: true,
              is2FAEnabled: false
            },
            version: 0
          })
        };
        
        Object.entries(authData).forEach(([key, value]) => {
          localStorage.setItem(key, value);
        });
        localStorage.setItem('token', credentials.token);
        localStorage.setItem('user', JSON.stringify(user));
        
        const expiry = Date.now() + (60 * 60 * 1000);
        localStorage.setItem('sessionExpiry', expiry.toString());
        
        setIsLoading(false);
        navigate('/dashboard');
      }
    } else {
      setIsLoading(false);
    }
  };

  const handle2FAVerify = async (code) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (code.length === 6) {
      // Get the real token from sessionStorage
      const token = sessionStorage.getItem('temp_token');
      const userStr = sessionStorage.getItem('temp_user');
      
      if (token && userStr) {
        const user = JSON.parse(userStr);
        
        // Store in auth store for the app to use
        const authData = {
          'kailash-auth': JSON.stringify({
            state: {
              accessToken: token,
              refreshToken: token,
              user: user,
              isAuthenticated: true,
              is2FAEnabled: user.is_2fa_enabled || false
            },
            version: 0
          })
        };
        
        localStorage.setItem('kailash-auth', authData['kailash-auth']);
        
        // Also set simple token for backward compatibility
        localStorage.setItem('token', token);
        
        // Clean up temp storage
        sessionStorage.removeItem('temp_token');
        sessionStorage.removeItem('temp_user');
      } else {
        // Fallback to mock token
        localStorage.setItem('token', 'jwt-token-' + Date.now());
      }
      
      setTimeout(() => {
        navigate("/dashboard");
      }, 500);
      return true;
    }
    return false;
  };

  const handleOnboardingComplete = () => {
    localStorage.setItem('kailash_has_visited', 'true');
    setIsFirstVisit(false);
  };

  if (isInitializing) {
    return <LoadingState />;
  }

  return (
    <div className="h-[100dvh] w-screen overflow-hidden flex flex-col bg-[#0a0a1a]">
      {/* Skip to main content */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      
      {/* Minimal Header - 8vh with dark theme */}
      <MinimalHeader />
      
      {/* Main L-Shaped Area - 92vh minus footer */}
      <main id="main-content" className="flex-1 relative overflow-hidden">
        {/* High-Quality Video Background */}
        <VideoBackground />
        
        {/* Top-Right Login Card */}
        <LoginCardOverlay onLogin={handleLogin} isLoading={isLoading} />
      </main>
      
      {/* Enhanced Footer */}
      <MinimalFooter />
      
      {/* 2FA Modal */}
      {show2FA && (
        <TwoFactorModal
          isOpen={show2FA}
          onClose={() => setShow2FA(false)}
          onVerify={handle2FAVerify}
        />
      )}
      
      {/* Onboarding Overlay */}
      {isFirstVisit && (
        <OnboardingOverlay onComplete={handleOnboardingComplete} />
      )}
    </div>
  );
};

export default LoginPage;