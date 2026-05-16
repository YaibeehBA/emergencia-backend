import Link from 'next/link'
import AppHeader from '@/components/app-header'
import PageTitle from '@/components/page-title'
import CasesTable from '@/components/cases-table'
import AppFooter from '@/components/app-footer'
import ApiErrorPanel from '@/components/api-error-panel'
import { ApiError } from '@/lib/api/client'
import { getRecentCases } from '@/lib/api/emergencies'

export default async function CasosPage() {
  let cases: Awaited<ReturnType<typeof getRecentCases>> = []
  let apiError: string | null = null

  try {
    cases = await getRecentCases(50, 168)
  } catch (e) {
    apiError =
      e instanceof ApiError
        ? e.message
        : e instanceof Error
          ? e.message
          : 'Error desconocido'
  }

  return (
    <>
      <AppHeader />
      <main className="pt-20 min-h-screen">
        <div className="max-w-6xl mx-auto px-6 md:px-10 py-16">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-4">
            <PageTitle
              title="Casos"
              subtitle={`${cases.length} registros. Seleccione una fila para ver el detalle.`}
            />
            <Link
              href="/"
              className="lambo-link text-xs shrink-0 mb-8 sm:mb-12"
            >
              + Nueva emergencia
            </Link>
          </div>
          {apiError && (
            <div className="mb-10">
              <ApiErrorPanel message={`No se pudieron cargar los casos: ${apiError}`} />
            </div>
          )}
          <CasesTable cases={cases} showFilters paginate pageSize={10} />
        </div>
        <AppFooter />
      </main>
    </>
  )
}
