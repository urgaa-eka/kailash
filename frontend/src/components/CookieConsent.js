import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './CookieConsent.css';

const CookieConsent = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState({
    necessary: true, // Always true, cannot be disabled
    functional: false,
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    // Check if user has already made a choice
    const cookieConsent = localStorage.getItem('kailash_cookie_consent');
    if (!cookieConsent) {
      // Delay showing banner slightly for better UX
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAcceptAll = () => {
    const consentData = {
      necessary: true,
      functional: true,
      analytics: true,
      marketing: true,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('kailash_cookie_consent', JSON.stringify(consentData));
    setIsVisible(false);
  };

  const handleRejectAll = () => {
    const consentData = {
      necessary: true, // Always required
      functional: false,
      analytics: false,
      marketing: false,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('kailash_cookie_consent', JSON.stringify(consentData));
    setIsVisible(false);
  };

  const handleSavePreferences = () => {
    const consentData = {
      ...preferences,
      necessary: true, // Ensure necessary is always true
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('kailash_cookie_consent', JSON.stringify(consentData));
    setIsVisible(false);
    setShowPreferences(false);
  };

  const handlePreferenceChange = (type) => {
    if (type === 'necessary') return; // Cannot disable necessary cookies
    setPreferences((prev) => ({
      ...prev,
      [type]: !prev[type],
    }));
  };

  if (!isVisible) return null;

  return (
    <div className="cookie-consent-overlay">
      <div className={`cookie-consent-banner ${showPreferences ? 'expanded' : ''}`}>
        {!showPreferences ? (
          // Simple View
          <>
            <div className="cookie-content">
              <div className="cookie-icon"></div>
              <div className="cookie-text">
                <h3>We Value Your Privacy</h3>
                <p>
                  We use cookies to enhance your browsing experience, provide personalized content, and analyze our traffic.
                  By clicking "Accept All", you consent to our use of cookies.{' '}
                  <Link to="/cookie-policy" className="cookie-link">Learn more</Link>
                </p>
              </div>
            </div>
            <div className="cookie-actions">
              <button className="btn-customize" onClick={() => setShowPreferences(true)}>
                Customize
              </button>
              <button className="btn-reject" onClick={handleRejectAll}>
                Reject All
              </button>
              <button className="btn-accept" onClick={handleAcceptAll}>
                Accept All
              </button>
            </div>
          </>
        ) : (
          // Preferences View
          <>
            <div className="cookie-preferences-header">
              <h3>Cookie Preferences</h3>
              <button className="btn-close" onClick={() => setShowPreferences(false)}>
                ×
              </button>
            </div>
            <div className="cookie-preferences-content">
              {/* Necessary Cookies */}
              <div className="cookie-category">
                <div className="category-header">
                  <div className="category-info">
                    <h4>Necessary Cookies</h4>
                    <p>Essential for the website to function properly. Cannot be disabled.</p>
                  </div>
                  <label className="toggle-switch disabled">
                    <input type="checkbox" checked={true} disabled />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              {/* Functional Cookies */}
              <div className="cookie-category">
                <div className="category-header">
                  <div className="category-info">
                    <h4>Functional Cookies</h4>
                    <p>Remember your preferences and personalize your experience.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={preferences.functional}
                      onChange={() => handlePreferenceChange('functional')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              {/* Analytics Cookies */}
              <div className="cookie-category">
                <div className="category-header">
                  <div className="category-info">
                    <h4>Analytics Cookies</h4>
                    <p>Help us understand how visitors interact with our website.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={preferences.analytics}
                      onChange={() => handlePreferenceChange('analytics')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              {/* Marketing Cookies */}
              <div className="cookie-category">
                <div className="category-header">
                  <div className="category-info">
                    <h4>Marketing Cookies</h4>
                    <p>Used to deliver personalized advertisements based on your interests.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={preferences.marketing}
                      onChange={() => handlePreferenceChange('marketing')}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>
            </div>
            <div className="cookie-preferences-actions">
              <Link to="/cookie-policy" className="cookie-policy-link">
                View Cookie Policy
              </Link>
              <button className="btn-save-preferences" onClick={handleSavePreferences}>
                Save Preferences
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CookieConsent;
