# Security QA MCP — Documentação Funcional Corporativa

## 1. Controle do documento

| Campo | Informação |
|---|---|
| Produto | Security QA MCP |
| Tipo | Documentação funcional corporativa |
| Versão | 1.0 |
| Status | Proposto |
| Público-alvo | Produto, Engenharia, Segurança, QA, Operações, Compliance e lideranças executivas |
| Idioma | Português do Brasil |

## 2. Sumário executivo

O Security QA MCP é uma plataforma corporativa para orquestrar, executar, governar e reportar testes automatizados de segurança em aplicações Web e APIs. O produto utiliza o Model Context Protocol (MCP) como camada de integração para agentes de IA, clientes MCP, pipelines de CI/CD, interfaces operacionais e automações corporativas.

A solução centraliza a execução de scanners, plugins e validadores, normaliza achados de segurança, aplica políticas de quality gate, gera evidências auditáveis e permite rastreabilidade ponta a ponta desde a solicitação da varredura até a remediação dos achados.

## 3. Objetivos

### 3.1 Objetivo geral

Fornecer uma plataforma padronizada, escalável e governável para automação de testes de segurança contínuos, reduzindo risco operacional, aumentando velocidade de validação e melhorando a visibilidade executiva sobre a postura de segurança de aplicações e APIs.

### 3.2 Objetivos específicos

- Automatizar testes DAST, testes de APIs, validações de TLS, headers, autenticação, autorização e exposição de dados.
- Expor funcionalidades por MCP, API HTTP, CLI e, quando aplicável, console Web.
- Padronizar achados, severidade, evidências, recomendações e status de tratamento.
- Integrar o ciclo de segurança aos pipelines de CI/CD e processos de desenvolvimento.
- Permitir execução assíncrona, distribuída, isolada e rastreável de varreduras.
- Habilitar extensibilidade por plugins, preservando governança e segurança operacional.
- Apoiar decisões de go/no-go por políticas de quality gate.
- Disponibilizar relatórios técnicos, executivos e exportações para ferramentas corporativas.

## 4. Problemas resolvidos

| Problema | Impacto atual | Como o Security QA MCP resolve |
|---|---|---|
| Testes de segurança manuais e inconsistentes | Baixa cobertura, atrasos e risco de erro humano | Automatiza execuções com escopos, políticas e evidências padronizadas |
| Ferramentas de scanner fragmentadas | Resultados duplicados, formatos distintos e pouca rastreabilidade | Normaliza, deduplica e correlaciona achados em modelo único |
| Falta de integração com CI/CD | Vulnerabilidades detectadas tarde no ciclo | Executa gates automatizados por severidade, risco e contexto |
| Ausência de evidências auditáveis | Dificuldade em comprovar conformidade | Armazena logs, evidências, relatórios e trilhas de auditoria |
| Baixa governança de plugins | Risco de execução insegura e resultados não confiáveis | Exige registro, versão, permissões e isolamento de runtime |
| Escala limitada de varreduras | Gargalos em equipes de AppSec e QA | Usa filas, workers distribuídos, retries e execução assíncrona |
| Visibilidade executiva insuficiente | Decisões sem métricas confiáveis | Fornece KPIs, dashboards e relatórios por projeto, tenant e período |

## 5. Personas

| Persona | Perfil | Necessidades | Indicadores de sucesso |
|---|---|---|---|
| Engenheiro de AppSec | Especialista em segurança de aplicações | Definir políticas, analisar achados e aprovar exceções | Redução de falsos positivos, cobertura de testes e tempo de triagem |
| QA Engineer | Responsável por qualidade funcional e não funcional | Executar validações de segurança em ambientes de teste | Feedback rápido e relatórios objetivos |
| Desenvolvedor | Responsável pela correção de vulnerabilidades | Entender falhas, reproduzir evidências e corrigir rapidamente | Tempo médio de remediação e baixa reincidência |
| Tech Lead | Responsável técnico por produto/squad | Acompanhar riscos e decisões de release | Gates previsíveis e backlog priorizado |
| DevOps/SRE | Responsável por pipelines e operação | Integrar scans, monitorar execução e garantir disponibilidade | Baixa taxa de falhas operacionais e execução escalável |
| Gestor de Segurança | Liderança de segurança | Visibilidade agregada de risco e conformidade | Tendência de risco, SLA de remediação e cobertura corporativa |
| Auditor/Compliance | Responsável por evidências e controles | Verificar trilhas, relatórios e retenção | Evidências completas, imutáveis e exportáveis |
| Product Owner | Responsável por valor de negócio | Priorizar funcionalidades e maximizar adoção | Adoção por squads, redução de risco e previsibilidade do roadmap |

## 6. Stakeholders

| Stakeholder | Papel | Interesse principal |
|---|---|---|
| CISO / Segurança Corporativa | Patrocinador estratégico | Redução de risco e governança de segurança |
| AppSec | Dono funcional especializado | Cobertura, precisão e políticas de segurança |
| Engenharia de Plataforma | Dono técnico da infraestrutura | Escalabilidade, confiabilidade e integrações |
| Squads de Produto | Usuários consumidores | Feedback rápido e acionável |
| QA / Qualidade | Usuários operacionais | Validação contínua e rastreável |
| DevOps/SRE | Operação | Observabilidade, automação e resiliência |
| Compliance / Auditoria | Governança | Evidências, retenção e segregação de funções |
| Jurídico / Privacidade | Consultivo | Proteção de dados e aderência regulatória |
| Gestão Executiva | Decisão | KPIs, risco agregado e retorno do investimento |

## 7. Escopo funcional

### 7.1 Dentro do escopo

- Cadastro e gestão de tenants, projetos, alvos e escopos de varredura.
- Criação, agendamento, execução, cancelamento e reprocessamento de scans.
- Execução de plugins de segurança com controle de versão e permissões.
- Normalização, deduplicação, correlação e classificação de findings.
- Gestão do ciclo de vida dos achados.
- Políticas de quality gate por severidade, tipo de alvo, ambiente e criticidade.
- Relatórios técnicos, executivos e exportações estruturadas.
- Integrações com CI/CD, issue trackers, SIEM, observabilidade e clientes MCP.
- Auditoria de ações e retenção de evidências.

### 7.2 Fora do escopo inicial

- Pentest manual substitutivo de avaliação humana especializada.
- Exploração destrutiva sem autorização explícita.
- Correção automática de código em repositórios produtivos sem aprovação humana.
- Gestão completa de ativos corporativos fora do contexto de aplicações e APIs testadas.

## 8. Casos de uso

| ID | Caso de uso | Ator principal | Resultado esperado |
|---|---|---|---|
| UC-001 | Cadastrar projeto | Admin de tenant | Projeto disponível para configuração de alvos e políticas |
| UC-002 | Cadastrar alvo Web | AppSec / QA | URL validada e pronta para varreduras autorizadas |
| UC-003 | Cadastrar API por OpenAPI | Desenvolvedor / QA | Contrato importado para testes de API e fuzzing |
| UC-004 | Criar scan sob demanda | AppSec / QA / Pipeline | Job criado, validado e enfileirado |
| UC-005 | Executar scan em CI/CD | Pipeline | Resultado usado para aprovar ou bloquear build/release |
| UC-006 | Consultar status de scan | Usuário autorizado | Status, progresso e eventos exibidos em tempo quase real |
| UC-007 | Analisar findings | AppSec / Desenvolvedor | Achados priorizados com evidências e recomendações |
| UC-008 | Solicitar exceção de policy | Tech Lead | Exceção registrada para avaliação e aprovação |
| UC-009 | Gerar relatório executivo | Gestor de Segurança | Relatório consolidado por período, projeto e severidade |
| UC-010 | Registrar plugin | Admin de plataforma | Plugin versionado, habilitado e governado |
| UC-011 | Exportar evidências para auditoria | Auditor | Pacote com trilha, achados, logs e relatórios |
| UC-012 | Cancelar execução | Operador / AppSec | Execução interrompida com estado consistente |

## 9. User stories

| ID | História | Prioridade | Critérios de aceite resumidos |
|---|---|---|---|
| US-001 | Como Admin, quero criar tenants e projetos para organizar o uso da plataforma. | Alta | Tenant e projeto criados com auditoria e RBAC aplicado |
| US-002 | Como AppSec, quero cadastrar alvos autorizados para evitar scans fora de escopo. | Alta | Alvo validado, com proprietário, ambiente e escopo explícito |
| US-003 | Como QA, quero iniciar scans sob demanda para validar releases. | Alta | Scan criado, executado e consultável |
| US-004 | Como DevOps, quero executar scans no pipeline para bloquear releases inseguros. | Alta | Gate retorna aprovado, reprovado ou inconclusivo com motivo |
| US-005 | Como Desenvolvedor, quero visualizar evidências reproduzíveis para corrigir vulnerabilidades. | Alta | Finding apresenta evidência, impacto, recomendação e referência |
| US-006 | Como AppSec, quero deduplicar achados para reduzir ruído operacional. | Média | Achados equivalentes vinculados a uma ocorrência canônica |
| US-007 | Como Gestor, quero dashboards de risco para acompanhar evolução da postura de segurança. | Média | KPIs exibidos por projeto, severidade, SLA e tendência |
| US-008 | Como Auditor, quero exportar evidências para comprovar controles. | Média | Exportação contém logs, trilha de auditoria e integridade verificável |
| US-009 | Como Admin, quero gerenciar plugins para expandir capacidades com segurança. | Média | Plugin registrado, versionado, assinado e limitado por permissões |
| US-010 | Como Tech Lead, quero solicitar exceções de findings para tratar riscos aceitos. | Média | Exceção tem justificativa, prazo, aprovador e auditoria |

## 10. Épicos e features

| Épico | Objetivo | Features |
|---|---|---|
| EP-001 Gestão de Identidade e Tenancy | Controlar acesso, segregação e governança | RBAC, tenants, projetos, usuários, grupos, tokens de serviço |
| EP-002 Gestão de Alvos e Escopos | Garantir autorização e contexto | Cadastro de URLs, APIs, ambientes, tags, criticidade, allowlist |
| EP-003 Orquestração de Scans | Executar testes de forma escalável | Criação de jobs, filas, agendamento, retries, cancelamento, reprocessamento |
| EP-004 Runtime de Plugins | Expandir capacidades de teste | Registro, versionamento, assinatura, permissões, sandbox e catálogo |
| EP-005 Findings e Evidências | Gerir vulnerabilidades detectadas | Normalização, deduplicação, severidade, evidências, status e comentários |
| EP-006 Policy & Quality Gates | Automatizar decisões de risco | Políticas, thresholds, exceções, gates de CI/CD e aprovação |
| EP-007 Reporting e Integrações | Distribuir informação acionável | Relatórios, SARIF/JSON/HTML, issue tracker, SIEM, webhooks |
| EP-008 Observabilidade e Auditoria | Operar com confiabilidade e conformidade | Logs, métricas, traces, trilhas de auditoria, retenção e alertas |

## 11. Critérios de aceite corporativos

### 11.1 Critérios gerais

- Toda funcionalidade deve respeitar autenticação, autorização e isolamento por tenant.
- Toda ação relevante deve gerar trilha de auditoria com ator, data/hora, origem e resultado.
- Toda execução deve possuir identificador único, status e correlação com logs e evidências.
- Toda falha deve ser tratada com mensagem clara, código de erro e orientação operacional.
- Toda integração deve possuir contrato versionado e documentação mínima.
- Toda exportação deve preservar integridade, rastreabilidade e classificação da informação.

### 11.2 Critérios por capacidade

| Capacidade | Critérios de aceite |
|---|---|
| Criação de scan | Valida alvo, escopo, permissões, política aplicável e disponibilidade de plugins antes de enfileirar |
| Execução de scan | Registra início, progresso, eventos, fim, duração, erros e artefatos gerados |
| Findings | Apresenta severidade, descrição, evidência, impacto, recomendação, origem e status |
| Quality gate | Retorna decisão determinística, justificativa e lista de findings impactantes |
| Plugin | Não executa sem registro, versão aprovada e permissões compatíveis |
| Relatórios | Permite filtros por tenant, projeto, alvo, período, severidade, status e ambiente |
| Auditoria | Permite consulta por ator, ação, recurso, período e resultado |

## 12. Regras de negócio

| ID | Regra |
|---|---|
| RN-001 | Nenhum scan pode ser executado sem alvo previamente autorizado. |
| RN-002 | Um alvo deve pertencer a exatamente um tenant e a pelo menos um projeto. |
| RN-003 | Scans produtivos exigem política explícita de janela, intensidade e permissões. |
| RN-004 | Plugins classificados como ativos ou intrusivos exigem aprovação administrativa. |
| RN-005 | Findings críticos devem violar quality gate, salvo exceção válida e vigente. |
| RN-006 | Exceções devem possuir justificativa, aprovador, prazo de expiração e escopo delimitado. |
| RN-007 | Findings expirados ou reabertos devem retornar ao fluxo de triagem. |
| RN-008 | Evidências não podem ser alteradas após persistência; novas versões devem ser anexadas. |
| RN-009 | Dados sensíveis em evidências devem ser mascarados sempre que possível. |
| RN-010 | Cancelamento de scan deve preservar logs, estado final e motivo. |
| RN-011 | Retentativas automáticas devem respeitar limite configurado por política. |
| RN-012 | Relatórios executivos não devem expor segredos, tokens ou payloads sensíveis. |
| RN-013 | Usuários só podem visualizar recursos de tenants e projetos aos quais possuem acesso. |
| RN-014 | Tokens de serviço devem possuir escopo mínimo e data de expiração recomendada. |
| RN-015 | Alterações em políticas devem manter histórico versionado. |

## 13. Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-001 | Permitir autenticação de usuários e serviços. | Alta |
| RF-002 | Permitir autorização por RBAC e escopos de projeto. | Alta |
| RF-003 | Permitir cadastro, edição, consulta e desativação de tenants. | Alta |
| RF-004 | Permitir cadastro, edição, consulta e arquivamento de projetos. | Alta |
| RF-005 | Permitir cadastro de alvos Web com URL, ambiente, criticidade e proprietário. | Alta |
| RF-006 | Permitir importação de contratos OpenAPI para alvos de API. | Alta |
| RF-007 | Validar se o alvo está dentro do escopo permitido antes do scan. | Alta |
| RF-008 | Criar scans sob demanda via MCP, API e CLI. | Alta |
| RF-009 | Criar scans por eventos de pipeline CI/CD. | Alta |
| RF-010 | Consultar status, progresso e resultado de scans. | Alta |
| RF-011 | Cancelar scans em execução, respeitando consistência de estado. | Média |
| RF-012 | Executar plugins conforme tipo de alvo, política e permissões. | Alta |
| RF-013 | Normalizar resultados de plugins em modelo único de findings. | Alta |
| RF-014 | Deduplicar findings por assinatura técnica e contexto. | Média |
| RF-015 | Classificar severidade por regra configurável e padrão corporativo. | Alta |
| RF-016 | Gerenciar ciclo de vida de findings: novo, em triagem, aceito, em correção, corrigido, falso positivo e reaberto. | Alta |
| RF-017 | Anexar evidências, logs, screenshots, HARs e artefatos aos resultados. | Alta |
| RF-018 | Definir e aplicar policies de quality gate. | Alta |
| RF-019 | Permitir solicitação, aprovação, rejeição e expiração de exceções. | Média |
| RF-020 | Gerar relatórios técnicos e executivos. | Média |
| RF-021 | Exportar resultados em JSON, SARIF e HTML. | Média |
| RF-022 | Integrar com issue trackers para abertura e atualização de tickets. | Média |
| RF-023 | Integrar com SIEM e observabilidade por eventos e webhooks. | Média |
| RF-024 | Registrar plugins com metadados, versão, capabilities e permissões. | Média |
| RF-025 | Auditar ações administrativas, operacionais e de segurança. | Alta |

## 14. Requisitos não funcionais

| Categoria | Requisito |
|---|---|
| Segurança | Criptografar dados em trânsito e em repouso conforme padrão corporativo. |
| Segurança | Isolar execuções de plugins em sandbox com menor privilégio. |
| Segurança | Proteger segredos por cofre corporativo ou mecanismo equivalente. |
| Privacidade | Mascarar dados sensíveis em evidências e relatórios quando aplicável. |
| Disponibilidade | Projetar componentes críticos para alta disponibilidade. |
| Escalabilidade | Suportar aumento horizontal de workers e filas. |
| Performance | Iniciar jobs assíncronos em tempo compatível com pipelines corporativos. |
| Confiabilidade | Implementar retries, idempotência e tolerância a falhas transitórias. |
| Observabilidade | Coletar métricas, logs estruturados e traces distribuídos. |
| Auditabilidade | Manter trilhas de auditoria consultáveis e exportáveis. |
| Usabilidade | Fornecer mensagens claras, filtros objetivos e relatórios compreensíveis. |
| Manutenibilidade | Preservar contratos versionados e baixo acoplamento entre módulos. |
| Portabilidade | Suportar execução local, containerizada e Kubernetes. |
| Compatibilidade | Expor contratos estáveis para MCP, API, CLI e integrações. |

## 15. Fluxos principais, alternativos e de exceção

### 15.1 Fluxo principal — execução de scan

1. Usuário ou pipeline solicita um scan informando tenant, projeto, alvo, ambiente e perfil de teste.
2. Plataforma autentica o solicitante.
3. Plataforma valida autorização e escopo do alvo.
4. Plataforma identifica policies e plugins aplicáveis.
5. Orquestrador cria job e publica evento na fila.
6. Worker consome job e prepara sandbox.
7. Plugins executam testes conforme contrato e limites configurados.
8. Resultados são normalizados, deduplicados e persistidos.
9. Evidências são armazenadas e associadas aos findings.
10. Quality gate é avaliado.
11. Resultado, decisão e relatórios ficam disponíveis para consulta.

### 15.2 Fluxos alternativos

| ID | Fluxo alternativo | Tratamento esperado |
|---|---|---|
| FA-001 | Scan agendado em vez de sob demanda | Scheduler cria solicitação no horário configurado e segue fluxo principal |
| FA-002 | Pipeline solicita apenas quality gate com scan já existente | Plataforma recupera resultado elegível e reavalia policy vigente |
| FA-003 | Plugin opcional indisponível | Scan continua com plugins obrigatórios e registra aviso operacional |
| FA-004 | Finding já existente detectado novamente | Plataforma atualiza recorrência, evidência e data de última detecção |
| FA-005 | Exceção vigente cobre finding bloqueante | Gate considera exceção e registra decisão com referência da aprovação |

### 15.3 Fluxos de exceção

| ID | Exceção | Resposta do sistema |
|---|---|---|
| FE-001 | Usuário não autenticado | Rejeitar solicitação com erro de autenticação |
| FE-002 | Usuário sem permissão | Rejeitar solicitação com erro de autorização e registrar auditoria |
| FE-003 | Alvo fora de escopo | Bloquear scan, registrar motivo e orientar cadastro/validação |
| FE-004 | Policy inexistente | Aplicar policy padrão segura ou bloquear conforme configuração corporativa |
| FE-005 | Falha transitória no worker | Reenfileirar job respeitando limite de retries |
| FE-006 | Timeout de plugin | Encerrar plugin, preservar logs e marcar resultado parcial |
| FE-007 | Evidência contém segredo detectado | Mascarar conteúdo, registrar ocorrência e restringir acesso |
| FE-008 | Armazenamento indisponível | Marcar execução como inconclusiva e emitir alerta operacional |
| FE-009 | Quality gate não calculável | Retornar estado inconclusivo e impedir aprovação automática |

## 16. Matriz de permissões

| Ação / Papel | Admin Plataforma | Admin Tenant | AppSec | QA | Desenvolvedor | DevOps/SRE | Auditor | Gestor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gerenciar tenants | C | N | N | N | N | N | R | R |
| Gerenciar projetos | C | C | A | N | N | N | R | R |
| Gerenciar usuários e grupos | C | C | N | N | N | N | R | N |
| Cadastrar alvos | C | C | C | A | A | A | R | R |
| Criar scans | C | C | C | C | A | C | R | R |
| Cancelar scans | C | C | C | A | N | C | R | R |
| Visualizar findings | C | C | C | C | C | C | R | R |
| Alterar status de findings | C | C | C | A | A | N | R | R |
| Aprovar exceções | C | C | C | N | N | N | R | R |
| Gerenciar policies | C | C | C | N | N | A | R | R |
| Gerenciar plugins | C | A | A | N | N | A | R | R |
| Gerar relatórios | C | C | C | C | A | A | C | C |
| Exportar evidências | C | C | C | A | N | A | C | A |
| Consultar auditoria | C | C | A | N | N | A | C | R |

Legenda: C = controle total; A = acesso limitado/assistido; R = somente leitura; N = não permitido.

## 17. Roadmap do produto

| Horizonte | Objetivo | Entregas previstas |
|---|---|---|
| 0-3 meses | MVP operacional | MCP Server básico, API de scans, cadastro de alvos, execução assíncrona, plugins iniciais, findings, gate simples e relatório JSON/HTML |
| 3-6 meses | Escala e governança | RBAC completo, policies avançadas, exceções, deduplicação, auditoria, integrações CI/CD e issue tracker |
| 6-9 meses | Enterprise readiness | Multi-tenant robusto, dashboards executivos, SIEM, retenção, assinatura de plugins, observabilidade completa |
| 9-12 meses | Otimização e inteligência | Correlação avançada, priorização por risco, recomendações enriquecidas, analytics e automações assistidas por IA |

## 18. MVP

### 18.1 Objetivo do MVP

Validar o valor central do produto: criar scans autorizados, executar testes automatizados de segurança, produzir findings padronizados e aplicar quality gate consumível por pipelines e clientes MCP.

### 18.2 Escopo do MVP

- Cadastro de tenant, projeto e alvo.
- Criação de scan via MCP/API/CLI.
- Execução assíncrona com fila e worker único ou pool simples.
- Plugins iniciais: security headers, TLS audit e OpenAPI basic checks.
- Normalização básica de findings.
- Evidências textuais e logs de execução.
- Quality gate por severidade crítica/alta.
- Relatório JSON e HTML simples.
- Auditoria mínima de criação, execução e consulta.

### 18.3 Fora do MVP

- Console Web completo.
- Correlação avançada entre múltiplos scanners.
- Aprovação formal de exceções por workflow complexo.
- Marketplace de plugins.
- Analytics preditivo.

## 19. Backlog priorizado

| Prioridade | Item | Tipo | Valor de negócio |
|---:|---|---|---|
| 1 | Criar modelo de tenant, projeto e alvo | Feature | Base de governança e isolamento |
| 2 | Implementar autenticação e autorização mínima | Feature | Segurança de acesso |
| 3 | Criar endpoint/tool MCP para iniciar scan | Feature | Valor central via MCP |
| 4 | Implementar orquestrador e fila de jobs | Feature | Execução assíncrona e escalável |
| 5 | Implementar worker de execução | Feature | Capacidade operacional de scan |
| 6 | Implementar plugin de security headers | Feature | Primeiro teste Web de alto valor |
| 7 | Implementar plugin de TLS audit | Feature | Validação de configuração crítica |
| 8 | Implementar importação OpenAPI básica | Feature | Cobertura inicial de APIs |
| 9 | Normalizar findings | Feature | Resultado padronizado e acionável |
| 10 | Implementar quality gate simples | Feature | Integração com release management |
| 11 | Gerar relatório JSON/HTML | Feature | Consumo técnico e evidência |
| 12 | Registrar auditoria mínima | Feature | Rastreabilidade corporativa |
| 13 | Integrar com CI/CD | Feature | Adoção por squads |
| 14 | Criar lifecycle de findings | Feature | Gestão de remediação |
| 15 | Implementar exceções com expiração | Feature | Governança de risco aceito |

## 20. KPIs

| KPI | Definição | Objetivo esperado |
|---|---|---|
| Cobertura de aplicações | Percentual de aplicações/projetos com scans configurados | Aumentar continuamente até cobertura corporativa definida |
| Frequência de scans | Média de execuções por projeto por período | Garantir validação contínua |
| Taxa de gates reprovados | Percentual de gates bloqueados por risco | Reduzir ao longo do tempo sem reduzir rigor |
| MTTR de vulnerabilidades | Tempo médio entre detecção e correção | Reduzir por severidade |
| Taxa de reincidência | Findings corrigidos que reaparecem | Reduzir por melhoria de qualidade |
| Falsos positivos confirmados | Percentual de findings classificados como falso positivo | Reduzir por ajuste de plugins e regras |
| SLA de triagem | Percentual de findings triados dentro do prazo | Atingir meta por severidade |
| Adoção por squads | Squads usando scans em pipeline | Aumentar por ondas de implantação |
| Disponibilidade da plataforma | Uptime dos componentes críticos | Atender meta corporativa |

## 21. Métricas operacionais e analíticas

- Quantidade de scans criados, executados, cancelados, falhos e inconclusivos.
- Tempo médio de fila, execução, normalização e geração de relatório.
- Distribuição de findings por severidade, tipo, plugin, projeto, ambiente e status.
- Quantidade de exceções ativas, expiradas, aprovadas e rejeitadas.
- Consumo de recursos por tenant, projeto, plugin e worker.
- Taxa de erro por integração, API, plugin e fila.
- Volume de evidências armazenadas e custo estimado por período.
- Percentual de scans com resultado parcial.
- Tendência de risco por release, sprint, produto e unidade de negócio.

## 22. Definition of Ready

Um item de backlog está pronto para desenvolvimento quando:

- Possui objetivo de negócio claro.
- Possui persona ou stakeholder beneficiado identificado.
- Possui escopo funcional e fora de escopo definidos.
- Possui critérios de aceite objetivos e testáveis.
- Possui dependências técnicas e funcionais mapeadas.
- Possui impactos de segurança, privacidade e auditoria avaliados.
- Possui prioridade definida pelo Product Owner.
- Possui dados, contratos ou integrações necessários identificados.
- Possui estratégia mínima de teste acordada.
- Está estimado ou dimensionado pela equipe.

## 23. Definition of Done

Um item é considerado concluído quando:

- Implementação atende aos critérios de aceite aprovados.
- Testes unitários, integração, contrato e/ou e2e aplicáveis foram executados com sucesso.
- Requisitos de segurança, autorização, auditoria e observabilidade foram implementados quando aplicáveis.
- Documentação funcional, técnica ou operacional foi atualizada.
- Logs, métricas e erros seguem padrão do produto.
- Contratos públicos foram versionados e revisados.
- Evidências de teste estão disponíveis.
- Revisão de código foi aprovada.
- Deploy em ambiente alvo foi validado ou está preparado conforme processo corporativo.
- Não há pendências críticas conhecidas para o escopo entregue.

## 24. Premissas

- Os alvos testados possuem autorização formal para execução de scans.
- A organização possui política de classificação de severidade ou adotará uma referência padrão como CVSS/OWASP.
- Ambientes produtivos exigem políticas mais restritivas de intensidade, janela e escopo.
- Integrações corporativas podem variar por organização e devem ser ativadas por adaptadores configuráveis.
- Plugins externos devem ser tratados como componentes de risco e executados com isolamento.

## 25. Riscos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| Scans causarem indisponibilidade em ambiente sensível | Alto | Policies por ambiente, limites de taxa, janelas de execução e allowlist |
| Falsos positivos reduzirem confiança | Médio | Deduplicação, triagem, calibração de plugins e feedback loop |
| Vazamento de dados em evidências | Alto | Mascaramento, criptografia, RBAC e retenção controlada |
| Plugins maliciosos ou vulneráveis | Alto | Assinatura, sandbox, revisão, permissões mínimas e catálogo aprovado |
| Baixa adoção por squads | Médio | Integração CI/CD simples, relatórios acionáveis e onboarding guiado |
| Crescimento de custo operacional | Médio | Métricas de consumo, quotas, autoscaling e políticas de retenção |

## 26. Glossário

| Termo | Definição |
|---|---|
| MCP | Model Context Protocol, protocolo para exposição padronizada de ferramentas e contexto a clientes compatíveis. |
| Scan | Execução planejada ou sob demanda de testes de segurança contra um alvo autorizado. |
| Target/Alvo | Aplicação Web, API ou endpoint autorizado para teste. |
| Finding/Achado | Resultado normalizado que representa uma vulnerabilidade, fraqueza ou observação de segurança. |
| Evidence/Evidência | Artefato que sustenta um finding, como logs, resposta HTTP, screenshot, HAR ou payload. |
| Quality Gate | Decisão automatizada que aprova, reprova ou torna inconclusivo um fluxo com base em políticas. |
| Plugin | Extensão executável responsável por um tipo específico de teste, parser, correlação ou relatório. |
| Tenant | Unidade lógica de isolamento organizacional. |
| Policy | Conjunto versionado de regras aplicadas a scans, findings, gates e exceções. |
| Exceção | Aceitação temporária e auditável de risco para um finding ou regra de gate. |
