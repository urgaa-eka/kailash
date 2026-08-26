import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, Shield, FileText, Activity, Award, AlertTriangle } from 'lucide-react';

const Compliance = () => {
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
              <Award className="w-10 h-10 text-purple-600" />
              <h1 className="text-4xl font-bold text-gray-900">Compliance</h1>
            </div>
            <p className="text-gray-600">Last Updated: {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
            <p className="text-sm text-gray-500 mt-2">Our commitment to regulatory compliance and industry standards</p>
          </div>

          {/* Legal Content */}
          <div className="space-y-8 text-gray-700 leading-relaxed">
            {/* Section 1 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <h2 className="text-2xl font-bold text-purple-900">1. Regulatory Compliance Overview</h2>
              </div>
              <p className="mb-4">
                Go4Garage Kailash is committed to maintaining the highest standards of regulatory compliance across all aspects of EV charging infrastructure management. Our platform adheres to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>National Standards:</strong> Bureau of Indian Standards (BIS) for EV charging infrastructure</li>
                <li><strong>Electrical Safety:</strong> Central Electricity Authority (CEA) regulations</li>
                <li><strong>Data Protection:</strong> Information Technology Act, 2000 and Digital Personal Data Protection Act, 2023</li>
                <li><strong>Environmental:</strong> Ministry of Environment, Forest and Climate Change guidelines</li>
                <li><strong>Automotive:</strong> Ministry of Road Transport and Highways (MoRTH) requirements</li>
              </ul>
            </section>

            {/* Section 2 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">2. Industry Standards Adherence</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.1 EV Charging Standards</h3>
              <div className="bg-green-50 p-6 rounded-lg border border-green-200 mb-4">
                <p className="font-semibold mb-3">BIS Standards Compliance:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><strong>IS 17017 (Part 1):</strong> AC charging requirements</li>
                  <li><strong>IS 17017 (Part 2):</strong> DC charging specifications</li>
                  <li><strong>IS 17017 (Part 3):</strong> Communication protocols</li>
                  <li><strong>IEC 61851:</strong> Conductive charging system standards</li>
                  <li><strong>ISO 15118:</strong> Vehicle-to-grid communication</li>
                </ul>
              </div>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.2 Software and Data Standards</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>ISO/IEC 27001:</strong> Information security management principles</li>
                <li><strong>ISO/IEC 27017:</strong> Cloud security controls</li>
                <li><strong>ISO/IEC 27018:</strong> Privacy protection in cloud computing</li>
                <li><strong>OCPP 2.0.1:</strong> Open Charge Point Protocol compliance</li>
                <li><strong>API Security:</strong> OAuth 2.0 and OpenID Connect standards</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.3 Electrical Safety Standards</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>CEA Technical Standards:</strong> Connectivity and metering</li>
                <li><strong>IS 732:</strong> Electrical installations code</li>
                <li><strong>IS 3043:</strong> Earthing practices</li>
                <li><strong>IS 13032:</strong> Surge protection requirements</li>
              </ul>
            </section>

            {/* Section 3 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="w-6 h-6 text-g4g-blue" />
                <h2 className="text-2xl font-bold text-purple-900">3. Security Certifications and Practices</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.1 Platform Security</h3>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="font-semibold mb-2">CHECK Implemented</p>
                  <ul className="text-sm space-y-1">
                    <li>• TLS 1.3 encryption</li>
                    <li>• AES-256 data encryption</li>
                    <li>• Multi-factor authentication</li>
                    <li>• Role-based access control</li>
                    <li>• 24/7 SHIV monitoring</li>
                  </ul>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="font-semibold mb-2">Security Measures</p>
                  <ul className="text-sm space-y-1">
                    <li>• Intrusion detection system</li>
                    <li>• DDoS protection</li>
                    <li>• Regular penetration testing</li>
                    <li>• Vulnerability assessments</li>
                    <li>• Security audit logs</li>
                  </ul>
                </div>
              </div>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">3.2 Certifications (Target/In Progress)</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>ISO 27001:</strong> Information Security Management (Target: Q2 2026)</li>
                <li><strong>SOC 2 Type II:</strong> Service Organization Controls (Planned)</li>
                <li><strong>CERT-In Empanelment:</strong> Indian Computer Emergency Response Team</li>
                <li><strong>PCI DSS:</strong> Payment Card Industry Data Security Standard (if handling payments)</li>
              </ul>
            </section>

            {/* Section 4 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">4. Data Protection Compliance</h2>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">4.1 Indian Data Protection Laws</h3>
              <p className="mb-4">Full compliance with:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>IT Act 2000:</strong> Section 43A (reasonable security practices)</li>
                <li><strong>IT Rules 2011:</strong> Sensitive personal data protection</li>
                <li><strong>DPDP Act 2023:</strong> Digital Personal Data Protection provisions</li>
                <li><strong>Data Localization:</strong> Critical data stored within India</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">4.2 Data Handling Practices</h3>
              <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 mb-4">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-300">
                      <th className="text-left py-2 font-semibold">Data Type</th>
                      <th className="text-left py-2 font-semibold">Storage</th>
                      <th className="text-left py-2 font-semibold">Retention</th>
                      <th className="text-left py-2 font-semibold">Encryption</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-200">
                      <td className="py-2">Personal Data</td>
                      <td className="py-2">India (MongoDB)</td>
                      <td className="py-2">Account lifetime</td>
                      <td className="py-2">AES-256</td>
                    </tr>
                    <tr className="border-b border-gray-200">
                      <td className="py-2">Transaction Data</td>
                      <td className="py-2">India</td>
                      <td className="py-2">7 years</td>
                      <td className="py-2">AES-256</td>
                    </tr>
                    <tr className="border-b border-gray-200">
                      <td className="py-2">Usage Logs</td>
                      <td className="py-2">India</td>
                      <td className="py-2">12 months</td>
                      <td className="py-2">Yes</td>
                    </tr>
                    <tr>
                      <td className="py-2">Security Logs</td>
                      <td className="py-2">India</td>
                      <td className="py-2">24 months</td>
                      <td className="py-2">Yes</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            {/* Section 5 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">5. Electrical Safety Compliance</h2>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.1 Charging Infrastructure Requirements</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Voltage Standards:</strong> Compliance with 230V AC / 400V DC standards</li>
                <li><strong>Current Ratings:</strong> Proper amperage specifications per BIS standards</li>
                <li><strong>Protection Systems:</strong> GFCI, MCB, and surge protection devices</li>
                <li><strong>Grounding:</strong> Proper earthing as per IS 3043</li>
                <li><strong>Cable Standards:</strong> Fire-resistant cables per IS 694</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">5.2 Safety Monitoring</h3>
              <p className="mb-4">Kailash provides real-time monitoring of:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Voltage and current levels</li>
                <li>Temperature monitoring</li>
                <li>Earth leakage detection</li>
                <li>Overload protection status</li>
                <li>Emergency shutdown systems</li>
              </ul>
            </section>

            {/* Section 6 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">6. Environmental Compliance</h2>
              
              <p className="mb-4">Adherence to environmental regulations:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>E-Waste Management:</strong> Compliance with E-Waste Rules, 2016</li>
                <li><strong>Carbon Neutrality:</strong> Tracking and reporting of energy consumption</li>
                <li><strong>Green Energy:</strong> Support for renewable energy integration</li>
                <li><strong>Material Standards:</strong> RoHS compliant equipment recommendations</li>
                <li><strong>Sustainability Reporting:</strong> ESG metrics and reporting capabilities</li>
              </ul>
            </section>

            {/* Section 7 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">7. Accessibility Standards</h2>
              
              <p className="mb-4">Platform accessibility features:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>WCAG 2.1 Level AA:</strong> Web Content Accessibility Guidelines</li>
                <li><strong>Screen Reader Support:</strong> Compatible with assistive technologies</li>
                <li><strong>Keyboard Navigation:</strong> Full keyboard accessibility</li>
                <li><strong>Color Contrast:</strong> Minimum 4.5:1 contrast ratio</li>
                <li><strong>Responsive Design:</strong> Mobile and tablet accessibility</li>
              </ul>
            </section>

            {/* Section 8 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">8. Audit and Monitoring Procedures</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">8.1 Internal Audits</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Quarterly Reviews:</strong> Compliance status assessment</li>
                <li><strong>Security Audits:</strong> Monthly vulnerability scans</li>
                <li><strong>Code Reviews:</strong> Continuous security code analysis</li>
                <li><strong>Access Reviews:</strong> User permissions audit every quarter</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">8.2 External Audits</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Annual Security Audit:</strong> Third-party security assessment</li>
                <li><strong>Penetration Testing:</strong> Annual ethical hacking tests</li>
                <li><strong>Compliance Certification:</strong> Independent verification of standards</li>
                <li><strong>Financial Audit:</strong> Annual financial and operational audit</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">8.3 Continuous Monitoring</h3>
              <p className="mb-4">Our SHIV guardian system provides:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>24/7 security monitoring</li>
                <li>Real-time threat detection</li>
                <li>Automated compliance checks</li>
                <li>Performance monitoring</li>
                <li>Incident response tracking</li>
              </ul>
            </section>

            {/* Section 9 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-6 h-6 text-orange-600" />
                <h2 className="text-2xl font-bold text-purple-900">9. Incident Response Procedures</h2>
              </div>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">9.1 Security Incidents</h3>
              <div className="bg-orange-50 p-6 rounded-lg border border-orange-200 mb-4">
                <p className="font-semibold mb-3">Response Timeline:</p>
                <ol className="list-decimal list-inside space-y-2 ml-4">
                  <li><strong>Detection:</strong> Immediate (automated SHIV monitoring)</li>
                  <li><strong>Assessment:</strong> Within 15 minutes</li>
                  <li><strong>Containment:</strong> Within 1 hour</li>
                  <li><strong>Notification:</strong> Affected users within 24 hours</li>
                  <li><strong>Resolution:</strong> Based on severity (P0: 4 hours, P1: 24 hours)</li>
                  <li><strong>Post-Mortem:</strong> Within 72 hours</li>
                </ol>
              </div>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">9.2 Data Breach Protocol</h3>
              <p className="mb-4">In case of a data breach:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Immediate containment and investigation</li>
                <li>User notification within 72 hours</li>
                <li>CERT-In reporting as required</li>
                <li>Forensic analysis and remediation</li>
                <li>Regulatory compliance reporting</li>
              </ul>
            </section>

            {/* Section 10 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">10. Regular Compliance Updates</h2>
              
              <p className="mb-4">We maintain compliance through:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Regulatory Monitoring:</strong> Continuous tracking of new regulations</li>
                <li><strong>Standards Updates:</strong> Immediate implementation of new standards</li>
                <li><strong>Training Programs:</strong> Regular compliance training for staff</li>
                <li><strong>Documentation:</strong> Up-to-date compliance documentation</li>
                <li><strong>Stakeholder Communication:</strong> Regular updates to users</li>
              </ul>

              <div className="bg-green-50 p-6 rounded-lg border border-green-200 mt-4">
                <p className="font-semibold mb-2">Compliance Commitment:</p>
                <p className="text-sm">
                  Go4Garage is committed to maintaining the highest standards of compliance across all regulatory domains. We proactively monitor changes in regulations and industry standards to ensure Kailash remains fully compliant.
                </p>
              </div>
            </section>

            {/* Section 11 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">11. Contact for Compliance Matters</h2>
              <p className="mb-4">For compliance-related inquiries:</p>
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <p className="font-semibold mb-2">Compliance Officer</p>
                <p>Go4Garage (Kailash)</p>
                <p>Email: compliance@go4garage.com</p>
                <p>Support: support@go4garage.com</p>
                <p>Website: https://go4garage.in</p>
                <p className="mt-3 text-sm text-gray-600">For urgent compliance matters, please mark emails as "URGENT - COMPLIANCE"</p>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="bg-purple-50 p-6 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Compliance Excellence:</strong> We take our compliance obligations seriously and continuously work to exceed industry standards.
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

export default Compliance;