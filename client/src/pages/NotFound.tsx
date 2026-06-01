import { useNavigate, useSearchParams } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl font-extrabold text-navy-50 mb-2">404</div>
        <h1 className="text-2xl font-bold text-navy-700 mb-2">Page not found</h1>
        <p className="text-gray-500 mb-6">The page you're looking for doesn't exist.</p>
        <button
          onClick={() => navigate(`/portal?persona=${persona}`)}
          className="btn-primary"
        >
          Return to Portal
        </button>
      </div>
    </div>
  );
}
