# Security QA MCP — Design do Scanner Engine

## 1. Objetivo

Este documento projeta o **Scanner Engine** do Security QA MCP sem implementar código. O módulo centraliza a seleção, preparação, execução, observabilidade, normalização e atualização de scanners externos por meio de plugins padronizados.

O Scanner Engine deve suportar plugins para:

- OWASP ZAP
- Nuclei
- Nikto
- Trivy
- OWASP Dependency Check
- Semgrep
- CodeQL
- Grype
- Snyk
- Gitleaks
- TruffleHog
- Nmap

## 2. Escopo e responsabilidades

O Scanner Engine pertence ao plano de execução e deve ser acionado por casos de uso de scan, workers ou pipelines. Ele não decide regras de negócio de aceitação de risco; essa decisão permanece no domínio de findings e policies.

### Responsabilidades incluídas

- Resolver scanners elegíveis para um alvo e um perfil de teste.
- Validar capabilities, permissões, versão e saúde de cada scanner.
- Preparar ambientes de execução isolados.
- Executar scanners com retry, timeout, cache e logs padronizados.
- Capturar resultados brutos e evidências.
- Acionar parsers e normalizers específicos.
- Entregar findings canônicos para o pipeline de correlação.
- Expor health checks e estratégia de atualização por scanner.

### Responsabilidades excluídas

- Persistência transacional direta de findings finais.
- Aprovação de escopo e autorização de tenant.
- Decisão de quality gate.
- Geração final de relatórios executivos.
- Implementação concreta de CLI, containers ou SDKs de fornecedores.

## 3. Posicionamento arquitetural

```text
Scan Orchestrator
  → ScannerPlan
  → Scanner Engine
      ├─ Plugin Registry Client
      ├─ Scanner Selector
      ├─ Execution Coordinator
      ├─ Runtime Sandbox
      ├─ Adapter Layer
      ├─ Parser Layer
      ├─ Normalization Pipeline
      ├─ Error/Retry/Timeout Policies
      ├─ Cache Layer
      ├─ Health Check Manager
      └─ Update Strategy Manager
  → Finding Normalizer / Correlator
  → Policy Engine
  → Report Service
```

O módulo deve seguir Clean Architecture e Hexagonal Architecture:

- O core do Scanner Engine depende de interfaces.
- Plugins concretos ficam em `adapters/scanner-*` ou `plugins/scanner-*`.
- Contratos públicos de entrada e saída ficam em `packages/contracts/src/plugins`.
- Helpers reutilizáveis de criação de plugins ficam em `packages/plugin-sdk`.

## 4. Estrutura conceitual de pastas

```text
packages/
├─ application/
│  └─ src/
│     ├─ services/scanner-engine/
│     ├─ ports/outbound/scanner-engine/
│     └─ dto/scanner-engine/
├─ contracts/
│  └─ src/
│     ├─ plugins/scanner/
│     └─ schemas/scanner-results/
├─ plugin-sdk/
│  └─ src/
│     ├─ scanner-interface/
│     ├─ parser-interface/
│     ├─ normalizer-interface/
│     └─ testing/scanner-fixtures/
└─ shared-kernel/
   └─ src/
      ├─ errors/scanner-errors/
      ├─ logging/scanner-log-context/
      └─ result/scanner-result/

adapters/
├─ scanner-zap/
├─ scanner-nuclei/
├─ scanner-nikto/
├─ scanner-trivy/
├─ scanner-dependency-check/
├─ scanner-semgrep/
├─ scanner-codeql/
├─ scanner-grype/
├─ scanner-snyk/
├─ scanner-gitleaks/
├─ scanner-trufflehog/
└─ scanner-nmap/
```

Esta estrutura é apenas uma diretriz de design. A implementação pode consolidar adaptadores quando houver ganho operacional, desde que os contratos permaneçam independentes por scanner.

## 5. Componentes obrigatórios por scanner

Cada scanner deve possuir os seguintes componentes conceituais.

| Componente | Responsabilidade | Entrada principal | Saída principal |
|---|---|---|---|
| Interface | Contrato estável exposto pelo plugin. | `ScannerExecutionRequest` | `ScannerExecutionResult` |
| Adapter | Traduz contrato interno para comando, API, container ou SDK externo. | Configuração canônica | Invocação concreta |
| Executor | Controla ciclo de execução, processo, container, streaming e cancelamento. | Plano de execução | Resultado bruto e metadados |
| Parser | Converte saída nativa para objetos intermediários tipados. | JSON, XML, SARIF, logs ou stdout | `ParsedFinding[]` |
| Normalizer | Mapeia achados para schema canônico da plataforma. | `ParsedFinding[]` | `CanonicalFinding[]` |
| Error Handler | Classifica falhas recuperáveis, não recuperáveis e de configuração. | Erro técnico ou funcional | `ScannerError` padronizado |
| Retry | Define retentativas por falha transitória. | Política por scanner | Nova tentativa ou falha final |
| Timeout | Impõe limites de duração e cancelamento cooperativo/forçado. | SLA e perfil | Execução finalizada ou abortada |
| Logs | Produz logs estruturados, redigidos e correlacionados. | Eventos de execução | Eventos observáveis |
| Cache | Reusa downloads, bases de dados, templates e resultados elegíveis. | Chaves determinísticas | Cache hit/miss e artefatos |
| Health Check | Verifica disponibilidade, versão e dependências. | Ambiente de runtime | Estado de saúde |
| Estratégia de atualização | Atualiza imagem, binário, ruleset, DB ou templates. | Fonte confiável | Versão validada |

## 6. Contratos conceituais

### 6.1 Interface do scanner

A interface de scanner deve declarar:

- Identidade do scanner: nome, vendor, versão do adapter e versão da ferramenta.
- Capabilities suportadas.
- Tipos de alvo aceitos.
- Requisitos de runtime: CPU, memória, disco, rede, permissões e secrets.
- Formatos de saída suportados.
- Estratégia de parser e normalizer.
- Políticas padrão de retry, timeout, cache e update.
- Sinais de cancelamento e progresso.

### 6.2 Requisição de execução

A requisição canônica deve conter:

- `tenant_id`, `project_id`, `scan_id`, `plugin_execution_id` e `correlation_id`.
- Target normalizado: URL, host, CIDR, repositório, imagem, filesystem, SBOM ou package manifest.
- Escopo permitido e restrições de rede.
- Perfil de intensidade: `safe`, `standard`, `deep` ou `ci-fast`.
- Configuração específica do scanner validada por schema.
- Secrets referenciados por handle, nunca materializados em logs.
- Políticas de timeout, retry, cache e retenção.

### 6.3 Resultado de execução

O resultado canônico deve conter:

- Status: `success`, `partial_success`, `failed`, `timeout`, `cancelled` ou `skipped`.
- Metadados: versão da ferramenta, versão das regras, duração e recursos consumidos.
- Artefatos brutos: caminhos ou URIs para stdout, stderr, JSON, XML, SARIF, logs, bancos e evidências.
- Findings normalizados.
- Warnings de parsing, limitações e achados descartados.
- Erros padronizados, quando aplicável.

## 7. Capabilities e seleção de scanners

| Scanner | Tipo principal | Targets | Capabilities sugeridas |
|---|---|---|---|
| OWASP ZAP | DAST Web/API | URL, OpenAPI, GraphQL | `dast.web`, `dast.api`, `active_scan`, `passive_scan` |
| Nuclei | Template-based scanning | URL, host, API | `template_scan`, `cve_check`, `misconfiguration` |
| Nikto | Web server scanning | URL, host | `web_server_audit`, `legacy_checks` |
| Trivy | Container/SBOM/IaC/dependency | imagem, filesystem, repo, SBOM | `container_vuln`, `iac_scan`, `sbom_scan`, `secret_scan` |
| OWASP Dependency Check | SCA | manifests, filesystem | `dependency_vuln`, `cve_mapping` |
| Semgrep | SAST | repositório, filesystem | `sast`, `custom_rules`, `secrets_light` |
| CodeQL | SAST semântico | repositório | `semantic_sast`, `code_database` |
| Grype | SCA/SBOM/Image | imagem, filesystem, SBOM | `container_vuln`, `sbom_scan` |
| Snyk | SCA/SAST/Container/IaC | repo, imagem, manifests | `commercial_sca`, `sast`, `container_vuln`, `iac_scan` |
| Gitleaks | Secrets | repo, filesystem | `secret_scan`, `git_history_scan` |
| TruffleHog | Secrets | repo, filesystem, SaaS connectors | `verified_secret_scan`, `git_history_scan` |
| Nmap | Network discovery | host, CIDR | `port_scan`, `service_detection`, `script_scan` |

A seleção deve considerar target, policy, tenant, licença, intensidade permitida, tempo disponível, histórico de falhas e custo estimado.

## 8. Fluxo de execução

```text
1. ScannerPlan recebido pelo worker
2. Scanner Engine carrega metadata do plugin
3. Health check rápido valida pré-condições
4. Cache é consultado para bases, templates e resultados elegíveis
5. Adapter monta comando/API/container request
6. Executor inicia sandbox com limites de CPU, memória, rede e tempo
7. Logs e métricas são emitidos em tempo real
8. Timeout e cancelamento são monitorados
9. Retry é aplicado somente para falhas transitórias seguras
10. Artefatos brutos são enviados para object storage
11. Parser converte saída nativa em modelo intermediário
12. Normalizer produz findings canônicos
13. Error Handler classifica falhas e warnings
14. Resultado retorna ao pipeline de findings
```

## 9. Parser e normalização

### 9.1 Parser

Cada parser deve ser tolerante a variações de versão e registrar perdas de informação. Ele deve preservar referências ao artefato bruto para auditoria.

Formatos esperados:

- ZAP: JSON e XML.
- Nuclei: JSONL.
- Nikto: XML, JSON ou CSV quando disponível.
- Trivy: JSON, CycloneDX ou SARIF.
- Dependency Check: JSON, XML, HTML apenas como artefato.
- Semgrep: JSON ou SARIF.
- CodeQL: SARIF.
- Grype: JSON, CycloneDX ou SARIF.
- Snyk: JSON ou SARIF conforme produto.
- Gitleaks: JSON ou SARIF.
- TruffleHog: JSON.
- Nmap: XML preferencialmente.

### 9.2 Normalizer

O normalizer deve mapear cada achado para um schema canônico com:

- Título, descrição e recomendação.
- Severidade normalizada e severidade original.
- Confiança.
- CWE, CVE, CVSS, OWASP, CAPEC e referências quando existirem.
- Localização: URL, host, porta, path, arquivo, linha, pacote, imagem ou commit.
- Evidência redigida.
- Fingerprint estável para deduplicação.
- Origem: scanner, regra, versão da regra e versão da ferramenta.

## 10. Error Handler

Erros devem ser classificados em categorias padronizadas:

| Categoria | Exemplos | Retry? | Ação |
|---|---|---|---|
| Configuração inválida | Flag incompatível, target não suportado | Não | Marcar como `failed_config` |
| Falha transitória | Pull de imagem falhou, rate limit temporário | Sim | Backoff com jitter |
| Timeout | Execução excedeu SLA | Condicional | Encerrar sandbox e marcar parcial se houver resultados |
| Falha de parser | Saída inválida ou versão desconhecida | Não | Preservar artefato bruto e emitir warning/falha |
| Falha de licença | Token Snyk ausente, licença expirada | Não | Marcar como `failed_license` |
| Falha de saúde | DB de scanner indisponível | Sim, se transitória | Reagendar ou degradar |
| Violação de escopo | Scanner tentou acessar alvo não permitido | Não | Cancelar e auditar como evento de segurança |

## 11. Retry

A política de retry deve ser declarativa por scanner:

- Tentativas padrão: 0 a 3.
- Backoff exponencial com jitter.
- Orçamento máximo de tempo por plugin.
- Retry apenas para erros idempotentes e transitórios.
- Nunca repetir varreduras ativas agressivas se houver risco de duplicar impacto no alvo.
- Registrar cada tentativa com o mesmo `correlation_id` e número de tentativa.

## 12. Timeout e cancelamento

Timeouts devem existir em três níveis:

- **Startup timeout**: tempo máximo para preparar imagem, base, ruleset ou banco.
- **Execution timeout**: duração máxima da varredura.
- **Graceful shutdown timeout**: tempo para encerramento cooperativo antes de kill forçado.

Scanners longos devem emitir heartbeats. Ausência de heartbeat deve abrir caminho para cancelamento defensivo.

## 13. Logs e observabilidade

Todos os scanners devem emitir logs estruturados com:

- `timestamp`, `level`, `tenant_id`, `project_id`, `scan_id`, `plugin_execution_id`, `scanner_id`, `correlation_id`.
- Fase: `prepare`, `execute`, `parse`, `normalize`, `cache`, `health_check`, `update`.
- Versão da ferramenta e versão de ruleset/template/database.
- Redaction obrigatória de secrets, tokens, cookies, Authorization headers, URLs assinadas e evidências sensíveis.

Métricas mínimas:

- Duração por fase.
- Taxa de sucesso/falha por scanner.
- Timeouts por scanner.
- Cache hit ratio.
- Quantidade de findings por severidade.
- Falhas de parser por versão.
- Idade de bases/templates.

## 14. Cache

O cache deve reduzir custo sem comprometer frescor e rastreabilidade.

| Item | Estratégia | Invalidação |
|---|---|---|
| Imagens de scanner | Cache de registry local ou node cache | Digest mudou ou política de atualização |
| Templates Nuclei | Cache versionado por commit/tag | TTL, assinatura ou nova release |
| DB Trivy/Grype | Cache por timestamp e checksum | TTL curto e checksum divergente |
| DB Dependency Check | Cache persistente controlado | TTL e versão NVD |
| Rules Semgrep/CodeQL | Cache por pacote/commit | Versão da regra mudou |
| Resultados SCA | Cache por lockfile/SBOM hash | Manifest, lockfile ou DB mudou |
| Secret scanning | Cache por commit range | Novo commit ou regra mudou |
| Nmap service probes | Cache de assets internos | Mudança de target ou TTL curto |

Resultados cacheados devem ser marcados com `cache_hit=true`, chave de cache e idade do dado.

## 15. Health Check

Cada plugin deve fornecer:

- **Liveness**: o adapter responde e consegue iniciar.
- **Readiness**: ferramenta, imagem, licença, banco, ruleset e permissões estão prontos.
- **Version check**: versão instalada e versão esperada.
- **Capability check**: capabilities declaradas estão realmente disponíveis.
- **Dependency check**: templates, DBs, runtimes, network e secrets necessários.

Health checks devem ser leves por padrão e profundos sob demanda.

## 16. Estratégia de atualização

Atualizações devem ser seguras, auditáveis e reversíveis.

| Scanner | O que atualizar | Estratégia recomendada |
|---|---|---|
| OWASP ZAP | Imagem, add-ons, rules | Imagem pinada por digest; canal estável; smoke test antes de promover |
| Nuclei | Binário e templates | Templates assinados/pinados por commit; atualização frequente com validação |
| Nikto | Binário e database | Janela controlada; validação de checksums |
| Trivy | Binário/imagem e vulnerability DB | DB com TTL curto; imagem pinada; fallback para DB anterior |
| Dependency Check | Binário e NVD data | Mirror/cache interno; atualização agendada; proteção contra rate limit |
| Semgrep | Binário/imagem e rules | Rulesets versionados; canary em projetos sintéticos |
| CodeQL | CLI, packs e query suites | Packs versionados; database compatibility check |
| Grype | Binário/imagem e vulnerability DB | DB cache versionado; fallback automático |
| Snyk | CLI e policy/org config | Versão aprovada; validação de token/licença; monitorar breaking changes |
| Gitleaks | Binário e regras | Rulesets internos assinados; baseline versionado |
| TruffleHog | Binário e detectors | Versão pinada; teste de detectores com fixtures |
| Nmap | Binário, scripts NSE e service DB | Atualização controlada; bloquear scripts perigosos por padrão |

O Update Strategy Manager deve suportar:

- Canais `stable`, `candidate` e `pinned`.
- Rollback por versão anterior conhecida.
- Assinatura, checksum ou digest obrigatório.
- Smoke tests com fixtures por scanner.
- Auditoria de quem aprovou, quando e por quê.

## 17. Requisitos específicos por scanner

### 17.1 OWASP ZAP

- Deve executar preferencialmente em container isolado.
- Suportar baseline/passive scan e active scan mediante policy explícita.
- Parser deve mapear alertas para CWE, WASC, confidence e risk.
- Timeout deve diferenciar spider, ajax spider e active scan.
- Cache pode incluir add-ons e imagem, mas não resultados de DAST dinâmico salvo política específica.

### 17.2 Nuclei

- Deve pinçar templates por versão/commit para reprodutibilidade.
- Deve limitar severidades, tags e templates perigosos por policy.
- Parser JSONL deve tolerar linhas inválidas sem perder o arquivo bruto.
- Retry deve evitar duplicar templates com efeitos colaterais.

### 17.3 Nikto

- Deve ser tratado como scanner legado útil para web server audit.
- Parser deve preservar IDs OSVDB/legacy quando existirem, mas normalizar para referências modernas quando possível.
- Timeout deve ser conservador para evitar scans longos não produtivos.

### 17.4 Trivy

- Deve suportar imagem, filesystem, repo, SBOM e IaC conforme configuração.
- Normalizer deve mapear CVE, package, installed version, fixed version, layer e target.
- Cache de vulnerability DB é obrigatório em ambientes CI/CD.

### 17.5 OWASP Dependency Check

- Deve usar cache/mirror do NVD para reduzir rate limits.
- Parser JSON é preferencial.
- Normalizer deve deduplicar por package URL, CPE, CVE e lockfile.

### 17.6 Semgrep

- Deve suportar rulesets internos e externos aprovados.
- Parser deve mapear arquivo, linha, coluna, rule id, message, severity e metadata CWE/OWASP.
- Cache de dependências/rulesets deve ser separado de resultados.

### 17.7 CodeQL

- Deve tratar criação de database como fase própria com timeout específico.
- Parser SARIF é obrigatório.
- Normalizer deve preservar rule id, query id, locations, dataflow trace e precision.

### 17.8 Grype

- Deve complementar ou substituir Trivy conforme policy.
- Normalizer deve preservar matcher, package type, CVE, fixed versions e SBOM source.
- Cache de DB deve ser versionado por checksum.

### 17.9 Snyk

- Deve isolar credenciais por tenant/projeto.
- Health check deve validar token, org e features licenciadas.
- Error Handler deve diferenciar falha de licença, rate limit e vulnerabilidade encontrada.

### 17.10 Gitleaks

- Deve suportar baseline e commit range.
- Normalizer deve redigir secrets e preservar apenas fingerprint/prova mínima.
- Retry raramente é necessário; falhas geralmente são configuração ou I/O.

### 17.11 TruffleHog

- Deve preferir modo de verificação de secrets quando permitido e seguro.
- Logs devem ocultar completamente valores detectados.
- Health check deve validar conectores externos somente quando configurados.

### 17.12 Nmap

- Deve exigir autorização explícita de escopo, principalmente para CIDR.
- Scripts NSE intrusivos devem ficar bloqueados por padrão.
- Parser XML deve mapear host, porta, protocolo, serviço, versão, script output e confidence.
- Retry deve ser limitado para não amplificar tráfego de rede.

## 18. Segurança operacional

- Todos os scanners executam com menor privilégio.
- Filesystem read-only sempre que possível.
- Diretório temporário efêmero e limpo ao final.
- Network egress restrito ao alvo autorizado e fontes de update aprovadas.
- Secrets entregues por handle temporário e redigidos em todas as saídas.
- Artefatos brutos devem ter classificação, retenção e criptografia.
- Execuções ativas perigosas exigem policy explícita e auditoria.

## 19. Critérios de aceite de design

- Cada scanner possui interface, adapter, executor, parser, normalizer, error handler, retry, timeout, logs, cache, health check e estratégia de atualização definidos.
- O core do Scanner Engine não depende de ferramentas externas concretas.
- Resultados brutos são preservados para auditoria.
- Findings são normalizados para um schema único.
- Falhas são classificadas de forma consistente.
- Atualizações são pinadas, verificadas e reversíveis.
- Execuções respeitam escopo, isolamento e observabilidade enterprise.
