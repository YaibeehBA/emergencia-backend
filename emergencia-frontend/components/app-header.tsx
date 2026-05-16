'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import SystemStatus from '@/components/system-status'

const NAV_LINKS = [
  { href: '/', label: 'Nueva emergencia', exact: true },
  { href: '/operaciones', label: 'Centro de operaciones', exact: false },
  { href: '/casos', label: 'Casos', exact: false },
  { href: '/estadisticas', label: 'Estadísticas', exact: false },
]

export default function AppHeader() {
  const pathname = usePathname()

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-sm border-b border-[var(--lambo-charcoal)]">
      <div className="max-w-6xl mx-auto px-6 md:px-10 h-16 flex items-center justify-between gap-4">
        <Link href="/" className="group shrink-0">
          <span className="lambo-display text-lg text-white group-hover:text-[var(--lambo-gold)] transition-colors">
            SENTRIA
          </span>
        </Link>

        <nav
          aria-label="Navegación principal"
          className="hidden md:flex items-center gap-8"
        >
          {NAV_LINKS.map((link) => {
            const isActive = link.exact
              ? pathname === link.href
              : pathname.startsWith(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'lambo-label text-[0.65rem] transition-colors',
                  isActive
                    ? 'text-[var(--lambo-gold)]'
                    : 'text-[var(--lambo-ash)] hover:text-white',
                )}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>

        <div className="hidden sm:block">
          <SystemStatus />
        </div>
      </div>
    </header>
  )
}
