interface EmptyStateProps {
  message: string
  description?: string
}

export default function EmptyState({ message, description }: EmptyStateProps) {
  return (
    <div className="py-16 text-center">
      <p className="text-sm text-muted-foreground">{message}</p>
      {description && (
        <p className="mt-1 text-xs text-muted-foreground/60">{description}</p>
      )}
    </div>
  )
}
