# Evolution of Todo - Multi-Phase Todo Application

A comprehensive todo application that evolves from a simple console app to an AI-powered chatbot with modern cloud deployment.

## 🚀 Live Demos

**Phase III - AI Chatbot:** [https://frontend-production-1395.up.railway.app](https://frontend-production-1395.up.railway.app)

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

## Phase III: AI-Powered Chatbot

An advanced todo application featuring conversational AI for natural language task management with MCP (Model Context Protocol) tools.

### 🌟 Features

**AI-Powered Interface:**
- Natural language task management
- Conversational AI assistant with OpenAI ChatKit
- Real-time chat with message streaming
- Conversation history and context preservation
- Task management via MCP tools (add_task, complete_task, update_task, delete_task)

**Frontend:**
- Premium glassmorphism UI design
- Light/Dark theme toggle
- Responsive design for all devices
- JWT authentication with secure token management
- Task overlay view for comprehensive task management
- Real-time task updates and notifications

**Backend:**
- FastAPI REST API with streaming support
- PostgreSQL database with async SQLModel ORM
- JWT authentication with bcrypt password hashing
- OpenAI Agents SDK integration
- MCP (Model Context Protocol) server with custom tools
- Comprehensive error handling and logging

**MCP Tools:**
- `add_task`: Create new tasks with optional due dates
- `complete_task`: Mark tasks as complete/incomplete
- `update_task`: Modify task details and due dates
- `delete_task`: Remove tasks from the system
- `list_tasks`: View all tasks with filtering options

### 🔗 Live Application

- **Frontend:** [https://frontend-production-1395.up.railway.app](https://frontend-production-1395.up.railway.app)
- **Backend API:** [https://backend-production-1395.up.railway.app](https://backend-production-1395.up.railway.app)
- **API Documentation:** Available at `/docs` on the backend

### 🛠️ Technology Stack

**Frontend:**
- Next.js 14 with App Router
- React 18
- TypeScript 5
- Tailwind CSS
- OpenAI ChatKit
- OpenAI Agents SDK
- Deployed on Railway

**Backend:**
- Python 3.13
- FastAPI 0.115+
- SQLModel with asyncpg
- OpenAI Agents SDK (openai>=1.0)
- MCP SDK (mcp>=1.0)
- PostgreSQL (Neon Serverless)
- Deployed on Railway

**AI/ML:**
- OpenAI GPT models via API
- MCP (Model Context Protocol) for tool integration
- Real-time message streaming
- Context-aware conversation management

### 📦 Project Structure

```
Phase-III-AI-Chatbot/
├── frontend/              # Next.js frontend with AI integration
│   ├── src/
│   │   ├── app/          # Next.js app routes (auth, chat, api)
│   │   ├── components/   # React components (ChatMessage, TaskList, etc.)
│   │   ├── lib/          # API client & utilities
│   │   ├── context/      # React context providers (AuthContext)
│   │   └── types/        # TypeScript type definitions
│   └── public/           # Static assets
│
└── backend/              # FastAPI backend with MCP server
    ├── src/
    │   ├── main.py       # FastAPI application entry
    │   ├── models.py     # SQLModel database models
    │   ├── auth.py       # JWT authentication
    │   ├── database.py   # Database configuration
    │   ├── routes/       # API route handlers (auth, chat, conversations)
    │   ├── mcp_tools/    # MCP tool implementations
    │   │   ├── add_task.py
    │   │   ├── complete_task.py
    │   │   ├── update_task.py
    │   │   ├── delete_task.py
    │   │   └── list_tasks.py
    │   ├── mcp/          # MCP server configuration
    │   └── agents/       # Agent helper functions
    └── requirements.txt  # Python dependencies
```

### 🚀 Local Development

**Frontend:**
```bash
cd Phase-III-AI-Chatbot/frontend
npm install
npm run dev
```

**Backend:**
```bash
cd Phase-III-AI-Chatbot/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

**Environment Variables:**
```
# Backend (.env)
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
NEON_DATABASE_URL=your-neon-url

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 📚 Documentation

- `specs/003-ai-chatbot/` - Complete Phase III specification
- `docs/` - Project documentation and architecture
- `Hackathon-II-Todo-Spec-Driven-Development.md` - Complete specification

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

## Phase I: In-Memory Python Console Todo App

A console-based todo application built with Python 3.13+ using only the standard library.

### 🛠️ Features

- Add new tasks with title and description
- View all tasks with status indicators
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks
- In-memory storage (no database required)

### 🚀 Running the Application

```bash
python src/todo_app.py
```

### 📦 Project Structure

```
Phase-I-Todo-Console-App/
├── src/
│   ├── todo_app.py      # Main application entry point
│   ├── models/
│   │   └── task.py      # Task data model
│   ├── services/
│   │   └── task_service.py  # Task management service
│   └── cli/
│       └── menu.py      # Console menu interface
│
└── tests/
    ├── unit/
    │   ├── test_task.py
    │   └── test_task_service.py
    └── integration/
        └── test_todo_app.py
```

### 📋 Requirements

- Python 3.13+
- No external dependencies

---

## 📝 License

MIT
