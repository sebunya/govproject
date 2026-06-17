import { lazy, Suspense, useEffect } from 'react';
import { Routes, Route, useLocation, useSearchParams } from 'react-router-dom';
import PersonaSwitcher from './components/PersonaSwitcher';
import DemoGuide from './components/DemoGuide';
import { ToastProvider } from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import InstallPrompt from './components/InstallPrompt';
import OfflineBanner from './components/OfflineBanner';
import { SkeletonCard } from './components/Skeleton';

// Lazy-loaded routes for code splitting
const LoginPage          = lazy(() => import('./pages/LoginPage'));
const CitizenPortal      = lazy(() => import('./pages/CitizenPortal'));
const OfficerDesk        = lazy(() => import('./pages/OfficerDesk'));
const LeadershipDashboard = lazy(() => import('./pages/LeadershipDashboard'));
const NotFound           = lazy(() => import('./pages/NotFound'));
const PrivacyPolicy      = lazy(() => import('./pages/PrivacyPolicy'));
const AboutPage          = lazy(() => import('./pages/AboutPage'));
const ApiDocsPage        = lazy(() => import('./pages/ApiDocsPage'));
const TrackApplication   = lazy(() => import('./pages/TrackApplication'));

function PageSuspense({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-4 py-8 space-y-4" aria-busy="true" aria-label="Loading page…">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      }
    >
      {children}
    </Suspense>
  );
}

// Scroll to top on route change + announce for screen readers
function RouteAnnouncer() {
  const location = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
    // Update document title for screen readers (pages set their own but this resets)
    const el = document.getElementById('route-announcer');
    if (el) {
      el.textContent = '';
      requestAnimationFrame(() => { el.textContent = document.title; });
    }
  }, [location.pathname]);
  return (
    <div
      id="route-announcer"
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    />
  );
}

function AppInner() {
  const [params] = useSearchParams();
  const location = useLocation();
  const persona = params.get('persona') || 'citizen';
  const isLoginPage = location.pathname === '/';

  return (
    <>
      <RouteAnnouncer />
      <OfflineBanner />
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {!isLoginPage && <PersonaSwitcher currentPersona={persona} />}

        <main id="main-content" className="flex-1" tabIndex={-1}>
          <PageSuspense>
            <Routes>
              <Route path="/" element={<LoginPage />} />
              <Route path="/portal/*" element={<CitizenPortal />} />
              <Route path="/desk/*"   element={<OfficerDesk />} />
              <Route path="/supervisor/*" element={<OfficerDesk />} />
              <Route path="/dashboard/*" element={<LeadershipDashboard />} />
              <Route path="/privacy"  element={<PrivacyPolicy />} />
              <Route path="/about"    element={<AboutPage />} />
              <Route path="/api-docs" element={<ApiDocsPage />} />
              <Route path="/track"    element={<TrackApplication />} />
              <Route path="*"         element={<NotFound />} />
            </Routes>
          </PageSuspense>
        </main>

        {!isLoginPage && <DemoGuide persona={persona} />}
        <InstallPrompt />
      </div>
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AppInner />
      </ToastProvider>
    </ErrorBoundary>
  );
}
