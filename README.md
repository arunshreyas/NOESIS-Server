Noesis API

Backend service for Noesis, a smart habit tracking platform that generates personalized habit plans using AI-assisted analysis of user-provided data.

This API handles authentication, user profiles, habit management, activity logging, and AI-powered recommendations.

🚀 Tech Stack

Framework: FastAPI (Python)

Database: PostgreSQL

ORM: SQLAlchemy

Auth: JWT (OAuth2 password flow)

AI Integration: OpenAI-compatible LLM API

Server: Uvicorn

✨ Core Features

User authentication (JWT-based)

Secure user profiles and onboarding data

Habit creation, tracking, and daily logs

Streak and history tracking

AI-assisted habit plan generation

Screenshot upload support (for user-provided screen time data)

Clean, RESTful API design

📁 Project Structure
app/
├── api/ # API routes
├── core/ # Config, security, settings
├── models/ # SQLAlchemy models
├── schemas/ # Pydantic schemas
├── services/ # Business logic (habits, AI, users)
├── db/ # Database session & utilities
├── main.py # Application entry point
tests/
.env.example
requirements.txt

⚙️ Setup & Installation
1️⃣ Clone the repository
git clone https://github.com/your-username/noesis-api.git
cd noesis-api

2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate # macOS/Linux
venv\Scripts\activate # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

🔐 Environment Variables

Create a .env file using .env.example as a reference.

DATABASE_URL=postgresql://user:password@localhost:5432/noesis
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

OPENAI_API_KEY=your-api-key

🗄️ Database Setup

Ensure PostgreSQL is running and a database is created.

Example:

CREATE DATABASE noesis;

The app uses SQLAlchemy models and manages relationships between users, habits, and logs.

▶️ Running the Server
uvicorn app.main:app --reload

The API will be available at:

http://localhost:8000

Interactive API docs:

Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc

🧠 AI Habit Recommendation Flow

User completes onboarding and provides:

Goals

Self-reported time usage

Optional screenshots

Backend aggregates relevant user context

AI service generates:

Personalized habit suggestions

Realistic schedules

Priority ordering

Results are stored and returned to the client

The AI acts as a decision-support system, not as an autonomous tracker.

🔗 Frontend

This API is designed to work with the Noesis mobile app, built using React Native.

👉 Companion repository:
Frontend: noesis-mobile (link here)

🛡️ Design Principles

Clear separation of concerns

Privacy-first (user-provided data only)

Predictable, versionable APIs

Simple, maintainable architecture (no unnecessary microservices)

📌 Status

This project is under active development and serves as a production-style portfolio project demonstrating backend design, API development, and AI integration.
