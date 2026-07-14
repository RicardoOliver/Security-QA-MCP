# Security QA MCP — Blueprint de Arquitetura Enterprise

## 1. Visão de alto nível

O **Security QA MCP** é uma plataforma enterprise para automatizar testes de segurança em aplicações Web e APIs usando o **Model Context Protocol (MCP)** como camada padronizada de exposição de ferramentas, contexto e resultados para clientes compatíveis com MCP, agentes de IA, pipelines de CI/CD e interfaces operacionais.

A plataforma deve executar milhares de varreduras diárias com isolamento, rastreabilidade, governança, controle de custos e segurança operacional. O sistema é desenhado para ser modular, extensível por plugins e preparado para operar em ambientes locais, Docker, Kubernetes e pipelines corporativos.

### Objetivos principais

- Orquestrar testes automatizados de segurança Web e API.
- Expor capacidades via MCP Server, API HTTP e CLI.
- Permitir plugins para scanners, validadores, parsers, correlacionadores e reporters.
- Suportar execuções assíncronas e distribuídas em larga escala.
- Padronizar evidências, achados, severidade, recomendações e rastreabilidade.
- Projetar o modelo de dados enterprise com multi tenant, auditoria, histórico, versionamento e soft delete.
- Integrar com CI/CD, repositórios, issue trackers, SIEM, observabilidade e sistemas de governança.
- Separar domínio, aplicação, infraestrutura e interfaces segundo Clean Architecture e Hexagonal Architecture.

### Capacidades funcionais

- Testes DAST para aplicações Web.
- Testes de segurança para APIs REST, GraphQL e OpenAPI.
- Fuzzing básico e orientado por contrato.
- Validação de headers, TLS, autenticação, autorização e exposição de dados.
- Execução de plugins de scanners externos.
- Normalização e correlação de resultados.
- Geração de relatórios técnicos e executivos.
- Policies de quality gate por severidade, risco e contexto.
- Execução local, em containers, workers distribuídos e CI/CD.

### Capacidades não funcionais

- Alta escalabilidade horizontal.
- Isolamento entre tenants, projetos e execuções.
- Tolerância a falhas com filas, retries e idempotência.
- Observabilidade completa com métricas, logs e traces.
- Segurança by design para execução de scanners potencialmente perigosos.
- Evolução por plugins sem acoplamento ao core.

---

## 2. Princípios arquiteturais

A arquitetura é guiada por:

- **Clean Architecture**: domínio independente de frameworks, bancos e protocolos.
- **Hexagonal Architecture**: portas no core e adaptadores nas bordas.
- **DDD pragmático**: agregados e linguagem ubíqua nos bounded contexts relevantes.
- **SOLID**: componentes pequenos, coesos e substituíveis.
- **Clean Code**: baixo acoplamento, alta legibilidade e contratos explícitos.
- **Event Driven Architecture**: workflows assíncronos, eventos de domínio e integração.
- **Plugin Architecture**: scanners e extensões carregados via contratos estáveis.
- **Security by Design**: isolamento, menor privilégio, validação e auditoria.
- **Cloud Native**: containers, health checks, autoscaling, configuração externa e stateless services sempre que possível.

---

## 3. Arquitetura lógica

A arquitetura lógica é organizada em camadas e bounded contexts.

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Interfaces                                                          │
│ ├─ MCP Server                                                       │
│ ├─ REST/GraphQL API                                                 │
│ ├─ CLI                                                              │
│ └─ Web Console                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Application Layer                                                   │
│ ├─ Use Cases                                                        │
│ ├─ Orchestration Services                                           │
│ ├─ Policy Evaluation                                                │
│ ├─ DTOs / Commands / Queries                                        │
│ └─ Application Events                                               │
├─────────────────────────────────────────────────────────────────────┤
│ Domain Layer                                                        │
│ ├─ Scan, Target, Finding, Evidence, Policy, Plugin, Report          │
│ ├─ Domain Services                                                  │
│ ├─ Value Objects                                                    │
│ ├─ Domain Events                                                    │
│ └─ Repository / Gateway Ports                                       │
├─────────────────────────────────────────────────────────────────────┤
│ Infrastructure Layer                                                │
│ ├─ Persistence Adapters                                             │
│ ├─ Queue / Event Bus Adapters                                       │
│ ├─ Object Storage Adapters                                          │
│ ├─ Secret Manager Adapters                                          │
│ ├─ Scanner Runtime Adapters                                         │
│ └─ Observability Adapters                                           │
└─────────────────────────────────────────────────────────────────────┘
```

### Bounded contexts sugeridos

| Contexto | Responsabilidade |
|---|---|
| Scan Management | Ciclo de vida de execuções, alvos, escopo, status e agendamento. |
| Security Testing | Execução de testes, seleção de plugins, sandbox e coleta de evidências. |
| Findings | Normalização, deduplicação, correlação, severidade e lifecycle de achados. |
| Policy & Gates | Regras de bloqueio, thresholds, exceções e decisões de aprovação. |
| Reporting | Relatórios técnicos, executivos, SARIF, JSON, HTML e integrações externas. |
| Plugin Management | Registro, versão, capabilities, assinatura, permissões e runtime de plugins. |
| Identity & Tenancy | Autenticação, autorização, tenants, projetos e RBAC/ABAC. |
| Audit & Compliance | Trilhas de auditoria, retenção, evidências e exportações de conformidade. |

---

## 4. Arquitetura física

Para escala enterprise, a implantação física deve separar plano de controle, plano de execução e plano de dados.

```text
                         ┌──────────────────────┐
                         │ MCP Clients / AI IDEs │
                         └──────────┬───────────┘
                                    │ MCP
┌─────────────┐   HTTPS   ┌─────────▼─────────┐
│ Web Console │──────────▶│ API Gateway / WAF │
└─────────────┘           └─────────┬─────────┘
                                    │
              ┌─────────────────────▼─────────────────────┐
              │ Control Plane                              │
              │ ├─ MCP Server                              │
              │ ├─ Public API                              │
              │ ├─ Auth Service                            │
              │ ├─ Scan Orchestrator                       │
              │ ├─ Plugin Registry                         │
              │ └─ Report Service                          │
              └───────────────┬───────────────┬────────────┘
                              │               │
                       Events │               │ SQL/NoSQL
                              │               │
                     ┌────────▼───────┐   ┌───▼────────────┐
                     │ Event Bus      │   │ Metadata DB    │
                     │ Kafka/NATS/SQS │   │ PostgreSQL     │
                     └────────┬───────┘   └────────────────┘
                              │
              ┌───────────────▼────────────────────┐
              │ Execution Plane                     │
              │ ├─ Worker Pool                      │
              │ ├─ Plugin Runtime                   │
              │ ├─ Browser Sandbox                  │
              │ ├─ API Test Sandbox                 │
              │ └─ Scanner Sidecars                 │
              └───────────────┬────────────────────┘
                              │ artifacts/evidence
                       ┌──────▼────────┐
                       │ Object Store  │
                       │ S3/MinIO/GCS  │
                       └───────────────┘
```

### Nós físicos principais

- **API Gateway/WAF**: TLS, rate limit, proteção, roteamento e autenticação inicial.
- **MCP Server**: expõe ferramentas e recursos MCP para criação, execução e consulta de scans.
- **Public API**: API REST/GraphQL para integrações, UI e automação.
- **Scan Orchestrator**: transforma requisições em jobs, aplica policies e publica eventos.
- **Worker Pool**: executa jobs em paralelo com autoscaling.
- **Plugin Runtime**: carrega e executa plugins em sandboxes isolados.
- **Metadata DB**: armazena entidades transacionais.
- **Object Store**: armazena evidências pesadas, logs brutos, screenshots, HARs e relatórios.
- **Event Bus**: desacopla orquestração, execução, findings e reporting.
- **Observability Stack**: OpenTelemetry, Prometheus, Grafana, Loki/ELK e Jaeger/Tempo.

---

## 5. Arquitetura modular

```text
security-qa-mcp/
├─ apps/
│  ├─ mcp-server/
│  ├─ api-server/
│  ├─ worker/
│  ├─ cli/
│  └─ web-console/
├─ packages/
│  ├─ domain/
│  ├─ application/
│  ├─ contracts/
│  ├─ plugin-sdk/
│  ├─ shared-kernel/
│  └─ test-fixtures/
├─ adapters/
│  ├─ persistence-postgres/
│  ├─ event-bus-nats/
│  ├─ object-storage-s3/
│  ├─ secrets-vault/
│  ├─ browser-playwright/
│  ├─ http-client/
│  └─ observability-otel/
├─ plugins/
│  ├─ security-headers/
│  ├─ tls-audit/
│  ├─ openapi-fuzzer/
│  ├─ authz-checker/
│  ├─ zap-adapter/
│  └─ nuclei-adapter/
├─ deploy/
│  ├─ docker/
│  ├─ compose/
│  ├─ helm/
│  └─ terraform/
├─ docs/
│  ├─ architecture/
│  ├─ adr/
│  ├─ threat-model/
│  └─ runbooks/
└─ tests/
   ├─ unit/
   ├─ integration/
   ├─ contract/
   ├─ e2e/
   └─ performance/
```

### Responsabilidades por módulo

| Módulo | Responsabilidade |
|---|---|
| apps/mcp-server | Implementar endpoints MCP, tools, resources e prompts operacionais. |
| apps/api-server | Expor APIs para UI, CI/CD e integrações externas. |
| apps/worker | Consumir jobs e executar workflows de teste. |
| apps/cli | Permitir execução local, automação e depuração. |
| apps/web-console | Operação visual, dashboards, findings e relatórios. |
| packages/domain | Entidades, value objects, eventos e regras de negócio puras. |
| packages/application | Casos de uso, orquestração, comandos, queries e policies. |
| packages/contracts | Schemas estáveis de eventos, APIs, findings, plugins e relatórios. |
| packages/plugin-sdk | Interfaces, helpers e contrato de desenvolvimento de plugins. |
| packages/shared-kernel | Tipos comuns, erros, utilitários e primitives transversais. |
| adapters/* | Implementações concretas de portas de infraestrutura. |
| plugins/* | Plugins independentes versionados e testáveis. |
| deploy/* | Artefatos de deploy local, container e cloud. |
| docs/* | Decisões, modelos, ameaças e runbooks. |
| tests/* | Estratégia completa de qualidade e segurança. |

---

## 6. Arquitetura técnica detalhada

A modelagem técnica completa do sistema, incluindo estrutura de pastas, packages, camadas, interfaces, entidades, DTOs, casos de uso, serviços, repositórios, adaptadores, gateways, configurações, eventos, exceptions, middlewares, builders, factories, validators, helpers e utilitários, está documentada em [`docs/architecture/technical-architecture.md`](docs/architecture/technical-architecture.md).

---

## 7. Componentes do domínio

### Entidades principais

- **Tenant**: organização ou unidade isolada.
- **Project**: agrupamento lógico de alvos, policies e integrações.
- **Target**: aplicação Web, endpoint de API, especificação OpenAPI ou GraphQL schema.
- **ScanRequest**: intenção de execução criada por usuário, MCP, API ou CI.
- **ScanExecution**: execução concreta com status, timestamps, configuração e correlação.
- **PluginDefinition**: metadata, versão, capacidades, permissões e entrypoint.
- **PluginExecution**: execução individual de um plugin dentro de um scan.
- **Finding**: achado normalizado de segurança.
- **Evidence**: evidência vinculada a um finding ou execução.
- **Policy**: regra de avaliação de risco, bloqueio ou aprovação.
- **Report**: artefato consolidado para consumo humano ou máquina.
- **AuditLog**: evento imutável de operação e segurança.

### Value objects

- `TargetUrl`
- `HttpMethod`
- `Severity`
- `Confidence`
- `CweId`
- `OwaspCategory`
- `CvssVector`
- `ScanScope`
- `CorrelationId`
- `PluginCapability`
- `ExecutionTimeout`
- `RateLimitPolicy`

### Eventos de domínio

- `ScanRequested`
- `ScanAccepted`
- `ScanRejected`
- `ScanScheduled`
- `ScanStarted`
- `PluginExecutionStarted`
- `PluginExecutionCompleted`
- `FindingDiscovered`
- `FindingDeduplicated`
- `PolicyEvaluated`
- `QualityGateFailed`
- `ReportGenerated`
- `ScanCompleted`
- `ScanFailed`

---

## 8. Portas e adaptadores

### Portas de entrada

- `CreateScanUseCase`
- `StartScanUseCase`
- `CancelScanUseCase`
- `GetScanStatusQuery`
- `ListFindingsQuery`
- `EvaluatePolicyUseCase`
- `GenerateReportUseCase`
- `RegisterPluginUseCase`

### Portas de saída

- `ScanRepository`
- `FindingRepository`
- `PolicyRepository`
- `PluginRegistryRepository`
- `EventPublisher`
- `JobQueue`
- `ObjectStorage`
- `SecretProvider`
- `PluginExecutor`
- `BrowserAutomationGateway`
- `HttpClientGateway`
- `TelemetryGateway`
- `AuditLogWriter`

### Adaptadores sugeridos

- PostgreSQL para metadados transacionais.
- Redis para cache, locks leves e rate limit.
- NATS JetStream, Kafka, RabbitMQ ou SQS para filas/eventos.
- S3, GCS, Azure Blob ou MinIO para evidências.
- HashiCorp Vault, AWS Secrets Manager ou Kubernetes Secrets para credenciais.
- Playwright para navegação e coleta Web.
- OWASP ZAP, Nuclei, Semgrep ou scanners comerciais via adaptadores.
- OpenTelemetry para traces, métricas e logs correlacionados.

---

## 9. Fluxo de comunicação

### Fluxo síncrono de criação

```text
Client/MCP/CLI
  → API Gateway
  → MCP Server ou API Server
  → CreateScanUseCase
  → valida escopo, tenant, auth, quota e policy
  → persiste ScanExecution=PENDING
  → publica ScanRequested
  → retorna scan_id e correlation_id
```

### Fluxo assíncrono de execução

```text
ScanRequested
  → Scan Orchestrator
  → resolve plugins aplicáveis
  → cria PluginExecution jobs
  → publica jobs no Event Bus
  → Workers consomem jobs
  → Plugin Runtime executa em sandbox
  → evidências são gravadas no Object Store
  → findings normalizados são persistidos
  → eventos FindingDiscovered são publicados
  → correlacionador deduplica e agrega risco
  → Policy Engine avalia quality gate
  → Report Service gera artefatos
  → ScanExecution=COMPLETED/FAILED
```

### Fluxo de consulta

```text
Client
  → MCP resource/read ou API query
  → Query Handler
  → Metadata DB + Object Store
  → DTO de status, findings, evidências ou relatório
```

---

## 10. Diagrama textual completo

```text
[User / CI / AI Agent]
        │
        ├── MCP tools/resources ──▶ [MCP Server]
        │                              │
        ├── REST/GraphQL ─────────▶ [API Server]
        │                              │
        └── CLI ───────────────────▶ [CLI Adapter]
                                       │
                                       ▼
                              [Application Use Cases]
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                        ▼
       [Domain Model]            [Policy Engine]          [Plugin Selector]
              │                        │                        │
              ▼                        ▼                        ▼
       [Repositories]           [Event Publisher]        [Job Scheduler]
              │                        │                        │
              ▼                        ▼                        ▼
       [PostgreSQL]             [Event Bus] ───────────▶ [Worker Pool]
                                                        │
                                                        ▼
                                                 [Plugin Runtime]
                                                        │
          ┌─────────────────────────────────────────────┼───────────────┐
          ▼                                             ▼               ▼
 [HTTP/API Probes]                              [Browser Sandbox] [External Scanners]
          │                                             │               │
          └─────────────────────────────┬───────────────┴───────────────┘
                                        ▼
                              [Evidence Collector]
                                        │
                      ┌─────────────────┴─────────────────┐
                      ▼                                   ▼
               [Object Storage]                    [Finding Normalizer]
                                                          │
                                                          ▼
                                                   [Finding Store]
                                                          │
                                                          ▼
                                                   [Report Service]
                                                          │
                                                          ▼
                                                   [Reports / Gates]
```

---

## 11. Fluxo completo de execução

1. **Recebimento da solicitação**
   - Usuário, agente MCP, pipeline ou CLI solicita um scan.
   - A entrada contém tenant, projeto, target, credenciais opcionais, escopo, tipo de teste e policies.

2. **Autenticação e autorização**
   - O gateway valida token, mTLS ou credencial de serviço.
   - O core verifica permissões por tenant, projeto e operação.

3. **Validação de escopo**
   - O sistema valida URL, domínio permitido, CIDR, ambientes bloqueados e limites de taxa.
   - SSRF, localhost, metadados cloud e redes internas são bloqueados por padrão, salvo allowlist explícita.

4. **Criação da execução**
   - A aplicação cria `ScanExecution` com status `PENDING`.
   - Um `correlation_id` é gerado.
   - Evento `ScanRequested` é emitido.

5. **Planejamento da execução**
   - O orquestrador carrega configurações, plugins elegíveis e dependências.
   - Um plano de execução é gerado com etapas paralelas e sequenciais.

6. **Agendamento de jobs**
   - Jobs são publicados para workers com idempotency key.
   - A prioridade considera tenant, SLA, origem e criticidade.

7. **Execução isolada**
   - Workers executam plugins em sandbox com timeout, CPU/memória limitadas e egress controlado.
   - Plugins não acessam secrets diretamente; recebem tokens efêmeros ou capabilities restritas.

8. **Coleta de evidências**
   - Requests, responses, screenshots, HAR, logs e payloads relevantes são armazenados no object storage.
   - Evidências recebem hash, metadados e política de retenção.

9. **Normalização de findings**
   - Resultados brutos são convertidos para schema canônico.
   - Severidade, confiança, CWE, OWASP e CVSS são preenchidos quando possível.

10. **Correlação e deduplicação**
    - Findings duplicados são agrupados por target, localização, tipo, payload e fingerprint.
    - Histórico anterior pode ser usado para regressão e tendência.

11. **Avaliação de policy**
    - O Policy Engine avalia regras como: bloquear se houver crítico, bloquear se CVSS >= 8, permitir exceções aprovadas.
    - O resultado gera `QualityGatePassed` ou `QualityGateFailed`.

12. **Geração de relatório**
    - Relatórios JSON, SARIF, HTML, Markdown e PDF podem ser produzidos.
    - Artefatos são publicados e vinculados à execução.

13. **Notificações e integrações**
    - Webhooks, Slack/Teams, Jira, GitHub/GitLab e SIEM podem ser notificados.

14. **Encerramento**
    - `ScanExecution` recebe status final.
    - Métricas e logs são finalizados com correlation id.
    - Auditoria registra a conclusão.

---

## 12. Modelo MCP

O MCP Server deve expor capacidades como ferramentas e recursos.

### Tools MCP sugeridas

| Tool | Descrição |
|---|---|
| `securityqa.create_scan` | Cria uma execução de teste de segurança. |
| `securityqa.get_scan_status` | Consulta status de uma execução. |
| `securityqa.cancel_scan` | Cancela uma execução pendente ou ativa. |
| `securityqa.list_findings` | Lista achados normalizados. |
| `securityqa.get_finding` | Detalha um achado e suas evidências. |
| `securityqa.evaluate_policy` | Avalia findings contra uma policy. |
| `securityqa.generate_report` | Gera relatório em formato solicitado. |
| `securityqa.list_plugins` | Lista plugins disponíveis e capabilities. |
| `securityqa.validate_target` | Valida escopo e segurança do alvo antes do scan. |

### Resources MCP sugeridos

- `securityqa://scans/{scan_id}`
- `securityqa://scans/{scan_id}/findings`
- `securityqa://findings/{finding_id}`
- `securityqa://reports/{report_id}`
- `securityqa://plugins`
- `securityqa://policies/{policy_id}`

### Prompts MCP sugeridos

- Analisar risco de achados.
- Gerar plano de remediação.
- Explicar evidências para desenvolvedores.
- Produzir resumo executivo.
- Sugerir testes complementares.

---

## 13. Estratégia de plugins

### Contrato de plugin

Cada plugin deve declarar:

- Nome, versão e fornecedor.
- Capabilities, como `web.headers`, `api.openapi.fuzz`, `tls.audit`.
- Tipo de alvo suportado.
- Permissões necessárias.
- Limites recomendados de CPU, memória, rede e tempo.
- Schema de configuração.
- Schema de saída.
- Política de segurança e assinatura.

### Tipos de plugin

- **Native plugins**: implementados no SDK oficial.
- **Adapter plugins**: encapsulam ferramentas externas como ZAP ou Nuclei.
- **Analyzer plugins**: processam evidências e geram findings.
- **Reporter plugins**: exportam relatórios em formatos específicos.
- **Integration plugins**: enviam resultados para Jira, GitHub, SIEM ou GRC.

### Isolamento

- Containers efêmeros por plugin ou por execução.
- Seccomp/AppArmor e filesystem read-only.
- Network policies por alvo autorizado.
- Timeouts obrigatórios.
- Quotas por tenant.
- Assinatura e verificação de integridade de plugins.

---

## 14. Tecnologias sugeridas

### Opção recomendada

| Camada | Tecnologia |
|---|---|
| Backend | TypeScript com Node.js ou Python com FastAPI para velocidade de entrega. |
| Core crítico de performance | Go ou Rust para workers de alta concorrência, se necessário. |
| MCP Server | SDK MCP oficial compatível com a linguagem escolhida. |
| API | REST OpenAPI-first; GraphQL opcional para console. |
| Banco transacional | PostgreSQL. |
| Cache/locks | Redis. |
| Event bus | NATS JetStream para simplicidade; Kafka para escala e retenção pesada. |
| Object storage | S3 ou MinIO local. |
| Browser automation | Playwright. |
| Containers | Docker e Kubernetes. |
| IaC | Terraform. |
| Deploy K8s | Helm ou Kustomize. |
| Observabilidade | OpenTelemetry, Prometheus, Grafana, Loki/ELK, Tempo/Jaeger. |
| Auth | OIDC/OAuth2, Keycloak, Auth0, Entra ID ou IdP corporativo. |
| Policy | OPA/Rego ou motor próprio simples inicialmente. |

### Recomendação pragmática inicial

- **TypeScript** para MCP Server, API, CLI, SDK de plugins e workers iniciais.
- **PostgreSQL + Redis + NATS JetStream + MinIO** para stack local e produção inicial.
- **Playwright** para automação Web.
- **OpenAPI + Zod/JSON Schema** para contratos.
- **OpenTelemetry** desde o primeiro dia.

---

## 15. Trade-offs da arquitetura

| Decisão | Benefício | Custo/risco |
|---|---|---|
| Event-driven | Escala, desacoplamento e resiliência. | Maior complexidade operacional e consistência eventual. |
| Plugins isolados | Extensibilidade e segurança. | Overhead de runtime e versionamento. |
| PostgreSQL central | Consistência e simplicidade. | Pode exigir particionamento/otimização em grande escala. |
| Object storage para evidências | Baixo custo e escala. | Latência maior que banco local. |
| MCP + API HTTP | Integra IA e sistemas tradicionais. | Dois contratos públicos a manter. |
| Clean Architecture | Testabilidade e evolução. | Mais camadas e boilerplate. |
| Kubernetes | Autoscaling e isolamento. | Complexidade de plataforma. |
| OPA/Rego | Policies declarativas poderosas. | Curva de aprendizado para times. |

---

## 16. Escalabilidade

### Estratégias

- Workers stateless e horizontalmente escaláveis.
- Filas particionadas por prioridade, tenant e tipo de teste.
- Backpressure por tenant e por destino para evitar abuso.
- Rate limit global, por projeto, por target e por plugin.
- Autoscaling baseado em tamanho da fila, CPU, memória e duração média de jobs.
- Separação de jobs leves e pesados.
- Sharding lógico de tenants em filas ou namespaces.
- Particionamento de tabelas por data e tenant para `scan_executions`, `plugin_executions` e `findings`.
- Storage frio para evidências antigas.
- Cache para catálogos de plugins, policies e status frequentes.

### Capacidade alvo

Para milhares de execuções diárias:

- Control plane com 2 a 5 réplicas por serviço crítico.
- Workers autoscaláveis de 0 a N conforme backlog.
- Cada execução deve ser dividida em jobs independentes quando possível.
- Retenção configurável para artefatos pesados.
- Limites de concorrência por tenant para fairness.

### Padrões de resiliência

- Idempotency keys em comandos e jobs.
- Retry com exponential backoff e jitter.
- Dead-letter queues para jobs inválidos.
- Circuit breakers para scanners externos e integrações.
- Checkpointing para scans longos.
- Cancelamento cooperativo de jobs.
- Reprocessamento seguro de eventos.

---

## 17. Segurança

### Controles fundamentais

- OIDC/OAuth2 com RBAC e ABAC.
- mTLS entre serviços sensíveis.
- Criptografia em trânsito e em repouso.
- Segregação por tenant em dados, filas, objetos e permissões.
- Auditoria imutável para ações críticas.
- Gestão centralizada de secrets.
- Least privilege em contas de serviço.
- Validação rigorosa de escopo para evitar SSRF e scans não autorizados.
- Allowlist de domínios, CIDRs e ambientes.
- Bloqueio padrão para localhost, link-local, metadata endpoints e redes privadas.
- Isolamento de plugins por container/sandbox.
- Egress control por policy de rede.
- Assinatura e verificação de plugins.
- Sanitização de logs e redaction de secrets.
- Retenção e descarte seguro de evidências.

### Ameaças prioritárias

| Ameaça | Mitigação |
|---|---|
| Uso da plataforma para atacar terceiros | Allowlist, aprovação de escopo, rate limit e auditoria. |
| SSRF via target malicioso | Validação DNS/IP, bloqueio de ranges sensíveis e resolução controlada. |
| Plugin malicioso | Assinatura, sandbox, permissões mínimas e revisão. |
| Vazamento de secrets | Secret manager, redaction e tokens efêmeros. |
| Exfiltração de evidências | IAM granular, criptografia e expiração. |
| DoS em aplicações alvo | Rate limit por alvo, perfil de teste seguro e janelas de execução. |
| Cross-tenant access | Filtros obrigatórios por tenant, testes de autorização e segregação. |

---

## 18. Observabilidade

### Métricas

- Total de scans criados, em execução, concluídos e falhos.
- Duração média/p95/p99 por tipo de scan e plugin.
- Tamanho de filas e idade do job mais antigo.
- Taxa de falha por plugin.
- Findings por severidade, tenant, projeto e tipo.
- Uso de CPU/memória por worker.
- Erros de integração externa.
- Quality gates aprovados/reprovados.
- Custo estimado por execução quando aplicável.

### Logs

- JSON estruturado.
- `correlation_id`, `scan_id`, `tenant_id`, `project_id`, `plugin_id`.
- Redaction automática de tokens, cookies, authorization headers e payloads sensíveis.
- Separação entre logs operacionais e evidências.

### Traces

- Trace distribuído do create scan até o report final.
- Spans para seleção de plugins, execução, armazenamento e policy evaluation.
- Propagação de contexto por eventos.

### Alertas

- Backlog de fila acima do limite.
- Falha elevada de plugins críticos.
- Latência p95 de execução fora do SLA.
- Object storage indisponível.
- Erros de autenticação anômalos.
- Tentativas bloqueadas por validação de escopo.
- Queda na geração de relatórios.

---

## 19. Estratégia de deploy

### Ambientes

- **Local**: Docker Compose com serviços mínimos.
- **Development**: namespace Kubernetes compartilhado ou compose avançado.
- **Staging**: próximo de produção, com dados sintéticos e scanners completos.
- **Production**: Kubernetes multi-AZ, managed DB, object storage gerenciado e observabilidade centralizada.

### Componentes em produção

- API Gateway/WAF.
- MCP Server com réplicas stateless.
- API Server com réplicas stateless.
- Orchestrator com concorrência controlada.
- Worker pools separados por tipo de carga.
- PostgreSQL gerenciado com backups e replicas.
- Redis gerenciado.
- NATS/Kafka gerenciado ou altamente disponível.
- Object storage com lifecycle policies.
- Secret manager corporativo.

### Estratégias de release

- Blue/green ou rolling update para serviços stateless.
- Canary para novos plugins.
- Feature flags para capabilities novas.
- Migrações versionadas e reversíveis sempre que possível.
- Backward compatibility em eventos e schemas.

---

## 20. Execução local e Docker

### Execução local mínima

```text
Developer Machine
├─ mcp-server
├─ api-server
├─ worker
├─ postgres
├─ redis
├─ nats
└─ minio
```

### Docker Compose recomendado

Serviços:

- `securityqa-mcp-server`
- `securityqa-api-server`
- `securityqa-worker`
- `postgres`
- `redis`
- `nats`
- `minio`
- `otel-collector`
- `prometheus`
- `grafana`

### Perfis de execução

- `minimal`: API, MCP, worker, PostgreSQL, Redis e NATS.
- `observability`: adiciona OpenTelemetry, Prometheus e Grafana.
- `scanner-full`: adiciona ZAP, browser sandbox e scanners externos.
- `devtools`: adiciona mocks, seed data e viewers de fila/storage.

### Configuração

- Variáveis de ambiente para endpoints e credenciais.
- Arquivo `.env.example` versionado.
- Secrets reais nunca versionados.
- Seeds sintéticos para testes locais.

---

## 21. Estratégia de CI/CD

### Pipeline de pull request

1. Instalação e cache de dependências.
2. Lint e formatação.
3. Testes unitários.
4. Testes de contrato de APIs, eventos e plugins.
5. Testes de integração com PostgreSQL, Redis, NATS e MinIO.
6. SAST e secret scanning.
7. Dependency scanning e SBOM.
8. Build de imagens Docker.
9. Scan de imagens.
10. Testes e2e essenciais.
11. Publicação de artefatos temporários.

### Pipeline de main/release

1. Versionamento semântico.
2. Build reprodutível.
3. Assinatura de imagens e plugins.
4. Publicação de SBOM.
5. Deploy em staging.
6. Testes smoke e regressão.
7. Aprovação manual quando exigido.
8. Deploy canary em produção.
9. Promoção gradual.
10. Monitoramento pós-deploy e rollback automático por SLO.

### Gates recomendados

- Cobertura mínima por camada crítica.
- Nenhum secret detectado.
- Nenhuma vulnerabilidade crítica sem exceção aprovada.
- Contratos MCP/API/eventos compatíveis.
- Imagens assinadas.
- Plugins assinados e aprovados.

---

## 22. Estratégia de dados

### PostgreSQL

Tabelas principais:

- `tenants`
- `projects`
- `targets`
- `scan_requests`
- `scan_executions`
- `plugin_definitions`
- `plugin_executions`
- `findings`
- `finding_instances`
- `evidences`
- `policies`
- `reports`
- `audit_logs`

### Object storage

Prefixos sugeridos:

```text
s3://securityqa-evidence/{tenant_id}/{project_id}/{scan_id}/raw/
s3://securityqa-evidence/{tenant_id}/{project_id}/{scan_id}/screenshots/
s3://securityqa-evidence/{tenant_id}/{project_id}/{scan_id}/har/
s3://securityqa-evidence/{tenant_id}/{project_id}/{scan_id}/reports/
```

### Retenção

- Evidências brutas: 30 a 90 dias por padrão.
- Relatórios: 1 a 7 anos conforme compliance.
- Audit logs: política corporativa, preferencialmente WORM/imutável.
- Findings normalizados: retenção longa para tendência histórica.

---

## 23. Estratégia de qualidade

### Tipos de teste

- Unitários para domínio e application layer.
- Contrato para MCP tools, API e eventos.
- Integração para adapters.
- E2E para fluxos de scan completos.
- Performance para filas e workers.
- Segurança para autenticação, autorização, SSRF e isolamento de plugins.
- Chaos testing para event bus, object storage e worker failures.

### Critérios de aceitação arquitetural

- Domínio não importa infraestrutura.
- Use cases dependem de portas, não de adaptadores concretos.
- Plugins não acessam banco diretamente.
- Todo job é idempotente.
- Todo evento tem schema versionado.
- Todo scan tem correlation id.
- Toda evidência tem hash e política de retenção.
- Toda execução de plugin tem timeout e limites.

---

## 24. Roadmap arquitetural sugerido

### Fase 1 — MVP operacional

- MCP Server básico.
- API de criação e consulta de scans.
- Worker único.
- PostgreSQL, Redis, NATS e MinIO.
- Plugins: security headers, TLS audit e OpenAPI passive checks.
- Relatório JSON/Markdown.
- Docker Compose.

### Fase 2 — Escala e governança

- Worker pool autoscalável.
- Plugin registry com versionamento.
- Policy engine.
- Deduplicação de findings.
- OpenTelemetry completo.
- Integração CI/CD com SARIF.

### Fase 3 — Enterprise

- Multi-tenancy avançado.
- RBAC/ABAC e OIDC corporativo.
- Assinatura de plugins.
- Auditoria imutável.
- Kubernetes/Helm.
- Integrações Jira, GitHub, GitLab, Slack/Teams e SIEM.

### Fase 4 — Otimização avançada

- Priorização por risco.
- Aprendizado com histórico.
- Planejamento inteligente de testes.
- Sharding de filas por tenant.
- SLOs por classe de serviço.
- Marketplace interno de plugins.

---

## 25. Decisões arquiteturais iniciais recomendadas

1. Adotar monorepo para reduzir fricção inicial entre core, apps, SDK e plugins.
2. Manter domínio e contratos independentes de frameworks.
3. Usar NATS JetStream inicialmente pela simplicidade operacional.
4. Usar PostgreSQL como fonte da verdade transacional.
5. Usar S3/MinIO para qualquer evidência pesada.
6. Tornar todo plugin executável em sandbox desde o início.
7. Versionar schemas MCP, API, eventos e findings.
8. Implementar observabilidade desde o MVP.
9. Bloquear targets não autorizados por padrão.
10. Separar control plane de execution plane antes da escala real.

---

## 26. Definition of Done arquitetural

A arquitetura pode ser considerada pronta para implementação quando:

- Os contratos MCP/API/eventos estiverem versionados.
- O modelo de domínio estiver validado com cenários reais.
- As portas e adaptadores principais estiverem definidos.
- A estratégia de plugin estiver documentada e testável.
- As policies de segurança de target e sandbox estiverem claras.
- O fluxo de execução assíncrona estiver coberto por testes de contrato.
- A observabilidade mínima estiver definida por métrica, log e trace.
- O deploy local em Docker estiver especificado.
- O pipeline CI/CD tiver gates de qualidade e segurança.
- As decisões principais estiverem registradas como ADRs.

### Documentos complementares

- [Documentação funcional corporativa](docs/product/functional-documentation.md)
- [Arquitetura técnica do sistema](docs/architecture/technical-architecture.md)
- [Projeto de banco de dados enterprise](docs/architecture/database-design.md)

## Documentação complementar

- [Projeto da API REST Enterprise](docs/api-rest-enterprise.md): endpoints, DTOs, validações, paginação, filtros, autenticação, OAuth2/JWT, OpenAPI/Swagger, erros, rate limit, idempotência, auditoria e logs.
