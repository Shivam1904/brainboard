import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { Responsive, WidthProvider } from 'react-grid-layout'
import HabitTrackerWidget from './widgets/HabitTrackerWidget';
import YearCalendarWidget from './widgets/YearCalendarWidget';
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import BaseWidget from './widgets/BaseWidget'
import CalendarWidget from './widgets/CalendarWidget'
import AdvancedSingleTaskWidget from './widgets/AdvancedSingleTaskWidget'
import PillarGraphsWidget from './widgets/PillarGraphsWidget'
import { DailyWidget } from '../services/api';
import type { Layout } from 'react-grid-layout';
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties } from '../config/grid'
import { useDashboardActions } from '../stores/dashboardStore'
import { handleRemoveWidgetUtil } from '../utils/widgetUtils'

const ResponsiveGridLayout = WidthProvider(Responsive)

interface DashboardProps {
  date: string;
  allWidgets: any[]; // Using any[] to match the structure or Import Types
  todayWidgets: DailyWidget[];
}

const Dashboard = ({ date, allWidgets: allWidgetsData, todayWidgets: todayWidgetsData }: DashboardProps) => {
  // Centralized layout: track per-widget size overrides (e.g., dynamic height changes)
  const [sizeOverrides, setSizeOverrides] = useState<Record<string, { w?: number; h?: number }>>({})

  // Track last height values to prevent unnecessary updates
  const lastHeightValues = useRef<Record<string, number>>({})

  // Get actions from store
  const { removeWidgetFromToday, updateDashboardWidgetLayout } = useDashboardActions()

  // Apply grid CSS properties on component mount
  useEffect(() => {
    const cssProperties = getGridCSSProperties()
    Object.entries(cssProperties).forEach(([property, value]) => {
      document.documentElement.style.setProperty(property, value)
    })
  }, [])

  // Helper to build a minimal placeholder layout to satisfy type; actual layout is centralized
  const buildPlaceholderLayout = (id: string) => ({ i: id, x: 0, y: 0, w: 1, h: 1 })

  // Get saved w/h from dashboard widget's widget_config.layout (persisted from size overrides)
  const getSavedLayout = useCallback(
    (widget: DailyWidget): { w?: number; h?: number } | undefined => {
      if (!widget.widget_id || widget.widget_id === 'task-list-combined') return undefined
      const dashboardWidget = allWidgetsData.find((w) => w.id === widget.widget_id)
      return dashboardWidget?.widget_config?.layout as { w?: number; h?: number } | undefined
    },
    [allWidgetsData]
  )

  // Process widgets for UI display
  const processWidgetsForUI = useMemo(() => {
    const trackerWidgetTypes = ['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker'];
    const viewWidgetTypes = ['allSchedules', 'aiChat', 'moodTracker', 'weatherWidget', 'simpleClock', 'notes'];

    const makeWidget = (base: Partial<DailyWidget>, overrides: Partial<DailyWidget> = {}): DailyWidget => ({
      id: base.id || '',
      daily_widget_id: base.daily_widget_id || '',
      widget_id: base.widget_id || '',
      widget_type: base.widget_type || '',
      title: base.title || '',
      description: base.description || '',
      frequency: 'daily',
      importance: 0.5,
      category: 'utilities',
      is_permanent: false,
      priority: 'LOW',
      date: new Date().toISOString().split('T')[0],
      created_at: new Date().toISOString(),
      layout: buildPlaceholderLayout(base.id || ''),
      ...base,
      ...overrides
    });

    const isValidWidget = (w: DailyWidget) =>
      w && w.daily_widget_id && w.widget_id && w.widget_type;

    const hasUpcomingMilestone = (milestones: any[]) => {
      const today = new Date();
      const weekAhead = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
      return milestones.some(m => {
        if (!m?.due_date) return false;
        const date = new Date(m.due_date);
        return date >= today && date <= weekAhead;
      });
    };

    // --- Prepare widget lists ---
    const uiWidgets: DailyWidget[] = [];
    const advancedWidgets: DailyWidget[] = [];
    const regularWidgets: DailyWidget[] = [];
    const trackerWidgets: DailyWidget[] = [];
    const webSearchWidgets: DailyWidget[] = [];

    // Process today's widgets
    const validWidgets = todayWidgetsData.filter(isValidWidget);

    validWidgets.forEach(widget => {
      if (viewWidgetTypes.includes(widget.widget_type)) return;

      const cfg = widget.widget_config || {};
      const milestones = Array.isArray(cfg.milestones) ? cfg.milestones : (Array.isArray(cfg.milestone_list) ? cfg.milestone_list : []);

      // Check for presence of data to determine if it's an advanced widget
      // The boolean flags might be missing/undefined in some API responses
      const hasTracker = !!cfg.include_tracker_details || !!cfg.value_type;
      const hasAlarm = !!cfg.include_alarm_details || (Array.isArray(cfg.alarm_times) && cfg.alarm_times.length > 0);
      const hasProgress = !!cfg.include_progress_details || (milestones.length > 0 && hasUpcomingMilestone(milestones));

      const advCondition = hasTracker || hasAlarm || hasProgress;

      if (trackerWidgetTypes.includes(widget.widget_type)) {
        trackerWidgets.push(makeWidget(widget, {
          id: `tracker-${widget.daily_widget_id}`,
          title: `Tracker: ${widget.title}`,
          reasoning: 'Tracker widget'
        }));
      } else if (advCondition) {
        advancedWidgets.push(makeWidget(widget, {
          id: `advanced-${widget.daily_widget_id}`,
          widget_type: 'advancedsingletask',
          title: `Advanced: ${widget.title}`,
          reasoning: 'Advanced single task widget with tracker/alarm/progress'
        }));
      } else {
        regularWidgets.push(widget);
      }

      if (cfg.include_websearch_details) {
        const config = getWidgetConfig('websearch');
        if (config) {
          webSearchWidgets.push(makeWidget(widget, {
            id: `websearch-${widget.daily_widget_id}`,
            widget_type: 'websearch',
            title: `Web Search: ${widget.title}`,
            category: 'information',
            description: `Web search for ${widget.title}`,
            reasoning: 'Web search widget for task'
          }));
        }
      }
    });

    // Assemble final list
    uiWidgets.push(...advancedWidgets);

    if (regularWidgets.length) {
      uiWidgets.push(makeWidget({
        id: 'task-list-combined',
        daily_widget_id: 'task-list-combined',
        widget_id: 'task-list-combined',
        widget_type: 'todo-task',
        title: 'Task List',
        category: 'productivity',
        description: 'Combined task list',
        widget_config: {
          combined_tasks: regularWidgets.map(w => ({
            id: w.daily_widget_id,
            widget_id: w.widget_id,
            title: w.title,
            description: w.description,
            importance: w.importance,
            category: w.category,
            widget_config: w.widget_config
          }))
        }
      }));
    }

    uiWidgets.push(...trackerWidgets, ...webSearchWidgets);

    return uiWidgets;
  }, [allWidgetsData, todayWidgetsData]);

  // Compute initial row-wise positions so items are spread across the row before wrapping
  const computeRowWiseLayout = (
    items: Array<{ id: string; w: number; h: number }>
  ) => {
    const cols = GRID_CONFIG.cols.lg
    let currentX = 0
    let currentY = 0
    let currentRowHeight = 0
    const positions = new Map<string, { x: number; y: number }>()

    for (const item of items) {
      const width = Math.min(item.w, cols)
      if (currentX + width > cols) {
        currentX = 0
        currentY += currentRowHeight
        currentRowHeight = 0
      }
      positions.set(item.id, { x: currentX, y: currentY })
      currentX += width
      currentRowHeight = Math.max(currentRowHeight, item.h)
    }

    return positions
  }
  const [computedPositions, setComputedPositions] = useState<Map<string, { x: number; y: number }>>(new Map())

  // Memoize the computed positions
  useEffect(() => {
    const layoutItems = processWidgetsForUI.map((w) => {
      const config = getWidgetConfig(w.widget_type)
      const override = sizeOverrides[w.daily_widget_id] || sizeOverrides[String(w.id)] || {}
      const savedLayout = getSavedLayout(w)
      const width = override.w ?? savedLayout?.w ?? (config?.defaultSize?.w ?? 12)
      const height = override.h ?? savedLayout?.h ?? (config?.defaultSize?.h ?? 8)
      return { id: String(w.id), w: width, h: height }
    })
    const positions = computeRowWiseLayout(layoutItems)
    setComputedPositions(positions)
  }, [processWidgetsForUI, sizeOverrides, getSavedLayout])

  const onHeightChange = useCallback((dailyWidgetId: string, newHeight: number) => {
    if (lastHeightValues.current[dailyWidgetId] !== newHeight) {
      lastHeightValues.current[dailyWidgetId] = newHeight
      setSizeOverrides((prev) => ({
        ...prev,
        [dailyWidgetId]: { ...(prev[dailyWidgetId] || {}), h: newHeight },
      }))
    }
  }, [])

  // When user resizes a widget, persist w/h
  const handleLayoutChange = useCallback(
    (newLayout: Layout[]) => {
      processWidgetsForUI.forEach((widget) => {
        const item = newLayout.find((l) => l.i === String(widget.id))
        if (!item || !widget.widget_id || widget.widget_id === 'task-list-combined') return
        const config = getWidgetConfig(widget.widget_type)
        const override = sizeOverrides[widget.daily_widget_id] || sizeOverrides[String(widget.id)] || {}
        const savedLayout = getSavedLayout(widget)
        const displayedW = override.w ?? savedLayout?.w ?? config?.defaultSize?.w ?? 12
        const displayedH = override.h ?? savedLayout?.h ?? config?.defaultSize?.h ?? 8
        if (item.w !== displayedW || item.h !== displayedH) {
          setSizeOverrides((prev) => ({
            ...prev,
            [widget.daily_widget_id]: { w: item.w, h: item.h },
            [String(widget.id)]: { w: item.w, h: item.h },
          }))
          updateDashboardWidgetLayout(widget.widget_id, { w: item.w, h: item.h })
        }
      })
    },
    [processWidgetsForUI, sizeOverrides, getSavedLayout, updateDashboardWidgetLayout]
  )

  const handleRemoveWidget = useCallback(async (dailyWidgetId: string) => {
    const widget = processWidgetsForUI.find(w => w.daily_widget_id === dailyWidgetId)
    const widgetType = widget?.widget_type || 'widget'
    const widgetTitle = widget?.title || ''

    if (widget?.title?.startsWith('Advanced: ')) {
      // Advanced specific logic kept partly here to access local processWidgetsForUI state for associated websearch removal if needed
      // Or we can move it all if we pass the list.
      // Let's use the util for the simpler parts and specialized logic.

      // Actually, the util handles the core logic. 
      // For the associated websearch removal, it requires finding the websearch widget ID.

      try {
        await removeWidgetFromToday(dailyWidgetId, date);

        // Logic for removing associated web search
        // In original code: const webSearchWidgetId = `websearch-${widget.id}`;
        // But widget.id in processed UI was `advanced-${real_id}`.
        // dailyWidgetId passed here is real `daily_widget_id`.
        // The websearch widget in UI list would have id `websearch-${dailyWidgetId}` approx?
        // Original: const webSearchWidgetId = `websearch-${widget.id}`; 
        // Wait, widget found via find(daily_widget_id) has `id` overridden to `advanced-...` (line 125).
        // So websearch ID constructed is `websearch-advanced-...` ??
        // Line 138: id: `websearch-${widget.daily_widget_id}`.
        // Original code line 272: `websearch-${widget.id}`. If widget.id is `advanced-...`, this is `websearch-advanced-...`.
        // BUT checks `processWidgetsForUI.find(w => w.daily_widget_id === webSearchWidgetId)`.
        // `daily_widget_id` for websearch widget (line 138) is `websearch-${widget.daily_widget_id}`.
        // So it seems it constructs an ID to find the UI element?

        // Let's simplify. If we just blindly try to remove the websearch widget that matches the task...
        // The `removeWidgetFromToday` needs a DB ID.
        // The websearch widget "Activity" in DB has its own daily_widget_id.
        // The UI construction fakes a daily_widget_id for websearch: `websearch-${widget.daily_widget_id}` (line 138).
        // This fake ID is NOT in the DB. `removeWidgetFromToday` with a fake ID will fail or do nothing on backend?
        // Line 138: `id: websearch-${widget.daily_widget_id}, daily_widget_id: websearch-${widget.daily_widget_id}`...
        // If these are not real DB items, how did `handleRemoveWidget` work before?
        // It calls `removeWidgetFromToday(webSearchWidgetId, date)`.
        // Does the backend handle 'websearch-...' IDs? Or is `removeWidgetFromToday` handling it?
        // `removeWidgetFromToday` calls API.

        // If the websearch widget is purely client-side generated (implied by "makeWidget" in "processWidgetsForUI"),
        // then we don't need to call API to remove it? It disappears when the main task is removed (re-render).
        // Yes, line 134 loops validWidgets. If task is removed from DB, validWidgets won't have it, so no websearch generated.
        // So the API call `removeWidgetFromToday(webSearchWidgetId)` in original code might have been redundant or failing silently?
        // UNLESS the websearch widget IS persisted.
        // Line 134: `if (cfg.include_websearch_details)`. This is config on the TASK widget.
        // So removing the task widget removes the config source.
        // So we just need to remove the task widget.

        // I will proceed with just removing the main widget using the util.

      } catch (error) {
        console.error('Failed to remove widget:', error);
        alert('Failed to remove widget.');
      }
      return;
    }

    await handleRemoveWidgetUtil({
      dailyWidgetId,
      widgetType,
      widgetTitle,
      date,
      removeWidgetFromToday
    })

  }, [processWidgetsForUI, removeWidgetFromToday, date])

  const renderWidget = (widget: DailyWidget) => {
    switch (widget.widget_type) {
      case 'websearch':
        return (
          <WebSearchWidget
            targetDate={date}
            widget={widget}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
          />
        );
      case 'todo-task':
        if (widget.widget_config?.combined_tasks) {
          return (
            <TaskListWidget
              targetDate={date}
              onHeightChange={onHeightChange}
              widget={{
                ...widget,
                title: 'Task List',
                description: `Combined task list with ${widget.widget_config.combined_tasks.length} tasks`
              }}
              onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
            />
          );
        }
        break;
      case 'advancedsingletask':
        return (
          <AdvancedSingleTaskWidget
            targetDate={date}
            widget={{
              ...widget,
              title: widget.title.replace('Advanced: ', ''),
              description: widget.description
            }}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
            onHeightChange={onHeightChange}
          />
        );
      case 'yearCalendar':
        return (
          <YearCalendarWidget
            targetDate={date}
            widget={widget}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
          />
        );
      case 'calendar':
        return (
          <CalendarWidget
            targetDate={date}
            widget={widget}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
          />
        );
      case 'habitTracker':
        return (
          <HabitTrackerWidget
            targetDate={date}
            widget={widget}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
          />
        );
      case 'pillarGraphs': // Check if this is the correct type, mostly likely 'pillarGraphs' based on component map but previously was 'pillarsGraph' in old file
      case 'pillarsGraph':
        return (
          <PillarGraphsWidget
            targetDate={date}
            widget={widget}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
          />
        );
      default:
        const config = getWidgetConfig(widget.widget_type);
        return (
          <BaseWidget
            title={config?.title || widget.widget_type}
            icon={config?.icon}
            onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
          >
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <div className="text-4xl mb-2">{config?.icon || '🚧'}</div>
              <h3 className="font-medium mb-2">{config?.title || widget.widget_type}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {config?.description || 'This widget is coming soon!'}
              </p>
              <div className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                Under Development
              </div>
            </div>
          </BaseWidget>
        )
    }
  }

  // Check for loading/error passed from parent via props if needed, or simply render
  // Since parent handles loading, we just render what we have. 
  // If data is empty but not error, it might be loading, but we don't have that state here anymore.
  // We can treat empty arrays as just empty dashboard.

  return (
    <div className={`flex flex-col h-full w-full bg-transparent overflow-hidden`}>
      <div className="flex-1 overflow-auto">
        <ResponsiveGridLayout
          className={`layout min-h-full`}
          breakpoints={GRID_CONFIG.breakpoints}
          cols={GRID_CONFIG.cols}
          rowHeight={GRID_CONFIG.rowHeight}
          margin={GRID_CONFIG.margin}
          containerPadding={GRID_CONFIG.containerPadding}
          draggableHandle=".widget-drag-handle"
          compactType="vertical"
          onLayoutChange={handleLayoutChange}
        >
          {processWidgetsForUI.map((widget: DailyWidget) => {
            const config = getWidgetConfig(widget.widget_type);
            const override = sizeOverrides[widget.daily_widget_id] || sizeOverrides[String(widget.id)] || {};
            const savedLayout = getSavedLayout(widget);
            const baseW = config?.defaultSize?.w ?? 12;
            const baseH = config?.defaultSize?.h ?? 8;
            const w = override.w ?? savedLayout?.w ?? baseW;
            const h = override.h ?? savedLayout?.h ?? baseH;
            const pos = computedPositions.get(String(widget.id));
            const x = pos?.x ?? 0;
            const y = pos?.y ?? (Infinity as number);
            const dataGrid = { i: String(widget.id), x, y, w, h } as const;
            return (
              <div key={widget.id} className="widget-container" data-grid={dataGrid}>
                {renderWidget(widget)}
              </div>
            );
          })}
        </ResponsiveGridLayout>
      </div>
    </div>
  )
}

export default Dashboard
