import React from 'react';
import './LegalPages.css';

const RefundPolicy = () => {
  return (
    <div className="legal-document-container">
      <div className="legal-header">
        <h1>Refund and Cancellation Policy</h1>
        <p className="last-updated">Last Updated: January 15, 2025</p>
      </div>
      
      <div className="legal-content">
        <section>
          <h2>1. Overview</h2>
          <p>
            This Refund and Cancellation Policy governs refund requests for Kailash platform services provided 
            by Go4Garage. We are committed to ensuring customer satisfaction while maintaining fair business 
            practices for our EV charging infrastructure management services.
          </p>
          <p>
            Kailash is an enterprise platform for managing electric vehicle charging operations. This policy 
            applies to subscription fees, usage charges, and any other payments made for Kailash services.
          </p>
        </section>

        <section>
          <h2>2. Subscription Services</h2>
          
          <h3>2.1 Free Trial Period</h3>
          <ul>
            <li><strong>Duration:</strong> 14-day free trial for new enterprise customers</li>
            <li><strong>Access:</strong> Full platform features during trial</li>
            <li><strong>Cancellation:</strong> Cancel anytime during trial with no charges</li>
            <li><strong>Data:</strong> Trial data retained for 30 days after trial ends</li>
            <li><strong>Conversion:</strong> Automatic conversion to paid plan unless cancelled</li>
          </ul>

          <h3>2.2 Monthly Subscriptions</h3>
          <ul>
            <li><strong>Billing Cycle:</strong> Monthly recurring on subscription start date</li>
            <li><strong>Cancellation Window:</strong> Cancel anytime, effective end of current billing period</li>
            <li><strong>No Refunds:</strong> No refund for partial month usage after billing</li>
            <li><strong>Access:</strong> Full access maintained until end of paid period</li>
            <li><strong>Reactivation:</strong> Can reactivate within 60 days without data loss</li>
          </ul>

          <h3>2.3 Annual Subscriptions</h3>
          <ul>
            <li><strong>Billing Cycle:</strong> Paid annually in advance</li>
            <li><strong>Discount:</strong> 20% discount compared to monthly billing</li>
            <li><strong>Refund Eligibility:</strong> Pro-rata refund if cancelled within first 60 days</li>
            <li><strong>After 60 Days:</strong> No refund, but service continues until term end</li>
            <li><strong>Renewal:</strong> Auto-renewal notice sent 30 days before expiry</li>
          </ul>
        </section>

        <section>
          <h2>3. Usage-Based Charges</h2>
          
          <h3>3.1 Charging Session Fees</h3>
          <p>Fees for actual charging sessions managed through Kailash:</p>
          <ul>
            <li><strong>Non-Refundable:</strong> Completed charging sessions are not refundable</li>
            <li><strong>Failed Sessions:</strong> Full refund if technical error prevented charging</li>
            <li><strong>Partial Charges:</strong> Pro-rated refund for interrupted sessions (system error only)</li>
            <li><strong>Dispute Window:</strong> Report issues within 7 days of transaction</li>
          </ul>

          <h3>3.2 API Usage Fees</h3>
          <ul>
            <li><strong>Billing:</strong> Monthly based on API call volume</li>
            <li><strong>Refund:</strong> Credit issued if system downtime exceeds SLA</li>
            <li><strong>Overages:</strong> No refund for accidentally exceeded limits</li>
            <li><strong>Disputes:</strong> Review usage logs with customer support</li>
          </ul>
        </section>

        <section>
          <h2>4. Refund Eligibility Criteria</h2>
          
          <h3>4.1 Eligible for Refund</h3>
          <p>Refunds are provided in these situations:</p>
          <ul>
            <li><strong>Service Failure:</strong> Platform unavailable for >24 consecutive hours</li>
            <li><strong>Billing Error:</strong> Incorrect charge amount or duplicate billing</li>
            <li><strong>Unauthorized Charge:</strong> Transaction not initiated by account holder</li>
            <li><strong>Early Cancellation:</strong> Annual plan cancelled within 60 days (pro-rata refund)</li>
            <li><strong>SLA Breach:</strong> Failure to meet guaranteed uptime (credit applied)</li>
            <li><strong>Technical Issues:</strong> System error causing loss of service</li>
          </ul>

          <h3>4.2 Not Eligible for Refund</h3>
          <p>Refunds will not be provided for:</p>
          <ul>
            <li>Change of mind after free trial period</li>
            <li>Lack of usage or non-utilization of platform</li>
            <li>Third-party service issues (internet connectivity, browser problems)</li>
            <li>User error or misunderstanding of features</li>
            <li>Scheduled maintenance downtime (notified in advance)</li>
            <li>Account suspension due to policy violations</li>
            <li>Partial month in monthly subscription</li>
            <li>After 60 days of annual subscription</li>
          </ul>
        </section>

        <section>
          <h2>5. Refund Request Process</h2>
          
          <h3>Step 1: Submit Request</h3>
          <p>Email your refund request to: <strong>connect@go4garage.in</strong></p>
          <p>Include the following information:</p>
          <ul>
            <li>Account Kailash Code ({'<REDACTED_kailash_code>'} format)</li>
            <li>Transaction ID or invoice number</li>
            <li>Date of charge</li>
            <li>Amount charged</li>
            <li>Reason for refund request</li>
            <li>Supporting documentation (screenshots, error messages)</li>
          </ul>

          <h3>Step 2: Review Process</h3>
          <ul>
            <li><strong>Acknowledgment:</strong> Within 24 hours of request submission</li>
            <li><strong>Investigation:</strong> 3-5 business days for standard requests</li>
            <li><strong>Complex Cases:</strong> Up to 10 business days for thorough review</li>
            <li><strong>Status Updates:</strong> Email updates every 3 business days</li>
          </ul>

          <h3>Step 3: Decision Notification</h3>
          <ul>
            <li><strong>Approval:</strong> Email confirmation with refund amount and timeline</li>
            <li><strong>Denial:</strong> Detailed explanation with appeal process</li>
            <li><strong>Partial Approval:</strong> Pro-rated refund with reasoning</li>
          </ul>

          <h3>Step 4: Refund Processing</h3>
          <ul>
            <li><strong>Timeline:</strong> 7-10 business days from approval</li>
            <li><strong>Method:</strong> Refund to original payment method</li>
            <li><strong>Currency:</strong> Same currency as original charge (INR)</li>
            <li><strong>Receipt:</strong> Email receipt upon successful refund</li>
          </ul>
        </section>

        <section>
          <h2>6. Cancellation Process</h2>
          
          <h3>6.1 How to Cancel</h3>
          <p><strong>Method 1:</strong> Self-Service (Preferred)</p>
          <ul>
            <li>Log into Kailash dashboard</li>
            <li>Navigate to Account Settings → Subscription</li>
            <li>Click "Cancel Subscription"</li>
            <li>Confirm cancellation reason (optional survey)</li>
            <li>Receive email confirmation</li>
          </ul>

          <p><strong>Method 2:</strong> Email Request</p>
          <ul>
            <li>Send request to connect@go4garage.in</li>
            <li>Subject: "Subscription Cancellation - [Your Kailash Code]"</li>
            <li>Include account details for verification</li>
            <li>Response within 24 hours</li>
          </ul>

          <h3>6.2 Cancellation Effective Date</h3>
          <ul>
            <li><strong>Monthly:</strong> End of current billing cycle</li>
            <li><strong>Annual:</strong> End of current term (no mid-term cancellation)</li>
            <li><strong>Trial:</strong> Immediate cancellation, no charges</li>
            <li><strong>Access:</strong> Full platform access until effective date</li>
          </ul>

          <h3>6.3 Post-Cancellation</h3>
          <ul>
            <li><strong>Data Retention:</strong> 90 days after cancellation</li>
            <li><strong>Reactivation Window:</strong> 60 days without data loss</li>
            <li><strong>Export Data:</strong> Download all data before cancellation</li>
            <li><strong>Final Invoice:</strong> Sent within 5 business days</li>
          </ul>
        </section>

        <section>
          <h2>7. Disputed Charges</h2>
          <p>If you notice an unauthorized or incorrect charge:</p>
          
          <h3>7.1 Immediate Action</h3>
          <ul>
            <li>Contact us immediately: connect@go4garage.in</li>
            <li>We will place a temporary hold on the charge pending investigation</li>
            <li>Investigation completed within 5 business days</li>
            <li>Funds released or refunded based on findings</li>
          </ul>

          <h3>7.2 Chargeback Policy</h3>
          <ul>
            <li>We encourage contacting us before initiating bank chargeback</li>
            <li>Chargebacks may result in account suspension pending resolution</li>
            <li>We respond to all chargebacks with transaction evidence</li>
            <li>Successful chargebacks processed per bank timeline</li>
            <li>Account access restored upon resolution</li>
          </ul>
        </section>

        <section>
          <h2>8. Special Circumstances</h2>
          
          <h3>8.1 Natural Disasters / Force Majeure</h3>
          <p>In case of natural disasters, pandemics, or other force majeure events:</p>
          <ul>
            <li>Billing may be suspended during event impact</li>
            <li>Pro-rated refund for service unavailability</li>
            <li>Extended grace period for payment obligations</li>
            <li>Flexible cancellation terms</li>
          </ul>

          <h3>8.2 Business Closure</h3>
          <p>If your business ceases EV charging operations:</p>
          <ul>
            <li>Provide business closure documentation</li>
            <li>Annual plan: Pro-rated refund consideration</li>
            <li>Monthly plan: Immediate cancellation available</li>
            <li>Data export assistance provided</li>
          </ul>

          <h3>8.3 Service Discontinuation</h3>
          <p>If Go4Garage discontinues Kailash:</p>
          <ul>
            <li>90-day advance notice to all customers</li>
            <li>Full refund of unused subscription period</li>
            <li>Data migration assistance provided</li>
            <li>Alternative solution recommendations</li>
          </ul>
        </section>

        <section>
          <h2>9. GST and Refunds</h2>
          <p>Refunds related to GST charges:</p>
          <ul>
            <li>Refund amount includes GST component</li>
            <li>Credit note issued for accounting purposes</li>
            <li>GST refund processed per GSTN regulations</li>
            <li>Revised tax invoice provided</li>
            <li>Timeline: 15-20 business days for GST refunds</li>
          </ul>
        </section>

        <section>
          <h2>10. Appeals and Escalation</h2>
          <p>If your refund request is denied and you wish to appeal:</p>
          
          <h3>10.1 First-Level Appeal</h3>
          <ul>
            <li>Email legal@go4garage.in within 15 days of denial</li>
            <li>Provide additional evidence or context</li>
            <li>Review by senior support team</li>
            <li>Response within 7 business days</li>
          </ul>

          <h3>10.2 Executive Escalation</h3>
          <ul>
            <li>Request escalation to management</li>
            <li>Final review by authorized decision maker</li>
            <li>Response within 10 business days</li>
            <li>Decision is final and binding</li>
          </ul>
        </section>

        <section>
          <h2>11. Policy Updates</h2>
          <p>
            This refund policy may be updated periodically. Material changes will be communicated via:
          </p>
          <ul>
            <li>Email notification to account administrators</li>
            <li>In-platform notification banner</li>
            <li>Updated "Last Updated" date</li>
          </ul>
          <p>
            Changes apply to transactions after the update date. Previous transactions governed by 
            policy in effect at time of transaction.
          </p>
        </section>

        <section>
          <h2>12. Contact Information</h2>
          <div className="contact-box">
            <p><strong>Go4Garage - Kailash Platform</strong></p>
            <p>Refund Requests: connect@go4garage.in</p>
            <p>Billing Inquiries: connect@go4garage.in</p>
            <p>Appeals: legal@go4garage.in</p>
            <p><strong>Response Time:</strong> Within 24 hours</p>
          </div>
        </section>
      </div>

      <div className="legal-footer">
        <p>© 2025 Go4Garage. All rights reserved.</p>
        <p>This Refund Policy is governed by the laws of India and Consumer Protection Act 2019.</p>
        <div className="contact-info">
          <p>General Inquiries: connect@go4garage.in</p>
          <p>Legal Matters: legal@go4garage.in</p>
        </div>
      </div>
    </div>
  );
};

export default RefundPolicy;