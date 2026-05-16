'use client'

import { useEffect, useRef, useState } from 'react'
import { Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { ScrollArea } from '@/components/ui/scroll-area'
import { toTimeInputValue } from '@/lib/datetime'
import { cn } from '@/lib/utils'

const pad = (n: number) => String(n).padStart(2, '0')

const HOURS = Array.from({ length: 24 }, (_, i) => pad(i))
const MINUTES = Array.from({ length: 60 }, (_, i) => pad(i))

const inputSurface =
  'h-10 w-full min-w-0 rounded-none border border-[#333] bg-[var(--lambo-iron)] px-3 py-2 text-sm text-white transition-colors outline-none hover:border-[var(--lambo-steel)] focus-visible:border-[var(--lambo-gold)]'

function parseTime(value: string): { hour: string; minute: string } {
  const match = value.match(/^(\d{1,2}):(\d{2})$/)
  if (match) {
    const hour = Math.min(23, Math.max(0, parseInt(match[1], 10)))
    const minute = Math.min(59, Math.max(0, parseInt(match[2], 10)))
    return { hour: pad(hour), minute: pad(minute) }
  }
  const now = new Date()
  return { hour: pad(now.getHours()), minute: pad(now.getMinutes()) }
}

function TimeColumn({
  label,
  items,
  value,
  onSelect,
  scrollKey,
}: {
  label: string
  items: string[]
  value: string
  onSelect: (v: string) => void
  scrollKey: number
}) {
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = listRef.current?.querySelector(`[data-time-value="${value}"]`)
    el?.scrollIntoView({ block: 'center' })
  }, [value, scrollKey])

  return (
    <div className="flex flex-col items-center min-w-0 flex-1">
      <span className="lambo-label text-[0.55rem] text-[var(--lambo-steel)] mb-2">
        {label}
      </span>
      <ScrollArea className="h-44 w-full border border-[#333] bg-black">
        <div ref={listRef} className="py-[4.5rem]">
          {items.map((item) => {
            const selected = item === value
            return (
              <button
                key={item}
                type="button"
                data-time-value={item}
                onClick={() => onSelect(item)}
                className={cn(
                  'flex w-full items-center justify-center py-2.5 text-sm tabular-nums transition-colors',
                  selected
                    ? 'bg-[var(--lambo-gold)] text-black font-medium'
                    : 'text-[var(--lambo-ash)] hover:bg-[var(--lambo-charcoal)] hover:text-white',
                )}
              >
                {item}
              </button>
            )
          })}
        </div>
      </ScrollArea>
    </div>
  )
}

export default function TimeInput24({
  id,
  value,
  onChange,
  className,
  'aria-label': ariaLabel,
}: {
  id?: string
  value: string
  onChange: (value: string) => void
  className?: string
  'aria-label'?: string
}) {
  const [open, setOpen] = useState(false)
  const [scrollKey, setScrollKey] = useState(0)
  const { hour, minute } = parseTime(value)
  const display = `${hour}:${minute}`

  const setHour = (h: string) => onChange(`${h}:${minute}`)
  const setMinute = (m: string) => onChange(`${hour}:${m}`)

  const setNow = () => {
    const t = toTimeInputValue()
    onChange(t)
    setScrollKey((k) => k + 1)
  }

  return (
    <Popover
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (next) setScrollKey((k) => k + 1)
      }}
    >
      <PopoverTrigger asChild>
        <button
          id={id}
          type="button"
          aria-label={ariaLabel ?? 'Seleccionar hora'}
          className={cn(
            inputSurface,
            'flex items-center justify-between gap-2 text-left',
            className,
          )}
        >
          <span className="tabular-nums tracking-wide">{display}</span>
          <Clock className="size-4 shrink-0 text-[var(--lambo-gold)]" aria-hidden />
        </button>
      </PopoverTrigger>
      <PopoverContent
        align="end"
        sideOffset={6}
        className="w-auto rounded-none border border-[#333] bg-[var(--lambo-charcoal)] p-0 shadow-xl"
      >
        <div className="border-b border-[#333] px-4 py-3">
          <p className="lambo-label text-[0.6rem] text-[var(--lambo-gold)]">Hora de ingreso</p>
          <p className="text-2xl text-white tabular-nums tracking-widest mt-1">{display}</p>
        </div>

        <div className="flex gap-2 p-3">
          <TimeColumn
            label="Hora"
            items={HOURS}
            value={hour}
            onSelect={setHour}
            scrollKey={scrollKey}
          />
          <div className="flex items-center pt-6 text-[var(--lambo-gold)] text-lg font-light">
            :
          </div>
          <TimeColumn
            label="Min"
            items={MINUTES}
            value={minute}
            onSelect={setMinute}
            scrollKey={scrollKey}
          />
        </div>

        <div className="flex border-t border-[#333]">
          <Button
            type="button"
            variant="ghost"
            className="flex-1 rounded-none h-11 text-xs uppercase tracking-wide text-[var(--lambo-ash)] hover:text-white hover:bg-black"
            onClick={setNow}
          >
            Ahora
          </Button>
          <Button
            type="button"
            className="flex-1 rounded-none h-11 text-xs uppercase tracking-wide bg-[var(--lambo-gold)] text-black hover:bg-[var(--lambo-gold-dark)]"
            onClick={() => setOpen(false)}
          >
            Listo
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}
