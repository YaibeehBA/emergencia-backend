'use client'

import { useEffect, useState } from 'react'
import AppHeader from '@/components/app-header'
import AppFooter from '@/components/app-footer'
import PageTitle from '@/components/page-title'
import { fetchPeriodStats } from '@/lib/api/emergencies'
import { ApiError } from '@/lib/api/client'
import type { Period, PeriodStats } from '@/lib/types'

const PERIODS: { value: Period; label: string }[] = [
  { value: '24h', label: '24 h' },
  { value: '7d', label: '7 días' },
  { value: '30d', label: '30 días' },
]

function StatRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between items-baseline border-b border-black py-4 last:border-0">
      <span className="text-sm text-[var(--lambo-ash)]">{label}</span>
      <span className="text-sm text-white font-medium">{value}</span>
    </div>
  )
}

export default function EstadisticasPage() {
  const [period, setPeriod] = useState<Period>('7d')
  const emptyStats: PeriodStats = {
    total: 0,
    approved: 0,
    denied: 0,
    pending: 0,
    manualReviews: 0,
    avgConfidence: 0,
    avgProcessingMs: 0,
  }
  const [stats, setStats] = useState<PeriodStats>(emptyStats)
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setApiError(null)
    fetchPeriodStats(period)
      .then((data) => {
        if (!cancelled) setStats(data)
      })
      .catch((e) => {
        if (!cancelled) {
          const msg =
            e instanceof ApiError
              ? e.message
              : e instanceof Error
                ? e.message
                : 'Error desconocido'
          setApiError(msg)
          setStats(emptyStats)
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [period])

  const approvalRate =
    stats.total > 0 ? ((stats.approved / stats.total) * 100).toFixed(1) : '0.0'
  const deniedRate =
    stats.total > 0 ? ((stats.denied / stats.total) * 100).toFixed(1) : '0.0'
  const pendingRate =
    stats.total > 0 ? ((stats.pending / stats.total) * 100).toFixed(1) : '0.0'

  return (
    <>
      <AppHeader />
      <main className="pt-20 min-h-screen">
        <div className="max-w-4xl mx-auto px-6 md:px-10 py-16">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-6 mb-12">
            <PageTitle
              title="Estadísticas"
              subtitle="Resumen de decisiones del agente por período."
            />
            <nav
              aria-label="Selector de período"
              className="flex border border-white/20 shrink-0"
            >
              {PERIODS.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => setPeriod(p.value)}
                  className={`lambo-label text-[0.65rem] px-5 py-3 transition-colors ${
                    period === p.value
                      ? 'bg-[var(--lambo-gold)] text-black'
                      : 'text-[var(--lambo-ash)] hover:text-white'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </nav>
          </div>

          {loading && (
            <p className="lambo-label text-[var(--lambo-gold)] mb-6">Actualizando...</p>
          )}

          {apiError && (
            <p className="text-sm text-red-400 border border-red-400/40 bg-red-950/30 p-4 mb-6">
              Error al cargar estadísticas desde el backend: {apiError}. Reinicia el
              servidor backend si acabas de actualizar el código.
            </p>
          )}

          <div className="grid md:grid-cols-2 gap-12 bg-[var(--lambo-charcoal)] p-8">
            <div>
              <p className="lambo-label mb-4">Volumen</p>
              <StatRow label="Total de casos" value={stats.total} />
              <StatRow label="Aprobados" value={`${stats.approved} (${approvalRate}%)`} />
              <StatRow label="Denegados" value={`${stats.denied} (${deniedRate}%)`} />
              <StatRow
                label="Pendientes de documentos"
                value={`${stats.pending} (${pendingRate}%)`}
              />
              <StatRow label="Revisiones manuales" value={stats.manualReviews} />
            </div>
            <div>
              <p className="lambo-label mb-4">Rendimiento</p>
              <StatRow
                label="Confianza media"
                value={`${Math.round(stats.avgConfidence * 100)}%`}
              />
              <StatRow
                label="Tiempo medio"
                value={`${stats.avgProcessingMs.toLocaleString('es')} ms`}
              />
              <StatRow
                label="Tiempo medio (s)"
                value={`${(stats.avgProcessingMs / 1000).toFixed(2)} s`}
              />
              <StatRow label="Período" value={period} />
            </div>
          </div>

          <div className="mt-12">
            <p className="lambo-label mb-4">Distribución</p>
            <div className="flex h-1 w-full bg-[var(--lambo-iron)]">
              {stats.approved > 0 && (
                <div
                  style={{ width: `${(stats.approved / stats.total) * 100}%` }}
                  className="h-full bg-[var(--lambo-gold)]"
                />
              )}
              {stats.denied > 0 && (
                <div
                  style={{ width: `${(stats.denied / stats.total) * 100}%` }}
                  className="h-full bg-white/40"
                />
              )}
              {stats.pending > 0 && (
                <div
                  style={{ width: `${(stats.pending / stats.total) * 100}%` }}
                  className="h-full bg-[var(--lambo-steel)]"
                />
              )}
            </div>
          </div>
        </div>

        <AppFooter narrow />
      </main>
    </>
  )
}
