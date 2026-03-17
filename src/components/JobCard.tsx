import Link from 'next/link';
import Image from 'next/image';
import type { Job } from '@/lib/types';
import { StatusBadge } from './StatusBadge';

export function JobCard({ job }: { job: Job }) {
  const thumb = job.photoUrls[0];
  const createdAt = new Date(job.createdAt).toLocaleString('pt-BR');

  return (
    <Link href={`/job/${job.jobId}`} className="block">
      <div className="flex gap-4 rounded-lg border border-gray-200 bg-white p-4 transition hover:border-blue-300 hover:shadow-sm">
        <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-md bg-gray-100">
          {thumb ? (
            <Image src={thumb} alt={job.title} fill className="object-cover" unoptimized />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-300 text-xs">
              Sem foto
            </div>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-start justify-between gap-2">
            <h3 className="truncate text-sm font-semibold text-gray-900">{job.title}</h3>
            <StatusBadge status={job.status} />
          </div>
          <p className="mb-2 text-xs text-gray-500 line-clamp-2">{job.description}</p>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-blue-700">
              R$ {job.suggestedPrice.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-xs text-gray-400">{createdAt}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
