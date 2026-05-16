const LOCALE = 'es-EC'
const pad = (n: number) => String(n).padStart(2, '0')

/** Fecha local YYYY-MM-DD para input type="date". */
export function toDateInputValue(date: Date = new Date()): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

/** Hora local HH:mm (24 h) para input type="time". */
export function toTimeInputValue(date: Date = new Date()): string {
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function getLocalAdmissionDefaults(date: Date = new Date()) {
  return {
    date: toDateInputValue(date),
    time: toTimeInputValue(date),
  }
}

export function combineDateAndTime(date: string, time: string): string {
  return `${date}T${time}`
}

/** Convierte fecha y hora locales a ISO 8601 para el servicio de validación. */
export function admissionLocalToIso(date: string, time: string): string {
  return new Date(combineDateAndTime(date, time)).toISOString()
}

/**
 * Interpreta marcas de tiempo del backend (ISO 8601 o texto con AM/PM).
 */
export function parseBackendDateTime(value: string): Date {
  if (!value?.trim()) return new Date(NaN)

  const trimmed = value.trim()
  const iso = new Date(trimmed)
  if (!Number.isNaN(iso.getTime())) return iso

  const amPm = trimmed.match(
    /^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(a\.?\s*m\.?|p\.?\s*m\.?|AM|PM)$/i,
  )
  if (!amPm) return new Date(NaN)

  const a = parseInt(amPm[1], 10)
  const b = parseInt(amPm[2], 10)
  let year = parseInt(amPm[3], 10)
  if (year < 100) year += 2000

  let hour = parseInt(amPm[4], 10)
  const minute = parseInt(amPm[5], 10)
  const second = amPm[6] ? parseInt(amPm[6], 10) : 0
  const period = amPm[7].replace(/\./g, '').replace(/\s/g, '').toLowerCase()

  if (period.startsWith('p') && hour < 12) hour += 12
  if (period.startsWith('a') && hour === 12) hour = 0

  const tryBuild = (month: number, day: number) => {
    const d = new Date(year, month - 1, day, hour, minute, second)
    return Number.isNaN(d.getTime()) ? null : d
  }

  if (a > 12) return tryBuild(b, a) ?? new Date(NaN)
  if (b > 12) return tryBuild(a, b) ?? new Date(NaN)

  return tryBuild(a, b) ?? tryBuild(b, a) ?? new Date(NaN)
}

const FORMAT_24H: Intl.DateTimeFormatOptions = {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
}

/** Fecha y hora en zona local, siempre en formato 24 h (tablas y listados). */
export function formatDateTime24(value: string): string {
  const date = parseBackendDateTime(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleString(LOCALE, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    ...FORMAT_24H,
  })
}

/** Fecha y hora extendida en 24 h (detalle de caso). */
export function formatDateTimeLong24(value: string): string {
  const date = parseBackendDateTime(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleString(LOCALE, {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    ...FORMAT_24H,
  })
}

/** Solo hora HH:mm en 24 h. */
export function formatTime24(value: string): string {
  const date = parseBackendDateTime(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleTimeString(LOCALE, FORMAT_24H)
}

/** Valores para inputs de admisión a partir de una marca del backend. */
export function backendTimestampToInputs(value: string) {
  const date = parseBackendDateTime(value)
  if (Number.isNaN(date.getTime())) return getLocalAdmissionDefaults()
  return {
    date: toDateInputValue(date),
    time: toTimeInputValue(date),
  }
}
