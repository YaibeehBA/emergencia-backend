import { publicEnv } from '@/lib/env'

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${publicEnv.apiUrl}/health`, {
      cache: 'no-store',
    })
    return res.ok
  } catch {
    return false
  }
}
