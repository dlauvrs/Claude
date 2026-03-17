'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useJob } from '@/hooks/useJobs';
import { ImageGallery } from '@/components/ImageGallery';
import { JobDetail } from '@/components/JobDetail';
import { PriceForm } from '@/components/PriceForm';
import { StatusBadge } from '@/components/StatusBadge';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export default function JobPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const router = useRouter();
  const { job, isLoading, isError } = useJob(jobId);
  const [selectedPhoto, setSelectedPhoto] = useState(0);

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <LoadingSpinner />
      </div>
    );
  }

  if (isError || !job) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-red-600">
        Anúncio não encontrado.{' '}
        <Link href="/pending" className="underline">
          Voltar
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <Link href="/pending" className="text-sm text-gray-500 hover:text-gray-700">
          ← Voltar
        </Link>
        <StatusBadge status={job.status} />
      </div>

      <ImageGallery
        photoUrls={job.photoUrls}
        selectedIndex={selectedPhoto}
        onSelect={setSelectedPhoto}
      />

      <JobDetail job={job} />

      {job.status === 'pending_price' && (
        <PriceForm
          jobId={job.jobId}
          suggestedPrice={job.suggestedPrice}
          onSuccess={() => {
            setTimeout(() => router.push('/pending'), 1500);
          }}
        />
      )}
    </div>
  );
}
