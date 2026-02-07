import React, { useState, useEffect } from 'react';
import { useAllWidgetsData, useTodayWidgetsData } from '../hooks/useDashboardData';
import { useDashboardActions } from '../stores/dashboardStore';
import { DashboardWidget, apiService } from '../services/api';
import { Plus, Minus, AlertCircle, MinusCircle, ArrowDownCircle, CalendarIcon } from 'lucide-react';
import { categoryColors } from './widgets/CalendarWidget';
import { handleRemoveWidgetUtil } from '../utils/widgetUtils';

export type WidgetPriority = 'critical' | 'medium' | 'low';

interface WidgetPriorityInfo {
  priority: WidgetPriority;
  reason: string;
}

interface PlanTodayProps {
    date: string;
    onClose: () => void;
}

const PlanToday = ({ date, onClose }: PlanTodayProps) => {
    const currentDate = date;
    const { allWidgets, isLoading: isLoadingAll } = useAllWidgetsData();
    const { todayWidgets, isLoading: isLoadingToday } = useTodayWidgetsData(currentDate);
    const { addWidgetToToday, removeWidgetFromToday } = useDashboardActions();

    const [processingWidget, setProcessingWidget] = useState<string | null>(null);
    const [todayWidgetIds, setTodayWidgetIds] = useState<string[]>([]);
    const [widgetPriorities, setWidgetPriorities] = useState<Record<string, WidgetPriorityInfo>>({});
    const [priorityLoading, setPriorityLoading] = useState<Record<string, boolean>>({});

    useEffect(() => {
        if (todayWidgets) {
            setTodayWidgetIds(todayWidgets.map(w => w.widget_id));
        }
    }, [todayWidgets]);

    // Filter missions (used for list and for priority fetch) — only these get priority
    const missionWidgets = allWidgets.filter(widget => {
        const type = widget.widget_type;
        const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker']);
        const excludedTypes = new Set(['aiChat', 'moodTracker', 'notes', 'weatherWidget', 'simpleClock', 'allSchedules']);
        return !trackerTypes.has(type) && !excludedTypes.has(type);
    });

    // Fetch priority for each mission only (backend uses completion history + frequency)
    const dateForApi = currentDate && currentDate.length >= 10 ? currentDate.slice(0, 10) : currentDate;
    useEffect(() => {
        if (!dateForApi || missionWidgets.length === 0) return;
        const missionIds = missionWidgets.map(w => w.id);
        const abort = { current: false };
        missionIds.forEach((widgetId) => {
            setPriorityLoading(prev => ({ ...prev, [widgetId]: true }));
            apiService
                .getWidgetPriorityForDate(widgetId, dateForApi)
                .then((res) => {
                    if (!abort.current) {
                        setWidgetPriorities(prev => ({ ...prev, [widgetId]: { priority: res.priority, reason: res.reason } }));
                    }
                })
                .catch(() => {
                    if (!abort.current) {
                        setWidgetPriorities(prev => ({ ...prev, [widgetId]: { priority: 'medium', reason: 'Could not load past performance.' } }));
                    }
                })
                .finally(() => {
                    if (!abort.current) {
                        setPriorityLoading(prev => ({ ...prev, [widgetId]: false }));
                    }
                });
        });
        return () => { abort.current = true; };
    }, [dateForApi, missionWidgets.map(w => w.id).join(',')]);

    const getCategoryColor = (category: string) => {
        const lowerCategory = category?.toLowerCase() || 'utilities';
        return categoryColors[lowerCategory as keyof typeof categoryColors]?.color || 'gray';
    };

    const priorityStyles: Record<WidgetPriority, { bg: string; text: string; icon: React.ReactNode; label: string }> = {
        critical: { bg: 'bg-red-100 dark:bg-red-950/50', text: 'text-red-700 dark:text-red-400', icon: <AlertCircle className="w-3 h-3" />, label: 'Critical' },
        medium: { bg: 'bg-amber-100 dark:bg-amber-950/50', text: 'text-amber-700 dark:text-amber-400', icon: <MinusCircle className="w-3 h-3" />, label: 'Medium' },
        low: { bg: 'bg-emerald-100 dark:bg-emerald-950/50', text: 'text-emerald-700 dark:text-emerald-400', icon: <ArrowDownCircle className="w-3 h-3" />, label: 'Low' },
    };

    const handleToggleWidget = async (widget: DashboardWidget) => {
        const isAdded = todayWidgetIds.includes(widget.id);
        setProcessingWidget(widget.id);

        try {
            if (isAdded) {
                // Find the daily_widget_id for this widget
                const dailyWidget = todayWidgets.find(w => w.widget_id === widget.id);
                if (dailyWidget) {
                    await handleRemoveWidgetUtil({
                        dailyWidgetId: dailyWidget.daily_widget_id,
                        widgetType: widget.widget_type,
                        widgetTitle: widget.title,
                        date: currentDate,
                        removeWidgetFromToday
                    });
                }
            } else {
                await addWidgetToToday(widget.id, currentDate);
            }
        } catch (err) {
            console.error('Failed to toggle widget:', err);
            alert('Failed to update widget.');
        } finally {
            setProcessingWidget(null);
        }
    };

    // Filter trackers
    const trackerWidgets = allWidgets.filter(widget => {
        const type = widget.widget_type;
        const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker']);

        console.log("trackerWidgets", widget);
        // Exclude trackers and utilities
        return trackerTypes.has(type);
    });

    /* Remove early return for loading to prevent scroll loss */
    // if (isLoadingAll || isLoadingToday) {
    //     return (
    //         <div className="flex items-center justify-center h-full">
    //             <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    //         </div>
    //     );
    // }

    return (
        <div className="flex flex-col h-screen w-full">
            <div className="flex items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                    <button onClick={onClose} className="bg-gray-200 text-primary px-2 py-1 rounded-lg">X</button>
                    <h2 className="text-md ">Select Missions for <span className="font-bold">{currentDate}</span></h2>
                </div>
                {(isLoadingAll || isLoadingToday) && (
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                )}
            </div>

            <div className="flex flex-col gap-2 overflow-y-auto pb-4 custom-scrollbar">
                {missionWidgets.map(widget => {
                    const isAdded = todayWidgetIds.includes(widget.id);
                    const categoryColor = getCategoryColor(widget.category);

                    return (
                        <div
                            key={widget.id}
                            onClick={() => handleToggleWidget(widget)}

                            className={`py-2 px-3 rounded-xl border transition-all duration-200 bg-card hover:shadow-sm  ${isAdded ? 'border-primary/50 bg-primary/5' : 'border-border/60'}`}
                        >
                            <div className="flex items-center justify-between gap-3"
                                    >
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        
                                        <span className="font-semibold text-sm truncate">{widget.title}</span>
                                    {widget.description && (
                                        <span className="text-xs text-muted-foreground line-clamp-1 ml-1">{widget.description}</span>
                                    )}
                                    </div>
                                    {/* Past performance: priority + reason */}
                                    <div className="mt-1.5 ml-1 flex flex-wrap items-center gap-1.5">
                                        {priorityLoading[widget.id] ? (
                                            <span className="text-[10px] text-muted-foreground">Loading…</span>
                                        ) : widgetPriorities[widget.id] ? (
                                            <>
                                                <span className={`inline-flex items-center gap-0.5 text-[10px] font-medium px-1.5 py-0.5 rounded ${priorityStyles[widgetPriorities[widget.id].priority].bg} ${priorityStyles[widgetPriorities[widget.id].priority].text}`}>
                                                    {priorityStyles[widgetPriorities[widget.id].priority].icon}
                                                    {priorityStyles[widgetPriorities[widget.id].priority].label}
                                                </span>
                                                <span className="text-[10px] text-muted-foreground line-clamp-2" dangerouslySetInnerHTML={{ __html: widgetPriorities[widget.id].reason }}></span>
                                            </>
                                        ) : null}
                                    </div>
                                </div>
                                <span
                                            className="text-[9px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider shrink-0"
                                            style={{
                                                backgroundColor: `${categoryColor}20`,
                                                color: categoryColor
                                            }}
                                        >
                                            {widget.category || 'General'}
                                        </span>
                                <button
                                    onClick={() => handleToggleWidget(widget)}
                                    disabled={processingWidget === widget.id}
                                    className={`p-1.5 rounded-lg transition-all shrink-0 ${isAdded
                                        ? 'text-destructive bg-destructive/10 hover:bg-destructive/20'
                                        : processingWidget === widget.id
                                            ? 'text-muted-foreground animate-pulse cursor-wait'
                                            : 'text-muted-foreground hover:bg-primary hover:text-primary-foreground'
                                        }`}
                                >
                                    {processingWidget === widget.id ? (
                                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                    ) : isAdded ? (
                                        <Minus className="w-4 h-4" />
                                    ) : (
                                        <Plus className="w-4 h-4" />
                                    )}
                                </button>
                                
                            </div>
                            <div className="flex items-center gap-2">
                                {trackerWidgets.filter(w => w.id === widget.widget_config?.selected_calendar || w.id === widget.widget_config?.selected_habit_calendar || w.id === widget.widget_config?.selected_yearly_calendar).map(trackerWidget => {
                                    const isAdded = todayWidgetIds.includes(trackerWidget.id);

                                    return (
                                        <div
                                            key={trackerWidget.id}
                                            className={`py-1 px-2 rounded-md  transition-all duration-200  bg-card hover:shadow-sm  ${isAdded ? 'border border-primary/50 bg-primary/5' : ''}`}
                                        >
                                            <div className="flex items-center justify-between gap-3"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleToggleWidget(trackerWidget);
                                                    }}
                                                    >
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-1 mb-0.5 text-gray-500">
                                                        <CalendarIcon className="w-3 h-3" />
                                                        <p className="text-xs truncate">{trackerWidget.title}</p>
                                                    </div>
                                                </div>

                                                <button
                                                    disabled={processingWidget === trackerWidget.id}
                                                    className={`p-1 rounded-lg transition-all shrink-0 ${isAdded
                                                        ? 'text-destructive bg-destructive/10 hover:bg-destructive/20'
                                                        : processingWidget === trackerWidget.id
                                                            ? 'text-muted-foreground animate-pulse cursor-wait'
                                                            : 'text-muted-foreground hover:bg-primary hover:text-primary-foreground'
                                                        }`}
                                                >
                                                    {processingWidget === trackerWidget.id ? (
                                                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                                    ) : isAdded ? (
                                                        <Minus className="w-4 h-4" />
                                                    ) : (
                                                        <Plus className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </div>

                                        </div>
                                    );
                                })}
                            </div>

                        </div>
                    );
                })}

                {missionWidgets.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                        <p className="text-sm">No missions found. Create some widgets first!</p>
                    </div>
                )}
            </div>
            <div className="flex items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                    <button onClick={onClose} className="bg-primary text-primary-foreground px-2 py-1 rounded-lg">Done</button>
                </div>
            </div>
        </div>
    );
};

export default PlanToday;
