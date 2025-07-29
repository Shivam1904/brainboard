# TypeScript Types

This directory contains TypeScript interfaces and types for the Brainboard widget system.

## Overview

The types define the data structures for:
- **Widget Configuration**: Layout, settings, and metadata
- **Widget Data**: Specific data for each widget type (Todo, WebSearch, Calendar, etc.)
- **API Responses**: Backend API response structures
- **Type Guards**: Safe type checking for widget rendering

## Key Files

- `widgets.ts` - Main widget types and interfaces
- `dashboard.ts` - Dashboard-specific types
- `frequency.ts` - Frequency and scheduling types
- `index.ts` - Exports all types for easy importing

## Usage

```typescript
import { BaseWidget, TodoWidgetData, isTodoWidget } from '../types';

// Type-safe widget rendering
const renderWidget = (widget: BaseWidget) => {
  if (isTodoWidget(widget)) {
    // widget.data is now typed as TodoWidgetData
    return <TodoWidget data={widget.data} />;
  }
};
```

## Widget Types

- **Todo**: Task management with completion tracking
- **WebSearch**: Search queries and results
- **Calendar**: Events and scheduling
- **Alarm**: Time-based reminders
- **SingleItemTracker**: Progress tracking for individual items
- **AllSchedules**: Widget schedule management

For detailed API documentation, see the main project README. 