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

  return (
    <div>
      <h1>Backtest results</h1>
      <p className="subtitle">
        Win rate and average return per rule, evaluated across ~2 years of S&amp;P 500 history.
      </p>

      {isLoading && <p>Loading backtest results...</p>}
      {isError && <p className="error">Failed to load backtest results: {(error as Error).message}</p>}

      {data && data.length === 0 && <p>No backtest runs recorded yet. Run `python run_backtest.py`.</p>}

      {chartData && chartData.length > 0 && (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" angle={-35} textAnchor="end" interval={0} height={90} />
              <YAxis />
              <Tooltip />
              <Legend verticalAlign="top" />
              <Bar dataKey="winRate" name="Win rate %" fill="#4f8cff" isAnimationActive={false} />
              <Bar dataKey="avgReturn" name="Avg return %" fill="#37c98f" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {data && data.length > 0 && (
        <table>
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
            {data.map((r) => (
              <tr key={r.id}>
                <td>{r.ruleName}</td>
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
      )}
    </div>
  )
}
