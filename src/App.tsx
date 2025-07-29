import { useState } from 'react'
import Dashboard from './components/Dashboard'
import WidgetDataTest from './components/WidgetDataTest'

function App() {

  return (
    <div className="h-auto w-screen bg-background flex flex-col">
      <main className="flex-1">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
