import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import AllSchedulesWidget from './widgets/AllSchedulesWidget'
import AiChatWidget from './widgets/AiChatWidget';
import MoodTrackerWidget from './widgets/MoodTrackerWidget';
import SimpleClockWidget from './widgets/SimpleClockWidget';
import WeatherWidget from './widgets/WeatherWidget';
import NotesWidget from './widgets/NotesWidget';
import AddWidgetButton from './AddWidgetButton'
import { DailyWidget, DashboardWidget } from '../services/api';
import { useDashboardData } from '../hooks/useDashboardData'
import { useDashboardActions, useDashboardStore } from '../stores/dashboardStore'
import { getWidgetConfig, getAllWidgets } from '../config/widgets'
import { dashboardService } from '../services/dashboard'
import Dashboard from './Dashboard'
import Planner from './Planner'
import { handleRemoveWidgetUtil } from '../utils/widgetUtils'

const MainContent = ({ date, allWidgets, todayWidgets }: { date: string, allWidgets: DashboardWidget[], todayWidgets: DailyWidget[] }) => {
    const [isPlanning, setIsPlanning] = useState(false)

    // Reset planning mode if widgets are cleared (optional, but keeps logic clean)
    // Actually, if widgets are cleared, we default to Planner anyway, so isPlanning state doesn't matter much.
    // But good to keep consistent.

    // If there are no widgets for today, OR if we are explicitly in planning mode
    if ((!todayWidgets || todayWidgets.length === 0) || isPlanning) {
        return (
            <div className="flex-1 h-full">
                <Planner
                    date={date}
                    isPlanning={isPlanning}
                    onStartPlanning={() => setIsPlanning(true)}
                    onEndPlanning={() => setIsPlanning(false)}
                />
            </div>
        )
    }

    return (
        <div className="flex-1 h-full">
            <Dashboard date={date} allWidgets={allWidgets} todayWidgets={todayWidgets} />
        </div>
    )
}

const SidebarWidgetContainer = ({
    title,
    children,
    id,
    isExpanded,
    onToggle
}: {
    title: string,
    children: React.ReactNode,
    id: string,
    isExpanded: boolean,
    onToggle: (newState: boolean) => Promise<void>
}) => {
    const [isLoading, setIsLoading] = useState(false);

    const handleToggle = async () => {
        setIsLoading(true);
        try {
            await onToggle(!isExpanded);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col border rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden mb-4 shadow-sm">
            <div className="flex justify-between items-center p-2 bg-muted/30 border-b">
                <span className="font-semibold text-xs uppercase tracking-wider text-muted-foreground">{title}</span>
                <div className="flex items-center gap-2">
                    {isLoading && (
                        <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                    )}
                    <button
                        onClick={handleToggle}
                        disabled={isLoading}
                        className="text-[10px] px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50"
                    >
                        {isExpanded ? 'Collapse' : 'Expand'}
                    </button>
                </div>
            </div>
            {isExpanded ? (
                <div className="p-3">
                    {children}
                </div>
            ) : null}
        </div>
    );
}

const NewDashboard = () => {
    const [currentDate, setCurrentDate] = useState(new Date().toISOString().split('T')[0])

    const {
        allWidgets: allWidgetsData,
        todayWidgets: todayWidgetsData,
        isLoading,
        error
    } = useDashboardData(currentDate)

    const [sizeOverrides, setSizeOverrides] = useState<Record<string, { w?: number; h?: number }>>({})
    const lastHeightValues = useRef<Record<string, number>>({})

    const { addWidgetToToday, removeWidgetFromToday } = useDashboardActions()

    const refreshAllWidgets = useCallback(() => {
        const store = useDashboardStore.getState()
        store.loadData(currentDate)
    }, [currentDate])

    const handleAddWidget = useCallback(async (widget: DashboardWidget | 'refresh') => {
        if (widget === 'refresh') {
            refreshAllWidgets()
            return
        }
        try {
            await addWidgetToToday(widget.id, currentDate);
            refreshAllWidgets(); // Refresh after adding
        } catch (error) {
            console.error('Failed to add widget:', error);
        }
    }, [addWidgetToToday, currentDate, refreshAllWidgets])

    const handleViewToggle = async (widgetType: string, isExpand: boolean) => {
        try {
            const allConfigs = getAllWidgets();
            const widgetConfig = allConfigs.find(w => w.apiWidgetType === widgetType);

            if (widgetConfig) {
                const existingWidget = allWidgetsData.find(w => w.widget_type === widgetType);

                if (existingWidget) {
                    await dashboardService.updateWidget(existingWidget.id, {
                        widget_config: {
                            ...existingWidget.widget_config,
                            visibility: isExpand
                        }
                    })
                } else if (isExpand) {
                    await dashboardService.createWidget({
                        widget_type: widgetType,
                        title: widgetConfig.title,
                        description: widgetConfig.description,
                        frequency: 'daily',
                        importance: 0.7,
                        category: 'utilities',
                        is_permanent: true,
                        widget_config: { visibility: true }
                    })
                }
                refreshAllWidgets();
            }
        } catch (err) {
            console.error('Failed to toggle view widget:', err)
            refreshAllWidgets();
        }
    }

    const onHeightChange = useCallback((dailyWidgetId: string, newHeight: number) => {
        if (lastHeightValues.current[dailyWidgetId] !== newHeight) {
            console.log('Widget height changed:', dailyWidgetId, newHeight)
            lastHeightValues.current[dailyWidgetId] = newHeight
            setSizeOverrides((prev) => ({
                ...prev,
                [dailyWidgetId]: { ...(prev[dailyWidgetId] || {}), h: newHeight },
            }))
        }
    }, [])

    const handleRemoveWidget = useCallback(async (dailyWidgetId: string) => {
        // Search in todayWidgetsData since handleRemoveWidget is called with daily_widget_id
        const widget = todayWidgetsData.find(w => w.daily_widget_id === dailyWidgetId)

        const viewWidgetTypes = ['allSchedules', 'aiChat', 'moodTracker', 'notes', 'weatherWidget', 'simpleClock']

        // If it's a view widget or one of our sidebar widgets, handle differently or block
        if (dailyWidgetId.startsWith('new-') || (widget && viewWidgetTypes.includes(widget.widget_type))) {
            alert('View widgets are managed via the sidebar toggles.');
            return;
        }

        await handleRemoveWidgetUtil({
            dailyWidgetId,
            widgetType: widget?.widget_type || 'widget',
            widgetTitle: widget?.title || '',
            date: currentDate,
            removeWidgetFromToday
        })
    }, [todayWidgetsData, removeWidgetFromToday, currentDate])

    const renderWidgetContent = (type: string, widget: DailyWidget) => {
        switch (type) {
            case 'allSchedules':
                return (
                    <AllSchedulesWidget
                        targetDate={currentDate}
                        widget={widget}
                        onHeightChange={onHeightChange}
                        onWidgetAddedToToday={handleAddWidget}
                        onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
                        onRefresh={refreshAllWidgets}
                    />
                );
            case 'moodTracker':
                return <MoodTrackerWidget targetDate={currentDate} widget={widget} onRemove={() => handleRemoveWidget(widget.daily_widget_id)} />;
            case 'notes':
                return <NotesWidget targetDate={currentDate} widget={widget} onRemove={() => handleRemoveWidget(widget.daily_widget_id)} />;
            case 'weatherWidget':
                return <WeatherWidget targetDate={currentDate} widget={widget} onRemove={() => handleRemoveWidget(widget.daily_widget_id)} />;
            case 'simpleClock':
                return <SimpleClockWidget targetDate={currentDate} widget={widget} onRemove={() => handleRemoveWidget(widget.daily_widget_id)} />;
            case 'aiChat':
                return <AiChatWidget widget={widget} onRemove={() => handleRemoveWidget(widget.daily_widget_id)} />;
            default:
                return null;
        }
    }

    const getWidgetUIInfo = (type: string) => {
        const w = allWidgetsData.find(x => x.widget_type === type);
        const isExpanded = w?.widget_config?.visibility === true;
        const config = getWidgetConfig(type);

        const data = {
            id: `new-${type}`,
            daily_widget_id: `new-${type}`,
            widget_id: w?.id || '',
            widget_type: type,
            title: config?.title || type,
            description: config?.description || '',
            is_permanent: true,
            widget_config: w?.widget_config || {},
            date: currentDate,
            created_at: new Date().toISOString(),
            frequency: 'daily',
            importance: 0.5,
            category: 'utilities',
            priority: 'LOW',
            layout: { i: `new-${type}`, x: 0, y: 0, w: 1, h: 1 }
        } as DailyWidget;

        return { data, isExpanded };
    }

    if (isLoading) {
        return (
            <div className="h-full w-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="h-full w-full flex items-center justify-center text-destructive">
                Error: {error}
            </div>
        )
    }

    const leftSidebarWidgets = [
        { type: 'allSchedules', title: 'Schedules' },
        { type: 'moodTracker', title: 'Mood Tracker' },
        { type: 'notes', title: 'Notes' }
    ].map(w => ({ ...w, ...getWidgetUIInfo(w.type) }));

    const rightSidebarWidgets = [
        { type: 'weatherWidget', title: 'Weather' },
        { type: 'simpleClock', title: 'Clock' },
        { type: 'aiChat', title: 'Brainy AI' }
    ].map(w => ({ ...w, ...getWidgetUIInfo(w.type) }));

    return (
        <div className="flex flex-col h-full w-full bg-gradient-to-br from-yellow-50 via-sky-50 to-white dark:from-indigo-950 dark:via-slate-950 dark:to-black">
            {/* Header */}
            <div className="px-6 py-4 flex justify-between items-center border-b border-border/40 backdrop-blur-md sticky top-0 z-10">
                <div className="flex flex-col">
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">
                        🧠 Brainboard
                    </h1>
                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest">
                        New Dashboard Layout
                    </p>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-3 bg-muted/50 px-3 py-1 rounded-full border border-border/50">
                        <button className="hover:text-primary transition-colors" onClick={() => setCurrentDate(new Date(new Date(currentDate).setDate(new Date(currentDate).getDate() - 1)).toISOString().split('T')[0])}>
                            ‹
                        </button>
                        <span className="text-sm font-medium tabular-nums font-mono">
                            {currentDate}
                        </span>
                        <button className="hover:text-primary transition-colors" onClick={() => setCurrentDate(new Date(new Date(currentDate).setDate(new Date(currentDate).getDate() + 1)).toISOString().split('T')[0])}>
                            ›
                        </button>
                    </div>
                    <AddWidgetButton
                        onAddWidget={handleAddWidget}
                        existingViewWidgets={allWidgetsData}
                        refreshAllWidgets={refreshAllWidgets}
                    />
                </div>
            </div>

            {/* Main Layout */}
            <div className="flex flex-1 overflow-hidden p-6 gap-6">
                {/* Left Sidebar */}
                <div className="w-80 flex flex-col overflow-y-auto pr-2 custom-scrollbar">
                    {leftSidebarWidgets.map((w) => (
                        <SidebarWidgetContainer
                            key={w.type}
                            title={w.title}
                            id={w.type}
                            isExpanded={w.isExpanded}
                            onToggle={(newState) => handleViewToggle(w.type, newState)}
                        >
                            {renderWidgetContent(w.type, w.data)}
                        </SidebarWidgetContainer>
                    ))}
                </div>

                {/* Center Main Area */}
                <div className="flex-1 flex flex-col">
                    <MainContent date={currentDate} allWidgets={allWidgetsData} todayWidgets={todayWidgetsData} />
                </div>

                {/* Right Sidebar */}
                <div className="w-80 flex flex-col overflow-y-auto pr-2 custom-scrollbar">
                    {rightSidebarWidgets.map((w) => (
                        <SidebarWidgetContainer
                            key={w.type}
                            title={w.title}
                            id={w.type}
                            isExpanded={w.isExpanded}
                            onToggle={(newState) => handleViewToggle(w.type, newState)}
                        >
                            {renderWidgetContent(w.type, w.data)}
                        </SidebarWidgetContainer>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default NewDashboard
