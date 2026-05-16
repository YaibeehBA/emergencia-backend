'use client'

import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import PageTitle from '@/components/page-title'
import StatusBadge from '@/components/status-badge'
import ConfidenceBar from '@/components/confidence-bar'
import { Button } from '@/components/ui/button'
import { formatDateTimeLong24 } from '@/lib/datetime'
import type { EmergencyCase } from '@/lib/types'

export default function CaseDetailView({ caso }: { caso: EmergencyCase }) {
  const router = useRouter()
  const { decision } = caso

  return (
    <>
      <button
        type="button"
        onClick={() => router.back()}
        className="lambo-link text-xs mb-8 block"
      >
        ← Volver a casos
      </button>

      <PageTitle title={`Caso ${caso.id}`} subtitle={formatDateTimeLong24(caso.createdAt)} />

      <div className="grid md:grid-cols-2 gap-12 mb-12">
        <div className="bg-[var(--lambo-charcoal)] p-8">
          <p className="lambo-label mb-6">Datos de ingreso</p>
          <dl className="space-y-3 text-sm">
            {[
              { label: 'Paciente', value: caso.patientName },
              { label: 'Cédula', value: caso.cedula },
              { label: 'Hospital', value: caso.hospitalName },
              { label: 'ID Hospital', value: caso.hospitalId },
              {
                label: 'Notificación',
                value: caso.emails.length ? caso.emails.join(', ') : '—',
              },
            ].map(({ label, value }) => (
              <div key={label} className="flex gap-4">
                <dt className="w-32 shrink-0 text-[var(--lambo-ash)]">{label}</dt>
                <dd className="text-white">{value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="bg-[var(--lambo-charcoal)] p-8">
          <p className="lambo-label mb-6">Decisión IA</p>
          <div className="space-y-4">
            <StatusBadge status={decision.status} />
            <ConfidenceBar confidence={decision.confidence} />
            <dl className="space-y-3 text-sm pt-4">
              {[
                { label: 'Póliza', value: decision.policyNumber },
                { label: 'Preexistencias', value: decision.hasPreexistences ? 'Sí' : 'No' },
                { label: 'Suspendida', value: decision.policySuspended ? 'Sí' : 'No' },
                { label: 'Vencida', value: decision.policyExpired ? 'Sí' : 'No' },
                { label: 'Revisión manual', value: decision.requiresManualReview ? 'Sí' : 'No' },
                { label: 'Tiempo', value: `${decision.processingTimeMs} ms` },
              ].map(({ label, value }) => (
                <div key={label} className="flex gap-4">
                  <dt className="w-32 shrink-0 text-[var(--lambo-ash)]">{label}</dt>
                  <dd className="text-white">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      <div className="mb-12">
        <p className="lambo-label mb-3">Fundamento de la decisión</p>
        <p className="text-sm text-[var(--lambo-smoke)] leading-relaxed max-w-3xl">
          {decision.reason}
        </p>
      </div>

      <div className="mb-12">
        <p className="lambo-label mb-6">Pasos del agente IA</p>
        <ol className="space-y-4">
          {decision.agentSteps.map((step) => (
            <li
              key={step.step}
              className="flex gap-4 text-sm border-b border-black pb-4 last:border-0"
            >
              <span className="text-[var(--lambo-gold)] w-6 shrink-0">
                {String(step.step).padStart(2, '0')}
              </span>
              <span className="flex-1 text-[var(--lambo-ash)]">{step.description}</span>
              {step.durationMs > 0 && (
                <span className="text-xs text-[var(--lambo-steel)] shrink-0">
                  {step.durationMs} ms
                </span>
              )}
            </li>
          ))}
        </ol>
      </div>

      <div className="flex flex-wrap gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => toast.success(`Notificación reenviada a ${caso.emails.join(', ') || 'contactos registrados'}`)}
        >
          Reenviar notificación
        </Button>
        <Button
          type="button"
          variant="ghost"
          onClick={() => toast.success('Caso marcado como revisado')}
        >
          Marcar como revisado
        </Button>
      </div>
    </>
  )
}
