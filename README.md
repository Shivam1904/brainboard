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
- **Backend**: FastAPI (Python)
- **Database**: SQLite (via SQLAlchemy + aiosqlite)

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd brainboard
```

### Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```
The backend will start at `http://localhost:8989`.
API Documentation: `http://localhost:8989/docs`

### Frontend Setup

```bash
# Return to root directory
cd ..

# Install dependencies
npm install

# Start development server
npm run dev
```
The frontend will start at `http://localhost:5173`.

## 🏗️ Project Structure

```
brainboard/
├── backend/           # FastAPI backend
│   ├── main.py        # Entry point
│   ├── config.py      # Configuration settings
│   ├── routes/        # API Endpoints
│   ├── services/      # Business logic
│   └── requirements.txt # Python dependencies
├── src/               # React + Vite frontend
└── ideas/             # Project documentation
```

## 🛠️ Development

### Prerequisites
- **Node.js 18+** (recommended: use [nvm](https://github.com/nvm-sh/nvm) for version management)
- **Python 3.10+**
- **Git**
- **DB Browser for SQLite** (optional): `brew install --cask db-browser-for-sqlite` for visual database management

### Environment Setup

#### Backend (`.env`)
Create a `.env` file in the `backend/` directory:
```env
# Backend Configuration
HOST=0.0.0.0
PORT=8989
RELOAD=True

# External APIs
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here
```

#### Frontend (`.env`)
Create a `.env` file in the root directory:
```env
VITE_API_BASE_URL=http://localhost:8989
```

### Important Notes
- **Always activate your virtual environment** (`source .venv/bin/activate`) before running the backend.
- **Keep environments isolated** to avoid dependency conflicts.

## 📋 Available Scripts

### Root Level
- `npm run dev` - Start Vite frontend
- `npm run build` - Build frontend for production
- `npm run test` - Run tests
- `npm run lint` - Lint code

### Backend (`backend/`)
- `python main.py` - Start FastAPI server
- `python init_db.py` - Initialize database
- `python generate_dummy_data.py` - Populate database with test data

## 🔧 Troubleshooting

### Common Issues

**Backend Port Already in Use**:
```bash
lsof -ti:8989 | xargs kill -9
```

**PostCSS Error**: If you see "module is not defined in ES module scope"
- The `postcss.config.cjs` file should have `.cjs` extension (not `.js`)

**Database Management**:
1. Install: `brew install --cask db-browser-for-sqlite`
2. Open "DB Browser for SQLite" app
3. Click "Open Database" → Navigate to `backend/brainboard.db`
4. Use "Browse Data" tab to view/edit your widgets and summaries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Brainboard** - Organize your digital life with AI-powered widgets! 🧠✨
