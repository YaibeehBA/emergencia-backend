import SystemStatus from '@/components/system-status'
import { cn } from '@/lib/utils'

const PILLARS = [
  {
    title: 'Validación instantánea',
    text: 'Cobertura verificada en segundos al ingreso a emergencia.',
  },
  {
    title: 'Agente IA',
    text: 'Póliza, preexistencias y suspensiones analizadas automáticamente.',
  },
  {
    title: 'Hospital + aseguradora',
    text: 'Decisión compartida con trazabilidad para ambas partes.',
  },
]

interface AdmissionHeroProps {
  variant?: 'default' | 'splash'
}

export default function AdmissionHero({ variant = 'default' }: AdmissionHeroProps) {
  const isSplash = variant === 'splash'

  return (
    <section className={cn(!isSplash && 'mb-14')}>
      <div
        className={cn(
          'flex gap-4 mb-8 md:mb-10',
          isSplash ? 'flex-col sm:flex-row sm:items-start sm:justify-between' : 'items-start justify-between gap-6',
        )}
      >
        <div className="min-w-0">
          <p className="lambo-label text-[var(--lambo-gold)] mb-3 md:mb-4">
            Ingreso de paciente
          </p>
          <h1
            className={cn(
              'lambo-display text-white leading-[0.92] mb-3 md:mb-4',
              isSplash ? 'text-4xl sm:text-5xl md:text-7xl' : 'text-5xl md:text-7xl',
            )}
          >
            SENTRIA
          </h1>
          <p
            className={cn(
              'text-[var(--lambo-ash)] leading-relaxed',
              isSplash ? 'text-sm sm:text-base max-w-lg' : 'text-sm md:text-base max-w-xl',
            )}
          >
            Sistema Inteligente de Validación Hospitalaria. Valide cobertura
            antes de que el tiempo en emergencia se convierta en incertidumbre.
          </p>
        </div>
        <div className={cn(isSplash ? 'shrink-0' : 'hidden md:block pt-2')}>
          <SystemStatus />
        </div>
      </div>

      <div
        className={cn(
          'grid gap-px bg-[var(--lambo-charcoal)]',
          isSplash ? 'grid-cols-1 sm:grid-cols-3' : 'md:grid-cols-3',
        )}
      >
        {PILLARS.map((p) => (
          <div
            key={p.title}
            className={cn('bg-black', isSplash ? 'p-5 sm:p-6 md:p-8' : 'p-6 md:p-8')}
          >
            <p className="lambo-label text-[var(--lambo-gold)] text-[0.65rem] mb-2 md:mb-3">
              {p.title}
            </p>
            <p className="text-xs text-[var(--lambo-ash)] leading-relaxed">{p.text}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
