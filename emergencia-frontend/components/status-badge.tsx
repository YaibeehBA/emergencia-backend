import { cn } from '@/lib/utils'
import type { DecisionStatus } from '@/lib/types'

const STATUS_CONFIG: Record<
  DecisionStatus,
  { label: string; className: string }
> = {
  APPROVED: {
    label: 'Aprobado',
    className: 'text-[var(--lambo-gold)] border-[var(--lambo-gold)]',
  },
  DENIED: {
    label: 'Denegado',
    className: 'text-white border-white/40',
  },
  PENDING_DOCUMENTS: {
    label: 'Pendiente de documentos',
    className: 'text-[var(--lambo-ash)] border-[var(--lambo-steel)]',
  },
}

interface StatusBadgeProps {
  status: DecisionStatus
  className?: string
}

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status]
  return (
    <span
      className={cn(
        'inline-block lambo-label text-[0.65rem] border px-3 py-1',
        config.className,
        className,
      )}
    >
      {config.label}
    </span>
  )
}
