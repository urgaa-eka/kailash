import React from 'react';
import './LegalPages.css';

const WarrantyPolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Warranty Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Warranty Overview</h2>
            <p>
              Go4Garage provides comprehensive warranty coverage for all hardware products sold through our platform.
              This warranty covers defects in materials and workmanship under normal use.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Warranty Periods</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Product Category</th>
                  <th>Standard Warranty</th>
                  <th>Extended Warranty Available</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>EV Charging Stations</td>
                  <td>3 years</td>
                  <td>Up to 5 years</td>
                </tr>
                <tr>
                  <td>Charging Cables</td>
                  <td>1 year</td>
                  <td>Up to 2 years</td>
                </tr>
                <tr>
                  <td>Controllers & Electronics</td>
                  <td>2 years</td>
                  <td>Up to 3 years</td>
                </tr>
                <tr>
                  <td>Accessories</td>
                  <td>6 months</td>
                  <td>Up to 1 year</td>
                </tr>
                <tr>
                  <td>Installation Services</td>
                  <td>1 year</td>
                  <td>N/A</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>3. What Is Covered</h2>
            <p>The warranty covers:</p>
            <ul>
              <li>Manufacturing defects</li>
              <li>Faulty components</li>
              <li>Workmanship issues</li>
              <li>Functional failures under normal use</li>
              <li>Parts and labor for covered repairs</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. What Is Not Covered</h2>
            <p>The warranty does not cover:</p>
            <ul>
              <li><strong>Normal Wear and Tear:</strong> Cosmetic damage, scratches, fading</li>
              <li><strong>Misuse:</strong> Damage from improper use or installation</li>
              <li><strong>Environmental:</strong> Damage from lightning, floods, fire, or extreme weather</li>
              <li><strong>Unauthorized Modifications:</strong> Repairs or alterations by non-certified personnel</li>
              <li><strong>Third-Party Products:</strong> Components not supplied by Go4Garage</li>
              <li><strong>Commercial Abuse:</strong> Use beyond specified capacity</li>
              <li><strong>Lack of Maintenance:</strong> Failure to follow maintenance guidelines</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Warranty Claim Process</h2>
            <h3>Step 1: Contact Support</h3>
            <ul>
              <li>Email: warranty@go4garage.com</li>
              <li>Include: Purchase order number, product details, issue description</li>
              <li>Attach: Photos/videos of the issue</li>
            </ul>

            <h3>Step 2: Initial Assessment</h3>
            <ul>
              <li>Support team reviews your claim within 24-48 hours</li>
              <li>May request additional information or diagnostics</li>
              <li>Remote troubleshooting attempted first</li>
            </ul>

            <h3>Step 3: Authorization</h3>
            <ul>
              <li>Warranty claim approved or denied with explanation</li>
              <li>Return authorization (RMA) number issued if replacement needed</li>
              <li>Instructions provided for return shipping</li>
            </ul>

            <h3>Step 4: Resolution</h3>
            <p>Depending on the issue:</p>
            <ul>
              <li><strong>Repair:</strong> Product repaired and returned within 10-15 business days</li>
              <li><strong>Replacement:</strong> New product shipped within 5-7 business days</li>
              <li><strong>Refund:</strong> Processed within 10 business days (if irreparable)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>6. Warranty Validation</h2>
            <p>To validate your warranty, you must provide:</p>
            <ul>
              <li>Original purchase receipt or invoice</li>
              <li>Product serial number</li>
              <li>Warranty registration (if applicable)</li>
              <li>Proof of proper installation (for charging stations)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Return Shipping</h2>
            <h3>7.1 Covered Under Warranty</h3>
            <ul>
              <li>Go4Garage covers return shipping costs</li>
              <li>Pre-paid shipping label provided</li>
              <li>Use original packaging if possible</li>
            </ul>

            <h3>7.2 Not Covered Under Warranty</h3>
            <ul>
              <li>Customer responsible for shipping costs</li>
              <li>Option to have product inspected for repair quote</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. Extended Warranty</h2>
            <p>Extended warranty plans offer:</p>
            <ul>
              <li>Coverage beyond standard warranty period</li>
              <li>Priority support and faster turnaround</li>
              <li>Accidental damage protection (optional add-on)</li>
              <li>Annual preventive maintenance (for charging stations)</li>
            </ul>

            <h3>8.1 Purchasing Extended Warranty</h3>
            <ul>
              <li>Must be purchased within 30 days of original purchase</li>
              <li>Available at checkout or through customer portal</li>
              <li>Pricing varies by product category</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. On-Site Service</h2>
            <p>For installed charging stations:</p>
            <ul>
              <li><strong>Metro Cities:</strong> On-site service within 48-72 hours</li>
              <li><strong>Other Areas:</strong> Within 5-7 business days</li>
              <li><strong>Remote Diagnostics:</strong> Attempted first to save time</li>
              <li><strong>Replacement Units:</strong> Provided if repair takes longer than 5 days</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Transferability</h2>
            <p>
              Warranty is transferable to subsequent owners if:
            </p>
            <ul>
              <li>Product is properly registered with Go4Garage</li>
              <li>Transfer is reported within 30 days</li>
              <li>Transfer fee may apply (₹500 for hardware)</li>
              <li>Original proof of purchase is provided</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Limitation of Liability</h2>
            <p>
              THIS WARRANTY IS IN LIEU OF ALL OTHER WARRANTIES, EXPRESS OR IMPLIED. OUR LIABILITY IS LIMITED TO
              REPAIR, REPLACEMENT, OR REFUND OF THE PRODUCT PRICE. WE ARE NOT LIABLE FOR:
            </p>
            <ul>
              <li>Consequential or incidental damages</li>
              <li>Loss of use, revenue, or profit</li>
              <li>Property damage from product failure</li>
              <li>Third-party claims</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Warranty Registration</h2>
            <p>Register your product for warranty benefits:</p>
            <ul>
              <li>Online: go4garage.com/warranty-registration</li>
              <li>Required within 30 days of purchase</li>
              <li>Faster claim processing for registered products</li>
              <li>Automatic notifications for recalls or updates</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>13. Warranty Contact</h2>
            <p>For warranty support:</p>
            <ul>
              <li><strong>Email:</strong> warranty@go4garage.com</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX</li>
              <li><strong>Hours:</strong> Mon-Sat, 9 AM - 6 PM IST</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For warranty inquiries, contact: warranty@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default WarrantyPolicy;
