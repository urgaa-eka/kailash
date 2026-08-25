import React from 'react';
import './LegalPages.css';

const DataBreachPolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Data Breach Response Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              Go4Garage is committed to protecting your data. This Data Breach Response Policy outlines our procedures
              for detecting, responding to, and recovering from data security incidents that may affect your personal information.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. What Constitutes a Data Breach</h2>
            <p>A data breach is defined as:</p>
            <ul>
              <li>Unauthorized access to personal or sensitive data</li>
              <li>Accidental or unlawful destruction, loss, alteration, or disclosure of data</li>
              <li>Any incident that compromises the security, confidentiality, or integrity of data</li>
              <li>Ransomware attacks affecting data availability</li>
              <li>Insider threats resulting in data exposure</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Breach Detection and Assessment</h2>
            <h3>3.1 Detection Methods</h3>
            <p>We employ multiple detection mechanisms:</p>
            <ul>
              <li>Real-time monitoring systems and intrusion detection</li>
              <li>Automated security alerts and anomaly detection</li>
              <li>Regular security audits and vulnerability assessments</li>
              <li>Employee and third-party incident reporting</li>
              <li>User reports of suspicious activity</li>
            </ul>

            <h3>3.2 Initial Assessment</h3>
            <p>Upon detection, our security team will:</p>
            <ul>
              <li>Verify the incident within 1 hour of detection</li>
              <li>Assess the scope and severity of the breach</li>
              <li>Identify affected systems, data types, and users</li>
              <li>Document the incident timeline and evidence</li>
              <li>Activate our incident response team</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Breach Response Procedures</h2>
            <h3>4.1 Immediate Actions (0-24 hours)</h3>
            <ul>
              <li><strong>Containment:</strong> Isolate affected systems to prevent further damage</li>
              <li><strong>Evidence Preservation:</strong> Secure logs, records, and forensic data</li>
              <li><strong>Team Mobilization:</strong> Assemble cross-functional incident response team</li>
              <li><strong>Initial Communication:</strong> Notify key stakeholders internally</li>
              <li><strong>Risk Assessment:</strong> Evaluate potential harm to affected individuals</li>
            </ul>

            <h3>4.2 Investigation Phase (24-72 hours)</h3>
            <ul>
              <li>Conduct forensic analysis to determine breach cause and entry point</li>
              <li>Identify all compromised data elements and affected users</li>
              <li>Assess whether encryption or other protections were in place</li>
              <li>Evaluate the likelihood of data misuse</li>
              <li>Coordinate with law enforcement if criminal activity is suspected</li>
            </ul>

            <h3>4.3 Remediation (72 hours - ongoing)</h3>
            <ul>
              <li>Patch vulnerabilities and strengthen security controls</li>
              <li>Reset credentials for affected accounts</li>
              <li>Restore systems from clean backups if necessary</li>
              <li>Implement additional monitoring for affected systems</li>
              <li>Review and update security policies based on lessons learned</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Notification Requirements</h2>
            <h3>5.1 Affected Users</h3>
            <p>We will notify affected users without undue delay and within:</p>
            <ul>
              <li><strong>72 hours</strong> for breaches involving high-risk personal data</li>
              <li><strong>30 days</strong> for breaches involving other personal information</li>
              <li>Notification will include:
                <ul>
                  <li>Description of the breach and data types affected</li>
                  <li>Likely consequences and potential risks</li>
                  <li>Measures taken to address the breach</li>
                  <li>Recommended actions for affected users</li>
                  <li>Contact information for questions</li>
                </ul>
              </li>
            </ul>

            <h3>5.2 Regulatory Authorities</h3>
            <p>We will notify relevant authorities as required by law:</p>
            <ul>
              <li><strong>GDPR:</strong> Within 72 hours to the supervisory authority</li>
              <li><strong>CCPA:</strong> As required by California law</li>
              <li><strong>Other Jurisdictions:</strong> According to applicable data protection laws</li>
            </ul>

            <h3>5.3 Public Disclosure</h3>
            <p>For significant breaches affecting a large number of users, we will:</p>
            <ul>
              <li>Issue public statements through our website and media</li>
              <li>Provide regular updates on investigation progress</li>
              <li>Maintain transparency about remediation efforts</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. User Rights and Support</h2>
            <p>If your data is affected by a breach, you have the right to:</p>
            <ul>
              <li>Receive detailed information about the breach</li>
              <li>Access free credit monitoring services (for financial data breaches)</li>
              <li>Request account deletion or data portability</li>
              <li>File a complaint with data protection authorities</li>
              <li>Seek compensation for damages under applicable law</li>
            </ul>

            <h3>6.1 Support Resources</h3>
            <p>We will provide affected users with:</p>
            <ul>
              <li>Dedicated support hotline and email (security@go4garage.com)</li>
              <li>Step-by-step guidance on protective measures</li>
              <li>Identity theft protection services (for high-risk breaches)</li>
              <li>Regular updates on investigation and remediation</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Prevention and Preparedness</h2>
            <h3>7.1 Proactive Measures</h3>
            <p>To minimize breach risks, we maintain:</p>
            <ul>
              <li>Industry-standard encryption for data at rest and in transit</li>
              <li>Multi-factor authentication for sensitive systems</li>
              <li>Regular security training for all employees</li>
              <li>Penetration testing and vulnerability scanning</li>
              <li>Third-party security audits and certifications</li>
            </ul>

            <h3>7.2 Business Continuity</h3>
            <ul>
              <li>Maintained incident response team with defined roles</li>
              <li>Regular disaster recovery drills and simulations</li>
              <li>Secure data backup and recovery procedures</li>
              <li>Cyber insurance coverage</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Post-Incident Review</h2>
            <p>After resolving a breach, we will:</p>
            <ul>
              <li>Conduct a comprehensive post-mortem analysis</li>
              <li>Document lessons learned and areas for improvement</li>
              <li>Update security policies and procedures</li>
              <li>Implement additional safeguards to prevent recurrence</li>
              <li>Provide transparency report to stakeholders</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Reporting a Security Concern</h2>
            <p>If you suspect a data breach or security vulnerability:</p>
            <ul>
              <li><strong>Email:</strong> security@go4garage.com</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX (24/7 Security Hotline)</li>
              <li><strong>Response Time:</strong> We will acknowledge reports within 24 hours</li>
            </ul>
            <p>
              We encourage responsible disclosure and will not take legal action against security researchers
              who report vulnerabilities in good faith.
            </p>
          </section>

          <section className="legal-section">
            <h2>10. Updates to This Policy</h2>
            <p>
              This Data Breach Response Policy is reviewed and updated annually or following significant incidents.
              Material changes will be communicated through our website and email notifications.
            </p>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For questions about this policy, contact: legal@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default DataBreachPolicy;
