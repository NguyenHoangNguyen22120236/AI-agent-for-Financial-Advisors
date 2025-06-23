# AI Agent for Financial Advisors

An AI-powered assistant that integrates with **Gmail**, **Google Calendar**, and **HubSpot** to help financial advisors automate communications and client management.

---

## 🧰 Tech Stack

- **Backend:** FastAPI, Alembic, PostgreSQL (via Docker)
- **Frontend:** React
- **Integrations:** Google OAuth, HubSpot OAuth, OpenAI API

---

## 📁 Project Structure

```
AI-agent-for-Financial-Advisors/
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env
├── docker-compose.yml
└── README.md
```

---

## 🚀 Getting Started (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AI-agent-for-Financial-Advisors.git
cd AI-agent-for-Financial-Advisors
```

---

### 2. Start PostgreSQL with Docker

Make sure Docker is running. Start the PostgreSQL container:

```bash
docker-compose up -d
```

---

### 3. Backend Setup

#### a. Create Python Virtual Environment

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux
```

#### b. Install Dependencies

```bash
pip install -r requirements.txt
```

#### c. Create `.env` File

Create a `.env` file in the `backend/` directory with the following content:

```env
# Database credentials
POSTGRES_DB=advisor_db
POSTGRES_USER=advisor_user
POSTGRES_PASSWORD=advisor_pass

DATABASE_URL=postgresql+psycopg2://advisor_user:advisor_pass@localhost:5432/advisor_db

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# HubSpot OAuth
HUBSPOT_CLIENT_ID=your-hubspot-client-id
HUBSPOT_CLIENT_SECRET=your-hubspot-client-secret
HUBSPOT_REDIRECT_URI=http://localhost:8000/auth/hubspot/callback

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

> **Note:** Replace sensitive values with your actual credentials.

#### d. Run Alembic Migrations

```bash
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

#### e. Start FastAPI Backend

```bash
uvicorn app.main:app --reload
```

The backend will be available at [http://localhost:8000](http://localhost:8000).

---

### 4. Frontend Setup

#### a. Create `.env` File

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://127.0.0.1:8000
```

#### b. Install Dependencies

```bash
cd ../frontend
npm install
```

#### c. Start the React App

```bash
npm start
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

---

## 🔗 OAuth & API Keys

- **Google OAuth:** Set up credentials in Google Cloud Console.
- **HubSpot OAuth:** Register your app in HubSpot Developer Portal.
- **OpenAI API:** Get your API key from OpenAI.

Update the `.env` files with your credentials.

---

## 📝 Useful Commands

- **Start PostgreSQL:**  
  `docker-compose up -d`
- **Stop PostgreSQL:**  
  `docker-compose down`
- **Run Alembic migrations:**  
  `alembic upgrade head`
- **Start backend:**  
  `uvicorn app.main:app --reload`
- **Start frontend:**  
  `npm start` (in `frontend/`)

---

## 🛠️ Troubleshooting

- Ensure Docker is running for PostgreSQL.
- Check `.env` files for correct credentials.
- If ports are in use, update the `docker-compose.yml` and `.env` files accordingly.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📬 Contact

For questions, open an issue or contact the