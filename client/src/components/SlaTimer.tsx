interface SlaTimerProps {
  submittedAt: string;
  slaHours: number;
  label?: string;
}

export default function SlaTimer({ submittedAt, slaHours, label = 'SLA' }: SlaTimerProps) {
  const submitted = new Date(submittedAt).getTime();
  const deadline = submitted + slaHours * 3600000;
  const now = Date.now();
  const totalMs = deadline - submitted;
  const remainingMs = deadline - now;
  const pct = Math.max(0, Math.min(100, (remainingMs / totalMs) * 100));

  const hoursRemaining = Math.max(0, Math.floor(remainingMs / 3600000));
  const daysRemaining = Math.floor(hoursRemaining / 24);
  const hrsLeft = hoursRemaining % 24;

  const isBreached = remainingMs <= 0;
  const isWarning = pct < 50 && pct >= 10;
  const isCritical = pct < 10 && !isBreached;

  const barColor = isBreached
    ? 'bg-status-red'
    : isCritical
    ? 'bg-status-red'
    : isWarning
    ? 'bg-status-orange'
    : 'bg-status-green';

  const textColor = isBreached || isCritical
    ? 'text-status-red'
    : isWarning
    ? 'text-status-orange'
    : 'text-status-green';

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500 font-medium">{label}</span>
        <span className={`text-xs font-semibold ${textColor}`}>
          {isBreached
            ? '⚠ SLA BREACHED'
            : daysRemaining > 0
            ? `${daysRemaining}d ${hrsLeft}h left`
            : `${hoursRemaining}h left`}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`${barColor} h-2 rounded-full sla-progress transition-all`}
          style={{ width: `${isBreached ? 100 : pct}%` }}
        />
      </div>
    </div>
  );
}
