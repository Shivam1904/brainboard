import NewDashboard from './components/NewDashboard'

function App() {

  return (
    <div className="h-auto w-screen bg-background flex flex-col">
      <main className="flex-1 overflow-hidden h-screen">
        <NewDashboard />
      </main>
    </div>
  )
}

export default App
