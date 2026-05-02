import React from 'react';
import './LegalPages.css';

const DisclaimerPolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Disclaimer Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. General Disclaimer</h2>
            <p>
              The information provided on the Go4Garage platform is for general informational purposes only.
              While we strive to keep the information accurate and up-to-date, we make no representations or
              warranties of any kind, express or implied, about the completeness, accuracy, reliability,
              suitability, or availability of the platform or the information, products, services, or related
              graphics contained on the platform for any purpose.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. No Warranty</h2>
            <p>
              THE PLATFORM IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT ANY WARRANTIES OF ANY KIND,
              EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
            </p>
            <ul>
              <li>Warranties of merchantability</li>
              <li>Fitness for a particular purpose</li>
              <li>Non-infringement</li>
              <li>Accuracy or completeness of content</li>
              <li>Uninterrupted or error-free operation</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Limitation of Liability</h2>
            <p>
              TO THE FULLEST EXTENT PERMITTED BY LAW, GO4GARAGE SHALL NOT BE LIABLE FOR ANY:
            </p>
            <ul>
              <li>Direct, indirect, incidental, special, or consequential damages</li>
              <li>Loss of profits, revenue, or data</li>
              <li>Business interruption</li>
              <li>Loss of use or opportunity</li>
              <li>Damages arising from reliance on information provided</li>
            </ul>
            <p>
              This applies whether based on warranty, contract, tort, or any other legal theory, and whether
              or not we have been informed of the possibility of such damage.
            </p>
          </section>

          <section className="legal-section">
            <h2>4. Technical Accuracy</h2>
            <p>
              While we make every effort to ensure technical accuracy of information related to EV charging
              infrastructure and operations:
            </p>
            <ul>
              <li>Technical specifications may change without notice</li>
              <li>Charging times and efficiency may vary based on conditions</li>
              <li>Equipment performance depends on multiple factors</li>
              <li>We recommend consulting qualified professionals for critical decisions</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Third-Party Content</h2>
            <p>
              Our platform may contain links to third-party websites or services. We do not endorse or assume
              responsibility for:
            </p>
            <ul>
              <li>Content, accuracy, or opinions expressed on third-party sites</li>
              <li>Privacy practices or terms of third-party services</li>
              <li>Availability or functionality of external links</li>
              <li>Products or services offered by third parties</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Professional Advice</h2>
            <p>
              Information on this platform should not be considered as professional advice:
            </p>
            <ul>
              <li><strong>Legal:</strong> Not a substitute for legal counsel</li>
              <li><strong>Financial:</strong> Not investment or financial advice</li>
              <li><strong>Technical:</strong> Not a substitute for qualified technicians</li>
              <li><strong>Safety:</strong> Always follow manufacturer guidelines and safety protocols</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Changes and Updates</h2>
            <p>
              We reserve the right to modify, suspend, or discontinue any aspect of the platform at any time
              without notice or liability.
            </p>
          </section>

          <section className="legal-section">
            <h2>8. User Responsibility</h2>
            <p>
              You are solely responsible for:
            </p>
            <ul>
              <li>Your use of the platform and any reliance on information provided</li>
              <li>Verifying information before making decisions</li>
              <li>Compliance with applicable laws and regulations</li>
              <li>Maintaining security of your account credentials</li>
              <li>Backup of your data</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. No Endorsement</h2>
            <p>
              Mention of specific products, services, companies, or organizations does not imply endorsement
              or recommendation by Go4Garage.
            </p>
          </section>

          <section className="legal-section">
            <h2>10. Jurisdiction</h2>
            <p>
              These disclaimers are governed by the laws of India. Some jurisdictions do not allow limitations
              on implied warranties or liability, so these limitations may not apply to you.
            </p>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For questions, contact: legal@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default DisclaimerPolicy;
