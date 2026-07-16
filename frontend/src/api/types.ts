export interface Signal {
  id: number
  symbol: string
  timestamp: string
  ruleName: string
  closeAtSignal: number
  details: string
}

export interface IndicatorSnapshot {
  id: number
  symbol: string
  timestamp: string
  close: number
  volume: number
  rsi: number
  macd: number
  macdSignal: number
  macdHist: number
  vwap: number
}

export interface BacktestResult {
  id: number
  runAt: string
  ruleName: string
  horizonDays: number
  triggerCount: number
  winRatePct: number
  avgReturnPct: number
}

export interface Page<T> {
  content: T[]
  totalElements: number
  totalPages: number
  number: number
  size: number
  first: boolean
  last: boolean
}
