import React from 'react';
import './LegalPages.css';

const SLA = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Service Level Agreement (SLA)</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Agreement Overview</h2>
            <p>
              This Service Level Agreement (SLA) defines the performance standards, availability commitments,
              and support obligations that Go4Garage commits to delivering for our Charging Point Command Center platform.
              This SLA applies to all paid service tiers and enterprise customers.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Service Availability</h2>
            <h3>2.1 Uptime Guarantee</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Service Tier</th>
                  <th>Monthly Uptime Commitment</th>
                  <th>Max Downtime/Month</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Standard</td>
                  <td>99.5%</td>
                  <td>3.6 hours</td>
                </tr>
                <tr>
                  <td>Professional</td>
                  <td>99.9%</td>
                  <td>43.2 minutes</td>
                </tr>
                <tr>
                  <td>Enterprise</td>
                  <td>99.95%</td>
                  <td>21.6 minutes</td>
                </tr>
              </tbody>
            </table>

            <h3>2.2 Exclusions from Uptime Calculation</h3>
            <p>Downtime is not counted in the following circumstances:</p>
            <ul>
              <li>Scheduled maintenance windows (notified 48 hours in advance)</li>
              <li>Emergency security patches (notified 2 hours in advance)</li>
              <li>Force majeure events (natural disasters, pandemics, government actions)</li>
              <li>Issues caused by customer's infrastructure or third-party services</li>
              <li>Customer-initiated service suspensions or violations of Terms of Service</li>
              <li>Network issues beyond our control (ISP outages, DDoS attacks)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Performance Metrics</h2>
            <h3>3.1 Response Times</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Operation</th>
                  <th>Target Response Time</th>
                  <th>95th Percentile</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>API Request (read)</td>
                  <td>&lt; 200ms</td>
                  <td>&lt; 500ms</td>
                </tr>
                <tr>
                  <td>API Request (write)</td>
                  <td>&lt; 500ms</td>
                  <td>&lt; 1000ms</td>
                </tr>
                <tr>
                  <td>Dashboard Load Time</td>
                  <td>&lt; 2 seconds</td>
                  <td>&lt; 4 seconds</td>
                </tr>
                <tr>
                  <td>Data Synchronization</td>
                  <td>&lt; 30 seconds</td>
                  <td>&lt; 60 seconds</td>
                </tr>
              </tbody>
            </table>

            <h3>3.2 Data Processing</h3>
            <ul>
              <li><strong>Real-time Analytics:</strong> Data processed and available within 5 minutes</li>
              <li><strong>Report Generation:</strong> Standard reports delivered within 15 minutes</li>
              <li><strong>Batch Processing:</strong> Completed within scheduled time windows</li>
              <li><strong>Data Backup:</strong> Performed daily with 99.99% reliability</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Support Services</h2>
            <h3>4.1 Support Channels and Response Times</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Priority Level</th>
                  <th>Definition</th>
                  <th>Standard Tier</th>
                  <th>Professional Tier</th>
                  <th>Enterprise Tier</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Critical (P1)</td>
                  <td>Complete service outage</td>
                  <td>4 hours</td>
                  <td>1 hour</td>
                  <td>15 minutes</td>
                </tr>
                <tr>
                  <td>High (P2)</td>
                  <td>Major feature unavailable</td>
                  <td>8 hours</td>
                  <td>4 hours</td>
                  <td>1 hour</td>
                </tr>
                <tr>
                  <td>Medium (P3)</td>
                  <td>Minor feature issue</td>
                  <td>24 hours</td>
                  <td>12 hours</td>
                  <td>4 hours</td>
                </tr>
                <tr>
                  <td>Low (P4)</td>
                  <td>General inquiry</td>
                  <td>48 hours</td>
                  <td>24 hours</td>
                  <td>8 hours</td>
                </tr>
              </tbody>
            </table>

            <h3>4.2 Support Availability</h3>
            <ul>
              <li><strong>Standard Tier:</strong> Business hours (9 AM - 6 PM IST, Mon-Fri)</li>
              <li><strong>Professional Tier:</strong> Extended hours (8 AM - 10 PM IST, Mon-Sat)</li>
              <li><strong>Enterprise Tier:</strong> 24/7/365 support with dedicated account manager</li>
            </ul>

            <h3>4.3 Support Channels</h3>
            <ul>
              <li><strong>Email:</strong> support@go4garage.com (all tiers)</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX (Professional and Enterprise)</li>
              <li><strong>Live Chat:</strong> Available through dashboard (Professional and Enterprise)</li>
              <li><strong>Dedicated Slack/Teams Channel:</strong> Enterprise only</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Incident Management</h2>
            <h3>5.1 Incident Response Process</h3>
            <ol>
              <li><strong>Detection:</strong> Automated monitoring detects issue</li>
              <li><strong>Notification:</strong> Customers notified via status page and email</li>
              <li><strong>Investigation:</strong> Engineering team assesses root cause</li>
              <li><strong>Resolution:</strong> Issue fixed and services restored</li>
              <li><strong>Post-Mortem:</strong> Detailed incident report shared within 48 hours</li>
            </ol>

            <h3>5.2 Status Communication</h3>
            <ul>
              <li><strong>Status Page:</strong> status.go4garage.com (real-time updates)</li>
              <li><strong>Email Notifications:</strong> Automatic alerts for subscribed users</li>
              <li><strong>In-App Notifications:</strong> Banner alerts for active sessions</li>
              <li><strong>Update Frequency:</strong> Every 30 minutes during active incidents</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Data Management</h2>
            <h3>6.1 Data Backup and Recovery</h3>
            <ul>
              <li><strong>Backup Frequency:</strong> Continuous backups with 15-minute increments</li>
              <li><strong>Backup Retention:</strong>
                <ul>
                  <li>Daily backups: Retained for 7 days</li>
                  <li>Weekly backups: Retained for 4 weeks</li>
                  <li>Monthly backups: Retained for 12 months</li>
                </ul>
              </li>
              <li><strong>Recovery Time Objective (RTO):</strong>
                <ul>
                  <li>Standard: 24 hours</li>
                  <li>Professional: 4 hours</li>
                  <li>Enterprise: 1 hour</li>
                </ul>
              </li>
              <li><strong>Recovery Point Objective (RPO):</strong>
                <ul>
                  <li>Standard: 1 hour of data loss</li>
                  <li>Professional: 15 minutes of data loss</li>
                  <li>Enterprise: Near-zero data loss</li>
                </ul>
              </li>
            </ul>

            <h3>6.2 Data Export</h3>
            <ul>
              <li>Customers can export their data at any time via dashboard</li>
              <li>Data provided in standard formats (CSV, JSON, XML)</li>
              <li>Export requests processed within 24 hours</li>
              <li>Large exports may be delivered via secure download link</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Security Commitments</h2>
            <ul>
              <li><strong>Encryption:</strong> TLS 1.3 for data in transit, AES-256 for data at rest</li>
              <li><strong>Access Controls:</strong> Role-based access control (RBAC) with audit logs</li>
              <li><strong>Compliance:</strong> ISO 27001, SOC 2 Type II certified annually</li>
              <li><strong>Vulnerability Management:</strong> Quarterly penetration testing</li>
              <li><strong>Incident Response:</strong> Security incidents addressed per Data Breach Policy</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Service Credits</h2>
            <h3>8.1 Eligibility</h3>
            <p>Customers are eligible for service credits if:</p>
            <ul>
              <li>Monthly uptime falls below the committed percentage</li>
              <li>Support response times exceed SLA commitments by more than 50%</li>
              <li>Customer reports the issue within 30 days of occurrence</li>
            </ul>

            <h3>8.2 Credit Calculation</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Monthly Uptime Achieved</th>
                  <th>Service Credit (% of Monthly Fee)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>99.0% - 99.49%</td>
                  <td>10%</td>
                </tr>
                <tr>
                  <td>98.0% - 98.99%</td>
                  <td>25%</td>
                </tr>
                <tr>
                  <td>95.0% - 97.99%</td>
                  <td>50%</td>
                </tr>
                <tr>
                  <td>&lt; 95.0%</td>
                  <td>100%</td>
                </tr>
              </tbody>
            </table>

            <h3>8.3 Credit Request Process</h3>
            <ol>
              <li>Submit credit request to billing@go4garage.com within 30 days</li>
              <li>Include: Account details, incident dates, affected services</li>
              <li>We will verify and respond within 10 business days</li>
              <li>Approved credits applied to next billing cycle</li>
            </ol>

            <p><strong>Maximum Total Credits:</strong> Service credits will not exceed 100% of monthly fees for the affected month.</p>
          </section>

          <section className="legal-section">
            <h2>9. Scheduled Maintenance</h2>
            <ul>
              <li><strong>Frequency:</strong> Typically monthly, during low-traffic periods</li>
              <li><strong>Notification:</strong> 48 hours advance notice via email and status page</li>
              <li><strong>Maintenance Window:</strong> Typically 2-4 AM IST on weekends</li>
              <li><strong>Emergency Maintenance:</strong> 2 hours notice for critical security updates</li>
              <li><strong>Impact:</strong> Partial or full service unavailability during window</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Service Limitations</h2>
            <h3>10.1 Rate Limits</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Service Tier</th>
                  <th>API Requests/Minute</th>
                  <th>Concurrent Sessions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Standard</td>
                  <td>100</td>
                  <td>10</td>
                </tr>
                <tr>
                  <td>Professional</td>
                  <td>500</td>
                  <td>50</td>
                </tr>
                <tr>
                  <td>Enterprise</td>
                  <td>Custom</td>
                  <td>Unlimited</td>
                </tr>
              </tbody>
            </table>

            <h3>10.2 Storage Limits</h3>
            <ul>
              <li><strong>Standard:</strong> 50 GB data storage</li>
              <li><strong>Professional:</strong> 500 GB data storage</li>
              <li><strong>Enterprise:</strong> Custom storage allocation</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Third-Party Dependencies</h2>
            <p>
              This SLA applies only to services directly controlled by Go4Garage. Performance may be affected by:
            </p>
            <ul>
              <li>Customer's internet connectivity</li>
              <li>Third-party APIs and integrations (payment gateways, mapping services)</li>
              <li>Cloud infrastructure providers (subject to their SLAs)</li>
              <li>Customer's device and browser compatibility</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. SLA Review and Updates</h2>
            <p>
              This SLA is reviewed quarterly and may be updated to reflect:
            </p>
            <ul>
              <li>Improvements in service capabilities</li>
              <li>Changes in infrastructure</li>
              <li>Customer feedback and industry best practices</li>
              <li>Regulatory requirements</li>
            </ul>
            <p>
              Material changes will be communicated 30 days in advance. Continued use of services
              constitutes acceptance of the updated SLA.
            </p>
          </section>

          <section className="legal-section">
            <h2>13. Contact Information</h2>
            <p>For SLA-related inquiries:</p>
            <ul>
              <li><strong>Support:</strong> support@go4garage.com</li>
              <li><strong>Billing/Credits:</strong> billing@go4garage.com</li>
              <li><strong>Status Updates:</strong> status.go4garage.com</li>
              <li><strong>Emergency Hotline:</strong> +91-XXX-XXXX-XXX (Enterprise customers)</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For questions about this SLA, contact: support@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default SLA;
