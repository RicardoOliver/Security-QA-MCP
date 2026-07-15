install:
	python -m pip install -r backend/requirements.txt
	cd frontend && npm install

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 3000

test:
	cd backend && pytest -q

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
