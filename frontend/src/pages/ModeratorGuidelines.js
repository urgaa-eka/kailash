import React from 'react';
import './LegalPages.css';

const ModeratorGuidelines = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Moderator Guidelines</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Introduction</h2>
            <p>
              This document provides guidance for Go4Garage community moderators. Moderators play a crucial role
              in maintaining a safe, respectful, and productive environment for all users.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Moderator Responsibilities</h2>
            <ul>
              <li>Enforce Community Guidelines fairly and consistently</li>
              <li>Review and respond to user reports promptly</li>
              <li>Remove content that violates policies</li>
              <li>Issue warnings, suspensions, or bans as appropriate</li>
              <li>Document all moderation actions</li>
              <li>Communicate decisions clearly to affected users</li>
              <li>Escalate complex cases to senior moderators</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Core Principles</h2>
            <h3>3.1 Fairness</h3>
            <ul>
              <li>Apply rules consistently to all users</li>
              <li>No favoritism or bias</li>
              <li>Consider context and intent</li>
              <li>Treat similar cases similarly</li>
            </ul>

            <h3>3.2 Transparency</h3>
            <ul>
              <li>Explain reasons for moderation actions</li>
              <li>Provide clear communication</li>
              <li>Document decisions for review</li>
              <li>Be open about moderator identity</li>
            </ul>

            <h3>3.3 Respect</h3>
            <ul>
              <li>Treat all users with dignity</li>
              <li>Remain professional in all interactions</li>
              <li>Listen to user concerns</li>
              <li>Avoid personal conflicts</li>
            </ul>

            <h3>3.4 Accountability</h3>
            <ul>
              <li>Take responsibility for actions</li>
              <li>Accept feedback and corrections</li>
              <li>Participate in regular reviews</li>
              <li>Continuously improve practices</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Decision-Making Framework</h2>
            <h3>4.1 Assessment Criteria</h3>
            <p>When reviewing content or behavior, consider:</p>
            <ul>
              <li><strong>Severity:</strong> How serious is the violation?</li>
              <li><strong>Intent:</strong> Was it deliberate or accidental?</li>
              <li><strong>Context:</strong> What were the circumstances?</li>
              <li><strong>History:</strong> Past behavior and violations</li>
              <li><strong>Impact:</strong> Harm caused to community or individuals</li>
            </ul>

            <h3>4.2 Action Matrix</h3>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Violation Type</th>
                  <th>First Offense</th>
                  <th>Second Offense</th>
                  <th>Third Offense</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Minor (spam, off-topic)</td>
                  <td>Warning</td>
                  <td>Content removal + warning</td>
                  <td>7-day suspension</td>
                </tr>
                <tr>
                  <td>Moderate (disrespect, mild harassment)</td>
                  <td>Content removal + warning</td>
                  <td>7-day suspension</td>
                  <td>30-day suspension</td>
                </tr>
                <tr>
                  <td>Serious (threats, hate speech)</td>
                  <td>30-day suspension</td>
                  <td>Permanent ban</td>
                  <td>-</td>
                </tr>
                <tr>
                  <td>Severe (illegal activity, doxxing)</td>
                  <td>Immediate permanent ban</td>
                  <td>-</td>
                  <td>-</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>5. Content Moderation</h2>
            <h3>5.1 Review Queue Priority</h3>
            <ol>
              <li><strong>Urgent:</strong> Illegal content, doxxing, threats (immediate action)</li>
              <li><strong>High:</strong> Harassment, hate speech (within 1 hour)</li>
              <li><strong>Medium:</strong> Spam, inappropriate content (within 4 hours)</li>
              <li><strong>Low:</strong> Minor violations, disputes (within 24 hours)</li>
            </ol>

            <h3>5.2 Content Removal Criteria</h3>
            <p>Remove content that:</p>
            <ul>
              <li>Violates Community Guidelines</li>
              <li>Contains illegal material</li>
              <li>Poses safety risks</li>
              <li>Infringes intellectual property</li>
              <li>Contains personal information without consent</li>
            </ul>

            <h3>5.3 Preserving Evidence</h3>
            <p>Before removing severe violations:</p>
            <ul>
              <li>Take screenshots for records</li>
              <li>Document URLs and timestamps</li>
              <li>Save copies in moderation logs</li>
              <li>May be needed for legal proceedings</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. User Communication</h2>
            <h3>6.1 Notification Templates</h3>
            <p>Use standardized templates for:</p>
            <ul>
              <li>Warnings</li>
              <li>Content removal notices</li>
              <li>Suspension notifications</li>
              <li>Ban notifications</li>
              <li>Appeal responses</li>
            </ul>

            <h3>6.2 Communication Best Practices</h3>
            <ul>
              <li>Be clear and specific about violations</li>
              <li>Cite relevant policy sections</li>
              <li>Explain the action taken</li>
              <li>Provide path to appeal if applicable</li>
              <li>Remain professional and neutral in tone</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Escalation Procedures</h2>
            <h3>7.1 When to Escalate</h3>
            <p>Escalate to senior moderators when:</p>
            <ul>
              <li>Uncertain about appropriate action</li>
              <li>High-profile users involved</li>
              <li>Legal implications present</li>
              <li>Complex or precedent-setting cases</li>
              <li>Potential for significant community impact</li>
              <li>Personal conflict of interest</li>
            </ul>

            <h3>7.2 Escalation Process</h3>
            <ol>
              <li>Document the case thoroughly</li>
              <li>Tag senior moderator in internal system</li>
              <li>Provide context and your assessment</li>
              <li>Await guidance before taking action</li>
              <li>Implement decided course of action</li>
            </ol>
          </section>

          <section className="legal-section">
            <h2>8. Appeals Handling</h2>
            <h3>8.1 Review Process</h3>
            <ol>
              <li>Verify original decision was documented</li>
              <li>Review user's appeal reasoning</li>
              <li>Examine any new evidence</li>
              <li>Consult with original moderator if different</li>
              <li>Make impartial determination</li>
              <li>Communicate decision clearly</li>
            </ol>

            <h3>8.2 Grounds for Overturning</h3>
            <ul>
              <li>New evidence changes circumstances</li>
              <li>Original decision was based on incorrect information</li>
              <li>Policy was misapplied</li>
              <li>Punishment was disproportionate</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Conflict of Interest</h2>
            <h3>9.1 Disclosure Requirements</h3>
            <p>Recuse yourself from cases involving:</p>
            <ul>
              <li>Friends or family members</li>
              <li>Business relationships</li>
              <li>Personal disputes</li>
              <li>Financial interests</li>
            </ul>

            <h3>9.2 Recusal Process</h3>
            <ol>
              <li>Recognize potential conflict</li>
              <li>Immediately notify senior moderator</li>
              <li>Transfer case to unaffected moderator</li>
              <li>Document recusal in case notes</li>
            </ol>
          </section>

          <section className="legal-section">
            <h2>10. Privacy and Confidentiality</h2>
            <ul>
              <li>Do not share user information externally</li>
              <li>Keep moderation discussions confidential</li>
              <li>Do not discuss specific cases publicly</li>
              <li>Secure access to moderation tools</li>
              <li>Report any security breaches immediately</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Tool Usage</h2>
            <h3>11.1 Moderation Tools</h3>
            <ul>
              <li><strong>Content Queue:</strong> Review reported content</li>
              <li><strong>User Management:</strong> Issue warnings, suspensions, bans</li>
              <li><strong>Logs:</strong> Document all actions</li>
              <li><strong>Templates:</strong> Standardized communication</li>
              <li><strong>Analytics:</strong> Track moderation metrics</li>
            </ul>

            <h3>11.2 Tool Security</h3>
            <ul>
              <li>Never share moderator credentials</li>
              <li>Use strong, unique passwords</li>
              <li>Enable two-factor authentication</li>
              <li>Log out when finished</li>
              <li>Report suspicious activity</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Self-Care and Burnout Prevention</h2>
            <p>Moderating can be emotionally taxing:</p>
            <ul>
              <li>Take regular breaks</li>
              <li>Seek support from other moderators</li>
              <li>Report to coordinators if overwhelmed</li>
              <li>Use available mental health resources</li>
              <li>Maintain work-life balance</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Performance Expectations</h2>
            <h3>13.1 Metrics</h3>
            <ul>
              <li><strong>Response Time:</strong> 90% of reports handled within SLA</li>
              <li><strong>Accuracy:</strong> Less than 5% of decisions overturned on appeal</li>
              <li><strong>Consistency:</strong> Align with team average for similar cases</li>
              <li><strong>Documentation:</strong> 100% of actions properly logged</li>
            </ul>

            <h3>13.2 Reviews</h3>
            <ul>
              <li>Quarterly performance reviews</li>
              <li>Random case audits</li>
              <li>Peer feedback sessions</li>
              <li>Continuous training opportunities</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>14. Training and Development</h2>
            <ul>
              <li>Complete onboarding training</li>
              <li>Participate in monthly training sessions</li>
              <li>Stay updated on policy changes</li>
              <li>Share knowledge with team</li>
              <li>Pursue specialized training as needed</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>15. Contact</h2>
            <p>For moderator support:</p>
            <ul>
              <li><strong>Coordinator:</strong> moderators@go4garage.com</li>
              <li><strong>Emergency:</strong> emergency@go4garage.com</li>
              <li><strong>Training:</strong> training@go4garage.com</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For moderator support, contact: moderators@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default ModeratorGuidelines;
