import React from 'react';
import './LegalPages.css';

const SecurityPolicy = () => {
  return (
    <div className="legal-document-container">
      <div className="legal-header">
        <h1>Security Policy</h1>
        <p className="last-updated">Last Updated: January 15, 2025</p>
      </div>
      
      <div className="legal-content">
        <section>
          <h2>1. Security Commitment</h2>
          <p>
            Go4Garage is committed to maintaining the highest standards of information security for the Kailash platform. 
            This Security Policy outlines our approach to protecting critical EV charging infrastructure data, user information, 
            and system integrity against evolving cyber threats.
          </p>
          <p>
            Kailash manages mission-critical charging operations. Security is not just a feature—it's the foundation 
            of our platform. This policy details our multi-layered security architecture designed to protect against 
            unauthorized access, data breaches, and operational disruptions.
          </p>
        </section>

        <section>
          <h2>2. SHIV Guardian System</h2>
          <p>
            SHIV is our AI-powered security guardian that provides 24/7 monitoring and threat detection:
          </p>
          
          <h3>2.1 Real-Time Monitoring</h3>
          <ul>
            <li><strong>System Health:</strong> Continuous monitoring of all platform components</li>
            <li><strong>Threat Detection:</strong> AI-powered anomaly detection and pattern recognition</li>
            <li><strong>Access Monitoring:</strong> Real-time tracking of authentication attempts and user activities</li>
            <li><strong>API Security:</strong> Request analysis for suspicious patterns or attacks</li>
            <li><strong>Infrastructure Monitoring:</strong> Charging station communication security</li>
          </ul>

          <h3>2.2 Threat Response</h3>
          <ul>
            <li><strong>Automatic Blocking:</strong> Immediate blocking of detected threats</li>
            <li><strong>Alert System:</strong> Real-time notifications to security team</li>
            <li><strong>Incident Logging:</strong> Comprehensive logs of all security events</li>
            <li><strong>Adaptive Defense:</strong> Learning from attack patterns to strengthen security</li>
          </ul>
        </section>

        <section>
          <h2>3. Data Encryption</h2>
          
          <h3>3.1 Encryption at Rest</h3>
          <p>All data stored in Kailash is encrypted:</p>
          <ul>
            <li><strong>Algorithm:</strong> AES-256 encryption (industry standard)</li>
            <li><strong>Database:</strong> MongoDB encrypted storage with field-level encryption for sensitive data</li>
            <li><strong>Backups:</strong> Encrypted using same standards as primary storage</li>
            <li><strong>Key Management:</strong> Separate key management system with role-based access</li>
            <li><strong>Key Rotation:</strong> Encryption keys rotated every 90 days</li>
          </ul>

          <h3>3.2 Encryption in Transit</h3>
          <p>All data transmission is secured:</p>
          <ul>
            <li><strong>Protocol:</strong> TLS 1.3 (latest standard)</li>
            <li><strong>API Calls:</strong> HTTPS only, HTTP automatically redirected</li>
            <li><strong>Certificates:</strong> 2048-bit SSL certificates with automatic renewal</li>
            <li><strong>Perfect Forward Secrecy:</strong> Session keys not compromised if long-term keys leaked</li>
            <li><strong>HSTS:</strong> HTTP Strict Transport Security enabled</li>
          </ul>
        </section>

        <section>
          <h2>4. Authentication and Access Control</h2>
          
          <h3>4.1 User Authentication</h3>
          <ul>
            <li><strong>Kailash Code System:</strong> Unique identifier (e.g., {'<REDACTED_kailash_code>'})</li>
            <li><strong>Password Policy:</strong> Minimum 12 characters, complexity requirements</li>
            <li><strong>Password Hashing:</strong> Bcrypt with salt (14 rounds)</li>
            <li><strong>Session Management:</strong> 60-minute timeout, secure session tokens</li>
            <li><strong>Multi-Factor Authentication:</strong> Available for high-security accounts</li>
            <li><strong>Failed Attempts:</strong> Account lockout after 5 failed attempts (15-minute lockout)</li>
          </ul>

          <h3>4.2 Role-Based Access Control (RBAC)</h3>
          <ul>
            <li><strong>Principle of Least Privilege:</strong> Users granted minimum necessary permissions</li>
            <li><strong>Role Hierarchy:</strong> Admin, Manager, Operator, Viewer</li>
            <li><strong>Permission Granularity:</strong> Fine-grained control over resources</li>
            <li><strong>Access Reviews:</strong> Quarterly review of user permissions</li>
            <li><strong>Audit Logs:</strong> All access attempts logged and monitored</li>
          </ul>

          <h3>4.3 API Security</h3>
          <ul>
            <li><strong>Authentication:</strong> JWT tokens with 1-hour expiration</li>
            <li><strong>API Keys:</strong> Secure key generation and rotation</li>
            <li><strong>Rate Limiting:</strong> Protection against API abuse (1000 requests/hour default)</li>
            <li><strong>IP Whitelisting:</strong> Optional restriction to specific IP ranges</li>
            <li><strong>OAuth 2.0:</strong> Standard protocol for third-party integrations</li>
          </ul>
        </section>

        <section>
          <h2>5. Infrastructure Security</h2>
          
          <h3>5.1 Cloud Infrastructure</h3>
          <ul>
            <li><strong>Hosting:</strong> MongoDB Atlas with data stored in Indian data centers</li>
            <li><strong>Network Isolation:</strong> Virtual Private Cloud (VPC) configuration</li>
            <li><strong>Firewall:</strong> Stateful firewall with strict ingress/egress rules</li>
            <li><strong>DDoS Protection:</strong> Automatic mitigation of distributed denial-of-service attacks</li>
            <li><strong>Intrusion Detection:</strong> IDS/IPS systems monitoring network traffic</li>
          </ul>

          <h3>5.2 Application Security</h3>
          <ul>
            <li><strong>Secure Development:</strong> OWASP Top 10 compliance</li>
            <li><strong>Input Validation:</strong> Sanitization of all user inputs</li>
            <li><strong>SQL Injection:</strong> Parameterized queries, no dynamic SQL</li>
            <li><strong>XSS Protection:</strong> Output encoding, Content Security Policy</li>
            <li><strong>CSRF Protection:</strong> Token-based validation for state-changing operations</li>
            <li><strong>Dependency Scanning:</strong> Automated vulnerability scanning of third-party libraries</li>
          </ul>

          <h3>5.3 Physical Security</h3>
          <ul>
            <li><strong>Data Center:</strong> ISO 27001 certified facilities in India</li>
            <li><strong>Access Control:</strong> Biometric access, 24/7 security personnel</li>
            <li><strong>Surveillance:</strong> CCTV monitoring of all entry points</li>
            <li><strong>Environmental:</strong> Fire suppression, climate control, power redundancy</li>
          </ul>
        </section>

        <section>
          <h2>6. Security Monitoring and Logging</h2>
          
          <h3>6.1 Comprehensive Logging</h3>
          <ul>
            <li><strong>Authentication Logs:</strong> All login attempts (successful and failed)</li>
            <li><strong>Access Logs:</strong> Resource access with timestamps and user IDs</li>
            <li><strong>API Logs:</strong> All API calls with request/response metadata</li>
            <li><strong>System Logs:</strong> Application errors, warnings, and events</li>
            <li><strong>Security Logs:</strong> SHIV alerts, blocked threats, anomalies</li>
            <li><strong>Retention:</strong> Logs retained for 2 years (CERT-In compliance)</li>
          </ul>

          <h3>6.2 Security Information and Event Management (SIEM)</h3>
          <ul>
            <li><strong>Centralized Logging:</strong> All logs aggregated for analysis</li>
            <li><strong>Real-Time Analysis:</strong> Automated correlation of security events</li>
            <li><strong>Alert Generation:</strong> Automatic alerts for suspicious activities</li>
            <li><strong>Threat Intelligence:</strong> Integration with threat intelligence feeds</li>
          </ul>
        </section>

        <section>
          <h2>7. Vulnerability Management</h2>
          
          <h3>7.1 Vulnerability Scanning</h3>
          <ul>
            <li><strong>Automated Scans:</strong> Weekly vulnerability scans</li>
            <li><strong>Penetration Testing:</strong> Annual third-party penetration tests</li>
            <li><strong>Dependency Checks:</strong> Daily scans of third-party libraries</li>
            <li><strong>CVSS Scoring:</strong> Prioritization based on severity</li>
          </ul>

          <h3>7.2 Patch Management</h3>
          <ul>
            <li><strong>Critical Patches:</strong> Applied within 24 hours of availability</li>
            <li><strong>High Priority:</strong> Applied within 7 days</li>
            <li><strong>Medium/Low:</strong> Applied during monthly maintenance window</li>
            <li><strong>Testing:</strong> All patches tested in staging before production</li>
            <li><strong>Rollback Plan:</strong> Documented rollback procedures for all changes</li>
          </ul>
        </section>

        <section>
          <h2>8. Incident Response</h2>
          
          <h3>8.1 Incident Response Team</h3>
          <ul>
            <li><strong>Composition:</strong> Security engineer, DevOps, Management, Legal</li>
            <li><strong>Availability:</strong> 24/7 on-call rotation</li>
            <li><strong>Training:</strong> Quarterly incident response drills</li>
            <li><strong>Communication:</strong> Defined escalation and notification procedures</li>
          </ul>

          <h3>8.2 Response Timeline</h3>
          <ul>
            <li><strong>Detection:</strong> Immediate (automated SHIV alerts)</li>
            <li><strong>Assessment:</strong> Within 15 minutes of detection</li>
            <li><strong>Containment:</strong> Within 1 hour for critical incidents</li>
            <li><strong>Notification:</strong> Users notified within 24 hours (data breach)</li>
            <li><strong>Resolution:</strong> Based on severity (Critical: 4 hours, High: 24 hours)</li>
            <li><strong>Post-Mortem:</strong> Within 72 hours of resolution</li>
          </ul>

          <h3>8.3 CERT-In Compliance</h3>
          <ul>
            <li><strong>Reporting:</strong> Cybersecurity incidents reported to CERT-In within 6 hours</li>
            <li><strong>Categories:</strong> As per CERT-In Directions 2022</li>
            <li><strong>Information:</strong> Incident details, affected systems, remediation actions</li>
            <li><strong>Updates:</strong> Status updates provided as investigation progresses</li>
          </ul>
        </section>

        <section>
          <h2>9. Data Backup and Recovery</h2>
          
          <h3>9.1 Backup Strategy</h3>
          <ul>
            <li><strong>Frequency:</strong> Daily automated backups</li>
            <li><strong>Retention:</strong> 30 daily, 12 weekly, 7 annual backups</li>
            <li><strong>Encryption:</strong> All backups encrypted at rest</li>
            <li><strong>Geo-Redundancy:</strong> Backups stored in multiple Indian data centers</li>
            <li><strong>Testing:</strong> Monthly backup restoration tests</li>
          </ul>

          <h3>9.2 Disaster Recovery</h3>
          <ul>
            <li><strong>RTO (Recovery Time Objective):</strong> 4 hours for critical systems</li>
            <li><strong>RPO (Recovery Point Objective):</strong> 1 hour (maximum data loss)</li>
            <li><strong>Failover:</strong> Automated failover to secondary systems</li>
            <li><strong>DR Drills:</strong> Quarterly disaster recovery simulations</li>
          </ul>
        </section>

        <section>
          <h2>10. Third-Party Security</h2>
          
          <h3>10.1 Vendor Assessment</h3>
          <ul>
            <li><strong>Security Review:</strong> All vendors undergo security assessment</li>
            <li><strong>Compliance:</strong> Vendors must meet ISO 27001 or equivalent</li>
            <li><strong>Contracts:</strong> Data Processing Agreements (DPAs) required</li>
            <li><strong>Audits:</strong> Annual security audits of critical vendors</li>
          </ul>

          <h3>10.2 Current Third Parties</h3>
          <ul>
            <li><strong>MongoDB Atlas:</strong> Database (SOC 2 Type II, ISO 27001)</li>
            <li><strong>Anthropic:</strong> AI processing (secure API, no data retention)</li>
          </ul>
        </section>

        <section>
          <h2>11. Employee Security</h2>
          
          <h3>11.1 Security Training</h3>
          <ul>
            <li><strong>Onboarding:</strong> Security awareness training for all new employees</li>
            <li><strong>Annual Training:</strong> Mandatory yearly security refresher</li>
            <li><strong>Phishing Simulations:</strong> Quarterly phishing awareness tests</li>
            <li><strong>Incident Response:</strong> Specialized training for security team</li>
          </ul>

          <h3>11.2 Access Management</h3>
          <ul>
            <li><strong>Provisioning:</strong> Access granted based on role requirements</li>
            <li><strong>Deprovisioning:</strong> Access revoked immediately upon termination</li>
            <li><strong>Reviews:</strong> Quarterly access reviews for all employees</li>
            <li><strong>Privileged Access:</strong> Additional controls for admin access</li>
          </ul>
        </section>

        <section>
          <h2>12. Compliance and Certifications</h2>
          <ul>
            <li><strong>IT Act 2000:</strong> Reasonable security practices (Section 43A)</li>
            <li><strong>DPDP Act 2023:</strong> Data protection compliance</li>
            <li><strong>CERT-In Directions:</strong> Incident reporting and log retention</li>
            <li><strong>ISO 27001:</strong> Target certification (in progress)</li>
            <li><strong>IS 17017-1:</strong> EV charging safety standards</li>
          </ul>
        </section>

        <section>
          <h2>13. Security Reporting</h2>
          <p>Report security vulnerabilities or incidents:</p>
          <div className="contact-box emergency">
            <p><strong>URGENT: Security Incidents</strong></p>
            <p>Email: security@go4garage.in</p>
            <p>Subject: "SECURITY INCIDENT - [Brief Description]"</p>
            <p><strong>Response Time:</strong> Within 1 hour for critical incidents</p>
          </div>

          <h3>Responsible Disclosure</h3>
          <ul>
            <li>Report vulnerabilities to security@go4garage.in</li>
            <li>Provide detailed reproduction steps</li>
            <li>Allow 90 days for remediation before public disclosure</li>
            <li>Acknowledgment of security researchers (with permission)</li>
          </ul>
        </section>

        <section>
          <h2>14. Policy Updates</h2>
          <p>
            This Security Policy is reviewed and updated quarterly or when significant changes occur. 
            Material updates will be communicated to users.
          </p>
        </section>

        <section>
          <h2>15. Contact Information</h2>
          <div className="contact-box">
            <p><strong>Go4Garage - Kailash Platform</strong></p>
            <p>Security Inquiries: security@go4garage.in</p>
            <p>General Inquiries: connect@go4garage.in</p>
            <p>Legal Matters: legal@go4garage.in</p>
          </div>
        </section>
      </div>

      <div className="legal-footer">
        <p>© 2025 Go4Garage. All rights reserved.</p>
        <p>This Security Policy complies with IT Act 2000, DPDP Act 2023, and CERT-In Directions 2022.</p>
        <div className="contact-info">
          <p>General Inquiries: connect@go4garage.in</p>
          <p>Security: security@go4garage.in</p>
        </div>
      </div>
    </div>
  );
};

export default SecurityPolicy;