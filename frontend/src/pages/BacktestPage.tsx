import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { fetchBacktestResults } from '../api/client'
import { ruleBadgeClass } from '../lib/ruleBadge'

function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 6 }).map((_, i) => (
        <tr key={i} className="border-t border-border">
          {Array.from({ length: 5 }).map((__, j) => (
            <td key={j} className="px-4 py-3">
              <div className="skeleton w-16" />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}

export function BacktestPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['backtest-results'],
    queryFn: () => fetchBacktestResults(),
  })

  const chartData = data?.map((r) => ({
    label: `${r.ruleName} (${r.horizonDays}d)`,
    winRate: Number(r.winRatePct.toFixed(1)),
    avgReturn: Number(r.avgReturnPct.toFixed(2)),
  }))

  const stats = useMemo(() => {
    if (!data || data.length === 0) return null
    const best = data.reduce((a, b) => (b.winRatePct > a.winRatePct ? b : a))
    const avgReturn = data.reduce((sum, r) => sum + r.avgReturnPct, 0) / data.length
    return { combos: data.length, best, avgReturn }
  }, [data])

  return (
    <div>
      <h1 className="page-title">Backtest results</h1>
      <p className="page-subtitle">
        Win rate and average return per rule, evaluated across ~2 years of S&amp;P 500 history.
      </p>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Rule × horizon combos</div>
          <div className="stat-value">{stats?.combos ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Best win rate</div>
          <div className="stat-value">
            {stats ? `${stats.best.winRatePct.toFixed(1)}%` : '—'}
          </div>
        </div>
        <div className="stat-card col-span-2">
          <div className="stat-label">Best performer</div>
          <div className="stat-value flex items-center gap-2 text-base">
            {stats ? (
              <>
                <span className={`badge ${ruleBadgeClass(stats.best.ruleName)}`}>{stats.best.ruleName}</span>
                <span className="text-text">{stats.best.horizonDays}d</span>
              </>
            ) : (
              '—'
            )}
          </div>
        </div>
      </div>

      {isError && <p className="error-text mb-4">Failed to load backtest results: {(error as Error).message}</p>}

      {data && data.length === 0 && (
        <p className="page-subtitle">No backtest runs recorded yet. Run `python run_backtest.py`.</p>
      )}

      {(isLoading || (chartData && chartData.length > 0)) && (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={chartData ?? []} margin={{ top: 8, right: 16, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="label" angle={-35} textAnchor="end" interval={0} height={90} className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{
                  background: 'var(--color-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 8,
                  fontSize: 13,
                }}
              />
              <Legend verticalAlign="top" />
              <Bar dataKey="winRate" name="Win rate %" fill="#8b5cf6" isAnimationActive={false} radius={[4, 4, 0, 0]} />
              <Bar dataKey="avgReturn" name="Avg return %" fill="#10b981" isAnimationActive={false} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {(isLoading || (data && data.length > 0)) && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rule</th>
                <th>Horizon</th>
                <th>Triggers</th>
                <th>Win rate</th>
                <th>Avg return</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && <SkeletonRows />}
              {data?.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className={`badge ${ruleBadgeClass(r.ruleName)}`}>{r.ruleName}</span>
                  </td>
                  <td>{r.horizonDays}d</td>
                  <td>{r.triggerCount}</td>
                  <td>{r.winRatePct.toFixed(1)}%</td>
                  <td className={r.avgReturnPct >= 0 ? 'flag-positive' : 'flag-negative'}>
                    {r.avgReturnPct >= 0 ? '+' : ''}
                    {r.avgReturnPct.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
