import React from 'react';
import './LegalPages.css';

const CCPACompliance = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>CCPA Compliance</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              This notice applies to California residents and describes our practices regarding the collection,
              use, and disclosure of personal information in accordance with the California Consumer Privacy Act (CCPA).
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Your CCPA Rights</h2>
            <h3>2.1 Right to Know</h3>
            <p>You have the right to request information about:</p>
            <ul>
              <li>Categories of personal information we collected</li>
              <li>Specific pieces of personal information we collected</li>
              <li>Categories of sources from which we collected personal information</li>
              <li>Business purposes for collecting or selling personal information</li>
              <li>Categories of third parties with whom we share personal information</li>
            </ul>

            <h3>2.2 Right to Delete</h3>
            <p>You have the right to request deletion of personal information we collected from you.</p>

            <h3>2.3 Right to Opt-Out of Sale</h3>
            <p>You have the right to opt-out of the sale of your personal information.</p>

            <h3>2.4 Right to Non-Discrimination</h3>
            <p>We will not discriminate against you for exercising your CCPA rights.</p>
          </section>

          <section className="legal-section">
            <h2>3. Personal Information We Collect</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Examples</th>
                  <th>Business Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Identifiers</td>
                  <td>Name, email, phone, IP address</td>
                  <td>Account management, communication</td>
                </tr>
                <tr>
                  <td>Commercial Information</td>
                  <td>Purchase history, payment info</td>
                  <td>Transaction processing</td>
                </tr>
                <tr>
                  <td>Internet Activity</td>
                  <td>Browsing history, search history</td>
                  <td>Service improvement, analytics</td>
                </tr>
                <tr>
                  <td>Geolocation Data</td>
                  <td>Device location, IP location</td>
                  <td>Service customization</td>
                </tr>
                <tr>
                  <td>Professional Information</td>
                  <td>Company name, job title</td>
                  <td>B2B services</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>4. How We Use Personal Information</h2>
            <ul>
              <li>Provide and maintain our services</li>
              <li>Process transactions and payments</li>
              <li>Communicate with you about your account</li>
              <li>Send marketing communications (with consent)</li>
              <li>Improve and develop new services</li>
              <li>Detect and prevent fraud</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Disclosure of Personal Information</h2>
            <p>We may disclose your personal information to:</p>
            <ul>
              <li><strong>Service Providers:</strong> Payment processors, hosting providers, analytics services</li>
              <li><strong>Business Partners:</strong> For joint marketing or co-branded services</li>
              <li><strong>Legal Authorities:</strong> When required by law or to protect rights</li>
              <li><strong>Corporate Transactions:</strong> In case of merger, acquisition, or asset sale</li>
            </ul>

            <p><strong>We do not sell your personal information to third parties.</strong></p>
          </section>

          <section className="legal-section">
            <h2>6. Data Retention</h2>
            <p>We retain personal information for as long as necessary to:</p>
            <ul>
              <li>Provide our services</li>
              <li>Comply with legal obligations</li>
              <li>Resolve disputes</li>
              <li>Enforce our agreements</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Exercising Your CCPA Rights</h2>
            <h3>7.1 How to Submit a Request</h3>
            <p>You can submit a request by:</p>
            <ul>
              <li><strong>Email:</strong> privacy@go4garage.com</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX (toll-free for California residents)</li>
              <li><strong>Online Form:</strong> Available in your account settings</li>
            </ul>

            <h3>7.2 Verification Process</h3>
            <p>To verify your identity, we may request:</p>
            <ul>
              <li>Email confirmation</li>
              <li>Account credentials</li>
              <li>Additional identifying information</li>
            </ul>

            <h3>7.3 Response Timeline</h3>
            <ul>
              <li>Acknowledgment within 10 days</li>
              <li>Complete response within 45 days</li>
              <li>May extend by additional 45 days if needed</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Authorized Agents</h2>
            <p>
              You may designate an authorized agent to submit requests on your behalf. The agent must provide:
            </p>
            <ul>
              <li>Proof of authorization (signed permission)</li>
              <li>Verification of their own identity</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Do Not Sell My Personal Information</h2>
            <p>
              We do not sell personal information. If our practices change, we will update this notice and
              provide you with an opt-out mechanism.
            </p>
          </section>

          <section className="legal-section">
            <h2>10. CCPA for Minors</h2>
            <p>
              We do not knowingly sell personal information of consumers under 16 years of age without
              affirmative authorization.
            </p>
          </section>

          <section className="legal-section">
            <h2>11. Contact Information</h2>
            <p>For CCPA-related inquiries:</p>
            <ul>
              <li><strong>Email:</strong> privacy@go4garage.com</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX</li>
              <li><strong>Address:</strong> Go4Garage Privacy Office, [Address], India</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For CCPA inquiries, contact: privacy@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default CCPACompliance;
