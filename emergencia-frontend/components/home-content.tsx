'use client'

import { useEffect, useState } from 'react'
import SentriaSplash, { hasSeenSplash } from '@/components/sentria-splash'
import AdmissionForm from '@/components/admission-form'
import SystemStatus from '@/components/system-status'

export default function HomeContent() {
  const [mounted, setMounted] = useState(false)
  const [showSplash, setShowSplash] = useState(false)

  useEffect(() => {
    setShowSplash(!hasSeenSplash())
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className="min-h-[50vh]" aria-hidden />
  }

  return (
    <>
      {showSplash && <SentriaSplash onContinue={() => setShowSplash(false)} />}

      {!showSplash && (
        <div className="max-w-3xl mx-auto px-5 sm:px-6 md:px-10 py-6 md:py-10">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
            <div>
              <p className="lambo-label text-[var(--lambo-gold)] mb-2">Nueva emergencia</p>
              <h1 className="lambo-display text-3xl md:text-4xl text-white leading-tight">
                Ingreso de paciente
              </h1>
            </div>
            <SystemStatus />
          </div>

          <section>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between mb-8 border-b border-[var(--lambo-charcoal)] pb-4">
              <h2 className="lambo-label text-[var(--lambo-ash)]">Validación de cobertura</h2>
              <span className="lambo-label text-[0.6rem] text-[var(--lambo-steel)]">
                Agente IA · SENTRIA
              </span>
            </div>
            <AdmissionForm />
          </section>
        </div>
      )}
    </>
  )
}
