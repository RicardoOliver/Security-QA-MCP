# Security QA MCP — Projeto do MCP Server

## 1. Objetivo

Este documento projeta o **MCP Server** do Security QA MCP como a interface padronizada para clientes compatíveis com Model Context Protocol, agentes de IA, IDEs, automações de CI/CD e operadores técnicos. O servidor deve expor ferramentas, recursos, prompts e capacidades de segurança de forma governada, auditável, extensível e segura.

O MCP Server não executa scanners diretamente no processo principal. Ele atua como **control plane protocol adapter**, validando entradas, aplicando contexto, chamando casos de uso da camada de aplicação, registrando auditoria e retornando respostas estruturadas.

## 2. Responsabilidades do MCP Server

- Expor ferramentas MCP para criar, consultar, cancelar e governar scans.
- Expor resources MCP para leitura contextual de projetos, alvos, políticas, findings, evidências e relatórios.
- Expor prompts MCP reutilizáveis para análise de findings, geração de planos de correção e explicações executivas.
- Declarar capabilities para discovery automático por clientes MCP.
- Gerenciar contexto de tenant, projeto, ator, correlação, sessão e permissões.
- Validar todos os parâmetros de entrada antes de acionar casos de uso.
- Traduzir erros de domínio, aplicação e infraestrutura para erros MCP estáveis.
- Registrar automaticamente ferramentas, resources, prompts e scanners habilitados.
- Participar do lifecycle de inicialização, health check, readiness, shutdown e drenagem de operações.
- Preparar extensão futura por scanners e plugins sem alterar o contrato central.

## 3. Princípios de desenho

| Princípio | Aplicação no MCP Server |
|---|---|
| Adaptador fino | O MCP Server converte protocolo em comandos e queries, sem conter regra de negócio. |
| Contratos versionados | Tools, resources, prompts e schemas usam versões explícitas e compatíveis. |
| Segurança por padrão | Toda operação exige tenant, projeto, escopo e permissões compatíveis. |
| Idempotência | Operações mutáveis aceitam `idempotency_key` para evitar duplicidade em retries. |
| Observabilidade nativa | Toda chamada recebe `correlation_id`, logs estruturados, métricas e traces. |
| Respostas acionáveis | Erros e resultados incluem códigos, próximos passos e referências. |
| Extensibilidade controlada | Novos scanners entram via manifesto, registry, capabilities e handlers genéricos. |

## 4. Estrutura proposta

```text
apps/mcp-server/src/
├─ bootstrap/
│  ├─ create-mcp-server.ts
│  ├─ dependency-container.ts
│  ├─ lifecycle-manager.ts
│  └─ register-all.ts
├─ capabilities/
│  ├─ capability-provider.ts
│  ├─ scanner-capability-mapper.ts
│  └─ server-capabilities.ts
├─ context/
│  ├─ mcp-context.ts
│  ├─ context-resolver.ts
│  ├─ correlation-context.ts
│  ├─ tenant-project-scope.ts
│  └─ context-store.ts
├─ handlers/
│  ├─ tool-handler.ts
│  ├─ resource-handler.ts
│  ├─ prompt-handler.ts
│  ├─ completion-handler.ts
│  └─ error-handler.ts
├─ registries/
│  ├─ tool-registry.ts
│  ├─ resource-registry.ts
│  ├─ prompt-registry.ts
│  ├─ scanner-registry.ts
│  └─ auto-discovery.ts
├─ tools/
│  ├─ scan/
│  ├─ findings/
│  ├─ policy/
│  ├─ reports/
│  ├─ plugins/
│  └─ system/
├─ resources/
│  ├─ project-resources.ts
│  ├─ scan-resources.ts
│  ├─ finding-resources.ts
│  ├─ evidence-resources.ts
│  ├─ policy-resources.ts
│  └─ plugin-resources.ts
├─ prompts/
│  ├─ analyze-finding.prompt.ts
│  ├─ remediation-plan.prompt.ts
│  ├─ executive-summary.prompt.ts
│  └─ scanner-selection.prompt.ts
├─ validators/
│  ├─ mcp-schema-validator.ts
│  ├─ authorization-validator.ts
│  ├─ target-scope-validator.ts
│  ├─ plugin-permission-validator.ts
│  └─ rate-limit-validator.ts
└─ mappers/
   ├─ mcp-request-mapper.ts
   ├─ mcp-response-mapper.ts
   └─ mcp-error-mapper.ts
```

## 5. Capabilities

O MCP Server deve publicar capabilities para que clientes descubram dinamicamente o que está disponível.

### 5.1 Capabilities do servidor

| Capability | Descrição |
|---|---|
| `tools` | Lista ferramentas executáveis com nome, descrição, schema de entrada e schema de saída. |
| `resources` | Lista URIs consultáveis e templates de URI para entidades do domínio. |
| `prompts` | Lista prompts reutilizáveis parametrizáveis. |
| `logging` | Permite que o cliente receba eventos operacionais filtrados por severidade. |
| `progress` | Permite reportar progresso de operações longas, principalmente scans e relatórios. |
| `cancellation` | Permite cancelamento cooperativo de chamadas em andamento quando suportado. |
| `sampling` | Opcional; pode ser habilitado para tarefas assistidas por LLM, como sumarização, quando governado. |

### 5.2 Capabilities de scanners

Cada scanner ou plugin registrado contribui capabilities próprias:

| Campo | Exemplo | Uso |
|---|---|---|
| `scanner_id` | `security-headers` | Identificação estável do scanner. |
| `scanner_version` | `1.4.0` | Seleção e auditoria de versão. |
| `target_types` | `web`, `api`, `openapi` | Compatibilidade com o alvo. |
| `test_categories` | `headers`, `tls`, `dast`, `fuzzing` | Descoberta e seleção automática. |
| `intensity_levels` | `passive`, `safe-active`, `intrusive` | Controle de risco operacional. |
| `required_permissions` | `network.http.outbound`, `browser.sandbox` | Validação antes da execução. |
| `output_schemas` | `SecurityFindingSchema/v1` | Normalização de resultados. |
| `supports_cancel` | `true` | Cancelamento cooperativo. |
| `supports_progress` | `true` | Streaming de progresso. |

## 6. Tools

Todas as tools devem seguir o padrão:

- Nome em snake case, prefixado por domínio funcional.
- Entrada validada por schema versionado.
- Saída com `status`, `data`, `warnings`, `correlation_id` e `audit_id` quando aplicável.
- Erros mapeados para códigos MCP estáveis.
- Auditoria em operações mutáveis ou sensíveis.

### 6.1 `scan_create`

Cria uma execução de scan sob demanda.

**Entrada principal**

| Campo | Obrigatório | Descrição |
|---|---:|---|
| `tenant_id` | Sim | Tenant da execução. |
| `project_id` | Sim | Projeto dono do alvo. |
| `target_id` | Sim | Alvo previamente cadastrado e autorizado. |
| `profile` | Sim | Perfil de scan: `quick`, `standard`, `deep`, `ci-gate` ou customizado. |
| `scanner_ids` | Não | Lista explícita de scanners; se omitida, a policy seleciona automaticamente. |
| `policy_id` | Não | Política específica; se omitida, usa a policy efetiva do projeto/alvo. |
| `idempotency_key` | Sim | Chave para evitar criação duplicada. |
| `metadata` | Não | Branch, commit, pipeline, ambiente e tags. |

**Funcionamento**

1. Resolve contexto do ator e do tenant.
2. Valida schema, RBAC, escopo do projeto e autorização do alvo.
3. Carrega policy efetiva e seleciona scanners compatíveis.
4. Verifica permissões, intensidade, janela operacional e quotas.
5. Cria scan em estado `queued` por caso de uso da aplicação.
6. Publica evento `ScanRequested` no barramento.
7. Retorna `scan_id`, status inicial, scanners selecionados e links de resources.

### 6.2 `scan_get_status`

Consulta progresso, estado e eventos recentes de um scan.

**Funcionamento**: valida acesso ao tenant/projeto, busca visão de status, calcula progresso agregado por etapas e retorna `queued`, `running`, `completed`, `failed`, `cancelled` ou `partially_completed`, incluindo percentuais por scanner e próximos passos.

### 6.3 `scan_cancel`

Solicita cancelamento cooperativo de uma execução.

**Funcionamento**: valida permissão operacional, registra motivo, altera estado para `cancelling`, publica comando de cancelamento aos workers, aguarda confirmação assíncrona e preserva logs/evidências já gerados.

### 6.4 `scan_retry`

Reprocessa uma execução falha ou parcialmente concluída.

**Funcionamento**: valida elegibilidade, limites de retry e idempotência; permite repetir todos os scanners ou apenas scanners com falha; cria nova tentativa vinculada ao scan original para rastreabilidade.

### 6.5 `scan_list`

Lista scans filtrados por projeto, alvo, status, período, branch, commit, severidade máxima encontrada e tags.

**Funcionamento**: aplica paginação, ordenação, autorização por projeto e redaction de metadados sensíveis.

### 6.6 `target_validate_scope`

Valida se uma URL, host, API ou contrato OpenAPI está dentro do escopo autorizado.

**Funcionamento**: normaliza entradas, compara com allowlists/denylists, valida ambiente, resolve DNS quando permitido pela policy, identifica riscos de SSRF e retorna decisão `allowed`, `denied` ou `requires_approval`.

### 6.7 `finding_list`

Lista achados normalizados de um scan, alvo ou projeto.

**Funcionamento**: aplica filtros por severidade, status, scanner, CWE, OWASP, data, fingerprint e quality gate; retorna dados paginados e links para evidências.

### 6.8 `finding_get`

Obtém detalhes de um achado específico.

**Funcionamento**: retorna descrição, severidade, impacto, evidências, origem, deduplicação, recomendações, referências, histórico de status e decisões de exceção.

### 6.9 `finding_update_status`

Atualiza o lifecycle de um achado.

**Funcionamento**: valida transição permitida, papel do ator, justificativa obrigatória quando necessário e registra auditoria. Estados sugeridos: `new`, `triaged`, `accepted_risk`, `in_remediation`, `fixed`, `false_positive`, `reopened`.

### 6.10 `policy_evaluate_gate`

Avalia quality gate para um scan, projeto, branch ou release.

**Funcionamento**: carrega findings aplicáveis, exceções vigentes e thresholds da policy; retorna decisão `passed`, `failed` ou `inconclusive`, com motivos, achados bloqueantes e recomendação de ação.

### 6.11 `policy_request_exception`

Solicita exceção para finding, scanner, alvo ou policy.

**Funcionamento**: exige justificativa, prazo, escopo, risco aceito e aprovador; cria registro auditável em estado `pending_approval`.

### 6.12 `report_generate`

Gera relatório técnico, executivo, auditoria, SARIF, JSON ou HTML.

**Funcionamento**: valida escopo, enfileira job de relatório, aplica redaction conforme perfil, armazena artefato no object store e retorna `report_id` para consulta posterior.

### 6.13 `report_get`

Consulta metadados e links seguros de download de relatório.

**Funcionamento**: valida autorização, gera URL assinada de curta duração quando aplicável e retorna hashes de integridade.

### 6.14 `plugin_list`

Lista plugins/scanners disponíveis, versões, status, capabilities e permissões.

**Funcionamento**: consulta registry, filtra por tenant/projeto/policy e informa se cada scanner está `enabled`, `disabled`, `deprecated`, `requires_approval` ou `unavailable`.

### 6.15 `plugin_register`

Registra um novo scanner ou plugin.

**Funcionamento**: recebe manifesto assinado ou referência a pacote, valida schema, assinatura, compatibilidade, permissões solicitadas e política administrativa; registra versão em estado `pending`, `approved` ou `rejected`.

### 6.16 `scanner_recommend`

Recomenda scanners para um alvo ou contrato.

**Funcionamento**: compara tipo de alvo, tecnologias, policy, histórico de findings e intensidade permitida; retorna lista priorizada com justificativa e riscos operacionais.

### 6.17 `evidence_get_metadata`

Consulta metadados de evidências sem expor conteúdo sensível por padrão.

**Funcionamento**: retorna tipo, tamanho, hash, classificação, origem, retenção, redaction aplicada e link seguro quando autorizado.

### 6.18 `audit_search`

Pesquisa trilhas de auditoria relacionadas a scans, findings, policies, plugins e relatórios.

**Funcionamento**: aplica filtros por ator, ação, recurso, período, resultado e correlação; retorna eventos paginados imutáveis.

### 6.19 `system_health`

Retorna health operacional do MCP Server e dependências críticas.

**Funcionamento**: checa banco, barramento, registry, object store, workers e versão do servidor; separa `live`, `ready` e `degraded`.

## 7. Resources

Resources são leituras contextuais, cacheáveis quando seguro, representadas por URIs estáveis.

| URI | Descrição |
|---|---|
| `securityqa://tenants/{tenant_id}/projects` | Lista projetos acessíveis. |
| `securityqa://projects/{project_id}` | Metadados do projeto. |
| `securityqa://projects/{project_id}/targets` | Alvos autorizados do projeto. |
| `securityqa://targets/{target_id}` | Detalhes de alvo, escopo e policy efetiva. |
| `securityqa://scans/{scan_id}` | Estado consolidado do scan. |
| `securityqa://scans/{scan_id}/events` | Linha do tempo de eventos do scan. |
| `securityqa://scans/{scan_id}/findings` | Findings do scan. |
| `securityqa://findings/{finding_id}` | Detalhe canônico do finding. |
| `securityqa://findings/{finding_id}/evidence` | Evidências associadas. |
| `securityqa://policies/{policy_id}` | Política versionada. |
| `securityqa://plugins` | Catálogo de plugins visíveis ao ator. |
| `securityqa://plugins/{plugin_id}/manifest` | Manifesto e capabilities do plugin. |
| `securityqa://reports/{report_id}` | Metadados de relatório. |
| `securityqa://audit?resource_id={id}` | Trilha de auditoria filtrada. |

Resources devem respeitar autorização, classificação da informação, paginação, ETag, TTL de cache e mascaramento de segredos.

## 8. Prompts

Prompts ajudam clientes MCP a executar tarefas recorrentes com contexto padronizado.

| Prompt | Parâmetros | Resultado esperado |
|---|---|---|
| `analyze_finding` | `finding_id`, `audience`, `depth` | Explicação técnica ou executiva do achado. |
| `remediation_plan` | `finding_id`, `technology_stack`, `sla` | Plano de correção priorizado e testável. |
| `executive_summary` | `project_id`, `period`, `risk_model` | Resumo de risco, tendência e decisões necessárias. |
| `quality_gate_explanation` | `scan_id` ou `gate_id` | Explicação dos motivos de aprovação/reprovação. |
| `scanner_selection` | `target_id`, `profile`, `constraints` | Justificativa dos scanners recomendados. |
| `audit_evidence_package` | `scan_id` ou `project_id` | Roteiro para pacote de evidências de auditoria. |

Prompts nunca devem embutir segredos. O handler deve buscar resources autorizados, resumir contexto, aplicar redaction e registrar uso quando houver dado sensível.

## 9. Handlers

### 9.1 Tool handler

Responsável por receber chamadas `tools/call`, localizar definição no `ToolRegistry`, validar entrada, criar contexto, executar caso de uso, mapear saída e registrar métricas.

### 9.2 Resource handler

Responsável por resolver URI, aplicar autorização, carregar query apropriada, serializar resposta, aplicar cache headers e mascarar campos sensíveis.

### 9.3 Prompt handler

Responsável por listar prompts, validar parâmetros, montar mensagens com contexto autorizado e limitar tamanho para evitar vazamento de dados ou estouro de contexto.

### 9.4 Completion handler

Opcionalmente fornece autocomplete de `project_id`, `target_id`, `scanner_id`, severidades e status, sempre filtrado por autorização.

### 9.5 Error handler

Centraliza conversão de exceções e resultados falhos para respostas MCP consistentes, incluindo `error_code`, `message`, `details`, `retryable`, `correlation_id` e `user_action`.

## 10. Context Management

O contexto MCP deve ser resolvido a cada chamada e propagado até application/domain.

| Elemento | Origem | Uso |
|---|---|---|
| `correlation_id` | Header, metadata MCP ou gerado no servidor | Observabilidade ponta a ponta. |
| `request_id` | Gerado por chamada | Diagnóstico de requisição individual. |
| `actor_id` | Token, sessão ou credencial de serviço | Auditoria e autorização. |
| `tenant_id` | Entrada, token ou resource URI | Isolamento multi tenant. |
| `project_scope` | Claims, RBAC ou ABAC | Filtro de recursos e permissões. |
| `client_info` | Handshake MCP | Compatibilidade, limites e auditoria. |
| `trace_context` | OpenTelemetry | Tracing distribuído. |
| `classification` | Policy de dados | Redaction e autorização de evidências. |

O servidor deve evitar estado global mutável. Contexto por requisição deve ser armazenado em mecanismo equivalente a `AsyncLocalStorage` ou passado explicitamente.

## 11. Lifecycle

### 11.1 Inicialização

1. Carregar configuração externa e segredos.
2. Inicializar logger, métricas e tracing.
3. Montar container de dependências.
4. Conectar a banco, event bus, object store e registry.
5. Descobrir ferramentas, resources, prompts e scanners.
6. Validar duplicidade de nomes e versões incompatíveis.
7. Publicar capabilities.
8. Marcar readiness quando dependências críticas estiverem saudáveis.

### 11.2 Operação

- Aceitar chamadas MCP.
- Aplicar rate limit e quotas.
- Executar handlers com timeout e cancellation token.
- Emitir métricas por tool/resource/prompt.
- Publicar logs estruturados com redaction.

### 11.3 Shutdown

1. Parar de aceitar novas chamadas.
2. Drenar requisições em andamento até timeout.
3. Cancelar operações cooperativas quando possível.
4. Fechar conexões com dependências.
5. Exportar spans e métricas pendentes.
6. Registrar evento de shutdown.

## 12. Registro automático

O registro automático deve reduzir boilerplate e impedir inconsistências.

### 12.1 Definição declarativa

Cada tool, resource ou prompt deve exportar uma definição declarativa:

```text
name/version/description/input_schema/output_schema/required_permissions/handler_factory
```

### 12.2 Auto-discovery

- Varre módulos conhecidos em `tools/`, `resources/` e `prompts/` durante bootstrap.
- Carrega manifestos de plugins aprovados pelo `ScannerRegistry`.
- Rejeita nomes duplicados, schemas inválidos e versões incompatíveis.
- Gera catálogo final usado nas capabilities MCP.

### 12.3 Registro de scanners

Scanners entram por manifesto:

```json
{
  "id": "security-headers",
  "version": "1.0.0",
  "entrypoint": "container://security-headers:1.0.0",
  "target_types": ["web"],
  "capabilities": ["headers", "passive"],
  "required_permissions": ["network.http.outbound"],
  "input_schema": "PluginInputSchema/v1",
  "output_schema": "PluginOutputSchema/v1"
}
```

O MCP Server não carrega código arbitrário do plugin no processo principal; ele registra metadados e aciona a execução via orquestrador/runtime.

## 13. Validação

A validação deve ocorrer em camadas complementares:

| Camada | Validações |
|---|---|
| Schema | Tipos, campos obrigatórios, enums, formato de URI, limites de tamanho. |
| Autenticação | Identidade do ator e validade de credenciais. |
| Autorização | Permissões por tenant, projeto, recurso e ação. |
| Escopo | Alvo autorizado, allowlist, ambiente, janela e intensidade. |
| Policy | Quotas, qualidade mínima, scanners permitidos, exceções e gates. |
| Segurança | SSRF, URLs internas proibidas, segredos em payloads, payloads perigosos. |
| Idempotência | Reuso seguro de chaves em comandos mutáveis. |
| Contrato | Compatibilidade entre versão da tool, plugin e schemas. |

Falhas de validação devem retornar erro não retryable, com campos inválidos e orientação de correção.

## 14. Tratamento de erros

| Classe de erro | Código sugerido | Retry | Exemplo |
|---|---|---:|---|
| Validação | `VALIDATION_ERROR` | Não | Campo obrigatório ausente. |
| Autenticação | `AUTHENTICATION_REQUIRED` | Não | Token ausente ou expirado. |
| Autorização | `AUTHORIZATION_DENIED` | Não | Ator sem acesso ao projeto. |
| Escopo | `TARGET_OUT_OF_SCOPE` | Não | URL fora da allowlist. |
| Conflito | `CONFLICT` | Depende | Scan já cancelado. |
| Rate limit | `RATE_LIMITED` | Sim | Quota excedida temporariamente. |
| Dependência | `DEPENDENCY_UNAVAILABLE` | Sim | Event bus indisponível. |
| Timeout | `TIMEOUT` | Sim | Consulta demorou demais. |
| Plugin | `PLUGIN_EXECUTION_ERROR` | Depende | Scanner retornou saída inválida. |
| Interno | `INTERNAL_ERROR` | Sim | Falha inesperada mascarada. |

Erros internos não devem expor stack trace, segredos, payloads brutos ou detalhes de infraestrutura ao cliente final.

## 15. Estratégia para adicionar novos scanners

### 15.1 Contrato estável de scanner

Todo scanner deve implementar o contrato de plugin, composto por:

- Manifesto com metadados, versão, capabilities e permissões.
- Schema de entrada compatível com `PluginInputSchema`.
- Saída compatível com `PluginOutputSchema`.
- Findings no formato canônico `SecurityFindingSchema`.
- Suporte opcional a progresso, cancelamento e artefatos.

### 15.2 Fluxo de inclusão

1. Desenvolvedor cria scanner usando `packages/plugin-sdk`.
2. Define manifesto, schemas, permissões e testes de contrato.
3. Publica pacote/container assinado em registry confiável.
4. Admin registra plugin via `plugin_register` ou pipeline administrativo.
5. Plataforma valida assinatura, schemas, permissões e compatibilidade.
6. Scanner fica disponível como `pending_approval` ou `enabled` conforme policy.
7. Capabilities aparecem automaticamente em `plugin_list` e `scanner_recommend`.
8. Orquestrador passa a selecioná-lo quando policy e target forem compatíveis.

### 15.3 Regras para evolução

- Novas versões devem ser instaláveis lado a lado.
- Breaking changes exigem novo major version e migração planejada.
- Depreciação deve manter janela de compatibilidade.
- Resultados devem continuar normalizados no modelo canônico.
- Permissões adicionais exigem nova aprovação administrativa.
- Scanners intrusivos exigem policy explícita, janela e confirmação operacional.

## 16. Segurança operacional

- Executar scanners em sandbox/container isolado, nunca no processo MCP.
- Aplicar allowlist de rede, DNS seguro e bloqueio de endereços internos quando não autorizados.
- Redigir tokens, cookies, Authorization headers e payloads sensíveis.
- Limitar tamanho de evidências e respostas MCP.
- Aplicar timeouts, quotas, circuit breakers e backpressure.
- Registrar auditoria imutável para ações sensíveis.
- Separar permissões de leitura, execução, administração e auditoria.

## 17. Observabilidade

Métricas mínimas:

- `mcp_tool_calls_total` por tool, status e tenant.
- `mcp_tool_duration_seconds` por tool.
- `mcp_resource_reads_total` por resource e status.
- `mcp_prompt_calls_total` por prompt.
- `scan_requests_total` por perfil, status e scanner.
- `mcp_errors_total` por código.
- `mcp_rate_limited_total` por tenant/projeto.

Logs devem conter `correlation_id`, `request_id`, `actor_id` mascarado, `tenant_id`, `tool/resource/prompt`, duração, status e erro normalizado.

## 18. Modelo de resposta padrão

```json
{
  "status": "success",
  "data": {},
  "warnings": [],
  "correlation_id": "01J...",
  "audit_id": "aud_..."
}
```

Em erro:

```json
{
  "status": "error",
  "error": {
    "code": "TARGET_OUT_OF_SCOPE",
    "message": "O alvo informado não está autorizado para este projeto.",
    "retryable": false,
    "user_action": "Revise o cadastro do alvo ou solicite aprovação de escopo."
  },
  "correlation_id": "01J..."
}
```

## 19. Roadmap incremental de implementação

| Fase | Entregas |
|---|---|
| Fase 1 | Bootstrap MCP, contexto, health, `scan_create`, `scan_get_status`, resources básicos e catálogo de plugins mockado. |
| Fase 2 | Findings, evidências, quality gate, reports e auditoria. |
| Fase 3 | Registro administrativo de plugins, scanner registry real, seleção automática e contrato de plugin. |
| Fase 4 | Prompts avançados, completion, streaming de progresso, cancelamento e observabilidade completa. |
| Fase 5 | Multi tenant enterprise completo, policies avançadas, marketplace interno de scanners e governança de versões. |
