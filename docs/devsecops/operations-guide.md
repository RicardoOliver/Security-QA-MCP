# Guia operacional — Security QA MCP

## Execução local
1. Instale as dependências do backend:
   - `cd backend && pip install -r requirements.txt`
2. Instale as dependências do frontend:
   - `cd frontend && npm install`
3. Inicie o backend:
   - `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Inicie o frontend:
   - `cd frontend && npm run dev -- --host 0.0.0.0 --port 3000`

## Execução com Docker Compose
- `docker compose up --build`
- A API fica disponível em `http://localhost:8000`
- O frontend fica disponível em `http://localhost:3000`

## CI/CD
- O pipeline GitHub Actions valida backend e frontend automaticamente em cada push e pull request.
- O fluxo inclui instalação de dependências, testes e build.
