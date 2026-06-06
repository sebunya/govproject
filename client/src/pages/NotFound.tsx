import { Link, useSearchParams } from 'react-router-dom';
import { useEffect } from 'react';

export default function NotFound() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  useEffect(() => {
    document.title = '404 — Page Not Found | NileGov Stack';
    return () => { document.title = 'NileGov Stack — Mbarara District Government Services'; };
  }, []);

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-16">
      <div className="text-center max-w-md mx-auto">
        <div
          className="w-24 h-24 bg-navy-50 rounded-2xl flex items-center justify-center mx-auto mb-6"
          aria-hidden="true"
        >
          <span className="text-5xl">🗺️</span>
        </div>
        <h1 className="text-2xl font-extrabold text-navy-700 mb-2">Page not found</h1>
        <p className="text-gray-500 text-sm leading-relaxed mb-8 max-w-xs mx-auto">
          The page you are looking for does not exist or has moved. Use the links below to get back on track.
        </p>
        <div className="flex flex-col xs:flex-row gap-3 justify-center">
          <Link to={`/portal?persona=${persona}`} className="btn-primary">
            Return to Portal
          </Link>
          <Link to={`/track?persona=${persona}`} className="btn-secondary">
            Track Application
          </Link>
        </div>
        <p className="mt-8 text-xs text-gray-400">
          Error 404 &middot; NileGov Stack &middot; Mbarara District Local Government
        </p>
      </div>
    </div>
  );
}
