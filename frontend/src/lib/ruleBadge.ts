const RULE_BADGE_CLASSES: Record<string, string> = {
  oversold_reclaim_vwap: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  macd_bullish_crossover: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  overbought_warning: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
}

const FALLBACK_BADGE_CLASS = 'bg-accent-bg text-accent'

export function ruleBadgeClass(ruleName: string): string {
  return RULE_BADGE_CLASSES[ruleName] ?? FALLBACK_BADGE_CLASS
}
