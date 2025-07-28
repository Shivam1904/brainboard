// import { useState } from 'react' // Unused import
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="h-screen w-screen overflow-hidden bg-background flex flex-col">
      <main className="flex-1 overflow-hidden">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
