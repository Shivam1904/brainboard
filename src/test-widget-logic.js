// Test script for widget logic
// This file can be run in the browser console to test the widget processing logic

// Sample data structure for testing
const sampleAllWidgets = [
  {
    id: '1',
    widget_type: 'allSchedules',
    title: 'All Schedules',
    widget_config: {
      visibility: true
    },
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    id: '2',
    widget_type: 'aiChat',
    title: 'Brainy AI',
    widget_config: {
      visibility: false
    },
    created_at: '2024-01-01T00:00:00Z'
  }
];

const sampleTodayWidgets = [
  {
    id: 'task1',
    widget_id: 'task1',
    title: 'Advanced Task 1',
    widget_type: 'todo-task',
    importance: 0.8,
    category: 'productivity',
    widget_config: {
      include_tracker_details: true,
      include_alarm_details: true,
      include_progress_details: true,
      include_websearch_details: true,
      search_query_detailed: 'advanced task 1 research',
      milestones: [
        { text: 'Milestone 1', due_date: '2024-01-15' } // Assuming today is 2024-01-10
      ]
    },
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 'task2',
    widget_id: 'task2',
    title: 'Regular Task 1',
    widget_type: 'todo-task',
    importance: 0.5,
    category: 'productivity',
    widget_config: {
      include_tracker_details: false,
      include_alarm_details: false,
      include_progress_details: false,
      include_websearch_details: false
    },
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    id: 'task3',
    widget_id: 'task3',
    title: 'Regular Task 2',
    widget_type: 'todo-task',
    importance: 0.6,
    category: 'health',
    widget_config: {
      include_tracker_details: false,
      include_alarm_details: true, // Only alarm, not all criteria
      include_progress_details: false,
      include_websearch_details: true,
      search_query_detailed: 'health research'
    },
    created_at: '2024-01-01T00:00:00Z'
  }
];

// Mock functions for testing
const getWidgetConfig = (widgetType) => {
  const configs = {
    'allSchedules': {
      title: 'All Schedules',
      description: 'Manage all widget schedules',
      defaultSize: { w: 12, h: 15 },
      minSize: { w: 12, h: 10 },
      maxSize: { w: 30, h: 36 }
    },
    'aiChat': {
      title: 'Brainy AI',
      description: 'AI-powered chat widget',
      defaultSize: { w: 14, h: 14 },
      minSize: { w: 8, h: 8 },
      maxSize: { w: 20, h: 24 }
    },
    'advanced-single-task': {
      title: 'Advanced Single Task',
      description: 'Advanced single task with tracker, alarm, and progress details',
      defaultSize: { w: 12, h: 14 },
      minSize: { w: 8, h: 6 },
      maxSize: { w: 18, h: 20 }
    },
    'todo-task': {
      title: 'Task List',
      description: 'Manage daily tasks and to-dos',
      defaultSize: { w: 12, h: 15 },
      minSize: { w: 8, h: 8 },
      maxSize: { w: 30, h: 36 }
    },
    'websearch': {
      title: 'Web Search',
      description: 'AI-powered web search and summaries',
      defaultSize: { w: 11, h: 14 },
      minSize: { w: 8, h: 8 },
      maxSize: { w: 20, h: 24 }
    }
  };
  return configs[widgetType];
};

const findOptimalPosition = (widgetType, existingWidgets) => {
  // Simple position calculation for testing
  return { x: existingWidgets.length * 2, y: 0 };
};

// Test the widget processing logic
function testWidgetLogic() {
  console.log('=== Testing Widget Logic ===');
  
  const uiWidgets = [];
  const viewWidgetTypes = ['allSchedules', 'aiChat'];
  
  // Step 1: Handle view widgets
  console.log('\n1. Processing view widgets...');
  viewWidgetTypes.forEach(widgetType => {
    const allWidgetsViewWidget = sampleAllWidgets.find(w => w.widget_type === widgetType);
    const isVisible = allWidgetsViewWidget?.widget_config?.visibility;
    
    console.log(`  ${widgetType}: visibility = ${isVisible}`);
    
    if (isVisible) {
      const config = getWidgetConfig(widgetType);
      const position = findOptimalPosition(widgetType, uiWidgets);
      
      const viewWidget = {
        id: `auto-${widgetType}`,
        daily_widget_id: `auto-${widgetType}`,
        widget_id: allWidgetsViewWidget?.id || '',
        widget_type: widgetType,
        title: config.title,
        layout: {
          i: `auto-${widgetType}`,
          x: position.x,
          y: position.y,
          w: config.defaultSize.w,
          h: config.defaultSize.h,
        }
      };
      
      uiWidgets.push(viewWidget);
      console.log(`  ✓ Added ${widgetType} widget`);
    }
  });
  
  // Step 2: Process today's widgets
  console.log('\n2. Processing today\'s widgets...');
  const advancedSingleTaskWidgets = [];
  const regularTaskWidgets = [];
  const webSearchWidgets = [];
  
  sampleTodayWidgets.forEach((widget) => {
    const widgetConfig = widget.widget_config || {};
    
    // Check criteria
    const hasTrackerDetails = widgetConfig.include_tracker_details === true;
    const hasAlarmDetails = widgetConfig.include_alarm_details === true;
    const hasProgressDetails = widgetConfig.include_progress_details === true;
    
    // Check if milestone is coming up in 7 days (mock: assume milestone is upcoming)
    const hasUpcomingMilestone = hasProgressDetails && widgetConfig.milestones && 
      Array.isArray(widgetConfig.milestones) && widgetConfig.milestones.length > 0;
    
    console.log(`  ${widget.title}:`, {
      hasTrackerDetails,
      hasAlarmDetails,
      hasProgressDetails,
      hasUpcomingMilestone
    });
    
    // Determine widget type
    if (hasTrackerDetails && hasAlarmDetails && hasProgressDetails && hasUpcomingMilestone) {
      console.log(`  ✓ Creating advanced single task widget for: ${widget.title}`);
      const config = getWidgetConfig('advanced-single-task');
      const position = findOptimalPosition('advanced-single-task', uiWidgets);
      
      const advancedWidget = {
        ...widget,
        daily_widget_id: widget.id,
        widget_type: 'advanced-single-task',
        title: `Advanced: ${widget.title}`,
        layout: {
          i: widget.id,
          x: position.x,
          y: position.y,
          w: config.defaultSize.w,
          h: config.defaultSize.h,
        }
      };
      
      advancedSingleTaskWidgets.push(advancedWidget);
    } else {
      console.log(`  ✓ Adding to regular task list: ${widget.title}`);
      regularTaskWidgets.push(widget);
    }
    
    // Check for web search widget
    if (widgetConfig.include_websearch_details === true) {
      console.log(`  ✓ Creating web search widget for: ${widget.title}`);
      const config = getWidgetConfig('websearch');
      const position = findOptimalPosition('websearch', uiWidgets);
      
      const webSearchWidget = {
        id: `websearch-${widget.id}`,
        daily_widget_id: `websearch-${widget.id}`,
        widget_id: widget.widget_id,
        widget_type: 'websearch',
        title: `Web Search: ${widget.title}`,
        layout: {
          i: `websearch-${widget.id}`,
          x: position.x,
          y: position.y,
          w: config.defaultSize.w,
          h: config.defaultSize.h,
        }
      };
      
      webSearchWidgets.push(webSearchWidget);
    }
  });
  
  // Step 3: Add advanced single task widgets
  console.log(`\n3. Adding ${advancedSingleTaskWidgets.length} advanced single task widgets`);
  uiWidgets.push(...advancedSingleTaskWidgets);
  
  // Step 4: Create combined task list
  console.log(`\n4. Creating combined task list with ${regularTaskWidgets.length} regular tasks`);
  if (regularTaskWidgets.length > 0) {
    const config = getWidgetConfig('todo-task');
    const position = findOptimalPosition('todo-task', uiWidgets);
    
    const taskListWidget = {
      id: 'task-list-combined',
      daily_widget_id: 'task-list-combined',
      widget_type: 'todo-task',
      title: 'Task List',
      layout: {
        i: 'task-list-combined',
        x: position.x,
        y: position.y,
        w: config.defaultSize.w,
        h: config.defaultSize.h,
      },
      widget_config: {
        combined_tasks: regularTaskWidgets.map(w => ({
          id: w.id,
          title: w.title,
          importance: w.importance,
          category: w.category
        }))
      }
    };
    
    uiWidgets.push(taskListWidget);
  }
  
  // Step 5: Add web search widgets
  console.log(`\n5. Adding ${webSearchWidgets.length} web search widgets`);
  uiWidgets.push(...webSearchWidgets);
  
  // Results
  console.log('\n=== Results ===');
  console.log(`Total widgets created: ${uiWidgets.length}`);
  console.log('Widget types:');
  uiWidgets.forEach(widget => {
    console.log(`  - ${widget.widget_type}: ${widget.title}`);
  });
  
  return uiWidgets;
}

// Run the test
const results = testWidgetLogic();
console.log('\nTest completed! Check the results above.'); 