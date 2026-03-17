'use client';

import useSWR from 'swr';
import type { Job } from '@/lib/types';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function useJobs(status?: Job['status']) {
  const url = status ? `/api/jobs?status=${status}` : '/api/jobs';
  const { data, error, isLoading, mutate } = useSWR<Job[]>(url, fetcher, {
    refreshInterval: 15000,
  });

  return {
    jobs: data ?? [],
    isLoading,
    isError: !!error,
    refresh: mutate,
  };
}

export function useJob(jobId: string) {
  const { data, error, isLoading, mutate } = useSWR<Job>(
    jobId ? `/api/jobs?jobId=${jobId}` : null,
    fetcher,
    { refreshInterval: 10000 }
  );

  return { job: data ?? null, isLoading, isError: !!error, refresh: mutate };
}
