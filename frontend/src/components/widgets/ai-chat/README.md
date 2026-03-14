# AI Chat Component System

A flexible component system for AI chat responses that allows dynamic rendering of interactive components based on AI responses.

## Overview

The AI chat component system consists of:
- **Component Registry**: Pre-built interactive components
- **Response Generator**: Smart response generation based on user input
- **Component Renderer**: Dynamic component rendering system

## Components

### Available Components

1. **TodoFormComponent** (`todo-form`)
   - Creates new todo items
   - Props: `onSubmit`, `onCancel`

2. **NameChangeComponent** (`name-change`)
   - Handles name change requests
   - Props: `currentName`, `onAccept`, `onCancel`

3. **ConfirmationComponent** (`confirmation`)
   - Confirmation dialogs
   - Props: `message`, `onConfirm`, `onCancel`

4. **DataDisplayComponent** (`data-display`)
   - Displays structured data
   - Props: `title`, `data`, `onAction`

5. **ProgressTrackerComponent** (`progress-tracker`)
   - Shows progress bars
   - Props: `current`, `total`, `label`, `onComplete`

6. **QuickActionsComponent** (`quick-actions`)
   - Grid of action buttons
   - Props: `actions`, `onAction`

## Usage

### Basic Component Usage

```tsx
import { renderAiChatComponent } from './AiChatComponents';

const component = {
  id: 'todo-1',
  type: 'todo-form',
  props: {}
};

const handleAction = (componentId: string, action: string, data: any) => {
  console.log('Action:', componentId, action, data);
};

renderAiChatComponent(component, handleAction);
```

### Adding New Components

1. Create the component:
```tsx
export const MyComponent: React.FC<MyComponentProps> = ({ onAction }) => {
  return (
    <div className="bg-muted/50 rounded-lg p-3 border">
      {/* Component content */}
    </div>
  );
};
```

2. Add to registry:
```tsx
export const AI_CHAT_COMPONENTS = {
  // ... existing components
  'my-component': MyComponent,
} as const;
```

3. Update component renderer if needed for special action handling.

## Response Generator

### Smart Response Patterns

The AI response generator recognizes patterns in user input:

- **Greetings**: "hi", "hello", "hey"
- **Todo Requests**: "todo", "task", "create todo"
- **Name Changes**: "change name", "rename"
- **Progress**: "progress", "status", "how much"
- **Data Requests**: "show data", "statistics"
- **Quick Actions**: "quick", "actions", "menu"
- **Confirmations**: "delete", "remove", "confirm"
- **Help**: "help", "what can you do"

### Adding New Patterns

```tsx
const RESPONSE_PATTERNS = {
  // ... existing patterns
  myPattern: {
    triggers: ['my', 'trigger', 'words'],
    thinkingSteps: [
      'Step 1...',
      'Step 2...'
    ],
    response: 'Response message',
    components: [
      {
        id: 'my-component-1',
        type: 'my-component',
        props: { /* component props */ }
      }
    ]
  }
};
```

### Follow-up Responses

The system handles follow-up responses when users interact with components:

```tsx
static generateFollowUpResponse(componentId: string, action: string, data: any): AIResponse {
  switch (componentId) {
    case 'todo-form-1':
      if (action === 'submit') {
        return {
          thinkingSteps: ['Processing...'],
          response: 'Todo created!',
          components: []
        };
      }
      break;
  }
  return DEFAULT_RESPONSE;
}
```

## Integration with Socket Service

When connected to WebSocket:
- Components send actions via socket
- Real-time responses from AI backend
- Automatic reconnection handling

When offline:
- Local response generation
- Simulated thinking steps
- Fallback interactions

## Styling

All components use consistent styling:
- `bg-muted/50` for component backgrounds
- `rounded-lg p-3 border` for containers
- `text-xs` for small text
- `bg-primary` for primary actions
- `bg-secondary` for secondary actions

## Best Practices

1. **Component Design**
   - Keep components focused and single-purpose
   - Use consistent prop patterns
   - Include proper TypeScript interfaces

2. **Response Patterns**
   - Use clear, descriptive triggers
   - Provide meaningful thinking steps
   - Include relevant components

3. **Action Handling**
   - Use descriptive action names
   - Handle all possible component states
   - Provide fallback responses

4. **User Experience**
   - Show thinking steps for complex operations
   - Provide clear feedback for actions
   - Use appropriate component types for different scenarios 