import { NavLink, Route, Routes } from 'react-router-dom'
import { SignalsPage } from './pages/SignalsPage'
import { ScreenerPage } from './pages/ScreenerPage'
import { BacktestPage } from './pages/BacktestPage'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <span className="brand">MarketPulse</span>
        <nav>
          <NavLink to="/" end>
            Signals
          </NavLink>
          <NavLink to="/screener">Screener</NavLink>
          <NavLink to="/backtest">Backtest</NavLink>
        </nav>
      </header>

      <main className="app-main">
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
