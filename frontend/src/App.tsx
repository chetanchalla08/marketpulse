import { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import { SignalsPage } from './pages/SignalsPage'
import { ScreenerPage } from './pages/ScreenerPage'
import { BacktestPage } from './pages/BacktestPage'
import './App.css'

function useDarkMode() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'))

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return [dark, setDark] as const
}

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-4 w-4">
      <circle cx="12" cy="12" r="4" />
      <path
        strokeLinecap="round"
        d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
      />
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
      <path d="M20.354 15.354A9 9 0 0 1 8.646 3.646 9.003 9.003 0 1 0 20.354 15.354Z" />
    </svg>
  )
}

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors ${
    isActive ? 'bg-accent-bg text-accent' : 'text-text hover:bg-surface hover:text-text-h'
  }`

function App() {
  const [dark, setDark] = useDarkMode()

  return (
    <div className="flex min-h-svh flex-col bg-bg text-text">
      <header className="sticky top-0 z-10 flex items-center gap-8 border-b border-border bg-bg/85 px-6 py-3 backdrop-blur">
        <span className="flex items-center gap-2 text-[15px] font-semibold tracking-tight text-text-h">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent" />
          MarketPulse
        </span>
        <nav className="flex gap-1">
          <NavLink to="/" end className={navLinkClass}>
            Signals
          </NavLink>
          <NavLink to="/screener" className={navLinkClass}>
            Screener
          </NavLink>
          <NavLink to="/backtest" className={navLinkClass}>
            Backtest
          </NavLink>
        </nav>
        <button
          type="button"
          onClick={() => setDark((d) => !d)}
          aria-label="Toggle dark mode"
          className="ml-auto flex h-8 w-8 items-center justify-center rounded-full border border-border text-text transition-colors hover:border-accent-border hover:text-accent"
        >
          {dark ? <SunIcon /> : <MoonIcon />}
        </button>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        <Routes>
          <Route path="/" element={<SignalsPage />} />
          <Route path="/screener" element={<ScreenerPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
