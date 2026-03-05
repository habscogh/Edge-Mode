import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ChevronDown, 
  ChevronUp, 
  ArrowLeft, 
  HelpCircle,
  Flame,
  Target,
  Trophy,
  CreditCard,
  Users,
  User,
  Mail
} from 'lucide-react';

const FAQItem = ({ question, answer, isOpen, onClick }) => {
  return (
    <div className="border-b border-zinc-800 last:border-b-0">
      <button
        onClick={onClick}
        className="w-full py-4 flex items-center justify-between text-left hover:bg-zinc-900/50 transition-colors px-1"
        data-testid={`faq-item-${question.substring(0, 20).replace(/\s/g, '-').toLowerCase()}`}
      >
        <span className="text-white font-body pr-4">{question}</span>
        {isOpen ? (
          <ChevronUp className="w-5 h-5 text-zinc-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-zinc-400 flex-shrink-0" />
        )}
      </button>
      {isOpen && (
        <div className="pb-4 px-1 text-zinc-400 text-sm font-body leading-relaxed">
          {answer}
        </div>
      )}
    </div>
  );
};

const FAQSection = ({ title, icon: Icon, items, openIndex, setOpenIndex, sectionKey }) => {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-4">
        <Icon className="w-5 h-5 text-primary" />
        <h2 className="text-lg font-heading font-bold uppercase tracking-wide text-white">
          {title}
        </h2>
      </div>
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden">
        {items.map((item, index) => (
          <FAQItem
            key={index}
            question={item.q}
            answer={item.a}
            isOpen={openIndex === `${sectionKey}-${index}`}
            onClick={() => setOpenIndex(openIndex === `${sectionKey}-${index}` ? null : `${sectionKey}-${index}`)}
          />
        ))}
      </div>
    </div>
  );
};

export const FAQScreen = () => {
  const navigate = useNavigate();
  const [openIndex, setOpenIndex] = useState(null);

  const faqData = {
    gettingStarted: {
      title: "Getting Started",
      icon: Flame,
      items: [
        {
          q: "What is Edge Mode?",
          a: "Edge Mode is a self-improvement app designed for teens (ages 12-19) based on the concept of becoming '1% better every day.' You track daily effort across different areas of your life called 'pillars' - like fitness, studying, or skill development. The app helps you build consistency, track streaks, and visualize your progress over time."
        },
        {
          q: "What are pillars?",
          a: "Pillars are the different areas of your life you want to improve. During onboarding, you choose 3-5 pillars from options like Fitness/Training, Study/Academics, Skill Development, Reading/Learning, Sports Practice, Personal Projects, and Discipline Habits. You set weekly targets for each pillar."
        },
        {
          q: "How do I log a session?",
          a: "Tap the 'Log Session' button on your dashboard, select a pillar, choose how many minutes you spent (or use the default 30 min), optionally add a note, and tap 'Complete Session.' You can also use Quick Log on the dashboard for faster logging."
        },
        {
          q: "Can I change my pillars later?",
          a: "Yes! Go to Profile > Manage Pillars to add new pillars, remove existing ones, or adjust your weekly targets. You can have between 1-5 active pillars at any time. Removing a pillar won't delete your logged sessions."
        }
      ]
    },
    streaks: {
      title: "Streaks & Progress",
      icon: Target,
      items: [
        {
          q: "How do streaks work?",
          a: "Your streak counts consecutive days where you've logged at least one session. Log something every day to keep your streak going! Your current streak and longest streak are displayed on your dashboard and profile."
        },
        {
          q: "What happens if I miss a day?",
          a: "If you don't log any session for a day, your current streak resets to 0. However, your longest streak record is preserved. Don't worry - you can always start building a new streak!"
        },
        {
          q: "What is the Performance Index?",
          a: "Your Performance Index shows how well you're hitting your weekly targets across all pillars. It's calculated based on sessions completed vs. your target. Ratings range from 'Elite' (90%+) to 'Getting Started' (below 25%)."
        },
        {
          q: "What is Consistency?",
          a: "Consistency measures how many days per week you log at least one session. If you log something 5 out of 7 days, your consistency is ~71%. Higher consistency leads to better results!"
        }
      ]
    },
    badges: {
      title: "Badges & Achievements",
      icon: Trophy,
      items: [
        {
          q: "How do I earn badges?",
          a: "Badges are earned automatically when you hit certain milestones. Log your first session to get 'First Step,' maintain a 7-day streak for 'Week Warrior,' and so on. Check the Achievements page to see all available badges and your progress."
        },
        {
          q: "What badges are available?",
          a: "There are 8 badges: First Step (first session), Week Warrior (7-day streak), Fortnight Fighter (14-day streak), Monthly Master (30-day streak), Century Club (100 sessions), 50 Hour Club (50+ hours logged), Perfect Week (7 consecutive days), and Pillar Master (hit all targets in a week)."
        },
        {
          q: "Can I share my badges?",
          a: "Yes! Each earned badge has a share button. You can share to Twitter/X, Facebook, or copy to clipboard. When you hit milestone streaks (7, 14, 30 days), you'll also get a celebration popup with share options."
        }
      ]
    },
    subscription: {
      title: "Subscription & Pricing",
      icon: CreditCard,
      items: [
        {
          q: "How does the free trial work?",
          a: "New users get a 14-day free trial with full access to all features. You'll see a reminder banner when 3 days are left. After the trial, you'll need to subscribe to continue using the app."
        },
        {
          q: "What are the subscription options?",
          a: "We offer two plans: Monthly at $4.99/month, or Yearly at $49.99/year (save 17%). Both plans include unlimited session tracking, all badges, groups, leaderboards, and email reminders."
        },
        {
          q: "How do I cancel my subscription?",
          a: "You can manage your subscription through Stripe's customer portal. Go to Profile > Subscription > Manage Subscription. Cancellation takes effect at the end of your current billing period."
        },
        {
          q: "What happens to my data if I cancel?",
          a: "Your data is preserved even if you cancel. If you resubscribe later, all your history, streaks records, and badges will still be there."
        }
      ]
    },
    social: {
      title: "Groups & Social",
      icon: Users,
      items: [
        {
          q: "How do groups work?",
          a: "Groups let you compete with friends on a private leaderboard. Create a group to get a unique invite code, then share it with friends. Group members can see each other's weekly performance rankings."
        },
        {
          q: "How do I join a group?",
          a: "Get an invite code from a friend who created a group, go to the Groups page, and enter the code. You can be in multiple groups at once."
        },
        {
          q: "What is the global leaderboard?",
          a: "The global leaderboard shows the most improved users each week across all of Edge Mode. It's opt-in for privacy - enable it in your Profile settings if you want to compete globally."
        },
        {
          q: "How do I invite friends?",
          a: "Go to Profile > Invite Friends. You'll get a unique referral link and code. Share it directly or send an email invite. When friends sign up with your code, they'll be tracked as your referrals."
        }
      ]
    },
    account: {
      title: "Account & Privacy",
      icon: User,
      items: [
        {
          q: "How do I reset my password?",
          a: "On the login screen, tap 'Forgot password?' and enter your email. You'll receive a reset link. If you're logged in, go to Profile > Change Password."
        },
        {
          q: "Can I change my email?",
          a: "Yes, go to Profile > Change Email. You'll need to enter your current password to confirm the change."
        },
        {
          q: "How do I delete my account?",
          a: "Go to Profile > Delete Account. This action is permanent and will delete all your data including sessions, badges, and group memberships. You'll need to enter your password to confirm."
        },
        {
          q: "Is my data private?",
          a: "Yes, your session data is private by default. Only you can see your logged sessions and progress. If you join groups or opt into the global leaderboard, only your performance metrics (not session details) are visible to others."
        }
      ]
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] pb-24" data-testid="faq-screen">
      <div className="p-6 max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 transition-colors"
            data-testid="faq-back-btn"
          >
            <ArrowLeft className="w-5 h-5 text-zinc-400" />
          </button>
          <div>
            <h1 className="text-2xl font-heading font-bold uppercase tracking-tight text-white">
              Help & FAQ
            </h1>
            <p className="text-zinc-400 font-body text-sm">
              Find answers to common questions
            </p>
          </div>
        </div>

        {/* FAQ Sections */}
        {Object.entries(faqData).map(([key, section]) => (
          <FAQSection
            key={key}
            sectionKey={key}
            title={section.title}
            icon={section.icon}
            items={section.items}
            openIndex={openIndex}
            setOpenIndex={setOpenIndex}
          />
        ))}

        {/* Contact Section */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-6 mt-8">
          <div className="flex items-center gap-2 mb-3">
            <Mail className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-heading font-bold uppercase tracking-wide text-white">
              Still Need Help?
            </h2>
          </div>
          <p className="text-zinc-400 text-sm font-body mb-4">
            Can't find what you're looking for? Reach out to us and we'll get back to you as soon as possible.
          </p>
          <a 
            href="mailto:support@edgemodeapp.com"
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md font-heading uppercase text-sm tracking-wide hover:bg-primary/90 transition-colors"
            data-testid="contact-support-btn"
          >
            <Mail className="w-4 h-4" />
            Contact Support
          </a>
        </div>

        {/* Legal Links */}
        <div className="flex justify-center gap-6 mt-8 text-sm">
          <a 
            href="/privacy" 
            className="text-zinc-500 hover:text-primary transition-colors font-body"
          >
            Privacy Policy
          </a>
          <a 
            href="/terms" 
            className="text-zinc-500 hover:text-primary transition-colors font-body"
          >
            Terms of Service
          </a>
        </div>
      </div>
    </div>
  );
};
