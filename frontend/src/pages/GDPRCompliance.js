import React from 'react';
import './LegalPages.css';

const GDPRCompliance = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>GDPR Compliance</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              Go4Garage is committed to compliance with the General Data Protection Regulation (GDPR) for all
              users in the European Economic Area (EEA). This document outlines our GDPR compliance measures
              and your rights under GDPR.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Legal Basis for Processing</h2>
            <p>We process your personal data under the following legal bases:</p>
            <ul>
              <li><strong>Consent:</strong> When you explicitly agree to data processing</li>
              <li><strong>Contract:</strong> To fulfill our service obligations to you</li>
              <li><strong>Legal Obligation:</strong> To comply with applicable laws</li>
              <li><strong>Legitimate Interest:</strong> For fraud prevention, security, and service improvement</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Your GDPR Rights</h2>
            <h3>3.1 Right to Access</h3>
            <p>You have the right to request a copy of all personal data we hold about you.</p>

            <h3>3.2 Right to Rectification</h3>
            <p>You can request correction of inaccurate or incomplete personal data.</p>

            <h3>3.3 Right to Erasure (Right to be Forgotten)</h3>
            <p>You can request deletion of your personal data in certain circumstances.</p>

            <h3>3.4 Right to Restrict Processing</h3>
            <p>You can request that we limit how we use your data.</p>

            <h3>3.5 Right to Data Portability</h3>
            <p>You can request your data in a machine-readable format to transfer to another service.</p>

            <h3>3.6 Right to Object</h3>
            <p>You can object to processing based on legitimate interests or direct marketing.</p>

            <h3>3.7 Rights Related to Automated Decision-Making</h3>
            <p>You have the right not to be subject to decisions based solely on automated processing.</p>
          </section>

          <section className="legal-section">
            <h2>4. Data Processing Activities</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Processing Activity</th>
                  <th>Legal Basis</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Account Management</td>
                  <td>Contract</td>
                  <td>Service delivery</td>
                </tr>
                <tr>
                  <td>Payment Processing</td>
                  <td>Contract</td>
                  <td>Transaction fulfillment</td>
                </tr>
                <tr>
                  <td>Email Marketing</td>
                  <td>Consent</td>
                  <td>Promotional communications</td>
                </tr>
                <tr>
                  <td>Analytics</td>
                  <td>Legitimate Interest</td>
                  <td>Service improvement</td>
                </tr>
                <tr>
                  <td>Fraud Prevention</td>
                  <td>Legitimate Interest</td>
                  <td>Security and compliance</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>5. Data Retention</h2>
            <p>We retain personal data for the following periods:</p>
            <ul>
              <li><strong>Account Data:</strong> Until account deletion + 30 days</li>
              <li><strong>Transaction Records:</strong> 7 years (legal requirement)</li>
              <li><strong>Marketing Data:</strong> Until consent withdrawal + 90 days</li>
              <li><strong>Support Tickets:</strong> 3 years</li>
              <li><strong>Logs:</strong> 90 days</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Data Transfers</h2>
            <p>
              We may transfer your data outside the EEA. When we do, we ensure adequate protection through:
            </p>
            <ul>
              <li><strong>Standard Contractual Clauses (SCCs):</strong> EU-approved contracts</li>
              <li><strong>Adequacy Decisions:</strong> Transfers to countries with adequate data protection</li>
              <li><strong>Binding Corporate Rules:</strong> Internal data protection policies</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Data Security Measures</h2>
            <ul>
              <li>End-to-end encryption for data in transit (TLS 1.3)</li>
              <li>AES-256 encryption for data at rest</li>
              <li>Regular security audits and penetration testing</li>
              <li>Access controls and authentication mechanisms</li>
              <li>Employee training on data protection</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Data Protection Officer</h2>
            <p>Our Data Protection Officer can be contacted at:</p>
            <ul>
              <li><strong>Email:</strong> dpo@go4garage.com</li>
              <li><strong>Address:</strong> Go4Garage Data Protection, [Address], India</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Exercising Your Rights</h2>
            <p>To exercise any of your GDPR rights:</p>
            <ol>
              <li>Email privacy@go4garage.com with your request</li>
              <li>Verify your identity (for security purposes)</li>
              <li>We will respond within 30 days</li>
              <li>Complex requests may take up to 90 days</li>
            </ol>
          </section>

          <section className="legal-section">
            <h2>10. Supervisory Authority</h2>
            <p>
              You have the right to lodge a complaint with your local supervisory authority if you believe
              your data protection rights have been violated.
            </p>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For GDPR inquiries, contact: dpo@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default GDPRCompliance;
