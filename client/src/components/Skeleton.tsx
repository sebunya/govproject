interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function SkeletonLine({ className = '' }: { className?: string }) {
  return <div className={`skeleton-text ${className}`} aria-hidden="true" />;
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`card space-y-3 ${className}`} aria-hidden="true">
      <div className="flex items-center justify-between">
        <div className="skeleton h-5 w-2/5 rounded" />
        <div className="skeleton h-6 w-16 rounded-full" />
      </div>
      <div className="skeleton h-4 w-3/5 rounded" />
      <div className="skeleton h-4 w-4/5 rounded" />
      <div className="flex gap-2 pt-1">
        <div className="skeleton h-8 w-24 rounded-lg" />
        <div className="skeleton h-8 w-20 rounded-lg" />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 4, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="card p-0 overflow-hidden" aria-hidden="true" aria-busy="true" aria-label="Loading…">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <div className="skeleton h-4 w-32 rounded" />
      </div>
      <div className="divide-y divide-gray-100">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="px-4 py-3 flex gap-4">
            {Array.from({ length: cols }).map((_, c) => (
              <div key={c} className={`skeleton h-4 rounded flex-1 ${c === 0 ? 'max-w-[120px]' : ''}`} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonStatCards({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4" style={{ gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))` }} aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="stat-card space-y-2">
          <div className="skeleton h-3 w-20 rounded" />
          <div className="skeleton h-8 w-16 rounded" />
          <div className="skeleton h-3 w-24 rounded" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonText({ lines = 3, className = '' }: SkeletonProps) {
  const widths = ['w-full', 'w-5/6', 'w-4/6', 'w-3/5', 'w-full', 'w-2/3'];
  return (
    <div className={`space-y-2 ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`skeleton h-4 rounded ${widths[i % widths.length]}`} />
      ))}
    </div>
  );
}

export default function Skeleton({ className = '', lines = 1 }: SkeletonProps) {
  if (lines > 1) return <SkeletonText lines={lines} className={className} />;
  return <div className={`skeleton ${className}`} aria-hidden="true" />;
}
