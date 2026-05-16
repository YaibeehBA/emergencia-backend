'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import StatusBadge from '@/components/status-badge'
import EmptyState from '@/components/empty-state'
import { formatDateTime24 } from '@/lib/datetime'
import type { EmergencyCase, DecisionStatus } from '@/lib/types'

interface CasesTableProps {
  cases: EmergencyCase[]
  showFilters?: boolean
  /** Vista previa sin paginación (ej. centro de operaciones) */
  limit?: number
  /** Paginación en vista completa de casos */
  paginate?: boolean
  pageSize?: number
}

export default function CasesTable({
  cases,
  showFilters = false,
  limit,
  paginate = false,
  pageSize = 10,
}: CasesTableProps) {
  const router = useRouter()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<'ALL' | DecisionStatus>('ALL')
  const [page, setPage] = useState(1)

  const filtered = useMemo(
    () =>
      cases.filter((c) => {
        const matchesSearch =
          search === '' ||
          c.cedula.includes(search) ||
          c.patientName.toLowerCase().includes(search.toLowerCase()) ||
          c.id.toLowerCase().includes(search.toLowerCase())
        const matchesStatus =
          statusFilter === 'ALL' || c.decision.status === statusFilter
        return matchesSearch && matchesStatus
      }),
    [cases, search, statusFilter],
  )

  const usePagination = paginate && !limit
  const totalPages = usePagination
    ? Math.max(1, Math.ceil(filtered.length / pageSize))
    : 1

  useEffect(() => {
    setPage(1)
  }, [search, statusFilter, cases.length])

  useEffect(() => {
    if (page > totalPages) setPage(totalPages)
  }, [page, totalPages])

  const displayed = useMemo(() => {
    if (limit) return filtered.slice(0, limit)
    if (usePagination) {
      const start = (page - 1) * pageSize
      return filtered.slice(start, start + pageSize)
    }
    return filtered
  }, [filtered, limit, usePagination, page, pageSize])

  const rangeStart = usePagination ? (page - 1) * pageSize + 1 : 1
  const rangeEnd = usePagination
    ? Math.min(page * pageSize, filtered.length)
    : displayed.length

  return (
    <div className="space-y-6">
      {showFilters && (
        <div className="flex flex-wrap gap-4 items-end justify-between">
          <div className="flex flex-wrap gap-4">
            <Input
              placeholder="Buscar por cédula, nombre o ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="max-w-sm"
            />
            <Select
              value={statusFilter}
              onValueChange={(v) => setStatusFilter(v as typeof statusFilter)}
            >
              <SelectTrigger className="w-52 bg-[var(--lambo-iron)] border-[#333] rounded-none text-white">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent className="bg-[var(--lambo-charcoal)] border-[#333] text-white rounded-none">
                <SelectItem value="ALL">Todos los estados</SelectItem>
                <SelectItem value="APPROVED">Aprobado</SelectItem>
                <SelectItem value="DENIED">Denegado</SelectItem>
                <SelectItem value="PENDING_DOCUMENTS">Pendiente</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {usePagination && filtered.length > 0 && (
            <p className="lambo-label text-[0.6rem] text-[var(--lambo-steel)]">
              {filtered.length} caso{filtered.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>
      )}

      {displayed.length === 0 ? (
        <EmptyState
          message="No se encontraron casos."
          description="Intente con otros filtros o realice una nueva admisión."
        />
      ) : (
        <>
          <div className="border border-[var(--lambo-charcoal)] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-black bg-[var(--lambo-charcoal)]">
                  <th className="text-left py-4 px-4 lambo-label text-[0.6rem]">ID</th>
                  <th className="text-left py-4 px-4 lambo-label text-[0.6rem]">Paciente</th>
                  <th className="text-left py-4 px-4 lambo-label text-[0.6rem] hidden md:table-cell">
                    Cédula
                  </th>
                  <th className="text-left py-4 px-4 lambo-label text-[0.6rem] hidden lg:table-cell">
                    Hospital
                  </th>
                  <th className="text-left py-4 px-4 lambo-label text-[0.6rem]">Estado</th>
                  <th className="text-right py-4 px-4 lambo-label text-[0.6rem] hidden md:table-cell">
                    Fecha
                  </th>
                </tr>
              </thead>
              <tbody>
                {displayed.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => router.push(`/casos/${c.id}`)}
                    className="border-b border-black last:border-0 cursor-pointer transition-colors hover:bg-[var(--lambo-charcoal)]"
                  >
                    <td className="py-4 px-4 text-[var(--lambo-steel)] text-xs">{c.id}</td>
                    <td className="py-4 px-4 text-white uppercase text-xs tracking-wide">
                      {c.patientName}
                    </td>
                    <td className="py-4 px-4 text-[var(--lambo-ash)] hidden md:table-cell">
                      {c.cedula}
                    </td>
                    <td className="py-4 px-4 text-[var(--lambo-ash)] hidden lg:table-cell truncate max-w-[200px]">
                      {c.hospitalName}
                    </td>
                    <td className="py-4 px-4">
                      <StatusBadge status={c.decision.status} />
                    </td>
                    <td className="py-4 px-4 text-[var(--lambo-steel)] text-xs text-right hidden md:table-cell">
                      {formatDateTime24(c.createdAt)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {usePagination && filtered.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-[var(--lambo-charcoal)]">
              <p className="lambo-label text-[0.6rem] text-[var(--lambo-ash)]">
                Mostrando {rangeStart}–{rangeEnd} de {filtered.length}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Anterior
                </Button>
                <span className="lambo-label text-[0.65rem] text-white px-3">
                  {page} / {totalPages}
                </span>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
