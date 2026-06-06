const STATUS_CONFIG: Record<string, { label: string; cls: string }> = {
  draft:                  { label: 'Draft',                    cls: 'badge-blue' },
  submitted:              { label: 'Submitted — Awaiting Review', cls: 'badge-blue' },
  under_review:           { label: 'Under Review',             cls: 'badge-blue' },
  pending_countersign:    { label: 'Pending Countersignature', cls: 'badge-orange' },
  approved:               { label: 'Approved',                 cls: 'badge-green' },
  rejected:               { label: 'Rejected',                 cls: 'badge-red' },
  more_info_requested:    { label: 'More Information Requested', cls: 'badge-orange' },
  withdrawn:              { label: 'Withdrawn',                   cls: 'bg-gray-200 text-gray-600 text-xs font-semibold px-2 py-0.5 rounded-full' },
};

export default function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] || { label: status, cls: 'badge-blue' };
  return <span className={cfg.cls}>{cfg.label}</span>;
}
