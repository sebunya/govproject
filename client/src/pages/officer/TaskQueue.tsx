import { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import StatusBadge from '../../components/StatusBadge';
import SlaTimer from '../../components/SlaTimer';
import { SkeletonTable } from '../../components/Skeleton';

export default function TaskQueue() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'officer';
  const prevCountRef = useRef<number | null>(null);
  const [newCount, setNewCount] = useState(0);
  const [search, setSearch] = useState('');

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ['officer-queue'],
    queryFn: () => axios.get('/api/applications?persona=officer').then(r => r.data),
    refetchInterval: 5000,
  });

  // Track newly arrived applications
  useEffect(() => {
    if (prevCountRef.current !== null && apps.length > prevCountRef.current) {
      setNewCount(apps.length - prevCountRef.current);
      setTimeout(() => setNewCount(0), 8000);
    }
    prevCountRef.current = apps.length;
  }, [apps.length]);

  const filtered = (apps as any[]).filter((a: any) =>
    !search ||
    a.fullName?.toLowerCase().includes(search.toLowerCase()) ||
    a.referenceNumber?.toLowerCase().includes(search.toLowerCase()) ||
    a.cooperativeName?.toLowerCase().includes(search.toLowerCase()) ||
    a.businessName?.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) return (
    <div className="space-y-6">
      <SkeletonTable rows={5} cols={6} />
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
          <div className={`text-3xl font-extrabold text-navy-700 ${newCount > 0 ? 'animate-pulse-slow' : ''}`}>
            {apps.length}
          </div>
          <div className="text-xs text-gray-500">Pending applications</div>
          {newCount > 0 && (
            <div className="mt-1 badge-blue animate-pulse-slow">{newCount} new!</div>
          )}
        </div>
      </div>

      {/* SLA legend */}
      <div className="flex flex-wrap gap-4 text-xs">
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-status-green inline-block" /> &gt;50% time remaining</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-status-orange inline-block" /> &lt;50% time remaining</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-status-red inline-block" /> &lt;10% / breached · sorted most urgent first</span>
      </div>

      <input
        className="form-input"
        placeholder="Search by name, reference number, or business…"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      {search && <p className="text-xs text-gray-500">{filtered.length} of {(apps as any[]).length} shown</p>}

      {filtered.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">{search ? '🔍' : '🎉'}</div>
          <h3 className="font-bold text-gray-700">{search ? 'No matching applications' : 'No pending applications'}</h3>
          <p className="text-gray-500 text-sm mt-1">{search ? 'Try a different search term.' : 'All applications have been processed.'}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((app: any) => {
            const isNew = Date.now() - new Date(app.submittedAt).getTime() < 3600000;
            const isUrgent = (() => {
              const deadline = new Date(app.submittedAt).getTime() + app.slaResponseHours * 3600000;
              const pct = Math.max(0, (deadline - Date.now()) / (app.slaResponseHours * 3600000)) * 100;
              return pct < 10;
            })();

            return (
              <div
                key={app.id}
                onClick={() => navigate(`/desk/review/${app.id}?persona=${persona}`)}
                className={`card cursor-pointer transition-all hover:shadow-md ${
                  isUrgent ? 'border-status-red ring-1 ring-status-red' :
                  isNew ? 'border-navy-700 ring-1 ring-navy-700 ring-opacity-30' :
                  'hover:border-navy-700'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="font-extrabold text-navy-700">{app.referenceNumber}</span>
                      <StatusBadge status={app.status} />
                      {isNew && <span className="badge-blue animate-pulse-slow">NEW</span>}
                      {isUrgent && <span className="badge-red animate-pulse-slow">⚠ URGENT</span>}
                      {app.escalationState === 'escalated' && <span className="bg-status-red text-white text-xs font-bold px-2 py-0.5 rounded-full">🚨 ESCALATED</span>}
                    </div>
                    <p className="font-semibold text-sm text-gray-800">{app.fullName}</p>
                    <p className="text-sm text-gray-600">{app.businessName || app.cooperativeName}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {app.serviceCode === 'trading-licence' ? '🏪 Trading Licence' : '🌿 Agribusiness Permit'}
                      {' · '}{app.district}
                      {' · '}Submitted: {new Date(app.submittedAt).toLocaleDateString('en-UG', { day: 'numeric', month: 'short' })}
                    </p>
                  </div>
                  <div className="shrink-0 w-44 space-y-2">
                    <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResponseHours} label="Response SLA" />
                    <SlaTimer submittedAt={app.submittedAt} slaHours={app.slaResolveHours} label="Resolution SLA" />
                  </div>
                  <div className="text-navy-700 text-xl self-center">›</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
