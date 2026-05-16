interface PageTitleProps {
  title: string
  subtitle?: string
}

export default function PageTitle({ title, subtitle }: PageTitleProps) {
  return (
    <div className="mb-12 border-b border-[var(--lambo-charcoal)] pb-8">
      <h1 className="lambo-display text-3xl md:text-5xl text-white leading-[0.95]">
        {title}
      </h1>
      {subtitle && (
        <p className="mt-4 text-base text-[var(--lambo-ash)] max-w-2xl">{subtitle}</p>
      )}
    </div>
  )
}
