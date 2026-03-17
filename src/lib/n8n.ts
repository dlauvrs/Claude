export async function resumeWorkflow(
  resumeWebhookUrl: string,
  payload: { price: number; action: 'approve' | 'reject'; jobId: string }
): Promise<void> {
  const res = await fetch(resumeWebhookUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`n8n resume webhook returned ${res.status}`);
  }
}
