import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const TermsAndConditions = () => {
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
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Terms & Conditions</h1>
            <p className="text-gray-600">Last Updated: {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
          </div>

          {/* Legal Content */}
          <div className="space-y-8 text-gray-700 leading-relaxed">
            {/* Section 1 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">1. Introduction</h2>
              <p className="mb-4">
                Welcome to Kailash, the Go4Garage Charging Command Center. These Terms and Conditions ("Terms") govern your access to and use of the Kailash platform, a comprehensive EV infrastructure management system operated by Go4Garage.
              </p>
              <p className="mb-4">
                By accessing or using Kailash, you agree to be bound by these Terms. If you do not agree to these Terms, please do not use our services.
              </p>
            </section>

            {/* Section 2 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">2. Service Description</h2>
              <p className="mb-4">
                Kailash is an AI-powered organizational operating system designed specifically for EV charging infrastructure management. Our platform provides:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Real-time charging station monitoring and control</li>
                <li>AI-powered system intelligence through KAILASH</li>
                <li>Enterprise fleet operations management</li>
                <li>Advanced diagnostics and reporting</li>
                <li>Integrated payment and billing systems</li>
                <li>OEMSG (Original Equipment Manufacturer Support Group) compliance features</li>
              </ul>
            </section>

            {/* Section 3 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">3. User Obligations and Responsibilities</h2>
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.1 Account Security</h3>
              <p className="mb-4">
                You are responsible for maintaining the confidentiality of your Kailash Code and Decode (password). You agree to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Keep your login credentials secure and confidential</li>
                <li>Not share your account with unauthorized persons</li>
                <li>Notify us immediately of any unauthorized access</li>
                <li>Use strong, unique passwords</li>
                <li>Enable two-factor authentication where available</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.2 Acceptable Use</h3>
              <p className="mb-4">
                You agree to use Kailash only for lawful purposes and in accordance with these Terms. You agree not to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Attempt to gain unauthorized access to any part of the platform</li>
                <li>Interfere with or disrupt the platform's operation</li>
                <li>Use the platform for any fraudulent or illegal activities</li>
                <li>Reverse engineer, decompile, or disassemble any part of the platform</li>
                <li>Upload or transmit viruses, malware, or harmful code</li>
              </ul>
            </section>

            {/* Section 4 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">4. Service Availability and Limitations</h2>
              <p className="mb-4">
                While we strive to provide uninterrupted service, Kailash is provided "as is" and "as available." We do not guarantee that:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>The service will be uninterrupted or error-free</li>
                <li>Defects will be corrected immediately</li>
                <li>The service will meet all your specific requirements</li>
                <li>Data transmission will be secure or error-free</li>
              </ul>
              <p className="mb-4">
                We reserve the right to modify, suspend, or discontinue any part of the service at any time with or without notice.
              </p>
            </section>

            {/* Section 5 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">5. Intellectual Property Rights</h2>
              <p className="mb-4">
                All content, features, and functionality of Kailash, including but not limited to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Software code and architecture</li>
                <li>KAILASH AI system and algorithms</li>
                <li>Design, graphics, and user interface</li>
                <li>Logos, trademarks, and branding</li>
                <li>Documentation and technical materials</li>
              </ul>
              <p className="mb-4">
                are owned by Go4Garage and are protected by Indian and international copyright, trademark, and other intellectual property laws. You are granted a limited, non-exclusive, non-transferable license to access and use Kailash solely for your authorized business purposes.
              </p>
            </section>

            {/* Section 6 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">6. Limitation of Liability</h2>
              <p className="mb-4">
                To the maximum extent permitted by Indian law, Go4Garage shall not be liable for:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Any indirect, incidental, special, consequential, or punitive damages</li>
                <li>Loss of profits, revenue, data, or business opportunities</li>
                <li>Service interruptions or data loss</li>
                <li>Third-party actions or failures of third-party services</li>
                <li>Unauthorized access to or alteration of your data</li>
              </ul>
              <p className="mb-4">
                Our total liability for any claims arising from your use of Kailash shall not exceed the amount paid by you (if any) for the service in the 12 months preceding the claim.
              </p>
            </section>

            {/* Section 7 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">7. Modification of Terms</h2>
              <p className="mb-4">
                We reserve the right to modify these Terms at any time. We will notify you of any material changes by:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Posting the updated Terms on the platform</li>
                <li>Updating the "Last Updated" date</li>
                <li>Sending notice to your registered email address (for significant changes)</li>
              </ul>
              <p className="mb-4">
                Your continued use of Kailash after such modifications constitutes acceptance of the updated Terms.
              </p>
            </section>

            {/* Section 8 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">8. Governing Law and Jurisdiction</h2>
              <p className="mb-4">
                These Terms shall be governed by and construed in accordance with the laws of India, without regard to its conflict of law provisions. Any disputes arising from these Terms or your use of Kailash shall be subject to the exclusive jurisdiction of the courts in Bangalore, Karnataka, India.
              </p>
            </section>

            {/* Section 9 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">9. Dispute Resolution</h2>
              <p className="mb-4">
                In the event of any dispute, controversy, or claim arising out of or relating to these Terms:
              </p>
              <ol className="list-decimal list-inside space-y-2 ml-4 mb-4">
                <li><strong>Negotiation:</strong> The parties shall first attempt to resolve the dispute through good faith negotiations.</li>
                <li><strong>Mediation:</strong> If negotiation fails within 30 days, the parties agree to attempt mediation through a mutually agreed mediator.</li>
                <li><strong>Arbitration:</strong> If mediation is unsuccessful, disputes shall be resolved through binding arbitration under the Arbitration and Conciliation Act, 1996.</li>
                <li><strong>Litigation:</strong> Only after exhausting the above remedies may either party resort to litigation in the designated courts.</li>
              </ol>
            </section>

            {/* Section 10 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">10. Contact Information</h2>
              <p className="mb-4">
                For questions, concerns, or notices regarding these Terms, please contact us at:
              </p>
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <p className="font-semibold mb-2">Go4Garage (Kailash)</p>
                <p>Email: legal@go4garage.com</p>
                <p>Support: support@go4garage.com</p>
                <p>Website: https://go4garage.in</p>
                <p className="mt-3 text-sm text-gray-600">Business Hours: Monday - Saturday, 9:00 AM - 6:00 PM IST</p>
              </div>
            </section>

            {/* Section 11 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">11. Severability</h2>
              <p className="mb-4">
                If any provision of these Terms is found to be invalid, illegal, or unenforceable, the remaining provisions shall continue in full force and effect.
              </p>
            </section>

            {/* Section 12 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">12. Entire Agreement</h2>
              <p className="mb-4">
                These Terms constitute the entire agreement between you and Go4Garage regarding your use of Kailash and supersede all prior agreements and understandings.
              </p>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="bg-purple-50 p-6 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Acknowledgment:</strong> By using Kailash, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions.
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

export default TermsAndConditions;