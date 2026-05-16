'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import AdmissionHero from '@/components/admission-hero'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const STORAGE_KEY = 'sentria_splash_dismissed'
const FADE_MS = 550

interface SentriaSplashProps {
  onContinue: () => void
}

export function hasSeenSplash(): boolean {
  if (typeof window === 'undefined') return true
  return sessionStorage.getItem(STORAGE_KEY) === '1'
}

export function dismissSplash(): void {
  sessionStorage.setItem(STORAGE_KEY, '1')
}

type SplashPhase = 'visible' | 'exiting' | 'hidden'

export default function SentriaSplash({ onContinue }: SentriaSplashProps) {
  const [phase, setPhase] = useState<SplashPhase>('visible')
  const scrollRef = useRef<HTMLDivElement>(null)
  const exitingRef = useRef(false)

  const exit = useCallback(() => {
    if (exitingRef.current) return
    exitingRef.current = true
    dismissSplash()
    setPhase('exiting')
    window.setTimeout(() => {
      setPhase('hidden')
      onContinue()
    }, FADE_MS)
  }, [onContinue])

  useEffect(() => {
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [])

  useEffect(() => {
    const onWheel = (e: WheelEvent) => {
      if (Math.abs(e.deltaY) > 8) exit()
    }
    let touchStartY = 0
    const onTouchStart = (e: TouchEvent) => {
      touchStartY = e.touches[0]?.clientY ?? 0
    }
    const onTouchMove = (e: TouchEvent) => {
      const y = e.touches[0]?.clientY ?? touchStartY
      if (touchStartY - y > 50) exit()
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
        e.preventDefault()
        exit()
      }
    }
    window.addEventListener('wheel', onWheel, { passive: true })
    window.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchmove', onTouchMove, { passive: true })
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('wheel', onWheel)
      window.removeEventListener('touchstart', onTouchStart)
      window.removeEventListener('touchmove', onTouchMove)
      window.removeEventListener('keydown', onKey)
    }
  }, [exit])

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    if (el.scrollTop > 48) exit()
  }

  if (phase === 'hidden') return null

  return (
    <div
      className={cn(
        'splash-overlay fixed inset-0 z-[100] bg-black',
        phase === 'exiting' && 'splash-overlay--exit',
      )}
      role="dialog"
      aria-modal="true"
      aria-label="Presentación SENTRIA"
    >
      <div className="flex h-[100dvh] max-h-[100dvh] flex-col">
        {/* Contenido desplazable */}
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto overscroll-y-contain px-5 pt-20 pb-6 sm:px-8 md:px-10 md:pt-24"
        >
          <div className="mx-auto max-w-6xl">
            <AdmissionHero variant="splash" />
            <p className="mt-8 text-center lambo-label text-[0.6rem] text-[var(--lambo-steel)] animate-pulse">
              Desliza hacia abajo o pulse continuar
            </p>
          </div>
        </div>

        {/* Barra fija: botón siempre visible */}
        <div className="shrink-0 border-t border-[var(--lambo-charcoal)] bg-black px-5 pt-4 pb-[max(1rem,env(safe-area-inset-bottom))] sm:px-8 md:px-10">
          <div className="mx-auto flex max-w-6xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="lambo-label text-center text-[0.6rem] text-[var(--lambo-steel)] sm:text-left">
              Registrar una nueva emergencia
            </p>
            <Button
              type="button"
              size="lg"
              className="w-full sm:w-auto min-h-12 shrink-0"
              onClick={exit}
            >
              Continuar
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
