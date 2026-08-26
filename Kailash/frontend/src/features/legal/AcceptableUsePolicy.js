import React from 'react';
import './LegalPages.css';

const AcceptableUsePolicy = () => {
  return (
    <div className="legal-document-container">
      <div className="legal-header">
        <h1>Acceptable Use Policy</h1>
        <p className="last-updated">Last Updated: January 15, 2025</p>
      </div>
      
      <div className="legal-content">
        <section>
          <h2>1. Introduction and Purpose</h2>
          <p>
            This Acceptable Use Policy ("AUP") governs your use of the Kailash platform operated by Go4Garage. 
            By accessing or using Kailash, you agree to comply with this policy. This AUP is designed to protect 
            the integrity, security, and availability of our EV charging infrastructure management platform for all users.
          </p>
          <p>
            Kailash provides enterprise-grade management tools for electric vehicle charging operations. Misuse of 
            the platform can compromise critical infrastructure, endanger charging operations, and violate Indian 
            cybersecurity regulations. This policy establishes clear boundaries for acceptable behavior.
          </p>
        </section>

        <section>
          <h2>2. Permitted Uses</h2>
          <p>You may use Kailash for the following authorized purposes:</p>
          <ul>
            <li><strong>Charging Station Management:</strong> Monitor, control, and manage EV charging infrastructure</li>
            <li><strong>Operations Monitoring:</strong> Track charging sessions, energy consumption, and station performance</li>
            <li><strong>User Management:</strong> Administer user accounts and access permissions within your organization</li>
            <li><strong>Reporting and Analytics:</strong> Generate reports, view dashboards, and analyze operational data</li>
            <li><strong>GANESHA AI Commands:</strong> Issue commands to the AI assistant for business intelligence and task automation</li>
            <li><strong>System Configuration:</strong> Configure settings, integrations, and preferences within authorized parameters</li>
            <li><strong>API Integration:</strong> Integrate Kailash with your business systems via official APIs</li>
            <li><strong>Data Export:</strong> Export your organization's data in compliance with data retention policies</li>
          </ul>
        </section>

        <section>
          <h2>3. Prohibited Activities</h2>
          <p>The following activities are strictly prohibited when using Kailash:</p>
          
          <h3>3.1 Security Violations</h3>
          <ul>
            <li>Attempting to gain unauthorized access to any part of the platform</li>
            <li>Probing, scanning, or testing vulnerabilities without written authorization</li>
            <li>Circumventing authentication or security measures</li>
            <li>Accessing accounts, data, or systems that you are not authorized to access</li>
            <li>Impersonating other users or entities</li>
            <li>Sharing your authentication credentials (Code {'<REDACTED_kailash_code>'} access must remain confidential)</li>
            <li>Reverse engineering, decompiling, or disassembling platform components</li>
          </ul>

          <h3>3.2 System Interference</h3>
          <ul>
            <li>Interfering with or disrupting platform services or servers</li>
            <li>Launching denial-of-service (DoS) attacks</li>
            <li>Overloading systems with excessive requests (API rate limit violations)</li>
            <li>Introducing viruses, malware, ransomware, or other malicious code</li>
            <li>Using automated tools (bots, scrapers) without authorization</li>
            <li>Modifying, disabling, or interfering with SHIV security monitoring</li>
          </ul>

          <h3>3.3 Data Misuse</h3>
          <ul>
            <li>Collecting or harvesting user data without authorization</li>
            <li>Sharing confidential platform data with unauthorized parties</li>
            <li>Using platform data for purposes other than EV charging operations</li>
            <li>Selling, renting, or transferring access to Kailash</li>
            <li>Creating derivative databases from platform data</li>
            <li>Violating data protection laws (IT Act 2000, DPDP Act 2023)</li>
          </ul>

          <h3>3.4 Infrastructure Misuse</h3>
          <ul>
            <li>Issuing commands that could damage charging equipment</li>
            <li>Manipulating energy consumption or billing data</li>
            <li>Overriding safety protocols or emergency shutdown systems</li>
            <li>Conducting unauthorized load testing on charging infrastructure</li>
            <li>Tampering with PARVATI workload balancing algorithms</li>
          </ul>

          <h3>3.5 Fraudulent Activities</h3>
          <ul>
            <li>Creating false accounts or providing false information</li>
            <li>Manipulating transaction records or billing information</li>
            <li>Engaging in price manipulation or fraud</li>
            <li>Using stolen payment methods or credentials</li>
            <li>Creating fake charging sessions or reports</li>
          </ul>

          <h3>3.6 Illegal Content and Activities</h3>
          <ul>
            <li>Using Kailash for any illegal purpose under Indian law</li>
            <li>Violating intellectual property rights</li>
            <li>Violating export control or sanctions regulations</li>
            <li>Facilitating illegal activities through platform misuse</li>
            <li>Uploading content that violates IT Act 2000 provisions</li>
          </ul>
        </section>

        <section>
          <h2>4. Account Security Responsibilities</h2>
          <p>You are responsible for maintaining the security of your Kailash account:</p>
          <ul>
            <li><strong>Password Protection:</strong> Keep your Decode (password) confidential and secure</li>
            <li><strong>Authorized Access Only:</strong> Do not share your Kailash Code with others</li>
            <li><strong>Device Security:</strong> Use secure devices and networks to access Kailash</li>
            <li><strong>Session Management:</strong> Log out after each session (60-minute timeout applies)</li>
            <li><strong>Suspicious Activity:</strong> Report any unauthorized access immediately to security@go4garage.in</li>
            <li><strong>Multi-Factor Authentication:</strong> Enable 2FA if available for your account</li>
            <li><strong>Regular Password Changes:</strong> Update your password periodically</li>
          </ul>
        </section>

        <section>
          <h2>5. Monitoring and Enforcement</h2>
          <p>
            Go4Garage actively monitors Kailash usage to ensure compliance with this AUP. Our SHIV security 
            system provides 24/7 monitoring for suspicious activities and policy violations.
          </p>
          
          <h3>5.1 Automated Monitoring</h3>
          <ul>
            <li>SHIV guardian agent monitors all system activities</li>
            <li>API usage is logged and analyzed for anomalies</li>
            <li>Failed login attempts trigger security alerts</li>
            <li>Unusual command patterns are flagged for review</li>
            <li>Data access patterns are analyzed for unauthorized behavior</li>
          </ul>

          <h3>5.2 Human Review</h3>
          <ul>
            <li>Security team reviews SHIV alerts daily</li>
            <li>Quarterly audits of user activity logs</li>
            <li>Investigation of reported violations</li>
            <li>Compliance checks for high-risk activities</li>
          </ul>
        </section>

        <section>
          <h2>6. Consequences of Policy Violations</h2>
          <p>Violations of this AUP may result in the following actions:</p>
          
          <h3>6.1 Warning and Remediation</h3>
          <p>Minor or first-time violations:</p>
          <ul>
            <li>Written warning sent to account administrator</li>
            <li>Required acknowledgment of policy</li>
            <li>Mandatory security training</li>
            <li>30-day monitoring period</li>
          </ul>

          <h3>6.2 Account Suspension</h3>
          <p>Repeated or moderate violations:</p>
          <ul>
            <li>Temporary suspension (7-30 days)</li>
            <li>Access restoration contingent on compliance plan</li>
            <li>Increased monitoring for 90 days</li>
            <li>Potential financial penalties for infrastructure damage</li>
          </ul>

          <h3>6.3 Account Termination</h3>
          <p>Serious violations or persistent non-compliance:</p>
          <ul>
            <li>Permanent account termination</li>
            <li>No refund of fees</li>
            <li>Potential legal action</li>
            <li>Reporting to authorities (CERT-In, law enforcement)</li>
          </ul>

          <h3>6.4 Legal Action</h3>
          <p>Criminal violations or significant damage:</p>
          <ul>
            <li>Reporting to Indian law enforcement authorities</li>
            <li>Civil litigation for damages</li>
            <li>Cooperation with CERT-In cybersecurity investigations</li>
            <li>Prosecution under IT Act 2000 (Sections 43, 66, 66B, 66C as applicable)</li>
          </ul>
        </section>

        <section>
          <h2>7. Reporting Violations</h2>
          <p>If you become aware of any violation of this AUP, please report it immediately:</p>
          
          <div className="contact-box">
            <p><strong>Security Violations:</strong></p>
            <p>Email: security@go4garage.in</p>
            <p>Subject: "AUP Violation Report - [Brief Description]"</p>
            <p><strong>Include:</strong> Date/time, description of violation, affected systems, evidence (screenshots if applicable)</p>
          </div>

          <p>All reports are:</p>
          <ul>
            <li>Treated confidentially</li>
            <li>Investigated within 48 hours</li>
            <li>Responded to within 5 business days</li>
            <li>Protected from retaliation (good faith reporting)</li>
          </ul>
        </section>

        <section>
          <h2>8. Compliance with Laws and Regulations</h2>
          <p>In addition to this AUP, you must comply with:</p>
          <ul>
            <li><strong>IT Act 2000:</strong> Information Technology Act and amendments</li>
            <li><strong>DPDP Act 2023:</strong> Digital Personal Data Protection Act</li>
            <li><strong>CERT-In Directions:</strong> Cybersecurity incident reporting requirements</li>
            <li><strong>IS 17017-1:</strong> EV charging safety standards</li>
            <li><strong>Electricity Act 2003:</strong> Grid connection and safety regulations</li>
            <li><strong>BIS Standards:</strong> Equipment certification requirements</li>
          </ul>
        </section>

        <section>
          <h2>9. Updates to This Policy</h2>
          <p>
            Go4Garage reserves the right to update this AUP at any time. Material changes will be communicated via:
          </p>
          <ul>
            <li>Email notification to account administrators</li>
            <li>In-platform notification banner</li>
            <li>Updated "Last Updated" date on this page</li>
          </ul>
          <p>
            Continued use of Kailash after policy updates constitutes acceptance of the revised AUP.
          </p>
        </section>

        <section>
          <h2>10. Your Responsibilities</h2>
          <p>By using Kailash, you agree to:</p>
          <ul>
            <li>Read and understand this Acceptable Use Policy</li>
            <li>Comply with all provisions at all times</li>
            <li>Ensure your team members are aware of and follow this policy</li>
            <li>Report violations promptly</li>
            <li>Cooperate with security investigations</li>
            <li>Accept consequences for policy violations</li>
            <li>Stay informed about policy updates</li>
          </ul>
        </section>

        <section>
          <h2>11. Contact Information</h2>
          <div className="contact-box">
            <p><strong>Go4Garage - Kailash Platform</strong></p>
            <p>General Inquiries: connect@go4garage.in</p>
            <p>Security Issues: security@go4garage.in</p>
            <p>Legal Matters: legal@go4garage.in</p>
          </div>
        </section>
      </div>

      <div className="legal-footer">
        <p>© 2025 Go4Garage. All rights reserved.</p>
        <p>This Acceptable Use Policy is governed by the laws of India.</p>
        <div className="contact-info">
          <p>General Inquiries: connect@go4garage.in</p>
          <p>Legal Matters: legal@go4garage.in</p>
        </div>
      </div>
    </div>
  );
};

export default AcceptableUsePolicy;