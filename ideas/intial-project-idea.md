# 🧠 Brainboard — AI-Powered Planner with Smart Widgets

**Brainboard** is a modular productivity web app designed to give users a single place to track, manage, and automate all their boring or repetitive tasks. It features a dynamic grid system where users can add intelligent widgets powered by APIs and AI.

---

## 🧩 Core Idea

- The app runs as a **monorepo** with:
  - `apps/frontend` – React UI with grid and widgets
  - `apps/backend` – FastAPI service (reminder logic, AI agent logic)
  - `infra/` – AWS infrastructure (Lambda, DynamoDB, Cognito, etc.)

- The main UI is a **draggable, resizable grid layout**.
- Each widget is independent and pluggable, with isolated logic and styling.
- User layouts and widget state are persisted (per-user, using Cognito).

---

## ✨ Example Widgets

- ✅ **Reminder Widget**  
  A simple task manager with create/update/delete functionality and optional due dates.

- ✅ **Web Summary Widget**  
  An AI-powered agent that:
  - Accepts a freeform query
  - Performs a web search using **Serper.dev**
  - Summarizes results using **OpenAI GPT**
  - Returns a clean, digestible summary

---

## ⚙️ Tech Stack

### Frontend
- React (with Vite)
- Tailwind CSS
- `react-grid-layout`
- Zustand (state management)
- Hosted on AWS S3 + CloudFront

### Backend
- FastAPI (Python)
- Deployed on AWS Lambda via API Gateway
- Auth via Amazon Cognito
- Data stored in DynamoDB
- AI services via Serper.dev + OpenAI API

---

## 🧠 Cursor Agent Notes

When generating or editing code:
- All widgets live in `apps/frontend` and follow modular structure
- Reminder API is a basic authenticated CRUD service
- Summary API runs an async agent (search → summarize → store)
- Each widget connects to the backend via REST APIs
- Use Cognito JWT for per-user data access
- Handle async state (loading, error, ready) in frontend widgets
- Code should be extensible for future widgets

---

## ✅ Goals

- Clean, modular dashboard for managing personal productivity
- Intelligent widgets that combine automation with LLMs
- Easy to expand with new tools for reminders, planning, tracking, or summarizing

