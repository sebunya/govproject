import { useQuery } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';

const DEMO_NIN = 'CM93019100ABC1J';

export default function MyApplications() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ['my-applications'],
    queryFn: () => axios.get(`/api/applications?persona=citizen&nin=${DEMO_NIN}`).then(r => r.data),
    refetchInterval: 5000,
  });

  if (isLoading) return (
    <div className="flex items-center justify-center py-20">
      <div className="animate-spin h-8 w-8 border-4 border-navy-700 border-t-transparent rounded-full" />
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-navy-700">My Applications</h1>
        <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-2" />
        <p className="text-gray-600">Showing applications for NIN: {DEMO_NIN}</p>
      </div>

      {apps.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">📋</div>
          <h3 className="font-bold text-gray-700 mb-2">No applications yet</h3>
          <p className="text-gray-500 text-sm mb-4">Start by applying for a government service.</p>
          <button
            onClick={() => navigate(`/portal/services?persona=${persona}`)}
            className="btn-primary"
          >
            Apply for a Service
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {apps.map((app: any) => {
            const isNew = Date.now() - new Date(app.submittedAt).getTime() < 3600000;
            return (
            <div
              key={app.id}
              onClick={() => navigate(`/portal/application/${app.id}?persona=${persona}`)}
              className={`card hover:shadow-md cursor-pointer transition-all ${isNew ? 'border-navy-700 ring-2 ring-navy-700 ring-opacity-20' : 'hover:border-navy-700'}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="font-extrabold text-navy-700">{app.referenceNumber}</span>
                    <StatusBadge status={app.status} />
                    {isNew && <span className="badge-blue animate-pulse-slow">NEW</span>}
                    {app.status === 'approved' && <span className="badge-green">✓ Permit Granted</span>}
                    {app.rating && (
                      <span className="text-xs text-gray-500">{'⭐'.repeat(app.rating)} {app.rating}/5</span>
                    )}
                  </div>
                  <p className="text-sm font-medium text-gray-700">{app.serviceType}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Submitted: {new Date(app.submittedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}
                    {app.resolvedAt && ` · Resolved: ${new Date(app.resolvedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}`}
                  </p>
                  {(app.cooperativeName || app.businessName) && (
                    <p className="text-xs text-gray-500 mt-0.5">
                      {app.businessName ? `Business: ${app.businessName}` : `Cooperative: ${app.cooperativeName}`}
                    </p>
                  )}
                </div>
                <div className="text-navy-700 text-xl">›</div>
              </div>
              {!app.resolvedAt && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution SLA" />
                </div>
              )}
            </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
