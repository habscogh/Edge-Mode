import React, { useState, useEffect } from 'react';
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
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TermsOfService } from './pages/TermsOfService';
import { ForgotPassword } from './pages/ForgotPassword';
import { HistoryScreen } from './pages/HistoryScreen';
import { AdminDashboard } from './pages/AdminDashboard';
import { TrialExpiredScreen } from './pages/TrialExpiredScreen';
import { AchievementsScreen } from './pages/AchievementsScreen';
import { InviteFriendsScreen } from './pages/InviteFriendsScreen';
import { FAQScreen } from './pages/FAQScreen';
import { BottomNav } from './components/BottomNav';
import { Toaster } from './components/ui/sonner';
import axios from 'axios';
import './App.css';

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
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/terms" element={<TermsOfService />} />
      </Routes>
      {showBottomNav && <BottomNav />}
      <Toaster />
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;