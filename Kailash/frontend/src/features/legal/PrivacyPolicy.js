import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, Database, Lock, Eye, Users, Globe } from 'lucide-react';

const PrivacyPolicy = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-4">
          <button 
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-purple-600 hover:text-purple-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-semibold">Back to Login</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-12">
          {/* Legal Header */}
          <div className="border-b-2 border-purple-600 pb-6 mb-8">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="w-10 h-10 text-purple-600" />
              <h1 className="text-4xl font-bold text-gray-900">Privacy Policy</h1>
            </div>
            <p className="text-gray-600">Last Updated: {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
            <p className="text-sm text-gray-500 mt-2">Your privacy is important to us. This policy explains how we collect, use, and protect your information.</p>
          </div>

          {/* Legal Content */}
          <div className="space-y-8 text-gray-700 leading-relaxed">
            {/* Section 1 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Database className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">1. Information We Collect</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">1.1 Personal Information</h3>
              <p className="mb-4">When you use Kailash, we collect:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Account Information:</strong> Kailash Code (username), email address, phone number</li>
                <li><strong>Authentication Data:</strong> Encrypted passwords, two-factor authentication details</li>
                <li><strong>Profile Data:</strong> Name, organization details, role/designation</li>
                <li><strong>Contact Information:</strong> Business address, communication preferences</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">1.2 Usage Information</h3>
              <p className="mb-4">We automatically collect information about how you interact with Kailash:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Activity Logs:</strong> Commands issued to GANESHA AI, tasks created, system interactions</li>
                <li><strong>System Metrics:</strong> Response times, feature usage, performance data</li>
                <li><strong>Session Data:</strong> Login/logout times, session duration, active features used</li>
                <li><strong>Device Information:</strong> Browser type, operating system, IP address</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">1.3 EV Charging Operations Data</h3>
              <p className="mb-4">Specific to our charging infrastructure management:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Station Data:</strong> Charging station locations, status, performance metrics</li>
                <li><strong>Transaction Data:</strong> Charging sessions, energy consumption, billing information</li>
                <li><strong>Fleet Data:</strong> Vehicle information, charging patterns, fleet operations</li>
                <li><strong>Diagnostic Data:</strong> System health, error logs, maintenance records</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">1.4 Technical Information</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Cookies and similar tracking technologies</li>
                <li>API usage logs and integration data</li>
                <li>Error reports and debugging information</li>
                <li>Security and monitoring logs</li>
              </ul>
            </section>

            {/* Section 2 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Eye className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">2. How We Use Your Information</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.1 Service Provision</h3>
              <p className="mb-4">We use your information to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Provide and maintain Kailash platform services</li>
                <li>Process your commands through GANESHA AI system</li>
                <li>Monitor and manage EV charging infrastructure</li>
                <li>Generate reports and analytics dashboards</li>
                <li>Enable SHIV security monitoring and PARVATI workload balancing</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.2 Platform Improvement</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Analyze usage patterns to enhance features</li>
                <li>Train and improve KAILASH AI algorithms</li>
                <li>Identify and fix technical issues</li>
                <li>Develop new features and capabilities</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.3 Communication</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Send service notifications and alerts</li>
                <li>Provide customer support</li>
                <li>Share important updates and security notices</li>
                <li>Respond to your inquiries and requests</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.4 Security and Compliance</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Detect and prevent fraud and security threats</li>
                <li>Ensure compliance with legal obligations</li>
                <li>Protect user accounts and platform integrity</li>
                <li>Conduct security audits and monitoring</li>
              </ul>
            </section>

            {/* Section 3 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Lock className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">3. Data Storage and Security</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.1 Storage Infrastructure</h3>
              <p className="mb-4">Your data is stored securely using:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Database:</strong> MongoDB with encryption at rest</li>
                <li><strong>Location:</strong> Servers located in India (primary) with secure backup facilities</li>
                <li><strong>Session Management:</strong> Secure, encrypted session cookies with 24-hour expiration</li>
                <li><strong>Backup:</strong> Regular automated backups with secure off-site storage</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.2 Security Measures</h3>
              <p className="mb-4">We implement multiple layers of security:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Encryption:</strong> TLS/SSL encryption for data in transit</li>
                <li><strong>Authentication:</strong> Multi-factor authentication (2FA) support</li>
                <li><strong>Access Control:</strong> Role-based access control (RBAC) system</li>
                <li><strong>Monitoring:</strong> 24/7 SHIV security monitoring for threats</li>
                <li><strong>Auditing:</strong> Comprehensive audit logs of all system activities</li>
                <li><strong>Compliance:</strong> Regular security assessments and penetration testing</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.3 Data Retention</h3>
              <p className="mb-4">We retain your data:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Account Data:</strong> As long as your account is active</li>
                <li><strong>Transaction Records:</strong> 7 years (as per Indian tax and accounting laws)</li>
                <li><strong>Usage Logs:</strong> 12 months for analysis and troubleshooting</li>
                <li><strong>Security Logs:</strong> 24 months for audit and compliance</li>
              </ul>
            </section>

            {/* Section 4 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">4. Information Sharing and Disclosure</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">4.1 Third-Party Services</h3>
              <p className="mb-4">We may share information with:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Cloud Infrastructure:</strong> Hosting and database services (with data processing agreements)</li>
                <li><strong>AI Services:</strong> Anthropic (Claude API) for GANESHA AI processing (only command text, no personal data)</li>
                <li><strong>Analytics:</strong> Anonymized usage data for platform improvement</li>
                <li><strong>Payment Processors:</strong> For billing and transaction processing (if applicable)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">4.2 Legal Requirements</h3>
              <p className="mb-4">We may disclose information when required by law:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>To comply with legal processes or government requests</li>
                <li>To enforce our Terms and Conditions</li>
                <li>To protect the rights, property, or safety of Go4Garage, users, or the public</li>
                <li>In connection with a merger, acquisition, or sale of assets (with notice)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">4.3 No Sale of Personal Data</h3>
              <p className="mb-4">
                <strong>We do not sell, rent, or trade your personal information to third parties for marketing purposes.</strong>
              </p>
            </section>

            {/* Section 5 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">5. Your Rights and Choices</h2>
              </div>
              
              <p className="mb-4">You have the following rights regarding your personal information:</p>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.1 Access and Portability</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Request a copy of your personal data</li>
                <li>Export your data in a machine-readable format</li>
                <li>View your activity logs and usage history</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.2 Correction and Update</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Update your profile information</li>
                <li>Correct inaccurate data</li>
                <li>Modify communication preferences</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.3 Deletion</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Request deletion of your account and data</li>
                <li>Note: Some data may be retained for legal/compliance purposes</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.4 Objection and Restriction</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Object to certain types of data processing</li>
                <li>Restrict processing under certain circumstances</li>
                <li>Opt-out of marketing communications</li>
              </ul>

              <p className="mt-4 bg-purple-50 p-4 rounded-lg border border-purple-200">
                <strong>To exercise your rights,</strong> contact us at privacy@go4garage.com with your request and account details.
              </p>
            </section>

            {/* Section 6 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">6. Cookies and Tracking Technologies</h2>
              
              <p className="mb-4">Kailash uses cookies and similar technologies:</p>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">6.1 Types of Cookies</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Essential Cookies:</strong> Required for platform functionality (session management, authentication)</li>
                <li><strong>Performance Cookies:</strong> Help us understand how you use the platform</li>
                <li><strong>Security Cookies:</strong> Detect fraud and protect against security threats</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">6.2 Managing Cookies</h3>
              <p className="mb-4">
                You can control cookies through your browser settings. However, disabling essential cookies may affect platform functionality.
              </p>
            </section>

            {/* Section 7 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">7. Children's Privacy</h2>
              <p className="mb-4">
                Kailash is not intended for individuals under the age of 18. We do not knowingly collect personal information from children. If we become aware that we have collected information from a child, we will take steps to delete it immediately.
              </p>
            </section>

            {/* Section 8 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Globe className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">8. International Data Transfers</h2>
              </div>
              <p className="mb-4">
                Your data is primarily stored and processed in India. If we transfer data internationally, we ensure appropriate safeguards are in place, including:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Standard contractual clauses</li>
                <li>Adequate data protection measures</li>
                <li>Compliance with applicable data protection laws</li>
              </ul>
            </section>

            {/* Section 9 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">9. Compliance with Indian Laws</h2>
              <p className="mb-4">We comply with:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Information Technology Act, 2000:</strong> Data protection and cybersecurity</li>
                <li><strong>IT Rules, 2011:</strong> Reasonable security practices</li>
                <li><strong>Digital Personal Data Protection Act, 2023:</strong> Personal data processing</li>
                <li><strong>Industry Standards:</strong> ISO 27001 principles for information security</li>
              </ul>
            </section>

            {/* Section 10 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">10. Changes to This Privacy Policy</h2>
              <p className="mb-4">
                We may update this Privacy Policy from time to time. We will notify you of material changes by:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Posting the updated policy on the platform</li>
                <li>Updating the "Last Updated" date</li>
                <li>Sending email notification for significant changes</li>
              </ul>
              <p className="mb-4">
                Your continued use after changes indicates acceptance of the updated policy.
              </p>
            </section>

            {/* Section 11 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">11. Contact Us</h2>
              <p className="mb-4">
                For privacy-related questions, concerns, or requests:
              </p>
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <p className="font-semibold mb-2">Data Protection Officer</p>
                <p>Go4Garage (Kailash)</p>
                <p>Email: privacy@go4garage.com</p>
                <p>Support: support@go4garage.com</p>
                <p>Website: https://go4garage.in</p>
                <p className="mt-3 text-sm text-gray-600">We will respond to your requests within 30 days.</p>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="bg-purple-50 p-6 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Your Privacy Matters:</strong> We are committed to protecting your privacy and maintaining the security of your information. This policy explains our practices in detail.
              </p>
              <p className="text-sm text-gray-600">
                © {new Date().getFullYear()} Go4Garage. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;