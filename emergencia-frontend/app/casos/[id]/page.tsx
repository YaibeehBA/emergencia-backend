import { notFound } from 'next/navigation'
import AppHeader from '@/components/app-header'
import AppFooter from '@/components/app-footer'
import ApiErrorPanel from '@/components/api-error-panel'
import CaseDetailView from '@/components/case-detail-view'
import { ApiError } from '@/lib/api/client'
import { getCaseById } from '@/lib/api/emergencies'
import type { EmergencyCase } from '@/lib/types'

export default async function CaseDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  if (!/^\d+$/.test(id)) notFound()

  let caso: EmergencyCase | null = null
  let apiError: string | null = null

  try {
    caso = await getCaseById(id)
  } catch (e) {
    const msg =
      e instanceof ApiError
        ? e.message
        : e instanceof Error
          ? e.message
          : 'Error desconocido'
    apiError = msg
    caso = null
  }

  if (!caso && !apiError) notFound()

  return (
    <>
      <AppHeader />
      <main className="pt-20 min-h-screen">
        <div className="max-w-4xl mx-auto px-6 md:px-10 py-16">
          {apiError ? (
            <ApiErrorPanel message={`No se pudo cargar el caso #${id}: ${apiError}`} />
          ) : (
            caso && <CaseDetailView caso={caso} />
          )}
        </div>
        <AppFooter narrow />
      </main>
    </>
  )
}
