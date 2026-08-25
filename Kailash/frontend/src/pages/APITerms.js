import React from 'react';
import './LegalPages.css';

const APITerms = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>API Terms of Use</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              These API Terms govern your access to and use of the Go4Garage API. By accessing our API, you agree
              to comply with these terms in addition to our main Terms of Service.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. API Access</h2>
            <h3>2.1 Registration</h3>
            <ul>
              <li>API access requires approved developer account</li>
              <li>Valid API key must be used for all requests</li>
              <li>API keys are confidential and non-transferable</li>
              <li>Each application requires separate API key</li>
            </ul>

            <h3>2.2 Authentication</h3>
            <ul>
              <li>OAuth 2.0 for user-authorized actions</li>
              <li>API key authentication for service-to-service calls</li>
              <li>JWT tokens for session management</li>
              <li>Refresh tokens valid for 30 days</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Rate Limits</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Tier</th>
                  <th>Requests/Minute</th>
                  <th>Daily Limit</th>
                  <th>Burst Allowance</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Free</td>
                  <td>60</td>
                  <td>10,000</td>
                  <td>100 req/min for 1 min</td>
                </tr>
                <tr>
                  <td>Basic</td>
                  <td>300</td>
                  <td>100,000</td>
                  <td>500 req/min for 2 min</td>
                </tr>
                <tr>
                  <td>Professional</td>
                  <td>1,000</td>
                  <td>1,000,000</td>
                  <td>2,000 req/min for 5 min</td>
                </tr>
                <tr>
                  <td>Enterprise</td>
                  <td>Custom</td>
                  <td>Unlimited</td>
                  <td>Custom</td>
                </tr>
              </tbody>
            </table>

            <h3>3.1 Rate Limit Response</h3>
            <p>When rate limit is exceeded:</p>
            <ul>
              <li>HTTP 429 (Too Many Requests) returned</li>
              <li>Retry-After header indicates wait time</li>
              <li>X-RateLimit headers provide current status</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Acceptable Use</h2>
            <h3>4.1 Permitted Uses</h3>
            <ul>
              <li>Building applications that integrate with Go4Garage</li>
              <li>Creating value-added services for users</li>
              <li>Internal business intelligence and analytics</li>
              <li>Educational and research purposes</li>
            </ul>

            <h3>4.2 Prohibited Uses</h3>
            <ul>
              <li>Scraping or systematic data extraction</li>
              <li>Reverse engineering the API or platform</li>
              <li>Competing directly with Go4Garage services</li>
              <li>Reselling API access without authorization</li>
              <li>Circumventing rate limits or security measures</li>
              <li>Transmitting malware or malicious code</li>
              <li>Violating user privacy or data protection laws</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Data Usage and Privacy</h2>
            <h3>5.1 Data Access</h3>
            <p>You may access:</p>
            <ul>
              <li>Data you own or have permission to access</li>
              <li>Public data as per API documentation</li>
              <li>User-authorized data via OAuth flow</li>
            </ul>

            <h3>5.2 Data Storage and Caching</h3>
            <ul>
              <li>Cache data for reasonable periods (max 24 hours for non-static data)</li>
              <li>Respect cache-control headers</li>
              <li>Delete cached data when requested</li>
              <li>Do not create permanent copies of user data</li>
            </ul>

            <h3>5.3 Privacy Obligations</h3>
            <ul>
              <li>Comply with applicable data protection laws</li>
              <li>Maintain privacy policy for your application</li>
              <li>Obtain necessary user consents</li>
              <li>Implement appropriate security measures</li>
              <li>Report data breaches within 24 hours</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. API Availability</h2>
            <h3>6.1 Uptime</h3>
            <ul>
              <li><strong>Target Uptime:</strong> 99.9% monthly</li>
              <li><strong>Scheduled Maintenance:</strong> Announced 48 hours in advance</li>
              <li><strong>Status Page:</strong> api-status.go4garage.com</li>
            </ul>

            <h3>6.2 Deprecation Policy</h3>
            <ul>
              <li>Major version supported for minimum 12 months after new version release</li>
              <li>Deprecation notices provided 6 months in advance</li>
              <li>Migration guides published for breaking changes</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Versioning</h2>
            <ul>
              <li><strong>Current Version:</strong> v2.0</li>
              <li><strong>URL Format:</strong> https://api.go4garage.com/v2/</li>
              <li><strong>Version Compatibility:</strong> Backward compatible within major version</li>
              <li><strong>Breaking Changes:</strong> Require new major version</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Attribution and Branding</h2>
            <h3>8.1 Required Attribution</h3>
            <ul>
              <li>Display "Powered by Go4Garage" in your application</li>
              <li>Link to go4garage.com where appropriate</li>
              <li>Use approved logos and branding (available in developer portal)</li>
            </ul>

            <h3>8.2 Trademark Usage</h3>
            <ul>
              <li>Do not modify Go4Garage logos</li>
              <li>Do not imply endorsement without permission</li>
              <li>Do not use Go4Garage in your application name without approval</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. API Monitoring</h2>
            <p>We monitor API usage for:</p>
            <ul>
              <li>Performance optimization</li>
              <li>Abuse detection</li>
              <li>Compliance with terms</li>
              <li>Usage analytics</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Support and Documentation</h2>
            <h3>10.1 Documentation</h3>
            <ul>
              <li><strong>Developer Portal:</strong> developers.go4garage.com</li>
              <li><strong>API Reference:</strong> Comprehensive endpoint documentation</li>
              <li><strong>Code Examples:</strong> Sample implementations in multiple languages</li>
              <li><strong>Changelog:</strong> Updated with all API changes</li>
            </ul>

            <h3>10.2 Support Channels</h3>
            <ul>
              <li><strong>Email:</strong> api-support@go4garage.com</li>
              <li><strong>Community Forum:</strong> community.go4garage.com/api</li>
              <li><strong>Status Updates:</strong> @Go4GarageAPI on Twitter</li>
              <li><strong>Enterprise Support:</strong> Dedicated Slack channel</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Fees and Billing</h2>
            <h3>11.1 Pricing Tiers</h3>
            <ul>
              <li><strong>Free:</strong> ₹0/month (rate limited)</li>
              <li><strong>Basic:</strong> ₹2,999/month</li>
              <li><strong>Professional:</strong> ₹9,999/month</li>
              <li><strong>Enterprise:</strong> Custom pricing</li>
            </ul>

            <h3>11.2 Overage Charges</h3>
            <ul>
              <li>Charged for usage beyond tier limits</li>
              <li>₹0.01 per additional API call</li>
              <li>Billed monthly in arrears</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Security Requirements</h2>
            <ul>
              <li>Use HTTPS for all API requests</li>
              <li>Secure storage of API keys (environment variables, key management services)</li>
              <li>Implement proper error handling</li>
              <li>Regular security audits of your application</li>
              <li>Prompt patching of vulnerabilities</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Liability and Warranties</h2>
            <p>
              API IS PROVIDED "AS IS" WITHOUT WARRANTIES. WE ARE NOT LIABLE FOR:
            </p>
            <ul>
              <li>Service interruptions or errors</li>
              <li>Data loss or corruption</li>
              <li>Third-party integrations</li>
              <li>Your application's functionality</li>
              <li>Damages from API changes</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>14. Termination</h2>
            <h3>14.1 Your Rights</h3>
            <ul>
              <li>Stop using API at any time</li>
              <li>Export your data before termination</li>
              <li>Cancel subscription with 30 days notice</li>
            </ul>

            <h3>14.2 Our Rights</h3>
            <p>We may suspend or terminate access for:</p>
            <ul>
              <li>Violation of these terms</li>
              <li>Non-payment</li>
              <li>Security concerns</li>
              <li>Illegal activity</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>15. Changes to Terms</h2>
            <p>
              We may modify these API Terms with 30 days notice. Continued use after changes constitutes acceptance.
              Material changes affecting functionality will have 90 days notice.
            </p>
          </section>

          <section className="legal-section">
            <h2>16. Contact</h2>
            <ul>
              <li><strong>API Support:</strong> api-support@go4garage.com</li>
              <li><strong>Legal:</strong> legal@go4garage.com</li>
              <li><strong>Security:</strong> security@go4garage.com</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For API questions, contact: api-support@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default APITerms;
