import { useState } from 'react'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-foreground">
            🧠 Brainboard
          </h1>
          <p className="text-sm text-muted-foreground">
            AI-Powered Dashboard with Smart Widgets
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-6">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
