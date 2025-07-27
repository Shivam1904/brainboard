import { useState, useEffect } from 'react'
import { Plus, Check, Clock, Trash2 } from 'lucide-react'
import BaseWidget from './BaseWidget'

interface Reminder {
  id: string
  text: string
  completed: boolean
  dueDate?: string
  createdAt: string
}

interface ReminderWidgetProps {
  onRemove: () => void
}

const ReminderWidget = ({ onRemove }: ReminderWidgetProps) => {
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [newReminderText, setNewReminderText] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Load reminders from API
  useEffect(() => {
    loadReminders()
  }, [])

  const loadReminders = async () => {
    setIsLoading(true)
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/reminders')
      // const data = await response.json()
      // setReminders(data)
      
      // Mock data for now
      setReminders([
        {
          id: '1',
          text: 'Review project proposal',
          completed: false,
          dueDate: '2025-07-27',
          createdAt: '2025-07-26'
        },
        {
          id: '2',
          text: 'Call dentist for appointment',
          completed: true,
          createdAt: '2025-07-26'
        }
      ])
    } catch (error) {
      console.error('Failed to load reminders:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const addReminder = async () => {
    if (!newReminderText.trim()) return

    const newReminder: Reminder = {
      id: Date.now().toString(),
      text: newReminderText,
      completed: false,
      createdAt: new Date().toISOString()
    }

    try {
      // TODO: API call to create reminder
      setReminders(prev => [...prev, newReminder])
      setNewReminderText('')
    } catch (error) {
      console.error('Failed to add reminder:', error)
    }
  }

  const toggleReminder = async (id: string) => {
    try {
      // TODO: API call to update reminder
      setReminders(prev =>
        prev.map(reminder =>
          reminder.id === id
            ? { ...reminder, completed: !reminder.completed }
            : reminder
        )
      )
    } catch (error) {
      console.error('Failed to update reminder:', error)
    }
  }

  const deleteReminder = async (id: string) => {
    const reminder = reminders.find(r => r.id === id)
    if (reminder && confirm(`Delete reminder: "${reminder.text}"?`)) {
      try {
        // TODO: API call to delete reminder
        setReminders(prev => prev.filter(reminder => reminder.id !== id))
      } catch (error) {
        console.error('Failed to delete reminder:', error)
      }
    }
  }

  return (
    <BaseWidget
      title="Reminders"
      icon="📝"
      onRemove={onRemove}
    >
      <div className="h-full flex flex-col">
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={newReminderText}
            onChange={(e) => setNewReminderText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addReminder()}
            placeholder="Add a reminder..."
            className="flex-1 px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            onClick={addReminder}
            className="px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            <Plus size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2">
          {isLoading ? (
            <div className="text-center text-muted-foreground py-4">
              Loading reminders...
            </div>
          ) : reminders.length === 0 ? (
            <div className="text-center text-muted-foreground py-4">
              No reminders yet. Add one above!
            </div>
          ) : (
            reminders.map((reminder) => (
              <div
                key={reminder.id}
                className={`flex items-center gap-3 p-2 border rounded-md ${
                  reminder.completed ? 'bg-muted' : 'bg-background'
                }`}
              >
                <button
                  onClick={() => toggleReminder(reminder.id)}
                  className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center ${
                    reminder.completed
                      ? 'bg-primary border-primary text-primary-foreground'
                      : 'border-muted-foreground hover:border-primary'
                  }`}
                >
                  {reminder.completed && <Check size={12} />}
                </button>
                
                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm ${
                      reminder.completed
                        ? 'line-through text-muted-foreground'
                        : 'text-foreground'
                    }`}
                  >
                    {reminder.text}
                  </p>
                  {reminder.dueDate && (
                    <div className="flex items-center gap-1 mt-1">
                      <Clock size={12} className="text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">
                        Due {new Date(reminder.dueDate).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
                
                                <button
                  onClick={() => {
                    deleteReminder(reminder.id)
                  }}
                  className="flex-shrink-0 text-muted-foreground hover:text-destructive transition-colors p-1 rounded hover:bg-destructive/10"
                  title="Delete reminder"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </BaseWidget>
  )
}

export default ReminderWidget
