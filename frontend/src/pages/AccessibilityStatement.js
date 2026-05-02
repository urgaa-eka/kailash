import React from 'react';
import './LegalPages.css';

const AccessibilityStatement = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Accessibility Statement</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Our Commitment</h2>
            <p>
              Go4Garage is committed to ensuring digital accessibility for people with disabilities. We are
              continually improving the user experience for everyone and applying the relevant accessibility standards.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Conformance Status</h2>
            <p>
              We aim to conform to the Web Content Accessibility Guidelines (WCAG) 2.1 Level AA. These guidelines
              explain how to make web content more accessible for people with disabilities.
            </p>
            <ul>
              <li><strong>WCAG 2.1 Level A:</strong> Fully conformant</li>
              <li><strong>WCAG 2.1 Level AA:</strong> Partially conformant</li>
              <li><strong>Target:</strong> Full Level AA conformance by Q2 2025</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>3. Accessibility Features</h2>
            <h3>3.1 Keyboard Navigation</h3>
            <ul>
              <li>All interactive elements accessible via keyboard</li>
              <li>Logical tab order throughout the site</li>
              <li>Visible focus indicators</li>
              <li>Skip navigation links</li>
            </ul>

            <h3>3.2 Screen Reader Support</h3>
            <ul>
              <li>Semantic HTML markup</li>
              <li>ARIA labels and landmarks</li>
              <li>Alternative text for images</li>
              <li>Descriptive link text</li>
            </ul>

            <h3>3.3 Visual Design</h3>
            <ul>
              <li>Sufficient color contrast (WCAG AA standard)</li>
              <li>Resizable text up to 200%</li>
              <li>No information conveyed by color alone</li>
              <li>Responsive design for different screen sizes</li>
            </ul>

            <h3>3.4 Multimedia</h3>
            <ul>
              <li>Captions for videos</li>
              <li>Transcripts for audio content</li>
              <li>Audio descriptions where applicable</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Compatible Technologies</h2>
            <p>Our platform is designed to work with:</p>
            <ul>
              <li><strong>Browsers:</strong> Latest versions of Chrome, Firefox, Safari, Edge</li>
              <li><strong>Screen Readers:</strong> JAWS, NVDA, VoiceOver, TalkBack</li>
              <li><strong>Operating Systems:</strong> Windows, macOS, iOS, Android</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Known Limitations</h2>
            <p>Despite our efforts, some limitations may exist:</p>
            <ul>
              <li>Third-party embedded content may not be fully accessible</li>
              <li>Some PDF documents may require remediation</li>
              <li>Older browser versions may have limited support</li>
            </ul>
            <p>We are actively working to address these limitations.</p>
          </section>

          <section className="legal-section">
            <h2>6. Ongoing Efforts</h2>
            <p>We continuously work to improve accessibility through:</p>
            <ul>
              <li>Regular accessibility audits and testing</li>
              <li>User testing with people with disabilities</li>
              <li>Employee training on accessibility best practices</li>
              <li>Incorporating accessibility into our development process</li>
              <li>Staying updated with WCAG guidelines and best practices</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Feedback and Assistance</h2>
            <p>
              We welcome your feedback on the accessibility of our platform. If you encounter accessibility
              barriers, please contact us:
            </p>
            <ul>
              <li><strong>Email:</strong> accessibility@go4garage.com</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX</li>
              <li><strong>Response Time:</strong> Within 2 business days</li>
            </ul>
            <p>
              Please include:
            </p>
            <ul>
              <li>The specific page or feature</li>
              <li>The problem you encountered</li>
              <li>Your browser and assistive technology details</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Alternative Formats</h2>
            <p>
              If you require information in an alternative format, we can provide:
            </p>
            <ul>
              <li>Large print documents</li>
              <li>Audio recordings</li>
              <li>Accessible PDF versions</li>
              <li>Plain text email versions</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Technical Specifications</h2>
            <p>Our accessibility relies on the following technologies:</p>
            <ul>
              <li>HTML5</li>
              <li>WAI-ARIA</li>
              <li>CSS3</li>
              <li>JavaScript (with graceful degradation)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Compliance and Standards</h2>
            <p>We strive to comply with:</p>
            <ul>
              <li><strong>WCAG 2.1 Level AA:</strong> Web accessibility standard</li>
              <li><strong>Section 508:</strong> U.S. federal accessibility requirements</li>
              <li><strong>EN 301 549:</strong> European accessibility standard</li>
              <li><strong>ADA:</strong> Americans with Disabilities Act</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For accessibility support, contact: accessibility@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default AccessibilityStatement;
