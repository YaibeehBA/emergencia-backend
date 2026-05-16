'use client'

import { useEffect, useState } from 'react'
import { checkApiHealth } from '@/lib/api/health'

type Status = 'checking' | 'online' | 'offline'

export default function SystemStatus() {
  const [status, setStatus] = useState<Status>('checking')

  useEffect(() => {
    let cancelled = false

    const run = async () => {
      setStatus('checking')
      const ok = await checkApiHealth()
      if (!cancelled) setStatus(ok ? 'online' : 'offline')
    }

    run()
    const interval = setInterval(run, 60_000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  const label =
    status === 'checking'
      ? 'Sincronizando…'
      : status === 'online'
        ? 'Sistema operativo'
        : 'Sin conexión al servidor'

  const dotColor =
    status === 'online'
      ? 'bg-[var(--lambo-gold)]'
      : status === 'offline'
        ? 'bg-red-500'
        : 'bg-[var(--lambo-ash)]'

  return (
    <div className="flex items-center gap-2" title={label}>
      <span className="relative flex h-2 w-2">
        {status === 'online' && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--lambo-gold)] opacity-40" />
        )}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${dotColor}`} />
      </span>
      <span className="lambo-label text-[0.6rem] text-[var(--lambo-ash)]">{label}</span>
    </div>
  )
}
