import React from 'react';
import './LegalPages.css';

const DataRetentionPolicy = () => {
  return (
    <div className="legal-document-container">
      <div className="legal-header">
        <h1>Data Retention Policy</h1>
        <p className="last-updated">Last Updated: January 15, 2025</p>
      </div>
      
      <div className="legal-content">
        <section>
          <h2>1. Purpose and Scope</h2>
          <p>
            This Data Retention Policy defines how Go4Garage collects, stores, retains, and disposes of data 
            within the Kailash platform. This policy ensures compliance with Indian data protection laws 
            (IT Act 2000, DPDP Act 2023) while maintaining operational efficiency and meeting business requirements.
          </p>
          <p>
            Kailash processes critical infrastructure data for EV charging operations. Proper data retention 
            ensures system reliability, regulatory compliance, audit trails, and protection of user rights.
          </p>
        </section>

        <section>
          <h2>2. Data Categories and Retention Periods</h2>
          
          <h3>2.1 Account and User Data</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Retention Period</th>
                <th>Legal Basis</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Account credentials (Kailash Code)</td>
                <td>Active account + 1 year</td>
                <td>Contract performance</td>
              </tr>
              <tr>
                <td>User profile information</td>
                <td>Active account + 6 months</td>
                <td>Legitimate interest</td>
              </tr>
              <tr>
                <td>Authentication logs</td>
                <td>2 years</td>
                <td>Security compliance</td>
              </tr>
              <tr>
                <td>Access permissions history</td>
                <td>3 years</td>
                <td>Audit requirements</td>
              </tr>
            </tbody>
          </table>

          <h3>2.2 Operational Data</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Retention Period</th>
                <th>Legal Basis</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Charging session records</td>
                <td>7 years</td>
                <td>Tax compliance (Income Tax Act)</td>
              </tr>
              <tr>
                <td>Energy consumption data</td>
                <td>5 years</td>
                <td>Electricity Act 2003</td>
              </tr>
              <tr>
                <td>Station performance metrics</td>
                <td>3 years</td>
                <td>Operational analysis</td>
              </tr>
              <tr>
                <td>GANESHA AI command history</td>
                <td>1 year</td>
                <td>Service improvement</td>
              </tr>
              <tr>
                <td>Dashboard configurations</td>
                <td>Active account duration</td>
                <td>User convenience</td>
              </tr>
            </tbody>
          </table>

          <h3>2.3 Financial Data</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Retention Period</th>
                <th>Legal Basis</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Transaction records</td>
                <td>7 years</td>
                <td>Income Tax Act 1961</td>
              </tr>
              <tr>
                <td>GST invoices</td>
                <td>6 years</td>
                <td>GST Act 2017</td>
              </tr>
              <tr>
                <td>Payment method information</td>
                <td>Transaction + 3 months</td>
                <td>Dispute resolution</td>
              </tr>
              <tr>
                <td>Billing statements</td>
                <td>7 years</td>
                <td>Accounting standards</td>
              </tr>
            </tbody>
          </table>

          <h3>2.4 Security and Monitoring Data</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Retention Period</th>
                <th>Legal Basis</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>SHIV security logs</td>
                <td>2 years</td>
                <td>CERT-In Directions 2022</td>
              </tr>
              <tr>
                <td>Failed login attempts</td>
                <td>180 days</td>
                <td>Security analysis</td>
              </tr>
              <tr>
                <td>PARVATI workload logs</td>
                <td>1 year</td>
                <td>System optimization</td>
              </tr>
              <tr>
                <td>Incident response records</td>
                <td>5 years</td>
                <td>Legal compliance</td>
              </tr>
              <tr>
                <td>Audit trails</td>
                <td>3 years</td>
                <td>Regulatory audit</td>
              </tr>
            </tbody>
          </table>

          <h3>2.5 Communication Data</h3>
          <table>
            <thead>
              <tr>
                <th>Data Type</th>
                <th>Retention Period</th>
                <th>Legal Basis</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Support tickets</td>
                <td>3 years</td>
                <td>Service quality</td>
              </tr>
              <tr>
                <td>Email correspondence</td>
                <td>2 years</td>
                <td>Business records</td>
              </tr>
              <tr>
                <td>System notifications</td>
                <td>90 days</td>
                <td>Operational tracking</td>
              </tr>
              <tr>
                <td>Alert history</td>
                <td>1 year</td>
                <td>Trend analysis</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section>
          <h2>3. Data Storage and Security</h2>
          <p>All retained data is stored securely in compliance with Indian regulations:</p>
          <ul>
            <li><strong>Primary Storage:</strong> MongoDB database hosted in India</li>
            <li><strong>Encryption:</strong> AES-256 encryption at rest, TLS 1.3 in transit</li>
            <li><strong>Access Control:</strong> Role-based access with audit logging</li>
            <li><strong>Backup Storage:</strong> Encrypted backups in geographically separate Indian data centers</li>
            <li><strong>Data Localization:</strong> All critical data stored within Indian territory (DPDP Act compliance)</li>
          </ul>
        </section>

        <section>
          <h2>4. Data Disposal Procedures</h2>
          <p>When retention periods expire, data is securely disposed of:</p>
          
          <h3>4.1 Automated Deletion</h3>
          <ul>
            <li>Scheduled deletion jobs run monthly</li>
            <li>Data past retention period flagged for deletion</li>
            <li>30-day grace period before permanent deletion</li>
            <li>Deletion logs maintained for audit (retained 2 years)</li>
          </ul>

          <h3>4.2 Secure Deletion Methods</h3>
          <ul>
            <li><strong>Database Records:</strong> Cryptographic erasure (encryption keys destroyed)</li>
            <li><strong>Backup Data:</strong> Secure overwrite (DoD 5220.22-M standard)</li>
            <li><strong>Log Files:</strong> Shredding and verification</li>
            <li><strong>Physical Media:</strong> Destruction certificates from certified vendors</li>
          </ul>

          <h3>4.3 Verification Process</h3>
          <ul>
            <li>Quarterly audits of deletion processes</li>
            <li>Verification of data no longer accessible</li>
            <li>Documentation of disposal actions</li>
            <li>Compliance reports to Data Protection Officer</li>
          </ul>
        </section>

        <section>
          <h2>5. User Rights and Data Requests</h2>
          <p>Under DPDP Act 2023, users have specific rights regarding their retained data:</p>
          
          <h3>5.1 Right to Access</h3>
          <p>Request a copy of all your retained data:</p>
          <ul>
            <li>Submit request to legal@go4garage.in</li>
            <li>Verification of identity required</li>
            <li>Response within 30 days</li>
            <li>Data provided in machine-readable format (JSON)</li>
            <li>First request free, subsequent requests may incur reasonable fees</li>
          </ul>

          <h3>5.2 Right to Deletion</h3>
          <p>Request deletion of your data (subject to legal retention requirements):</p>
          <ul>
            <li>Account closure triggers deletion process</li>
            <li>Non-essential data deleted within 30 days</li>
            <li>Legally required data retained per schedule</li>
            <li>Notification when deletion complete</li>
          </ul>

          <h3>5.3 Right to Correction</h3>
          <p>Request correction of inaccurate data:</p>
          <ul>
            <li>Submit correction request with evidence</li>
            <li>Review and update within 15 days</li>
            <li>Notification of changes made</li>
            <li>Historical records annotated (not deleted) for audit trail</li>
          </ul>
        </section>

        <section>
          <h2>6. Legal Holds and Exceptions</h2>
          <p>In certain circumstances, normal retention periods may be extended:</p>
          
          <h3>6.1 Legal Proceedings</h3>
          <ul>
            <li>Data relevant to litigation preserved indefinitely</li>
            <li>Legal hold notice issued by legal team</li>
            <li>Automated deletion suspended</li>
            <li>Hold released when legal matter concluded</li>
          </ul>

          <h3>6.2 Regulatory Investigations</h3>
          <ul>
            <li>CERT-In cybersecurity investigations</li>
            <li>Electricity board compliance audits</li>
            <li>Tax authority inquiries</li>
            <li>Data preserved until investigation closure</li>
          </ul>

          <h3>6.3 Security Incidents</h3>
          <ul>
            <li>Incident-related data retained for 5 years minimum</li>
            <li>SHIV logs preserved for forensic analysis</li>
            <li>Evidence chain maintained</li>
            <li>Law enforcement cooperation requirements</li>
          </ul>
        </section>

        <section>
          <h2>7. Third-Party Data Processing</h2>
          <p>Third-party services process data on our behalf with equivalent retention standards:</p>
          <ul>
            <li><strong>MongoDB Atlas:</strong> Database hosting (follows our retention policy)</li>
            <li><strong>Anthropic:</strong> AI processing (no data retention beyond session)</li>
            <li><strong>Backup Services:</strong> Encrypted backups (same retention as primary)</li>
          </ul>
          <p>All third-party processors bound by Data Processing Agreements (DPAs).</p>
        </section>

        <section>
          <h2>8. Backup Retention</h2>
          <p>Backup data retention for business continuity:</p>
          <ul>
            <li><strong>Daily Backups:</strong> Retained 30 days</li>
            <li><strong>Weekly Backups:</strong> Retained 90 days</li>
            <li><strong>Monthly Backups:</strong> Retained 1 year</li>
            <li><strong>Annual Backups:</strong> Retained 7 years (tax compliance)</li>
          </ul>
          <p>Backup data subject to same deletion rights (excluding legally required retention).</p>
        </section>

        <section>
          <h2>9. Policy Review and Updates</h2>
          <p>This policy is reviewed and updated:</p>
          <ul>
            <li>Annually by Data Protection Officer</li>
            <li>When regulations change (e.g., new DPDP Act rules)</li>
            <li>After security incidents requiring retention changes</li>
            <li>Based on technology or business process updates</li>
          </ul>
          <p>Material changes communicated via email to users.</p>
        </section>

        <section>
          <h2>10. Compliance and Accountability</h2>
          <p>Accountability measures for this policy:</p>
          <ul>
            <li><strong>Data Protection Officer:</strong> Oversees policy implementation</li>
            <li><strong>Quarterly Audits:</strong> Compliance verification</li>
            <li><strong>Deletion Reports:</strong> Monthly disposal logs</li>
            <li><strong>Training:</strong> Annual staff training on retention requirements</li>
            <li><strong>Documentation:</strong> Retention decision records maintained</li>
          </ul>
        </section>

        <section>
          <h2>11. Contact Information</h2>
          <p>For data retention inquiries or requests:</p>
          <div className="contact-box">
            <p><strong>Go4Garage - Kailash Platform</strong></p>
            <p>General Inquiries: connect@go4garage.in</p>
            <p>Data Requests: legal@go4garage.in</p>
            <p>Data Protection Officer: legal@go4garage.in</p>
          </div>
        </section>
      </div>

      <div className="legal-footer">
        <p>© 2025 Go4Garage. All rights reserved.</p>
        <p>This Data Retention Policy complies with IT Act 2000 and DPDP Act 2023.</p>
        <div className="contact-info">
          <p>General Inquiries: connect@go4garage.in</p>
          <p>Legal Matters: legal@go4garage.in</p>
        </div>
      </div>
    </div>
  );
};

export default DataRetentionPolicy;