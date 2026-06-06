import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface HeaderProps { persona?: string; }

const personaLabels: Record<string, { name: string; role: string; avatar: string }> = {
  citizen:    { name: 'Akello Sarah Namugenyi', role: 'Citizen — Mbarara District',     avatar: '👩🏾‍🌾' },
  officer:    { name: 'Tumusiime Robert',       role: 'District Agricultural Officer',   avatar: '👨🏾‍💼' },
  supervisor: { name: 'Nakamya Grace',          role: 'Senior District Officer',         avatar: '👩🏾‍💼' },
  leadership: { name: 'Executive Dashboard',    role: 'District Leadership',             avatar: '📊' },
};

interface NavItem { label: string; to: string; icon: string }

function getNavItems(persona: string): NavItem[] {
  const p = `persona=${persona}`;
  switch (persona) {
    case 'officer':
      return [
        { label: 'Task Queue', to: `/desk?${p}`,     icon: '📋' },
        { label: 'About',      to: `/about?${p}`,    icon: 'ℹ️' },
        { label: 'API Docs',   to: `/api-docs?${p}`, icon: '⚙️' },
      ];
    case 'supervisor':
      return [
        { label: 'Review Queue', to: `/supervisor?${p}`, icon: '✅' },
        { label: 'About',        to: `/about?${p}`,      icon: 'ℹ️' },
      ];
    case 'leadership':
      return [
        { label: 'Dashboard', to: `/dashboard?${p}`, icon: '📊' },
        { label: 'About',     to: `/about?${p}`,     icon: 'ℹ️' },
      ];
    default: // citizen
      return [
        { label: 'Home',             to: `/portal?${p}`,                      icon: '🏠' },
        { label: 'Services',         to: `/portal/services?${p}`,             icon: '📋' },
        { label: 'My Applications',  to: `/portal/my-applications?${p}`,      icon: '📁' },
        { label: 'Track',            to: `/track?${p}`,                       icon: '🔍' },
        { label: 'About',            to: `/about?${p}`,                       icon: 'ℹ️' },
      ];
  }
}

function NavLink({ to, label, onClick }: { to: string; label: string; onClick?: () => void }) {
  const location = useLocation();
  const path = to.split('?')[0];
  const isActive = location.pathname === path || location.pathname.startsWith(path + '/');
  return (
    <Link
      to={to}
      onClick={onClick}
      aria-current={isActive ? 'page' : undefined}
      className={`px-3 py-2.5 text-xs font-semibold rounded-md transition-colors whitespace-nowrap
        ${isActive
          ? 'text-gold-500 bg-navy-800 border-b-2 border-gold-500'
          : 'text-gray-300 hover:text-white hover:bg-navy-800'
        }`}
    >
      {label}
    </Link>
  );
}

/** Uganda national logo mark — black shield with yellow "N" and red bottom bar */
function NileLogo({ size = 36 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect width="36" height="36" rx="7" fill="#1A1A1A"/>
      <rect x="0" y="29" width="36" height="7" rx="0" fill="#C8102E"/>
      <rect x="0" y="29" width="36" height="3" fill="#C8102E"/>
      <text x="18" y="25" fontFamily="system-ui,sans-serif" fontWeight="800" fontSize="22"
            fill="#F5C000" textAnchor="middle" dominantBaseline="auto">N</text>
    </svg>
  );
}

export default function Header({ persona = 'citizen' }: HeaderProps) {
  const info = personaLabels[persona] || personaLabels.citizen;
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);
  const navItems = getNavItems(persona);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 4);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  useEffect(() => {
    if (!mobileOpen) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') setMobileOpen(false); };
    document.addEventListener('keydown', handler);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handler);
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  useEffect(() => {
    if (mobileOpen) drawerRef.current?.querySelector<HTMLElement>('a,button')?.focus();
  }, [mobileOpen]);

  return (
    <>
      <header
        className={`bg-navy-700 text-white sticky top-0 z-40 transition-shadow duration-200 pt-safe ${scrolled ? 'shadow-nav' : ''}`}
        role="banner"
      >
        {/* Main header row */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between gap-4">

            {/* Logo */}
            <Link
              to={`/?persona=${persona}`}
              className="flex items-center gap-3 group flex-shrink-0 focus-visible:outline-none"
              aria-label="NileGov Stack — Home"
            >
              <NileLogo size={36} />
              <div className="leading-tight">
                <div className="font-bold text-base sm:text-lg leading-none text-white">NileGov Stack</div>
                <div className="text-gray-300 text-2xs sm:text-xs opacity-70 leading-tight hidden xs:block">
                  Mbarara District Local Government
                </div>
              </div>
            </Link>

            {/* Uganda flag colours — decorative pill (desktop) */}
            <div className="hidden sm:flex items-center gap-0.5 rounded-full overflow-hidden border border-white/10 flex-shrink-0" aria-hidden="true">
              <span className="w-4 h-4 bg-navy-900 inline-block" title="Black" />
              <span className="w-4 h-4 bg-gold-500 inline-block" title="Yellow" />
              <span className="w-4 h-4 bg-ug-red inline-block" title="Red" />
              <span className="w-4 h-4 bg-navy-900 inline-block" />
              <span className="w-4 h-4 bg-gold-500 inline-block" />
              <span className="w-4 h-4 bg-ug-red inline-block" />
            </div>

            {/* User info — desktop */}
            <div className="hidden md:flex items-center gap-3 text-right flex-shrink-0">
              <div>
                <div className="text-xs text-gray-400 leading-none mb-0.5">Signed in as</div>
                <div className="text-sm font-semibold leading-none text-white">{info.name}</div>
                <div className="text-xs text-gray-400 mt-0.5">{info.role}</div>
              </div>
              <div className="w-9 h-9 rounded-full bg-navy-600 border border-white/10 flex items-center justify-center text-xl flex-shrink-0" aria-hidden="true">
                {info.avatar}
              </div>
            </div>

            {/* Hamburger — mobile */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-navy-600 transition-colors flex-shrink-0"
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
              aria-controls="mobile-nav"
              onClick={() => setMobileOpen(v => !v)}
            >
              <span className="block w-5 h-0.5 bg-white mb-1.5 transition-transform origin-center" style={{ transform: mobileOpen ? 'rotate(45deg) translate(0, 6px)' : '' }} />
              <span className="block w-5 h-0.5 bg-white mb-1.5 transition-opacity" style={{ opacity: mobileOpen ? 0 : 1 }} />
              <span className="block w-5 h-0.5 bg-white transition-transform origin-center" style={{ transform: mobileOpen ? 'rotate(-45deg) translate(0, -6px)' : '' }} />
            </button>
          </div>
        </div>

        {/* Uganda flag tri-stripe (black | yellow | red) */}
        <div className="flex" style={{ height: '4px' }} aria-hidden="true">
          <div className="flex-1 bg-navy-900" />
          <div className="flex-1 bg-gold-500" />
          <div className="flex-1 bg-ug-red" />
        </div>

        {/* Desktop nav */}
        <nav className="bg-navy-800 hidden md:block" aria-label="Main navigation" role="navigation">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center gap-0.5 overflow-x-auto py-0.5">
            {navItems.map(item => (
              <NavLink key={item.to} to={item.to} label={item.label} />
            ))}
          </div>
        </nav>
      </header>

      {/* Mobile nav overlay */}
      {mobileOpen && (
        <div className="nav-overlay md:hidden" aria-hidden="true" onClick={() => setMobileOpen(false)} />
      )}

      {/* Mobile nav drawer */}
      <div
        id="mobile-nav"
        ref={drawerRef}
        className={`nav-drawer md:hidden ${mobileOpen ? 'open' : ''}`}
        role="dialog"
        aria-label="Navigation menu"
        aria-modal="true"
      >
        {/* Drawer header */}
        <div className="bg-navy-700 px-4 py-3">
          {/* Uganda flag stripe */}
          <div className="flex mb-3" style={{ height: '3px' }} aria-hidden="true">
            <div className="flex-1 bg-navy-900" />
            <div className="flex-1 bg-gold-500" />
            <div className="flex-1 bg-ug-red" />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <NileLogo size={28} />
              <span className="text-white font-bold text-sm">NileGov Stack</span>
            </div>
            <button
              onClick={() => setMobileOpen(false)}
              className="text-white p-1.5 hover:bg-navy-600 rounded-lg transition-colors"
              aria-label="Close navigation"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" aria-hidden="true">
                <path d="M18 6 6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        {/* User info */}
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-xl flex-shrink-0" aria-hidden="true">
            {info.avatar}
          </div>
          <div>
            <div className="text-sm font-bold text-navy-700">{info.name}</div>
            <div className="text-xs text-gray-500">{info.role}</div>
          </div>
        </div>

        {/* Nav links */}
        <nav className="px-2 py-3 space-y-0.5" aria-label="Mobile navigation">
          {navItems.map(item => (
            <Link
              key={item.to}
              to={item.to}
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium text-gray-700
                         hover:bg-gray-100 hover:text-navy-700 transition-colors"
            >
              <span className="text-base w-6 text-center" aria-hidden="true">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-gray-100">
          <div className="text-xs text-gray-400 text-center">Prototype — Not a live production system</div>
        </div>
      </div>
    </>
  );
}
