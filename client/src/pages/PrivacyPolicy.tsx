import Header from '../components/Header';
import Footer from '../components/Footer';
import { useSearchParams } from 'react-router-dom';

export default function PrivacyPolicy() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  const sections = [
    {
      title: '1. Who We Are',
      content: `NileGov Stack is a digital government service delivery platform operated by Mbarara District Local Government, a statutory body established under the Local Governments Act (Cap 243) of Uganda. This prototype is developed for demonstration purposes under the Ministry of ICT and National Guidance Innovator Showcase (June 2026).

Contact: District Town Clerk, Mbarara District Local Government, Plot 1 Sharpe Road, Mbarara, Uganda. Email: clerk@mbarara.go.ug`
    },
    {
      title: '2. Legal Basis for Processing',
      content: `We process personal data in accordance with the Data Protection and Privacy Act 2019 (PDPA 2019) of Uganda. Our legal bases include:
• Consent (Section 10, PDPA 2019): You provide explicit, informed consent before any data is collected.
• Public task (Section 10(c)): Processing is necessary for the performance of a task carried out in the public interest under the Local Governments Act.
• Legal obligation: Processing is required to comply with statutory duties of local government under applicable law.`
    },
    {
      title: '3. Data We Collect',
      content: `We collect the following categories of personal data:
• Identity data: Full name, date of birth, gender, National Identification Number (NIN) — retrieved from the National Identification and Registration Authority (NIRA) via the UGHub Integration Spine.
• Tax data: Tax Identification Number (TIN), tax compliance status — retrieved from the Uganda Revenue Authority (URA) via the UGHub Integration Spine.
• Application data: Service applied for, business or cooperative name, district, uploaded documents.
• Consent record: Timestamp of your consent declaration, in accordance with Section 10 of PDPA 2019.
• Communication data: Phone number or email address for notifications.
• Feedback data: Optional service satisfaction rating and comments.

NOTE: In this prototype demonstration, all NIRA and URA data is SIMULATED. No real personal data is transmitted to or retrieved from live government systems.`
    },
    {
      title: '4. How We Use Your Data',
      content: `Your personal data is used exclusively for:
• Processing your application for the government service you have applied for.
• Verifying your identity and eligibility.
• Communicating with you about your application status via SMS, email, or portal notification.
• Recording an audit trail for accountability and legal compliance.
• Generating anonymised statistics for service delivery monitoring and evaluation.

We do not use your data for marketing, profiling, or any purpose incompatible with the service you applied for.`
    },
    {
      title: '5. Data Sharing',
      content: `Your data may be shared with:
• District Officers: only those directly responsible for processing your application.
• Supervisor/Senior Officers: when your application is escalated or requires countersignature.
• NIRA and URA: data retrieved from these agencies under formal Data Sharing Agreements (DSAs) consistent with Section 28 of PDPA 2019. In production, all inter-agency data exchanges would be routed through the NITA-U UGHub Integration Spine under signed DSAs.
• Payment processor (Pesapal): only the amount, reference, and method — no biometric or NIN data. Prototype uses Pesapal API 3.0 Sandbox only.

We do NOT share your data with third parties for commercial purposes.`
    },
    {
      title: '6. Data Retention',
      content: `In accordance with the Government Records and Archives Act and applicable local government retention schedules:
• Application records: Retained for 7 years from date of resolution.
• Audit logs: Retained for 10 years.
• Consent records: Retained for the full duration of the processing relationship.
• Rejected applications: Retained for 3 years.
• Payment records: Retained for 7 years for financial audit purposes.

In this prototype environment, all data is ephemeral and is deleted when the demonstration system is reseeded.`
    },
    {
      title: '7. Your Rights Under PDPA 2019',
      content: `You have the following rights under the Data Protection and Privacy Act 2019:
• Right of access (Section 20): You may request a copy of all personal data held about you.
• Right to rectification (Section 22): You may request correction of inaccurate data.
• Right to erasure (Section 23): You may request deletion of your data where processing is no longer necessary.
• Right to object (Section 24): You may object to processing on grounds of legitimate interest.
• Right to data portability: You may request your data in a machine-readable format.
• Right to lodge a complaint: With the Personal Data Protection Office (PDPO) of Uganda.

To exercise these rights, contact: dataprotection@mbarara.go.ug`
    },
    {
      title: '8. Security Measures',
      content: `We implement appropriate technical and organisational measures to protect your personal data, including:
• Access controls limiting data to authorised officers only.
• Audit logging of all access and modifications to application data.
• Encrypted storage of sensitive fields.
• Role-based persona access (citizen, officer, supervisor, leadership).
• No passwords or credentials stored — access controlled by district identity verification.

In production, all data in transit would be encrypted using TLS 1.3 and all API exchanges signed using government-issued certificates.`
    },
    {
      title: '9. Cookies and Tracking',
      content: `NileGov Stack does not use tracking cookies, advertising cookies, or third-party analytics. We use only essential session data stored locally in your browser to maintain your application form state. No data is sent to external analytics services.`
    },
    {
      title: '10. Prototype Disclaimer',
      content: `THIS IS A PROTOTYPE DEMONSTRATION SYSTEM ONLY.
• No live government data is accessed or transmitted.
• All NIRA identity verification is simulated.
• All URA tax clearance data is simulated.
• All Pesapal payment processing is simulated (Sandbox API 3.0).
• No SMS, email, or portal notifications are sent to real recipients.
• All application data entered is fictional and will be deleted after each demonstration.

This prototype is presented for evaluation by the Ministry of ICT and National Guidance. It does not constitute an official government service.`
    },
    {
      title: '11. Contact and Complaints',
      content: `Data Controller: Mbarara District Local Government
Data Protection Officer: District Town Clerk
Address: Plot 1 Sharpe Road, Mbarara, Uganda
Email: dataprotection@mbarara.go.ug

Personal Data Protection Office (PDPO) of Uganda
For complaints: pdpo.go.ug | info@pdpo.go.ug
Physical address: Kampala, Uganda`
    },
  ];

  return (
    <div>
      <Header persona={persona} />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-navy-700">Privacy Policy</h1>
          <div className="w-16 h-0.5 bg-gold-500 mt-2 mb-3" />
          <p className="text-gray-600">Mbarara District Local Government · NileGov Stack · Last updated: June 2026</p>
          <div className="bg-gold-50 border border-gold-500 rounded-xl p-4 mt-4">
            <p className="text-sm text-yellow-900">
              <strong>⚠ Prototype Notice:</strong> This privacy policy describes the data practices of the NileGov Stack prototype system, presented at the Ministry of ICT and National Guidance Innovator Showcase (June 2026). This is not a live government system. All integrations are simulated.
            </p>
          </div>
        </div>

        <div className="space-y-8">
          {sections.map(s => (
            <div key={s.title} className="card">
              <h2 className="text-lg font-bold text-navy-700 mb-3">{s.title}</h2>
              <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{s.content}</div>
            </div>
          ))}
        </div>

        <div className="mt-8 bg-navy-50 rounded-xl p-6 text-center">
          <p className="text-sm text-gray-600">
            This privacy policy is prepared in accordance with the <strong>Data Protection and Privacy Act 2019 (Uganda)</strong> and the <strong>Data Protection and Privacy Regulations 2021</strong>.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
