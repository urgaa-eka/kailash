import React from 'react';
import './LegalPages.css';

const Transparency = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Transparency Report</h1>
          <p className="last-updated">Reporting Period: January - December 2024</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              This transparency report provides detailed information about Go4Garage's data practices, government
              requests, security incidents, and operational statistics. We believe transparency builds trust and
              accountability with our users.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Government and Legal Requests</h2>
            <h3>2.1 Data Requests</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Request Type</th>
                  <th>Received</th>
                  <th>Complied</th>
                  <th>Rejected</th>
                  <th>Pending</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Law Enforcement</td>
                  <td>12</td>
                  <td>8</td>
                  <td>3</td>
                  <td>1</td>
                </tr>
                <tr>
                  <td>Subpoenas</td>
                  <td>5</td>
                  <td>4</td>
                  <td>1</td>
                  <td>0</td>
                </tr>
                <tr>
                  <td>Court Orders</td>
                  <td>3</td>
                  <td>3</td>
                  <td>0</td>
                  <td>0</td>
                </tr>
                <tr>
                  <td>National Security</td>
                  <td>0</td>
                  <td>0</td>
                  <td>0</td>
                  <td>0</td>
                </tr>
              </tbody>
            </table>

            <h3>2.2 User Notifications</h3>
            <ul>
              <li>Users notified: 11 of 20 cases (55%)</li>
              <li>Gag orders preventing notification: 2 cases</li>
              <li>Average notification delay: 45 days</li>
            </ul>

            <h3>2.3 Content Removal Requests</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Request Source</th>
                  <th>Received</th>
                  <th>Removed</th>
                  <th>Rejected</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Copyright (DMCA)</td>
                  <td>8</td>
                  <td>7</td>
                  <td>1</td>
                </tr>
                <tr>
                  <td>Defamation</td>
                  <td>4</td>
                  <td>1</td>
                  <td>3</td>
                </tr>
                <tr>
                  <td>Trademark</td>
                  <td>2</td>
                  <td>2</td>
                  <td>0</td>
                </tr>
                <tr>
                  <td>Other Legal</td>
                  <td>3</td>
                  <td>1</td>
                  <td>2</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>3. Security and Privacy</h2>
            <h3>3.1 Security Incidents</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Incident Type</th>
                  <th>Count</th>
                  <th>Users Affected</th>
                  <th>Resolution Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Data Breach</td>
                  <td>0</td>
                  <td>0</td>
                  <td>N/A</td>
                </tr>
                <tr>
                  <td>Unauthorized Access Attempts</td>
                  <td>247</td>
                  <td>0 (all blocked)</td>
                  <td>Real-time</td>
                </tr>
                <tr>
                  <td>DDoS Attacks</td>
                  <td>3</td>
                  <td>All users (brief)</td>
                  <td>Avg 15 minutes</td>
                </tr>
                <tr>
                  <td>Phishing Attempts</td>
                  <td>18</td>
                  <td>0 (reported by users)</td>
                  <td>24 hours</td>
                </tr>
              </tbody>
            </table>

            <h3>3.2 Vulnerability Disclosures</h3>
            <ul>
              <li>Vulnerabilities reported: 14</li>
              <li>Critical: 1 (patched within 24 hours)</li>
              <li>High: 3 (patched within 7 days)</li>
              <li>Medium: 7 (patched within 30 days)</li>
              <li>Low: 3 (patched within 90 days)</li>
              <li>Bug bounty rewards paid: ₹3,45,000</li>
            </ul>

            <h3>3.3 Data Breaches</h3>
            <p>
              We are pleased to report <strong>zero data breaches</strong> affecting user personal information
              during the reporting period.
            </p>
          </section>

          <section className="legal-section">
            <h2>4. User Data Rights Requests</h2>
            <h3>4.1 GDPR Requests (EU Users)</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Request Type</th>
                  <th>Received</th>
                  <th>Completed</th>
                  <th>Avg. Response Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Data Access</td>
                  <td>142</td>
                  <td>142</td>
                  <td>12 days</td>
                </tr>
                <tr>
                  <td>Data Portability</td>
                  <td>38</td>
                  <td>38</td>
                  <td>8 days</td>
                </tr>
                <tr>
                  <td>Data Deletion</td>
                  <td>67</td>
                  <td>67</td>
                  <td>15 days</td>
                </tr>
                <tr>
                  <td>Data Rectification</td>
                  <td>29</td>
                  <td>29</td>
                  <td>5 days</td>
                </tr>
                <tr>
                  <td>Objection to Processing</td>
                  <td>11</td>
                  <td>11</td>
                  <td>7 days</td>
                </tr>
              </tbody>
            </table>

            <h3>4.2 CCPA Requests (California Users)</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Request Type</th>
                  <th>Received</th>
                  <th>Completed</th>
                  <th>Avg. Response Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Know What Data</td>
                  <td>23</td>
                  <td>23</td>
                  <td>18 days</td>
                </tr>
                <tr>
                  <td>Delete Data</td>
                  <td>15</td>
                  <td>15</td>
                  <td>22 days</td>
                </tr>
                <tr>
                  <td>Opt-Out of Sale</td>
                  <td>7</td>
                  <td>7</td>
                  <td>3 days</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>5. Platform Statistics</h2>
            <h3>5.1 User Metrics</h3>
            <ul>
              <li><strong>Active Users:</strong> 125,000 (up 35% YoY)</li>
              <li><strong>New Registrations:</strong> 45,000</li>
              <li><strong>Account Deletions:</strong> 2,300 (1.8% of total)</li>
              <li><strong>Data Exports:</strong> 890</li>
            </ul>

            <h3>5.2 Platform Activity</h3>
            <ul>
              <li><strong>Charging Sessions:</strong> 1.2 million</li>
              <li><strong>Energy Delivered:</strong> 18 GWh</li>
              <li><strong>CO2 Avoided:</strong> 12,000 metric tons</li>
              <li><strong>API Calls:</strong> 450 million</li>
            </ul>

            <h3>5.3 Content Moderation</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Content Type</th>
                  <th>Reports</th>
                  <th>Removed</th>
                  <th>Warnings Issued</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Spam</td>
                  <td>234</td>
                  <td>198</td>
                  <td>36</td>
                </tr>
                <tr>
                  <td>Harassment</td>
                  <td>45</td>
                  <td>32</td>
                  <td>13</td>
                </tr>
                <tr>
                  <td>Inappropriate Content</td>
                  <td>67</td>
                  <td>54</td>
                  <td>13</td>
                </tr>
                <tr>
                  <td>Misinformation</td>
                  <td>12</td>
                  <td>8</td>
                  <td>4</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>6. Third-Party Data Sharing</h2>
            <h3>6.1 Service Providers</h3>
            <ul>
              <li>Total subprocessors: 23</li>
              <li>New subprocessors added: 4</li>
              <li>Subprocessors removed: 2</li>
              <li>Data Processing Agreements: 100% coverage</li>
            </ul>

            <h3>6.2 Data Shared</h3>
            <p>We share data with third parties only for:</p>
            <ul>
              <li>Service provision (cloud hosting, payment processing)</li>
              <li>Analytics (anonymized and aggregated)</li>
              <li>Legal compliance</li>
              <li>User-authorized integrations</li>
            </ul>
            <p><strong>We do not sell user data to third parties.</strong></p>
          </section>

          <section className="legal-section">
            <h2>7. Diversity and Inclusion</h2>
            <h3>7.1 Workforce Demographics</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Percentage</th>
                  <th>Change YoY</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Women in Workforce</td>
                  <td>38%</td>
                  <td>+5%</td>
                </tr>
                <tr>
                  <td>Women in Leadership</td>
                  <td>32%</td>
                  <td>+8%</td>
                </tr>
                <tr>
                  <td>Women in Tech Roles</td>
                  <td>28%</td>
                  <td>+6%</td>
                </tr>
                <tr>
                  <td>Underrepresented Minorities</td>
                  <td>24%</td>
                  <td>+4%</td>
                </tr>
              </tbody>
            </table>

            <h3>7.2 Pay Equity</h3>
            <ul>
              <li>Gender pay gap: 3% (industry avg: 8%)</li>
              <li>Annual pay equity audit conducted</li>
              <li>Adjustments made for 12 employees</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Environmental Impact</h2>
            <h3>8.1 Carbon Footprint</h3>
            <ul>
              <li><strong>Total Emissions:</strong> 450 tons CO2e (down 15% YoY)</li>
              <li><strong>Scope 1:</strong> 45 tons (direct emissions)</li>
              <li><strong>Scope 2:</strong> 120 tons (electricity)</li>
              <li><strong>Scope 3:</strong> 285 tons (supply chain, travel)</li>
              <li><strong>Carbon Offset:</strong> 500 tons (110% of emissions)</li>
            </ul>

            <h3>8.2 Renewable Energy</h3>
            <ul>
              <li>Renewable energy: 78% of operations (up from 65%)</li>
              <li>Goal: 100% renewable by 2026</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Financial Transparency</h2>
            <h3>9.1 Revenue Breakdown</h3>
            <ul>
              <li>Subscription services: 65%</li>
              <li>Transaction fees: 25%</li>
              <li>Hardware sales: 8%</li>
              <li>Other: 2%</li>
            </ul>

            <h3>9.2 Responsible Investment</h3>
            <ul>
              <li>R&D investment: 18% of revenue</li>
              <li>Security investment: 5% of revenue</li>
              <li>Community programs: 1% of profits</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Customer Support</h2>
            <h3>10.1 Support Metrics</h3>
            <ul>
              <li><strong>Tickets Received:</strong> 45,000</li>
              <li><strong>Avg. First Response Time:</strong> 4 hours</li>
              <li><strong>Avg. Resolution Time:</strong> 18 hours</li>
              <li><strong>Customer Satisfaction:</strong> 4.3/5</li>
              <li><strong>SLA Compliance:</strong> 96%</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Looking Forward</h2>
            <h3>11.1 2025 Commitments</h3>
            <ul>
              <li>Achieve SOC 2 Type II certification</li>
              <li>Expand bug bounty program</li>
              <li>Increase workforce diversity by 10%</li>
              <li>Reach 85% renewable energy usage</li>
              <li>Launch transparency API for enterprise customers</li>
              <li>Publish quarterly transparency updates</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Methodology</h2>
            <p>
              This report includes data from January 1, 2024, to December 31, 2024. Data is collected from
              internal systems, audited by third parties where applicable, and reviewed by our legal and
              compliance teams.
            </p>
          </section>

          <section className="legal-section">
            <h2>13. Feedback</h2>
            <p>
              We welcome feedback on this transparency report:
            </p>
            <ul>
              <li><strong>Email:</strong> transparency@go4garage.com</li>
              <li><strong>Survey:</strong> go4garage.com/transparency-feedback</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For transparency inquiries, contact: transparency@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default Transparency;
