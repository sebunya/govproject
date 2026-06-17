import { Link, useSearchParams } from 'react-router-dom';
import { useEffect } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function NotFound() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  useEffect(() => {
    document.title = '404 — Page Not Found | NileGov Stack';
    return () => { document.title = 'NileGov Stack — Mbarara District Government Services'; };
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Header persona={persona} />
      <main
        id="main-content"
        className="flex-1 flex items-center justify-center px-4 py-16"
        tabIndex={-1}
      >
        <div className="text-center max-w-md mx-auto">
          {/* Uganda-flag coloured indicator */}
          <div className="flex justify-center gap-1 mb-6" aria-hidden="true">
            <div className="w-3 h-12 rounded-full bg-navy-700" />
            <div className="w-3 h-12 rounded-full bg-gold-500" />
            <div className="w-3 h-12 rounded-full bg-ug-red" />
          </div>

          <div
            className="w-24 h-24 bg-navy-50 rounded-2xl flex items-center justify-center mx-auto mb-6"
            aria-hidden="true"
          >
            <span className="text-5xl">🗺️</span>
          </div>

          <h1 className="text-3xl font-extrabold text-navy-700 mb-2">Page not found</h1>
          <div className="w-12 h-0.5 bg-gold-500 mx-auto mb-4" />
          <p className="text-gray-500 text-sm leading-relaxed mb-8 max-w-xs mx-auto">
            The page you are looking for does not exist or has been moved.
            Use the links below to get back on track.
          </p>

          <div className="flex flex-col xs:flex-row gap-3 justify-center">
            <Link to={`/?persona=${persona}`} className="btn-primary">
              Return Home
            </Link>
            <Link to={`/track?persona=${persona}`} className="btn-secondary">
              Track Application
            </Link>
          </div>

          <p className="mt-10 text-xs text-gray-400">
            Error 404 · NileGov Stack · Mbarara District Local Government
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
