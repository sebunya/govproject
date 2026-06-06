import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';

interface HeaderProps { persona?: string; }

const personaLabels: Record<string, { name: string; role: string; avatar: string }> = {
  citizen:    { name: 'Akello Sarah Namugenyi', role: 'Citizen — Mbarara District', avatar: '👩🏾‍🌾' },
  officer:    { name: 'Tumusiime Robert', role: 'District Agricultural Officer', avatar: '👨🏾‍💼' },
  supervisor: { name: 'Nakamya Grace', role: 'Senior District Officer', avatar: '👩🏾‍💼' },
  leadership: { name: 'Executive Dashboard', role: 'District Leadership', avatar: '📊' },
};

interface NavItem { label: string; to: string; icon: string; citizenOnly?: boolean }

function getNavItems(persona: string): NavItem[] {
  return [
    { label: 'Home', to: `/portal?persona=${persona}`, icon: '🏠' },
    { label: 'Services', to: `/portal/services?persona=${persona}`, icon: '📋' },
    ...(persona === 'citizen'
      ? [{ label: 'My Applications', to: `/portal/my-applications?persona=${persona}`, icon: '📁', citizenOnly: true }]
      : []),
    { label: 'Track', to: `/track?persona=${persona}`, icon: '🔍' },
    { label: 'About', to: `/about?persona=${persona}`, icon: 'ℹ️' },
    { label: 'API Docs', to: `/api-docs?persona=${persona}`, icon: '⚙️' },
  ];
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
          ? 'text-gold-500 bg-navy-800'
          : 'text-navy-100 hover:text-white hover:bg-navy-800'
        }`}
    >
      {label}
    </Link>
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

  // Close on Escape
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

  // Trap focus in drawer
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
            {/* Logo + title */}
            <Link
              to={`/portal?persona=${persona}`}
              className="flex items-center gap-3 group flex-shrink-0"
              aria-label="NileGov Stack — Home"
            >
              <div
                className="w-9 h-9 bg-gold-500 rounded-lg flex items-center justify-center
                           font-bold text-white text-xl flex-shrink-0
                           group-hover:bg-gold-400 transition-colors"
                aria-hidden="true"
              >
                N
              </div>
              <div className="leading-tight">
                <div className="font-bold text-base sm:text-lg leading-none">NileGov Stack</div>
                <div className="text-navy-100 text-2xs sm:text-xs opacity-70 leading-tight hidden xs:block">
                  Mbarara District Local Government
                </div>
              </div>
            </Link>

            {/* User info — desktop */}
            <div className="hidden md:flex items-center gap-3 text-right">
              <div>
                <div className="text-xs text-navy-100 opacity-70 leading-none mb-0.5">Signed in as</div>
                <div className="text-sm font-semibold leading-none">{info.name}</div>
                <div className="text-xs text-navy-100 opacity-60 mt-0.5">{info.role}</div>
              </div>
              <div
                className="w-9 h-9 rounded-full bg-navy-600 flex items-center justify-center text-xl flex-shrink-0"
                aria-hidden="true"
              >
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
              <span className="block w-5 h-0.5 bg-white mb-1 transition-transform" style={{ transform: mobileOpen ? 'rotate(45deg) translate(2px, 6px)' : '' }} />
              <span className="block w-5 h-0.5 bg-white mb-1 transition-opacity" style={{ opacity: mobileOpen ? 0 : 1 }} />
              <span className="block w-5 h-0.5 bg-white transition-transform" style={{ transform: mobileOpen ? 'rotate(-45deg) translate(2px, -6px)' : '' }} />
            </button>
          </div>
        </div>

        {/* Gold accent bar */}
        <div className="h-0.5 bg-gold-500" aria-hidden="true" />

        {/* Desktop nav */}
        <nav
          className="bg-navy-800 hidden md:block"
          aria-label="Main navigation"
          role="navigation"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center gap-0.5 overflow-x-auto py-0.5">
            {navItems.map(item => (
              <NavLink key={item.to} to={item.to} label={item.label} />
            ))}
          </div>
        </nav>
      </header>

      {/* Mobile nav overlay + drawer */}
      {mobileOpen && (
        <div
          className="nav-overlay md:hidden"
          aria-hidden="true"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <div
        id="mobile-nav"
        ref={drawerRef}
        className={`nav-drawer md:hidden ${mobileOpen ? 'open' : ''}`}
        role="dialog"
        aria-label="Navigation menu"
        aria-modal="true"
      >
        <div className="bg-navy-700 px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gold-500 rounded-lg flex items-center justify-center font-bold text-white" aria-hidden="true">N</div>
            <span className="text-white font-bold">NileGov Stack</span>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="text-white p-1.5 hover:bg-navy-600 rounded-lg transition-colors"
            aria-label="Close navigation"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>

        {/* User info in drawer */}
        <div className="bg-navy-50 border-b border-gray-200 px-4 py-3 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-navy-100 flex items-center justify-center text-xl" aria-hidden="true">
            {info.avatar}
          </div>
          <div>
            <div className="text-sm font-bold text-navy-700">{info.name}</div>
            <div className="text-xs text-gray-500">{info.role}</div>
          </div>
        </div>

        <nav className="px-2 py-3 space-y-0.5" aria-label="Mobile navigation">
          {navItems.map(item => (
            <Link
              key={item.to}
              to={item.to}
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium text-gray-700
                         hover:bg-navy-50 hover:text-navy-700 transition-colors"
            >
              <span className="text-base w-6 text-center" aria-hidden="true">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-gray-100">
          <div className="text-xs text-gray-400 text-center">
            Prototype — Not a live production system
          </div>
        </div>
      </div>
    </>
  );
}
