import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Clock, RefreshCw } from 'lucide-react';

const SESSION_TIMEOUT = 60 * 60 * 1000; // 60 minutes in milliseconds
const WARNING_TIME = 5 * 60 * 1000; // Show warning 5 minutes before timeout

export const SessionTimeout = ({ isAuthenticated }) => {
  const [showWarning, setShowWarning] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const navigate = useNavigate();

  const resetTimer = useCallback(() => {
    const expiry = Date.now() + SESSION_TIMEOUT;
    localStorage.setItem('sessionExpiry', expiry.toString());
    setShowWarning(false);
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('sessionExpiry');
    navigate('/');
    window.location.reload();
  }, [navigate]);

  const extendSession = useCallback(() => {
    resetTimer();
    setShowWarning(false);
  }, [resetTimer]);

  useEffect(() => {
    if (!isAuthenticated) return;

    // Initialize session expiry if not set
    if (!localStorage.getItem('sessionExpiry')) {
      resetTimer();
    }

    const checkSession = () => {
      const expiry = parseInt(localStorage.getItem('sessionExpiry') || '0');
      const now = Date.now();
      const remaining = expiry - now;

      if (remaining <= 0) {
        // Session expired
        handleLogout();
      } else if (remaining <= WARNING_TIME) {
        // Show warning
        setShowWarning(true);
        setTimeLeft(Math.ceil(remaining / 1000));
      } else {
        setShowWarning(false);
      }
    };

    // Check every second
    const interval = setInterval(checkSession, 1000);

    // Reset timer on user activity
    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    const handleActivity = () => {
      if (!showWarning) {
        resetTimer();
      }
    };

    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity);
    });

    return () => {
      clearInterval(interval);
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity);
      });
    };
  }, [isAuthenticated, resetTimer, handleLogout, showWarning]);

  if (!showWarning || !isAuthenticated) return null;

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-2xl p-6 max-w-md mx-4 animate-in fade-in zoom-in duration-300">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Session Expiring Soon</h3>
            <p className="text-sm text-gray-500">Your session will expire due to inactivity</p>
          </div>
        </div>

        <div className="bg-gray-100 rounded-lg p-4 mb-4 text-center">
          <div className="flex items-center justify-center gap-2 text-2xl font-mono font-bold text-gray-800">
            <Clock className="w-6 h-6 text-amber-600" />
            <span>{minutes}:{seconds.toString().padStart(2, '0')}</span>
          </div>
          <p className="text-sm text-gray-500 mt-1">Time remaining</p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleLogout}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
          >
            Logout Now
          </button>
          <button
            onClick={extendSession}
            className="flex-1 px-4 py-2 bg-[#8172AD] text-white rounded-lg hover:bg-[#6d5f9a] transition-colors font-medium flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Stay Logged In
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center mt-4">
          For security, sessions automatically expire after 60 minutes of inactivity
        </p>
      </div>
    </div>
  );
};

export default SessionTimeout;
