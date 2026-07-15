# ADR 0001: Escolha do stack backend

## Status
Accepted

## Context
O projeto precisa de uma API rápida para expor scans, findings e integrações, com forte separação entre domínio e infraestrutura.

## Decision
Usar FastAPI com SQLAlchemy 2 e uma estrutura em camadas inspirada em Clean Architecture.

## Consequences
- Desenvolvimento rápido e legível.
- Contratos explícitos com Pydantic.
- Facilidade de integração com testes e documentação OpenAPI.
