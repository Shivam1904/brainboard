import { useState } from 'react'
import Dashboard from './components/Dashboard'
import WidgetDataTest from './components/WidgetDataTest'

function App() {
  const [showTest, setShowTest] = useState(false);

  return (
    <div className="h-auto w-screen bg-background flex flex-col">
      <header className="bg-card border-b p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">🧠 Brainboard</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowTest(false)}
              className={`px-3 py-1 rounded text-sm ${
                !showTest 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setShowTest(true)}
              className={`px-3 py-1 rounded text-sm ${
                showTest 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              Test Widget Data
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1">
        {showTest ? <WidgetDataTest /> : <Dashboard />}
      </main>
    </div>
  )
}

export default App
