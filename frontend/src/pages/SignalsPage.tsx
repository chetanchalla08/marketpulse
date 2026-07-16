import { useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { fetchSignals } from '../api/client'

const RULE_NAMES = ['oversold_reclaim_vwap', 'macd_bullish_crossover', 'overbought_warning']
const PAGE_SIZE = 20

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

  return (
    <div>
      <h1>Signals</h1>
      <p className="subtitle">Rule triggers from the live S&amp;P 500 screener, most recent first.</p>

      <div className="filters">
        <input
          type="text"
          placeholder="Filter by symbol (e.g. AAPL)"
          value={symbol}
          onChange={(e) => {
            setSymbol(e.target.value.toUpperCase())
            setPage(0)
          }}
        />
        <select
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

      {isLoading && <p>Loading signals...</p>}
      {isError && <p className="error">Failed to load signals: {(error as Error).message}</p>}

      {data && (
        <>
          <table>
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
              {data.content.map((s) => (
                <tr key={s.id}>
                  <td>{new Date(s.timestamp).toLocaleString()}</td>
                  <td className="symbol">{s.symbol}</td>
                  <td>{s.ruleName}</td>
                  <td>${s.closeAtSignal.toFixed(2)}</td>
                  <td className="details">{s.details}</td>
                </tr>
              ))}
              {data.content.length === 0 && (
                <tr>
                  <td colSpan={5}>No signals match these filters.</td>
                </tr>
              )}
            </tbody>
          </table>

          <div className="pagination">
            <button disabled={data.first} onClick={() => setPage((p) => p - 1)}>
              Previous
            </button>
            <span>
              Page {data.number + 1} of {Math.max(data.totalPages, 1)} ({data.totalElements} total)
            </span>
            <button disabled={data.last} onClick={() => setPage((p) => p + 1)}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
