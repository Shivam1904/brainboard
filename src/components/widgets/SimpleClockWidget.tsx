import { useEffect, useMemo, useState } from 'react'
import BaseWidget from './BaseWidget'
import { DailyWidget } from '../../services/api'

interface SimpleClockWidgetProps {
  widget: DailyWidget
  onRemove: () => void
  targetDate: string
}

type ClockMode = 'analog' | 'digital'
type ClockTheme = 'day' | 'night'

const pad = (num: number) => num.toString().padStart(2, '0')

const SimpleClockWidget = ({ widget, onRemove, targetDate }: SimpleClockWidgetProps) => {
  // Check if targetDate is today
  const isToday = useMemo(() => {
    const today = new Date()
    const target = new Date(targetDate + 'T00:00:00') // Parse yyyy-mm-dd format
    return today.getFullYear() === target.getFullYear() &&
      today.getMonth() === target.getMonth() &&
      today.getDate() === target.getDate()
  }, [targetDate])

  // If not today, show midnight, otherwise show current time
  const [now, setNow] = useState<Date>(() => {
    if (isToday) {
      return new Date()
    } else {
      const target = new Date(targetDate)
      target.setHours(0, 0, 0, 0) // Set to midnight
      return target
    }
  })

  const [mode, setMode] = useState<ClockMode>('analog')
  const inferredTheme: ClockTheme = useMemo(() => {
    const hour = now.getHours()
    return hour >= 6 && hour < 18 ? 'day' : 'night'
  }, [now])
  const [theme, setTheme] = useState<ClockTheme>(inferredTheme)

  useEffect(() => {
    // Only update time if it's today
    if (isToday) {
      const timer = setInterval(() => setNow(new Date()), 1000)
      return () => clearInterval(timer)
    }
  }, [isToday])

  // Keep theme in sync when user hasn't toggled manually (only on mount)
  useEffect(() => {
    setTheme(inferredTheme)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const hours = now.getHours()
  const minutes = now.getMinutes()
  const seconds = now.getSeconds()

  const hourHandDeg = ((hours % 12) + minutes / 60) * 30 // 360 / 12
  const minuteHandDeg = (minutes + seconds / 60) * 6 // 360 / 60
  const secondHandDeg = seconds * 6

  const isDay = theme === 'day'



  const ringClasses = isDay ? 'border-yellow-300' : 'border-indigo-500/60'
  const tickClasses = isDay ? 'bg-yellow-400/80' : 'bg-indigo-300/70'
  const centerDotClasses = isDay ? 'bg-yellow-500' : 'bg-indigo-300'
  const hourHandColor = isDay ? 'bg-yellow-700' : 'bg-indigo-200'
  const minuteHandColor = isDay ? 'bg-yellow-600' : 'bg-indigo-300'
  const secondHandColor = isDay ? 'bg-rose-500' : 'bg-pink-400'

  const ampm = hours >= 12 ? 'PM' : 'AM'
  const displayHours12 = hours % 12 === 0 ? 12 : hours % 12

  return (
    <BaseWidget title={widget.title || 'Simple Clock'} icon={isDay ? '🌞' : '🌙'} onRemove={onRemove}>
      <div className={`h-full w-full p-3 `}>
        <div className="relative items-center justify-between">
          <div className="flex absolute top-0 right-0 left-0 justify-center pt-12 z-10 opacity-50">
            <button
              onClick={() => setMode('analog')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${mode === 'analog'
                  ? 'bg-gradient-to-r from-yellow-500 to-yellow-300 opacity-80'
                  : 'bg-secondary '
                }`}
            >
              Analog
            </button>
            <button
              onClick={() => setMode('digital')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${mode === 'digital'
                  ? 'bg-gradient-to-r from-indigo-500 to-indigo-300 opacity-80'
                  : 'bg-secondary '
                }`}
            >
              Digital
            </button>
          </div>

          {false && (<div className="flex gap-1">
            <button
              onClick={() => setTheme('day')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${theme === 'day'
                  ? 'bg-amber-500 text-white'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
              title="Day theme"
            >
              🌞 Day
            </button>
            <button
              onClick={() => setTheme('night')}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${theme === 'night'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
              title="Night theme"
            >
              🌙 Night
            </button>
          </div>)}
        </div>

        {mode === 'analog' ? (
          <div className="h-full flex items-center justify-center">
            <div className={`relative aspect-square w-full max-w-[240px] rounded-full border-4 ${ringClasses} shadow-inner shadow-black/10`}>
              {/* hour ticks */}
              {[...Array(12)].map((_, i) => (
                <div
                  key={i}
                  className={`absolute left-1/2 top-1/2 h-[2px] w-[10%] ${tickClasses}`}
                  style={{
                    transformOrigin: '0% 50%',
                    transform: `rotate(${i * 30}deg) translateX(45%)`,
                    opacity: 0.9
                  }}
                />
              ))}

              {/* hour hand */}
              <div
                className={`absolute left-1/2 top-1/2 ${hourHandColor} rounded-full`}
                style={{
                  width: '4px',
                  height: '28%',
                  transform: `translate(-50%, -100%) rotate(${hourHandDeg}deg)`,
                  transformOrigin: '50% 100%'
                }}
              />

              {/* minute hand */}
              <div
                className={`absolute left-1/2 top-1/2 ${minuteHandColor} rounded-full`}
                style={{
                  width: '3px',
                  height: '38%',
                  transform: `translate(-50%, -100%) rotate(${minuteHandDeg}deg)`,
                  transformOrigin: '50% 100%'
                }}
              />

              {/* second hand */}
              <div
                className={`absolute left-1/2 top-1/2 ${secondHandColor} rounded-full`}
                style={{
                  width: '2px',
                  height: '42%',
                  transform: `translate(-50%, -100%) rotate(${secondHandDeg}deg)`,
                  transformOrigin: '50% 100%'
                }}
              />

              {/* center cap */}
              <div className={`absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full ${centerDotClasses}`} />
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center pt-12">
            <div className={`rounded-2xl px-4 py-3 text-4xl font-semibold tracking-widest shadow-sm ${isDay ? 'bg-white/70 text-gray-800' : 'bg-slate-800/60 text-slate-100'
              }`}>
              {pad(displayHours12)}:{pad(minutes)}:{pad(seconds)} <span className="text-base align-middle opacity-70">{ampm}</span>
            </div>
            <div className="mt-2 text-xs opacity-75">
              {now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </div>
          </div>
        )}
      </div>
    </BaseWidget>
  )
}

export default SimpleClockWidget

