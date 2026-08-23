import React from 'react';
import './LegalPages.css';

const IncidentResponse = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Incident Response Plan</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Overview</h2>
            <p>
              This Incident Response Plan outlines our procedures for detecting, responding to, and recovering from
              security incidents that may affect the Go4Garage platform and user data.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Incident Response Team</h2>
            <h3>2.1 Core Team Members</h3>
            <ul>
              <li><strong>Incident Commander:</strong> Overall incident management</li>
              <li><strong>Security Lead:</strong> Technical investigation and remediation</li>
              <li><strong>Communications Lead:</strong> Internal and external communications</li>
              <li><strong>Legal Counsel:</strong> Legal implications and compliance</li>
              <li><strong>PR/Marketing:</strong> Public relations and brand protection</li>
              <li><strong>Customer Support Lead:</strong> User communication and support</li>
            </ul>

            <h3>2.2 On-Call Rotation</h3>
            <ul>
              <li>24/7 on-call security engineer</li>
              <li>Weekly rotation schedule</li>
              <li>Backup contacts for each role</li>
              <li>Escalation procedures documented</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Incident Classification</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Definition</th>
                  <th>Response Time</th>
                  <th>Examples</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Critical (P0)</td>
                  <td>Active breach with confirmed data exposure</td>
                  <td>Immediate</td>
                  <td>Ransomware, data theft, complete system compromise</td>
                </tr>
                <tr>
                  <td>High (P1)</td>
                  <td>Potential breach or significant vulnerability</td>
                  <td>15 minutes</td>
                  <td>Unauthorized access attempts, DDoS attack, zero-day exploit</td>
                </tr>
                <tr>
                  <td>Medium (P2)</td>
                  <td>Security concern requiring investigation</td>
                  <td>1 hour</td>
                  <td>Suspicious activity, minor data leak, failed security controls</td>
                </tr>
                <tr>
                  <td>Low (P3)</td>
                  <td>Policy violation or minor security issue</td>
                  <td>4 hours</td>
                  <td>Phishing attempts, minor misconfigurations, low-risk vulnerabilities</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>4. Detection Methods</h2>
            <ul>
              <li><strong>Automated Monitoring:</strong> SIEM alerts, IDS/IPS, anomaly detection</li>
              <li><strong>Log Analysis:</strong> Continuous review of system and application logs</li>
              <li><strong>Security Tools:</strong> Vulnerability scanners, threat intelligence feeds</li>
              <li><strong>User Reports:</strong> Security concerns reported by users or employees</li>
              <li><strong>Third-Party Alerts:</strong> Notifications from partners or researchers</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Incident Response Phases</h2>
            <h3>Phase 1: Preparation (Ongoing)</h3>
            <ul>
              <li>Maintain incident response procedures</li>
              <li>Regular training and drills</li>
              <li>Keep contact lists updated</li>
              <li>Ensure tools and access are ready</li>
              <li>Maintain backups and recovery capabilities</li>
            </ul>

            <h3>Phase 2: Detection and Analysis (0-1 hour)</h3>
            <ol>
              <li><strong>Alert Received:</strong> Incident detected via monitoring or report</li>
              <li><strong>Initial Assessment:</strong> Determine severity and scope</li>
              <li><strong>Team Activation:</strong> Notify appropriate team members</li>
              <li><strong>Evidence Collection:</strong> Preserve logs, screenshots, forensic data</li>
              <li><strong>Preliminary Analysis:</strong> Identify attack vector and compromised systems</li>
            </ol>

            <h3>Phase 3: Containment (1-4 hours)</h3>
            <ul>
              <li><strong>Short-term:</strong>
                <ul>
                  <li>Isolate affected systems</li>
                  <li>Block malicious IPs/domains</li>
                  <li>Disable compromised accounts</li>
                  <li>Implement emergency patches</li>
                </ul>
              </li>
              <li><strong>Long-term:</strong>
                <ul>
                  <li>Apply permanent fixes</li>
                  <li>Rebuild compromised systems</li>
                  <li>Update security controls</li>
                </ul>
              </li>
            </ul>

            <h3>Phase 4: Eradication (4-24 hours)</h3>
            <ul>
              <li>Remove malware and unauthorized access</li>
              <li>Close security vulnerabilities</li>
              <li>Strengthen weak security controls</li>
              <li>Verify complete removal of threat</li>
              <li>Update indicators of compromise (IOCs)</li>
            </ul>

            <h3>Phase 5: Recovery (24-72 hours)</h3>
            <ul>
              <li>Restore systems to normal operation</li>
              <li>Verify system integrity</li>
              <li>Monitor for recurring issues</li>
              <li>Restore data from clean backups if needed</li>
              <li>Gradually restore user access</li>
            </ul>

            <h3>Phase 6: Post-Incident Activity (1-2 weeks)</h3>
            <ul>
              <li>Complete incident documentation</li>
              <li>Conduct post-mortem analysis</li>
              <li>Identify lessons learned</li>
              <li>Update procedures and controls</li>
              <li>Implement preventive measures</li>
              <li>Prepare final incident report</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Communication Procedures</h2>
            <h3>6.1 Internal Communication</h3>
            <ul>
              <li><strong>War Room:</strong> Dedicated Slack/Teams channel</li>
              <li><strong>Status Updates:</strong> Every 2 hours during active incident</li>
              <li><strong>Executive Briefings:</strong> For P0/P1 incidents</li>
              <li><strong>All-Hands:</strong> After resolution if company-wide impact</li>
            </ul>

            <h3>6.2 Customer Communication</h3>
            <ul>
              <li><strong>Status Page:</strong> Real-time updates on status.go4garage.com</li>
              <li><strong>Email Notifications:</strong> For affected users (within 72 hours for data breaches)</li>
              <li><strong>In-App Banners:</strong> Service disruption notices</li>
              <li><strong>Support Channels:</strong> Prepared FAQs and responses</li>
            </ul>

            <h3>6.3 Regulatory Notification</h3>
            <ul>
              <li><strong>Data Protection Authorities:</strong> Within 72 hours (GDPR)</li>
              <li><strong>Law Enforcement:</strong> For criminal activity</li>
              <li><strong>Affected Partners:</strong> Within 24 hours if their data affected</li>
            </ul>

            <h3>6.4 Media Relations</h3>
            <ul>
              <li>All media inquiries directed to PR lead</li>
              <li>Prepared holding statements</li>
              <li>No speculation about ongoing incidents</li>
              <li>Coordinated messaging across channels</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Evidence Preservation</h2>
            <ul>
              <li>Chain of custody documentation</li>
              <li>Forensic image creation of affected systems</li>
              <li>Log preservation and analysis</li>
              <li>Screenshot and video capture</li>
              <li>Secure storage of evidence</li>
              <li>Maintain for legal proceedings</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Legal Considerations</h2>
            <ul>
              <li>Attorney-client privilege for sensitive communications</li>
              <li>Compliance with breach notification laws</li>
              <li>Coordination with law enforcement</li>
              <li>Litigation hold procedures</li>
              <li>Insurance claim processes</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Recovery Priorities</h2>
            <h3>9.1 Critical Systems (RTO: 1 hour)</h3>
            <ul>
              <li>Authentication services</li>
              <li>Core platform functionality</li>
              <li>Payment processing</li>
              <li>Customer-facing APIs</li>
            </ul>

            <h3>9.2 High Priority (RTO: 4 hours)</h3>
            <ul>
              <li>Charging station management</li>
              <li>Customer dashboard</li>
              <li>Support systems</li>
              <li>Monitoring and alerting</li>
            </ul>

            <h3>9.3 Standard Priority (RTO: 24 hours)</h3>
            <ul>
              <li>Analytics and reporting</li>
              <li>Marketing systems</li>
              <li>Internal tools</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Testing and Drills</h2>
            <ul>
              <li><strong>Tabletop Exercises:</strong> Quarterly scenario-based discussions</li>
              <li><strong>Simulations:</strong> Semi-annual full incident simulation</li>
              <li><strong>Red Team Exercises:</strong> Annual penetration testing</li>
              <li><strong>Plan Reviews:</strong> Monthly procedure updates</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Third-Party Coordination</h2>
            <ul>
              <li><strong>Cloud Providers:</strong> AWS, Google Cloud incident response</li>
              <li><strong>Security Vendors:</strong> Threat intelligence partners</li>
              <li><strong>Forensics:</strong> External incident response firms on retainer</li>
              <li><strong>Legal:</strong> External counsel for complex incidents</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Reporting a Security Incident</h2>
            <p>If you discover a security incident or vulnerability:</p>
            <ul>
              <li><strong>Emergency Hotline:</strong> +91-XXX-XXXX-XXX (24/7)</li>
              <li><strong>Email:</strong> security@go4garage.com</li>
              <li><strong>Responsible Disclosure:</strong> security-disclosure@go4garage.com</li>
              <li><strong>Response Time:</strong> Acknowledgment within 1 hour</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Continuous Improvement</h2>
            <ul>
              <li>Post-incident review reports</li>
              <li>Lessons learned database</li>
              <li>Procedure updates based on findings</li>
              <li>Training improvements</li>
              <li>Tool and technology enhancements</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>To report a security incident: security@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default IncidentResponse;
