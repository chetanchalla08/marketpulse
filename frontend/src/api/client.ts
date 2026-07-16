import type { BacktestResult, IndicatorSnapshot, Page, Signal } from './types'

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export function fetchSignals(params: {
  symbol?: string
  ruleName?: string
  page: number
  size: number
}): Promise<Page<Signal>> {
  const qs = new URLSearchParams()
  if (params.symbol) qs.set('symbol', params.symbol)
  if (params.ruleName) qs.set('ruleName', params.ruleName)
  qs.set('page', String(params.page))
  qs.set('size', String(params.size))
  return getJson(`/api/signals?${qs.toString()}`)
}

export function fetchLatestIndicators(): Promise<IndicatorSnapshot[]> {
  return getJson('/api/indicators/latest')
}

export function fetchIndicatorHistory(symbol: string, limit = 100): Promise<IndicatorSnapshot[]> {
  return getJson(`/api/indicators/${encodeURIComponent(symbol)}?limit=${limit}`)
}

export function fetchBacktestResults(runAt?: string): Promise<BacktestResult[]> {
  const qs = runAt ? `?runAt=${encodeURIComponent(runAt)}` : ''
  return getJson(`/api/backtest/results${qs}`)
}

export function fetchBacktestRuns(): Promise<string[]> {
  return getJson('/api/backtest/runs')
}
