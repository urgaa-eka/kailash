import React from 'react';
import { Link } from 'react-router-dom';
import './LegalFooter.css';

const LegalFooter = () => {
  return (
    <footer className="legal-footer-container">
      <div className="legal-footer-content">
        {/* Column 1: General Legal */}
        <div className="footer-column">
          <h3>Legal</h3>
          <ul>
            <li><Link to="/terms">Terms & Conditions</Link></li>
            <li><Link to="/privacy">Privacy Policy</Link></li>
            <li><Link to="/cookie-policy">Cookie Policy</Link></li>
            <li><Link to="/disclaimer">Disclaimer</Link></li>
            <li><Link to="/acceptable-use">Acceptable Use Policy</Link></li>
            <li><Link to="/intellectual-property">Intellectual Property</Link></li>
            <li><Link to="/dmca">DMCA Policy</Link></li>
            <li><Link to="/age-restriction">Age Restriction</Link></li>
          </ul>
        </div>

        {/* Column 2: Data & Privacy */}
        <div className="footer-column">
          <h3>Data & Privacy</h3>
          <ul>
            <li><Link to="/gdpr-compliance">GDPR Compliance</Link></li>
            <li><Link to="/ccpa-compliance">CCPA Compliance</Link></li>
            <li><Link to="/data-retention">Data Retention Policy</Link></li>
            <li><Link to="/data-breach">Data Breach Policy</Link></li>
            <li><Link to="/data-transfer">Data Transfer Policy</Link></li>
            <li><Link to="/subprocessors">Subprocessor List</Link></li>
            <li><Link to="/user-rights">User Rights</Link></li>
          </ul>
        </div>

        {/* Column 3: Services & Operations */}
        <div className="footer-column">
          <h3>Services</h3>
          <ul>
            <li><Link to="/sla">Service Level Agreement</Link></li>
            <li><Link to="/refund-policy">Refund Policy</Link></li>
            <li><Link to="/shipping-policy">Shipping Policy</Link></li>
            <li><Link to="/warranty-policy">Warranty Policy</Link></li>
            <li><Link to="/api-terms">API Terms</Link></li>
            <li><Link to="/oemsg">OEMSG Registration</Link></li>
          </ul>
        </div>

        {/* Column 4: Community & Guidelines */}
        <div className="footer-column">
          <h3>Community</h3>
          <ul>
            <li><Link to="/community-guidelines">Community Guidelines</Link></li>
            <li><Link to="/moderator-guidelines">Moderator Guidelines</Link></li>
            <li><Link to="/code-of-conduct">Code of Conduct</Link></li>
            <li><Link to="/ethics">Ethics & Values</Link></li>
          </ul>
        </div>

        {/* Column 5: Security & Compliance */}
        <div className="footer-column">
          <h3>Security</h3>
          <ul>
            <li><Link to="/security-policy">Security Policy</Link></li>
            <li><Link to="/incident-response">Incident Response</Link></li>
            <li><Link to="/penetration-testing">Penetration Testing</Link></li>
            <li><Link to="/bug-bounty">Bug Bounty Program</Link></li>
            <li><Link to="/accessibility">Accessibility</Link></li>
            <li><Link to="/compliance">Compliance</Link></li>
          </ul>
        </div>

        {/* Column 6: About & Transparency */}
        <div className="footer-column">
          <h3>About</h3>
          <ul>
            <li><Link to="/transparency">Transparency Report</Link></li>
            <li><a href="mailto:legal@go4garage.com">Contact Legal</a></li>
            <li><a href="mailto:support@go4garage.com">Support</a></li>
            <li><a href="mailto:privacy@go4garage.com">Privacy Inquiries</a></li>
          </ul>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <p>&copy; 2025 Go4Garage Charging Point. All rights reserved.</p>
          <p className="made-in-bharat">
            Made In Bharat <span className="flag-emoji">🇮🇳</span>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default LegalFooter;
