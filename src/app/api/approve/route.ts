import { NextRequest, NextResponse } from 'next/server';
import { getJobById } from '@/lib/sheets';
import { resumeWorkflow } from '@/lib/n8n';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { jobId: string; price: number; action: 'approve' | 'reject' };
    const { jobId, price, action } = body;

    if (!jobId || !action) {
      return NextResponse.json({ error: 'jobId and action are required' }, { status: 400 });
    }
    if (action === 'approve' && (!price || price <= 0)) {
      return NextResponse.json({ error: 'A valid price is required to approve' }, { status: 400 });
    }

    const job = await getJobById(jobId);
    if (!job) {
      return NextResponse.json({ error: 'Job not found' }, { status: 404 });
    }
    if (job.status !== 'pending_price') {
      return NextResponse.json(
        { error: `Job is already ${job.status}` },
        { status: 409 }
      );
    }
    if (!job.resumeWebhookUrl) {
      return NextResponse.json({ error: 'No resume webhook URL for this job' }, { status: 500 });
    }

    await resumeWorkflow(job.resumeWebhookUrl, { price, action, jobId });
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error('[api/approve]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
