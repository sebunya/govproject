export type PersonaType = 'citizen' | 'officer' | 'supervisor' | 'leadership';

export type ApplicationStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'pending_countersign'
  | 'approved'
  | 'rejected'
  | 'more_info_requested';

export interface NiraResult {
  fullName: string;
  dateOfBirth: string;
  district: string;
  gender: string;
  verified: boolean;
  _simulated: true;
}

export interface UraResult {
  taxStatus: string;
  clearanceValidUntil: string;
  _simulated: true;
}

export interface Application {
  id: number;
  referenceNumber: string;
  serviceType: string;
  nin: string;
  fullName: string;
  dateOfBirth: string;
  district: string;
  gender: string;
  cooperativeName: string;
  proposedTin: string;
  taxStatus: string;
  taxClearanceValidUntil: string;
  consentTimestamp: string;
  status: ApplicationStatus;
  slaResponseHours: number;
  slaResolveHours: number;
  submittedAt: string;
  respondedAt: string | null;
  resolvedAt: string | null;
  assignedOfficerId: number | null;
  officerNotes: string | null;
  officerDecision: string | null;
  supervisorNotes: string | null;
  supervisorDecision: string | null;
  documents: Document[];
  rating: number | null;
  ratingComment: string | null;
  ratedAt: string | null;
}

export interface Document {
  id: number;
  applicationId: number;
  originalName: string;
  storedName: string;
  fileType: string;
  uploadedAt: string;
}

export interface Officer {
  id: number;
  name: string;
  role: 'officer' | 'supervisor';
  district: string;
}

export interface DashboardMetrics {
  todayProcessed: number;
  weekProcessed: number;
  avgResolutionHours: number;
  slaCompliancePercent: number;
  activeApplications: number;
  bottlenecks: Bottleneck[];
  districtStats: DistrictStat[];
  weeklyTrend: WeeklyTrendPoint[];
  categoryStats: CategoryStat[];
}

export interface Bottleneck {
  stage: string;
  count: number;
  avgWaitHours: number;
}

export interface DistrictStat {
  district: string;
  total: number;
  approved: number;
  slaBreached: number;
}

export interface WeeklyTrendPoint {
  week: string;
  submitted: number;
  resolved: number;
  slaBreached: number;
}

export interface CategoryStat {
  category: string;
  total: number;
  slaBreached: number;
  avgResolutionHours: number;
}
