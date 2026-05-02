import React from 'react';
import './LegalPages.css';

const ShippingPolicy = () => {
  return (
    <div className="legal-page">
      <div className="legal-container">
        <header className="legal-header">
          <h1>Shipping and Delivery Policy</h1>
          <p className="last-updated">Last Updated: January 2025</p>
        </header>

        <div className="legal-content">
          <section className="legal-section">
            <h2>1. Overview</h2>
            <p>
              This Shipping and Delivery Policy applies to physical products ordered through the Go4Garage platform,
              including charging equipment, accessories, and hardware components.
            </p>
          </section>

          <section className="legal-section">
            <h2>2. Shipping Zones and Timeframes</h2>
            <table className="sla-table">
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Location</th>
                  <th>Processing Time</th>
                  <th>Delivery Time</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Metro Cities</td>
                  <td>Delhi, Mumbai, Bangalore, etc.</td>
                  <td>1-2 business days</td>
                  <td>3-5 business days</td>
                </tr>
                <tr>
                  <td>Urban Areas</td>
                  <td>Tier-2 cities</td>
                  <td>1-2 business days</td>
                  <td>5-7 business days</td>
                </tr>
                <tr>
                  <td>Rural Areas</td>
                  <td>Remote locations</td>
                  <td>2-3 business days</td>
                  <td>7-14 business days</td>
                </tr>
                <tr>
                  <td>International</td>
                  <td>Select countries</td>
                  <td>3-5 business days</td>
                  <td>10-21 business days</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section className="legal-section">
            <h2>3. Shipping Methods</h2>
            <h3>3.1 Standard Shipping</h3>
            <ul>
              <li><strong>Cost:</strong> Calculated based on weight and destination</li>
              <li><strong>Tracking:</strong> Provided via email and SMS</li>
              <li><strong>Carrier:</strong> India Post, Blue Dart, Delhivery</li>
            </ul>

            <h3>3.2 Express Shipping</h3>
            <ul>
              <li><strong>Cost:</strong> Premium rate (2-3x standard)</li>
              <li><strong>Delivery:</strong> 2-3 business days within India</li>
              <li><strong>Carrier:</strong> FedEx, DHL, Blue Dart Express</li>
            </ul>

            <h3>3.3 Installation Services</h3>
            <ul>
              <li>Available for charging equipment</li>
              <li>Scheduled separately after delivery</li>
              <li>Performed by certified technicians</li>
              <li>Additional charges apply</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>4. Shipping Costs</h2>
            <p>Shipping costs are calculated based on:</p>
            <ul>
              <li>Product weight and dimensions</li>
              <li>Delivery destination</li>
              <li>Shipping method selected</li>
              <li>Order value (free shipping on orders above ₹10,000)</li>
            </ul>

            <h3>4.1 Free Shipping Eligibility</h3>
            <ul>
              <li>Orders above ₹10,000 within India</li>
              <li>Enterprise customers (all orders)</li>
              <li>Promotional periods (as announced)</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>5. Order Processing</h2>
            <ol>
              <li><strong>Order Confirmation:</strong> Email sent within 24 hours</li>
              <li><strong>Processing:</strong> 1-3 business days</li>
              <li><strong>Dispatch:</strong> Notification with tracking details</li>
              <li><strong>Delivery:</strong> Based on selected shipping method</li>
            </ol>
          </section>

          <section className="legal-section">
            <h2>6. Tracking Orders</h2>
            <p>Track your order through:</p>
            <ul>
              <li><strong>Dashboard:</strong> Real-time tracking in your account</li>
              <li><strong>Email:</strong> Automated updates at each stage</li>
              <li><strong>SMS:</strong> Key milestone notifications</li>
              <li><strong>Carrier Website:</strong> Direct tracking via carrier portal</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>7. Delivery Procedures</h2>
            <h3>7.1 Standard Delivery</h3>
            <ul>
              <li>Signature required for orders above ₹5,000</li>
              <li>Photo ID verification for high-value items</li>
              <li>Inspection allowed before acceptance</li>
              <li>3 delivery attempts before return to sender</li>
            </ul>

            <h3>7.2 Failed Delivery</h3>
            <p>If delivery fails:</p>
            <ul>
              <li>You'll receive notification via SMS/email</li>
              <li>Rescheduling options provided</li>
              <li>Pickup from carrier depot available</li>
              <li>Return to sender after 3 failed attempts</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>8. International Shipping</h2>
            <p>For international orders:</p>
            <ul>
              <li><strong>Availability:</strong> Select countries only</li>
              <li><strong>Customs:</strong> Customer responsible for duties and taxes</li>
              <li><strong>Documentation:</strong> May require additional paperwork</li>
              <li><strong>Restrictions:</strong> Some products not available for export</li>
              <li><strong>Currency:</strong> All charges in INR or USD</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>9. Product Availability</h2>
            <p>In case of unavailability:</p>
            <ul>
              <li>You'll be notified within 48 hours</li>
              <li>Options: wait for restock, substitute product, or refund</li>
              <li>No charges for order cancellation due to unavailability</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>10. Damaged or Lost Shipments</h2>
            <h3>10.1 Damaged Packages</h3>
            <p>If your package arrives damaged:</p>
            <ol>
              <li>Do not accept the delivery</li>
              <li>Take photos of the damaged package</li>
              <li>Report to support@go4garage.com within 24 hours</li>
              <li>We'll arrange replacement or refund</li>
            </ol>

            <h3>10.2 Lost Shipments</h3>
            <p>If your package is lost:</p>
            <ul>
              <li>Contact us if delivery is delayed beyond estimated date + 7 days</li>
              <li>We'll investigate with the carrier</li>
              <li>Replacement or refund processed within 10 business days</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>11. Address Changes</h2>
            <p>To change delivery address:</p>
            <ul>
              <li>Contact us within 24 hours of order placement</li>
              <li>Changes possible before dispatch only</li>
              <li>Email: orders@go4garage.com</li>
              <li>Additional charges may apply for address correction</li>
            </ul>
          </section>

          <section className="legal-section">
            <h2>12. Holidays and Weather</h2>
            <p>
              Shipping may be delayed during:
            </p>
            <ul>
              <li>National holidays and festivals</li>
              <li>Extreme weather conditions</li>
              <li>Force majeure events</li>
              <li>Peak shopping seasons</li>
            </ul>
            <p>We'll communicate any expected delays proactively.</p>
          </section>

          <section className="legal-section">
            <h2>13. Contact Information</h2>
            <p>For shipping inquiries:</p>
            <ul>
              <li><strong>Email:</strong> orders@go4garage.com</li>
              <li><strong>Phone:</strong> +91-XXX-XXXX-XXX</li>
              <li><strong>Hours:</strong> Mon-Sat, 9 AM - 6 PM IST</li>
            </ul>
          </section>
        </div>

        <footer className="legal-footer">
          <p>For shipping questions, contact: orders@go4garage.com</p>
          <p>Go4Garage Charging Point &copy; 2025. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default ShippingPolicy;
