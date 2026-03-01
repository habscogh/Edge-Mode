import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export const TermsOfService = () => {
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
          Terms of Service
        </h1>

        <div className="space-y-6 text-zinc-300 font-body">
          <p className="text-sm text-zinc-500">Last updated: {new Date().toLocaleDateString()}</p>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Agreement to Terms</h2>
            <p>By accessing or using Edge Mode, you agree to be bound by these Terms of Service. If you disagree with any part of these terms, you may not use our service.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Age Requirement</h2>
            <p>Edge Mode is designed for users aged 12-19. By registering, you confirm that you are within this age range. Users under 18 should have parental or guardian consent before using paid features.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Free Trial</h2>
            <p>New users receive a 14-day free trial with full access to all features. No payment is required during the trial period. You may cancel at any time during the trial without being charged.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Subscription and Payment</h2>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Monthly subscription: $5.99/month</li>
              <li>Yearly subscription: $59.99/year</li>
              <li>Payments are processed securely through Stripe</li>
              <li>Subscriptions automatically renew unless cancelled</li>
              <li>You can cancel at any time from your profile settings</li>
              <li>No refunds for partial months or years</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">User Responsibilities</h2>
            <p>You agree to:</p>
            <ul className="list-disc list-inside space-y-2 ml-4">
              <li>Provide accurate information during registration</li>
              <li>Maintain the security of your account credentials</li>
              <li>Not share your account with others</li>
              <li>Use the service for personal, non-commercial purposes</li>
              <li>Not attempt to hack, disrupt, or misuse the service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Content and Data</h2>
            <p>You retain ownership of the data you create (session logs, notes, etc.). We may use aggregated, anonymized data for analytics and improving our service.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Leaderboards</h2>
            <p>By opting into global leaderboards, you consent to displaying your username, performance stats, and age group publicly. You can opt-out at any time.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Service Availability</h2>
            <p>We strive for 99.9% uptime but do not guarantee uninterrupted service. We may perform maintenance that temporarily affects availability.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Account Termination</h2>
            <p>We reserve the right to suspend or terminate accounts that violate these terms. You may delete your account at any time from your profile settings.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Limitation of Liability</h2>
            <p>Edge Mode is provided "as is" without warranties. We are not liable for any indirect, incidental, or consequential damages arising from your use of the service.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Changes to Terms</h2>
            <p>We may update these Terms of Service from time to time. Continued use of the service after changes constitutes acceptance of the new terms.</p>
          </section>

          <section>
            <h2 className="text-2xl font-heading font-bold text-white mb-3">Contact Us</h2>
            <p>If you have questions about these Terms, please contact us at:</p>
            <p className="text-primary mt-2">admin@edgemodeapp.com</p>
          </section>
        </div>
      </div>
    </div>
  );
};