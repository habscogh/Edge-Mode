import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, Upload, Send, Mail, Check, X, AlertCircle, 
  Loader2, FileText, Trash2, Clock, UserCheck, RefreshCw
} from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const BulkInviteSection = () => {
  const [emails, setEmails] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [resending, setResending] = useState(null);
  const [results, setResults] = useState(null);
  const [invitations, setInvitations] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const fetchInvitationHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await axios.get(`${API}/coach/invitations`);
      setInvitations(response.data.invitations || []);
    } catch (error) {
      console.error('Failed to fetch invitations:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      // Parse CSV - handle comma, semicolon, newline separators
      const parsed = text
        .split(/[,;\n\r]+/)
        .map(e => e.trim())
        .filter(e => e && e.includes('@'));
      
      setEmails(parsed.join('\n'));
      toast.success(`Loaded ${parsed.length} emails from file`);
    };
    reader.readAsText(file);
  };

  const handleSendInvites = async () => {
    const emailList = emails
      .split(/[,;\n\r]+/)
      .map(e => e.trim())
      .filter(e => e);

    if (emailList.length === 0) {
      toast.error('Please enter at least one email');
      return;
    }

    if (emailList.length > 50) {
      toast.error('Maximum 50 emails per batch');
      return;
    }

    setSending(true);
    setResults(null);

    try {
      const response = await axios.post(`${API}/coach/bulk-invite`, {
        emails: emailList,
        custom_message: customMessage
      });

      setResults(response.data);
      
      if (response.data.sent > 0) {
        toast.success(`Sent ${response.data.sent} invitation${response.data.sent !== 1 ? 's' : ''}!`);
        setEmails('');
        setCustomMessage('');
        fetchInvitationHistory();
      } else {
        toast.error('No invitations sent. Check the results for details.');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send invitations');
    } finally {
      setSending(false);
    }
  };

  const emailCount = emails.split(/[,;\n\r]+/).filter(e => e.trim()).length;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5">
      <h3 className="text-lg font-heading font-bold uppercase text-white flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-primary" />
        Bulk Invite Players
      </h3>

      <div className="space-y-4">
        {/* Email Input */}
        <div>
          <label className="text-sm text-zinc-400 mb-2 block">
            Player Emails (one per line, or comma/semicolon separated)
          </label>
          <textarea
            value={emails}
            onChange={(e) => setEmails(e.target.value)}
            placeholder="player1@email.com&#10;player2@email.com&#10;player3@email.com"
            className="w-full h-32 bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white text-sm font-mono resize-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-zinc-500">
              {emailCount} email{emailCount !== 1 ? 's' : ''} (max 50 per batch)
            </span>
            <label className="flex items-center gap-2 text-xs text-primary hover:text-primary/80 cursor-pointer">
              <Upload className="w-4 h-4" />
              Upload CSV
              <input
                type="file"
                accept=".csv,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {/* Custom Message */}
        <div>
          <label className="text-sm text-zinc-400 mb-2 block">
            Personal Message (optional)
          </label>
          <textarea
            value={customMessage}
            onChange={(e) => setCustomMessage(e.target.value)}
            placeholder="Looking forward to having you on the team! Let's crush it together."
            className="w-full h-20 bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-white text-sm resize-none focus:border-primary focus:ring-1 focus:ring-primary"
            maxLength={500}
          />
          <div className="text-xs text-zinc-500 text-right mt-1">
            {customMessage.length}/500
          </div>
        </div>

        {/* Send Button */}
        <Button
          onClick={handleSendInvites}
          disabled={sending || emailCount === 0}
          className="w-full"
        >
          {sending ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Sending Invitations...
            </>
          ) : (
            <>
              <Send className="w-4 h-4 mr-2" />
              Send {emailCount} Invitation{emailCount !== 1 ? 's' : ''}
            </>
          )}
        </Button>

        {/* Results */}
        {results && (
          <div className={`p-4 rounded-lg border ${
            results.success 
              ? 'bg-green-500/10 border-green-500/30' 
              : 'bg-red-500/10 border-red-500/30'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              {results.success ? (
                <Check className="w-5 h-5 text-green-400" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-400" />
              )}
              <span className={results.success ? 'text-green-400' : 'text-red-400'}>
                {results.message}
              </span>
            </div>
            
            {results.sent > 0 && (
              <div className="text-sm text-zinc-400 mb-2">
                ✓ {results.sent} email{results.sent !== 1 ? 's' : ''} sent successfully
              </div>
            )}

            {results.invalid_emails?.length > 0 && (
              <div className="mt-2">
                <div className="text-xs text-zinc-500 mb-1">Invalid emails:</div>
                {results.invalid_emails.map((e, i) => (
                  <div key={i} className="text-xs text-red-400">
                    {e.email}: {e.reason}
                  </div>
                ))}
              </div>
            )}

            {results.failed_emails?.length > 0 && (
              <div className="mt-2">
                <div className="text-xs text-zinc-500 mb-1">Failed to send:</div>
                {results.failed_emails.map((e, i) => (
                  <div key={i} className="text-xs text-red-400">
                    {e.email}: {e.reason}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Invitation History Toggle */}
        <div className="border-t border-zinc-800 pt-4">
          <button
            onClick={() => {
              setShowHistory(!showHistory);
              if (!showHistory && invitations.length === 0) {
                fetchInvitationHistory();
              }
            }}
            className="flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
          >
            <Clock className="w-4 h-4" />
            {showHistory ? 'Hide' : 'Show'} Invitation History
          </button>

          {showHistory && (
            <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
              {loadingHistory ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="w-5 h-5 text-primary animate-spin" />
                </div>
              ) : invitations.length === 0 ? (
                <div className="text-sm text-zinc-500 text-center py-4">
                  No invitations sent yet
                </div>
              ) : (
                invitations.map((inv, i) => (
                  <div 
                    key={i} 
                    className="flex items-center justify-between bg-zinc-950 px-3 py-2 rounded text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <Mail className="w-3 h-3 text-zinc-500" />
                      <span className="text-zinc-300">{inv.email}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {inv.joined ? (
                        <span className="flex items-center gap-1 text-xs text-green-400">
                          <UserCheck className="w-3 h-3" />
                          Joined{inv.username ? ` as ${inv.username}` : ''}
                        </span>
                      ) : (
                        <span className="text-xs text-zinc-500">
                          {new Date(inv.sent_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
