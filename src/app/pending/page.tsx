'use client';

import { useJobs } from '@/hooks/useJobs';
import { JobCard } from '@/components/JobCard';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export default function PendingPage() {
  const { jobs, isLoading, isError } = useJobs('pending_price');

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">Aguardando Aprovação</h1>
        <span className="text-sm text-gray-500">Atualiza a cada 15s</span>
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner />
        </div>
      )}

      {isError && (
        <div className="rounded-lg bg-red-50 p-4 text-center text-red-600">
          Erro ao carregar anúncios. Verifique a conexão.
        </div>
      )}

      {!isLoading && !isError && jobs.length === 0 && (
        <div className="rounded-lg bg-gray-100 p-8 text-center text-gray-500">
          Nenhum anúncio aguardando aprovação.
        </div>
      )}

      {!isLoading && jobs.length > 0 && (
        <div className="space-y-3">
          {jobs.map((job) => (
            <JobCard key={job.jobId} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
