# Security QA MCP — Arquitetura Técnica do Sistema

## 1. Objetivo deste documento

Este documento modela a estrutura técnica do **Security QA MCP** para orientar a implementação sem prescrever código. A proposta usa Clean Architecture, Hexagonal Architecture e DDD pragmático para separar regras de negócio, casos de uso, adaptadores, contratos e pontos de entrada.

A arquitetura técnica define:

- Estrutura de pastas do monorepo.
- Organização dos packages.
- Camadas e dependências permitidas.
- Interfaces, entidades, DTOs, casos de uso e serviços.
- Repositórios, adaptadores, gateways e configurações.
- Eventos, exceptions, middlewares, builders, factories, validators, helpers e utilitários.
- Responsabilidade de cada classe ou contrato conceitual.

## 2. Regras de dependência entre camadas

```text
apps/* ────────────────┐
adapters/* ────────────┼──▶ packages/application ───▶ packages/domain ───▶ packages/shared-kernel
plugins/* ─────────────┘              │                         ▲
                                      ▼                         │
                              packages/contracts                │
                                      ▲                         │
packages/plugin-sdk ─────────────────┘                         │
```

### 2.1 Camadas

| Camada | Local | Responsabilidade | Pode depender de | Não pode depender de |
|---|---|---|---|---|
| Interfaces de entrada | `apps/*` | Receber chamadas MCP, HTTP, CLI, worker e UI. | `application`, `contracts`, `shared-kernel` | Regras internas de adaptadores concretos. |
| Application | `packages/application` | Orquestrar casos de uso, transações, policies e portas. | `domain`, `contracts`, `shared-kernel` | Frameworks HTTP, bancos, filas e SDKs externos. |
| Domain | `packages/domain` | Regras de negócio puras, entidades, value objects e eventos de domínio. | `shared-kernel` | Application, infrastructure, frameworks e I/O. |
| Contracts | `packages/contracts` | Schemas públicos versionados para API, MCP, eventos e plugins. | `shared-kernel` | Implementações de domínio ou infraestrutura. |
| Infrastructure | `adapters/*` | Implementar portas de saída com tecnologias concretas. | `application`, `domain`, `contracts`, `shared-kernel` | Apps específicos, exceto composição explícita. |
| Plugin SDK | `packages/plugin-sdk` | Definir contrato de criação de plugins. | `contracts`, `shared-kernel` | Core interno de application/domain. |
| Plugins | `plugins/*` | Implementar capacidades de teste isoladas. | `plugin-sdk`, `contracts`, `shared-kernel` | Banco, filas e domínio interno. |

### 2.2 Regras técnicas obrigatórias

- O domínio não realiza I/O.
- Casos de uso dependem de interfaces, nunca de adaptadores concretos.
- Adaptadores convertem modelos externos para modelos de aplicação ou contratos.
- DTOs de API/MCP não são entidades de domínio.
- Plugins retornam resultados canônicos por contrato, sem persistir diretamente.
- Eventos publicados fora do processo usam schemas versionados.
- Cada comando mutável deve ser idempotente quando acionado por API, MCP ou fila.

## 3. Estrutura de pastas

```text
security-qa-mcp/
├─ apps/
│  ├─ mcp-server/
│  │  └─ src/
│  │     ├─ tools/
│  │     ├─ resources/
│  │     ├─ prompts/
│  │     ├─ mappers/
│  │     ├─ middlewares/
│  │     └─ bootstrap/
│  ├─ api-server/
│  │  └─ src/
│  │     ├─ controllers/
│  │     ├─ routes/
│  │     ├─ middlewares/
│  │     ├─ presenters/
│  │     ├─ mappers/
│  │     └─ bootstrap/
│  ├─ worker/
│  │  └─ src/
│  │     ├─ consumers/
│  │     ├─ handlers/
│  │     ├─ schedulers/
│  │     ├─ processors/
│  │     └─ bootstrap/
│  ├─ cli/
│  │  └─ src/
│  │     ├─ commands/
│  │     ├─ formatters/
│  │     └─ bootstrap/
│  └─ web-console/
│     └─ src/
│        ├─ pages/
│        ├─ components/
│        ├─ features/
│        ├─ clients/
│        └─ state/
├─ packages/
│  ├─ domain/
│  │  └─ src/
│  │     ├─ identity-tenancy/
│  │     │  ├─ entities/
│  │     │  ├─ value-objects/
│  │     │  ├─ events/
│  │     │  ├─ services/
│  │     │  └─ repositories/
│  │     ├─ scan-management/
│  │     ├─ security-testing/
│  │     ├─ findings/
│  │     ├─ policy-gates/
│  │     ├─ reporting/
│  │     ├─ plugin-management/
│  │     ├─ audit-compliance/
│  │     └─ shared/
│  ├─ application/
│  │  └─ src/
│  │     ├─ use-cases/
│  │     ├─ commands/
│  │     ├─ queries/
│  │     ├─ dto/
│  │     ├─ ports/
│  │     │  ├─ inbound/
│  │     │  └─ outbound/
│  │     ├─ services/
│  │     ├─ validators/
│  │     ├─ mappers/
│  │     ├─ policies/
│  │     └─ events/
│  ├─ contracts/
│  │  └─ src/
│  │     ├─ api/
│  │     ├─ mcp/
│  │     ├─ events/
│  │     ├─ plugins/
│  │     ├─ reports/
│  │     └─ schemas/
│  ├─ plugin-sdk/
│  │  └─ src/
│  │     ├─ interfaces/
│  │     ├─ builders/
│  │     ├─ validators/
│  │     ├─ helpers/
│  │     └─ testing/
│  ├─ shared-kernel/
│  │  └─ src/
│  │     ├─ primitives/
│  │     ├─ errors/
│  │     ├─ result/
│  │     ├─ clock/
│  │     ├─ ids/
│  │     ├─ logging/
│  │     └─ utils/
│  └─ test-fixtures/
│     └─ src/
│        ├─ builders/
│        ├─ factories/
│        ├─ mocks/
│        └─ samples/
├─ adapters/
│  ├─ persistence-postgres/
│  ├─ event-bus-nats/
│  ├─ cache-redis/
│  ├─ object-storage-s3/
│  ├─ secrets-vault/
│  ├─ browser-playwright/
│  ├─ http-client/
│  ├─ scanner-zap/
│  ├─ scanner-nuclei/
│  ├─ policy-opa/
│  ├─ observability-otel/
│  └─ notifications-webhook/
├─ plugins/
│  ├─ security-headers/
│  ├─ tls-audit/
│  ├─ openapi-fuzzer/
│  ├─ authz-checker/
│  └─ passive-api-analyzer/
├─ deploy/
│  ├─ docker/
│  ├─ compose/
│  ├─ helm/
│  └─ terraform/
├─ docs/
│  ├─ architecture/
│  ├─ adr/
│  ├─ product/
│  ├─ threat-model/
│  └─ runbooks/
└─ tests/
   ├─ unit/
   ├─ integration/
   ├─ contract/
   ├─ e2e/
   └─ performance/
```

## 4. Organização dos packages

### 4.1 `packages/shared-kernel`

Package com abstrações transversais pequenas e estáveis.

| Classe/Contrato | Responsabilidade |
|---|---|
| `EntityId` | Representar identificadores fortemente tipados. |
| `TenantId`, `ProjectId`, `ScanId`, `FindingId`, `PluginId`, `ReportId` | Evitar troca acidental de IDs entre agregados. |
| `AggregateRoot` | Base conceitual para agregados que registram eventos de domínio. |
| `DomainEvent` | Contrato base para eventos internos do domínio. |
| `Result<T>` | Representar sucesso/falha sem lançar exceções em fluxos esperados. |
| `ErrorCode` | Padronizar códigos de erro funcionais e técnicos. |
| `Clock` | Abstrair obtenção de data/hora para testabilidade. |
| `IdGenerator` | Gerar UUID/ULID de forma substituível. |
| `CorrelationContext` | Carregar `correlation_id`, ator e origem entre camadas. |
| `Pagination` | Representar paginação em queries. |
| `Sort` | Representar ordenação em queries. |
| `RedactionHelper` | Mascarar tokens, cookies, headers e payloads sensíveis. |
| `HashHelper` | Calcular hashes de evidências e fingerprints. |
| `UrlHelper` | Normalizar URLs sem validar autorização de negócio. |
| `DateRange` | Representar intervalos de tempo válidos. |

### 4.2 `packages/contracts`

Package com contratos versionados consumidos por apps, plugins e integrações.

| Classe/Contrato | Responsabilidade |
|---|---|
| `CreateScanRequestSchema` | Definir payload público para criação de scan. |
| `CreateScanResponseSchema` | Definir resposta pública com IDs e status inicial. |
| `ScanStatusResponseSchema` | Definir visão consultável do andamento do scan. |
| `FindingResponseSchema` | Definir formato público de achado. |
| `EvidenceResponseSchema` | Definir metadados públicos de evidência. |
| `QualityGateResponseSchema` | Definir decisão de gate e motivos. |
| `PluginManifestSchema` | Definir manifesto de plugin, versão, capabilities e permissões. |
| `PluginInputSchema` | Definir entrada padronizada para execução de plugin. |
| `PluginOutputSchema` | Definir saída padronizada de plugin. |
| `SecurityFindingSchema` | Definir formato canônico de finding bruto ou normalizado. |
| `ScanRequestedEventSchema` | Definir evento de integração para scan solicitado. |
| `PluginExecutionCompletedEventSchema` | Definir evento de conclusão de plugin. |
| `FindingDiscoveredEventSchema` | Definir evento de achado descoberto. |
| `ReportGeneratedEventSchema` | Definir evento de relatório gerado. |
| `SarifExportSchema` | Definir compatibilidade de exportação SARIF. |

### 4.3 `packages/domain`

Package com regras puras por bounded context.

#### Identity & Tenancy

| Classe | Responsabilidade |
|---|---|
| `Tenant` | Agregado de isolamento organizacional, status, quotas e configurações base. |
| `Project` | Agregado que agrupa alvos, policies, integrações e permissões. |
| `User` | Representar usuário conhecido e seus vínculos de acesso. |
| `ServiceAccount` | Representar identidade técnica usada por pipelines e integrações. |
| `Role` | Representar conjunto de permissões por tenant ou projeto. |
| `Permission` | Representar ação autorizável granular. |
| `AccessPolicy` | Avaliar se um ator pode executar uma ação sobre um recurso. |
| `TenantQuota` | Controlar limites de concorrência, volume e retenção. |

#### Scan Management

| Classe | Responsabilidade |
|---|---|
| `Target` | Agregado de aplicação ou API autorizada para varredura. |
| `WebTarget` | Especialização conceitual de alvo baseado em URL Web. |
| `ApiTarget` | Especialização conceitual de alvo baseado em OpenAPI/GraphQL. |
| `ScanScope` | Value object com hosts, rotas, métodos, limites e exclusões permitidos. |
| `ScanRequest` | Representar intenção de scan criada por usuário, MCP, API ou CI. |
| `ScanExecution` | Agregado de execução concreta, status, progresso, timestamps e resultado. |
| `ScanPlan` | Plano derivado contendo plugins, etapas, dependências e limites. |
| `ScanStatus` | Value object/enumerador de estados permitidos. |
| `ScanProfile` | Perfil de intensidade, timeout, concorrência e profundidade. |
| `CancellationReason` | Motivo rastreável de cancelamento. |
| `ScanStateMachine` | Garantir transições válidas de status. |

#### Security Testing

| Classe | Responsabilidade |
|---|---|
| `PluginDefinition` | Agregado de plugin registrado com manifesto, versão e assinatura. |
| `PluginCapability` | Value object que descreve capacidade técnica do plugin. |
| `PluginPermission` | Value object de permissão de rede, filesystem, secrets e recursos. |
| `PluginExecution` | Entidade de execução individual de plugin dentro de um scan. |
| `SandboxPolicy` | Regras de isolamento, CPU, memória, rede e filesystem. |
| `TestStep` | Etapa planejada de teste executável. |
| `TestPayload` | Payload controlado usado por fuzzing ou validação. |
| `RawScannerResult` | Resultado bruto antes de normalização. |

#### Findings

| Classe | Responsabilidade |
|---|---|
| `Finding` | Agregado canônico de vulnerabilidade ou fragilidade detectada. |
| `FindingInstance` | Ocorrência concreta de um finding em target, rota ou parâmetro. |
| `Evidence` | Entidade de evidência com hash, tipo, localização e retenção. |
| `Severity` | Value object de severidade normalizada. |
| `Confidence` | Value object de confiança do achado. |
| `CvssVector` | Value object de vetor CVSS validado. |
| `CweId` | Value object para referência CWE. |
| `OwaspCategory` | Value object para categorização OWASP. |
| `FindingFingerprint` | Assinatura técnica usada para deduplicação. |
| `FindingLifecycle` | Máquina de estados para triagem, correção, falso positivo e reabertura. |
| `RemediationGuidance` | Recomendações técnicas associadas ao finding. |

#### Policy & Gates

| Classe | Responsabilidade |
|---|---|
| `Policy` | Agregado de regras versionadas de avaliação de risco. |
| `PolicyRule` | Regra individual baseada em severidade, tipo, ambiente ou contexto. |
| `PolicyException` | Exceção aprovada com escopo, justificativa, aprovador e expiração. |
| `QualityGate` | Definição de decisão go/no-go para pipeline ou release. |
| `QualityGateDecision` | Resultado determinístico da avaliação. |
| `RiskScore` | Value object de pontuação agregada de risco. |
| `Threshold` | Value object de limite configurável. |

#### Reporting

| Classe | Responsabilidade |
|---|---|
| `Report` | Agregado de artefato gerado e seus metadados. |
| `ReportTemplate` | Modelo de relatório técnico, executivo ou auditoria. |
| `ReportFormat` | Value object para JSON, SARIF, HTML, Markdown ou PDF. |
| `ReportSection` | Componente estrutural reutilizável do relatório. |
| `ExportPackage` | Pacote de exportação com relatórios, evidências e manifesto de integridade. |

#### Audit & Compliance

| Classe | Responsabilidade |
|---|---|
| `AuditLog` | Registro imutável de ação relevante. |
| `AuditActor` | Usuário, serviço ou sistema que realizou ação. |
| `AuditResource` | Recurso afetado por ação auditada. |
| `RetentionPolicy` | Regra de retenção de evidências, relatórios e logs. |
| `DataClassification` | Classificação de sensibilidade da informação. |

### 4.4 `packages/application`

Package responsável por orquestração e casos de uso.

#### Commands

| Classe | Responsabilidade |
|---|---|
| `CreateScanCommand` | Carregar dados necessários para solicitar scan. |
| `CancelScanCommand` | Carregar dados necessários para cancelar execução. |
| `RegisterTargetCommand` | Carregar dados para registrar alvo autorizado. |
| `RegisterPluginCommand` | Carregar manifesto e assinatura de plugin. |
| `EvaluatePolicyCommand` | Carregar contexto para avaliação manual ou automática de policy. |
| `GenerateReportCommand` | Carregar parâmetros de geração de relatório. |
| `RequestPolicyExceptionCommand` | Carregar justificativa e escopo de exceção. |
| `ApprovePolicyExceptionCommand` | Carregar decisão de aprovação de exceção. |

#### Queries

| Classe | Responsabilidade |
|---|---|
| `GetScanStatusQuery` | Solicitar estado e progresso de execução. |
| `ListScansQuery` | Consultar scans com filtros e paginação. |
| `ListFindingsQuery` | Consultar findings por tenant, projeto, scan, severidade e status. |
| `GetFindingQuery` | Consultar detalhe de finding e evidências. |
| `ListPluginsQuery` | Consultar catálogo e capabilities de plugins. |
| `GetReportQuery` | Consultar relatório ou metadados de exportação. |
| `GetAuditTrailQuery` | Consultar trilha de auditoria filtrada. |

#### DTOs

| Classe | Responsabilidade |
|---|---|
| `ScanRequestDto` | Representar entrada de criação de scan após adaptação externa. |
| `ScanExecutionDto` | Representar execução para respostas e integrações. |
| `ScanPlanDto` | Expor plano de execução para auditoria ou debug. |
| `FindingDto` | Representar finding normalizado para leitura. |
| `EvidenceDto` | Representar metadados de evidência sem conteúdo sensível. |
| `PluginDefinitionDto` | Representar plugin registrado. |
| `QualityGateDecisionDto` | Representar decisão de gate. |
| `ReportDto` | Representar relatório gerado. |
| `AuditLogDto` | Representar evento de auditoria para consulta. |
| `PageDto<T>` | Representar resultado paginado. |
| `ErrorDto` | Representar erro padronizado para apps. |

#### Casos de uso

| Classe | Responsabilidade |
|---|---|
| `CreateScanUseCase` | Validar ator, target, escopo, quotas e criar execução pendente. |
| `PlanScanUseCase` | Resolver plugins, dependências, limites e gerar plano executável. |
| `StartScanUseCase` | Publicar jobs iniciais e mover execução para estado ativo. |
| `CancelScanUseCase` | Solicitar cancelamento cooperativo e preservar consistência. |
| `CompleteScanUseCase` | Consolidar resultados, avaliar policy e finalizar execução. |
| `RegisterTargetUseCase` | Cadastrar alvo autorizado com validação anti-SSRF e governança. |
| `ImportOpenApiTargetUseCase` | Criar alvo de API a partir de contrato OpenAPI. |
| `RegisterPluginUseCase` | Registrar plugin após validar manifesto, assinatura e permissões. |
| `SelectPluginsUseCase` | Selecionar plugins compatíveis com target, policy e perfil. |
| `ExecutePluginUseCase` | Orquestrar execução de plugin via porta `PluginExecutor`. |
| `NormalizeFindingUseCase` | Converter resultados brutos em findings canônicos. |
| `DeduplicateFindingsUseCase` | Agrupar findings equivalentes por fingerprint e contexto. |
| `EvaluatePolicyUseCase` | Avaliar findings, exceções e thresholds para gerar gate. |
| `GenerateReportUseCase` | Produzir relatório técnico, executivo ou formato de máquina. |
| `ExportEvidenceUseCase` | Montar pacote de evidências para auditoria. |
| `RequestPolicyExceptionUseCase` | Criar solicitação de exceção com prazo e justificativa. |
| `ApprovePolicyExceptionUseCase` | Aprovar ou rejeitar exceção com trilha de auditoria. |
| `WriteAuditLogUseCase` | Registrar ações relevantes de forma padronizada. |

#### Serviços de aplicação

| Classe | Responsabilidade |
|---|---|
| `ScanOrchestrationService` | Coordenar sequência de criação, planejamento e publicação de jobs. |
| `PluginSelectionService` | Aplicar matriz de compatibilidade entre target, profile, policy e capabilities. |
| `FindingNormalizationService` | Unificar severidade, categorias, referências e evidências. |
| `FindingCorrelationService` | Correlacionar histórico, recorrência e regressões. |
| `PolicyEvaluationService` | Aplicar regras, exceções e thresholds sem depender de engine concreta. |
| `ReportAssemblyService` | Montar seções e dados antes de renderizar relatório. |
| `EvidenceRedactionService` | Mascarar dados sensíveis antes de armazenamento ou exposição. |
| `AuditService` | Padronizar eventos de auditoria para comandos críticos. |
| `QuotaService` | Verificar limites por tenant, projeto, target e plugin. |
| `IdempotencyService` | Detectar comandos repetidos e retornar resultado consistente. |
| `TransactionService` | Delimitar unidade de trabalho por abstração. |

#### Portas de entrada

| Interface | Responsabilidade |
|---|---|
| `CreateScanInputPort` | Contrato para criação de scan. |
| `CancelScanInputPort` | Contrato para cancelamento de scan. |
| `GetScanStatusInputPort` | Contrato para consulta de status. |
| `ListFindingsInputPort` | Contrato para listagem de findings. |
| `RegisterPluginInputPort` | Contrato para registro de plugin. |
| `GenerateReportInputPort` | Contrato para geração de relatório. |

#### Portas de saída

| Interface | Responsabilidade |
|---|---|
| `TenantRepository` | Persistir e consultar tenants. |
| `ProjectRepository` | Persistir e consultar projetos. |
| `TargetRepository` | Persistir e consultar alvos autorizados. |
| `ScanRequestRepository` | Persistir solicitações de scan. |
| `ScanExecutionRepository` | Persistir execução, progresso e status. |
| `PluginDefinitionRepository` | Persistir catálogo de plugins. |
| `PluginExecutionRepository` | Persistir execuções individuais de plugins. |
| `FindingRepository` | Persistir findings e instâncias. |
| `EvidenceRepository` | Persistir metadados de evidências. |
| `PolicyRepository` | Persistir policies e versões. |
| `PolicyExceptionRepository` | Persistir exceções de policy. |
| `ReportRepository` | Persistir metadados de relatórios. |
| `AuditLogRepository` | Persistir trilhas de auditoria. |
| `EventPublisher` | Publicar eventos de domínio ou integração. |
| `JobQueue` | Enfileirar jobs para workers. |
| `ObjectStorageGateway` | Armazenar e recuperar artefatos pesados. |
| `SecretProviderGateway` | Obter secrets efêmeros e controlados. |
| `PluginExecutorGateway` | Executar plugins em runtime isolado. |
| `HttpClientGateway` | Realizar chamadas HTTP controladas. |
| `BrowserAutomationGateway` | Automatizar navegador e coletar evidências Web. |
| `PolicyEngineGateway` | Avaliar policies em engine externa quando aplicável. |
| `TelemetryGateway` | Registrar métricas, logs e traces. |
| `NotificationGateway` | Enviar webhooks ou mensagens para integrações. |

## 5. Aplicações (`apps/*`)

### 5.1 `apps/mcp-server`

| Classe | Responsabilidade |
|---|---|
| `McpServerBootstrap` | Inicializar servidor MCP, dependências e handlers. |
| `CreateScanTool` | Adaptar chamada MCP para `CreateScanUseCase`. |
| `GetScanStatusTool` | Adaptar consulta MCP para status de execução. |
| `CancelScanTool` | Adaptar cancelamento MCP. |
| `ListFindingsTool` | Adaptar listagem de findings para clientes MCP. |
| `GenerateReportTool` | Adaptar geração de relatório por MCP. |
| `ValidateTargetTool` | Expor validação de alvo antes do scan. |
| `ScanResourceProvider` | Expor `securityqa://scans/{scan_id}`. |
| `FindingResourceProvider` | Expor detalhes de findings e evidências. |
| `ReportResourceProvider` | Expor relatórios gerados. |
| `McpRequestMapper` | Converter payload MCP em commands/queries. |
| `McpResponsePresenter` | Converter DTOs de aplicação em respostas MCP. |
| `McpAuthMiddleware` | Validar identidade e escopos da chamada MCP. |
| `McpCorrelationMiddleware` | Criar e propagar correlation id. |
| `McpErrorMiddleware` | Converter exceptions em erros MCP padronizados. |

### 5.2 `apps/api-server`

| Classe | Responsabilidade |
|---|---|
| `ApiServerBootstrap` | Inicializar servidor HTTP, rotas, middlewares e DI. |
| `ScanController` | Expor endpoints de criação, cancelamento e consulta de scans. |
| `TargetController` | Expor endpoints de gestão de alvos. |
| `FindingController` | Expor endpoints de findings e evidências. |
| `PolicyController` | Expor endpoints de policies, gates e exceções. |
| `PluginController` | Expor endpoints de catálogo e registro de plugins. |
| `ReportController` | Expor endpoints de relatórios e exportações. |
| `AuditController` | Expor consulta autorizada de trilhas de auditoria. |
| `HttpRouteRegistry` | Registrar rotas e versões de API. |
| `HttpRequestMapper` | Converter requests HTTP em commands/queries. |
| `HttpResponsePresenter` | Converter DTOs em respostas HTTP. |
| `AuthMiddleware` | Autenticar JWT, API key, mTLS ou token de serviço. |
| `AuthorizationMiddleware` | Autorizar operação por tenant/projeto/recurso. |
| `RateLimitMiddleware` | Aplicar limites por ator, tenant e endpoint. |
| `ValidationMiddleware` | Validar schema de entrada. |
| `ErrorHandlingMiddleware` | Converter exceptions em `ErrorDto`. |
| `AuditMiddleware` | Registrar ações administrativas e operacionais relevantes. |

### 5.3 `apps/worker`

| Classe | Responsabilidade |
|---|---|
| `WorkerBootstrap` | Inicializar consumidores, registradores e dependências. |
| `ScanRequestedConsumer` | Consumir evento de scan solicitado e iniciar planejamento. |
| `PluginExecutionConsumer` | Consumir jobs de execução de plugin. |
| `FindingDiscoveredConsumer` | Consumir achados para normalização/correlação. |
| `ReportGenerationConsumer` | Consumir solicitações de geração de relatório. |
| `PluginJobHandler` | Coordenar sandbox, execução e coleta de resultado. |
| `ScanCompletionProcessor` | Consolidar estado final de execução. |
| `RetryScheduler` | Reagendar jobs transitórios com backoff. |
| `DeadLetterHandler` | Tratar jobs inválidos ou definitivamente falhos. |
| `CancellationWatcher` | Interromper jobs quando houver cancelamento cooperativo. |
| `WorkerHealthProbe` | Expor readiness/liveness operacional. |

### 5.4 `apps/cli`

| Classe | Responsabilidade |
|---|---|
| `CliBootstrap` | Inicializar comandos e configuração local. |
| `CreateScanCommandHandler` | Permitir criação de scan via terminal. |
| `ScanStatusCommandHandler` | Consultar status via terminal. |
| `ListFindingsCommandHandler` | Listar findings em tabela, JSON ou Markdown. |
| `GenerateReportCommandHandler` | Solicitar relatório via terminal. |
| `CliConfigLoader` | Carregar endpoint, token e preferências locais. |
| `CliOutputFormatter` | Renderizar saída humana ou máquina. |

## 6. Adaptadores (`adapters/*`)

| Adaptador | Classe principal | Responsabilidade |
|---|---|---|
| `persistence-postgres` | `PostgresScanExecutionRepository` | Implementar persistência de scans em PostgreSQL. |
| `persistence-postgres` | `PostgresFindingRepository` | Persistir e consultar findings, instâncias e filtros. |
| `persistence-postgres` | `PostgresPolicyRepository` | Persistir policies versionadas e exceções. |
| `persistence-postgres` | `PostgresUnitOfWork` | Implementar transações por unidade de trabalho. |
| `event-bus-nats` | `NatsEventPublisher` | Publicar eventos em NATS JetStream. |
| `event-bus-nats` | `NatsJobQueue` | Enfileirar e consumir jobs de execução. |
| `cache-redis` | `RedisIdempotencyStore` | Guardar chaves de idempotência. |
| `cache-redis` | `RedisRateLimitStore` | Contabilizar limites distribuídos. |
| `object-storage-s3` | `S3ObjectStorageGateway` | Armazenar evidências, relatórios e artefatos. |
| `secrets-vault` | `VaultSecretProviderGateway` | Resolver secrets efêmeros com menor privilégio. |
| `browser-playwright` | `PlaywrightBrowserGateway` | Executar navegação controlada e coletar screenshots/HAR. |
| `http-client` | `SafeHttpClientGateway` | Realizar chamadas HTTP com bloqueios anti-SSRF. |
| `scanner-zap` | `ZapPluginExecutorAdapter` | Encapsular OWASP ZAP como executor compatível. |
| `scanner-nuclei` | `NucleiPluginExecutorAdapter` | Encapsular Nuclei como executor compatível. |
| `policy-opa` | `OpaPolicyEngineGateway` | Delegar avaliação de policy para OPA/Rego. |
| `observability-otel` | `OpenTelemetryGateway` | Emitir traces, métricas e logs correlacionados. |
| `notifications-webhook` | `WebhookNotificationGateway` | Enviar eventos para sistemas externos. |

## 7. Gateways

Gateways são portas de saída orientadas a capacidades externas.

| Gateway | Responsabilidade |
|---|---|
| `ObjectStorageGateway` | Armazenar, baixar, assinar URL temporária e validar hash de artefatos. |
| `SecretProviderGateway` | Entregar credenciais temporárias sem expor secrets permanentes. |
| `PluginExecutorGateway` | Executar plugin nativo, container ou scanner externo. |
| `BrowserAutomationGateway` | Abstrair Playwright ou alternativa de navegador. |
| `HttpClientGateway` | Abstrair cliente HTTP seguro com DNS pinning e egress control. |
| `PolicyEngineGateway` | Abstrair OPA ou motor próprio de policies. |
| `TelemetryGateway` | Abstrair emissão de métricas, logs e traces. |
| `NotificationGateway` | Abstrair Slack, Teams, Jira, GitHub, SIEM ou webhooks. |
| `CiCdGateway` | Abstrair callbacks e statuses para pipelines. |
| `IssueTrackerGateway` | Criar e atualizar tickets de remediação. |

## 8. Configurações

| Classe | Responsabilidade |
|---|---|
| `AppConfig` | Agregar configuração geral da aplicação. |
| `ServerConfig` | Definir porta, host, timeouts e limites HTTP/MCP. |
| `DatabaseConfig` | Definir conexão, pool, SSL e migrações do banco. |
| `EventBusConfig` | Definir brokers, subjects/topics, durable consumers e retries. |
| `ObjectStorageConfig` | Definir bucket, região, criptografia e lifecycle. |
| `RedisConfig` | Definir conexão, TTLs e prefixos de cache. |
| `AuthConfig` | Definir issuer OIDC, audiences, JWKS e escopos. |
| `TenantIsolationConfig` | Definir estratégia de segregação por tenant. |
| `PluginRuntimeConfig` | Definir limites padrão de sandbox. |
| `ScannerConfig` | Definir parâmetros de scanners externos. |
| `SecurityConfig` | Definir allowlists, denylists, ranges bloqueados e redaction. |
| `ObservabilityConfig` | Definir service name, exporters e sampling. |
| `ConfigLoader` | Carregar env vars, arquivos e defaults. |
| `ConfigValidator` | Validar configuração na inicialização. |

## 9. Eventos

### 9.1 Eventos de domínio

| Evento | Responsabilidade |
|---|---|
| `TenantCreated` | Indicar criação de tenant. |
| `ProjectCreated` | Indicar criação de projeto. |
| `TargetRegistered` | Indicar novo alvo autorizado. |
| `ScanRequested` | Indicar intenção de scan aceita pelo domínio. |
| `ScanPlanned` | Indicar plano de execução definido. |
| `ScanStarted` | Indicar início real de execução. |
| `PluginExecutionStarted` | Indicar início de plugin. |
| `PluginExecutionCompleted` | Indicar fim bem-sucedido de plugin. |
| `PluginExecutionFailed` | Indicar falha de plugin. |
| `FindingDiscovered` | Indicar descoberta de achado. |
| `FindingDeduplicated` | Indicar associação a finding canônico. |
| `PolicyEvaluated` | Indicar avaliação de policy concluída. |
| `QualityGatePassed` | Indicar gate aprovado. |
| `QualityGateFailed` | Indicar gate reprovado. |
| `ReportGenerated` | Indicar relatório disponível. |
| `ScanCompleted` | Indicar scan concluído. |
| `ScanFailed` | Indicar scan encerrado com falha. |
| `ScanCancelled` | Indicar scan cancelado. |

### 9.2 Eventos de integração

| Evento | Responsabilidade |
|---|---|
| `scan.requested.v1` | Acionar orquestração assíncrona. |
| `scan.planned.v1` | Acionar criação de jobs de plugin. |
| `plugin.execution.requested.v1` | Solicitar execução de plugin por worker. |
| `plugin.execution.completed.v1` | Informar saída de plugin. |
| `finding.discovered.v1` | Acionar normalização/correlação. |
| `quality_gate.evaluated.v1` | Notificar pipelines e integrações. |
| `report.generated.v1` | Notificar disponibilidade de relatório. |
| `audit.recorded.v1` | Exportar trilhas para SIEM/GRC. |

## 10. Exceptions

| Exception | Responsabilidade |
|---|---|
| `DomainException` | Base para violação de regra de negócio. |
| `ApplicationException` | Base para falhas de orquestração de caso de uso. |
| `InfrastructureException` | Base para falhas técnicas em adaptadores. |
| `ValidationException` | Representar entrada inválida. |
| `AuthenticationException` | Representar ausência ou invalidade de identidade. |
| `AuthorizationException` | Representar acesso negado. |
| `TenantIsolationException` | Representar tentativa de acesso cross-tenant. |
| `TargetOutOfScopeException` | Representar alvo fora do escopo autorizado. |
| `UnsafeTargetException` | Representar target bloqueado por risco SSRF/rede. |
| `QuotaExceededException` | Representar limite excedido. |
| `PluginNotAllowedException` | Representar plugin incompatível ou sem aprovação. |
| `PluginExecutionException` | Representar falha de execução de plugin. |
| `PolicyEvaluationException` | Representar erro ao avaliar policy. |
| `EvidenceStorageException` | Representar falha ao armazenar evidência. |
| `IdempotencyConflictException` | Representar replay incompatível de comando. |
| `ConcurrencyException` | Representar conflito otimista ou lock concorrente. |
| `ConfigurationException` | Representar configuração inválida. |

## 11. Middlewares

| Middleware | Responsabilidade |
|---|---|
| `CorrelationIdMiddleware` | Criar ou propagar correlation id. |
| `RequestLoggingMiddleware` | Registrar início/fim de requisições com redaction. |
| `AuthenticationMiddleware` | Autenticar ator humano ou serviço. |
| `AuthorizationMiddleware` | Validar permissões por recurso. |
| `TenantContextMiddleware` | Resolver tenant e impedir acesso cruzado. |
| `SchemaValidationMiddleware` | Validar payload contra contratos. |
| `RateLimitMiddleware` | Aplicar limites por origem, tenant e rota. |
| `IdempotencyMiddleware` | Controlar repetição de comandos mutáveis. |
| `AuditMiddleware` | Emitir auditoria para ações relevantes. |
| `ErrorMappingMiddleware` | Converter exceptions em resposta padronizada. |
| `SecurityHeadersMiddleware` | Aplicar headers de segurança nas APIs. |
| `TimeoutMiddleware` | Encerrar requisições acima do limite. |
| `MetricsMiddleware` | Emitir métricas por rota/tool/status. |

## 12. Builders

| Builder | Responsabilidade |
|---|---|
| `ScanRequestBuilder` | Construir `ScanRequest` válido em testes e fluxos internos. |
| `ScanPlanBuilder` | Montar plano de execução a partir de plugins e policies. |
| `FindingBuilder` | Criar finding canônico com severidade, evidências e referências. |
| `EvidenceBuilder` | Criar metadados de evidência com hash e classificação. |
| `PolicyBuilder` | Compor policy versionada com regras e thresholds. |
| `QualityGateDecisionBuilder` | Montar decisão com motivos e findings bloqueantes. |
| `ReportBuilder` | Compor relatório por seções. |
| `PluginManifestBuilder` | Auxiliar criação de manifestos de plugin. |
| `AuditLogBuilder` | Padronizar trilhas de auditoria. |
| `TestFixtureBuilder` | Gerar objetos consistentes para testes automatizados. |

## 13. Factories

| Factory | Responsabilidade |
|---|---|
| `TargetFactory` | Criar `WebTarget` ou `ApiTarget` a partir do tipo informado. |
| `ScanExecutionFactory` | Criar execução inicial com IDs, status e timestamps. |
| `PluginExecutionFactory` | Criar execução individual para cada plugin do plano. |
| `FindingFactory` | Criar finding a partir de resultado normalizado. |
| `EvidenceFactory` | Criar evidência por tipo de artefato. |
| `PolicyFactory` | Criar policy a partir de template corporativo. |
| `ReportFactory` | Criar relatório conforme formato solicitado. |
| `RepositoryFactory` | Compor repositórios concretos na inicialização. |
| `GatewayFactory` | Compor gateways concretos conforme configuração. |
| `UseCaseFactory` | Montar casos de uso com portas e serviços. |
| `PluginRuntimeFactory` | Selecionar runtime nativo, container ou scanner externo. |

## 14. Validators

| Validator | Responsabilidade |
|---|---|
| `CreateScanValidator` | Validar dados mínimos para criação de scan. |
| `TargetScopeValidator` | Garantir alvo dentro de escopo autorizado. |
| `SafeUrlValidator` | Bloquear localhost, metadata endpoints e ranges proibidos. |
| `OpenApiContractValidator` | Validar contrato OpenAPI importado. |
| `PluginManifestValidator` | Validar manifesto, versão, capabilities e permissões. |
| `PluginSignatureValidator` | Validar assinatura e integridade do plugin. |
| `PolicyValidator` | Validar consistência de regras e thresholds. |
| `PolicyExceptionValidator` | Validar justificativa, prazo, aprovador e escopo. |
| `FindingValidator` | Validar finding canônico antes de persistir. |
| `EvidenceValidator` | Validar hash, tipo, tamanho e classificação. |
| `ReportRequestValidator` | Validar formato, filtros e permissões de relatório. |
| `PaginationValidator` | Validar limites de paginação para evitar abuso. |
| `TenantAccessValidator` | Validar relação ator-tenant-projeto. |

## 15. Helpers e utilitários

| Helper/Utilitário | Responsabilidade |
|---|---|
| `SeverityMapper` | Converter severidades de scanners para padrão corporativo. |
| `CvssCalculator` | Calcular ou validar score CVSS quando aplicável. |
| `FindingFingerprintHelper` | Gerar fingerprint estável para deduplicação. |
| `EvidenceHashHelper` | Calcular hash e manifesto de integridade. |
| `SensitiveDataRedactor` | Remover ou mascarar dados sensíveis. |
| `UrlNormalizer` | Normalizar URL, path e query para comparação. |
| `DnsResolutionHelper` | Resolver DNS com proteção contra rebinding. |
| `NetworkRangeHelper` | Classificar IPs públicos, privados e sensíveis. |
| `RetryPolicyHelper` | Calcular backoff exponencial com jitter. |
| `TimeoutHelper` | Calcular deadlines por operação. |
| `JsonSchemaHelper` | Validar e versionar schemas JSON. |
| `SarifMapper` | Converter findings para SARIF. |
| `MarkdownReportFormatter` | Renderizar relatório Markdown. |
| `HtmlReportFormatter` | Renderizar relatório HTML. |
| `ObjectKeyBuilder` | Construir chaves de object storage por tenant/projeto/scan. |
| `LogContextHelper` | Enriquecer logs com tenant, scan, plugin e correlation id. |

## 16. Interfaces por domínio

### 16.1 Repositórios

| Interface | Métodos conceituais | Responsabilidade |
|---|---|---|
| `ScanExecutionRepository` | `save`, `findById`, `updateStatus`, `appendProgress` | Fonte transacional do ciclo de execução. |
| `FindingRepository` | `save`, `findByFingerprint`, `listByScan`, `updateLifecycle` | Fonte transacional de findings. |
| `EvidenceRepository` | `saveMetadata`, `listByFinding`, `listByScan` | Fonte transacional de metadados de evidência. |
| `PolicyRepository` | `saveVersion`, `findActiveByProject`, `findById` | Fonte transacional de policies. |
| `PluginDefinitionRepository` | `save`, `findCompatible`, `findByCapability` | Fonte transacional de catálogo de plugins. |
| `AuditLogRepository` | `append`, `search` | Fonte de trilha auditável. |

### 16.2 Serviços de domínio

| Serviço | Responsabilidade |
|---|---|
| `ScopeAuthorizationDomainService` | Determinar se um target pode ser testado no escopo declarado. |
| `ScanStateDomainService` | Aplicar transições válidas de execução. |
| `PluginCompatibilityDomainService` | Verificar compatibilidade entre plugin, target e policy. |
| `FindingDeduplicationDomainService` | Determinar equivalência entre findings. |
| `SeverityClassificationDomainService` | Classificar severidade com base em regras corporativas. |
| `PolicyDecisionDomainService` | Determinar decisão de gate com base em findings e exceções. |
| `RetentionDomainService` | Determinar retenção correta para evidências e relatórios. |

## 17. Fluxo técnico de criação de scan

```text
CreateScanTool/ScanController
  → mapper externo
  → CreateScanCommand
  → CreateScanValidator
  → TenantAccessValidator
  → TargetScopeValidator
  → QuotaService
  → ScanExecutionFactory
  → ScanExecutionRepository.save
  → EventPublisher.publish(scan.requested.v1)
  → AuditService.record
  → ScanExecutionDto
  → presenter externo
```

## 18. Fluxo técnico de execução de plugin

```text
PluginExecutionConsumer
  → PluginJobHandler
  → ScanExecutionRepository.findById
  → PluginDefinitionRepository.findById
  → SecretProviderGateway.resolveEphemeralSecrets
  → PluginRuntimeFactory.create
  → PluginExecutorGateway.execute
  → EvidenceRedactionService
  → ObjectStorageGateway.put
  → FindingNormalizationService
  → FindingRepository.save
  → EventPublisher.publish(finding.discovered.v1)
  → PluginExecutionRepository.updateStatus
  → TelemetryGateway.recordMetrics
```

## 19. Fluxo técnico de quality gate

```text
CompleteScanUseCase
  → FindingRepository.listByScan
  → PolicyRepository.findActiveByProject
  → PolicyExceptionRepository.findValidForContext
  → PolicyEvaluationService.evaluate
  → QualityGateDecisionBuilder
  → EventPublisher.publish(quality_gate.evaluated.v1)
  → ReportGeneration job
  → ScanExecutionRepository.updateStatus
```

## 20. Convenções de nomenclatura

| Tipo | Convenção | Exemplo |
|---|---|---|
| Entidade | Substantivo de domínio | `ScanExecution` |
| Value object | Substantivo específico | `CvssVector` |
| Caso de uso | Verbo + objeto + `UseCase` | `CreateScanUseCase` |
| Command | Verbo + objeto + `Command` | `CreateScanCommand` |
| Query | Verbo de leitura + objeto + `Query` | `GetScanStatusQuery` |
| DTO | Objeto + `Dto` | `FindingDto` |
| Porta | Capacidade + tipo | `ObjectStorageGateway` |
| Repositório | Agregado + `Repository` | `FindingRepository` |
| Adaptador | Tecnologia + porta | `S3ObjectStorageGateway` |
| Evento domínio | Fato no passado | `ScanCompleted` |
| Evento integração | Recurso.ação.versão | `scan.completed.v1` |
| Exception | Problema + `Exception` | `TargetOutOfScopeException` |

## 21. Estratégia de implementação futura

A implementação deve começar pelos contratos e domínio, evoluindo para aplicação e só depois para adaptadores concretos:

1. Definir schemas em `packages/contracts`.
2. Definir value objects, entidades e eventos em `packages/domain`.
3. Definir portas e casos de uso em `packages/application`.
4. Criar adaptadores in-memory para testes.
5. Implementar apps MCP/API/worker usando os casos de uso.
6. Implementar adaptadores PostgreSQL, NATS, S3/MinIO, Redis e OpenTelemetry.
7. Implementar SDK e primeiros plugins oficiais.
8. Adicionar testes de contrato, integração e e2e.

