import React from 'react';
import './LegalPages.css';

const AgeRestrictionPolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Age Restriction Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Minimum Age Requirement</h2>
            <p>
              To use the Go4Garage platform, you must be at least <strong>18 years of age</strong>. By using
              our services, you represent and warrant that you meet this age requirement.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Why We Have Age Restrictions</h2>
            <p>Age restrictions are necessary because:</p>
            <ul>
              <li><strong>Legal Contracts:</strong> Our Terms of Service constitute a binding legal agreement</li>
              <li><strong>Payment Processing:</strong> Financial transactions require legal capacity</li>
              <li><strong>Data Protection:</strong> Special protections apply to children's data under COPPA, GDPR-K</li>
              <li><strong>Safety:</strong> EV charging infrastructure involves high-voltage equipment</li>
              <li><strong>Business Nature:</strong> Our services are primarily B2B and commercial</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Jurisdiction-Specific Requirements</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Jurisdiction</th>
                  <th>Minimum Age</th>
                  <th>Special Provisions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>India</td>
                  <td>18 years</td>
                  <td>As per Contract Act, 1872</td>
                </tr>
                <tr>
                  <td>European Union</td>
                  <td>16 years</td>
                  <td>GDPR Article 8; may vary by member state</td>
                </tr>
                <tr>
                  <td>United States</td>
                  <td>18 years</td>
                  <td>COPPA compliance; 13+ with parental consent</td>
                </tr>
                <tr>
                  <td>United Kingdom</td>
                  <td>18 years</td>
                  <td>Age Appropriate Design Code</td>
                </tr>
                <tr>
                  <td>Other Countries</td>
                  <td>18 years or local age of majority</td>
                  <td>Whichever is higher applies</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>4. Age Verification</h2>
            <p>We may verify your age through:</p>
            <ul>
              <li><strong>Account Registration:</strong> Date of birth required during signup</li>
              <li><strong>Payment Methods:</strong> Credit/debit cards require 18+ status</li>
              <li><strong>Identity Documents:</strong> May request government-issued ID for high-value transactions</li>
              <li><strong>Business Verification:</strong> Company registration documents for enterprise accounts</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Children's Privacy</h2>
            <p>
              We do not knowingly collect personal information from individuals under 18 years of age. If we
              learn that we have collected information from a minor:
            </p>
            <ul>
              <li>We will delete the information promptly</li>
              <li>The account will be terminated</li>
              <li>Parents/guardians will be notified if contact information is available</li>
              <li>Refunds will be processed for any payments made</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Educational and Research Use</h2>
            <h3>6.1 Academic Institutions</h3>
            <p>Students under 18 may access the platform through:</p>
            <ul>
              <li><strong>Institutional Accounts:</strong> Supervised by qualified educators</li>
              <li><strong>Parental Consent:</strong> Written permission from parent/guardian</li>
              <li><strong>Limited Access:</strong> Educational materials only, no transactions</li>
            </ul>

            <h3>6.2 Requirements</h3>
            <ul>
              <li>Educational institution must have active enterprise account</li>
              <li>All activities monitored by responsible adult</li>
              <li>No payment processing capabilities for minor accounts</li>
              <li>Compliance with FERPA and other educational privacy laws</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Parental Controls</h2>
            <p>For educational access, we provide:</p>
            <ul>
              <li>Activity monitoring dashboards for educators/parents</li>
              <li>Restricted access to sensitive information</li>
              <li>No marketing communications to minor accounts</li>
              <li>Enhanced privacy protections</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Consequences of Providing False Age Information</h2>
            <p>If you provide false age information:</p>
            <ul>
              <li>Your account will be immediately terminated</li>
              <li>Access to all services will be revoked</li>
              <li>You may be prohibited from creating future accounts</li>
              <li>Legal action may be taken for fraudulent misrepresentation</li>
              <li>You remain liable for any charges incurred</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Parental Rights</h2>
            <p>Parents or legal guardians may:</p>
            <ul>
              <li>Review any data collected from their child</li>
              <li>Request deletion of their child's account and data</li>
              <li>Refuse further collection or use of their child's information</li>
              <li>Contact us at privacy@go4garage.com</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Reporting Underage Users</h2>
            <p>
              If you believe an account is held by someone under the minimum age, please report it:
            </p>
            <ul>
              <li><strong>Email:</strong> compliance@go4garage.com</li>
              <li><strong>Subject Line:</strong> "Underage Account Report"</li>
              <li><strong>Include:</strong> Account username/email, reason for concern, any evidence</li>
            </ul>
            <p>We will investigate all reports promptly and take appropriate action.</p>
          </section>

          <section className="legal-section">
            <h2>11. International Users</h2>
            <p>
              If your country has a higher age of majority than 18, that age applies. Users are responsible
              for knowing and complying with local age requirements.
            </p>
          </section>

          <section className="legal-section">
            <h2>12. Changes to Age Requirements</h2>
            <p>
              We reserve the right to modify age requirements based on:
            </p>
            <ul>
              <li>Changes in applicable laws</li>
              <li>Introduction of new services</li>
              <li>Risk assessment and safety considerations</li>
            </ul>
            <p>Changes will be communicated via email and website notice.</p>
          </section>

          <section className="legal-section">
            <h2>13. Contact Information</h2>
            <p>For questions about age restrictions:</p>
            <ul>
              <li><strong>General:</strong> support@go4garage.com</li>
              <li><strong>Privacy/Compliance:</strong> privacy@go4garage.com</li>
              <li><strong>Educational Access:</strong> education@go4garage.com</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For age-related inquiries, contact: compliance@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default AgeRestrictionPolicy;
