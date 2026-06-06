import { useNavigate, useLocation } from 'react-router-dom';
import IntegrationStatusBar from './IntegrationStatusBar';

const personas = [
  { id: 'citizen',    label: 'Akello Sarah', role: 'Citizen',                     route: '/portal',    icon: '👩🏾‍🌾' },
  { id: 'officer',    label: 'Tumusiime Robert', role: 'District Agric. Officer', route: '/desk',      icon: '👨🏾‍💼' },
  { id: 'supervisor', label: 'Nakamya Grace', role: 'Senior District Officer',    route: '/supervisor', icon: '👩🏾‍💼' },
  { id: 'leadership', label: 'Executive View', role: 'District Leadership',        route: '/dashboard', icon: '📊' },
];

export default function PersonaSwitcher({ currentPersona }: { currentPersona: string }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleSwitch = (p: typeof personas[0]) => {
    // Preserve query string except persona
    const params = new URLSearchParams(location.search);
    params.set('persona', p.id);
    navigate(`${p.route}?${params.toString()}`);
  };

  return (
    <div className="persona-switcher" role="navigation" aria-label="Demo persona switcher">
      <div className="bg-navy-900 border-b border-navy-700 px-3 sm:px-4 py-1.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2">
          <span className="text-gold-500 text-2xs sm:text-xs font-bold tracking-widest uppercase shrink-0 hidden xs:block">
            Demo Persona
          </span>
          <div className="flex gap-1 flex-1 xs:flex-none justify-start xs:justify-end overflow-x-auto pb-0.5">
            {personas.map(p => (
              <button
                key={p.id}
                onClick={() => handleSwitch(p)}
                aria-pressed={currentPersona === p.id}
                aria-label={`Switch to ${p.label} — ${p.role}`}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all
                  whitespace-nowrap shrink-0
                  ${currentPersona === p.id
                    ? 'bg-gold-500 text-white shadow-sm'
                    : 'text-gray-300 hover:bg-navy-700 hover:text-white'
                  }`}
              >
                <span aria-hidden="true">{p.icon}</span>
                <span className="hidden sm:inline">{p.label}</span>
                <span className="sm:hidden">{p.id.slice(0,3)}</span>
                <span className="text-2xs opacity-60 hidden lg:inline">— {p.role}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      <IntegrationStatusBar />
    </div>
  );
}
