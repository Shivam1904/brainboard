# Dashboard Widget Logic Implementation

## Overview

The Dashboard component has been modified to implement a new widget logic system that processes widgets based on specific criteria and configuration settings.

## New Widget Logic

### 1. View Widgets (from All Widgets List)

**Widgets Processed:**
- `allSchedules` - All Schedules management widget
- `aiChat` - AI Chat widget

**Logic:**
- Only widgets with `widget_config.visibility = true` are displayed
- These widgets are automatically positioned and cannot be removed directly
- They are managed through the Views dropdown in the AddWidgetButton

### 2. Today's Widgets Processing

**Widget Types Created:**
- `advanced-single-task` - Individual advanced task widgets
- `todo-task` - Combined task list widget
- `websearch` - Web search widgets (automatically generated)

**Criteria for Advanced Single Task Widget:**

A widget becomes an "advanced single task" if ALL of the following conditions are met:

1. `widget_config.include_tracker_details === true`
2. `widget_config.include_alarm_details === true`
3. `widget_config.include_progress_details === true`
4. Has upcoming milestones within 7 days

**Milestone Check Logic:**
```javascript
const hasUpcomingMilestone = hasProgressDetails && widgetConfig.milestones && 
  Array.isArray(widgetConfig.milestones) && 
  widgetConfig.milestones.some((milestone) => {
    if (!milestone.due_date) return false;
    const milestoneDate = new Date(milestone.due_date);
    const today = new Date();
    const sevenDaysFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    return milestoneDate >= today && milestoneDate <= sevenDaysFromNow;
  });
```

**Web Search Widget Generation:**
- If `widget_config.include_websearch_details === true`, an additional web search widget is created
- The web search widget uses the `search_query_detailed` field or falls back to the widget title

## Widget Processing Flow

### Step 1: View Widgets
1. Fetch all widgets from API
2. Filter for `allSchedules` and `aiChat` widgets
3. Check `widget_config.visibility` for each
4. Add visible widgets to dashboard

### Step 2: Today's Widgets Analysis
1. Fetch today's widgets from API
2. For each widget, check the four criteria for advanced single task
3. Categorize widgets into:
   - Advanced single task widgets (meet all criteria)
   - Regular task widgets (don't meet all criteria)
   - Web search widgets (if `include_websearch_details` is true)

### Step 3: Widget Creation
1. Create individual advanced single task widgets
2. Create combined task list widget for regular tasks
3. Create web search widgets for tasks with web search enabled

## New Widget Types

### Advanced Single Task Widget
- **Type:** `advanced-single-task`
- **Component:** `SingleItemTrackerWidget`
- **Size:** 12x14 (default), 8x6 (min), 18x20 (max)
- **Icon:** 🎯
- **Description:** Advanced single task with tracker, alarm, and progress details

### Combined Task List Widget
- **Type:** `todo-task` (with special handling)
- **Component:** `TaskListWidget`
- **Special Property:** `widget_config.combined_tasks` array
- **Description:** Combined task list for regular tasks

### Web Search Widget
- **Type:** `websearch`
- **Component:** `WebSearchWidget`
- **Auto-generated:** Yes
- **Naming:** `Web Search: {Original Task Title}`

## Widget Removal Logic

### Protected Widgets
- View widgets (`allSchedules`, `aiChat`) - managed through Views dropdown
- Combined task list widget (`task-list-combined`) - cannot be removed directly
- Web search widgets (`websearch-*`) - automatically generated, cannot be removed directly

### Advanced Single Task Removal
- Removes the main widget
- Also removes associated web search widget if it exists
- Refreshes the dashboard to update all widgets

## Configuration Updates

### Widget Config (`src/config/widgets.ts`)
- Added `advanced-single-task` widget configuration
- Updated `getImplementedWidgets()` to include the new widget type

### Dashboard Component (`src/components/Dashboard.tsx`)
- Modified `fetchTodayWidgets()` function with new logic
- Updated `renderWidget()` to handle new widget types
- Enhanced `removeWidget()` with special handling for new widget types
- Added console logging for debugging

## Testing

A test script has been created at `src/test-widget-logic.js` that can be run in the browser console to verify the widget processing logic works correctly.

### Test Scenarios
1. **View Widgets:** Tests visibility logic for allSchedules and aiChat
2. **Advanced Single Task:** Tests criteria checking and widget creation
3. **Regular Tasks:** Tests combined task list creation
4. **Web Search:** Tests automatic web search widget generation

## Console Logging

The implementation includes detailed console logging to help debug the widget processing:

```javascript
console.log('Processing today\'s widgets:', todayWidgetsData.length, 'widgets');
console.log(`Widget "${widget.title}":`, { hasTrackerDetails, hasAlarmDetails, hasProgressDetails, hasUpcomingMilestone });
console.log(`Creating advanced single task widget for: ${widget.title}`);
console.log(`Adding to regular task list: ${widget.title}`);
console.log(`Creating web search widget for: ${widget.title}`);
```

## API Compatibility

The implementation maintains compatibility with the existing API structure:
- Uses existing `DailyWidget` interface
- Preserves all original widget properties
- Maintains backward compatibility with existing widgets
- Uses existing API endpoints for widget management

## Future Enhancements

1. **Performance Optimization:** Consider caching widget configurations
2. **Dynamic Criteria:** Make the 7-day milestone window configurable
3. **Widget Grouping:** Add visual grouping for related widgets
4. **Smart Positioning:** Improve widget positioning algorithm
5. **Batch Operations:** Add support for batch widget operations 