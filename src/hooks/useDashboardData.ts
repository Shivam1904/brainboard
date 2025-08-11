import { useEffect, useRef, useMemo } from 'react'
import { useDashboardStore, useAllWidgets, useTodayWidgets } from '../stores/dashboardStore'

/**
 * Simple hook to load dashboard data with proper memoization
 */
export const useDashboardData = (targetDate: string) => {
  const lastLoadedDate = useRef<string | null>(null)
  const store = useDashboardStore()
  
  useEffect(() => {
    store.loadData(targetDate)
  }, [targetDate])

  // Memoize the return object to prevent unnecessary re-renders
  return useMemo(() => ({
    allWidgets: store.allWidgets,
    todayWidgets: store.todayWidgets,
    isLoading: store.isLoading,
    error: store.error
  }), [store.allWidgets, store.todayWidgets, store.isLoading, store.error])
}

/**
 * Hook for accessing only today's widgets data
 */
export const useTodayWidgetsData = (targetDate: string) => {
  const lastLoadedDate = useRef<string | null>(null)
  const store = useDashboardStore()
  
  return useMemo(() => ({
    todayWidgets: store.todayWidgets,
    isLoading: store.isLoading,
    error: store.error
  }), [store.todayWidgets, store.isLoading, store.error])
}

/**
 * Hook for accessing only all widgets data
 */
export const useAllWidgetsData = () => {
  const hasLoaded = useRef(false)
  const store = useDashboardStore()
  
  return useMemo(() => ({
    allWidgets: store.allWidgets,
    isLoading: store.isLoading,
    error: store.error
  }), [store.allWidgets, store.isLoading, store.error])
} 