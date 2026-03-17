import type { JobStatus } from '@/lib/types';

const CONFIG: Record<JobStatus, { label: string; className: string }> = {
  pending_price: {
    label: 'Aguardando Preço',
    className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  },
  published: {
    label: 'Publicado',
    className: 'bg-green-100 text-green-800 border-green-200',
  },
  rejected: {
    label: 'Rejeitado',
    className: 'bg-red-100 text-red-800 border-red-200',
  },
};

export function StatusBadge({ status }: { status: JobStatus }) {
  const { label, className } = CONFIG[status];
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  );
}
