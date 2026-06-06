import { Routes, Route, Navigate } from 'react-router-dom';
import { useSearchParams } from 'react-router-dom';
import PersonaSwitcher from './components/PersonaSwitcher';
import DemoGuide from './components/DemoGuide';
import { ToastProvider } from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import CitizenPortal from './pages/CitizenPortal';
import OfficerDesk from './pages/OfficerDesk';
import LeadershipDashboard from './pages/LeadershipDashboard';
import NotFound from './pages/NotFound';
import PrivacyPolicy from './pages/PrivacyPolicy';
import AboutPage from './pages/AboutPage';
import ApiDocsPage from './pages/ApiDocsPage';
import TrackApplication from './pages/TrackApplication';

export default function App() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <ErrorBoundary>
    <ToastProvider>
      <div className="min-h-screen bg-gray-50">
        <PersonaSwitcher currentPersona={persona} />
        <DemoGuide persona={persona} />
        <Routes>
          <Route path="/" element={<Navigate to={`/portal?persona=${persona}`} replace />} />
          <Route path="/portal/*" element={<CitizenPortal />} />
          <Route path="/desk/*" element={<OfficerDesk />} />
          <Route path="/supervisor/*" element={<OfficerDesk />} />
          <Route path="/dashboard/*" element={<LeadershipDashboard />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/api-docs" element={<ApiDocsPage />} />
          <Route path="/track" element={<TrackApplication />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </ToastProvider>
    </ErrorBoundary>
  );
}
