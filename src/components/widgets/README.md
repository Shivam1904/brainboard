# Widget Components

This directory contains all the widget components for the Brainboard system.

## ✅ Implemented Widgets

### Web Search Widget (`WebSearchWidget.tsx`)

**Status**: ✅ Fully implemented with dummy data

**Features**:
- Displays individual web search results for scheduled queries
- Each widget has its own unique search query and results
- Dynamic content based on search query
- Loading states and error handling
- Responsive design with image support
- Configurable display options (showImages, maxResults)

**API Integration**:
- Ready for backend integration with API endpoints defined in `src/config/api.ts`
- Currently uses dummy data with `getDummyWebSearchResult()` function
- Easy to switch to real API calls by uncommenting the import and API calls

**Dummy Data**:
- Unique results for different search queries (football, AI, stocks, etc.)
- Each result includes formatted content with images
- Timestamps and search terms are displayed

**Usage**:
The widget is automatically created for each `webSearch` type item in the dashboard configuration. Each widget displays results for its specific search query.

### All Schedules Widget (`AllSchedulesWidget.tsx`)

**Status**: ✅ Fully implemented with CRUD functionality

**Features**:
- **Complete Schedule Management**: View, add, edit, and delete all widget schedules
- **Type-Specific Forms**: Dynamic forms based on widget type
- **Category Management**: Color-coded categories for organization
- **CRUD Operations**: Full create, read, update, delete functionality
- **Modal Interfaces**: Clean form interfaces for editing
- **Responsive Design**: Large widget (16x12) with scrollable content

**Supported Widget Types**:
- `userTask` - Tasks with importance levels
- `userHabit` - Habits with alarms and importance
- `itemTracker` - Metric tracking
- `webSearch` - Web search queries
- `alarm` - Time-based alarms
- `calendar` - Calendar widgets
- `weatherWig` - Weather information
- `statsWidget` - Statistics display
- `newsWidget` - News feeds

**Form Features**:
- **Common Fields**: Title, type, frequency, category
- **Type-Specific Fields**: 
  - Web Search: Search query
  - Tasks/Habits: Importance, alarms
  - Alarms: Time specifications
- **Validation**: Required field validation
- **Dynamic Forms**: Fields appear/disappear based on widget type

**API Integration**:
- Ready for backend integration
- Currently uses dummy data from `src/data/dashboardDummyData.ts`
- Prepared for real API calls (commented out)

### Task List Widget (`TaskListWidget.tsx`)

**Status**: ✅ Fully implemented with task management functionality

**Features**:
- **Today's Tasks Display**: Shows all tasks for the current day
- **Progress Tracking**: Visual progress bar showing completion percentage
- **Task Management**: Check/uncheck tasks to update status
- **Mission Creation**: Add new missions with comprehensive form
- **Priority System**: Color-coded priority levels (High, Medium, Low)
- **Category Organization**: Visual category tags for task organization
- **Responsive Design**: Medium-large widget (12x10) with scrollable content

**Task Properties**:
- **Title** - Task name
- **Description** - Detailed task description
- **Priority** - High, Medium, or Low priority
- **Category** - Work, Health, Learning, Personal
- **Due Date** - Task deadline
- **Completion Status** - Checked/unchecked state

**Mission Form Features**:
- **Title** - Mission name (required)
- **Description** - Detailed mission description
- **Priority** - Priority level selection
- **Category** - Category selection
- **Due Date** - Date picker for deadline
- **Frequency** - Daily, Weekly, Monthly, or Once

**API Integration**:
- **Get Today's Tasks**: `GET /api/tasks/today`
- **Update Task Status**: `PUT /api/tasks/update`
- **Add New Mission**: `POST /api/tasks/mission`
- Ready for backend integration
- Currently uses dummy data with realistic task examples
- Prepared for real API calls (commented out)

**Dummy Data**:
- 5 sample tasks with different priorities and categories
- Mix of completed and pending tasks
- Realistic task descriptions and due dates
- Various categories (work, health, learning, personal)

**Usage**:
The widget displays today's tasks with a progress bar and allows users to:
- View all tasks with their details
- Check/uncheck tasks to mark completion
- Add new missions through a comprehensive form
- Track progress visually
- Organize tasks by priority and category

### Calendar Widget (`CalendarWidget.tsx`)

**Status**: ✅ Fully implemented with monthly calendar functionality

**Features**:
- **Monthly Calendar View**: Full calendar grid with navigation
- **Event Display**: Shows events, milestones, reminders, and tasks on calendar days
- **Event Types**: Color-coded event types (event, milestone, reminder, task)
- **Priority System**: Visual priority indicators with border colors
- **Navigation**: Previous/next month navigation and "Today" button
- **Event Details**: Click events to view detailed information
- **Upcoming Events**: List of upcoming events below the calendar
- **Responsive Design**: Large widget (16x12) with comprehensive calendar view

**Calendar Features**:
- **Month Navigation**: Navigate between months with arrow buttons
- **Today Highlight**: Current day is highlighted in blue
- **Event Indicators**: Events shown as colored blocks on calendar days
- **Event Overflow**: Shows "+X more" for days with many events
- **Today Button**: Quick navigation to current month

**Event Properties**:
- **Title** - Event name
- **Date** - Event date
- **Time** - Event time (optional)
- **Location** - Event location (optional)
- **Type** - Event, milestone, reminder, or task
- **Priority** - High, Medium, or Low priority
- **Description** - Detailed event description

**Event Types**:
- **Event** (Blue) - General events and meetings
- **Milestone** (Purple) - Important project milestones
- **Reminder** (Yellow) - Personal reminders and appointments
- **Task** (Green) - Task-related calendar items

**API Integration**:
- **Get Monthly Calendar**: `GET /api/calendar/monthly?year={year}&month={month}`
- Ready for backend integration
- Currently uses dummy data with realistic calendar events
- Prepared for real API calls (commented out)

**Dummy Data**:
- 6 sample events across different types and priorities
- Events spread across the month for realistic display
- Various event types (meetings, appointments, milestones, tasks)
- Different locations and time slots

**Usage**:
The calendar widget provides comprehensive calendar functionality:
- View monthly calendar with all events
- Navigate between months
- Click events to view detailed information
- See upcoming events list
- Track milestones and important dates
- Manage appointments and meetings

## 📋 Planned Widgets

### Task List Widget
- Daily task management and tracking
- Mission creation with detailed forms
- Progress visualization and goal tracking

### Calendar Widget
- Monthly calendar view and planning
- Visual representation of past performance
- Future planning with events and milestones

### Habit Tracker Widget
- Habit tracking with streak counting
- Statistics and insights
- Progress charts and improvement tracking

### Reminders Widget
- Quick reminder management
- Time-based alerts with countdown timers
- Priority levels and categories

### Item Tracker Widget
- Track individual metrics (weight, smoking, etc.)
- Simple data entry forms
- Progress visualization and historical charts

### Weather Widget
- Weather information display
- Current conditions and forecasts
- Location-based weather data

### Stats Widget
- Statistics and analytics display
- Data visualization and charts
- Performance tracking

### News Widget
- News feed display
- Category-based news filtering
- Real-time news updates

## 🏗️ Widget Development

### Creating New Widgets

1. **Create Component File**:
   ```typescript
   // src/components/widgets/NewWidget.tsx
   import { useState, useEffect } from 'react';
   import BaseWidget from './BaseWidget';
   
   interface NewWidgetProps {
     onRemove: () => void;
     config?: Record<string, any>;
     scheduledItem?: {
       id: string;
       title: string;
       // Add other properties as needed
     };
   }
   
   const NewWidget = ({ onRemove, config, scheduledItem }: NewWidgetProps) => {
     // Widget implementation
     return (
       <BaseWidget title="New Widget" icon="🔧" onRemove={onRemove}>
         {/* Widget content */}
       </BaseWidget>
     );
   };
   
   export default NewWidget;
   ```

2. **Add Configuration**:
   ```typescript
   // src/config/widgets.ts
   newWidget: {
     id: 'newWidget',
     title: 'New Widget',
     description: 'Description of the new widget',
     component: 'NewWidget',
     minSize: { w: 6, h: 4 },
     maxSize: { w: 12, h: 10 },
     defaultSize: { w: 8, h: 6 },
     deletable: true,
     resizable: true,
     category: 'productivity',
     icon: '🔧'
   }
   ```

3. **Update Dashboard**:
   ```typescript
   // src/components/Dashboard.tsx
   import NewWidget from './widgets/NewWidget';
   
   // In renderWidget function:
   case 'newWidget':
     return (
       <NewWidget
         onRemove={() => removeWidget(widget.id)}
         config={widget.config}
         scheduledItem={widget.scheduledItem}
       />
     );
   ```

4. **Mark as Implemented**:
   ```typescript
   // src/config/widgets.ts
   export const getImplementedWidgets = (): WidgetConfig[] => {
     return [
       WIDGET_CONFIGS.webSearch,
       WIDGET_CONFIGS.allSchedules,
       WIDGET_CONFIGS.newWidget, // Add this line
     ];
   };
   ```

### Widget Best Practices

1. **Use BaseWidget**: Always wrap your widget content in `BaseWidget`
2. **Handle Loading States**: Show loading indicators while fetching data
3. **Error Handling**: Provide graceful error states with retry options
4. **Responsive Design**: Ensure widgets work well at different sizes
5. **TypeScript**: Use proper typing for props and data
6. **API Integration**: Prepare for real API calls with dummy data fallbacks

### Widget Configuration

Each widget can receive configuration through the `config` prop:
```typescript
interface WidgetConfig {
  // Common configuration options
  showCompleted?: boolean;
  maxItems?: number;
  refreshInterval?: number;
  
  // Widget-specific options
  [key: string]: any;
}
```

### Scheduled Item Integration

Widgets can receive scheduled item data through the `scheduledItem` prop:
```typescript
interface ScheduledItem {
  id: string;
  title: string;
  type: string;
  frequency: string;
  category?: string;
  importance?: 'High' | 'Medium' | 'Low';
  alarm?: string;
  searchQuery?: string;
  config?: Record<string, any>;
}
```

## 🔧 API Integration

### Current Status
- All widgets are prepared for API integration
- Dummy data is used for development
- API endpoints are defined in `src/config/api.ts`

### Switching to Real APIs
1. Uncomment API imports in widget components
2. Replace dummy data calls with real API calls
3. Update error handling for network requests
4. Test with real backend endpoints

## 📊 Widget Statistics

- **Implemented**: 4 widgets
- **Planned**: 6 widgets
- **Total**: 10 widget types
- **Categories**: Productivity, Information, Entertainment, Utilities

## 🎯 Next Steps

1. Implement remaining planned widgets
2. Add real API integration
3. Implement real-time updates
4. Add widget data caching
5. Create widget themes and customization
6. Add analytics and performance tracking 