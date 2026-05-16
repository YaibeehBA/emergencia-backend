'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import TimeInput24 from '@/components/time-input-24'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import StatusBadge from '@/components/status-badge'
import ConfidenceBar from '@/components/confidence-bar'
import { ADMISSION_LOADING_STEPS } from '@/lib/admission-loading'
import { submitAdmission } from '@/lib/api/emergencies'
import {
  admissionLocalToIso,
  getLocalAdmissionDefaults,
} from '@/lib/datetime'
import type { AgentDecision } from '@/lib/types'

type Phase = 'idle' | 'loading' | 'result'

function AdmissionResult({
  result,
  caseId,
  onReset,
}: {
  result: AgentDecision
  caseId: number
  onReset: () => void
}) {
  const router = useRouter()

  return (
    <div className="space-y-8 border border-[var(--lambo-charcoal)] bg-[var(--lambo-charcoal)] p-8">
      <div className="space-y-4">
        <p className="lambo-label">Decisión del agente IA</p>
        <StatusBadge status={result.status} />
        <ConfidenceBar confidence={result.confidence} />
      </div>

      <div>
        <p className="lambo-label mb-2">Fundamento</p>
        <p className="text-sm text-[var(--lambo-smoke)] leading-relaxed">{result.reason}</p>
      </div>

      <dl className="space-y-3 text-sm border-t border-black pt-6">
        {[
          { label: 'Número de póliza', value: result.policyNumber },
          { label: 'Preexistencias', value: result.hasPreexistences ? 'Sí' : 'No' },
          { label: 'Póliza suspendida', value: result.policySuspended ? 'Sí' : 'No' },
          { label: 'Póliza vencida', value: result.policyExpired ? 'Sí' : 'No' },
          { label: 'Revisión manual', value: result.requiresManualReview ? 'Sí' : 'No' },
          { label: 'Tiempo de procesamiento', value: `${result.processingTimeMs} ms` },
        ].map(({ label, value }) => (
          <div key={label} className="flex gap-6">
            <dt className="w-48 shrink-0 text-[var(--lambo-ash)]">{label}</dt>
            <dd className="text-white">{value}</dd>
          </div>
        ))}
      </dl>

      <div className="flex flex-wrap gap-4 pt-4">
        {caseId > 0 && (
          <Button type="button" onClick={() => router.push(`/casos/${caseId}`)}>
            Ver caso #{caseId}
          </Button>
        )}
        <Button type="button" variant="outline" onClick={onReset}>
          Otra emergencia
        </Button>
        <Link href="/operaciones">
          <Button type="button" variant="ghost">
            Centro de operaciones
          </Button>
        </Link>
      </div>
    </div>
  )
}

export default function AdmissionForm() {
  const [cedula, setCedula] = useState('')
  const [hospitalId, setHospitalId] = useState('')
  const [hospitalName, setHospitalName] = useState('')
  const [hospitalEmail, setHospitalEmail] = useState('')
  const [insuranceEmail, setInsuranceEmail] = useState('casos@segurosecuador.com')
  const [admissionDate, setAdmissionDate] = useState(
    () => getLocalAdmissionDefaults().date,
  )
  const [admissionTime, setAdmissionTime] = useState(
    () => getLocalAdmissionDefaults().time,
  )
  const [phase, setPhase] = useState<Phase>('idle')
  const [visibleSteps, setVisibleSteps] = useState<string[]>([])
  const [result, setResult] = useState<AgentDecision | null>(null)
  const [caseId, setCaseId] = useState(0)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPhase('loading')
    setVisibleSteps([])
    setResult(null)
    setCaseId(0)

    for (let i = 0; i < ADMISSION_LOADING_STEPS.length; i++) {
      await new Promise((r) => setTimeout(r, 400 + Math.random() * 200))
      setVisibleSteps((prev) => [...prev, ADMISSION_LOADING_STEPS[i]])
    }

    try {
      const admission = await submitAdmission({
        cedula: cedula.replace(/\D/g, '').slice(0, 10),
        hospital_id: hospitalId,
        hospital_name: hospitalName,
        hospital_email: hospitalEmail,
        insurance_manager_email: insuranceEmail,
        admission_timestamp: admissionLocalToIso(admissionDate, admissionTime),
      })
      setResult(admission.decision)
      setCaseId(admission.caseId)
      setPhase('result')
      toast.success('Emergencia procesada correctamente')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al procesar admisión')
      setPhase('idle')
    }
  }

  const handleReset = () => {
    setPhase('idle')
    setVisibleSteps([])
    setResult(null)
    setCaseId(0)
    setCedula('')
    setHospitalId('')
    setHospitalName('')
    setHospitalEmail('')
    setInsuranceEmail('casos@segurosecuador.com')
    const now = getLocalAdmissionDefaults()
    setAdmissionDate(now.date)
    setAdmissionTime(now.time)
  }

  if (phase === 'loading') {
    const progress = (visibleSteps.length / ADMISSION_LOADING_STEPS.length) * 100
    return (
      <div className="space-y-8 py-6">
        <div>
          <p className="lambo-label text-[var(--lambo-gold)] mb-2">Agente SENTRIA en ejecución</p>
          <p className="text-xs text-[var(--lambo-steel)]">
            Validando cobertura · cédula {cedula || '—'}
          </p>
        </div>
        <div className="h-[2px] w-full bg-[var(--lambo-iron)]">
          <div
            className="h-full bg-[var(--lambo-gold)] transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <ul className="space-y-3">
          {visibleSteps.map((step, i) => (
            <li key={i} className="text-sm text-[var(--lambo-ash)] flex gap-3">
              <span className="text-[var(--lambo-gold)] text-xs">
                {String(i + 1).padStart(2, '0')}
              </span>
              {step}
            </li>
          ))}
        </ul>
      </div>
    )
  }

  if (phase === 'result' && result) {
    return <AdmissionResult result={result} caseId={caseId} onReset={handleReset} />
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-10">
      <div className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="cedula" className="lambo-label">
            Cédula del paciente
          </Label>
          <Input
            id="cedula"
            value={cedula}
            onChange={(e) => setCedula(e.target.value.replace(/\D/g, '').slice(0, 10))}
            placeholder="Ingrese cédula de 10 dígitos"
            required
            maxLength={10}
          />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="hospitalId" className="lambo-label">
              ID del hospital
            </Label>
            <Input
              id="hospitalId"
              value={hospitalId}
              onChange={(e) => setHospitalId(e.target.value)}
              placeholder="Identificador del centro"
              required
            />
          </div>
          <div className="space-y-2">
            <Label className="lambo-label">Fecha y hora de ingreso</Label>
            <div className="grid grid-cols-2 gap-3">
              <Input
                id="admissionDate"
                type="date"
                lang="es-EC"
                value={admissionDate}
                onChange={(e) => setAdmissionDate(e.target.value)}
                required
                aria-label="Fecha de ingreso"
              />
              <TimeInput24
                id="admissionTime"
                value={admissionTime}
                onChange={setAdmissionTime}
                aria-label="Hora de ingreso"
              />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="hospitalName" className="lambo-label">
            Nombre del hospital
          </Label>
          <Input
            id="hospitalName"
            value={hospitalName}
            onChange={(e) => setHospitalName(e.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="hospitalEmail" className="lambo-label">
            Correo del hospital
          </Label>
          <Input
            id="hospitalEmail"
            type="email"
            value={hospitalEmail}
            onChange={(e) => setHospitalEmail(e.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="insuranceEmail" className="lambo-label">
            Correo gestor de seguros
          </Label>
          <Input
            id="insuranceEmail"
            type="email"
            value={insuranceEmail}
            onChange={(e) => setInsuranceEmail(e.target.value)}
            required
          />
        </div>
      </div>

      <Button type="submit" size="lg">
        Iniciar validación
      </Button>
    </form>
  )
}
