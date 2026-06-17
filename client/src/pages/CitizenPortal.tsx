import { Routes, Route, useSearchParams } from 'react-router-dom';
import Footer from '../components/Footer';
import Header from '../components/Header';
import CitizenLanding from './citizen/CitizenLanding';
import ServiceCatalogue from './citizen/ServiceCatalogue';
import ApplicationForm from './citizen/ApplicationForm';
import ApplicationStatus from './citizen/ApplicationStatus';
import MyApplications from './citizen/MyApplications';

export default function CitizenPortal() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <div>
      <Header persona={persona} />
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <Routes>
          <Route index element={<CitizenLanding />} />
          <Route path="services" element={<ServiceCatalogue />} />
          <Route path="apply" element={<ApplicationForm />} />
          <Route path="my-applications" element={<MyApplications />} />
          <Route path="application/:id" element={<ApplicationStatus />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
