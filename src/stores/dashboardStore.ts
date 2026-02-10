import { create } from 'zustand'
import { dashboardService } from '../services/dashboard'
import { DashboardWidget, DailyWidget } from '../services/api'

interface DashboardState {
  // Data
  allWidgets: DashboardWidget[]
  todayWidgets: DailyWidget[]

  // Loading states
  isLoading: boolean
  error: string | null
  lastLoadedDate: string | null

  // Actions
  loadData: (targetDate: string) => Promise<void>
  addWidgetToToday: (widgetId: string, targetDate: string) => Promise<{
    success: boolean;
    message: string;
    daily_widget_id: string;
    widget_id: string;
  }>
  removeWidgetFromToday: (dailyWidgetId: string, targetDate: string) => Promise<void>
  updateWidgetActivity: (dailyWidgetId: string, activityData: Record<string, unknown>) => Promise<void>
  updateDashboardWidgetLayout: (widgetId: string, layout: { w: number; h: number }) => Promise<void>
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  // Initial state
  allWidgets: [],
  todayWidgets: [],
  isLoading: false,
  error: null,
  lastLoadedDate: null,

  // Load data
  loadData: async (targetDate: string) => {
    // Avoid double-loading or re-loading the same date if not needed
    if (get().isLoading || (get().lastLoadedDate === targetDate && get().allWidgets.length > 0)) {
      return
    }

    set({ isLoading: true, error: null })

    try {
      const [allWidgets, todayWidgets] = await Promise.all([
        dashboardService.getAllWidgets(),
        dashboardService.getTodayWidgets(targetDate)
      ])

      set({
        allWidgets,
        todayWidgets,
        isLoading: false,
        lastLoadedDate: targetDate
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load data'
      set({
        error: errorMessage,
        isLoading: false
      })
    }
  },


  // Add widget to today
  addWidgetToToday: async (widgetId: string, targetDate: string) => {
    const result = await dashboardService.addWidgetToToday(widgetId, targetDate)
    // Refresh today's widgets
    set({
      todayWidgets: [...get().todayWidgets, result as unknown as DailyWidget]
    })
    return result
  },

  // Remove widget from today
  removeWidgetFromToday: async (dailyWidgetId: string, targetDate: string) => {
    await dashboardService.removeWidgetFromToday(dailyWidgetId, targetDate)
    // Refresh today's widgets
    set({
      todayWidgets: get().todayWidgets.filter(widget => widget.daily_widget_id !== dailyWidgetId)
    })
  },

  // Update widget activity
  updateWidgetActivity: async (dailyWidgetId: string, activityData: Record<string, unknown>) => {
    await dashboardService.updateActivity(dailyWidgetId, activityData)
    // Refresh today's widgets
    const newActivityData = {
      ...get().todayWidgets.find(widget => widget.daily_widget_id === dailyWidgetId)?.activity_data,
      ...activityData
    }
    set({
      todayWidgets: get().todayWidgets.map(widget => widget.daily_widget_id === dailyWidgetId ? { ...widget, activity_data: newActivityData } : widget)
    })
  },

  // Persist widget size (w, h) to dashboard widget's widget_config.layout
  updateDashboardWidgetLayout: async (widgetId: string, layout: { w: number; h: number }) => {
    const widget = get().allWidgets.find((w) => w.id === widgetId)
    if (!widget) return
    const widgetConfig = { ...(widget.widget_config || {}), layout }
    try {
      await dashboardService.updateWidget(widgetId, { widget_config: widgetConfig })
      set({
        allWidgets: get().allWidgets.map((w) =>
          w.id === widgetId ? { ...w, widget_config: widgetConfig } : w
        )
      })
    } catch (error) {
      console.error('Failed to save widget layout:', error)
    }
  }
}))

// Simple selectors
export const useAllWidgets = () => useDashboardStore(state => state.allWidgets)
export const useTodayWidgets = () => useDashboardStore(state => state.todayWidgets)
export const useIsLoading = () => useDashboardStore(state => state.isLoading)
export const useError = () => useDashboardStore(state => state.error)

// Individual action selectors to prevent unnecessary re-renders
export const useLoadData = () => useDashboardStore(state => state.loadData)
export const useAddWidgetToToday = () => useDashboardStore(state => state.addWidgetToToday)
export const useRemoveWidgetFromToday = () => useDashboardStore(state => state.removeWidgetFromToday)
export const useUpdateWidgetActivity = () => useDashboardStore(state => state.updateWidgetActivity)
export const useUpdateDashboardWidgetLayout = () => useDashboardStore(state => state.updateDashboardWidgetLayout)

// Legacy hook for backward compatibility (but this will cause re-renders)
export const useDashboardActions = () => {
  const store = useDashboardStore()
  return {
    loadData: store.loadData,
    addWidgetToToday: store.addWidgetToToday,
    removeWidgetFromToday: store.removeWidgetFromToday,
    updateWidgetActivity: store.updateWidgetActivity,
    updateDashboardWidgetLayout: store.updateDashboardWidgetLayout
  }
} 