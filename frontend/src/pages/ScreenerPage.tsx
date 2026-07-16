import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchLatestIndicators } from '../api/client'
import type { IndicatorSnapshot } from '../api/types'

type SortKey = 'symbol' | 'close' | 'rsi' | 'macdHist' | 'vwap'

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
      <h1>Screener</h1>
      <p className="subtitle">
        Latest indicator snapshot per symbol across the S&amp;P 500 ({data?.length ?? 0} tickers).
      </p>

      <div className="filters">
        <input
          type="text"
          placeholder="Search symbol..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading && <p>Loading watchlist...</p>}
      {isError && <p className="error">Failed to load watchlist: {(error as Error).message}</p>}

      {data && (
        <table>
          <thead>
            <tr>
              <th className="sortable" onClick={() => toggleSort('symbol')}>
                Symbol
              </th>
              <th className="sortable" onClick={() => toggleSort('close')}>
                Close
              </th>
              <th className="sortable" onClick={() => toggleSort('rsi')}>
                RSI
              </th>
              <th className="sortable" onClick={() => toggleSort('macdHist')}>
                MACD Hist
              </th>
              <th className="sortable" onClick={() => toggleSort('vwap')}>
                VWAP
              </th>
              <th>As of</th>
            </tr>
          </thead>
          <tbody>
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
      )}
      {rows.length > 200 && (
        <p className="subtitle">Showing first 200 of {rows.length} matching tickers.</p>
      )}
    </div>
  )
}
