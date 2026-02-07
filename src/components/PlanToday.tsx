import React, { useState, useEffect } from 'react';
import { useAllWidgetsData, useTodayWidgetsData } from '../hooks/useDashboardData';
import { useDashboardActions } from '../stores/dashboardStore';
import { DashboardWidget } from '../services/api';
import { Plus, Minus, X } from 'lucide-react';
import { categoryColors } from './widgets/CalendarWidget';
import { handleRemoveWidgetUtil } from '../utils/widgetUtils';

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

    useEffect(() => {
        if (todayWidgets) {
            setTodayWidgetIds(todayWidgets.map(w => w.widget_id));
        }
    }, [todayWidgets]);

    const getCategoryColor = (category: string) => {
        const lowerCategory = category?.toLowerCase() || 'utilities';
        return categoryColors[lowerCategory as keyof typeof categoryColors]?.color || 'gray';
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

    // Filter missions
    const missionWidgets = allWidgets.filter(widget => {
        const type = widget.widget_type;
        const trackerTypes = new Set(['calendar', 'weekchart', 'yearCalendar', 'pillarsGraph', 'habitTracker']);
        const excludedTypes = new Set(['aiChat', 'moodTracker', 'notes', 'weatherWidget', 'simpleClock', 'allSchedules']);

        // Exclude trackers and utilities
        return !trackerTypes.has(type) && !excludedTypes.has(type);
    });

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
        <div className="flex flex-col h-full w-full">
            <div className="flex items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                    <button onClick={onClose} className="bg-gray-200 text-primary px-2 py-1 rounded-lg">X</button>
                    <h2 className="text-md font-bold">Select Missions for Today</h2>
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
                            className={`py-2 px-3 rounded-xl border transition-all duration-200 bg-card hover:shadow-sm  ${isAdded ? 'border-primary/50 bg-primary/5' : 'border-border/60'}`}
                        >
                            <div className="flex items-center justify-between gap-3">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-0.5">
                                        <span
                                            className="text-[9px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider shrink-0"
                                            style={{
                                                backgroundColor: `${categoryColor}20`,
                                                color: categoryColor
                                            }}
                                        >
                                            {widget.category || 'General'}
                                        </span>
                                        <h3 className="font-semibold text-sm truncate">{widget.title}</h3>
                                    </div>
                                    {widget.description && (
                                        <p className="text-xs text-muted-foreground line-clamp-1 ml-1">{widget.description}</p>
                                    )}
                                </div>

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
                                    const categoryColor = getCategoryColor(trackerWidget.category);

                                    return (
                                        <div
                                            key={trackerWidget.id}
                                            className={`py-2 px-3 transition-all duration-200 bg-card hover:shadow-sm  ${isAdded ? 'border-primary/50 bg-primary/5' : 'border-border/60'}`}
                                        >
                                            <div className="flex items-center justify-between gap-3">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-2 mb-0.5">
                                                        <h3 className="font-semibold text-sm truncate">{trackerWidget.title}</h3>
                                                    </div>
                                                </div>

                                                <button
                                                    onClick={() => handleToggleWidget(trackerWidget)}
                                                    disabled={processingWidget === trackerWidget.id}
                                                    className={`p-1.5 rounded-lg transition-all shrink-0 ${isAdded
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

        </div>
    );
};

export default PlanToday;
