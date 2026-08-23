import React from 'react';
import './LegalPages.css';

const DataTransferPolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>International Data Transfer Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Overview</h2>
            <p>
              Go4Garage operates globally and may transfer your personal data across international borders.
              This policy explains how we protect your data during international transfers.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Data Storage Locations</h2>
            <h3>2.1 Primary Data Centers</h3>
            <ul>
              <li><strong>India:</strong> Mumbai and Bangalore (primary storage)</li>
              <li><strong>European Union:</strong> Frankfurt, Germany (EU users)</li>
              <li><strong>United States:</strong> AWS US-East (backup and analytics)</li>
            </ul>

            <h3>2.2 Data Residency Options</h3>
            <p>Enterprise customers can choose:</p>
            <ul>
              <li>Dedicated regional data storage</li>
              <li>Data localization within specific countries</li>
              <li>Restrictions on cross-border transfers</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Legal Basis for Transfers</h2>
            <h3>3.1 Adequacy Decisions</h3>
            <p>We transfer data to countries with EU adequacy decisions:</p>
            <ul>
              <li>Countries recognized by EU Commission as providing adequate protection</li>
              <li>No additional safeguards required</li>
            </ul>

            <h3>3.2 Standard Contractual Clauses (SCCs)</h3>
            <ul>
              <li>EU-approved model contracts for data transfers</li>
              <li>Used for transfers to countries without adequacy decisions</li>
              <li>Legally binding commitments to protect data</li>
              <li>Copies available upon request</li>
            </ul>

            <h3>3.3 Binding Corporate Rules (BCRs)</h3>
            <ul>
              <li>Internal data protection policies</li>
              <li>Approved by EU data protection authorities</li>
              <li>Govern intra-company transfers</li>
            </ul>

            <h3>3.4 User Consent</h3>
            <ul>
              <li>Explicit consent obtained when required</li>
              <li>Informed about destination countries and risks</li>
              <li>Can withdraw consent at any time</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Data Transfer Safeguards</h2>
            <h3>4.1 Encryption</h3>
            <ul>
              <li><strong>In Transit:</strong> TLS 1.3 encryption for all transfers</li>
              <li><strong>At Rest:</strong> AES-256 encryption in all locations</li>
              <li><strong>Key Management:</strong> Separate keys per region</li>
            </ul>

            <h3>4.2 Access Controls</h3>
            <ul>
              <li>Role-based access control (RBAC)</li>
              <li>Multi-factor authentication required</li>
              <li>Regular access reviews</li>
              <li>Audit logs for all data access</li>
            </ul>

            <h3>4.3 Data Minimization</h3>
            <ul>
              <li>Only necessary data transferred</li>
              <li>Pseudonymization where possible</li>
              <li>Aggregated data for analytics</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Specific Regional Transfers</h2>
            <h3>5.1 EU to Non-EU Transfers</h3>
            <p>For EEA/UK users:</p>
            <ul>
              <li>Data processed primarily within EU</li>
              <li>SCCs in place for non-EU transfers</li>
              <li>Additional safeguards per Schrems II ruling</li>
              <li>Transfer Impact Assessments conducted</li>
            </ul>

            <h3>5.2 India Data Localization</h3>
            <ul>
              <li>Critical personal data stored in India</li>
              <li>Compliance with proposed Personal Data Protection Bill</li>
              <li>Mirrors maintained for business continuity</li>
            </ul>

            <h3>5.3 US Transfers</h3>
            <ul>
              <li>No longer rely on Privacy Shield (invalidated)</li>
              <li>SCCs and supplementary measures used</li>
              <li>Monitoring for US government access</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Third-Party Data Transfers</h2>
            <h3>6.1 Service Providers</h3>
            <p>We use global service providers:</p>
            <ul>
              <li><strong>Cloud Infrastructure:</strong> AWS, Google Cloud (multiple regions)</li>
              <li><strong>Analytics:</strong> Google Analytics (data anonymized)</li>
              <li><strong>Payment Processing:</strong> Stripe (global)</li>
              <li><strong>Support Tools:</strong> Zendesk, Intercom</li>
            </ul>

            <h3>6.2 Vendor Requirements</h3>
            <p>All vendors must:</p>
            <ul>
              <li>Sign Data Processing Agreements (DPAs)</li>
              <li>Implement appropriate safeguards</li>
              <li>Comply with applicable data protection laws</li>
              <li>Submit to regular audits</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Government Data Requests</h2>
            <h3>7.1 Response Policy</h3>
            <ul>
              <li>Challenge overbroad or unlawful requests</li>
              <li>Notify users when legally permitted</li>
              <li>Transparency reports published annually</li>
              <li>Minimize data disclosed</li>
            </ul>

            <h3>7.2 Legal Protections</h3>
            <ul>
              <li>Require valid legal process</li>
              <li>Review all requests with legal counsel</li>
              <li>Object to requests lacking proper jurisdiction</li>
              <li>Use legal mechanisms to protect user data</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Transfer Impact Assessments</h2>
            <p>We conduct assessments evaluating:</p>
            <ul>
              <li>Destination country laws and practices</li>
              <li>Nature and purpose of transfer</li>
              <li>Data categories and sensitivity</li>
              <li>Available safeguards and their effectiveness</li>
              <li>Risks to data subjects</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. User Rights Regarding Transfers</h2>
            <h3>9.1 Information Rights</h3>
            <ul>
              <li>Right to know where your data is stored</li>
              <li>Information about transfer safeguards</li>
              <li>Copies of SCCs upon request</li>
            </ul>

            <h3>9.2 Control Rights</h3>
            <ul>
              <li>Object to specific transfers (where legally possible)</li>
              <li>Request data localization (enterprise plans)</li>
              <li>Delete data to prevent future transfers</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Monitoring and Compliance</h2>
            <ul>
              <li>Regular audits of transfer practices</li>
              <li>Monitoring of legal developments</li>
              <li>Update safeguards as needed</li>
              <li>Annual review of all transfer mechanisms</li>
              <li>Incident response for unauthorized transfers</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Changes to Transfer Practices</h2>
            <p>
              If we materially change our data transfer practices:
            </p>
            <ul>
              <li>Notification provided 30 days in advance</li>
              <li>Explanation of new safeguards</li>
              <li>Option to object or delete account</li>
              <li>Updated policy published</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Complaints and Concerns</h2>
            <p>If you have concerns about data transfers:</p>
            <ul>
              <li><strong>Email:</strong> privacy@go4garage.com</li>
              <li><strong>DPO:</strong> dpo@go4garage.com</li>
              <li><strong>Supervisory Authority:</strong> File complaint with your local data protection authority</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Documentation</h2>
            <p>Available upon request:</p>
            <ul>
              <li>Standard Contractual Clauses</li>
              <li>Data Processing Agreements with vendors</li>
              <li>Transfer Impact Assessments</li>
              <li>List of data transfer destinations</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For data transfer questions, contact: privacy@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default DataTransferPolicy;
