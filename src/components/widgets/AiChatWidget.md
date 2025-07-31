# AiChatWidget

A sophisticated AI chat widget with real-time thinking feedback and interactive components.

## Features

### 🚀 Real-time AI Communication
- WebSocket-based real-time communication with AI backend
- Live thinking process visualization
- Automatic reconnection on connection loss
- Connection status indicator

### 🤔 AI Thinking Visualization
- Real-time display of AI's thinking steps
- Animated progress indicators
- Step-by-step processing feedback
- Visual thinking state management

### 🎛️ Interactive Components
The AI can respond with various interactive components:

- **Buttons**: Action buttons for user interactions
- **Select Dropdowns**: Choice selection components
- **Text Inputs**: User input fields
- **Sliders**: Range selection components
- **Checkboxes**: Boolean selection components

### 💬 Chat Interface
- Modern chat bubble design
- Auto-scrolling to latest messages
- Timestamp display
- Typing indicators
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)

### 🔧 Technical Features
- Socket service integration
- Fallback simulation when offline
- Responsive design
- Accessibility features
- Error handling and recovery

## Usage

### Basic Usage
```tsx
import AiChatWidget from './widgets/AiChatWidget';

<AiChatWidget 
  widget={widgetData} 
  onRemove={handleRemove} 
/>
```

### Socket Integration
The widget automatically connects to the WebSocket service and handles:
- Connection management
- Message sending/receiving
- Real-time thinking updates
- Interactive component actions

### Interactive Components
When the AI responds with interactive components, users can:
1. Click buttons to trigger actions
2. Select options from dropdowns
3. Enter text in input fields
4. Adjust values with sliders
5. Toggle checkboxes

## API Integration

### WebSocket Events
- `connection`: Connection status updates
- `thinking`: Real-time thinking step updates
- `response`: AI response with interactive components
- `error`: Error handling

### Message Types
- `user`: User messages
- `ai`: AI responses
- `thinking`: AI thinking process

## Configuration

The widget is configured in `src/config/widgets.ts`:
```typescript
aiChat: { 
  id: 'aiChat',
  apiWidgetType: 'aiChat',
  title: 'Brainy AI',
  description: 'AI-powered chat widget',
  component: 'AIChatWidget',
  minSize: { w: 8, h: 8 },
  maxSize: { w: 20, h: 24 },
  defaultSize: { w: 14, h: 14 },
  deletable: true,
  resizable: true,
  category: 'information',
  icon: '🤖'
}
```

## Socket Service

The widget uses `src/services/socket.ts` for WebSocket communication:
- Automatic connection management
- Reconnection logic
- Event handling
- Message formatting

## Future Enhancements

- Voice input/output
- File upload support
- Rich media responses
- Custom interactive components
- Multi-language support
- Conversation history
- Export chat functionality 