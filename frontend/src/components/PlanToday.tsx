import React, { useState, useEffect, useMemo } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { useDashboardActions } from '../stores/dashboardStore';
import { DashboardWidget, apiService, DailyWidget } from '../services/api';
import { Plus, Minus, AlertCircle, MinusCircle, ArrowDownCircle, CalendarIcon, ListOrdered } from 'lucide-react';
import { categoryColors } from '../constants/widgetConstants';
import { handleRemoveWidgetUtil } from '../utils/widgetUtils';

export type WidgetPriority = 'critical' | 'medium' | 'low';

interface WidgetPriorityInfo {
    priority: WidgetPriority;
    reason: string;
}

const PRIORITY_ORDER: Record<WidgetPriority, number> = { critical: 0, medium: 1, low: 2 };

interface PlanTodayProps {
    date: string;
    onClose: () => void;
}

const PlanToday = ({ date, onClose }: PlanTodayProps) => {
    const currentDate = date;
    const { allWidgets, todayWidgets, isLoading } = useDashboardData(date);
    const { addWidgetToToday, removeWidgetFromToday } = useDashboardActions();

    const [processingWidget, setProcessingWidget] = useState<string | null>(null);
    const [todayWidgetIds, setTodayWidgetIds] = useState<string[]>([]);
    const [widgetPriorities, setWidgetPriorities] = useState<Record<string, WidgetPriorityInfo>>({});
    const [priorityLoading, setPriorityLoading] = useState<Record<string, boolean>>({});
    const [sortByPriority, setSortByPriority] = useState(true);

    useEffect(() => {
        if (todayWidgets && Array.isArray(todayWidgets)) {
            const nextIds = todayWidgets.map((w: DailyWidget) => w.widget_id);
            setTodayWidgetIds(prev => {
                if (prev.length === nextIds.length && prev.every((id, i) => id === nextIds[i])) {
                    return prev;
                }
                return nextIds;
            });
        }
    }, [todayWidgets]);

    // Filter missions (used for list and for priority fetch) — only these get priority
    const missionWidgets = useMemo(() => {
        if (!allWidgets) return [];
        return (allWidgets as DashboardWidget[]).filter((widget: DashboardWidget) => {
            const type = widget.widget_type;
            const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker']);
            const excludedTypes = new Set(['aiChat', 'moodTracker', 'notes', 'weatherWidget', 'simpleClock', 'allSchedules']);
            return !trackerTypes.has(type) && !excludedTypes.has(type);
        });
    }, [allWidgets]);

    // Fetch priority for each mission only (backend uses completion history + frequency)
    const dateForApi = currentDate && currentDate.length >= 10 ? currentDate.slice(0, 10) : currentDate;
    const missionIdsStr = useMemo(() => missionWidgets.map((w: DashboardWidget) => w.id).join(','), [missionWidgets]);

    useEffect(() => {
        if (!dateForApi || missionIdsStr === '') return;
        const missionIds = missionIdsStr.split(',');
        const abort = { current: false };
        missionIds.forEach((widgetId: string) => {
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
    }, [dateForApi, missionIdsStr]);

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
                const dailyWidget = (todayWidgets as DailyWidget[]).find((w: DailyWidget) => w.widget_id === widget.id);
                if (dailyWidget) {
                    await handleRemoveWidgetUtil({
                        dailyWidgetId: dailyWidget.daily_widget_id,
                        _widgetType: widget.widget_type,
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
    const trackerWidgets = useMemo(() => {
        if (!allWidgets) return [];
        return (allWidgets as DashboardWidget[]).filter((widget: DashboardWidget) => {
            const type = widget.widget_type;
            const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker']);
            return trackerTypes.has(type);
        });
    }, [allWidgets]);

    // Sorted missions: by priority (critical first) when enabled, else list order
    const sortedMissions = useMemo(() => {
        if (!sortByPriority) return missionWidgets;
        return [...missionWidgets].sort((a, b) => {
            const pa = widgetPriorities[a.id]?.priority ?? 'medium';
            const pb = widgetPriorities[b.id]?.priority ?? 'medium';
            return PRIORITY_ORDER[pa] - PRIORITY_ORDER[pb];
        });
    }, [missionWidgets, sortByPriority, widgetPriorities]);

    /* Remove early return for loading to prevent scroll loss */
    // if (isLoadingAll || isLoadingToday) {
    //     return (
    //         <div className="flex items-center justify-center h-full">
    //             <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    //         </div>
    //     );
    // }

    const linkedTrackers = (widget: DashboardWidget) =>
        trackerWidgets.filter(
            (w: DashboardWidget) =>
                w.id === widget.widget_config?.selected_calendar ||
                w.id === widget.widget_config?.selected_habit_calendar ||
                w.id === widget.widget_config?.selected_yearly_calendar
        );

    return (
        <div className="flex flex-col h-full min-h-0 w-full">
            {/* Sticky header */}
            <div className="shrink-0 flex items-center justify-between gap-3 py-2 pr-1 border-b border-border/60 bg-background">
                <div className="flex items-center gap-2 min-w-0">
                    <button
                        type="button"
                        onClick={onClose}
                        className="shrink-0 size-8 flex items-center justify-center rounded-lg bg-muted text-muted-foreground hover:bg-muted/80"
                        aria-label="Close"
                    >
                        ×
                    </button>
                    <h2 className="text-sm font-medium truncate">
                        Missions for <span className="font-semibold text-foreground">{currentDate}</span>
                    </h2>
                    <span className="shrink-0 text-xs text-muted-foreground">
                        {sortedMissions.length} {sortedMissions.length === 1 ? 'mission' : 'missions'}
                    </span>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                    {isLoading && (
                        <div className="size-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    )}
                    <button
                        type="button"
                        onClick={() => setSortByPriority(p => !p)}
                        className={`flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-colors ${sortByPriority ? 'bg-primary/15 text-primary' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
                        title={sortByPriority ? 'Sorted by priority (Critical first)' : 'List order'}
                    >
                        <ListOrdered className="size-3.5" />
                        {sortByPriority ? 'Priority' : 'Order'}
                    </button>
                </div>
            </div>

            {/* Scrollable list — compact cards that scale from 5 to 30 */}
            <div className="flex-1 min-h-0 overflow-y-auto py-3 px-1 custom-scrollbar">
                <ul className="flex flex-col gap-2">
                    {sortedMissions.map((widget: DashboardWidget) => {
                        const isAdded = todayWidgetIds.includes(widget.id);
                        const categoryColor = getCategoryColor(widget.category);
                        const trackers = linkedTrackers(widget);
                        const priorityInfo = widgetPriorities[widget.id];
                        const loading = priorityLoading[widget.id];

                        return (
                            <li
                                key={widget.id}
                                className={`rounded-xl border transition-all duration-200 bg-card hover:shadow-sm cursor-pointer ${isAdded ? 'border-primary/50 bg-primary/5' : 'border-border/60'}`}
                                onClick={() => handleToggleWidget(widget)}
                            >
                                <div className="py-2 px-3">
                                    {/* Row 1: Title + category + add/remove */}
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="min-w-0 flex-1">
                                            <p className="font-semibold text-sm truncate">{widget.title}</p>
                                            {widget.description ? (
                                                <p className="text-xs text-muted-foreground truncate mt-0.5">{widget.description}</p>
                                            ) : null}
                                        </div>
                                        <div className="flex items-center gap-1.5 shrink-0">
                                            <span
                                                className="text-[10px] font-semibold px-1.5 py-0.5 rounded-md uppercase tracking-wider"
                                                style={{ backgroundColor: `${categoryColor}18`, color: categoryColor }}
                                            >
                                                {widget.category || 'General'}
                                            </span>
                                            <button
                                                type="button"
                                                onClick={e => {
                                                    e.stopPropagation();
                                                    handleToggleWidget(widget);
                                                }}
                                                disabled={processingWidget === widget.id}
                                                className={`p-1.5 rounded-lg transition-colors shrink-0 ${isAdded ? ' hover:bg-destructive/20' : processingWidget === widget.id ? 'text-muted-foreground cursor-wait' : 'text-muted-foreground hover:bg-primary hover:text-primary-foreground'}`}
                                                aria-label={isAdded ? 'Remove from today' : 'Add to today'}
                                            >
                                                {processingWidget === widget.id ? (
                                                    <div className="size-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                                ) : isAdded ? (
                                                    <Minus className="size-4" />
                                                ) : (
                                                    <Plus className="size-4" />
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                    {/* Row 2: Priority badge + reason (single line) */}
                                    <div className="mt-1.5 flex items-center gap-2 min-w-0">
                                        {loading ? (
                                            <span className="text-[10px] text-muted-foreground">Loading…</span>
                                        ) : priorityInfo ? (
                                            <>
                                                <span
                                                    className={`shrink-0 inline-flex items-center gap-0.5 text-[10px] font-medium px-1.5 py-0.5 rounded ${priorityStyles[priorityInfo.priority].bg} ${priorityStyles[priorityInfo.priority].text}`}
                                                >
                                                    {priorityStyles[priorityInfo.priority].icon}
                                                    {priorityStyles[priorityInfo.priority].label}
                                                </span>
                                                <span
                                                    className="text-[10px] text-muted-foreground truncate"
                                                    dangerouslySetInnerHTML={{ __html: priorityInfo.reason }}
                                                />
                                            </>
                                        ) : null}
                                    </div>
                                    {/* Row 3: Tracker chips (compact horizontal wrap) */}
                                    {trackers.length > 0 ? (
                                        <div className="mt-2 flex flex-wrap gap-1.5">
                                            {trackers.map((trackerWidget: DashboardWidget) => {
                                                const trackerAdded = todayWidgetIds.includes(trackerWidget.id);
                                                return (
                                                    <button
                                                        key={trackerWidget.id}
                                                        type="button"
                                                        onClick={e => {
                                                            e.stopPropagation();
                                                            handleToggleWidget(trackerWidget);
                                                        }}
                                                        disabled={processingWidget === trackerWidget.id}
                                                        className={`inline-flex items-center gap-1.5 py-1 px-2 rounded-lg border text-xs transition-colors ${trackerAdded ? 'border-primary/50 bg-primary/5 text-primary' : 'border-border/60 bg-muted/50 text-muted-foreground hover:border-primary/40 hover:bg-muted'}`}
                                                    >
                                                        <CalendarIcon className="size-3 shrink-0" />
                                                        <span className="truncate max-w-[120px]">{trackerWidget.title}</span>
                                                        {processingWidget === trackerWidget.id ? (
                                                            <div className="size-3 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0" />
                                                        ) : trackerAdded ? (
                                                            <Minus className="size-3 shrink-0" />
                                                        ) : (
                                                            <Plus className="size-3 shrink-0" />
                                                        )}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    ) : null}
                                </div>
                            </li>
                        );
                    })}
                </ul>

                {sortedMissions.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                        <p className="text-sm">No missions found. Create widgets to use as missions.</p>
                    </div>
                )}
            </div>

            {/* Sticky footer */}
            <div className="shrink-0 flex justify-end py-3 px-1 border-t border-border/60 bg-background">
                <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90"
                >
                    Done
                </button>
            </div>
        </div>
    );
};

export default PlanToday;
