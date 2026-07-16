import { useMemo, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { fetchSignals } from '../api/client'
import { ruleBadgeClass } from '../lib/ruleBadge'

const RULE_NAMES = ['oversold_reclaim_vwap', 'macd_bullish_crossover', 'overbought_warning']
const PAGE_SIZE = 20

function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 8 }).map((_, i) => (
        <tr key={i} className="border-t border-border">
          {Array.from({ length: 5 }).map((__, j) => (
            <td key={j} className="px-4 py-3">
              <div className="skeleton w-24" />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}

export function SignalsPage() {
  const [symbol, setSymbol] = useState('')
  const [ruleName, setRuleName] = useState('')
  const [page, setPage] = useState(0)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['signals', symbol, ruleName, page],
    queryFn: () =>
      fetchSignals({
        symbol: symbol.trim() || undefined,
        ruleName: ruleName || undefined,
        page,
        size: PAGE_SIZE,
      }),
    placeholderData: keepPreviousData,
  })

  const stats = useMemo(() => {
    if (!data) return null
    const distinctSymbols = new Set(data.content.map((s) => s.symbol)).size
    const mostRecent = data.content[0]?.timestamp
    return { distinctSymbols, mostRecent }
  }, [data])

  return (
    <div>
      <h1 className="page-title">Signals</h1>
      <p className="page-subtitle">Rule triggers from the live S&amp;P 500 screener, most recent first.</p>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Matching signals</div>
          <div className="stat-value">{data?.totalElements ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Symbols on this page</div>
          <div className="stat-value">{stats?.distinctSymbols ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Most recent</div>
          <div className="stat-value text-base">
            {stats?.mostRecent ? new Date(stats.mostRecent).toLocaleString() : '—'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Page</div>
          <div className="stat-value">{(data?.number ?? 0) + 1} / {Math.max(data?.totalPages ?? 1, 1)}</div>
        </div>
      </div>

      <div className="filters">
        <input
          type="text"
          className="input-field"
          placeholder="Filter by symbol (e.g. AAPL)"
          value={symbol}
          onChange={(e) => {
            setSymbol(e.target.value.toUpperCase())
            setPage(0)
          }}
        />
        <select
          className="select-field"
          value={ruleName}
          onChange={(e) => {
            setRuleName(e.target.value)
            setPage(0)
          }}
        >
          <option value="">All rules</option>
          {RULE_NAMES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {isError && <p className="error-text mb-4">Failed to load signals: {(error as Error).message}</p>}

      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Symbol</th>
              <th>Rule</th>
              <th>Close</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <SkeletonRows />}
            {data?.content.map((s) => (
              <tr key={s.id}>
                <td>{new Date(s.timestamp).toLocaleString()}</td>
                <td className="symbol">{s.symbol}</td>
                <td>
                  <span className={`badge ${ruleBadgeClass(s.ruleName)}`}>{s.ruleName}</span>
                </td>
                <td>${s.closeAtSignal.toFixed(2)}</td>
                <td className="details-cell">{s.details}</td>
              </tr>
            ))}
            {data?.content.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-text">
                  No signals match these filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {data && (
        <div className="pagination">
          <button className="btn-page" disabled={data.first} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <span>
            Page {data.number + 1} of {Math.max(data.totalPages, 1)} ({data.totalElements} total)
          </span>
          <button className="btn-page" disabled={data.last} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
        </div>
      )}
    </div>
  )
}
