import { ApiError, apiFetch } from './client'
import { API_PREFIX } from './config'
import {
  mapAgentDecision,
  mapCaseDetail,
  mapCaseListItem,
  mapDashboardStats,
  mapPeriodStats,
  periodToHours,
  type AdmissionPayload,
  type AdmissionResult,
  type BackendCaseDetail,
  type BackendCaseListItem,
  type BackendStatistics,
} from './mappers'
import type {
  AgentDecision,
  DashboardStats,
  EmergencyCase,
  Period,
  PeriodStats,
} from '@/lib/types'

interface CasesListData {
  total: number
  limit: number
  hours: number
  cases: BackendCaseListItem[]
}

export async function submitAdmission(
  payload: AdmissionPayload,
): Promise<{ caseId: number; decision: AgentDecision }> {
  const data = await apiFetch<AdmissionResult>(`${API_PREFIX}/admission`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })

  return {
    caseId: data.case_id,
    decision: mapAgentDecision(data.decision),
  }
}

export async function getRecentCases(
  limit = 20,
  hours = 24,
): Promise<EmergencyCase[]> {
  const data = await apiFetch<CasesListData>(
    `${API_PREFIX}/cases?limit=${limit}&hours=${hours}`,
  )
  return data.cases.map(mapCaseListItem)
}

export async function getCaseById(id: string): Promise<EmergencyCase | null> {
  try {
    const data = await apiFetch<BackendCaseDetail>(`${API_PREFIX}/cases/${id}`)
    return mapCaseDetail(data)
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null
    throw e
  }
}

export async function getStatistics(hours = 24): Promise<BackendStatistics> {
  return apiFetch<BackendStatistics>(`${API_PREFIX}/statistics?hours=${hours}`)
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const stats = await getStatistics(24)
  return mapDashboardStats(stats)
}

export async function fetchPeriodStats(period: Period): Promise<PeriodStats> {
  const stats = await getStatistics(periodToHours(period))
  return mapPeriodStats(stats, period)
}
