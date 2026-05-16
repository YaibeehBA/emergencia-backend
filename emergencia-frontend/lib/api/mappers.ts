import type {
  AgentDecision,
  AgentStep,
  DashboardStats,
  DecisionStatus,
  EmergencyCase,
  Period,
  PeriodStats,
} from '@/lib/types'

const DEFAULT_STEPS: AgentStep[] = [
  { step: 1, description: 'Verificación de póliza activa', durationMs: 0 },
  { step: 2, description: 'Análisis de preexistencias', durationMs: 0 },
  { step: 3, description: 'Verificación de suspensiones', durationMs: 0 },
  { step: 4, description: 'Emisión de decisión por agente IA', durationMs: 0 },
]

export interface BackendAgentDecision {
  status: string
  cedula?: string
  policy_number?: string | null
  decision_reason: string
  confidence: number
  pre_existing_conditions?: string[]
  is_suspended?: boolean
  requires_manual_review?: boolean
  processing_time_ms?: number
  timestamp?: string
}

export interface BackendCaseListItem {
  id: number
  cedula: string
  hospital_name?: string | null
  status?: string
  confidence?: number
  decision_reason?: string
  processing_time_ms?: number | null
  created_at: string
}

export interface BackendCaseDetail {
  id: number
  cedula: string
  hospital_id?: string | null
  hospital_name?: string | null
  hospital_email?: string
  agent_decision: BackendAgentDecision
  notification_status?: string
  hospital_notified_at?: string | null
  insurance_notified_at?: string | null
  processing_time_ms?: number | null
  admission_timestamp: string
  created_at: string
}

export interface BackendStatistics {
  period_hours: number
  total_cases: number
  approved: number
  denied: number
  pending: number
  avg_processing_time_ms: number
  approval_rate: number
  timestamp?: string
}

export interface AdmissionPayload {
  cedula: string
  hospital_id: string
  hospital_name?: string
  hospital_email: string
  insurance_manager_email: string
  admission_timestamp: string
}

export interface AdmissionResult {
  case_id: number
  cedula: string
  hospital_id: string
  hospital_email: string
  decision: BackendAgentDecision
  created_at: string
}

function asDecisionStatus(status: string): DecisionStatus {
  if (status === 'APPROVED' || status === 'DENIED' || status === 'PENDING_DOCUMENTS') {
    return status
  }
  return 'PENDING_DOCUMENTS'
}

function inferPolicyExpired(decision: BackendAgentDecision): boolean {
  const reason = (decision.decision_reason ?? '').toLowerCase()
  return reason.includes('vencid') || reason.includes('expir')
}

export function mapAgentDecision(
  raw: BackendAgentDecision,
  processingTimeMs?: number,
): AgentDecision {
  const preexisting = raw.pre_existing_conditions ?? []
  const ms = raw.processing_time_ms ?? processingTimeMs ?? 0

  return {
    status: asDecisionStatus(raw.status),
    confidence: raw.confidence ?? 0,
    reason: raw.decision_reason ?? '',
    policyNumber: raw.policy_number ?? '—',
    hasPreexistences: preexisting.length > 0,
    policySuspended: raw.is_suspended ?? false,
    policyExpired: inferPolicyExpired(raw),
    requiresManualReview: raw.requires_manual_review ?? false,
    processingTimeMs: ms,
    agentSteps: DEFAULT_STEPS.map((s, i) => ({
      ...s,
      durationMs: i === DEFAULT_STEPS.length - 1 ? ms : 0,
    })),
  }
}

export function mapCaseListItem(item: BackendCaseListItem): EmergencyCase {
  const decisionRaw: BackendAgentDecision = {
    status: item.status ?? 'PENDING_DOCUMENTS',
    decision_reason: item.decision_reason ?? '',
    confidence: item.confidence ?? 0,
    policy_number: null,
    pre_existing_conditions: [],
    is_suspended: false,
    requires_manual_review: false,
    processing_time_ms: item.processing_time_ms ?? undefined,
  }

  return {
    id: String(item.id),
    cedula: item.cedula,
    patientName: `Paciente · ${item.cedula}`,
    hospitalId: '',
    hospitalName: item.hospital_name ?? '—',
    emails: [],
    createdAt: item.created_at,
    decision: mapAgentDecision(decisionRaw, item.processing_time_ms ?? undefined),
  }
}

export function mapCaseDetail(detail: BackendCaseDetail): EmergencyCase {
  const emails = detail.hospital_email ? [detail.hospital_email] : []

  return {
    id: String(detail.id),
    cedula: detail.cedula,
    patientName: `Paciente · ${detail.cedula}`,
    hospitalId: detail.hospital_id ?? '—',
    hospitalName: detail.hospital_name ?? '—',
    emails,
    createdAt: detail.created_at,
    decision: mapAgentDecision(
      detail.agent_decision,
      detail.processing_time_ms ?? undefined,
    ),
  }
}

export function mapDashboardStats(stats: BackendStatistics): DashboardStats {
  const approvalRate =
    stats.approval_rate > 1 ? stats.approval_rate / 100 : stats.approval_rate

  return {
    casesToday: stats.total_cases,
    approvalRate,
    avgProcessingMs: Math.round(stats.avg_processing_time_ms),
    pendingReview: stats.pending,
  }
}

export function mapPeriodStats(
  stats: BackendStatistics,
  period: Period,
): PeriodStats {
  const total = stats.total_cases
  const avgConfidence =
    stats.approval_rate > 1 ? stats.approval_rate / 100 : stats.approval_rate

  return {
    period,
    total,
    approved: stats.approved,
    denied: stats.denied,
    pending: stats.pending,
    avgConfidence,
    avgProcessingMs: Math.round(stats.avg_processing_time_ms),
    manualReviews: stats.pending,
  }
}

export function periodToHours(period: Period): number {
  switch (period) {
    case '24h':
      return 24
    case '7d':
      return 168
    case '30d':
      return 720
    default:
      return 24
  }
}
