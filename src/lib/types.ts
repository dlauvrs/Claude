export type JobStatus = 'pending_price' | 'published' | 'rejected';

export interface VehicleCompatibility {
  make: string;
  model: string;
  yearFrom: number;
  yearTo: number;
}

export interface Job {
  jobId: string;
  status: JobStatus;
  phone: string;
  partId: string;
  title: string;
  description: string;
  suggestedPrice: number;
  finalPrice?: number;
  mlCategoryId: string;
  color: string;
  vehicleCompat: VehicleCompatibility[];
  photoUrls: string[];
  resumeWebhookUrl: string;
  mlListingId?: string;
  mlListingUrl?: string;
  createdAt: string;
  publishedAt?: string;
}
