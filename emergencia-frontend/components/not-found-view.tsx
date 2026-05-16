import Link from 'next/link'
import AppHeader from '@/components/app-header'
import AppFooter from '@/components/app-footer'

const QUICK_LINKS = [
  { href: '/', label: 'Nueva emergencia' },
  { href: '/operaciones', label: 'Centro de operaciones' },
  { href: '/casos', label: 'Casos' },
  { href: '/estadisticas', label: 'Estadísticas' },
] as const

export default function NotFoundView() {
  return (
    <>
      <AppHeader />
      <main className="pt-20 min-h-screen flex flex-col">
        <div className="flex-1 max-w-3xl mx-auto px-6 md:px-10 py-20 w-full">
          <p className="lambo-label text-[var(--lambo-gold)] mb-6">Error 404</p>

          <p
            className="lambo-display text-[clamp(5rem,18vw,10rem)] leading-none text-white/10 select-none mb-2"
            aria-hidden
          >
            404
          </p>

          <h1 className="lambo-display text-3xl md:text-5xl text-white leading-[0.95] mb-6">
            Ruta no encontrada
          </h1>

          <p className="text-base text-[var(--lambo-ash)] max-w-xl leading-relaxed mb-10">
            La página que buscas no existe o fue movida. Use los accesos siguientes
            para volver al flujo de validación hospitalaria.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 mb-14">
            <Link
              href="/"
              className="inline-flex justify-center items-center bg-[var(--lambo-gold)] text-black px-8 py-4 text-xs uppercase tracking-wide hover:bg-[var(--lambo-gold-dark)] transition-colors"
            >
              Ir a nueva emergencia
            </Link>
            <Link
              href="/operaciones"
              className="inline-flex justify-center items-center border border-white/20 text-white px-8 py-4 text-xs uppercase tracking-wide hover:border-[var(--lambo-gold)] hover:text-[var(--lambo-gold)] transition-colors"
            >
              Centro de operaciones
            </Link>
          </div>

          <nav aria-label="Enlaces rápidos">
            <p className="lambo-label text-[0.65rem] text-[var(--lambo-steel)] mb-4">
              Enlaces rápidos
            </p>
            <ul className="grid sm:grid-cols-2 gap-3">
              {QUICK_LINKS.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="block border border-[var(--lambo-charcoal)] bg-[var(--lambo-charcoal)]/50 px-5 py-4 text-sm text-[var(--lambo-ash)] hover:text-[var(--lambo-gold)] hover:border-[var(--lambo-gold-dark)] transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
        <AppFooter narrow />
      </main>
    </>
  )
}
