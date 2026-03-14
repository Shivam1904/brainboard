import { useEffect, useMemo } from 'react'
import { useDashboardStore } from '../stores/dashboardStore'

/**
 * Simple hook to load dashboard data with proper memoization
 */
export const useDashboardData = (targetDate: string) => {
  const allWidgets = useDashboardStore(state => state.allWidgets)
  const todayWidgets = useDashboardStore(state => state.todayWidgets)
  const isLoading = useDashboardStore(state => state.isLoading)
  const error = useDashboardStore(state => state.error)
  const loadData = useDashboardStore(state => state.loadData)

  useEffect(() => {
    if (targetDate) {
      loadData(targetDate)
    }
  }, [targetDate, loadData])

  // Memoize the return object to prevent unnecessary re-renders
  return useMemo(() => ({
    allWidgets,
    todayWidgets,
    isLoading,
    error
  }), [allWidgets, todayWidgets, isLoading, error])
}

/**
 * Hook for accessing only today's widgets data
 */
export const useTodayWidgetsData = () => {
  const todayWidgets = useDashboardStore(state => state.todayWidgets)
  const isLoading = useDashboardStore(state => state.isLoading)
  const error = useDashboardStore(state => state.error)

  return useMemo(() => ({
    todayWidgets,
    isLoading,
    error
  }), [todayWidgets, isLoading, error])
}

/**
 * Hook for accessing only all widgets data
 */
export const useAllWidgetsData = () => {
  const allWidgets = useDashboardStore(state => state.allWidgets)
  const isLoading = useDashboardStore(state => state.isLoading)
  const error = useDashboardStore(state => state.error)

  return useMemo(() => ({
    allWidgets,
    isLoading,
    error
  }), [allWidgets, isLoading, error])
}