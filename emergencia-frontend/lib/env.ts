/** Configuración pública del cliente (variable NEXT_PUBLIC_API_URL en despliegue). */

function normalizeOrigin(url: string): string {
  return url.trim().replace(/\/+$/, '')
}

export const publicEnv = {
  apiUrl: normalizeOrigin(
    process.env.NEXT_PUBLIC_API_URL?.trim() || 'http://localhost:8000',
  ),
  isProduction: process.env.NODE_ENV === 'production',
} as const
