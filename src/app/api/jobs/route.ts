import { NextRequest, NextResponse } from 'next/server';
import { getJobs, getJobById } from '@/lib/sheets';
import type { Job } from '@/lib/types';

export const runtime = 'nodejs';
export const revalidate = 0;

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = req.nextUrl;
    const jobId = searchParams.get('jobId');
    const status = searchParams.get('status') as Job['status'] | null;

    if (jobId) {
      const job = await getJobById(jobId);
      if (!job) return NextResponse.json({ error: 'Not found' }, { status: 404 });
      return NextResponse.json(job);
    }

    const jobs = await getJobs(status ?? undefined);
    return NextResponse.json(jobs);
  } catch (err) {
    console.error('[api/jobs]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
