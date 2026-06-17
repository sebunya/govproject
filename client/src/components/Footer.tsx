import { Link, useSearchParams } from 'react-router-dom';

export default function Footer() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';
  const year = new Date().getFullYear();

  return (
    <footer className="bg-navy-900 text-white mt-auto print:hidden pb-safe" role="contentinfo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">

          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div
                className="w-9 h-9 bg-ug-red rounded-lg flex items-center justify-center font-bold text-white text-lg"
                aria-hidden="true"
              >N</div>
              <div>
                <div className="font-bold text-base leading-none">NileGov Stack</div>
                <div className="text-2xs text-navy-100 opacity-60 mt-0.5">v1.0 Prototype</div>
              </div>
            </div>
            <p className="text-navy-100 text-xs leading-relaxed opacity-70 mb-3">
              A Uganda-built operational orchestration layer for government service delivery.
              Built for the Ministry of ICT and National Guidance Innovator Showcase, June 2026.
            </p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-status-green animate-pulse-slow inline-block" aria-hidden="true" />
              <span className="text-xs text-navy-100 opacity-60">Prototype — Not a live production system</span>
            </div>
          </div>

          {/* Citizen Services */}
          <div>
            <h3 className="font-bold text-xs mb-3 text-gold-500 uppercase tracking-widest">Citizen Services</h3>
            <ul className="space-y-2.5" role="list">
              {[
                { to: `/portal/services?persona=${persona}`, label: 'Service Catalogue' },
                { to: `/portal/apply?persona=${persona}`, label: 'Apply for a Service' },
                { to: `/portal/my-applications?persona=${persona}`, label: 'My Applications' },
                { to: `/track?persona=${persona}`, label: 'Reference Number Lookup' },
              ].map(item => (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className="text-xs text-navy-100 opacity-70 hover:opacity-100 hover:text-gold-500 transition-colors"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Platform */}
          <div>
            <h3 className="font-bold text-xs mb-3 text-gold-500 uppercase tracking-widest">Platform</h3>
            <ul className="space-y-2.5" role="list">
              {[
                { to: `/about?persona=${persona}`, label: 'About NileGov Stack' },
                { to: `/api-docs?persona=${persona}`, label: 'API Documentation' },
                { to: `/privacy?persona=${persona}`, label: 'Privacy Policy' },
              ].map(item => (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    className="text-xs text-navy-100 opacity-70 hover:opacity-100 hover:text-gold-500 transition-colors"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
              <li>
                <a
                  href="mailto:nilegov@demo.ug"
                  className="text-xs text-navy-100 opacity-70 hover:opacity-100 hover:text-gold-500 transition-colors"
                >
                  Contact Support
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-bold text-xs mb-3 text-gold-500 uppercase tracking-widest">Legal & Compliance</h3>
            <ul className="space-y-2 text-xs text-navy-100 opacity-60 leading-relaxed" role="list">
              <li>Data Protection &amp; Privacy Act 2019</li>
              <li>Access to Information Act 2005</li>
              <li>Electronic Transactions Act 2011</li>
              <li>Local Governments Act (Cap 243)</li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-navy-700 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-navy-100 opacity-50 text-center sm:text-left">
            &copy; {year} Mbarara District Local Government &middot; NileGov Stack Prototype
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs text-navy-100 opacity-40">
            <span>Built in Uganda 🇺🇬</span>
            <span aria-hidden="true">·</span>
            <span>Node.js · React · SQLite</span>
            <span aria-hidden="true">·</span>
            <span>NITA-U UGHub Pattern</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
