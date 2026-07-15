# Backend

Backend FastAPI para o Security QA MCP.

## Estrutura

- app/core: configuração, banco e segurança
- app/domain: modelos e portas de repositório
- app/application: casos de uso
- app/infrastructure: implementações de repositório
- app/interfaces/api: rotas e schemas

## Execução

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
