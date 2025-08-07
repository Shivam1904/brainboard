import { useState, useEffect } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import WebSearchWidget from './widgets/WebSearchWidget';
import TaskListWidget from './widgets/TaskListWidget'
import SingleItemTrackerWidget from './widgets/SingleItemTrackerWidget'
import AlarmWidget from './widgets/AlarmWidget'
import BaseWidget from './widgets/BaseWidget'
import CalendarWidget from './widgets/CalendarWidget'
import AddWidgetButton from './AddWidgetButton'
import { getWidgetConfig } from '../config/widgets'
import { GRID_CONFIG, getGridCSSProperties, findEmptyPosition } from '../config/grid'
import { dashboardService } from '../services/dashboard'
import { getDummyTodayWidgets } from '../data/widgetDummyData'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'
import HabitListWidget from './widgets/HabitListWidget';
import EventTrackerWidget from './widgets/EventTrackerWidget';
import AiChatWidget from './widgets/AiChatWidget';
import { apiService, DailyWidget } from '../services/api';
import { ApiCategory, ApiFrequency, ApiWidgetType } from '@/types/widgets';

const ResponsiveGridLayout = WidthProvider(Responsive)


const Dashboard = () => {
  const [showGridLines, setShowGridLines] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  const [widgets, setWidgets] = useState<DailyWidget[]>([])
  const [viewWidgetStates, setViewWidgetStates] = useState<DailyWidget[]>([])
  // Apply grid CSS properties on component mount
  useEffect(() => {
    const cssProperties = getGridCSSProperties()
    Object.entries(cssProperties).forEach(([property, value]) => {
      document.documentElement.style.setProperty(property, value)
    })
  }, [])

  // Find optimal position for a new widget
  const findOptimalPosition = (widgetType: string, existingWidgets: DailyWidget[]): { x: number; y: number } => {
    const config = getWidgetConfig(widgetType);
    if (!config) return { x: 0, y: 0 };

    // Try to find empty space using the existing function
    const emptyPosition = findEmptyPosition({
      widgetId: widgetType,
      widgets: existingWidgets,
      getWidgetConfig,
      gridCols: GRID_CONFIG.cols.lg,
      maxRows: 100
    });

    if (emptyPosition) {
      return emptyPosition;
    }

    // Fallback: simple horizontal placement with wrapping
    let currentX = 0;
    let currentY = 0;
    const maxX = GRID_CONFIG.cols.lg - config.defaultSize.w;

    // Find the rightmost widget to start from
    if (existingWidgets.length > 0) {
      const rightmostWidget = existingWidgets.reduce((rightmost, widget) => {
        return widget.layout.x + widget.layout.w > rightmost.layout.x + rightmost.layout.w ? widget : rightmost;
      });
      currentX = rightmostWidget.layout.x + rightmostWidget.layout.w;
      currentY = rightmostWidget.layout.y;
    }

    // If we can't fit horizontally, move to next row
    if (currentX + config.defaultSize.w > maxX) {
      currentX = 0;
      currentY += 2; // Add some spacing between rows
    }

    return { x: currentX, y: currentY };
  };

  // Fetch all widgets and today's widgets
  const fetchTodayWidgets = async () => {
    try {
      setDashboardLoading(true)
      setDashboardError(null)
      
      let allWidgetsData: any[] = [];
      let todayWidgetsData: DailyWidget[] = [];
      try {
        // Fetch all widgets first
        allWidgetsData = await dashboardService.getAllWidgets();
        console.log('Successfully fetched all widgets from API:', allWidgetsData);
        
        // Fetch today's widgets
        todayWidgetsData = await dashboardService.getTodayWidgets();
        console.log('Successfully fetched today\'s widgets from API:', todayWidgetsData);
      } catch (apiError) {
        console.warn('API call failed, falling back to dummy data:', apiError);
      }
      
      // Convert widgets to UI format with proper placement
      const uiWidgets: DailyWidget[] = [];
      
      // Track view widget states for the AddWidgetButton
      
      // First, handle view widgets (allSchedules, aiChat) from all widgets list
      const viewWidgetTypes = ['allSchedules', 'aiChat'];

      const allWidgetsDataViewWidgets = allWidgetsData.filter(w => viewWidgetTypes.includes(w.widget_type));

      setViewWidgetStates(allWidgetsDataViewWidgets);

      viewWidgetTypes.forEach(widgetType => {
        // Find the widget in all widgets list
        const allWidgetsViewWidget = allWidgetsData.find(w => w.widget_type === widgetType);
        const isVisible = allWidgetsViewWidget?.widget_config?.visibility; // Default to true if not set
        if (isVisible) {
          const config = getWidgetConfig(widgetType);
          if (config) {
            const position = findOptimalPosition(widgetType, uiWidgets);
            const viewWidget: DailyWidget = {
              id: `auto-${widgetType}`,
              daily_widget_id: `auto-${widgetType}`,
              widget_id: allWidgetsViewWidget?.id || '',
              widget_type: widgetType,
              title: config.title,
              frequency: 'daily',
              importance: 0.5,
              category: 'utilities',
              description: config.description,
              is_permanent: true,
              priority: 'LOW',
              reasoning: 'View widget managed by visibility setting',
              date: new Date().toISOString().split('T')[0],
              created_at: allWidgetsViewWidget?.created_at || new Date().toISOString(),
              widget_config: allWidgetsViewWidget?.widget_config ,
              layout: {
                i: `auto-${widgetType}`,
                x: position.x,
                y: position.y,
                w: config.defaultSize.w,
                h: config.defaultSize.h,
                minW: config.minSize.w,
                minH: config.minSize.h,
                maxW: config.maxSize.w,
                maxH: config.maxSize.h,
              }
            };
            
            uiWidgets.push(viewWidget);
          }
        }
      });
      
      // Then, handle other widgets from today's widgets list
      todayWidgetsData.forEach((widget: DailyWidget) => {
        // Skip view widgets as they're already handled above
        if (viewWidgetTypes.includes(widget.widget_type)) {
          return;
        }
        
        const config = getWidgetConfig(widget.widget_type);
        const defaultSize = config?.defaultSize || { w: 10, h: 10 };
        
        // Find optimal position for this widget
        const position = findOptimalPosition(widget.widget_type, uiWidgets);
        
        // Convert new API structure to DailyWidget format
        const uiWidget: DailyWidget = {
          ...widget,
          daily_widget_id: widget.id, // Map id to daily_widget_id for UI compatibility
          priority: widget.importance >= 0.7 ? 'HIGH' : 'LOW', // Derive priority from importance
          reasoning: 'Widget from today\'s dashboard', // Default reasoning
          date: new Date().toISOString().split('T')[0], // Current date
          created_at: widget.created_at,
          layout: {
            i: widget.id, // Use widget.id as layout identifier
            x: position.x,
            y: position.y,
            w: defaultSize.w,
            h: defaultSize.h,
            minW: config?.minSize?.w || 4,
            minH: config?.minSize?.h || 4,
            maxW: config?.maxSize?.w || 20,
            maxH: config?.maxSize?.h || 20,
          }
        };
        
        uiWidgets.push(uiWidget);
      });
      
      setWidgets(uiWidgets);
    } catch (err) {
      console.error('Failed to fetch widgets:', err)
      setDashboardError('Failed to load dashboard configuration')
    } finally {
      setDashboardLoading(false)
    }
  }

  // Fetch today's widgets on component mount
  useEffect(() => {
    fetchTodayWidgets()
  }, [])

  // Handle window resize to update constraints
  useEffect(() => {
    const handleResize = () => {
      // Re-constrain all widgets when window is resized
      setWidgets((prev: DailyWidget[]) => 
        prev.map((widget: DailyWidget) => ({
          ...widget,
          layout: constrainLayout(widget.layout)
        }))
      )
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Simple layout constraint function
  const constrainLayout = (layout: Layout): Layout => {
    const gridCols = GRID_CONFIG.cols.lg;
    const maxHeight = 50; // Maximum grid height
    
    return {
      ...layout,
      x: Math.max(0, Math.min(layout.x, gridCols - layout.w)),
      y: Math.max(0, Math.min(layout.y, maxHeight - layout.h)),
      w: Math.max(layout.minW || 1, Math.min(layout.w, layout.maxW || gridCols)),
      h: Math.max(layout.minH || 1, Math.min(layout.h, layout.maxH || maxHeight))
    };
  }

  // Create layouts object for react-grid-layout
  const layouts = {
    lg: widgets.map(widget => widget.layout)
  };

  const onLayoutChange = (layout: Layout[]) => {
    // Update widget layouts
    setWidgets((prev: DailyWidget[]) => 
      prev.map((widget: DailyWidget) => {
        const newLayout = layout.find(l => l.i === widget.daily_widget_id)
        return newLayout ? { ...widget, layout: newLayout } : widget
      })
    )
  }

  const onDragStop = (layout: Layout[]) => {
    // Apply constraints when the user finishes dragging
    applyConstraints(layout)
  }

  const onResizeStop = (layout: Layout[]) => {
    // Apply constraints when the user finishes resizing
    applyConstraints(layout)
  }

  const applyConstraints = (layout: Layout[]) => {
    const constrainedLayout = layout.map(l => constrainLayout(l));
    
    const updatedWidgets = widgets.map((widget: DailyWidget) => {
      const newLayout = constrainedLayout.find(l => l.i === widget.daily_widget_id)
      return newLayout ? { ...widget, layout: newLayout } : widget
    });
    
    setWidgets(updatedWidgets)
    
    // Add visual feedback
    const constrainedElements = document.querySelectorAll('.widget-container')
    constrainedElements.forEach((element) => {
      element.classList.add('constrained')
      setTimeout(() => {
        element.classList.remove('constrained')
      }, 500)
    })
  }

  // Add new widget using addNewWidget API
  const addWidget = async (widgetId: string) => {
    // Handle refresh case
    if (widgetId === 'refresh') {
      await fetchTodayWidgets();
      return;
    }
    
    const config = getWidgetConfig(widgetId);
    
    if (!config) {
      alert('Widget configuration not found.')
      return
    }
    
    try {
      // Call the API to add a new widget
      const response = await dashboardService.createWidget({
        widget_type: config.apiWidgetType as ApiWidgetType,
        frequency: 'daily' as ApiFrequency, // Default to daily
        importance: 0.5, // Default importance
        title: config.title,
        category: config.category as ApiCategory
      });
      
      console.log('Widget added successfully:', response);
      
      // Refresh the dashboard to show the new widget
      await fetchTodayWidgets();
      
    } catch (error) {
      console.error('Failed to add widget:', error);
      
    }
  }

  const removeWidget = async (dailyWidgetId: string) => {
    const widget = widgets.find(w => w.daily_widget_id === dailyWidgetId)
    const widgetType = widget?.widget_type || 'widget'
    
    // Prevent removal of view widgets - they should be managed through the Views dropdown
    if (widget?.widget_type === 'allSchedules' || widget?.widget_type === 'aiChat') {
      alert('View widgets cannot be removed directly. Use the Views dropdown to toggle their visibility.');
      return;
    }
    
    // Prevent removal of the automatically included "All Schedules" widget
    if (dailyWidgetId === 'auto-all-schedules') {
      alert('The "All Schedules" widget cannot be removed as it is automatically included for widget management.');
      return;
    }
    // Prevent removal of the automatically included "All Schedules" widget
    if (widget?.widget_type === 'todo-habit' || widget?.widget_type === 'todo-task') {
      alert('The "Habit and Task" widgets cannot be removed. Remove the individual tasks instead.');
      return;
    }
    
    if (confirm(`Are you sure you want to remove this ${widgetType} widget?`)) {
      try {
        // Call API to set is_active = 0
        await apiService.removeWidgetFromToday(dailyWidgetId);
        const updatedWidgets = widgets.filter((widget: DailyWidget) => widget.daily_widget_id !== dailyWidgetId);
        setWidgets(updatedWidgets)
      } catch (error) {
        alert('Failed to remove widget from dashboard. Please try again.');
        console.error('Failed to update is_active for DailyWidget:', error);
      }
    }
  }

  const renderWidget = (widget: DailyWidget) => {
    switch (widget.widget_type) {
      case 'alarm':
        return (
          <AlarmWidget 
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        )
      case 'websearch':
        return (
          <WebSearchWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'todo-task':
        return (
          <TaskListWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'todo-event':
        return (
          <EventTrackerWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
          );
      case 'todo-habit':
        return (
          <HabitListWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'singleitemtracker':
        return (
          <SingleItemTrackerWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'calendar':
        return (
          <CalendarWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'aiChat':
        return (
          <AiChatWidget
            widget={widget}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      case 'allSchedules':
        return (
          <AllSchedulesWidget
            onWidgetAddedToToday={() => fetchTodayWidgets()}
            onRemove={() => removeWidget(widget.daily_widget_id)}
          />
        );
      default:
        // For unimplemented widgets, show BaseWidget with placeholder content
        const config = getWidgetConfig(widget.widget_type);
    
        return (
          <BaseWidget
            title={config?.title || widget.widget_type}
            icon={config?.icon}
            onRemove={() => removeWidget(widget.daily_widget_id)}
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

  // Show loading state while fetching dashboard configuration
  if (dashboardLoading) {
    return (
      <div className="h-full w-full flex flex-col">
        <div className="px-4 py-3 flex justify-between items-center border-b bg-card shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-foreground">
                🧠 Brainboard
              </h1>
              <p className="text-xs text-muted-foreground">
                AI-Powered Dashboard with Smart Widgets
              </p>
            </div>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <h2 className="text-lg font-semibold mb-2">Loading Dashboard</h2>
            <p className="text-muted-foreground">Fetching today's widget configuration...</p>
          </div>
        </div>
      </div>
    )
  }

  // Show error state if dashboard loading failed
  if (dashboardError) {
    return (
      <div className="h-full w-full flex flex-col">
        <div className="px-4 py-3 flex justify-between items-center border-b bg-card shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-foreground">
                🧠 Brainboard
              </h1>
              <p className="text-xs text-muted-foreground">
                AI-Powered Dashboard with Smart Widgets
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchTodayWidgets}
              className="px-3 py-1 text-sm rounded bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-4">⚠️</div>
            <h2 className="text-lg font-semibold mb-2">Failed to Load Dashboard</h2>
            <p className="text-muted-foreground mb-4">{dashboardError}</p>
            <button
              onClick={fetchTodayWidgets}
              className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full flex flex-col bg-yellow-100">
      <div className="px-4 py-3 flex justify-between items-center border-b bg-card shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <h1 className="text-xl font-bold text-foreground">
              🧠 Brainboard
            </h1>
            <p className="text-xs text-muted-foreground">
              AI-Powered Dashboard with Smart Widgets
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowGridLines(!showGridLines)}
            className={`px-3 py-1 text-sm rounded transition-colors ${
              showGridLines 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            {showGridLines ? 'Hide Grid' : 'Show Grid'}
          </button>
          <AddWidgetButton 
            onAddWidget={addWidget} 
            existingViewWidgets={viewWidgetStates}
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-auto">
        <ResponsiveGridLayout
          className={`layout min-h-full ${showGridLines ? 'show-grid-lines' : ''}`}
          layouts={layouts}
          breakpoints={GRID_CONFIG.breakpoints}
          cols={GRID_CONFIG.cols}
          rowHeight={GRID_CONFIG.rowHeight}
          margin={GRID_CONFIG.margin}
          containerPadding={GRID_CONFIG.containerPadding}
          isDraggable={true}
          isResizable={true}
          preventCollision={true}
          compactType={null}
          useCSSTransforms={false}
          draggableHandle=".widget-drag-handle"
          onLayoutChange={onLayoutChange}
          onDragStop={onDragStop}
          onResizeStop={onResizeStop}
        >
        {widgets.map((widget: DailyWidget) => (
          <div key={widget.daily_widget_id} className="widget-container">
            {renderWidget(widget)}
          </div>
        ))}
      </ResponsiveGridLayout>
      </div>
    </div>
  )
}

export default Dashboard
