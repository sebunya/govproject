import { useState, useEffect } from 'react';

interface SlaTimerProps {
  submittedAt: string;
  slaHours: number;
  label?: string;
  compact?: boolean;
}

export default function SlaTimer({ submittedAt, slaHours, label = 'SLA', compact = false }: SlaTimerProps) {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const submitted = new Date(submittedAt).getTime();
  const deadline = submitted + slaHours * 3600000;
  const totalMs = deadline - submitted;
  const remainingMs = deadline - now;
  const pct = Math.max(0, Math.min(100, (remainingMs / totalMs) * 100));

  const totalSecs = Math.max(0, Math.floor(remainingMs / 1000));
  const daysLeft = Math.floor(totalSecs / 86400);
  const hrsLeft = Math.floor((totalSecs % 86400) / 3600);
  const minsLeft = Math.floor((totalSecs % 3600) / 60);
  const secsLeft = totalSecs % 60;

  const isBreached = remainingMs <= 0;
  const isCritical = pct < 10 && !isBreached;
  const isWarning = pct < 50 && pct >= 10;

  const barColor = isBreached || isCritical ? 'bg-status-red' : isWarning ? 'bg-status-orange' : 'bg-status-green';
  const textColor = isBreached || isCritical ? 'text-status-red' : isWarning ? 'text-status-orange' : 'text-status-green';

  const timeLabel = isBreached
    ? '⚠ SLA BREACHED'
    : daysLeft > 0
    ? `${daysLeft}d ${hrsLeft}h ${minsLeft}m`
    : hrsLeft > 0
    ? `${hrsLeft}h ${minsLeft}m ${secsLeft}s`
    : `${minsLeft}m ${secsLeft}s`;

  if (compact) {
    return (
      <span className={`text-xs font-semibold ${textColor}`}>
        {timeLabel}
      </span>
    );
  }

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500 font-medium">{label}</span>
        <span className={`text-xs font-semibold tabular-nums ${textColor} ${(isCritical || isBreached) ? 'animate-pulse-slow' : ''}`}>
          {timeLabel}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`${barColor} h-2 rounded-full sla-progress`}
          style={{ width: `${isBreached ? 100 : pct}%` }}
        />
      </div>
    </div>
  );
}
