import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export const PrivacyPolicy = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#09090b] p-6 pb-24">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-zinc-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-body">Back</span>
        </button>

        <h1 className="text-4xl font-heading font-bold uppercase tracking-tight text-white mb-6">
          Privacy Policy
        </h1>

        <div className="space-y-6 text-zinc-300 font-body">
          <p className="text-sm text-zinc-500">Last updated: {new Date().toLocaleDateString()}</p>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Introduction</h2>
            <p>Edge Mode ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard your information when you use our app.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Information We Collect</h2>
            <h3 className="text-xl font-heading text-white mb-2">Personal Information</h3>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Email address</li>
              <li>Username</li>
              <li>Age (to verify you're 12-19)</li>
              <li>Session tracking data (activities, minutes, dates)</li>
              <li>Payment information (processed securely by Stripe)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">How We Use Your Information</h2>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>To provide and maintain our service</li>
              <li>To track your progress and performance</li>
              <li>To process your subscription payments</li>
              <li>To send you important updates about your account</li>
              <li>To display your stats on group and global leaderboards (if you opt-in)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Data Security</h2>
            <p>We implement appropriate security measures to protect your personal information. Your password is encrypted, and payment information is processed securely through Stripe (we never store your credit card details).</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Your Rights</h2>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Access your personal data</li>
              <li>Update or correct your information</li>
              <li>Delete your account at any time</li>
              <li>Opt-in or opt-out of leaderboards</li>
              <li>Export your data</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Third-Party Services</h2>
            <p>We use Stripe for payment processing. Please review Stripe's privacy policy at <a href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">stripe.com/privacy</a></p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Children's Privacy</h2>
            <p>Edge Mode is designed for teens aged 12-19. We do not knowingly collect information from children under 12. If you believe we have collected information from a child under 12, please contact us immediately.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Changes to This Policy</h2>
            <p>We may update this Privacy Policy from time to time. We will notify you of any changes by updating the "Last updated" date.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Contact Us</h2>
            <p>If you have questions about this Privacy Policy, please contact us at:</p>
            <p className="text-primary mt-2">admin@edgemodeapp.com</p>
          </section>
        </div>
      </div>
    </div>
  );
};