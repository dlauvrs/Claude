import { google } from 'googleapis';
import type { Job, VehicleCompatibility } from './types';

function getAuth() {
  return new google.auth.GoogleAuth({
    credentials: {
      client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
      private_key: process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    },
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
}

function rowToJob(row: string[]): Job | null {
  if (!row[0]) return null;
  try {
    return {
      jobId: row[0] ?? '',
      status: (row[1] as Job['status']) ?? 'pending_price',
      phone: row[2] ?? '',
      partId: row[3] ?? '',
      title: row[4] ?? '',
      description: row[5] ?? '',
      suggestedPrice: parseFloat(row[6]) || 0,
      finalPrice: row[7] ? parseFloat(row[7]) : undefined,
      mlCategoryId: row[8] ?? '',
      color: row[9] ?? '',
      vehicleCompat: row[10] ? (JSON.parse(row[10]) as VehicleCompatibility[]) : [],
      photoUrls: row[11] ? (JSON.parse(row[11]) as string[]) : [],
      resumeWebhookUrl: row[12] ?? '',
      mlListingId: row[13] || undefined,
      mlListingUrl: row[14] || undefined,
      createdAt: row[15] ?? '',
      publishedAt: row[16] || undefined,
    };
  } catch {
    return null;
  }
}

export async function getJobs(status?: Job['status']): Promise<Job[]> {
  const auth = getAuth();
  const sheets = google.sheets({ version: 'v4', auth });

  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: process.env.GOOGLE_SHEETS_SPREADSHEET_ID,
    range: 'jobs!A2:R',
  });

  const rows = res.data.values as string[][] | null | undefined;
  if (!rows) return [];

  const jobs = rows.map(rowToJob).filter((j): j is Job => j !== null);
  return status ? jobs.filter((j) => j.status === status) : jobs;
}

export async function getJobById(jobId: string): Promise<Job | null> {
  const jobs = await getJobs();
  return jobs.find((j) => j.jobId === jobId) ?? null;
}
