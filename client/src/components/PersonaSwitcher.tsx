import { Link } from 'react-router-dom';
import IntegrationStatusBar from './IntegrationStatusBar';

const PERSONA_INFO: Record<string, { name: string; role: string; icon: string }> = {
  citizen:    { name: 'Akello Sarah',     role: 'Community Member',          icon: '👩🏾‍🌾' },
  officer:    { name: 'Tumusiime Robert', role: 'Dist. Agricultural Officer', icon: '👨🏾‍💼' },
  supervisor: { name: 'Nakamya Grace',    role: 'Senior District Officer',    icon: '👩🏾‍💼' },
  leadership: { name: 'Executive View',   role: 'District Leadership',        icon: '📊' },
};

export default function PersonaSwitcher({ currentPersona }: { currentPersona: string }) {
  const info = PERSONA_INFO[currentPersona] || PERSONA_INFO.citizen;

  return (
    <div className="persona-switcher" role="navigation" aria-label="Demo persona">
      <div className="bg-navy-900 border-b border-navy-700 px-3 sm:px-4 py-1.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-gold-500 text-2xs font-bold tracking-widest uppercase shrink-0 hidden xs:block">
              Demo Mode
            </span>
            <span className="text-gray-500 hidden xs:block" aria-hidden="true">·</span>
            <span className="text-lg" aria-hidden="true">{info.icon}</span>
            <span className="text-xs font-semibold text-white truncate">
              {info.name}
            </span>
            <span className="text-2xs text-gray-400 hidden sm:block truncate">
              — {info.role}
            </span>
          </div>
          <Link
            to="/"
            className="flex items-center gap-1.5 text-xs font-semibold text-gold-500 hover:text-gold-400
                       border border-gold-500/30 hover:border-gold-500/60 px-2.5 py-1 rounded
                       transition-colors whitespace-nowrap shrink-0"
            aria-label="Switch demo role"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
            </svg>
            <span>Switch Role</span>
          </Link>
        </div>
      </div>
      <IntegrationStatusBar />
    </div>
  );
}
