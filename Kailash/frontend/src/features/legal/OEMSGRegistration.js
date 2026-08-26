import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, FileText, Users, Calendar, HelpCircle, Mail, Phone } from 'lucide-react';

const OEMSGRegistration = () => {
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
              <Users className="w-10 h-10 text-purple-600" />
              <h1 className="text-4xl font-bold text-gray-900">OEMSG Registration</h1>
            </div>
            <p className="text-gray-600">Original Equipment Manufacturer Support Group</p>
            <p className="text-sm text-gray-500 mt-2">Your gateway to authorized EV infrastructure support and compliance</p>
          </div>

          {/* Legal Content */}
          <div className="space-y-8 text-gray-700 leading-relaxed">
            {/* Section 1 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">1. What is OEMSG?</h2>
              <p className="mb-4">
                The <strong>Original Equipment Manufacturer Support Group (OEMSG)</strong> is a comprehensive certification and support program designed to ensure that EV charging infrastructure providers meet industry standards and receive authorized support for their operations.
              </p>
              
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200 mb-4">
                <h3 className="font-semibold text-lg mb-3">OEMSG Benefits:</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-semibold">Official Certification</span>
                    </p>
                    <p className="text-sm ml-7">Recognized industry certification for EV infrastructure providers</p>
                  </div>
                  <div>
                    <p className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-semibold">Technical Support</span>
                    </p>
                    <p className="text-sm ml-7">Priority access to OEM technical assistance and resources</p>
                  </div>
                  <div>
                    <p className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-semibold">Compliance Assistance</span>
                    </p>
                    <p className="text-sm ml-7">Guidance on regulatory compliance and standards</p>
                  </div>
                  <div>
                    <p className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-semibold">Network Access</span>
                    </p>
                    <p className="text-sm ml-7">Join a network of certified EV infrastructure professionals</p>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 2 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">2. Registration Requirements</h2>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.1 Eligibility Criteria</h3>
              <p className="mb-4">To be eligible for OEMSG registration, your organization must:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>Business Registration:</strong> Valid GST registration and business license</li>
                <li><strong>Infrastructure:</strong> Operational EV charging infrastructure or service facilities</li>
                <li><strong>Technical Capability:</strong> Qualified technical staff for EV equipment maintenance</li>
                <li><strong>Compliance:</strong> Adherence to BIS standards and electrical safety regulations</li>
                <li><strong>Insurance:</strong> Valid liability insurance coverage</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">2.2 Organization Types</h3>
              <p className="mb-4">OEMSG registration is available for:</p>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="font-semibold mb-2">Charging Station Operators</p>
                  <p className="text-sm">CPOs managing public/private charging infrastructure</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <p className="font-semibold mb-2">Service Centers</p>
                  <p className="text-sm">Authorized EV maintenance and repair facilities</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="font-semibold mb-2">Fleet Operators</p>
                  <p className="text-sm">Commercial EV fleet management companies</p>
                </div>
              </div>
            </section>

            {/* Section 3 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">3. Registration Process</h2>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 mb-6">
                <h3 className="font-semibold mb-4 text-lg">Step-by-Step Registration Guide:</h3>
                
                <div className="space-y-6">
                  {/* Step 1 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                      1
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-2">Submit Application</h4>
                      <p className="text-sm mb-2">Complete the online registration form with your organization details</p>
                      <ul className="text-sm list-disc list-inside ml-2 space-y-1">
                        <li>Company name and registration number</li>
                        <li>Contact information and address</li>
                        <li>Type of operations (CPO/Service Center/Fleet)</li>
                        <li>Infrastructure details (number of charging points, capacity)</li>
                      </ul>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                      2
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-2">Document Submission</h4>
                      <p className="text-sm mb-2">Upload required documents (see Section 4 for complete checklist)</p>
                      <ul className="text-sm list-disc list-inside ml-2 space-y-1">
                        <li>Business registration certificates</li>
                        <li>Technical certifications</li>
                        <li>Insurance documentation</li>
                        <li>Compliance certificates</li>
                      </ul>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                      3
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-2">Verification & Assessment</h4>
                      <p className="text-sm mb-2">Our team reviews your application and documents</p>
                      <ul className="text-sm list-disc list-inside ml-2 space-y-1">
                        <li>Document verification (3-5 business days)</li>
                        <li>Technical assessment of infrastructure</li>
                        <li>Site inspection (if required)</li>
                        <li>Background verification</li>
                      </ul>
                    </div>
                  </div>

                  {/* Step 4 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                      4
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-2">Payment Processing</h4>
                      <p className="text-sm mb-2">Complete registration fee payment</p>
                      <ul className="text-sm list-disc list-inside ml-2 space-y-1">
                        <li>Receive payment invoice via email</li>
                        <li>Pay online through secure payment gateway</li>
                        <li>Accepted methods: Net Banking, UPI, Credit/Debit Card</li>
                      </ul>
                    </div>
                  </div>

                  {/* Step 5 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                      5
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800 mb-2">Certification Issued</h4>
                      <p className="text-sm mb-2">Receive your OEMSG certification</p>
                      <ul className="text-sm list-disc list-inside ml-2 space-y-1">
                        <li>Digital certificate with unique ID</li>
                        <li>Access to OEMSG member portal</li>
                        <li>Welcome kit with guidelines and resources</li>
                        <li>Add OEMSG badge to your website/materials</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 4 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">4. Required Documentation Checklist</h2>
              
              <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-300 mb-4">
                <p className="font-semibold mb-3 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Complete Document Checklist:
                </p>
                
                <div className="space-y-4">
                  <div>
                    <p className="font-semibold text-gray-800 mb-2">A. Business Documents</p>
                    <ul className="text-sm space-y-1 ml-4">
                      <li>• Certificate of Incorporation/Partnership Deed</li>
                      <li>• GST Registration Certificate</li>
                      <li>• PAN Card of the organization</li>
                      <li>• Current business license</li>
                      <li>• Registered office address proof</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-800 mb-2">B. Technical Certifications</p>
                    <ul className="text-sm space-y-1 ml-4">
                      <li>• BIS certification for charging equipment</li>
                      <li>• Electrical safety compliance certificates</li>
                      <li>• CEA connectivity approval (if applicable)</li>
                      <li>• Technical staff qualifications</li>
                      <li>• Fire safety NOC from local authorities</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-800 mb-2">C. Insurance & Liability</p>
                    <ul className="text-sm space-y-1 ml-4">
                      <li>• Valid liability insurance policy</li>
                      <li>• Professional indemnity insurance (for service centers)</li>
                      <li>• Equipment insurance certificate</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-800 mb-2">D. Infrastructure Details</p>
                    <ul className="text-sm space-y-1 ml-4">
                      <li>• Site plan and layout drawings</li>
                      <li>• Electrical single line diagram</li>
                      <li>• List of charging equipment with specifications</li>
                      <li>• Network architecture diagram (for connected chargers)</li>
                      <li>• Maintenance schedule and procedures</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-800 mb-2">E. Additional Documents</p>
                    <ul className="text-sm space-y-1 ml-4">
                      <li>• Authorized signatory declaration</li>
                      <li>• Bank account details for verification</li>
                      <li>• Privacy policy and terms of service</li>
                      <li>• Customer complaint resolution process</li>
                    </ul>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mt-4 italic">
                  Note: All documents must be self-attested and uploaded in PDF format (max 5MB per file)
                </p>
              </div>
            </section>

            {/* Section 5 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">5. Compliance Benefits</h2>
              
              <p className="mb-4">OEMSG registration provides comprehensive compliance support:</p>
              
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-green-50 p-5 rounded-lg border border-green-200">
                  <h3 className="font-semibold mb-3 text-green-900">Regulatory Compliance</h3>
                  <ul className="text-sm space-y-2">
                    <li>• Regular compliance updates</li>
                    <li>• Regulatory change notifications</li>
                    <li>• Compliance audit support</li>
                    <li>• Documentation assistance</li>
                  </ul>
                </div>
                
                <div className="bg-blue-50 p-5 rounded-lg border border-blue-200">
                  <h3 className="font-semibold mb-3 text-blue-900">Technical Support</h3>
                  <ul className="text-sm space-y-2">
                    <li>• Priority helpdesk access</li>
                    <li>• Technical training programs</li>
                    <li>• Equipment troubleshooting</li>
                    <li>• Best practices guidance</li>
                  </ul>
                </div>
                
                <div className="bg-purple-50 p-5 rounded-lg border border-purple-200">
                  <h3 className="font-semibold mb-3 text-purple-900">Business Benefits</h3>
                  <ul className="text-sm space-y-2">
                    <li>• Preferred vendor status</li>
                    <li>• Marketing support materials</li>
                    <li>• Industry networking events</li>
                    <li>• Tender qualification advantage</li>
                  </ul>
                </div>
                
                <div className="bg-orange-50 p-5 rounded-lg border border-orange-200">
                  <h3 className="font-semibold mb-3 text-orange-900">Operational Excellence</h3>
                  <ul className="text-sm space-y-2">
                    <li>• Performance benchmarking</li>
                    <li>• Quality standards guidance</li>
                    <li>• Efficiency improvement tips</li>
                    <li>• Industry insights reports</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Section 6 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Calendar className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">6. Renewal Procedures</h2>
              </div>
              
              <p className="mb-4">OEMSG certification is valid for <strong>2 years</strong> from the date of issuance.</p>
              
              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">6.1 Renewal Process</h3>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li><strong>90 Days Before Expiry:</strong> Renewal notification sent via email</li>
                <li><strong>60 Days Before Expiry:</strong> Submit renewal application online</li>
                <li><strong>45 Days Before Expiry:</strong> Update any changed documents</li>
                <li><strong>30 Days Before Expiry:</strong> Complete renewal fee payment</li>
                <li><strong>On Renewal:</strong> New certificate issued for 2 years</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-4">6.2 Renewal Requirements</h3>
              <p className="mb-4">For renewal, you must provide:</p>
              <ul className="list-disc list-inside space-y-2 ml-4 mb-4">
                <li>Updated business registration documents</li>
                <li>Current insurance certificates</li>
                <li>Compliance audit report (self-certification)</li>
                <li>Infrastructure expansion details (if applicable)</li>
                <li>Continued adherence to OEMSG standards</li>
              </ul>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-sm">
                  <strong>Early Renewal Discount:</strong> Renew 90+ days before expiry and receive a 10% discount on renewal fees!
                </p>
              </div>
            </section>

            {/* Section 7 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">7. Timeline Expectations</h2>
              
              <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-gray-300">
                      <th className="text-left py-3 font-semibold">Stage</th>
                      <th className="text-left py-3 font-semibold">Duration</th>
                      <th className="text-left py-3 font-semibold">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-200">
                      <td className="py-3">Application Submission</td>
                      <td className="py-3">1 day</td>
                      <td className="py-3">Online form completion</td>
                    </tr>
                    <tr className="border-b border-gray-200">
                      <td className="py-3">Initial Review</td>
                      <td className="py-3">3-5 business days</td>
                      <td className="py-3">Application and document verification</td>
                    </tr>
                    <tr className="border-b border-gray-200">
                      <td className="py-3">Technical Assessment</td>
                      <td className="py-3">5-7 business days</td>
                      <td className="py-3">Infrastructure evaluation</td>
                    </tr>
                    <tr className="border-b border-gray-200">
                      <td className="py-3">Site Inspection (if needed)</td>
                      <td className="py-3">7-10 business days</td>
                      <td className="py-3">On-site verification</td>
                    </tr>
                    <tr className="border-b border-gray-200">
                      <td className="py-3">Approval & Payment</td>
                      <td className="py-3">2-3 business days</td>
                      <td className="py-3">Final approval and fee processing</td>
                    </tr>
                    <tr>
                      <td className="py-3 font-semibold">Certificate Issuance</td>
                      <td className="py-3 font-semibold">1-2 business days</td>
                      <td className="py-3 font-semibold">Digital certificate delivery</td>
                    </tr>
                  </tbody>
                </table>
                <p className="text-xs text-gray-600 mt-4 italic">
                  Total estimated time: 20-30 business days from application to certification (may vary based on site inspection requirements)
                </p>
              </div>
            </section>

            {/* Section 8 */}
            <section>
              <h2 className="text-2xl font-bold text-purple-900 mb-4">8. Cost Information</h2>
              
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200 mb-4">
                <h3 className="font-semibold mb-4">Registration Fees (Indicative):</h3>
                
                <table className="w-full text-sm mb-4">
                  <thead>
                    <tr className="border-b border-purple-300">
                      <th className="text-left py-2">Organization Type</th>
                      <th className="text-left py-2">Initial Registration</th>
                      <th className="text-left py-2">Annual Renewal</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-purple-200">
                      <td className="py-2">Small Operators (1-5 stations)</td>
                      <td className="py-2">₹15,000 + GST</td>
                      <td className="py-2">₹10,000 + GST</td>
                    </tr>
                    <tr className="border-b border-purple-200">
                      <td className="py-2">Medium Operators (6-20 stations)</td>
                      <td className="py-2">₹35,000 + GST</td>
                      <td className="py-2">₹25,000 + GST</td>
                    </tr>
                    <tr>
                      <td className="py-2">Large Operators (21+ stations)</td>
                      <td className="py-2">₹75,000 + GST</td>
                      <td className="py-2">₹50,000 + GST</td>
                    </tr>
                  </tbody>
                </table>
                
                <p className="text-xs text-gray-700 italic">
                  Note: Fees are subject to change. Final pricing will be provided during the application process.
                </p>
              </div>
            </section>

            {/* Section 9 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <Mail className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">9. Support Contact Information</h2>
              </div>
              
              <p className="mb-4">Need help with your OEMSG registration? Contact us:</p>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-5 rounded-lg border border-blue-200">
                  <p className="font-semibold mb-3 flex items-center gap-2">
                    <Mail className="w-5 h-5" />
                    Email Support
                  </p>
                  <p className="text-sm mb-1"><strong>General Inquiries:</strong></p>
                  <p className="text-sm mb-3">oemsg@go4garage.com</p>
                  <p className="text-sm mb-1"><strong>Technical Support:</strong></p>
                  <p className="text-sm mb-3">oemsg-tech@go4garage.com</p>
                  <p className="text-sm mb-1"><strong>Document Queries:</strong></p>
                  <p className="text-sm">oemsg-docs@go4garage.com</p>
                </div>
                
                <div className="bg-green-50 p-5 rounded-lg border border-green-200">
                  <p className="font-semibold mb-3 flex items-center gap-2">
                    <Phone className="w-5 h-5" />
                    Phone Support
                  </p>
                  <p className="text-sm mb-1"><strong>Helpline:</strong></p>
                  <p className="text-sm mb-3">1800-XXX-XXXX (Toll-Free)</p>
                  <p className="text-sm mb-1"><strong>WhatsApp Support:</strong></p>
                  <p className="text-sm mb-3">+91-XXXXX-XXXXX</p>
                  <p className="text-sm mb-1"><strong>Business Hours:</strong></p>
                  <p className="text-sm">Mon-Sat: 9:00 AM - 6:00 PM IST</p>
                </div>
              </div>
            </section>

            {/* Section 10 */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <HelpCircle className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-purple-900">10. Frequently Asked Questions (FAQs)</h2>
              </div>
              
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold mb-2">Q1: Is OEMSG registration mandatory for all charging station operators?</p>
                  <p className="text-sm text-gray-700">A: While not legally mandatory, OEMSG registration is highly recommended as it demonstrates compliance with industry standards and provides access to OEM support. Many tender processes and partnerships require OEMSG certification.</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold mb-2">Q2: Can I start the registration process while my charging infrastructure is being set up?</p>
                  <p className="text-sm text-gray-700">A: Yes, you can initiate the application process. However, final certification will only be issued after infrastructure commissioning and site inspection (if required).</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold mb-2">Q3: What happens if my registration expires?</p>
                  <p className="text-sm text-gray-700">A: Your OEMSG certification will be suspended. You'll need to complete the renewal process to restore your certification. A grace period of 30 days is provided with a late fee.</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold mb-2">Q4: Can I add more charging stations after initial registration?</p>
                  <p className="text-sm text-gray-700">A: Yes, you can update your registration with additional infrastructure. Simply submit an amendment request with details of new stations. Additional fees may apply for significant expansions.</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold mb-2">Q5: Is OEMSG registration valid nationwide?</p>
                  <p className="text-sm text-gray-700">A: Yes, OEMSG certification is valid across India. However, you must comply with state-specific regulations and obtain local permits as required.</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <p className="font-semibold mb-2">Q6: What if my application is rejected?</p>
                  <p className="text-sm text-gray-700">A: We provide detailed feedback on rejection reasons. You can address the issues and reapply. A reduced reapplication fee applies if you resubmit within 60 days.</p>
                </div>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="bg-purple-50 p-6 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Ready to Get Started?</strong> Begin your OEMSG registration journey today and join the network of certified EV infrastructure professionals.
              </p>
              <p className="text-sm text-gray-600 mb-3">
                For immediate assistance or to schedule a consultation, reach out to our OEMSG support team.
              </p>
              <button 
                onClick={() => window.location.href = 'mailto:oemsg@go4garage.com?subject=OEMSG Registration Inquiry'}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-semibold"
              >
                Contact OEMSG Team
              </button>
              <p className="text-xs text-gray-500 mt-4">
                © {new Date().getFullYear()} Go4Garage. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OEMSGRegistration;