import React from 'react';
import './LegalPages.css';

const SubprocessorList = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Subprocessor List</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              This document lists all subprocessors (third-party service providers) that process personal data
              on behalf of Go4Garage. We maintain strict controls over subprocessor engagement.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Infrastructure Subprocessors</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Amazon Web Services (AWS)</td>
                  <td>Cloud Hosting</td>
                  <td>India (Mumbai), EU (Frankfurt), US (Virginia)</td>
                  <td>Infrastructure and data storage</td>
                </tr>
                <tr>
                  <td>Google Cloud Platform</td>
                  <td>Cloud Services</td>
                  <td>India, EU, US</td>
                  <td>Backup storage, analytics</td>
                </tr>
                <tr>
                  <td>Cloudflare</td>
                  <td>CDN & Security</td>
                  <td>Global</td>
                  <td>Content delivery, DDoS protection</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>3. Communication Subprocessors</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>SendGrid (Twilio)</td>
                  <td>Email Delivery</td>
                  <td>US, EU</td>
                  <td>Transactional and marketing emails</td>
                </tr>
                <tr>
                  <td>Twilio</td>
                  <td>SMS & Voice</td>
                  <td>Global</td>
                  <td>SMS notifications, 2FA</td>
                </tr>
                <tr>
                  <td>Intercom</td>
                  <td>Customer Messaging</td>
                  <td>US, EU</td>
                  <td>In-app messaging, support chat</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>4. Analytics and Monitoring</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Google Analytics</td>
                  <td>Web Analytics</td>
                  <td>US</td>
                  <td>Usage statistics, performance monitoring</td>
                </tr>
                <tr>
                  <td>Mixpanel</td>
                  <td>Product Analytics</td>
                  <td>US</td>
                  <td>User behavior analysis</td>
                </tr>
                <tr>
                  <td>Sentry</td>
                  <td>Error Tracking</td>
                  <td>US</td>
                  <td>Application monitoring, error logging</td>
                </tr>
                <tr>
                  <td>Datadog</td>
                  <td>Infrastructure Monitoring</td>
                  <td>US, EU</td>
                  <td>Server monitoring, logs</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>5. Payment Processing</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Stripe</td>
                  <td>Payment Gateway</td>
                  <td>Global (compliance with local regulations)</td>
                  <td>Credit card processing, subscription billing</td>
                </tr>
                <tr>
                  <td>Razorpay</td>
                  <td>Payment Gateway (India)</td>
                  <td>India</td>
                  <td>Local payment methods, UPI</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>6. Customer Support</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Zendesk</td>
                  <td>Help Desk</td>
                  <td>US, EU</td>
                  <td>Support ticket management</td>
                </tr>
                <tr>
                  <td>Freshdesk</td>
                  <td>Customer Support</td>
                  <td>India, US, EU</td>
                  <td>Support operations</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>7. Security and Compliance</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Auth0</td>
                  <td>Authentication</td>
                  <td>US, EU</td>
                  <td>Identity and access management</td>
                </tr>
                <tr>
                  <td>Vanta</td>
                  <td>Compliance Automation</td>
                  <td>US</td>
                  <td>SOC 2, ISO 27001 compliance</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>8. Marketing and CRM</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Subprocessor</th>
                  <th>Service Provided</th>
                  <th>Data Location</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>HubSpot</td>
                  <td>CRM & Marketing</td>
                  <td>US</td>
                  <td>Customer relationship management, marketing automation</td>
                </tr>
                <tr>
                  <td>Mailchimp</td>
                  <td>Email Marketing</td>
                  <td>US</td>
                  <td>Newsletter campaigns</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>9. Subprocessor Requirements</h2>
            <p>All subprocessors must:</p>
            <ul>
              <li>Sign Data Processing Agreements (DPAs)</li>
              <li>Implement appropriate technical and organizational measures</li>
              <li>Comply with GDPR, CCPA, and other applicable laws</li>
              <li>Maintain ISO 27001 or equivalent certification</li>
              <li>Undergo regular security audits</li>
              <li>Report security incidents within 24 hours</li>
              <li>Use Standard Contractual Clauses for international transfers</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Subprocessor Vetting Process</h2>
            <p>Before engaging a new subprocessor, we:</p>
            <ol>
              <li>Conduct security and privacy assessment</li>
              <li>Review certifications and compliance documentation</li>
              <li>Evaluate data processing practices</li>
              <li>Negotiate appropriate DPA terms</li>
              <li>Perform risk assessment</li>
              <li>Obtain customer approval if required by contract</li>
            </ol>
          </section>

          <section className="legal-section">
            <h2>11. Changes to Subprocessor List</h2>
            <h3>11.1 Adding New Subprocessors</h3>
            <p>When adding new subprocessors:</p>
            <ul>
              <li>Enterprise customers notified 30 days in advance</li>
              <li>Opportunity to object provided</li>
              <li>This list updated promptly</li>
              <li>Email notifications sent to subscribed users</li>
            </ul>

            <h3>11.2 Removing Subprocessors</h3>
            <ul>
              <li>List updated within 7 days of removal</li>
              <li>Data migration handled securely</li>
              <li>Certification of data deletion obtained</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Monitoring and Audits</h2>
            <ul>
              <li>Annual reviews of all subprocessor relationships</li>
              <li>Regular security audits and assessments</li>
              <li>Incident response drills</li>
              <li>Compliance verification</li>
              <li>Performance monitoring</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Customer Rights</h2>
            <h3>13.1 Information Rights</h3>
            <ul>
              <li>Access to DPAs upon request (with confidential information redacted)</li>
              <li>Information about subprocessor safeguards</li>
              <li>Details about data processing locations</li>
            </ul>

            <h3>13.2 Objection Rights</h3>
            <p>Enterprise customers can:</p>
            <ul>
              <li>Object to new subprocessors</li>
              <li>Request alternative arrangements</li>
              <li>Terminate agreement if concerns not resolved</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>14. Notification Subscription</h2>
            <p>Subscribe to subprocessor updates:</p>
            <ul>
              <li><strong>Email:</strong> subprocessor-updates@go4garage.com</li>
              <li><strong>RSS Feed:</strong> go4garage.com/subprocessors/feed</li>
              <li><strong>API:</strong> Webhook notifications available for enterprise</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>15. Contact</h2>
            <p>For questions about subprocessors:</p>
            <ul>
              <li><strong>Privacy Team:</strong> privacy@go4garage.com</li>
              <li><strong>DPO:</strong> dpo@go4garage.com</li>
              <li><strong>Compliance:</strong> compliance@go4garage.com</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For subprocessor inquiries, contact: privacy@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default SubprocessorList;
