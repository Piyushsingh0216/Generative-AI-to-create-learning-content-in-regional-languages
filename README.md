# AI Learning Platform (Full Stack)

Production-ready starter platform for AI-assisted learning with:
- FastAPI backend (JWT auth, file extraction, translation, summary, questions, chatbot, analytics, admin)
- React + Vite + Material UI frontend (SaaS dashboard UI, responsive layout)
- PostgreSQL-ready SQLAlchemy models (SQLite fallback for local development)

## Tech Stack
- Frontend: React (Vite), Material UI, Axios, React Router, Context API
- Backend: FastAPI, Uvicorn, SQLAlchemy, JWT auth, OCR/document parsing, OpenAI-ready service
- AI/Data tools: `pdfplumber`, `python-docx`, `python-pptx`, `pytesseract`, `deep-translator`, `gTTS`, `openai`

## Project Structure
```text
backend/
  app/
    main.py
    routes/
    services/
    models/
    schemas/
    utils/
    uploads/
    audio/
  requirements.txt
  .env.example

frontend/
  src/
    components/
    context/
    layouts/
    pages/
    services/
    App.jsx
  package.json
  .env.example
```

## API Key Placeholders
The project includes placeholders and does not hardcode secrets.

```python
# ====== API KEY PLACEHOLDER ======
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
# =================================
```

```python
# ====== API KEY PLACEHOLDER ======
GOOGLE_TRANSLATE_API_KEY = "YOUR_API_KEY_HERE"
# =================================
```

```python
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
```

## Features Implemented
1. Authentication
- Email/password signup + login
- JWT token issuance and protected routes

2. File Upload and Text Extraction
- Supported: `.pdf`, `.docx`, `.pptx`, `.txt`, `.jpg`, `.png`
- Extractors: `pdfplumber`, `python-docx`, `python-pptx`, `pytesseract`
- Files stored in `backend/app/uploads/`

3. Multilingual Translation (8 languages)
- `en`, `hi`, `ta`, `te`, `mr`, `bn`, `gu`, `kn`
- Uses `deep-translator` (GoogleTranslator)

4. AI Summary Generation
- Short summary + bullet-point summary
- OpenAI integration with fallback logic when key is missing

5. AI Question Generation
- 5 short-answer questions
- 5 MCQs in structured JSON

6. Context-Aware Chatbot (Basic RAG)
- Uses extracted uploaded text as prompt context
- Per-request context retrieval from user upload record

7. Voice Assistant (Toggle)
- `gTTS` MP3 generation
- Audio files stored in `backend/app/audio/`
- Served by static `/audio/*` route

8. Dashboard (MUI)
- AppBar + Drawer layout
- Upload, translation, summary, questions, chatbot, audio playback, analytics sections
- Responsive cards and grid system

9. Learning Progress Tracking
- Upload history, time spent, topics learned, summaries generated
- Stored per user in DB

10. Admin Panel
- Total users
- Total uploads
- Total summaries
- AI usage action counts

## Backend Setup (Windows)
1. Open PowerShell in project root.
2. Create virtual env and install dependencies:
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
3. Create env file:
```powershell
copy .env.example .env
```
4. Edit `.env` and set:
- `JWT_SECRET_KEY`
- `DATABASE_URL` (PostgreSQL in production)
- `OPENAI_API_KEY` (optional but recommended)
- `TESSERACT_CMD` (Windows Tesseract path)

5. Run backend:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup (Windows)
1. In a new PowerShell terminal:
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```
2. Open `http://localhost:5173`

## Tesseract OCR (Windows)
Install Tesseract OCR, then set:
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Key API Endpoints
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/uploads/`
- `GET /api/uploads/history`
- `POST /api/ai/translate`
- `POST /api/ai/summarize`
- `POST /api/ai/questions`
- `POST /api/ai/chat`
- `GET /api/dashboard/overview`
- `POST /api/dashboard/time-spent`
- `GET /api/admin/stats`

## Database Schema
- SQL file: [`database_schema.sql`](./database_schema.sql)
- ORM models: `backend/app/models/*.py`

## Deployment (Render + Vercel)

### Render (Backend)
1. Push repository to GitHub.
2. Create a new Render Web Service.
3. Root directory: `backend`
4. Build command:
```bash
pip install -r requirements.txt
```
5. Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
6. Add environment variables from `backend/.env.example`.
7. Set `DATABASE_URL` to Render PostgreSQL URL.

### Vercel (Frontend)
1. Import same repository into Vercel.
2. Set root directory: `frontend`
3. Build command:
```bash
npm run build
```
4. Output directory: `dist`
5. Add environment variables:
- `VITE_API_URL=https://<your-render-backend>/api`
- `VITE_BACKEND_ORIGIN=https://<your-render-backend>`

## Notes
- Code avoids Tailwind CSS and uses only Material UI.
- All key integrations are modularized under `backend/app/services`.
- OpenAI usage is optional at runtime; fallback logic keeps app functional without a key.
