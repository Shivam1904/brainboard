# 🧠 Brainboard

An AI-powered dashboard with smart widgets for productivity and personal development.

## 🚀 Features

### ✅ **Implemented Widgets**
- **Web Search Widget** - Individual search widgets with unique queries and results
- **Task List Widget** - Daily task management with progress tracking and mission creation
- **All Schedules Widget** - Comprehensive schedule management for all widgets

### 🏗️ **Architecture**
- **Dashboard API** - Dynamic widget loading from server configuration
- **Two-Tier API System** - Dashboard-level configuration + Widget-level data fetching
- **TypeScript** - Full type safety with comprehensive interfaces
- **Responsive Design** - Grid-based layout with drag-and-drop functionality

### 📱 **Widget Management**
- **Dynamic Loading** - Widgets loaded based on server configuration
- **Individual Data Fetching** - Each widget fetches its own data
- **Schedule Management** - Complete CRUD operations for widget schedules
- **Type-Specific Forms** - Different forms for different widget types

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Grid System**: React Grid Layout
- **Icons**: Lucide React
- **State Management**: React Hooks

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd brainboard

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🏗️ Project Structure

```
src/
├── components/
│   ├── widgets/
│   │   ├── WebSearchWidget.tsx      # Web search functionality
│   │   ├── AllSchedulesWidget.tsx   # Schedule management
│   │   └── BaseWidget.tsx           # Base widget component
│   ├── Dashboard.tsx                # Main dashboard
│   └── AddWidgetButton.tsx          # Widget addition UI
├── config/
│   ├── api.ts                       # API configuration
│   ├── widgets.ts                   # Widget definitions
│   └── grid.ts                      # Grid layout configuration
├── types/
│   └── dashboard.ts                 # TypeScript interfaces
├── data/
│   └── dashboardDummyData.ts        # Dummy data for development
└── App.tsx                          # Main application
```

## 🎯 Widget Types

### **Web Search Widget**
- **Purpose**: Display web search results for scheduled queries
- **Features**: Individual search queries, unique results, image support
- **Size**: Medium (10x8)

### **Task List Widget**
- **Purpose**: Daily task management and mission tracking
- **Features**: Progress tracking, task completion, mission creation, priority system
- **Size**: Medium-Large (12x10)

### **All Schedules Widget**
- **Purpose**: Manage all widget schedules and configurations
- **Features**: CRUD operations, type-specific forms, category management
- **Size**: Large (16x12)

### **Planned Widgets**
- Calendar Widget
- Habit Tracker Widget
- Reminders Widget
- Item Tracker Widget
- Weather Widget
- Stats Widget
- News Widget

## 🔧 Configuration

### **API Configuration**
The system uses a two-tier API architecture:

1. **Dashboard API** (`/api/dashboard/today`) - Returns widget configuration
2. **Widget APIs** - Each widget fetches its own data

### **Widget Configuration**
Widgets are defined in `src/config/widgets.ts` with:
- Size constraints (min/max/default)
- Category classification
- Component mapping
- Icon and description

## 🚀 Development

### **Adding New Widgets**
1. Create widget component in `src/components/widgets/`
2. Add configuration to `src/config/widgets.ts`
3. Update Dashboard component to render the widget
4. Add to `getImplementedWidgets()` function

### **API Integration**
1. Uncomment API calls in widget components
2. Update `src/config/api.ts` with real endpoints
3. Implement backend API endpoints

### **Dummy Data**
- Located in `src/data/dashboardDummyData.ts`
- Provides realistic test data for development
- Easy to extend for new widget types

## 📋 Widget Schedule Management

The All Schedules widget supports:

### **Widget Types**
- `userTask` - Tasks with importance levels
- `userHabit` - Habits with alarms and importance
- `itemTracker` - Metric tracking
- `webSearch` - Web search queries
- `alarm` - Time-based alarms
- `calendar` - Calendar widgets
- `weatherWig` - Weather information
- `statsWidget` - Statistics display
- `newsWidget` - News feeds

### **Schedule Properties**
- **Title** - Widget name
- **Type** - Widget type
- **Frequency** - Schedule frequency (daily, weekly-2, hourly, etc.)
- **Category** - Organization category (health, finance, etc.)
- **Importance** - Priority level (High, Medium, Low)
- **Alarm** - Time specifications
- **Search Query** - For web search widgets

## 🎨 UI/UX Features

- **Responsive Grid Layout** - Drag and drop widget positioning
- **Loading States** - Professional loading indicators
- **Error Handling** - Graceful error states with retry options
- **Modal Forms** - Clean form interfaces for editing
- **Category Colors** - Visual organization with color coding
- **Type-Specific Forms** - Dynamic forms based on widget type

## 🔮 Future Enhancements

- [ ] Real-time updates
- [ ] Widget data caching
- [ ] Offline support
- [ ] User preferences
- [ ] Widget themes
- [ ] Advanced scheduling
- [ ] Analytics dashboard
- [ ] Mobile optimization

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Brainboard** - Organize your digital life with AI-powered widgets! 🧠✨
