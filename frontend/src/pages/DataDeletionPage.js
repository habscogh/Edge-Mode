import React from 'react';
import { Link } from 'react-router-dom';
import { Trash2, Shield, ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';

const DataDeletionPage = () => {
  return (
    <div className="min-h-screen bg-background text-white">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <Link to="/" className="inline-flex items-center text-zinc-400 hover:text-white mb-8">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Edge Mode
        </Link>

        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
              <Trash2 className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Data Deletion Request</h1>
              <p className="text-zinc-400">Edge Mode Account & Data Removal</p>
            </div>
          </div>

          <div className="space-y-6 text-zinc-300">
            <section>
              <h2 className="text-lg font-semibold text-white mb-2">How to Delete Your Account</h2>
              <p className="mb-4">
                You can delete your Edge Mode account and all associated data directly from the app:
              </p>
              <ol className="list-decimal list-inside space-y-2 ml-4">
                <li>Log in to your Edge Mode account</li>
                <li>Go to <strong>Profile</strong> (tap your profile icon)</li>
                <li>Scroll down and tap <strong>"Delete Account"</strong></li>
                <li>Enter your password to confirm</li>
                <li>Your account and all data will be permanently deleted</li>
              </ol>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-2">What Gets Deleted</h2>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Your account and login credentials</li>
                <li>All session logs and activity history</li>
                <li>Badges, achievements, and streaks</li>
                <li>Group memberships and team associations</li>
                <li>Any subscription data (subscriptions will be cancelled)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-2">Can't Access Your Account?</h2>
              <p className="mb-4">
                If you're unable to log in or need assistance deleting your account, contact us:
              </p>
              <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4">
                <p className="text-sm">
                  <strong>Email:</strong>{' '}
                  <a href="mailto:support@edgemodeapp.com" className="text-primary hover:underline">
                    support@edgemodeapp.com
                  </a>
                </p>
                <p className="text-sm text-zinc-500 mt-2">
                  Include "Account Deletion Request" in the subject line and the email address associated with your account.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-2">Processing Time</h2>
              <p>
                In-app deletions are processed immediately. Email requests are processed within 7 business days.
              </p>
            </section>

            <div className="flex items-center gap-2 pt-4 border-t border-zinc-800 text-sm text-zinc-500">
              <Shield className="w-4 h-4" />
              <span>Your privacy is important to us. See our{' '}
                <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link>
              </span>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Link to="/auth">
            <Button className="bg-primary hover:bg-primary/90 text-black font-bold">
              Log In to Delete Account
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DataDeletionPage;
