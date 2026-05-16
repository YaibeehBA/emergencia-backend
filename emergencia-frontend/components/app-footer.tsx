import Link from 'next/link'

export default function AppFooter({ narrow = false }: { narrow?: boolean }) {
  return (
    <footer
      className={`${narrow ? 'max-w-3xl' : 'max-w-6xl'} mx-auto px-6 md:px-10 pb-10 pt-8 border-t border-[var(--lambo-charcoal)]`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <p className="lambo-label text-[0.65rem] text-white">SENTRIA</p>
          <p className="text-[0.65rem] text-[var(--lambo-steel)] mt-1">
            Sistema Inteligente de Validación Hospitalaria
          </p>
        </div>
        <div className="flex gap-6">
          <Link href="/operaciones" className="lambo-link text-[0.65rem]">
            Centro de operaciones
          </Link>
          <Link href="/casos" className="lambo-link text-[0.65rem]">
            Casos
          </Link>
        </div>
      </div>
    </footer>
  )
}
