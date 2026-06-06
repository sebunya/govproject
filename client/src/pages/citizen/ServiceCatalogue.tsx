import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { SkeletonCard } from '../../components/Skeleton';

export default function ServiceCatalogue() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const persona = params.get('persona') || 'citizen';

  const { data: services = [], isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: () => axios.get('/api/services').then(r => r.data),
    staleTime: 60000,
  });

  if (isLoading) return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading services…">
      <div className="h-8 w-48 skeleton rounded" />
      <div className="space-y-4">
        <SkeletonCard /><SkeletonCard />
      </div>
    </div>
  );

  const active = (services as any[]).filter((s: any) => s.active);
  const upcoming = (services as any[]).filter((s: any) => !s.active);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-navy-700">Service Catalogue</h1>
        <div className="w-16 h-0.5 bg-gold-500 mt-1 mb-2" />
        <p className="text-gray-600">Select a service to begin your application. Mbarara District Local Government.</p>
      </div>

      {active.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Available Now</h2>
          {active.map((svc: any) => {
            const docs: string[] = svc.requiredDocs ? svc.requiredDocs.split(',').map((d: string) => d.trim()) : [];
            const hasFee = svc.feeAmount > 0;
            return (
              <div
                key={svc.code}
                className="card hover:shadow-md hover:border-navy-700 cursor-pointer transition-all"
                onClick={() => navigate(`/portal/apply?persona=${persona}&service=${svc.code}`)}
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl p-3 rounded-xl bg-navy-50">{svc.icon}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-bold text-base text-navy-700">{svc.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{svc.description}</p>
                      </div>
                      <span className="badge-green shrink-0">Available</span>
                    </div>
                    <div className="flex flex-wrap gap-4 mt-3 text-xs text-gray-500">
                      <span>📂 {svc.category}</span>
                      <span>⏱ Response: {svc.slaResponseHours}h · Resolve: {Math.round(svc.slaResolveHours / 24)} days</span>
                      <span>💳 {hasFee ? `${svc.feeCurrency} ${Number(svc.feeAmount).toLocaleString()}` : 'No fee'}</span>
                    </div>
                    {docs.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        <span className="text-xs text-gray-400">Required:</span>
                        {docs.map(d => (
                          <span key={d} className="text-xs bg-navy-50 border border-navy-100 text-navy-700 px-2 py-0.5 rounded-full">{d}</span>
                        ))}
                      </div>
                    )}
                    {hasFee && (
                      <p className="text-xs text-yellow-800 bg-gold-50 border border-gold-500 rounded px-2 py-1 mt-2 inline-block">
                        💳 Fee payable via MTN/Airtel Mobile Money or Card — Pesapal Sandbox pattern
                      </p>
                    )}
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <button className="btn-primary text-sm py-2">Apply Now →</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {upcoming.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Coming Soon</h2>
          {upcoming.map((svc: any) => (
            <div key={svc.code} className="card opacity-60">
              <div className="flex items-start gap-4">
                <div className="text-3xl p-3 rounded-xl bg-gray-100">{svc.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-bold text-base text-gray-500">{svc.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{svc.description}</p>
                    </div>
                    <span className="badge-orange shrink-0">Coming soon</span>
                  </div>
                  <div className="flex flex-wrap gap-4 mt-3 text-xs text-gray-400">
                    <span>📂 {svc.category}</span>
                    <span>⏱ SLA: {Math.round(svc.slaResolveHours / 24)} days</span>
                    <span>💳 {svc.feeAmount > 0 ? `${svc.feeCurrency} ${Number(svc.feeAmount).toLocaleString()}` : 'No fee'}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
