import { Routes, Route, Navigate } from 'react-router-dom';
import { useSearchParams } from 'react-router-dom';
import PersonaSwitcher from './components/PersonaSwitcher';
import CitizenPortal from './pages/CitizenPortal';
import OfficerDesk from './pages/OfficerDesk';
import LeadershipDashboard from './pages/LeadershipDashboard';

export default function App() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <div className="min-h-screen bg-gray-50">
      <PersonaSwitcher currentPersona={persona} />
      <Routes>
        <Route path="/" element={<Navigate to={`/portal?persona=${persona}`} replace />} />
        <Route path="/portal/*" element={<CitizenPortal />} />
        <Route path="/desk/*" element={<OfficerDesk />} />
        <Route path="/supervisor/*" element={<OfficerDesk />} />
        <Route path="/dashboard/*" element={<LeadershipDashboard />} />
        <Route path="*" element={<Navigate to={`/portal?persona=${persona}`} replace />} />
      </Routes>
    </div>
  );
}
