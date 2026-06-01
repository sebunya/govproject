import { useNavigate, useSearchParams } from 'react-router-dom';

const services = [
  {
    id: 'cooperative-permit',
    title: 'Register Cooperative & Apply for Agribusiness Permit',
    description: 'Register your farming cooperative and apply for an agribusiness operating permit with Mbarara District Local Government.',
    category: 'Agriculture',
    sla: '14 working days',
    fee: 'No fee',
    active: true,
    icon: '🌿',
  },
  {
    id: 'land-permit',
    title: 'Land Development Permit',
    description: 'Apply for permission to develop or subdivide land within the district.',
    category: 'Land & Property',
    sla: '30 working days',
    fee: 'UGX 50,000',
    active: false,
    icon: '🏗',
  },
  {
    id: 'birth-certificate',
    title: 'Birth Certificate Application',
    description: 'Apply for or replace a birth certificate through the district registration office.',
    category: 'Civil Registration',
    sla: '7 working days',
    fee: 'No fee',
    active: false,
    icon: '📄',
  },
  {
    id: 'trading-licence',
    title: 'Trading Licence',
    description: 'Apply for a trading licence to operate a business within the district.',
    category: 'Business Licensing',
    sla: '10 working days',
    fee: 'UGX 120,000',
    active: false,
    icon: '🏪',
  },
  {
    id: 'health-permit',
    title: 'Food Handler Health Permit',
    description: 'Health clearance certificate for food handlers and food establishments.',
    category: 'Health & Safety',
    sla: '5 working days',
    fee: 'UGX 30,000',
    active: false,
    icon: '🏥',
  },
];

export default function ServiceCatalogue() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-navy-700">Service Catalogue</h1>
        <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-2" />
        <p className="text-gray-600">Select a service to begin your application.</p>
      </div>

      <div className="space-y-4">
        {services.map(svc => (
          <div
            key={svc.id}
            className={`card transition-all ${svc.active ? 'hover:shadow-md hover:border-navy-700 cursor-pointer' : 'opacity-60'}`}
            onClick={() => svc.active && navigate(`/portal/apply?persona=${persona}`)}
          >
            <div className="flex items-start gap-4">
              <div className={`text-3xl p-3 rounded-xl ${svc.active ? 'bg-navy-50' : 'bg-gray-100'}`}>
                {svc.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className={`font-bold text-base ${svc.active ? 'text-navy-700' : 'text-gray-500'}`}>
                      {svc.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">{svc.description}</p>
                  </div>
                  {svc.active ? (
                    <span className="badge-green shrink-0">Available</span>
                  ) : (
                    <span className="badge-orange shrink-0">Coming soon</span>
                  )}
                </div>
                <div className="flex flex-wrap gap-4 mt-3 text-xs text-gray-500">
                  <span>📂 {svc.category}</span>
                  <span>⏱ SLA: {svc.sla}</span>
                  <span>💳 {svc.fee}</span>
                </div>
              </div>
            </div>
            {svc.active && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <button className="btn-primary text-sm py-2">
                  Apply Now →
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
