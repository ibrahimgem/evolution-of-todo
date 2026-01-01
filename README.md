# Evolution of Todo - Multi-Phase Todo Application

A comprehensive todo application that evolves from a simple console app to a full-stack web application with modern cloud deployment.

## 🚀 Live Demo

**Phase II - Full-Stack Web Application:** [https://frontend-roan-delta-27.vercel.app](https://frontend-roan-delta-27.vercel.app)

---

## Phase I: In-Memory Python Console Todo App

A console-based todo application built with Python 3.13+ using only the standard library.

## Features

- Add new tasks with title and description
- View all tasks with status indicators
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks

## Running the Application

```bash
python src/todo_app.py
```

## Project Structure

```
src/
├── todo_app.py      # Main application entry point
├── models/
│   └── task.py      # Task data model
├── services/
│   └── task_service.py  # Task management service
└── cli/
    └── menu.py      # Console menu interface

tests/
├── unit/
│   ├── test_task.py
│   └── test_task_service.py
└── integration/
    └── test_todo_app.py
```

## Requirements

- Python 3.13+
- No external dependencies

---

## Phase II: Full-Stack Web Application

A production-ready web application with modern authentication and cloud deployment.

### 🌟 Features

**Frontend:**
- Premium glassmorphism UI design
- Light/Dark theme toggle
- Responsive design for all devices
- JWT authentication with secure token management
- Real-time task management (CRUD operations)
- Error boundaries for graceful error handling

**Backend:**
- FastAPI REST API
- PostgreSQL database with async SQLModel ORM
- JWT authentication with bcrypt password hashing
- Comprehensive error handling
- CORS configured for security
- Health check and monitoring endpoints

### 🔗 Live Application

- **Frontend:** [https://frontend-roan-delta-27.vercel.app](https://frontend-roan-delta-27.vercel.app)
- **API Documentation:** Available at `/docs` on the backend

### 🛠️ Technology Stack

**Frontend:**
- Next.js 14 with App Router
- React 18
- TypeScript 5
- Tailwind CSS
- Deployed on Vercel

**Backend:**
- Python 3.13
- FastAPI 0.115+
- SQLModel with asyncpg
- PostgreSQL (Neon Serverless)
- Deployed on Railway

### 📦 Project Structure

```
Phase-II-Full-Stack-Web-Application/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js app routes
│   │   ├── components/   # React components
│   │   ├── lib/          # API client & utilities
│   │   └── context/      # React context providers
│   └── public/           # Static assets
│
└── backend/              # FastAPI backend application
    ├── src/
    │   ├── main.py       # FastAPI application entry
    │   ├── models.py     # SQLModel database models
    │   ├── auth.py       # JWT authentication
    │   ├── database.py   # Database configuration
    │   └── routes/       # API route handlers
    └── requirements.txt  # Python dependencies
```

### 🚀 Local Development

**Frontend:**
```bash
cd Phase-II-Full-Stack-Web-Application/frontend
npm install
npm run dev
```

**Backend:**
```bash
cd Phase-II-Full-Stack-Web-Application/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### 📚 Documentation

- `DEPLOY_NOW.md` - Quick deployment guide
- `Hackathon-II-Todo-Spec-Driven-Development.md` - Complete specification

---

## 📝 License

MIT
