import React from 'react';
import './LegalPages.css';

const CodeOfConduct = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Code of Conduct</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Our Pledge</h2>
            <p>
              We, as members, contributors, and leaders of the Go4Garage community, pledge to make participation
              in our community a harassment-free experience for everyone, regardless of age, body size, visible or
              invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience,
              education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity
              and orientation.
            </p>
            <p>
              We pledge to act and interact in ways that contribute to an open, welcoming, diverse, inclusive,
              and healthy community.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Our Standards</h2>
            <h3>2.1 Expected Behavior</h3>
            <p>Examples of behavior that contributes to a positive environment:</p>
            <ul>
              <li>Demonstrating empathy and kindness toward other people</li>
              <li>Being respectful of differing opinions, viewpoints, and experiences</li>
              <li>Giving and gracefully accepting constructive feedback</li>
              <li>Accepting responsibility and apologizing to those affected by our mistakes</li>
              <li>Focusing on what is best for the overall community</li>
              <li>Using welcoming and inclusive language</li>
              <li>Showing patience with newcomers and less experienced members</li>
            </ul>

            <h3>2.2 Unacceptable Behavior</h3>
            <p>Examples of unacceptable behavior include:</p>
            <ul>
              <li>The use of sexualized language or imagery, and sexual attention or advances of any kind</li>
              <li>Trolling, insulting or derogatory comments, and personal or political attacks</li>
              <li>Public or private harassment</li>
              <li>Publishing others' private information without explicit permission</li>
              <li>Violent threats or language directed against another person</li>
              <li>Sexist, racist, homophobic, transphobic, ableist, or otherwise discriminatory jokes and language</li>
              <li>Posting or displaying sexually explicit or violent material</li>
              <li>Deliberate intimidation, stalking, or following</li>
              <li>Sustained disruption of talks or other events</li>
              <li>Inappropriate physical contact or unwelcome sexual attention</li>
              <li>Advocating for, or encouraging, any of the above behavior</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Scope</h2>
            <p>This Code of Conduct applies within all community spaces, including:</p>
            <ul>
              <li>Official Go4Garage platforms (website, mobile app, forums)</li>
              <li>Social media channels managed by Go4Garage</li>
              <li>Events hosted or sponsored by Go4Garage</li>
              <li>Interactions with official Go4Garage representatives</li>
              <li>Private communications if they affect the community</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Professional Conduct</h2>
            <h3>4.1 Business Interactions</h3>
            <ul>
              <li>Conduct all business dealings with integrity and honesty</li>
              <li>Honor commitments and agreements</li>
              <li>Provide accurate information about products and services</li>
              <li>Respect intellectual property rights</li>
              <li>Maintain confidentiality of sensitive information</li>
            </ul>

            <h3>4.2 Conflicts of Interest</h3>
            <ul>
              <li>Disclose potential conflicts of interest</li>
              <li>Prioritize community benefit over personal gain</li>
              <li>Recuse yourself from decisions where you have conflicts</li>
              <li>Maintain transparency in business relationships</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Inclusive Communication</h2>
            <h3>5.1 Language Guidelines</h3>
            <ul>
              <li>Use gender-neutral language when possible</li>
              <li>Avoid idioms or expressions that may not translate well</li>
              <li>Explain technical jargon for diverse audiences</li>
              <li>Be mindful of cultural differences in communication styles</li>
            </ul>

            <h3>5.2 Accessibility</h3>
            <ul>
              <li>Provide alt text for images</li>
              <li>Use clear, simple language when possible</li>
              <li>Offer content in multiple formats when feasible</li>
              <li>Be patient with communication barriers</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Enforcement Responsibilities</h2>
            <p>
              Community leaders and moderators are responsible for clarifying and enforcing our standards of
              acceptable behavior. They have the right and responsibility to remove, edit, or reject comments,
              commits, code, wiki edits, issues, and other contributions that are not aligned with this Code of Conduct.
            </p>
            <p>
              Moderators will communicate reasons for moderation decisions when appropriate.
            </p>
          </section>

          <section className="legal-section">
            <h2>7. Reporting Guidelines</h2>
            <h3>7.1 How to Report</h3>
            <p>If you experience or witness unacceptable behavior:</p>
            <ul>
              <li><strong>Email:</strong> conduct@go4garage.com</li>
              <li><strong>Anonymous Form:</strong> go4garage.com/report</li>
              <li><strong>In-Person:</strong> Contact any community leader or moderator</li>
            </ul>

            <h3>7.2 What to Include</h3>
            <ul>
              <li>Your contact information (if not anonymous)</li>
              <li>Description of the incident</li>
              <li>Date, time, and location</li>
              <li>Names of people involved (if known)</li>
              <li>Witnesses (if any)</li>
              <li>Any supporting evidence (screenshots, links, etc.)</li>
              <li>Impact of the behavior</li>
            </ul>

            <h3>7.3 Confidentiality</h3>
            <ul>
              <li>Reports handled confidentially</li>
              <li>Information shared only with those involved in resolution</li>
              <li>Reporter identity protected (unless disclosure necessary)</li>
              <li>Anonymous reports accepted but may limit investigation</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Enforcement Process</h2>
            <h3>8.1 Investigation</h3>
            <ol>
              <li>Report received and acknowledged within 24 hours</li>
              <li>Initial assessment of severity and urgency</li>
              <li>Gather information from all parties involved</li>
              <li>Review evidence and witness statements</li>
              <li>Consult with relevant experts if needed</li>
              <li>Make determination within 7-14 days</li>
            </ol>

            <h3>8.2 Possible Actions</h3>
            <ul>
              <li><strong>Warning:</strong> Private or public warning about behavior</li>
              <li><strong>Temporary Ban:</strong> Suspension from community for set period</li>
              <li><strong>Permanent Ban:</strong> Indefinite removal from community</li>
              <li><strong>Event Ban:</strong> Prohibition from attending events</li>
              <li><strong>Revocation of Privileges:</strong> Loss of moderator or contributor status</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Enforcement Guidelines</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Impact Level</th>
                  <th>Consequence</th>
                  <th>Examples</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Minor</td>
                  <td>Correction</td>
                  <td>Use of inappropriate language, unprofessional behavior</td>
                </tr>
                <tr>
                  <td>Moderate</td>
                  <td>Warning</td>
                  <td>Violation through single incident or series of actions</td>
                </tr>
                <tr>
                  <td>Serious</td>
                  <td>Temporary Ban</td>
                  <td>Sustained inappropriate behavior, harassment</td>
                </tr>
                <tr>
                  <td>Severe</td>
                  <td>Permanent Ban</td>
                  <td>Demonstrating pattern of violation, aggression, disparagement</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>10. Appeals Process</h2>
            <p>If you believe an enforcement decision was incorrect:</p>
            <ul>
              <li>Submit appeal to appeals@go4garage.com within 14 days</li>
              <li>Provide new evidence or context</li>
              <li>Appeal reviewed by different moderators</li>
              <li>Decision communicated within 14 days</li>
              <li>Appeal decisions are final</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Support for Affected Parties</h2>
            <p>We provide support to those who experience violations:</p>
            <ul>
              <li>Safe space to discuss the incident</li>
              <li>Resources for emotional support</li>
              <li>Protection from retaliation</li>
              <li>Follow-up to ensure safety and wellbeing</li>
              <li>Assistance with external reporting if desired</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Community Leadership</h2>
            <h3>12.1 Leader Responsibilities</h3>
            <p>Community leaders must:</p>
            <ul>
              <li>Model the behavior outlined in this Code</li>
              <li>Address violations promptly and fairly</li>
              <li>Maintain confidentiality</li>
              <li>Recuse themselves when conflicts exist</li>
              <li>Continuously educate themselves on DEI topics</li>
            </ul>

            <h3>12.2 Leader Accountability</h3>
            <ul>
              <li>Leaders held to higher standards</li>
              <li>Violations by leaders result in immediate review</li>
              <li>Loss of leadership position for serious violations</li>
              <li>Regular performance reviews</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Acknowledgment and Attribution</h2>
            <p>
              This Code of Conduct is adapted from the Contributor Covenant, version 2.1, available at
              https://www.contributor-covenant.org/version/2/1/code_of_conduct.html
            </p>
          </section>

          <section className="legal-section">
            <h2>14. Changes to This Code</h2>
            <p>
              We may revise this Code of Conduct periodically. Changes will be:
            </p>
            <ul>
              <li>Announced via email and platform notifications</li>
              <li>Open for community feedback (30-day comment period)</li>
              <li>Published with changelog and effective date</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>15. Contact Information</h2>
            <ul>
              <li><strong>Report Violations:</strong> conduct@go4garage.com</li>
              <li><strong>Anonymous Reporting:</strong> go4garage.com/report</li>
              <li><strong>Appeals:</strong> appeals@go4garage.com</li>
              <li><strong>Questions:</strong> community@go4garage.com</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>To report violations, contact: conduct@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default CodeOfConduct;
