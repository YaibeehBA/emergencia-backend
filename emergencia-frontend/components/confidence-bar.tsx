interface ConfidenceBarProps {
  confidence: number
  showLabel?: boolean
}

export default function ConfidenceBar({
  confidence,
  showLabel = true,
}: ConfidenceBarProps) {
  const pct = Math.round(confidence * 100)

  return (
    <div className="space-y-2">
      {showLabel && (
        <div className="flex justify-between items-baseline">
          <span className="lambo-label text-[0.65rem]">Confianza del agente</span>
          <span className="text-sm text-white">{pct}%</span>
        </div>
      )}
      <div className="h-[2px] w-full bg-[var(--lambo-iron)]">
        <div
          className="h-full bg-[var(--lambo-gold)] transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
