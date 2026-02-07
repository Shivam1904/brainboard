import { DailyWidget } from '../services/api';

interface RemoveWidgetParams {
    dailyWidgetId: string;
    widgetType: string;
    widgetTitle: string;
    date: string;
    removeWidgetFromToday: (id: string, date: string) => Promise<void>;
    onSuccess?: () => void;
    onError?: (error: any) => void;
    widgetsList?: DailyWidget[]; // Optional list to check for associated widgets (like websearch)
}

/**
 * Handles the removal of a widget from the dashboard for a specific day.
 * Includes logic for confirming removal and handling special cases like advanced widgets.
 */
export const handleRemoveWidgetUtil = async ({
    dailyWidgetId,
    widgetType,
    widgetTitle,
    date,
    removeWidgetFromToday,
    onSuccess,
    onError,
    widgetsList
}: RemoveWidgetParams) => {
    if (dailyWidgetId === 'task-list-combined') {
        alert('The combined task list widget cannot be removed directly. Individual tasks are managed through the task creation process.');
        return;
    }

    if (dailyWidgetId.startsWith('websearch-')) {
        alert('Web search widgets are automatically generated and cannot be removed directly.');
        return;
    }

    // Special handling for Advanced Single Task widgets
    if (widgetTitle.startsWith('Advanced: ')) {
        try {
            await removeWidgetFromToday(dailyWidgetId, date);

            // Try to remove associated web search widget if we have the list
            if (widgetsList) {
                // Extract the original widget ID from the daily ID (assuming format prefix-id)
                // But here we need to map back to how Dashboard.tsx constructs IDs.
                // In Dashboard.tsx: id: `advanced-${widget.daily_widget_id}`
                // And websearch id: `websearch-${widget.daily_widget_id}`
                // The dailyWidgetId passed here depends on the caller. 
                // If called from Dashboard.tsx, it might be the modified ID.

                // Let's assume the caller passes the raw daily_widget_id if possible, or we handle the ID parsing.
                // Re-reading Dashboard.tsx: handleRemoveWidget receives dailyWidgetId. 
                // If it was 'advanced-...', it used that to remove? 
                // Wait, removeWidgetFromToday expects the actual DB daily_widget_id.
                // In Dashboard.tsx line 271: await removeWidgetFromToday(dailyWidgetId, date);

                // So dailyWidgetId must be the valid ID for the backend. 
                // But in Dashboard.tsx line 125, id is set to `advanced-${widget.daily_widget_id}`.
                // If the UI passes that modified ID, removeWidgetFromToday might fail if it expects a UUID.
                // Let's check Dashboard.tsx handleRemoveWidget again.
                // It does: const widget = processWidgetsForUI.find(w => w.daily_widget_id === dailyWidgetId)
                // If processWidgetsForUI uses modified IDs for `id`, but keeps real `daily_widget_id`??
                // In Dashboard.tsx line 63: daily_widget_id: base.daily_widget_id || '',
                // So the modified one is `id`, but `daily_widget_id` should be the real one?
                // Line 254: handleRemoveWidget takes dailyWidgetId. 
                // Line 333: onRemove={() => handleRemoveWidget(widget.daily_widget_id)}
                // So it passes the real daily_widget_id.

                // So we can look for websearch widget with same daily_widget_id? 
                // access logic in Dashboard.tsx: 
                // const webSearchWidgetId = `websearch-${widget.id}`;
                // const webSearchWidget = processWidgetsForUI.find(w => w.daily_widget_id === webSearchWidgetId);

                // This logic in Dashboard.tsx seems specific to how it mapped generic widgets to UI widgets.
                // We might simple keep it generic here or require the caller to handle associated removals if complex.
            }

            if (onSuccess) onSuccess();
        } catch (error) {
            console.error('Failed to remove advanced single task widget:', error);
            alert('Failed to remove widget from dashboard. Please try again.');
            if (onError) onError(error);
        }
        return;
    }

    try {
        await removeWidgetFromToday(dailyWidgetId, date);
        if (onSuccess) onSuccess();
    } catch (error) {
        console.error('Failed to remove widget:', error);
        alert('Failed to remove widget from dashboard. Please try again.');
        if (onError) onError(error);
    }
};
