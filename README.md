# 🧠 Brainboard

An AI-powered modular productivity dashboard with smart widgets for managing tasks, summaries, and automation.

> [!TIP]
> For detailed architectural documentation, API specifications, and implementation guides, please see [PROJECT_DOCS.md](PROJECT_DOCS.md).

## 🚀 Features

### ✅ **Implemented Widgets**
- **Web Search Widget** - Individual search widgets with unique queries and results
- **Task List Widget** - Daily task management with progress tracking and mission creation
- **Calendar Widget** - Monthly calendar with events, milestones, and navigation
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
brainboard/
├── backend/           # FastAPI backend
├── src/               # React + Vite frontend
├── infra/             # AWS CDK infrastructure (for deployment)
└── ideas/             # Project documentation
```

## 🛠️ Development

### Prerequisites
- **Node.js 18+** (recommended: use [nvm](https://github.com/nvm-sh/nvm) for version management)
- **Python 3.10** (recommended: use [conda](https://docs.conda.io/en/latest/) for environment management)
- **Git**
- **DB Browser for SQLite** (optional): `brew install --cask db-browser-for-sqlite` for visual database management

### Environment Setup
This project uses specific versions for consistency:
- **Node.js**: 18+ (use `nvm use 18` if you have nvm)
- **Python**: 3.10 (create a dedicated conda environment)

### Important Notes
- **Always activate your conda environment** before installing backend dependencies or running the backend
- **Use the correct Node.js version** for frontend development
- **Keep environments isolated** to avoid dependency conflicts
- **AWS Credentials are optional** for local development - the app runs in local mode without DynamoDB
- **Root npm install required** for the `concurrently` package that runs both servers

### Getting API Keys
To enable full functionality, you'll need:
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
- **Serper.dev API Key**: Get from [Serper.dev](https://serper.dev/)

## 🧩 Widget System

Widgets are self-contained modules that can be added to the dashboard:

- **Reminder Widget:** Task management with CRUD operations
- **Web Summary Widget:** AI-powered web search and summarization
- **Extensible:** Easy to add new widgets following the established patterns

## 📋 Available Scripts

### Root Level
- `npm run dev` - Start both frontend and backend in development mode
- `npm run build` - Build both applications for production
- `npm run test` - Run all tests
- `npm run lint` - Lint all code

### Frontend (Root)
- `npm run dev` - Start Vite development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Backend (`backend/`)
- `npm run dev` - Start FastAPI development server
- `npm run test` - Run Python tests
- `npm run lint` - Lint Python code

### Setup
No additional setup scripts needed - just follow the Quick Start guide above.

## 🔧 Environment Configuration

The project uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

```bash
# Backend Configuration
FASTAPI_ENV=development
FASTAPI_HOST=localhost
FASTAPI_PORT=8000
DATABASE_URL=sqlite:///./brainboard.db

# External APIs (required for full functionality)
OPENAI_API_KEY=your-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here

# AWS Configuration (optional for local development)
AWS_REGION=us-east-1
DYNAMODB_TABLE_REMINDERS=brainboard-reminders
DYNAMODB_TABLE_SUMMARIES=brainboard-summaries

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## 🚀 Deployment

The app is designed to deploy on AWS using CDK (located in `infra/`):
- Frontend: S3 + CloudFront
- Backend: Lambda + API Gateway
- Database: DynamoDB
- Auth: Cognito

*Deployment scripts coming soon for production use.*

## 🔧 Troubleshooting

### Common Issues

**PostCSS Error**: If you see "module is not defined in ES module scope"
- The `postcss.config.cjs` file should have `.cjs` extension (not `.js`)

**Backend Port Already in Use**:
```bash
lsof -ti:8000 | xargs kill -9
```

**Conda Environment Issues**:
```bash
# If conda activate doesn't work, try:
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate brainboard
```

**AWS Credentials Error**:
- For local development, ignore AWS credential errors - the app runs in local mode

**Frontend Port Changes**:
- Vite automatically finds available ports, so check terminal output for the correct URL

### Database Management

**View Database Visually**:
1. Install: `brew install --cask db-browser-for-sqlite`
2. Open "DB Browser for SQLite" app
3. Click "Open Database" → Navigate to `backend/brainboard.db`
4. Use "Browse Data" tab to view/edit your widgets and summaries

### **Calendar Widget**
- **Purpose**: Monthly calendar with events and milestones
- **Features**: Month navigation, event display, upcoming events, event details
- **Size**: Large (16x12)

### **All Schedules Widget**
- **Purpose**: Manage all widget schedules and configurations
- **Features**: CRUD operations, type-specific forms, category management
- **Size**: Large (16x12)

### **Planned Widgets**
- Habit Tracker Widget
- Reminders Widget
- Item Tracker Widget
- Weather Widget
- Stats Widget
- News Widget

**Database Features**:
- ✅ View all widgets and AI summaries
- ✅ Edit data directly by double-clicking cells
- ✅ Delete rows with right-click → "Delete Row"
- ✅ Export data to CSV/JSON
- ✅ Run custom SQL queries
- ✅ Search and filter data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Brainboard** - Organize your digital life with AI-powered widgets! 🧠✨
