import { useQuery } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';

export default function TaskQueue() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'officer';

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ['officer-queue'],
    queryFn: () => axios.get('/api/applications?persona=officer').then(r => r.data),
    refetchInterval: 5000,
  });

  if (isLoading) return (
    <div className="flex items-center justify-center py-20">
      <div className="animate-spin h-8 w-8 border-4 border-navy-700 border-t-transparent rounded-full" />
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-navy-700">Officer Task Queue</h1>
          <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-2" />
          <p className="text-gray-600">Tumusiime Robert · Mbarara District Agricultural Office</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-extrabold text-navy-700">{apps.length}</div>
          <div className="text-xs text-gray-500">Pending applications</div>
        </div>
      </div>

      {/* SLA legend */}
      <div className="flex gap-4 text-xs">
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-status-green inline-block" /> &gt;50% time remaining</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-status-orange inline-block" /> &lt;50% time remaining</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-status-red inline-block" /> &lt;10% / breached</span>
      </div>

      {apps.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">🎉</div>
          <h3 className="font-bold text-gray-700">No pending applications</h3>
          <p className="text-gray-500 text-sm mt-1">All applications have been processed.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map((app: any) => (
            <div
              key={app.id}
              onClick={() => navigate(`/desk/review/${app.id}?persona=${persona}`)}
              className="card hover:shadow-md hover:border-navy-700 cursor-pointer transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="font-extrabold text-navy-700">{app.referenceNumber}</span>
                    <StatusBadge status={app.status} />
                  </div>
                  <p className="font-semibold text-sm text-gray-800">{app.fullName}</p>
                  <p className="text-sm text-gray-600">{app.cooperativeName}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Submitted: {new Date(app.submittedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'long', year: 'numeric' })}
                    {' · '}{app.district}
                  </p>
                </div>
                <div className="shrink-0 w-40">
                  <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResponseHours} label="Response SLA" />
                  <div className="mt-2">
                    <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution SLA" />
                  </div>
                </div>
                <div className="text-navy-700 text-xl self-center">›</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
