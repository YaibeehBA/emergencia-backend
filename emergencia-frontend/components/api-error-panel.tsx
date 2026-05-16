import Link from 'next/link'

export default function ApiErrorPanel({
  title = 'Servicio no disponible',
  message,
}: {
  title?: string
  message: string
}) {
  return (
    <div className="border border-[var(--lambo-gold-dark)] bg-[var(--lambo-charcoal)] p-8 max-w-2xl">
      <p className="lambo-label text-[var(--lambo-gold)] mb-3">Aviso del sistema</p>
      <h2 className="text-white text-lg mb-3">{title}</h2>
      <p className="text-sm text-[var(--lambo-ash)] mb-6 leading-relaxed">{message}</p>
      <Link
        href="/"
        className="inline-block bg-[var(--lambo-gold)] text-black px-6 py-3 text-xs uppercase tracking-wide hover:bg-[var(--lambo-gold-dark)] transition-colors"
      >
        Volver al inicio
      </Link>
    </div>
  )
}
