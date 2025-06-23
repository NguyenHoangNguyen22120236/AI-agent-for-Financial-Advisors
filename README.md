# AI-agent-for-Financial-Advisors

.venv\Scripts\activate

docker-compose run --rm backend alembic revision --autogenerate -m "Initial tables"

docker-compose run --rm backend alembic upgrade head



uvicorn main:app --reload