# Habit Tracker Widget Implementation

## Overview

The HabitTrackerWidget is a new widget that displays tasks in an arced grid layout for a month period, similar to the circular habit tracker image described. It provides a visual way to track daily habits and routines.

## Features

### 1. Circular Grid Layout
- **31 days** arranged in a circle around the perimeter
- **Concentric rings** for each habit/task
- **Checkboxes** for each day-habit combination
- **Color-coded** by task category

### 2. Task Management
- **Task selection**: Choose which tasks to track in the habit tracker
- **Category colors**: Each task category has a distinct color
- **Completion tracking**: Visual checkboxes show completed vs. incomplete habits
- **Monthly navigation**: Navigate between months to track progress over time

### 3. Data Integration
- **API integration**: Fetches data using `calendar_type: 'habit'`
- **Widget linking**: Tasks can be linked to the habit tracker via `selected_calendar`
- **Real-time updates**: Reflects changes in task completion status

## Implementation Details

### File Structure
```
src/components/widgets/HabitTrackerWidget.tsx  # Main widget component
src/config/widgets.ts                          # Widget configuration
src/components/Dashboard.tsx                   # Dashboard integration
```

### Key Components

#### 1. HabitTrackerWidget Component
- **Props**: `onRemove`, `widget`, `targetDate`
- **State**: Manages habit data, available widgets, selections
- **API calls**: Fetches habit data and available widgets

#### 2. Circular Grid Layout
- **Day positioning**: Uses trigonometry to position day numbers around the circle
- **Habit rings**: Each habit gets its own concentric ring
- **Checkbox positioning**: Checkboxes are positioned at the intersection of days and habits

#### 3. Task Selection System
- **Available widgets**: Fetches all available task widgets
- **Selection state**: Tracks which tasks are selected for the habit tracker
- **API updates**: Updates widget configurations when selections change

### Data Flow

1. **Initialization**: Widget fetches habit data and available tasks
2. **Data fetching**: Uses `apiService.getWidgetActivityForCalendar()` with `calendar_type: 'habit'`
3. **Task linking**: Tasks are linked via `widget_config.selected_calendar`
4. **Completion tracking**: Task completion status is tracked via `activity_data.status`

### Widget Configuration

```typescript
'todo-habit': {
  id: 'todo-habit',
  apiWidgetType: 'todo-habit',
  title: 'Habit Tracker',
  description: 'Track daily habits and routines with circular grid layout',
  component: 'HabitTrackerWidget',
  minSize: { w: 12, h: 12 },
  maxSize: { w: 30, h: 30 },
  defaultSize: { w: 16, h: 16 },
  deletable: true,
  resizable: true,
  category: 'productivity',
  icon: '🔄'
}
```

## Usage

### 1. Adding the Widget
- Use the "Add Widget" button in the dashboard
- Select "Habit Tracker" from the widget list
- The widget will appear with default size 16x16

### 2. Configuring Tasks
- Click the pencil icon to edit task selection
- Select/deselect tasks to include in the habit tracker
- Tasks are automatically color-coded by category

### 3. Tracking Progress
- Navigate between months using the arrow buttons
- Click "Today" to return to the current month
- Checkboxes show completion status for each day-habit combination

### 4. Task Completion
- Tasks are marked as completed when their `activity_data.status` is 'completed'
- Completion status is reflected in real-time in the circular grid
- Visual feedback shows progress over time

## Technical Implementation

### State Management
```typescript
interface HabitData {
  year: number;
  month: number;
  days: HabitDay[];
  tasks: HabitTask[];
  monthlyStats?: {
    totalTasksCompleted: number;
    totalTasks: number;
    averageCompletionRate: number;
    longestStreak: number;
  };
}
```

### API Integration
- **Data fetching**: `getWidgetActivityForCalendar()` with habit calendar type
- **Widget updates**: `updateWidget()` for task selection changes
- **Widget listing**: `getAllWidgets()` for available task selection

### Styling
- **Tailwind CSS**: Responsive design with hover effects
- **Color system**: Category-based color coding
- **Interactive elements**: Hover states and transitions

## Future Enhancements

### 1. Streak Tracking
- Visual streak indicators for consecutive completions
- Streak statistics and achievements
- Motivational streak milestones

### 2. Analytics
- Monthly completion rates
- Category performance tracking
- Progress visualization over time

### 3. Customization
- Custom habit colors
- Flexible habit scheduling
- Personal habit categories

### 4. Integration
- Calendar widget synchronization
- Task list widget integration
- Export/import functionality

## Troubleshooting

### Common Issues

1. **Widget not loading**: Check API connectivity and widget configuration
2. **Tasks not appearing**: Verify task selection and `selected_calendar` configuration
3. **Completion not updating**: Check `activity_data.status` values in the API response

### Debug Information
- Console logs show data fetching and processing
- Error messages display API failures
- Success messages confirm configuration updates

## Conclusion

The HabitTrackerWidget provides a unique and intuitive way to track daily habits and routines. Its circular grid layout makes it easy to visualize progress over time, while the integrated task management system ensures consistency with the broader application architecture.

The widget is designed to be extensible, allowing for future enhancements in streak tracking, analytics, and customization options. 