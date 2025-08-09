# Calendar Widget Enhancement Gameplan

## Current Implementation Analysis

### What's Already Working:
- ✅ Basic calendar grid with month navigation
- ✅ Todo completion tracking (progress bar: completed/total)
- ✅ Basic streak detection (flame icon with day count)
- ✅ Milestone display (trophy icon)
- ✅ Event display with icons (circle, checkcircle, trophy)
- ✅ API integration with real data
- ✅ Modal for event details

### Current Data Structure:
- `CalendarDay` has: `todosCompleted`, `todosTotal`, `habitStreak`, `milestones`
- `CalendarEvent` has: `activity_data`, `widget_config`, `type`, `priority`
- API provides: `activity_data` with status/progress, `widget_config` with streaks/milestones

## Enhanced Requirements

### 1. Todo Completion Visualization (CIRCLE DESIGN)
**Current**: Simple progress bar
**New**: Circular progress indicator
- **Circle Design**: 
  - Center: Date number
  - Arc segments: Each todo gets its own arc segment
  - Colors: Use category colors from `widget_config.category_color` or default colors
  - Filled arcs: Completed todos
  - Empty arcs: Pending todos
  - Size: Responsive to number of todos (max 8 segments visible)

**Questions**:
- What should be the default category colors if not specified?
- Should we show category names on hover?
- Maximum number of arcs to display before overflow?

### 2. Enhanced Streak Visualization
**Current**: Simple flame icon with day count
**New**: Progressive streak visualization
- **Color Progression**: 
  - Day 1: Light orange (#FFB366)
  - Day 2: Medium orange (#FF9933)
  - Day 3: Dark orange (#FF8000)
  - Day 4-6: Darker shades
  - Day 7+: Darkest orange (#CC6600) + larger size
- **Multiple Streaks**: Show multiple flame icons for different widget categories
- **Category Colors**: Each streak flame uses its widget's category color

**Questions**:
- Should we track streak history or just current streak?
- How to handle multiple widgets with different streak types?
- Should we show streak break indicators?

### 3. Top 3 Tasks Feature
**Current**: Not implemented
**New**: Thumbs up indicator for top 3 completion
- **Data Source**: Check `activity_data.top_3_tasks` or `activity_data.top_tasks`
- **Logic**: Count completed tasks in top 3 list
- **Display**: Thumbs up icon (👍) when all top 3 are completed
- **Position**: Bottom right of each day cell

**Questions**:
- Where is the top 3 data stored in activity_data?
- Should we show partial completion (e.g., 2/3 completed)?
- Should this be configurable per widget?

### 4. Enhanced Milestone Display
**Current**: Basic trophy icon
**New**: Smart milestone visualization
- **Past Milestones**: Full purple color + checkmark
- **Future Milestones**: Light purple color
- **Data Source**: 
  - Future: `widget_config.milestones` array
  - Past: Check `activity_data.milestone_completed` or similar
- **Multiple Milestones**: Stack or group by widget

**Questions**:
- How to identify completed milestones in activity_data?
- Should we show milestone titles on hover?
- How to handle multiple milestones on same day?

## Technical Implementation Plan

### Phase 1: Fix Current Issues
1. **Type Safety**: Fix TypeScript errors in event mapping
2. **Null Safety**: Add proper null checks for calendarData
3. **Performance**: Optimize re-renders

### Phase 2: Enhanced Visualizations
1. **Circular Progress Component**: Create reusable SVG-based circle component
2. **Streak Color System**: Implement color progression logic
3. **Top 3 Detection**: Add logic to detect and display top 3 completion
4. **Milestone Enhancement**: Improve milestone display logic

### Phase 3: Polish & Optimization
1. **Responsive Design**: Ensure all elements work on different screen sizes
2. **Accessibility**: Add proper ARIA labels and keyboard navigation
3. **Performance**: Optimize for large datasets
4. **Testing**: Add unit tests for new components

## Data Structure Enhancements Needed

### CalendarDay Interface Updates:
```typescript
interface CalendarDay {
  // ... existing fields
  todosByCategory: Map<string, { completed: number, total: number }>;
  streaksByCategory: Map<string, number>;
  top3Completed: boolean;
  milestones: {
    future: CalendarEvent[];
    past: CalendarEvent[];
  };
}
```

### Helper Functions Needed:
```typescript
// Color utilities
const getCategoryColor = (category: string): string => { /* ... */ };
const getStreakColor = (day: number): string => { /* ... */ };

// Progress calculations
const calculateCircularProgress = (todos: TodoItem[]): ArcSegment[] => { /* ... */ };
const checkTop3Completion = (activityData: any): boolean => { /* ... */ };
```

## Questions for Clarification

1. **Category Colors**: What's the default color scheme for widget categories?
2. **Top 3 Data**: Where exactly is the top 3 tasks data stored in the API response?
3. **Streak Types**: Are there different types of streaks (daily, weekly, monthly)?
4. **Milestone Completion**: How do we determine if a milestone is completed?
5. **Performance**: What's the expected maximum number of widgets per day?
6. **Mobile Support**: Should the calendar be responsive for mobile devices?
7. **Accessibility**: Any specific accessibility requirements?
8. **Testing**: What's the testing strategy for these new features?

## Next Steps

1. **Confirm Data Structure**: Verify where top 3 and milestone completion data is stored
2. **Design Approval**: Get approval for the circular progress design
3. **Implementation Order**: Start with Phase 1 (fixes) then move to Phase 2
4. **Component Creation**: Create reusable components for circular progress and streak visualization
5. **Integration Testing**: Test with real API data