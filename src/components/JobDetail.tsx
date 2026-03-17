import type { Job } from '@/lib/types';

export function JobDetail({ job }: { job: Job }) {
  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <div>
        <h2 className="text-lg font-bold text-gray-900">{job.title}</h2>
        {job.partId && (
          <p className="mt-0.5 text-xs text-gray-500">Código: {job.partId}</p>
        )}
      </div>

      <div>
        <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
          Descrição
        </h3>
        <p className="text-sm text-gray-700 whitespace-pre-line">{job.description}</p>
      </div>

      {job.vehicleCompat.length > 0 && (
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
            Compatibilidades
          </h3>
          <ul className="space-y-0.5">
            {job.vehicleCompat.map((v, i) => (
              <li key={i} className="text-sm text-gray-700">
                {v.make} {v.model} {v.yearFrom}–{v.yearTo}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">Cor</span>
          <p className="text-gray-700">{job.color || '—'}</p>
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Categoria ML
          </span>
          <p className="text-gray-700">{job.mlCategoryId || '—'}</p>
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            WhatsApp
          </span>
          <p className="text-gray-700">{job.phone}</p>
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Recebido em
          </span>
          <p className="text-gray-700">
            {new Date(job.createdAt).toLocaleString('pt-BR')}
          </p>
        </div>
      </div>

      {job.mlListingUrl && (
        <a
          href={job.mlListingUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
        >
          Ver anúncio no Mercado Livre →
        </a>
      )}
    </div>
  );
}
