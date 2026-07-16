import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchLatestIndicators } from '../api/client'
import type { IndicatorSnapshot } from '../api/types'

type SortKey = 'symbol' | 'close' | 'rsi' | 'macdHist' | 'vwap'

function SortArrow({ active, asc }: { active: boolean; asc: boolean }) {
  if (!active) return null
  return <span className="ml-1 text-accent">{asc ? '↑' : '↓'}</span>
}

function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 10 }).map((_, i) => (
        <tr key={i} className="border-t border-border">
          {Array.from({ length: 6 }).map((__, j) => (
            <td key={j} className="px-4 py-3">
              <div className="skeleton w-16" />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}

export function ScreenerPage() {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('symbol')
  const [sortAsc, setSortAsc] = useState(true)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['indicators-latest'],
    queryFn: fetchLatestIndicators,
  })

  const rows = useMemo(() => {
    if (!data) return []
    const filtered = search
      ? data.filter((r) => r.symbol.includes(search.toUpperCase()))
      : data
    const sorted = [...filtered].sort((a: IndicatorSnapshot, b: IndicatorSnapshot) => {
      const av = a[sortKey]
      const bv = b[sortKey]
      if (typeof av === 'string' && typeof bv === 'string') {
        return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av)
      }
      return sortAsc ? (av as number) - (bv as number) : (bv as number) - (av as number)
    })
    return sorted
  }, [data, search, sortKey, sortAsc])

  const stats = useMemo(() => {
    if (!data) return null
    const oversold = data.filter((r) => r.rsi < 35).length
    const overbought = data.filter((r) => r.rsi > 70).length
    return { total: data.length, oversold, overbought }
  }, [data])

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortAsc((asc) => !asc)
    } else {
      setSortKey(key)
      setSortAsc(true)
    }
  }

  return (
    <div>
      <h1 className="page-title">Screener</h1>
      <p className="page-subtitle">Latest indicator snapshot per symbol across the S&amp;P 500.</p>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Tickers screened</div>
          <div className="stat-value">{stats?.total ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Oversold (RSI &lt; 35)</div>
          <div className="stat-value text-emerald-600 dark:text-emerald-400">{stats?.oversold ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overbought (RSI &gt; 70)</div>
          <div className="stat-value text-rose-600 dark:text-rose-400">{stats?.overbought ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Showing</div>
          <div className="stat-value">{Math.min(rows.length, 200)}</div>
        </div>
      </div>

      <div className="filters">
        <input
          type="text"
          className="input-field"
          placeholder="Search symbol..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isError && <p className="error-text mb-4">Failed to load watchlist: {(error as Error).message}</p>}

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th className="sortable" onClick={() => toggleSort('symbol')}>
                Symbol <SortArrow active={sortKey === 'symbol'} asc={sortAsc} />
              </th>
              <th className="sortable" onClick={() => toggleSort('close')}>
                Close <SortArrow active={sortKey === 'close'} asc={sortAsc} />
              </th>
              <th className="sortable" onClick={() => toggleSort('rsi')}>
                RSI <SortArrow active={sortKey === 'rsi'} asc={sortAsc} />
              </th>
              <th className="sortable" onClick={() => toggleSort('macdHist')}>
                MACD Hist <SortArrow active={sortKey === 'macdHist'} asc={sortAsc} />
              </th>
              <th className="sortable" onClick={() => toggleSort('vwap')}>
                VWAP <SortArrow active={sortKey === 'vwap'} asc={sortAsc} />
              </th>
              <th>As of</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <SkeletonRows />}
            {rows.slice(0, 200).map((r) => (
              <tr key={r.symbol}>
                <td className="symbol">{r.symbol}</td>
                <td>${r.close.toFixed(2)}</td>
                <td className={r.rsi < 35 ? 'flag-low' : r.rsi > 70 ? 'flag-high' : ''}>
                  {r.rsi.toFixed(1)}
                </td>
                <td>{r.macdHist.toFixed(3)}</td>
                <td>${r.vwap.toFixed(2)}</td>
                <td>{new Date(r.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > 200 && (
        <p className="page-subtitle mt-3">Showing first 200 of {rows.length} matching tickers.</p>
      )}
    </div>
  )
}
