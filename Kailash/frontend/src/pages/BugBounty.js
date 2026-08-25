import React from 'react';
import './LegalPages.css';

const BugBounty = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Bug Bounty Program</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Program Overview</h2>
            <p>
              Go4Garage welcomes security researchers to help identify vulnerabilities in our platform.
              Our bug bounty program rewards responsible disclosure of security issues.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Scope</h2>
            <h3>2.1 In-Scope Targets</h3>
            <ul>
              <li><strong>Web Application:</strong> *.go4garage.com</li>
              <li><strong>API:</strong> api.go4garage.com</li>
              <li><strong>Mobile Apps:</strong> iOS and Android applications</li>
              <li><strong>Subdomains:</strong> All official subdomains</li>
            </ul>

            <h3>2.2 Out-of-Scope</h3>
            <ul>
              <li>Third-party services and websites</li>
              <li>Physical security testing</li>
              <li>Social engineering of employees</li>
              <li>Denial of Service (DoS/DDoS) attacks</li>
              <li>Spam or content injection</li>
              <li>Customer-owned charging stations</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Eligible Vulnerabilities</h2>
            <h3>3.1 High Priority (Premium Rewards)</h3>
            <ul>
              <li>Remote Code Execution (RCE)</li>
              <li>SQL Injection leading to data access</li>
              <li>Authentication bypass</li>
              <li>Privilege escalation</li>
              <li>Server-Side Request Forgery (SSRF) with impact</li>
              <li>Insecure Direct Object Reference (IDOR) accessing sensitive data</li>
              <li>Account takeover vulnerabilities</li>
            </ul>

            <h3>3.2 Medium Priority</h3>
            <ul>
              <li>Stored Cross-Site Scripting (XSS)</li>
              <li>Reflected XSS with significant impact</li>
              <li>Cross-Site Request Forgery (CSRF) on important actions</li>
              <li>Sensitive data exposure</li>
              <li>Business logic flaws</li>
              <li>API security issues</li>
            </ul>

            <h3>3.3 Low Priority</h3>
            <ul>
              <li>Self-XSS</li>
              <li>Missing security headers (without exploitation)</li>
              <li>Information disclosure (low sensitivity)</li>
              <li>CSRF on non-critical functions</li>
              <li>Clickjacking on non-sensitive pages</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Reward Structure</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Severity</th>
                  <th>Reward Range</th>
                  <th>Criteria</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Critical</td>
                  <td>₹50,000 - ₹2,00,000</td>
                  <td>RCE, authentication bypass, mass data breach</td>
                </tr>
                <tr>
                  <td>High</td>
                  <td>₹20,000 - ₹50,000</td>
                  <td>Privilege escalation, significant IDOR, stored XSS</td>
                </tr>
                <tr>
                  <td>Medium</td>
                  <td>₹5,000 - ₹20,000</td>
                  <td>CSRF, information disclosure, business logic flaws</td>
                </tr>
                <tr>
                  <td>Low</td>
                  <td>₹1,000 - ₹5,000</td>
                  <td>Minor configuration issues, low-impact vulnerabilities</td>
                </tr>
                <tr>
                  <td>Informational</td>
                  <td>Acknowledgment</td>
                  <td>Security recommendations, best practices</td>
                </tr>
              </tbody>
            </table>

            <h3>4.1 Bonus Rewards</h3>
            <ul>
              <li><strong>First Reporter:</strong> Only the first valid report of a vulnerability receives reward</li>
              <li><strong>Quality Report:</strong> Up to 25% bonus for exceptionally detailed reports</li>
              <li><strong>Critical Chains:</strong> Up to 50% bonus for novel exploit chains</li>
              <li><strong>Zero-Day:</strong> Up to 100% bonus for previously unknown vulnerability classes</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Rules of Engagement</h2>
            <h3>5.1 Testing Guidelines</h3>
            <ul>
              <li><strong>Use test accounts:</strong> Do not access real user data</li>
              <li><strong>No disruption:</strong> Do not impact service availability</li>
              <li><strong>Rate limiting:</strong> Respect rate limits and do not spam</li>
              <li><strong>Data handling:</strong> Do not store, share, or destroy data</li>
              <li><strong>Stop if impact:</strong> Immediately cease testing if you cause harm</li>
            </ul>

            <h3>5.2 Responsible Disclosure</h3>
            <ul>
              <li>Report vulnerabilities to bugbounty@go4garage.com</li>
              <li>Allow 90 days for remediation before public disclosure</li>
              <li>Do not publicly disclose without written permission</li>
              <li>Coordinate disclosure timeline with our security team</li>
            </ul>

            <h3>5.3 Prohibited Actions</h3>
            <ul>
              <li>Accessing or modifying other users' data</li>
              <li>Executing DoS/DDoS attacks</li>
              <li>Social engineering or phishing</li>
              <li>Physical attacks on facilities</li>
              <li>Spam, content injection, or SEO manipulation</li>
              <li>Brute forcing credentials or rate limit testing</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Submission Process</h2>
            <h3>6.1 How to Submit</h3>
            <ol>
              <li><strong>Email:</strong> bugbounty@go4garage.com (PGP key available)</li>
              <li><strong>Platform:</strong> HackerOne program (coming soon)</li>
              <li><strong>Subject:</strong> [Bug Bounty] Brief vulnerability description</li>
            </ol>

            <h3>6.2 Report Requirements</h3>
            <p>Include in your report:</p>
            <ul>
              <li><strong>Title:</strong> Clear, concise vulnerability name</li>
              <li><strong>Severity:</strong> Your assessment (Critical/High/Medium/Low)</li>
              <li><strong>Description:</strong> What is the vulnerability?</li>
              <li><strong>Impact:</strong> What can an attacker do?</li>
              <li><strong>Steps to Reproduce:</strong> Detailed, numbered steps</li>
              <li><strong>Proof of Concept:</strong> Code, screenshots, or video</li>
              <li><strong>Environment:</strong> Browser, OS, app version</li>
              <li><strong>Remediation:</strong> Suggested fix (optional but appreciated)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Response Timeline</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Stage</th>
                  <th>Timeline</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Acknowledgment</td>
                  <td>24 hours</td>
                  <td>Confirm receipt of report</td>
                </tr>
                <tr>
                  <td>Initial Triage</td>
                  <td>5 business days</td>
                  <td>Validate and assess severity</td>
                </tr>
                <tr>
                  <td>Investigation</td>
                  <td>10 business days</td>
                  <td>Complete analysis and determine impact</td>
                </tr>
                <tr>
                  <td>Resolution</td>
                  <td>30-90 days</td>
                  <td>Develop, test, and deploy fix</td>
                </tr>
                <tr>
                  <td>Bounty Award</td>
                  <td>Within 30 days of fix</td>
                  <td>Reward determined and processed</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>8. Report Status</h2>
            <p>Your report may receive one of these statuses:</p>
            <ul>
              <li><strong>Accepted:</strong> Valid vulnerability, eligible for reward</li>
              <li><strong>Duplicate:</strong> Already reported by another researcher</li>
              <li><strong>Informational:</strong> Interesting but not a security risk</li>
              <li><strong>Out of Scope:</strong> Target or vulnerability type not covered</li>
              <li><strong>Not Reproducible:</strong> Unable to verify the issue</li>
              <li><strong>Intended Behavior:</strong> Working as designed</li>
              <li><strong>N/A:</strong> Not applicable or insufficient information</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Payment Process</h2>
            <h3>9.1 Payment Methods</h3>
            <ul>
              <li>Bank transfer (India)</li>
              <li>PayPal (international)</li>
              <li>Wire transfer (for high-value rewards)</li>
              <li>Cryptocurrency (upon request)</li>
            </ul>

            <h3>9.2 Tax Requirements</h3>
            <ul>
              <li>Tax forms required for rewards above ₹10,000</li>
              <li>Indian researchers: PAN required</li>
              <li>International researchers: W-8BEN or equivalent</li>
              <li>Taxes are researcher's responsibility</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Legal Safe Harbor</h2>
            <p>
              Go4Garage commits to:
            </p>
            <ul>
              <li>Not pursue legal action against researchers who follow these guidelines</li>
              <li>Work with you to understand and validate the vulnerability</li>
              <li>Recognize your contribution publicly (with permission)</li>
              <li>Keep your identity confidential (if requested)</li>
            </ul>

            <p>
              This safe harbor applies only to security research activities conducted in accordance with
              this program.
            </p>
          </section>

          <section className="legal-section">
            <h2>11. Hall of Fame</h2>
            <p>
              Researchers who discover valid vulnerabilities will be recognized on our Security Hall of Fame:
            </p>
            <ul>
              <li>go4garage.com/security/hall-of-fame</li>
              <li>Listed with permission only</li>
              <li>Recognition on social media (optional)</li>
              <li>Annual top researcher awards</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Ineligible Vulnerabilities</h2>
            <p>The following are not eligible for rewards:</p>
            <ul>
              <li>Vulnerabilities in third-party applications or services</li>
              <li>Vulnerabilities requiring physical access</li>
              <li>Social engineering scenarios</li>
              <li>Issues already known to us</li>
              <li>Vulnerabilities discovered through automated scanning without manual validation</li>
              <li>Issues requiring user interaction with minimal impact</li>
              <li>Best practices violations without security impact</li>
              <li>Outdated software versions (without proof of exploitability)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Program Updates</h2>
            <p>
              We may update this program:
            </p>
            <ul>
              <li>Changes to scope or rewards will be announced 30 days in advance</li>
              <li>Subscribe to updates: bugbounty-updates@go4garage.com</li>
              <li>Follow @Go4GarageSec on Twitter for announcements</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>14. Frequently Asked Questions</h2>
            <h3>Q: Can I test on production systems?</h3>
            <p>A: Yes, but only with non-destructive methods. Do not impact service availability or access real user data.</p>

            <h3>Q: What if I accidentally access user data?</h3>
            <p>A: Immediately stop testing, report the vulnerability, and delete any data. Do not share or store it.</p>

            <h3>Q: Can I automate testing?</h3>
            <p>A: Limited automation is acceptable, but respect rate limits. Manual validation required for rewards.</p>

            <h3>Q: Is there a private bug bounty platform?</h3>
            <p>A: We're launching on HackerOne soon. Currently, email submissions are accepted.</p>
          </section>

          <section className="legal-section">
            <h2>15. Contact</h2>
            <ul>
              <li><strong>Bug Reports:</strong> bugbounty@go4garage.com</li>
              <li><strong>PGP Key:</strong> Available at go4garage.com/security/pgp</li>
              <li><strong>Questions:</strong> security@go4garage.com</li>
              <li><strong>Status Updates:</strong> @Go4GarageSec on Twitter</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>Submit vulnerabilities to: bugbounty@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default BugBounty;
