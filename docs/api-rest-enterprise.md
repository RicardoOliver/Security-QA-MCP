# Security QA MCP — Projeto da API REST Enterprise

## 1. Visão geral

A API REST do **Security QA MCP** é a interface pública para automações, console Web, pipelines CI/CD, integrações corporativas e clientes que não usam MCP diretamente. A API segue princípios REST, contratos versionados, autenticação forte, observabilidade nativa, respostas previsíveis e compatibilidade com OpenAPI 3.1.

| Item | Definição |
|---|---|
| Base URL produção | `https://api.security-qa-mcp.example.com` |
| Base URL sandbox | `https://sandbox-api.security-qa-mcp.example.com` |
| Versão atual | `v1` |
| Prefixo padrão | `/api/v1` |
| Formato | JSON UTF-8 |
| Datas | ISO 8601/RFC 3339 em UTC |
| IDs | UUID v4 ou ULID, conforme configuração da instalação |
| Autenticação | JWT Bearer, OAuth2/OIDC e tokens de serviço |
| Autorização | RBAC por tenant/projeto com extensões ABAC |
| Correlação | `X-Correlation-Id` obrigatório em clientes enterprise; gerado pelo gateway se ausente |

## 2. Convenções globais

### 2.1 Headers padrão

| Header | Direção | Obrigatório | Descrição |
|---|---:|---:|---|
| `Authorization: Bearer <token>` | Request | Sim, exceto health/public metadata | JWT de usuário, conta de serviço ou token OAuth2. |
| `Content-Type: application/json` | Request | Sim em payloads | Tipo do corpo enviado. |
| `Accept: application/json` | Request | Recomendado | Tipo de resposta esperado. |
| `X-Tenant-Id` | Request | Sim para tokens multi-tenant | Tenant operacional da chamada. |
| `X-Correlation-Id` | Request/Response | Recomendado | ID ponta a ponta para logs, auditoria e tracing. |
| `Idempotency-Key` | Request | Sim em comandos mutáveis críticos | Chave única de repetição segura. |
| `If-Match` | Request | Condicional | Controle otimista baseado em `version`/ETag para updates. |
| `ETag` | Response | Condicional | Versão de recurso para concorrência. |
| `X-RateLimit-Limit` | Response | Sim | Limite da janela atual. |
| `X-RateLimit-Remaining` | Response | Sim | Chamadas restantes na janela. |
| `X-RateLimit-Reset` | Response | Sim | Epoch seconds para reset da janela. |

### 2.2 Envelope de resposta

Consultas de item único retornam o recurso diretamente para reduzir ruído:

```json
{
  "id": "8b7f6d6e-29d4-4e4f-8b0a-7f7d7c0b4470",
  "tenant_id": "2f6502f9-b78e-4dd9-b0a6-4b8a6050db2b",
  "name": "Payments API",
  "created_at": "2026-07-14T10:15:30Z",
  "updated_at": "2026-07-14T10:15:30Z",
  "version": 1
}
```

Listagens usam envelope paginado:

```json
{
  "data": [],
  "page": {
    "limit": 50,
    "next_cursor": "eyJpZCI6...",
    "previous_cursor": null,
    "has_next": false
  },
  "links": {
    "self": "/api/v1/projects?limit=50",
    "next": null
  }
}
```

Erros seguem Problem Details compatível com RFC 9457:

```json
{
  "type": "https://docs.security-qa-mcp.example.com/errors/validation_failed",
  "title": "Validation failed",
  "status": 422,
  "code": "VALIDATION_FAILED",
  "detail": "The request payload contains invalid fields.",
  "correlation_id": "01J2WQ3Y4P7Y8X9Z0A1B2C3D4E",
  "errors": [
    {
      "field": "target.url",
      "message": "must be a valid HTTPS URL",
      "rule": "url.https_required"
    }
  ]
}
```

## 3. Versionamento

A API usa versionamento por caminho: `/api/v1`. Mudanças compatíveis podem ser publicadas sem trocar a versão. Mudanças incompatíveis exigem `/api/v2` e período de convivência.

### 3.1 Mudanças compatíveis

- Adicionar campos opcionais em responses.
- Adicionar endpoints novos.
- Adicionar valores novos a enums documentados como extensíveis.
- Ampliar limites máximos sem alterar semântica.

### 3.2 Mudanças incompatíveis

- Remover ou renomear campos.
- Tornar campo opcional em obrigatório.
- Alterar significado de status, enum ou filtro.
- Mudar modelo de autenticação sem fallback.

### 3.3 Depreciação

Endpoints obsoletos retornam headers:

```http
Deprecation: true
Sunset: Wed, 31 Dec 2027 23:59:59 GMT
Link: <https://docs.security-qa-mcp.example.com/migrations/v1-to-v2>; rel="deprecation"
```

## 4. Autenticação e autorização

### 4.1 JWT Bearer

Todos os endpoints protegidos aceitam JWT no header `Authorization`.

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

Claims mínimos:

| Claim | Tipo | Descrição |
|---|---|---|
| `iss` | string | Emissor confiável. |
| `sub` | string | Identidade humana, serviço ou integração. |
| `aud` | string/array | Deve conter `security-qa-mcp-api`. |
| `exp` | number | Expiração curta; recomendado até 15 minutos. |
| `iat` | number | Emissão. |
| `jti` | string | ID único do token para revogação e auditoria. |
| `tenant_id` | string | Tenant padrão quando aplicável. |
| `roles` | array | Papéis RBAC. |
| `permissions` | array | Permissões efetivas. |
| `scp` | string | Escopos OAuth2. |

Regras JWT:

- Assinatura RS256, ES256 ou EdDSA; HS256 não é recomendado para produção multi-tenant.
- Chaves publicadas por JWKS com rotação planejada.
- Tokens expirados retornam `401 TOKEN_EXPIRED`.
- Tokens válidos sem permissão retornam `403 FORBIDDEN`.

### 4.2 OAuth2/OIDC

Fluxos suportados:

| Fluxo | Uso recomendado |
|---|---|
| Authorization Code + PKCE | Console Web e clientes interativos. |
| Client Credentials | CI/CD, automações, workers e integrações server-to-server. |
| Token Exchange | Troca controlada entre gateway, MCP server e API. |
| Device Code | CLI em ambientes sem navegador local. |

Escopos principais:

| Scope | Permite |
|---|---|
| `projects:read` | Consultar projetos. |
| `projects:write` | Criar e alterar projetos. |
| `targets:read` | Consultar alvos. |
| `targets:write` | Criar e alterar alvos. |
| `scans:read` | Consultar scans e execuções. |
| `scans:write` | Criar, cancelar e reprocessar scans. |
| `findings:read` | Consultar achados e evidências. |
| `findings:write` | Alterar ciclo de vida dos achados. |
| `reports:read` | Baixar relatórios. |
| `reports:write` | Gerar relatórios. |
| `plugins:admin` | Administrar plugins. |
| `policies:admin` | Administrar policies e gates. |
| `audit:read` | Consultar trilhas de auditoria. |
| `admin:*` | Administração completa por tenant/plataforma. |

### 4.3 Permissões por recurso

Autorização efetiva combina:

1. Tenant ativo (`X-Tenant-Id` ou claim `tenant_id`).
2. Papel no projeto.
3. Permissão do endpoint.
4. Atributos do recurso, como ambiente `prod`, criticidade e ownership.
5. Condições de política, como segregação de função para aprovar exceções.

## 5. Paginação, ordenação e filtros

### 5.1 Paginação cursor-based

Parâmetros padrão:

| Parâmetro | Tipo | Default | Máximo | Descrição |
|---|---:|---:|---:|---|
| `limit` | integer | 50 | 200 | Quantidade de itens. |
| `cursor` | string | null | - | Cursor opaco retornado pela página anterior. |

### 5.2 Ordenação

`sort` aceita lista separada por vírgulas. Prefixo `-` indica descendente.

Exemplos:

- `sort=-created_at`
- `sort=severity,-created_at`
- `sort=status,name`

### 5.3 Filtros

Filtros usam query params tipados:

```http
GET /api/v1/findings?project_id=...&severity=critical,high&status=new,triage&created_from=2026-07-01T00:00:00Z&created_to=2026-07-14T23:59:59Z&limit=100
```

Convenções:

- Listas usam vírgula.
- Datas usam sufixos `_from` e `_to`.
- Busca textual usa `q`.
- Filtros desconhecidos retornam `400 UNKNOWN_FILTER`.
- Filtros sem permissão retornam `403 FILTER_FORBIDDEN` quando expõem dados sensíveis.

## 6. Validações globais

| Regra | Aplicação |
|---|---|
| Campos obrigatórios não podem ser `null`, vazios ou omitidos. |
| `name` deve ter 3 a 120 caracteres. |
| `slug` deve usar `^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$`. |
| URLs de targets devem usar `https://` por padrão; `http://` exige policy explícita. |
| IDs devem pertencer ao tenant ativo. |
| Payload máximo padrão: 1 MiB; upload de artefatos usa endpoints próprios. |
| Metadados JSONB têm limite de 32 KiB e chaves allowlisted. |
| Headers, cookies, tokens e secrets devem ser mascarados antes de persistência. |
| Updates devem enviar `If-Match` ou campo `version` em recursos versionados. |

## 7. Status HTTP

| Status | Uso |
|---:|---|
| `200 OK` | Consulta ou comando síncrono concluído. |
| `201 Created` | Recurso criado. Inclui `Location`. |
| `202 Accepted` | Processamento assíncrono aceito. |
| `204 No Content` | Operação sem corpo de resposta. |
| `304 Not Modified` | Cache/ETag sem alteração. |
| `400 Bad Request` | Query/header inválido ou sintaxe inválida. |
| `401 Unauthorized` | Ausência ou invalidade de autenticação. |
| `403 Forbidden` | Autenticado sem permissão. |
| `404 Not Found` | Recurso inexistente ou ocultado por tenant/permissão. |
| `409 Conflict` | Conflito de estado, duplicidade ou concorrência. |
| `412 Precondition Failed` | `If-Match` incompatível. |
| `415 Unsupported Media Type` | `Content-Type` não suportado. |
| `422 Unprocessable Entity` | Payload semanticamente inválido. |
| `429 Too Many Requests` | Rate limit excedido. |
| `500 Internal Server Error` | Erro inesperado. |
| `502 Bad Gateway` | Falha em dependência upstream. |
| `503 Service Unavailable` | Serviço indisponível/degradado. |
| `504 Gateway Timeout` | Timeout em dependência ou execução síncrona. |

## 8. Catálogo de endpoints

### 8.1 Health, metadata e OpenAPI

| Método | Endpoint | Auth | Descrição |
|---|---|---:|---|
| `GET` | `/health/live` | Não | Liveness probe. |
| `GET` | `/health/ready` | Não | Readiness probe. |
| `GET` | `/api/v1/meta` | Não | Metadados públicos da API. |
| `GET` | `/api/v1/openapi.json` | Não/Sim por ambiente | Documento OpenAPI 3.1. |
| `GET` | `/api/v1/docs` | Não/Sim por ambiente | Swagger UI/ReDoc. |

### 8.2 Identity e sessão

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/me` | autenticado | Retorna identidade, tenant e permissões efetivas. |
| `GET` | `/api/v1/tenants` | `admin:*` ou multi-tenant | Lista tenants acessíveis. |
| `POST` | `/api/v1/service-tokens` | `admin:*` | Cria token de serviço. |
| `DELETE` | `/api/v1/service-tokens/{token_id}` | `admin:*` | Revoga token de serviço. |

#### Response `GET /me`

```json
{
  "subject": "user_123",
  "tenant_id": "2f6502f9-b78e-4dd9-b0a6-4b8a6050db2b",
  "email": "ana@example.com",
  "display_name": "Ana Silva",
  "roles": ["tenant_admin"],
  "permissions": ["projects:read", "scans:write"],
  "expires_at": "2026-07-14T11:15:30Z"
}
```

### 8.3 Projetos

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/projects` | `projects:read` | Lista projetos. |
| `POST` | `/api/v1/projects` | `projects:write` | Cria projeto. |
| `GET` | `/api/v1/projects/{project_id}` | `projects:read` | Consulta projeto. |
| `PATCH` | `/api/v1/projects/{project_id}` | `projects:write` | Atualiza parcialmente projeto. |
| `DELETE` | `/api/v1/projects/{project_id}` | `projects:write` | Arquiva projeto por soft delete. |

#### DTO `CreateProjectRequest`

```json
{
  "name": "Payments Platform",
  "slug": "payments-platform",
  "description": "APIs e aplicações de pagamentos",
  "criticality": "high",
  "owner_team": "payments-core",
  "metadata": {
    "cost_center": "FIN-001"
  }
}
```

Validações:

- `name`: obrigatório, 3-120 caracteres.
- `slug`: obrigatório, único por tenant ativo.
- `criticality`: `low`, `medium`, `high` ou `critical`.
- `owner_team`: obrigatório em tenants com governança habilitada.

#### Response `ProjectResponse`

```json
{
  "id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "tenant_id": "2f6502f9-b78e-4dd9-b0a6-4b8a6050db2b",
  "name": "Payments Platform",
  "slug": "payments-platform",
  "criticality": "high",
  "owner_team": "payments-core",
  "created_at": "2026-07-14T10:15:30Z",
  "updated_at": "2026-07-14T10:15:30Z",
  "version": 1
}
```

### 8.4 Ambientes e alvos

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/environments` | `targets:read` | Lista ambientes do tenant. |
| `GET` | `/api/v1/projects/{project_id}/targets` | `targets:read` | Lista alvos do projeto. |
| `POST` | `/api/v1/projects/{project_id}/targets` | `targets:write` | Cadastra alvo. |
| `GET` | `/api/v1/targets/{target_id}` | `targets:read` | Consulta alvo. |
| `PATCH` | `/api/v1/targets/{target_id}` | `targets:write` | Atualiza alvo. |
| `DELETE` | `/api/v1/targets/{target_id}` | `targets:write` | Arquiva alvo. |
| `POST` | `/api/v1/targets/{target_id}/verify-ownership` | `targets:write` | Verifica autorização sobre domínio/API. |

#### DTO `CreateTargetRequest`

```json
{
  "name": "Payments Public API",
  "kind": "openapi",
  "environment_id": "b09ca4f4-1044-4f37-b0fd-43a4cc9c55ec",
  "base_url": "https://api.payments.example.com",
  "openapi_url": "https://api.payments.example.com/openapi.json",
  "scope": {
    "allow": ["https://api.payments.example.com/*"],
    "deny": ["https://api.payments.example.com/admin/*"],
    "max_depth": 5,
    "follow_external_redirects": false
  },
  "auth_profile_id": null,
  "tags": ["pci", "public"]
}
```

Validações:

- `kind`: `web`, `api_rest`, `api_graphql`, `openapi` ou `host`.
- `base_url`: HTTPS obrigatório salvo exceção aprovada.
- `scope.allow`: pelo menos um item.
- `scope.deny`: não pode conter wildcard global que invalide todo allow sem confirmação.
- Targets em `prod` exigem permissão adicional `targets:prod:write`.

### 8.5 Scans e execuções

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/scans` | `scans:read` | Lista solicitações de scan. |
| `POST` | `/api/v1/scans` | `scans:write` | Cria scan assíncrono. |
| `GET` | `/api/v1/scans/{scan_id}` | `scans:read` | Consulta scan. |
| `POST` | `/api/v1/scans/{scan_id}/cancel` | `scans:write` | Solicita cancelamento. |
| `POST` | `/api/v1/scans/{scan_id}/rerun` | `scans:write` | Reexecuta scan com configuração equivalente. |
| `GET` | `/api/v1/scans/{scan_id}/executions` | `scans:read` | Lista tentativas de execução. |
| `GET` | `/api/v1/scan-executions/{execution_id}` | `scans:read` | Consulta execução. |
| `GET` | `/api/v1/scan-executions/{execution_id}/events` | `scans:read` | Eventos/progresso da execução. |
| `GET` | `/api/v1/scan-executions/{execution_id}/logs` | `scans:read` | Logs operacionais redigidos. |

#### DTO `CreateScanRequest`

```json
{
  "project_id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "target_id": "1fd1db34-0763-4c02-af0c-84f892c7ab53",
  "name": "Release 2026.07.14 security gate",
  "trigger": "ci_cd",
  "profile": "api-baseline",
  "plugins": [
    { "plugin_key": "security-headers", "version": "^1.4.0" },
    { "plugin_key": "openapi-fuzzer", "version": "~2.1.0" }
  ],
  "execution": {
    "priority": "normal",
    "timeout_seconds": 3600,
    "max_retries": 1,
    "sandbox_level": "restricted"
  },
  "policy": {
    "gate_id": "d8fb0c26-5c62-4c27-97f1-a0109d76bc4d",
    "fail_on": ["critical", "high"]
  },
  "ci_context": {
    "provider": "github_actions",
    "repository": "org/payments",
    "commit_sha": "a3f1c...",
    "branch": "main",
    "run_id": "123456"
  }
}
```

Validações:

- `Idempotency-Key` obrigatório para `POST /scans`.
- `project_id` e `target_id` devem pertencer ao tenant ativo.
- `profile` deve existir e estar habilitado para o tipo de target.
- Plugins solicitados devem estar aprovados, compatíveis e permitidos pela policy.
- Scans em produção podem exigir janela autorizada e aprovação.

#### Response `ScanResponse` (`202 Accepted`)

```json
{
  "id": "35fe7e99-590c-45c4-b8f8-f4c3814743ff",
  "status": "queued",
  "project_id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "target_id": "1fd1db34-0763-4c02-af0c-84f892c7ab53",
  "latest_execution_id": "ea443177-bdde-4b4a-897e-0476de7ed557",
  "links": {
    "self": "/api/v1/scans/35fe7e99-590c-45c4-b8f8-f4c3814743ff",
    "execution": "/api/v1/scan-executions/ea443177-bdde-4b4a-897e-0476de7ed557",
    "events": "/api/v1/scan-executions/ea443177-bdde-4b4a-897e-0476de7ed557/events"
  },
  "created_at": "2026-07-14T10:15:30Z"
}
```

Filtros de scans:

| Filtro | Tipo | Exemplo |
|---|---|---|
| `project_id` | UUID | `project_id=...` |
| `target_id` | UUID | `target_id=...` |
| `status` | enum list | `status=queued,running` |
| `trigger` | enum | `trigger=ci_cd` |
| `created_from`, `created_to` | datetime | `created_from=2026-07-01T00:00:00Z` |
| `ci_commit_sha` | string | `ci_commit_sha=a3f1c` |

### 8.6 Findings, vulnerabilidades e evidências

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/findings` | `findings:read` | Lista achados canônicos. |
| `GET` | `/api/v1/findings/{finding_id}` | `findings:read` | Consulta achado. |
| `PATCH` | `/api/v1/findings/{finding_id}` | `findings:write` | Atualiza status, assignee ou metadados. |
| `POST` | `/api/v1/findings/{finding_id}/transitions` | `findings:write` | Executa transição de ciclo de vida. |
| `GET` | `/api/v1/findings/{finding_id}/instances` | `findings:read` | Lista ocorrências detectadas. |
| `GET` | `/api/v1/finding-instances/{instance_id}/evidences` | `findings:read` | Lista evidências. |
| `GET` | `/api/v1/evidences/{evidence_id}/download-url` | `findings:read` | URL temporária para baixar evidência. |

#### Response `FindingResponse`

```json
{
  "id": "b9d2b29c-d0e1-4ee5-93bb-65499a9d18fd",
  "project_id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "target_id": "1fd1db34-0763-4c02-af0c-84f892c7ab53",
  "title": "Missing Content-Security-Policy header",
  "severity": "medium",
  "status": "new",
  "confidence": "high",
  "cvss_score": 5.3,
  "cwe": ["CWE-693"],
  "owasp": ["OWASP-WEB-2021-A05"],
  "first_seen_at": "2026-07-14T10:20:00Z",
  "last_seen_at": "2026-07-14T10:20:00Z",
  "recommendation": "Configure a restrictive Content-Security-Policy header.",
  "fingerprint": "sha256:7d9c...",
  "version": 3
}
```

#### DTO `TransitionFindingRequest`

```json
{
  "to_status": "accepted_risk",
  "reason": "Legacy dependency scheduled for replacement",
  "expires_at": "2026-10-31T23:59:59Z",
  "approval_ticket": "SEC-1234"
}
```

Validações:

- Transições devem seguir máquina de estados configurada.
- `accepted_risk` exige justificativa, expiração e permissão de aprovação.
- `false_positive` exige evidência textual ou referência externa.
- `fixed` pode exigir confirmação por novo scan.

Filtros de findings:

| Filtro | Tipo |
|---|---|
| `project_id`, `target_id`, `scan_id`, `execution_id` | UUID |
| `severity` | `info,low,medium,high,critical` |
| `status` | `new,triage,accepted_risk,in_progress,fixed,false_positive,reopened,closed` |
| `confidence` | `low,medium,high` |
| `cwe`, `cve`, `owasp` | string/list |
| `first_seen_from`, `last_seen_to` | datetime |
| `q` | texto em título, descrição e endpoint afetado |

### 8.7 Policies e quality gates

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/policies` | `policies:admin` ou `scans:read` | Lista policies. |
| `POST` | `/api/v1/policies` | `policies:admin` | Cria policy. |
| `GET` | `/api/v1/policies/{policy_id}` | `policies:admin` ou `scans:read` | Consulta policy. |
| `PATCH` | `/api/v1/policies/{policy_id}` | `policies:admin` | Atualiza policy. |
| `POST` | `/api/v1/policies/{policy_id}/evaluate` | `scans:read` | Avalia gate contra execução/achados. |

#### DTO `CreatePolicyRequest`

```json
{
  "name": "Production release gate",
  "scope": "project",
  "project_id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "rules": [
    {
      "id": "no-critical-or-high",
      "effect": "deny",
      "when": {
        "finding.severity": ["critical", "high"],
        "finding.status": ["new", "triage", "reopened"]
      }
    }
  ],
  "default_effect": "allow"
}
```

### 8.8 Plugins

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/plugins` | `scans:read` | Lista plugins disponíveis. |
| `POST` | `/api/v1/plugins` | `plugins:admin` | Registra plugin. |
| `GET` | `/api/v1/plugins/{plugin_id}` | `scans:read` | Consulta plugin. |
| `POST` | `/api/v1/plugins/{plugin_id}/versions` | `plugins:admin` | Publica versão. |
| `POST` | `/api/v1/plugin-versions/{version_id}/approve` | `plugins:admin` | Aprova versão para uso. |
| `POST` | `/api/v1/plugin-versions/{version_id}/deprecate` | `plugins:admin` | Deprecia versão. |

#### DTO `RegisterPluginRequest`

```json
{
  "key": "security-headers",
  "name": "Security Headers Analyzer",
  "publisher": "Security QA MCP",
  "capabilities": ["http_headers", "passive_analysis"],
  "required_permissions": ["network:http:get"],
  "runtime": "container",
  "metadata": {
    "homepage": "https://plugins.example.com/security-headers"
  }
}
```

### 8.9 Relatórios e exportações

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/reports` | `reports:read` | Lista relatórios. |
| `POST` | `/api/v1/reports` | `reports:write` | Solicita geração assíncrona. |
| `GET` | `/api/v1/reports/{report_id}` | `reports:read` | Consulta relatório. |
| `GET` | `/api/v1/reports/{report_id}/download-url` | `reports:read` | URL temporária para download. |
| `POST` | `/api/v1/exports/sarif` | `reports:write` | Exporta SARIF sob demanda. |
| `POST` | `/api/v1/exports/audit-package` | `audit:read` | Gera pacote de auditoria. |

#### DTO `CreateReportRequest`

```json
{
  "kind": "executive",
  "project_id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "scan_execution_id": "ea443177-bdde-4b4a-897e-0476de7ed557",
  "format": "pdf",
  "locale": "pt-BR",
  "include_evidences": false,
  "filters": {
    "severity": ["critical", "high", "medium"]
  }
}
```

### 8.10 Integrações, pipelines e webhooks

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/integrations` | `admin:*` | Lista integrações. |
| `POST` | `/api/v1/integrations` | `admin:*` | Cria integração. |
| `PATCH` | `/api/v1/integrations/{integration_id}` | `admin:*` | Atualiza integração. |
| `POST` | `/api/v1/integrations/{integration_id}/test` | `admin:*` | Testa conectividade. |
| `GET` | `/api/v1/pipelines` | `scans:read` | Lista pipelines. |
| `POST` | `/api/v1/pipelines` | `scans:write` | Registra pipeline. |
| `POST` | `/api/v1/webhooks/{integration_key}` | assinatura HMAC | Recebe eventos externos. |

Webhooks de saída devem usar assinatura:

```http
X-Security-QA-Signature: sha256=<hmac>
X-Security-QA-Timestamp: 1784043330
X-Security-QA-Event: scan.completed
```

### 8.11 Auditoria e logs

| Método | Endpoint | Scope | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/audit-events` | `audit:read` | Consulta eventos de auditoria. |
| `GET` | `/api/v1/audit-events/{event_id}` | `audit:read` | Consulta evento específico. |
| `GET` | `/api/v1/logs` | `admin:*` ou `scans:read` | Consulta logs redigidos e filtrados. |
| `GET` | `/api/v1/metrics/security-summary` | `findings:read` | KPIs agregados de segurança. |

Filtros de auditoria:

- `actor_id`
- `resource_type`
- `resource_id`
- `action`
- `result=success,failure,denied`
- `created_from`, `created_to`
- `correlation_id`

## 9. DTOs canônicos

### 9.1 Tipos comuns

```json
{
  "Money": "não utilizado no escopo inicial",
  "Severity": ["info", "low", "medium", "high", "critical"],
  "ScanStatus": ["requested", "queued", "running", "canceling", "canceled", "succeeded", "failed", "timed_out"],
  "FindingStatus": ["new", "triage", "accepted_risk", "in_progress", "fixed", "false_positive", "reopened", "closed"],
  "EnvironmentKind": ["dev", "qa", "staging", "prod", "sandbox", "custom"],
  "TargetKind": ["web", "api_rest", "api_graphql", "openapi", "host"]
}
```

### 9.2 `ResourceMetadata`

```json
{
  "created_at": "2026-07-14T10:15:30Z",
  "created_by": "user_123",
  "updated_at": "2026-07-14T10:15:30Z",
  "updated_by": "user_123",
  "version": 1,
  "metadata": {}
}
```

### 9.3 `AuditEventResponse`

```json
{
  "id": "0f8f0572-38d4-48c5-afdf-7e40bc62f973",
  "tenant_id": "2f6502f9-b78e-4dd9-b0a6-4b8a6050db2b",
  "actor": {
    "id": "user_123",
    "type": "human",
    "display_name": "Ana Silva"
  },
  "action": "scan.create",
  "resource": {
    "type": "scan",
    "id": "35fe7e99-590c-45c4-b8f8-f4c3814743ff"
  },
  "result": "success",
  "source_ip": "203.0.113.10",
  "user_agent": "security-qa-cli/1.0",
  "correlation_id": "01J2WQ3Y4P7Y8X9Z0A1B2C3D4E",
  "created_at": "2026-07-14T10:15:30Z",
  "integrity_hash": "sha256:abcd..."
}
```

## 10. Tratamento de erros

### 10.1 Códigos de erro padronizados

| Código | HTTP | Quando ocorre |
|---|---:|---|
| `AUTHENTICATION_REQUIRED` | 401 | Token ausente. |
| `TOKEN_INVALID` | 401 | Token inválido, assinatura inválida ou audiência incorreta. |
| `TOKEN_EXPIRED` | 401 | Token expirado. |
| `FORBIDDEN` | 403 | Sem permissão efetiva. |
| `RESOURCE_NOT_FOUND` | 404 | Recurso inexistente ou inacessível. |
| `VALIDATION_FAILED` | 422 | Payload semanticamente inválido. |
| `UNKNOWN_FILTER` | 400 | Filtro não suportado. |
| `IDEMPOTENCY_CONFLICT` | 409 | Mesma chave com payload diferente. |
| `VERSION_CONFLICT` | 409 | Alteração concorrente detectada. |
| `PRECONDITION_FAILED` | 412 | ETag/`If-Match` incompatível. |
| `RATE_LIMIT_EXCEEDED` | 429 | Limite excedido. |
| `DEPENDENCY_UNAVAILABLE` | 503 | Fila, storage, scanner ou IdP indisponível. |
| `INTERNAL_ERROR` | 500 | Erro inesperado. |

### 10.2 Redação de dados sensíveis

Responses de erro nunca devem incluir:

- Tokens, cookies, secrets ou Authorization headers.
- Payloads completos com dados pessoais.
- Stack traces em produção.
- URLs pré-assinadas expiradas ou não mascaradas.

## 11. Rate limit e quotas

Rate limits são aplicados por tenant, sujeito, IP, client_id e endpoint. O gateway deve retornar `429` com `Retry-After`.

| Classe de endpoint | Limite inicial recomendado |
|---|---:|
| Leituras simples | 600 req/min por tenant |
| Listagens pesadas | 120 req/min por tenant |
| Criação de scans | 60 req/min por tenant |
| Geração de relatórios | 20 req/min por tenant |
| Downloads de evidência | 300 req/min por tenant |
| Webhooks recebidos | 300 req/min por integração |
| Login/token exchange | 30 req/min por sujeito/IP |

Exemplo:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1784043360
```

## 12. Idempotência

Endpoints mutáveis assíncronos e integrações devem aceitar `Idempotency-Key`.

Obrigatório em:

- `POST /api/v1/scans`
- `POST /api/v1/reports`
- `POST /api/v1/exports/*`
- `POST /api/v1/findings/{id}/transitions`
- `POST /api/v1/service-tokens`
- Recebimento de webhooks externos

Regras:

- Chave deve ter 16 a 128 caracteres.
- Escopo da chave: tenant + método + path + ator.
- Retenção mínima: 24 horas; recomendada: 7 dias para CI/CD.
- Mesmo payload retorna a resposta original.
- Payload diferente com mesma chave retorna `409 IDEMPOTENCY_CONFLICT`.

## 13. Auditoria

Toda ação relevante gera evento imutável em `audit_events`:

| Categoria | Exemplos |
|---|---|
| Autenticação | login, token exchange, token revogado, falha de autenticação. |
| Autorização | acesso negado, alteração de papel, mudança de permissão. |
| Configuração | criação/alteração de policy, integração, target, plugin. |
| Execução | scan criado, cancelado, reexecutado, finalizado, falhou. |
| Achados | mudança de status, aceite de risco, falso positivo, reabertura. |
| Dados sensíveis | download de evidência, geração de pacote de auditoria. |

Campos mínimos:

- `tenant_id`
- `actor_id`, `actor_type`
- `action`
- `resource_type`, `resource_id`
- `result`
- `before`, `after` ou diff redigido
- `source_ip`, `user_agent`, `client_id`
- `correlation_id`, `trace_id`
- `created_at`
- `integrity_hash`

## 14. Logs e observabilidade

### 14.1 Logs estruturados

Formato JSON recomendado:

```json
{
  "timestamp": "2026-07-14T10:15:30Z",
  "level": "INFO",
  "service": "api-server",
  "message": "scan created",
  "tenant_id": "2f6502f9-b78e-4dd9-b0a6-4b8a6050db2b",
  "project_id": "9f4a7d64-9e9f-4db8-a193-6a7a14cb3e85",
  "scan_id": "35fe7e99-590c-45c4-b8f8-f4c3814743ff",
  "correlation_id": "01J2WQ3Y4P7Y8X9Z0A1B2C3D4E",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "duration_ms": 42
}
```

Regras:

- Logs devem ser estruturados, correlacionáveis e sem secrets.
- `correlation_id` deve ser propagado para filas, workers e plugins.
- Erros devem registrar código interno, dependência e categoria, sem stack trace em resposta pública.
- Métricas devem incluir latência por endpoint, taxa de erro, filas, execução de scans, findings por severidade e rate limit.
- Traces OpenTelemetry devem cobrir gateway, API, banco, fila, workers e storage.

## 15. OpenAPI e Swagger

A especificação oficial deve ser publicada em `/api/v1/openapi.json` e validada em CI por testes de contrato. Swagger UI ou ReDoc podem ser expostos em `/api/v1/docs` em ambientes controlados.

### 15.1 Requisitos OpenAPI

- OpenAPI 3.1.
- Schemas JSON Schema com `additionalProperties: false` por padrão.
- `operationId` estável e único.
- Tags por domínio: `Projects`, `Targets`, `Scans`, `Findings`, `Reports`, `Plugins`, `Policies`, `Audit`.
- Security schemes para OAuth2 e Bearer JWT.
- Exemplos de request/response para todos os endpoints públicos.
- Respostas comuns referenciadas por componente: `ProblemDetails`, `PaginatedResponse`, `RateLimitHeaders`.

### 15.2 Exemplo mínimo de OpenAPI

```yaml
openapi: 3.1.0
info:
  title: Security QA MCP API
  version: 1.0.0
  description: Enterprise REST API for security scan orchestration and governance.
servers:
  - url: https://api.security-qa-mcp.example.com/api/v1
security:
  - bearerJwt: []
  - oauth2: [scans:read]
components:
  securitySchemes:
    bearerJwt:
      type: http
      scheme: bearer
      bearerFormat: JWT
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://idp.example.com/oauth2/authorize
          tokenUrl: https://idp.example.com/oauth2/token
          scopes:
            scans:read: Read scans
            scans:write: Create and manage scans
  schemas:
    ProblemDetails:
      type: object
      required: [type, title, status, code, correlation_id]
      properties:
        type: { type: string, format: uri }
        title: { type: string }
        status: { type: integer }
        code: { type: string }
        detail: { type: string }
        correlation_id: { type: string }
paths:
  /scans:
    post:
      tags: [Scans]
      operationId: createScan
      summary: Create an asynchronous security scan
      security:
        - oauth2: [scans:write]
        - bearerJwt: []
      parameters:
        - name: Idempotency-Key
          in: header
          required: true
          schema: { type: string, minLength: 16, maxLength: 128 }
      responses:
        '202':
          description: Scan accepted
        '422':
          description: Validation failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
```

## 16. Segurança operacional da API

- TLS 1.2+ obrigatório; TLS 1.3 recomendado.
- HSTS habilitado em domínios públicos.
- CORS allowlist por aplicação e ambiente.
- Proteção contra replay em webhooks por timestamp e HMAC.
- WAF/API Gateway com proteção contra payload anômalo.
- Upload/download sempre por URLs pré-assinadas de curta duração.
- Segredos em request devem usar referências a credenciais, nunca valores em claro quando possível.
- Ambientes produtivos exigem políticas adicionais para scans ativos.

## 17. Estratégia de compatibilidade enterprise

- Contratos OpenAPI versionados no repositório e publicados como artefato.
- Testes de contrato para SDKs e integrações críticas.
- Changelog público por versão.
- Política de suporte: versão principal atual e anterior.
- SDKs gerados a partir de OpenAPI, com retries, rate limit backoff, idempotência e correlation id.
- Ambientes sandbox com dados sintéticos para integração de clientes.
