import React, { useState, useEffect, Component } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LandingPage } from './pages/LandingPage';
import { AuthScreen } from './pages/AuthScreen';
import { OnboardingScreen } from './pages/OnboardingScreen';
import { Dashboard } from './pages/Dashboard';
import { LogScreen } from './pages/LogScreen';
import { GroupsScreen } from './pages/GroupsScreen';
import { LeaderboardScreen } from './pages/LeaderboardScreen';
import { ProfileScreen } from './pages/ProfileScreen';
import { WeeklyReviewScreen } from './pages/WeeklyReviewScreen';
import { SubscriptionSuccessScreen } from './pages/SubscriptionSuccessScreen';
import { StreakRecoverySuccessScreen } from './pages/StreakRecoverySuccessScreen';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TermsOfService } from './pages/TermsOfService';
import { ForgotPassword } from './pages/ForgotPassword';
import ResetPasswordScreen from './pages/ResetPasswordScreen';
import { HistoryScreen } from './pages/HistoryScreen';
import { AdminDashboard } from './pages/AdminDashboard';
import { TrialExpiredScreen } from './pages/TrialExpiredScreen';
import { AchievementsScreen } from './pages/AchievementsScreen';
import { InviteFriendsScreen } from './pages/InviteFriendsScreen';
import { FAQScreen } from './pages/FAQScreen';
import { ManagePillarsScreen } from './pages/ManagePillarsScreen';
import { ChallengesScreen } from './pages/ChallengesScreen';
import { CoachDashboard } from './pages/CoachDashboard';
import { ParentDashboard } from './pages/ParentDashboard';
import { FamilyScreen } from './pages/FamilyScreen';
import { CoachSignup } from './pages/CoachSignup';
import { JoinTeam } from './pages/JoinTeam';
import { CoachHome } from './pages/CoachHome';
import { SchoolLeaderboardScreen } from './pages/SchoolLeaderboardScreen';
import { JournalScreen } from './pages/JournalScreen';
import GiftPaymentPage from './pages/GiftPaymentPage';
import GiftSuccessPage from './pages/GiftSuccessPage';
import DataDeletionPage from './pages/DataDeletionPage';
import ShopScreen from './pages/ShopScreen';
import PetSelectionScreen from './pages/PetSelectionScreen';
import PetAccessoriesScreen from './pages/PetAccessoriesScreen';
import PetCodexScreen from './pages/PetCodexScreen';
import CompanionsScreen from './pages/CompanionsScreen';
import SouvenirsScreen from './pages/SouvenirsScreen';
import ExpeditionHistoryScreen from './pages/ExpeditionHistoryScreen';
import EvolutionTreeScreen from './pages/EvolutionTreeScreen';
import { BottomNav } from './components/BottomNav';
import { Toaster } from './components/ui/sonner';
import axios from 'axios';
import './App.css';

// Error Boundary to prevent white screens
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error Boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
          <div className="text-center max-w-md">
            <h1 className="text-2xl font-bold text-white mb-4">Something went wrong</h1>
            <p className="text-zinc-400 mb-6">We encountered an unexpected error. Please try again.</p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.reload();
                }}
                className="bg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary/90"
              >
                Try Again
              </button>
              <button
                onClick={() => {
                  window.location.href = '/dashboard';
                }}
                className="bg-zinc-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-zinc-600"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Check if trial is expired
const isTrialExpired = (user) => {
  if (!user) return false;
  if (user.subscription_active && !user.is_trial) return false; // Paid subscriber
  if (!user.is_trial) return false; // Not a trial user
  if (!user.trial_ends_at) return false;
  return new Date(user.trial_ends_at) < new Date();
};

const ProtectedRoute = ({ children, requiresOnboarding = true, allowExpiredTrial = false }) => {
  const { user, loading } = useAuth();
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkOnboarding = async () => {
      if (user && requiresOnboarding) {
        try {
          const response = await axios.get(`${API}/users/pillars`);
          setHasCompletedOnboarding(response.data.length > 0);
        } catch (error) {
          setHasCompletedOnboarding(false);
        }
      }
      setChecking(false);
    };

    if (!loading) {
      checkOnboarding();
    }
  }, [user, loading, requiresOnboarding]);

  if (loading || (requiresOnboarding && checking)) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" />;
  }

  // Check for expired trial (redirect to trial-expired page)
  if (!allowExpiredTrial && isTrialExpired(user)) {
    return <Navigate to="/trial-expired" />;
  }

  if (requiresOnboarding && !hasCompletedOnboarding) {
    return <Navigate to="/onboarding" />;
  }

  return children;
};

const AppRoutes = () => {
  const { user, loading } = useAuth();
  const location = useLocation();

  const showBottomNav = [
    '/dashboard',
    '/log',
    '/groups',
    '/leaderboard',
    '/review',
    '/profile',
  ].includes(location.pathname);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={user ? <Navigate to="/dashboard" /> : <AuthScreen />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute requiresOnboarding={false}>
              <OnboardingScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/log"
          element={
            <ProtectedRoute>
              <LogScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/groups"
          element={
            <ProtectedRoute>
              <GroupsScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leaderboard"
          element={
            <ProtectedRoute>
              <LeaderboardScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfileScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/review"
          element={
            <ProtectedRoute>
              <WeeklyReviewScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/subscription-success"
          element={
            <ProtectedRoute>
              <SubscriptionSuccessScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/streak-recovery/success"
          element={
            <ProtectedRoute>
              <StreakRecoverySuccessScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <HistoryScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/achievements"
          element={
            <ProtectedRoute>
              <AchievementsScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/invite"
          element={
            <ProtectedRoute>
              <InviteFriendsScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trial-expired"
          element={
            <ProtectedRoute requiresOnboarding={false} allowExpiredTrial={true}>
              <TrialExpiredScreen />
            </ProtectedRoute>
          }
        />
        <Route path="/faq" element={<FAQScreen />} />
        <Route
          path="/pillars"
          element={
            <ProtectedRoute>
              <ManagePillarsScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/challenges"
          element={
            <ProtectedRoute>
              <ChallengesScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/shop"
          element={
            <ProtectedRoute>
              <ShopScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pets"
          element={
            <ProtectedRoute>
              <PetSelectionScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pets/accessories"
          element={
            <ProtectedRoute>
              <PetAccessoriesScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/coach/:groupId"
          element={
            <ProtectedRoute>
              <CoachDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/parent-dashboard"
          element={
            <ProtectedRoute>
              <ParentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/family"
          element={
            <ProtectedRoute>
              <FamilyScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/school-leaderboard"
          element={
            <ProtectedRoute>
              <SchoolLeaderboardScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/journal"
          element={
            <ProtectedRoute>
              <JournalScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/pet-codex"
          element={
            <ProtectedRoute>
              <PetCodexScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/companions"
          element={
            <ProtectedRoute>
              <CompanionsScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/souvenirs"
          element={
            <ProtectedRoute>
              <SouvenirsScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/expedition-history"
          element={
            <ProtectedRoute>
              <ExpeditionHistoryScreen />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evolution-tree"
          element={
            <ProtectedRoute>
              <EvolutionTreeScreen />
            </ProtectedRoute>
          }
        />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/delete-account" element={<DataDeletionPage />} />
        <Route path="/reset-password" element={<ResetPasswordScreen />} />
        
        {/* Gift Payment Routes (Public - No Auth) */}
        <Route path="/gift/:giftCode" element={<GiftPaymentPage />} />
        <Route path="/gift-success" element={<GiftSuccessPage />} />
        
        {/* Coach Routes */}
        <Route path="/coach-signup" element={<CoachSignup />} />
        <Route path="/join/:teamCode" element={<JoinTeam />} />
        <Route
          path="/coach-home"
          element={
            <ProtectedRoute requiresOnboarding={false}>
              <CoachHome />
            </ProtectedRoute>
          }
        />
      </Routes>
      {showBottomNav && <BottomNav />}
      <Toaster />
    </>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;