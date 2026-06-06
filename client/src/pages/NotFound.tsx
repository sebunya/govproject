import { Link, useSearchParams } from 'react-router-dom';

export default function NotFound() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        <div className="text-7xl font-extrabold text-navy-50 mb-2">404</div>
        <h1 className="text-2xl font-bold text-navy-700 mb-2">Page not found</h1>
        <p className="text-gray-500 mb-6">The page you are looking for does not exist or has been moved.</p>
        <div className="flex flex-wrap gap-3 justify-center">
          <Link to={`/portal?persona=${persona}`} className="btn-primary">Return to Portal</Link>
          <Link to={`/track?persona=${persona}`} className="btn-secondary">Track Application</Link>
          <Link to={`/about?persona=${persona}`} className="btn-secondary">About NileGov Stack</Link>
        </div>
      </div>
    </div>
  );
}
