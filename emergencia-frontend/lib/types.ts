// ─────────────────────────────────────────────────────────────
// Emergencia-Sync — TypeScript Types
// ─────────────────────────────────────────────────────────────

export type DecisionStatus = 'APPROVED' | 'DENIED' | 'PENDING_DOCUMENTS'

export interface AgentStep {
  step: number
  description: string
  durationMs: number
}

export interface AgentDecision {
  status: DecisionStatus
  confidence: number          // 0–1
  reason: string
  policyNumber: string
  hasPreexistences: boolean
  policySuspended: boolean
  policyExpired: boolean
  requiresManualReview: boolean
  processingTimeMs: number
  agentSteps: AgentStep[]
}

export interface EmergencyCase {
  id: string
  cedula: string
  patientName: string
  hospitalId: string
  hospitalName: string
  emails: string[]
  createdAt: string           // ISO 8601
  decision: AgentDecision
}

export interface DashboardStats {
  casesToday: number
  approvalRate: number        // 0–1
  avgProcessingMs: number
  pendingReview: number
}

export type Period = '24h' | '7d' | '30d'

export interface PeriodStats {
  period: Period
  total: number
  approved: number
  denied: number
  pending: number
  avgConfidence: number       // 0–1
  avgProcessingMs: number
  manualReviews: number
}
