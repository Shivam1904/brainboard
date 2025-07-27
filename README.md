# 🧠 Brainboard

An AI-powered modular productivity dashboard with smart widgets for managing tasks, summaries, and automation.

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd brainboard
   ```

2. **Set up Node.js environment:**
   ```bash
   # Using nvm (recommended)
   nvm use 18
   # Or install Node.js 18+ if you don't have nvm
   ```

3. **Set up Python environment:**
   ```bash
   # Using conda (recommended)
   conda create -n brainboard python=3.10
   
   # Activate the environment (you'll need to do this each time)
   conda activate brainboard
   # OR if conda activate doesn't work:
   source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh && conda activate brainboard
   ```

4. **Install dependencies:**
   ```bash
   # Install root dependencies (needed for concurrently)
   npm install
   
   # Install frontend dependencies
   cd apps/frontend && npm install && cd ../..
   
   # Install backend dependencies (ensure conda environment is activated)
   cd apps/backend && conda env update -f environment.yml && cd ../..
   ```

5. **Set up environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```bash
   # Required for AI features
   OPENAI_API_KEY=your-openai-api-key
   SERPER_API_KEY=your-serper-api-key
   
   # Optional: AWS credentials for DynamoDB (can use local development without)
   AWS_REGION=us-east-1
   ```

6. **Start development servers:**
   ```bash
   # Ensure conda environment is activated first
   conda activate brainboard
   # OR: source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh && conda activate brainboard
   
   npm run dev
   ```
   This starts both frontend and backend concurrently:
   - Frontend: http://localhost:5173 (or next available port like 5174)
   - Backend: http://localhost:8000

## ⚠️ Local Development Notes

- **AWS Credentials**: Not required for local development. The backend will run in local mode without DynamoDB
- **PostCSS**: Uses `.cjs` extension for compatibility with ES modules
- **Port Conflicts**: If port 5173 is in use, Vite will automatically use the next available port
- **Conda Environment**: Always ensure your conda environment is activated before running backend commands

## 📁 Project Structure

```
brainboard/
├── apps/
│   ├── frontend/          # React + Vite frontend
│   └── backend/           # FastAPI backend
├── infra/                 # AWS CDK infrastructure
└── ideas/                 # Project documentation
```

## 🛠️ Development

### Prerequisites
- **Node.js 18+** (recommended: use [nvm](https://github.com/nvm-sh/nvm) for version management)
- **Python 3.10** (recommended: use [conda](https://docs.conda.io/en/latest/) for environment management)
- **Git**

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

### Project Structure
```
brainboard/
├── apps/
│   ├── frontend/          # React + Vite frontend
│   └── backend/           # FastAPI backend
├── infra/                 # AWS CDK infrastructure (for deployment)
└── ideas/                 # Project documentation
```

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

### Frontend (`apps/frontend/`)
- `npm run dev` - Start Vite development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Backend (`apps/backend/`)
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

## 🤝 Contributing

1. Follow the coding guidelines in `.github/instructions/`
2. Each widget should be self-contained and follow the established patterns
3. Test your changes locally before submitting
4. Run `npm run lint` to check code style

## 📄 License

MIT
