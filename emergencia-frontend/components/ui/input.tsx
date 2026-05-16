import * as React from 'react'

import { cn } from '@/lib/utils'

function Input({ className, type, ...props }: React.ComponentProps<'input'>) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        'h-10 w-full min-w-0 rounded-none border border-[#333] bg-[var(--lambo-iron)] px-3 py-2 text-sm text-white placeholder:text-[var(--lambo-steel)] transition-colors outline-none',
        'focus-visible:border-[var(--lambo-gold)] focus-visible:ring-0',
        'disabled:pointer-events-none disabled:opacity-50',
        className,
      )}
      {...props}
    />
  )
}

export { Input }
