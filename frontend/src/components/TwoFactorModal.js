import { useState, useRef, useEffect } from "react";
import { X, Check, Shield } from "lucide-react";
import { Button } from "./UI/button";
import { toast } from "sonner";

export const TwoFactorModal = ({ isOpen, onClose, onVerify }) => {
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [timer, setTimer] = useState(45);
  const [isVerifying, setIsVerifying] = useState(false);
  const inputRefs = useRef([]);

  useEffect(() => {
    if (isOpen && timer > 0) {
      const interval = setInterval(() => setTimer(prev => prev - 1), 1000);
      return () => clearInterval(interval);
    }
  }, [isOpen, timer]);

  useEffect(() => {
    if (isOpen && inputRefs.current[0]) inputRefs.current[0].focus();
  }, [isOpen]);

  const handleChange = (index, value) => {
    if (value.length > 1 || !/^[0-9]*$/.test(value)) return;
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    if (value && index < 5) inputRefs.current[index + 1]?.focus();
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  const handleVerify = async () => {
    const fullCode = code.join("");
    if (fullCode.length !== 6) {
      toast.error("Please enter all 6 digits");
      return;
    }
    setIsVerifying(true);
    const success = await onVerify(fullCode);
    if (success) {
      toast.success("Authentication successful!");
      onClose(); // Close the modal on successful verification
    } else {
      toast.error("Invalid verification code");
      setCode(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    }
    setIsVerifying(false);
  };

  const handleResend = () => {
    setTimer(45);
    setCode(["", "", "", "", "", ""]);
    toast.success("Verification code resent!");
    inputRefs.current[0]?.focus();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center">
      <div className="absolute inset-0 glass-dark" onClick={onClose} />
      <div 
        className="relative bg-white rounded-[20px] p-10 w-[500px] animate-modal-enter" 
        style={{ boxShadow: '0 24px 64px rgba(87, 6, 131, 0.3)' }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="2fa-title"
        aria-describedby="2fa-description"
      >
        <button 
          onClick={onClose} 
          className="absolute top-6 right-6 w-8 h-8 rounded-full bg-[rgba(87,6,131,0.1)] hover:bg-[rgba(87,6,131,0.2)] flex items-center justify-center transition-colors focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-3"
          aria-label="Close modal"
        >
          <X className="w-5 h-5 text-[hsl(var(--g4g-purple))]" strokeWidth={2} />
        </button>
        <div className="text-center mb-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-[hsl(var(--g4g-purple))] to-[hsl(var(--g4g-bright-green))] flex items-center justify-center">
            <Shield className="w-8 h-8 text-white" strokeWidth={2} />
          </div>
          <h2 id="2fa-title" className="text-2xl font-bold text-[hsl(var(--g4g-purple))] mb-2">Two-Factor Authentication</h2>
          <div className="h-px w-32 mx-auto bg-gradient-to-r from-transparent via-[hsl(var(--g4g-purple))] to-transparent mb-3" />
          <p id="2fa-description" className="text-sm text-[hsl(var(--g4g-text-gray))]">Enter the 6-digit code sent to your device</p>
        </div>
        <div className="flex justify-center gap-2 mb-6" role="group" aria-label="Verification code inputs">
          {code.map((digit, index) => (
            <input 
              key={index} 
              ref={el => inputRefs.current[index] = el} 
              type="text" 
              inputMode="numeric" 
              maxLength={1} 
              value={digit} 
              onChange={(e) => handleChange(index, e.target.value)} 
              onKeyDown={(e) => handleKeyDown(index, e)} 
              className="w-[60px] h-[72px] text-center text-2xl font-bold text-[hsl(var(--g4g-purple))] border-2 rounded-xl focus:border-[hsl(var(--g4g-bright-green))] focus:ring-2 focus:ring-[rgba(13,163,78,0.2)] focus:scale-105 transition-all duration-200 font-mono focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-3" 
              style={{ 
                borderColor: 'rgba(87, 6, 131, 0.2)', 
                backgroundColor: digit ? 'rgba(87, 6, 131, 0.05)' : 'transparent' 
              }}
              aria-label={`Digit ${index + 1}`}
            />
          ))}
        </div>
        <Button 
          onClick={handleVerify} 
          disabled={isVerifying || code.join("").length !== 6} 
          className="w-full h-12 text-base font-bold rounded-xl mb-4 transition-all duration-200" 
          style={{ background: 'linear-gradient(135deg, hsl(var(--g4g-bright-green)) 0%, hsl(var(--g4g-green)) 100%)' }}
          aria-busy={isVerifying}
        >
          {isVerifying ? "Verifying..." : (
            <>
              <Check className="w-5 h-5 mr-2" strokeWidth={2} />
              VERIFY & ACCESS
            </>
          )}
        </Button>
        <div className="flex items-center justify-center gap-4 text-sm" role="status" aria-live="polite">
          <span className="text-[hsl(var(--g4g-text-gray))]">
            {timer > 0 ? (
              <>Resend code in <span className="font-bold text-[hsl(var(--g4g-purple))]">0:{timer.toString().padStart(2, '0')}</span></>
            ) : "Code expired"}
          </span>
          <span className="text-[hsl(var(--g4g-gray))]">|</span>
          <button 
            onClick={handleResend} 
            disabled={timer > 0} 
            className="text-[hsl(var(--g4g-purple))] font-medium hover:underline disabled:opacity-50 disabled:cursor-not-allowed focus:outline-2 focus:outline-[hsl(var(--g4g-bright-green))] focus:outline-offset-3"
          >
            Resend
          </button>
        </div>
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-[60px] h-[60px] pointer-events-none">
          <img 
            src="https://customer-assets.emergentagent.com/job_evhub-auth/artifacts/qaougk0e_MASCOT.png" 
            alt="Mascot" 
            className="w-full h-full object-contain animate-mascot-bounce" 
          />
        </div>
      </div>
    </div>
  );
};

export default TwoFactorModal;