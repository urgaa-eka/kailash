import React from 'react';
import './LegalPages.css';

const CookiePolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Cookie Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. What Are Cookies</h2>
            <p>
              Cookies are small text files stored on your device when you visit our website. They help us provide
              a better user experience, remember your preferences, and analyze site performance.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Types of Cookies We Use</h2>
            <h3>2.1 Essential Cookies</h3>
            <p>These cookies are necessary for the website to function:</p>
            <ul>
              <li><strong>Session Cookies:</strong> Keep you logged in during your visit</li>
              <li><strong>Security Cookies:</strong> Protect against fraud and unauthorized access</li>
              <li><strong>Load Balancing:</strong> Distribute traffic across servers</li>
            </ul>

            <h3>2.2 Performance Cookies</h3>
            <p>These help us understand how visitors use our site:</p>
            <ul>
              <li><strong>Analytics:</strong> Google Analytics, Mixpanel for usage statistics</li>
              <li><strong>Error Tracking:</strong> Identify and fix technical issues</li>
              <li><strong>Speed Metrics:</strong> Monitor page load times</li>
            </ul>

            <h3>2.3 Functional Cookies</h3>
            <p>These remember your preferences:</p>
            <ul>
              <li><strong>Language Settings:</strong> Remember your preferred language</li>
              <li><strong>Theme Preferences:</strong> Dark mode or light mode settings</li>
              <li><strong>Consent Preferences:</strong> Remember your cookie choices</li>
            </ul>

            <h3>2.4 Targeting/Advertising Cookies</h3>
            <p>These deliver relevant advertisements:</p>
            <ul>
              <li><strong>Ad Networks:</strong> Google Ads, Facebook Pixel</li>
              <li><strong>Retargeting:</strong> Show relevant ads based on your interests</li>
              <li><strong>Conversion Tracking:</strong> Measure ad campaign effectiveness</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Cookie Details</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Cookie Name</th>
                  <th>Purpose</th>
                  <th>Duration</th>
                  <th>Type</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>kailash_session</td>
                  <td>Session management</td>
                  <td>Session</td>
                  <td>Essential</td>
                </tr>
                <tr>
                  <td>kailash_auth_token</td>
                  <td>Authentication</td>
                  <td>7 days</td>
                  <td>Essential</td>
                </tr>
                <tr>
                  <td>kailash_preferences</td>
                  <td>User preferences</td>
                  <td>1 year</td>
                  <td>Functional</td>
                </tr>
                <tr>
                  <td>_ga</td>
                  <td>Google Analytics</td>
                  <td>2 years</td>
                  <td>Performance</td>
                </tr>
                <tr>
                  <td>_fbp</td>
                  <td>Facebook Pixel</td>
                  <td>3 months</td>
                  <td>Targeting</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>4. Managing Your Cookie Preferences</h2>
            <p>You have several options to control cookies:</p>
            <ul>
              <li><strong>Cookie Banner:</strong> Accept or decline non-essential cookies on first visit</li>
              <li><strong>Browser Settings:</strong> Block or delete cookies through your browser</li>
              <li><strong>Opt-Out Tools:</strong> Use industry opt-out tools like NAI or DAA</li>
              <li><strong>Do Not Track:</strong> Enable DNT signals in your browser</li>
            </ul>

            <h3>4.1 Browser-Specific Instructions</h3>
            <ul>
              <li><strong>Chrome:</strong> Settings > Privacy and Security > Cookies</li>
              <li><strong>Firefox:</strong> Options > Privacy & Security > Cookies</li>
              <li><strong>Safari:</strong> Preferences > Privacy > Cookies</li>
              <li><strong>Edge:</strong> Settings > Privacy > Cookies</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Third-Party Cookies</h2>
            <p>We use services from third parties that may set their own cookies:</p>
            <ul>
              <li><strong>Google Analytics:</strong> <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Privacy Policy</a></li>
              <li><strong>Facebook:</strong> <a href="https://www.facebook.com/policy/cookies/" target="_blank" rel="noopener noreferrer">Cookie Policy</a></li>
              <li><strong>Stripe:</strong> <a href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer">Privacy Policy</a></li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Impact of Disabling Cookies</h2>
            <p>Disabling cookies may affect functionality:</p>
            <ul>
              <li>You may need to log in repeatedly</li>
              <li>Personalization features may not work</li>
              <li>Some features may be unavailable</li>
              <li>Website performance may be degraded</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Updates to This Policy</h2>
            <p>
              We may update this Cookie Policy periodically. Changes will be posted on this page with
              an updated revision date.
            </p>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For questions, contact: privacy@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default CookiePolicy;
