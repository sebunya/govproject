import { Link, useLocation } from 'react-router-dom';

interface HeaderProps {
  title?: string;
  subtitle?: string;
  persona?: string;
}

const personaLabels: Record<string, { name: string; role: string; org: string }> = {
  citizen: { name: 'Akello Sarah Namugenyi', role: 'Citizen', org: 'Mbarara District' },
  officer: { name: 'Tumusiime Robert', role: 'District Agricultural Officer', org: 'Mbarara District Local Government' },
  supervisor: { name: 'Nakamya Grace', role: 'Senior District Officer', org: 'Mbarara District Local Government' },
  leadership: { name: 'Executive Dashboard', role: 'District Leadership', org: 'Mbarara District Local Government' },
};

function NavLink({ to, label }: { to: string; label: string }) {
  const location = useLocation();
  const path = to.split('?')[0];
  const isActive = location.pathname === path || location.pathname.startsWith(path + '/');
  return (
    <Link
      to={to}
      className={`px-3 py-2 text-xs font-semibold transition-colors ${
        isActive
          ? 'text-gold-500 border-b-2 border-gold-500'
          : 'text-navy-100 hover:text-white opacity-80 hover:opacity-100'
      }`}
    >
      {label}
    </Link>
  );
}

export default function Header({ persona = 'citizen' }: HeaderProps) {
  const info = personaLabels[persona] || personaLabels.citizen;

  return (
    <header className="bg-navy-700 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gold-500 rounded-lg flex items-center justify-center font-bold text-white text-xl">
                N
              </div>
              <div>
                <div className="font-bold text-lg leading-tight tracking-tight">NileGov Stack</div>
                <div className="text-navy-100 text-xs opacity-80 leading-tight">
                  A Uganda-built operational layer for Government service delivery
                </div>
              </div>
            </div>
            <div className="hidden md:block w-px h-10 bg-navy-100 opacity-30 mx-2" />
            <div className="hidden md:block">
              <div className="text-xs text-navy-100 opacity-70">MDA</div>
              <div className="text-sm font-semibold">Mbarara District Local Government</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold">{info.name}</div>
            <div className="text-xs text-navy-100 opacity-80">{info.role}</div>
          </div>
        </div>
      </div>
      <div className="bg-gold-500 h-0.5" />
      <nav className="bg-navy-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex gap-1 overflow-x-auto">
          <NavLink to={`/portal?persona=${persona}`} label="Home" />
          <NavLink to={`/portal/services?persona=${persona}`} label="Services" />
          {persona === 'citizen' && <NavLink to={`/portal/my-applications?persona=${persona}`} label="My Applications" />}
          <NavLink to={`/track?persona=${persona}`} label="Track" />
          <NavLink to={`/about?persona=${persona}`} label="About" />
          <NavLink to={`/api-docs?persona=${persona}`} label="API Docs" />
        </div>
      </nav>
    </header>
  );
}
