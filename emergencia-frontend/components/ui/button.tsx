import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-normal uppercase tracking-[0.02em] transition-colors disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-[var(--lambo-gold)] focus-visible:ring-offset-2 focus-visible:ring-offset-black rounded-none",
  {
    variants: {
      variant: {
        default:
          'bg-[var(--lambo-gold)] text-black hover:bg-[var(--lambo-gold-dark)]',
        destructive:
          'bg-[var(--lambo-gold-dark)] text-white hover:bg-[#7a6200]',
        outline:
          'border border-white/50 bg-transparent text-white hover:bg-[var(--lambo-teal)] hover:border-[var(--lambo-teal)] hover:text-white',
        secondary:
          'bg-[var(--lambo-charcoal)] text-white hover:bg-[#2a2a2a]',
        ghost:
          'text-[var(--lambo-ash)] hover:text-white hover:bg-transparent',
        link: 'text-[var(--lambo-ash)] underline-offset-4 hover:text-[var(--lambo-link)] hover:underline normal-case',
      },
      size: {
        default: 'h-12 px-6 py-3',
        sm: 'h-10 px-4 text-xs',
        lg: 'h-14 px-8 text-base',
        icon: 'size-12',
        'icon-sm': 'size-10',
        'icon-lg': 'size-14',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : 'button'

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
