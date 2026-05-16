import Link from 'next/link'
import AppHeader from '@/components/app-header'
import PageTitle from '@/components/page-title'
import CasesTable from '@/components/cases-table'
import AppFooter from '@/components/app-footer'
import ApiErrorPanel from '@/components/api-error-panel'
import { ApiError } from '@/lib/api/client'
import { fetchDashboardStats, getRecentCases } from '@/lib/api/emergencies'
import type { DashboardStats, EmergencyCase } from '@/lib/types'

function StatItem({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="space-y-2 border-l-2 border-[var(--lambo-gold)] pl-6 py-2">
      <p className="lambo-display text-3xl md:text-4xl text-white">{value}</p>
      <p className="lambo-label text-[0.6rem] text-[var(--lambo-ash)]">{label}</p>
    </div>
  )
}

export default async function OperacionesPage() {
  let stats: DashboardStats
  let recentCases: EmergencyCase[]
  let apiError: string | null = null

  try {
    ;[stats, recentCases] = await Promise.all([
      fetchDashboardStats(),
      getRecentCases(7, 24),
    ])
  } catch (e) {
    const msg =
      e instanceof ApiError
        ? e.message
        : e instanceof Error
          ? e.message
          : 'Error desconocido'
    apiError = msg
    stats = {
      casesToday: 0,
      approvalRate: 0,
      avgProcessingMs: 0,
      pendingReview: 0,
    }
    recentCases = []
  }

  return (
    <>
      <AppHeader />
      <main className="pt-20 min-h-screen">
        <div className="max-w-6xl mx-auto px-6 md:px-10 py-16">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-12">
            <PageTitle
              title="Centro de operaciones"
              subtitle="Monitoreo y supervisión en tiempo real de validaciones de emergencia."
            />
            <Link
              href="/"
              className="inline-block shrink-0 bg-[var(--lambo-gold)] text-black px-6 py-3 text-xs uppercase tracking-wide hover:bg-[var(--lambo-gold-dark)] transition-colors"
            >
              + Nueva emergencia
            </Link>
          </div>

          <p className="lambo-label text-[var(--lambo-gold)] text-[0.65rem] mb-8 -mt-4">
            Supervisión · Últimas 24 horas
          </p>

          {apiError && (
            <div className="mb-10">
              <ApiErrorPanel
                message={`No fue posible obtener los datos del servidor (${apiError}). Verifique que el servicio de validación esté activo.`}
              />
            </div>
          )}

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            <StatItem label="Casos hoy" value={stats.casesToday} />
            <StatItem
              label="Tasa de aprobación"
              value={`${Math.round(stats.approvalRate * 100)}%`}
            />
            <StatItem
              label="Tiempo medio"
              value={`${stats.avgProcessingMs.toLocaleString('es')} ms`}
            />
            <StatItem label="Pendientes revisión" value={stats.pendingReview} />
          </div>

          <div className="mb-6 flex items-end justify-between border-b border-[var(--lambo-charcoal)] pb-4">
            <h2 className="lambo-display text-lg text-white">Cola reciente</h2>
            <Link href="/casos" className="lambo-link text-xs">
              Ver todos los casos
            </Link>
          </div>

          <CasesTable cases={recentCases} />
        </div>
        <AppFooter />
      </main>
    </>
  )
}
