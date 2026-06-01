import { Routes, Route, useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import TaskQueue from './officer/TaskQueue';
import ReviewInterface from './officer/ReviewInterface';
import SupervisorQueue from './officer/SupervisorQueue';

export default function OfficerDesk() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'officer';
  const isSupervisor = persona === 'supervisor';

  return (
    <div>
      <Header persona={persona} />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <Routes>
          <Route index element={isSupervisor ? <SupervisorQueue /> : <TaskQueue />} />
          <Route path="review/:id" element={<ReviewInterface />} />
        </Routes>
      </main>
    </div>
  );
}
