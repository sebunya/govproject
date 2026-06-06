import { useNavigate, useLocation } from 'react-router-dom';
import IntegrationStatusBar from './IntegrationStatusBar';

const personas = [
  { id: 'citizen', label: 'Akello Sarah', role: 'Citizen', route: '/portal', icon: '👩🏾‍🌾' },
  { id: 'officer', label: 'Tumusiime Robert', role: 'District Agricultural Officer', route: '/desk', icon: '👨🏾‍💼' },
  { id: 'supervisor', label: 'Nakamya Grace', role: 'Senior District Officer', route: '/supervisor', icon: '👩🏾‍💼' },
  { id: 'leadership', label: 'Executive View', role: 'District Leadership', route: '/dashboard', icon: '📊' },
];

export default function PersonaSwitcher({ currentPersona }: { currentPersona: string }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleSwitch = (p: typeof personas[0]) => {
    navigate(`${p.route}?persona=${p.id}`);
  };

  return (
    <>
    <div className="bg-navy-900 border-b border-navy-700 px-4 py-2">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <span className="text-gold-500 text-xs font-semibold tracking-wide uppercase">
          Demo Persona Switcher
        </span>
        <div className="flex gap-1">
          {personas.map(p => (
            <button
              key={p.id}
              onClick={() => handleSwitch(p)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                currentPersona === p.id
                  ? 'bg-gold-500 text-white'
                  : 'text-gray-300 hover:bg-navy-700 hover:text-white'
              }`}
            >
              <span>{p.icon}</span>
              <span className="hidden sm:inline">{p.label}</span>
              <span className="text-xs opacity-75 hidden md:inline">— {p.role}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
    <IntegrationStatusBar />
    </>
  );
}
