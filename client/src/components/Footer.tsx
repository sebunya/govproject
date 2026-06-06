import { Link, useSearchParams } from 'react-router-dom';

export default function Footer() {
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <footer className="bg-navy-900 text-white mt-16 print:hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 bg-gold-500 rounded-lg flex items-center justify-center font-bold text-white">N</div>
              <span className="font-bold text-lg">NileGov Stack</span>
            </div>
            <p className="text-navy-100 text-xs leading-relaxed opacity-70">
              A Uganda-built operational orchestration layer for government service delivery. Built for the Ministry of ICT and National Guidance Innovator Showcase, June 2026.
            </p>
            <div className="mt-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-status-green animate-pulse inline-block" />
              <span className="text-xs text-navy-100 opacity-70">Prototype — Not a live system</span>
            </div>
          </div>

          <div>
            <h3 className="font-bold text-sm mb-3 text-gold-500 uppercase tracking-wide">Citizen Services</h3>
            <ul className="space-y-2 text-xs text-navy-100 opacity-80">
              <li><Link to={`/portal/services?persona=${persona}`} className="hover:text-gold-500 transition-colors">Service Catalogue</Link></li>
              <li><Link to={`/portal/apply?persona=${persona}`} className="hover:text-gold-500 transition-colors">Apply for a Service</Link></li>
              <li><Link to={`/portal/my-applications?persona=${persona}`} className="hover:text-gold-500 transition-colors">Track My Applications</Link></li>
              <li><Link to={`/track?persona=${persona}`} className="hover:text-gold-500 transition-colors">Reference Number Lookup</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-sm mb-3 text-gold-500 uppercase tracking-wide">Platform</h3>
            <ul className="space-y-2 text-xs text-navy-100 opacity-80">
              <li><Link to={`/about?persona=${persona}`} className="hover:text-gold-500 transition-colors">About NileGov Stack</Link></li>
              <li><Link to={`/api-docs?persona=${persona}`} className="hover:text-gold-500 transition-colors">API Documentation</Link></li>
              <li><Link to={`/privacy?persona=${persona}`} className="hover:text-gold-500 transition-colors">Privacy Policy</Link></li>
              <li><a href="mailto:nilegov@demo.ug" className="hover:text-gold-500 transition-colors">Contact / Support</a></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-sm mb-3 text-gold-500 uppercase tracking-wide">Legal &amp; Compliance</h3>
            <ul className="space-y-2 text-xs text-navy-100 opacity-70 leading-relaxed">
              <li>Data Protection and Privacy Act 2019</li>
              <li>Access to Information Act 2005</li>
              <li>Electronic Transactions Act 2011</li>
              <li>Local Governments Act (Cap 243)</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-navy-700 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-xs text-navy-100 opacity-50">
            &copy; {new Date().getFullYear()} Mbarara District Local Government &middot; NileGov Stack v1.0 (Prototype)
          </div>
          <div className="flex items-center gap-4 text-xs text-navy-100 opacity-50">
            <span>Built in Uganda &#x1F1FA;&#x1F1EC;</span>
            <span>&middot;</span>
            <span>Node.js &middot; React &middot; SQLite</span>
            <span>&middot;</span>
            <span>NITA-U UGHub Pattern</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
