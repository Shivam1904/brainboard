import { useState } from 'react'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="h-screen w-screen overflow-hidden bg-background flex flex-col">
      <header className="border-b bg-card shrink-0">
        <div className="px-4 py-3">
          <h1 className="text-xl font-bold text-foreground">
            🧠 Brainboard
          </h1>
          <p className="text-xs text-muted-foreground">
            AI-Powered Dashboard with Smart Widgets
          </p>
        </div>
      </header>
      <main className="flex-1 overflow-hidden">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
