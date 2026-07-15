import { useEffect, useMemo, useState, type FormEvent } from 'react';

type AuthState = {
  access_token: string;
  token_type: string;
};

type Scan = {
  id: number;
  name: string;
  target_url: string;
  status: string;
  description: string;
  created_at?: string;
  updated_at?: string;
  findings_count?: number;
};

type Finding = {
  id: number;
  scan_id?: number | null;
  title: string;
  severity: string;
  description: string;
};

type ScanEvent = {
  event: string;
  details?: Record<string, unknown>;
};

type GovernanceSnapshot = {
  events: ScanEvent[];
  metrics: Record<string, number>;
};

type DashboardSummary = {
  total_scans: number;
  running_scans: number;
  total_findings: number;
  critical_findings: number;
  recent_scans: Scan[];
};

type QueueStatus = {
  queue_length: number;
  status: string;
};

type Tenant = {
  id: number;
  name: string;
  slug: string;
  description: string;
};

type Project = {
  id: number;
  name: string;
  tenant_id: number;
  description: string;
};

type Environment = {
  id: number;
  name: string;
  project_id: number;
  description: string;
};

type Target = {
  id: number;
  name: string;
  url: string;
  project_id: number;
  environment_id: number;
  description: string;
};

const severityColors: Record<string, string> = {
  critical: '#ff4d4f',
  high: '#ff7a00',
  medium: '#fadb14',
  low: '#52c41a',
};

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const normalizeCollection = <T extends { id: number; name: string }>(items: T[]) => {
  const uniqueItems = Array.from(new Map(items.map((item) => [item.id, item])).values());
  return uniqueItems.sort((left, right) => left.name.localeCompare(right.name));
};

const fetchWithTimeout = async (url: string, init?: RequestInit, timeoutMs = 8000) => {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    window.clearTimeout(timer);
  }
};

function App() {
  const [scans, setScans] = useState<Scan[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [targets, setTargets] = useState<Target[]>([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');
  const [enterpriseForm, setEnterpriseForm] = useState<'tenant' | 'project' | 'environment' | 'target'>('tenant');
  const [tenantForm, setTenantForm] = useState({ name: '', slug: '', description: '' });
  const [targetForm, setTargetForm] = useState({ name: '', url: '', project_id: '', environment_id: '', description: '' });
  const [projectForm, setProjectForm] = useState({ name: '', tenant_id: '', description: '' });
  const [environmentForm, setEnvironmentForm] = useState({ name: '', project_id: '', description: '' });
  const [runningScanId, setRunningScanId] = useState<number | null>(null);
  const [collectingScanId, setCollectingScanId] = useState<number | null>(null);
  const [form, setForm] = useState({ name: '', target_url: '', target_id: '', description: '' });
  const [auth, setAuth] = useState<AuthState | null>(() => {
    const stored = localStorage.getItem('security-qa-auth');
    return stored ? JSON.parse(stored) as AuthState : null;
  });
  const [loginForm, setLoginForm] = useState({ username: 'admin', password: 'password123' });
  const [authError, setAuthError] = useState('');
  const [scanEvents, setScanEvents] = useState<Record<number, ScanEvent[]>>({});
  const [governanceSnapshot, setGovernanceSnapshot] = useState<GovernanceSnapshot | null>(null);
  const [auditEvents, setAuditEvents] = useState<ScanEvent[]>([]);
  const [showGovernanceDetails, setShowGovernanceDetails] = useState(false);

  const loadDashboard = async (isInitialLoad = false) => {
    if (!auth?.access_token) {
      return;
    }

    try {
      if (isInitialLoad) {
        setLoading(true);
      }
      const [summaryResponse, findingsResponse, tenantsResponse, projectsResponse, environmentsResponse, targetsResponse, queueResponse] = await Promise.allSettled([
        fetchWithTimeout(`${API_BASE_URL}/api/v1/dashboard/summary`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetchWithTimeout(`${API_BASE_URL}/api/v1/findings`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetchWithTimeout(`${API_BASE_URL}/api/v1/tenants`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetchWithTimeout(`${API_BASE_URL}/api/v1/projects`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetchWithTimeout(`${API_BASE_URL}/api/v1/environments`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetchWithTimeout(`${API_BASE_URL}/api/v1/targets`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetchWithTimeout(`${API_BASE_URL}/api/v1/scans/queue/status`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
      ]);

      const responsePairs = [
        [summaryResponse, 'summary'],
        [findingsResponse, 'findings'],
        [tenantsResponse, 'tenants'],
        [projectsResponse, 'projects'],
        [environmentsResponse, 'environments'],
        [targetsResponse, 'targets'],
        [queueResponse, 'queue'],
      ] as const;

      const hasAnySuccessfulResponse = responsePairs.some(([result]) => result.status === 'fulfilled' && result.value.ok);
      if (!hasAnySuccessfulResponse) {
        throw new Error('Não foi possível carregar o dashboard.');
      }

      const summaryData = summaryResponse.status === 'fulfilled' && summaryResponse.value.ok
        ? await summaryResponse.value.json() as DashboardSummary
        : null;
      const findingsData = findingsResponse.status === 'fulfilled' && findingsResponse.value.ok
        ? await findingsResponse.value.json() as Finding[]
        : [];
      const tenantsData = tenantsResponse.status === 'fulfilled' && tenantsResponse.value.ok
        ? await tenantsResponse.value.json() as Tenant[]
        : [];
      const projectsData = projectsResponse.status === 'fulfilled' && projectsResponse.value.ok
        ? await projectsResponse.value.json() as Project[]
        : [];
      const environmentsData = environmentsResponse.status === 'fulfilled' && environmentsResponse.value.ok
        ? await environmentsResponse.value.json() as Environment[]
        : [];
      const targetsData = targetsResponse.status === 'fulfilled' && targetsResponse.value.ok
        ? await targetsResponse.value.json() as Target[]
        : [];
      const queueData = queueResponse.status === 'fulfilled' && queueResponse.value.ok
        ? await queueResponse.value.json() as QueueStatus
        : { queue_length: 0, status: 'unknown' };

      setSummary(summaryData ?? {
        total_scans: 0,
        running_scans: 0,
        total_findings: 0,
        critical_findings: 0,
        recent_scans: [],
      });
      setScans(summaryData?.recent_scans || []);
      setFindings(findingsData || []);
      setTenants(normalizeCollection(tenantsData || []));
      setProjects(normalizeCollection(projectsData || []));
      setEnvironments(normalizeCollection(environmentsData || []));
      setTargets(normalizeCollection(targetsData || []));
      setQueueStatus(queueData);
      setFilter('all');
      if (!summaryData) {
        setErrorMessage('Alguns dados do dashboard não puderam ser carregados.');
      } else {
        setErrorMessage('');
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Erro inesperado ao carregar o dashboard.');
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (!auth) {
      return;
    }

    void loadDashboard(true);
    void loadGovernance();
    const intervalId = window.setInterval(() => {
      void loadDashboard(false);
      void loadGovernance();
    }, 10000);

    return () => window.clearInterval(intervalId);
  }, [auth]);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      setSubmitting(true);
      setAuthError('');
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      });

      if (!response.ok) {
        throw new Error('Credenciais inválidas.');
      }

      const nextAuth = await response.json() as AuthState;
      localStorage.setItem('security-qa-auth', JSON.stringify(nextAuth));
      setAuth(nextAuth);
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Falha ao autenticar.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('security-qa-auth');
    setAuth(null);
    setSummary(null);
    setScans([]);
    setFindings([]);
  };

  const handleCreateTenant = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!tenantForm.name.trim() || !tenantForm.slug.trim()) {
      setSubmitMessage('Nome e slug do tenant são obrigatórios.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitMessage('');
      const response = await fetch(`${API_BASE_URL}/api/v1/tenants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth?.access_token ?? ''}`,
        },
        body: JSON.stringify(tenantForm),
      });

      if (!response.ok) {
        throw new Error('Falha ao criar tenant.');
      }

      setTenantForm({ name: '', slug: '', description: '' });
      setSubmitMessage('Tenant criado com sucesso.');
      await loadDashboard();
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível criar o tenant.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateProject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!projectForm.name.trim() || !projectForm.tenant_id) {
      setSubmitMessage('Nome do projeto e tenant são obrigatórios.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitMessage('');
      const response = await fetch(`${API_BASE_URL}/api/v1/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth?.access_token ?? ''}`,
        },
        body: JSON.stringify({
          name: projectForm.name,
          tenant_id: Number(projectForm.tenant_id),
          description: projectForm.description,
        }),
      });

      if (!response.ok) {
        throw new Error('Falha ao criar projeto.');
      }

      setProjectForm({ name: '', tenant_id: '', description: '' });
      setSubmitMessage('Projeto criado com sucesso.');
      await loadDashboard();
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível criar o projeto.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateEnvironment = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!environmentForm.name.trim() || !environmentForm.project_id) {
      setSubmitMessage('Nome do ambiente e projeto são obrigatórios.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitMessage('');
      const response = await fetch(`${API_BASE_URL}/api/v1/environments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth?.access_token ?? ''}`,
        },
        body: JSON.stringify({
          name: environmentForm.name,
          project_id: Number(environmentForm.project_id),
          description: environmentForm.description,
        }),
      });

      if (!response.ok) {
        throw new Error('Falha ao criar ambiente.');
      }

      setEnvironmentForm({ name: '', project_id: '', description: '' });
      setSubmitMessage('Ambiente criado com sucesso.');
      await loadDashboard();
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível criar o ambiente.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateTarget = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!targetForm.name.trim() || !targetForm.url.trim() || !targetForm.project_id || !targetForm.environment_id) {
      setSubmitMessage('Nome, URL, projeto e ambiente são obrigatórios.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitMessage('');
      const response = await fetch(`${API_BASE_URL}/api/v1/targets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth?.access_token ?? ''}`,
        },
        body: JSON.stringify({
          name: targetForm.name,
          url: targetForm.url,
          project_id: Number(targetForm.project_id),
          environment_id: Number(targetForm.environment_id),
          description: targetForm.description,
        }),
      });

      if (!response.ok) {
        throw new Error('Falha ao criar target.');
      }

      setTargetForm({ name: '', url: '', project_id: '', environment_id: '', description: '' });
      setSubmitMessage('Target criado com sucesso.');
      await loadDashboard();
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível criar o target.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!form.name.trim() || !form.target_url.trim()) {
      setSubmitMessage('Nome e URL alvo são obrigatórios.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitMessage('');
      const payload = {
        name: form.name,
        target_url: form.target_url,
        description: form.description,
        ...(form.target_id ? { target_id: Number(form.target_id) } : {}),
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/scans`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth?.access_token ?? ''}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Falha ao criar o scan.');
      }

      setForm({ name: '', target_url: '', target_id: '', description: '' });
      setSubmitMessage('Scan criado com sucesso.');
      await loadDashboard();
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível criar o scan.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRunScan = async (scanId: number) => {
    try {
      setRunningScanId(scanId);
      const response = await fetch(`${API_BASE_URL}/api/v1/scans/${scanId}/run`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth?.access_token ?? ''}` },
      });

      if (!response.ok) {
        throw new Error('Falha ao executar o scan.');
      }

      await loadDashboard();
      setSubmitMessage('Scan executado com sucesso.');
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível executar o scan.');
    } finally {
      setRunningScanId(null);
    }
  };

  const handleCollectResults = async (scanId: number) => {
    try {
      setCollectingScanId(scanId);
      const response = await fetch(`${API_BASE_URL}/api/v1/scans/${scanId}/collect`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth?.access_token ?? ''}` },
      });

      if (!response.ok) {
        throw new Error('Falha ao coletar os resultados.');
      }

      await loadDashboard();
      setSubmitMessage('Resultados coletados com sucesso.');
    } catch (error) {
      setSubmitMessage(error instanceof Error ? error.message : 'Não foi possível coletar os resultados.');
    } finally {
      setCollectingScanId(null);
    }
  };

  const loadScanEvents = async (scanId: number) => {
    if (!auth?.access_token) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/scans/${scanId}/events`, {
        headers: { Authorization: `Bearer ${auth.access_token}` },
      });

      if (!response.ok) {
        return;
      }

      const events = await response.json() as ScanEvent[];
      setScanEvents((current) => ({ ...current, [scanId]: events }));
    } catch {
      // Ignore event loading errors and keep the UI resilient.
    }
  };

  const loadGovernance = async () => {
    if (!auth?.access_token) {
      return;
    }

    try {
      const [auditResponse, observabilityResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/audit/events/export`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
        fetch(`${API_BASE_URL}/api/v1/observability/metrics/export`, {
          headers: { Authorization: `Bearer ${auth.access_token}` },
        }),
      ]);

      if (!auditResponse.ok || !observabilityResponse.ok) {
        return;
      }

      const [auditData, observabilityData] = await Promise.all([
        auditResponse.json() as Promise<ScanEvent[]>,
        observabilityResponse.json() as Promise<GovernanceSnapshot>,
      ]);

      setAuditEvents(auditData || []);
      setGovernanceSnapshot(observabilityData || { events: [], metrics: {} });
    } catch {
      // Ignore governance loading errors and keep the UI resilient.
    }
  };

  const filteredFindings = useMemo(() => {
    if (filter === 'all') return findings;
    return findings.filter((finding) => finding.severity === filter);
  }, [findings, filter]);

  const visibleTenants = useMemo(() => normalizeCollection(tenants).slice(0, 6), [tenants]);
  const visibleProjects = useMemo(() => normalizeCollection(projects).slice(0, 6), [projects]);
  const visibleEnvironments = useMemo(() => normalizeCollection(environments).slice(0, 6), [environments]);
  const visibleTargets = useMemo(() => normalizeCollection(targets).slice(0, 6), [targets]);

  if (!auth) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#07111f', color: '#f5f7fb' }}>
        <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 24, width: 360 }}>
          <h2 style={{ marginTop: 0 }}>Entrar no Security QA MCP</h2>
          <form onSubmit={handleLogin} style={{ display: 'grid', gap: 12 }}>
            <input
              value={loginForm.username}
              onChange={(event) => setLoginForm((current) => ({ ...current, username: event.target.value }))}
              placeholder="Usuário"
              style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }}
            />
            <input
              type="password"
              value={loginForm.password}
              onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
              placeholder="Senha"
              style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }}
            />
            <button type="submit" disabled={submitting} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 14px', fontWeight: 700 }}>
              {submitting ? 'Entrando...' : 'Entrar'}
            </button>
            {authError ? <span style={{ color: '#ff7a00', fontSize: 13 }}>{authError}</span> : null}
          </form>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#07111f', color: '#f5f7fb' }}>
        Carregando dashboard...
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#07111f', color: '#f5f7fb' }}>
        {errorMessage}
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#07111f', color: '#f5f7fb', fontFamily: 'Inter, sans-serif' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: 24 }}>
        <header style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
          <div>
            <h1 style={{ fontSize: 32, marginBottom: 8 }}>Security QA MCP</h1>
            <p style={{ margin: 0, color: '#8fa3bf' }}>Dashboard operacional para scans e findings de segurança.</p>
          </div>
          <button type="button" onClick={handleLogout} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '8px 12px', cursor: 'pointer' }}>
            Sair
          </button>
        </header>

        <section style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16, marginBottom: 24 }}>
          <h2 style={{ marginTop: 0, marginBottom: 12 }}>Criar novo scan</h2>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
              <input
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                placeholder="Nome do scan"
                style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }}
              />
              <select
                value={form.target_id}
                onChange={(event) => {
                  const nextTargetId = event.target.value;
                  const selectedTarget = targets.find((target) => String(target.id) === nextTargetId);
                  setForm((current) => ({
                    ...current,
                    target_id: nextTargetId,
                    target_url: selectedTarget?.url ?? current.target_url,
                  }));
                }}
                style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }}
              >
                <option value="">URL manual</option>
                {targets.map((target) => (
                  <option key={target.id} value={String(target.id)}>
                    {target.name} — {target.url}
                  </option>
                ))}
              </select>
            </div>
            <input
              value={form.target_url}
              onChange={(event) => setForm((current) => ({ ...current, target_url: event.target.value, target_id: current.target_id }))}
              placeholder="URL alvo (manual ou preenchida automaticamente)"
              style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }}
            />
            <textarea
              value={form.description}
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
              placeholder="Descrição do scan"
              rows={3}
              style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px', resize: 'vertical' }}
            />
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <button
                type="submit"
                disabled={submitting}
                style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 14px', cursor: submitting ? 'wait' : 'pointer', fontWeight: 700 }}
              >
                {submitting ? 'Criando...' : 'Criar scan'}
              </button>
              {submitMessage ? <span style={{ color: submitMessage.includes('sucesso') ? '#7ee787' : '#ff7a00', fontSize: 13 }}>{submitMessage}</span> : null}
            </div>
          </form>
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 24 }}>
          <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16 }}>
            <div style={{ color: '#8fa3bf', fontSize: 13 }}>Total de scans</div>
            <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>{summary?.total_scans ?? scans.length}</div>
          </div>
          <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16 }}>
            <div style={{ color: '#8fa3bf', fontSize: 13 }}>Scans em execução</div>
            <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>{summary?.running_scans ?? 0}</div>
          </div>
          <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16 }}>
            <div style={{ color: '#8fa3bf', fontSize: 13 }}>Fila de execução</div>
            <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>{queueStatus?.queue_length ?? 0}</div>
            <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 4 }}>{queueStatus?.status ?? 'inativa'}</div>
          </div>
          <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16 }}>
            <div style={{ color: '#8fa3bf', fontSize: 13 }}>Findings críticos</div>
            <div style={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}>{summary?.critical_findings ?? findings.filter((finding) => finding.severity === 'critical').length}</div>
          </div>
        </section>

        <section style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16, marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <h2 style={{ margin: 0 }}>Contexto enterprise</h2>
            <select value={enterpriseForm} onChange={(event) => setEnterpriseForm(event.target.value as 'tenant' | 'project' | 'environment' | 'target')} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '6px 8px' }}>
              <option value="tenant">Novo tenant</option>
              <option value="project">Novo projeto</option>
              <option value="environment">Novo ambiente</option>
              <option value="target">Novo target</option>
            </select>
          </div>

          {enterpriseForm === 'tenant' ? (
            <form onSubmit={handleCreateTenant} style={{ display: 'grid', gap: 12 }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                <input value={tenantForm.name} onChange={(event) => setTenantForm((current) => ({ ...current, name: event.target.value }))} placeholder="Nome do tenant" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
                <input value={tenantForm.slug} onChange={(event) => setTenantForm((current) => ({ ...current, slug: event.target.value }))} placeholder="Slug" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
              </div>
              <textarea value={tenantForm.description} onChange={(event) => setTenantForm((current) => ({ ...current, description: event.target.value }))} placeholder="Descrição" rows={2} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px', resize: 'vertical' }} />
              <button type="submit" disabled={submitting} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 14px', fontWeight: 700, width: 180 }}>{submitting ? 'Criando...' : 'Criar tenant'}</button>
            </form>
          ) : null}

          {enterpriseForm === 'project' ? (
            <form onSubmit={handleCreateProject} style={{ display: 'grid', gap: 12 }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                <input value={projectForm.name} onChange={(event) => setProjectForm((current) => ({ ...current, name: event.target.value }))} placeholder="Nome do projeto" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
                <input value={projectForm.tenant_id} onChange={(event) => setProjectForm((current) => ({ ...current, tenant_id: event.target.value }))} placeholder="ID do tenant" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
              </div>
              <textarea value={projectForm.description} onChange={(event) => setProjectForm((current) => ({ ...current, description: event.target.value }))} placeholder="Descrição" rows={2} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px', resize: 'vertical' }} />
              <button type="submit" disabled={submitting} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 14px', fontWeight: 700, width: 180 }}>{submitting ? 'Criando...' : 'Criar projeto'}</button>
            </form>
          ) : null}

          {enterpriseForm === 'environment' ? (
            <form onSubmit={handleCreateEnvironment} style={{ display: 'grid', gap: 12 }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                <input value={environmentForm.name} onChange={(event) => setEnvironmentForm((current) => ({ ...current, name: event.target.value }))} placeholder="Nome do ambiente" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
                <input value={environmentForm.project_id} onChange={(event) => setEnvironmentForm((current) => ({ ...current, project_id: event.target.value }))} placeholder="ID do projeto" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
              </div>
              <textarea value={environmentForm.description} onChange={(event) => setEnvironmentForm((current) => ({ ...current, description: event.target.value }))} placeholder="Descrição" rows={2} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px', resize: 'vertical' }} />
              <button type="submit" disabled={submitting} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 14px', fontWeight: 700, width: 180 }}>{submitting ? 'Criando...' : 'Criar ambiente'}</button>
            </form>
          ) : null}

          {enterpriseForm === 'target' ? (
            <form onSubmit={handleCreateTarget} style={{ display: 'grid', gap: 12 }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                <input value={targetForm.name} onChange={(event) => setTargetForm((current) => ({ ...current, name: event.target.value }))} placeholder="Nome do target" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
                <input value={targetForm.url} onChange={(event) => setTargetForm((current) => ({ ...current, url: event.target.value }))} placeholder="URL" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                <input value={targetForm.project_id} onChange={(event) => setTargetForm((current) => ({ ...current, project_id: event.target.value }))} placeholder="ID do projeto" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
                <input value={targetForm.environment_id} onChange={(event) => setTargetForm((current) => ({ ...current, environment_id: event.target.value }))} placeholder="ID do ambiente" style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px' }} />
              </div>
              <textarea value={targetForm.description} onChange={(event) => setTargetForm((current) => ({ ...current, description: event.target.value }))} placeholder="Descrição" rows={2} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '10px 12px', resize: 'vertical' }} />
              <button type="submit" disabled={submitting} style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 14px', fontWeight: 700, width: 180 }}>{submitting ? 'Criando...' : 'Criar target'}</button>
            </form>
          ) : null}

          {submitMessage ? <div style={{ marginTop: 12, color: submitMessage.includes('sucesso') ? '#7ee787' : '#ff7a00', fontSize: 13 }}>{submitMessage}</div> : null}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginTop: 16 }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <h3 style={{ margin: 0 }}>Tenants</h3>
                <span style={{ color: '#8fa3bf', fontSize: 12 }}>{tenants.length} total</span>
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                {visibleTenants.length === 0 ? <div style={{ color: '#8fa3bf' }}>Nenhum tenant cadastrado.</div> : visibleTenants.map((tenant) => (
                  <div key={tenant.id} style={{ background: '#13233c', borderRadius: 10, padding: 10 }}>
                    <strong>{tenant.name}</strong>
                    <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 4 }}>{tenant.slug}</div>
                  </div>
                ))}
                {tenants.length > visibleTenants.length ? <div style={{ color: '#8fa3bf', fontSize: 12 }}>… e mais {tenants.length - visibleTenants.length} itens</div> : null}
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <h3 style={{ margin: 0 }}>Projetos</h3>
                <span style={{ color: '#8fa3bf', fontSize: 12 }}>{projects.length} total</span>
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                {visibleProjects.length === 0 ? <div style={{ color: '#8fa3bf' }}>Nenhum projeto cadastrado.</div> : visibleProjects.map((project) => (
                  <div key={project.id} style={{ background: '#13233c', borderRadius: 10, padding: 10 }}>
                    <strong>{project.name}</strong>
                    <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 4 }}>Tenant #{project.tenant_id}</div>
                  </div>
                ))}
                {projects.length > visibleProjects.length ? <div style={{ color: '#8fa3bf', fontSize: 12 }}>… e mais {projects.length - visibleProjects.length} itens</div> : null}
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <h3 style={{ margin: 0 }}>Ambientes</h3>
                <span style={{ color: '#8fa3bf', fontSize: 12 }}>{environments.length} total</span>
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                {visibleEnvironments.length === 0 ? <div style={{ color: '#8fa3bf' }}>Nenhum ambiente cadastrado.</div> : visibleEnvironments.map((environment) => (
                  <div key={environment.id} style={{ background: '#13233c', borderRadius: 10, padding: 10 }}>
                    <strong>{environment.name}</strong>
                    <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 4 }}>Projeto #{environment.project_id}</div>
                  </div>
                ))}
                {environments.length > visibleEnvironments.length ? <div style={{ color: '#8fa3bf', fontSize: 12 }}>… e mais {environments.length - visibleEnvironments.length} itens</div> : null}
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <h3 style={{ margin: 0 }}>Targets</h3>
                <span style={{ color: '#8fa3bf', fontSize: 12 }}>{targets.length} total</span>
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                {visibleTargets.length === 0 ? <div style={{ color: '#8fa3bf' }}>Nenhum target cadastrado.</div> : visibleTargets.map((target) => (
                  <div key={target.id} style={{ background: '#13233c', borderRadius: 10, padding: 10 }}>
                    <strong>{target.name}</strong>
                    <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 4 }}>{target.url}</div>
                  </div>
                ))}
                {targets.length > visibleTargets.length ? <div style={{ color: '#8fa3bf', fontSize: 12 }}>… e mais {targets.length - visibleTargets.length} itens</div> : null}
              </div>
            </div>
          </div>
        </section>

        <section style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16, marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <h2 style={{ margin: 0 }}>Governança e auditoria</h2>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="button" onClick={() => setShowGovernanceDetails((current) => !current)} style={{ background: 'transparent', color: '#7dd3fc', border: '1px solid #24324d', borderRadius: 8, padding: '6px 10px', cursor: 'pointer', fontSize: 12 }}>
                {showGovernanceDetails ? 'Ocultar detalhes' : 'Mostrar detalhes'}
              </button>
              <a href={`${API_BASE_URL}/api/v1/audit/events/export?format=csv`} style={{ background: '#0f766e', color: '#fff', border: 'none', borderRadius: 8, padding: '6px 10px', fontSize: 12, textDecoration: 'none' }}>
                Exportar auditoria CSV
              </a>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
            <div style={{ background: '#13233c', borderRadius: 12, padding: 12 }}>
              <div style={{ color: '#8fa3bf', fontSize: 12, marginBottom: 8 }}>Eventos de observabilidade</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{governanceSnapshot?.events.length ?? 0}</div>
              <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 6 }}>
                {Object.entries(governanceSnapshot?.metrics ?? {}).slice(0, 3).map(([key, value]) => `${key}: ${value}`).join(' • ')}
              </div>
            </div>
            <div style={{ background: '#13233c', borderRadius: 12, padding: 12 }}>
              <div style={{ color: '#8fa3bf', fontSize: 12, marginBottom: 8 }}>Eventos de auditoria</div>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{auditEvents.length}</div>
              <div style={{ color: '#8fa3bf', fontSize: 12, marginTop: 6 }}>
                Últimos registros capturados para compliance e rastreio.
              </div>
            </div>
          </div>
          {showGovernanceDetails ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginTop: 16 }}>
              <div style={{ background: '#0b1220', borderRadius: 12, padding: 12 }}>
                <h3 style={{ marginTop: 0, marginBottom: 8 }}>Eventos de observabilidade</h3>
                <div style={{ display: 'grid', gap: 8 }}>
                  {(governanceSnapshot?.events ?? []).slice(0, 8).map((event, index) => (
                    <div key={`${event.event}-${index}`} style={{ background: '#13233c', borderRadius: 8, padding: 8, fontSize: 12, color: '#dce7ff' }}>
                      <strong>{event.event}</strong>
                      {event.details && Object.keys(event.details).length ? <div style={{ color: '#8fa3bf', marginTop: 4 }}>{JSON.stringify(event.details)}</div> : null}
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ background: '#0b1220', borderRadius: 12, padding: 12 }}>
                <h3 style={{ marginTop: 0, marginBottom: 8 }}>Eventos de auditoria</h3>
                <div style={{ display: 'grid', gap: 8 }}>
                  {auditEvents.slice(0, 8).map((event, index) => (
                    <div key={`${event.event}-${index}`} style={{ background: '#13233c', borderRadius: 8, padding: 8, fontSize: 12, color: '#dce7ff' }}>
                      <strong>{event.event}</strong>
                      {event.details && Object.keys(event.details).length ? <div style={{ color: '#8fa3bf', marginTop: 4 }}>{JSON.stringify(event.details)}</div> : null}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: 20 }}>
          <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16 }}>
            <h2 style={{ marginTop: 0 }}>Scans recentes</h2>
            <div style={{ display: 'grid', gap: 12 }}>
              {scans.length === 0 ? (
                <div style={{ color: '#8fa3bf' }}>Nenhum scan encontrado ainda.</div>
              ) : (
                scans.map((scan) => (
                  <div key={scan.id} style={{ background: '#13233c', borderRadius: 12, padding: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong>{scan.name}</strong>
                      <span style={{ fontSize: 12, textTransform: 'uppercase', color: '#7ee787' }}>{scan.status}</span>
                    </div>
                    <div style={{ color: '#8fa3bf', marginTop: 6, fontSize: 13 }}>{scan.target_url}</div>
                    {(() => {
                      const targetContext = targets.find((target) => target.url === scan.target_url);
                      const projectContext = projects.find((project) => project.id === targetContext?.project_id);
                      const environmentContext = environments.find((environment) => environment.id === targetContext?.environment_id);
                      return targetContext ? (
                        <div style={{ color: '#7dd3fc', marginTop: 6, fontSize: 12 }}>
                          Target: {targetContext.name} • Projeto: {projectContext?.name ?? `#${targetContext.project_id}`} • Ambiente: {environmentContext?.name ?? `#${targetContext.environment_id}`}
                        </div>
                      ) : null;
                    })()}
                    <div style={{ color: '#8fa3bf', marginTop: 4, fontSize: 12 }}>
                      {scan.findings_count ?? 0} findings • {scan.created_at ? new Date(scan.created_at).toLocaleString('pt-BR') : 'Sem timestamp'}
                    </div>
                    <div style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                      <button
                        type="button"
                        onClick={() => {
                          void handleRunScan(scan.id);
                          void loadScanEvents(scan.id);
                        }}
                        disabled={runningScanId === scan.id}
                        style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 10px', cursor: runningScanId === scan.id ? 'wait' : 'pointer', fontWeight: 700 }}
                      >
                        {runningScanId === scan.id ? 'Executando...' : 'Executar scan'}
                      </button>
                      <button
                        type="button"
                        onClick={() => void handleCollectResults(scan.id)}
                        disabled={collectingScanId === scan.id}
                        style={{ background: '#0f766e', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 10px', cursor: collectingScanId === scan.id ? 'wait' : 'pointer', fontWeight: 700 }}
                      >
                        {collectingScanId === scan.id ? 'Coletando...' : 'Coletar resultados'}
                      </button>
                    </div>
                    <div style={{ marginTop: 10 }}>
                      <button
                        type="button"
                        onClick={() => void loadScanEvents(scan.id)}
                        style={{ background: 'transparent', color: '#7dd3fc', border: '1px solid #24324d', borderRadius: 8, padding: '6px 10px', cursor: 'pointer', fontSize: 12 }}
                      >
                        Ver eventos
                      </button>
                      {scanEvents[scan.id]?.length ? (
                        <div style={{ marginTop: 8, display: 'grid', gap: 6 }}>
                          {scanEvents[scan.id].slice(-3).map((event, index) => (
                            <div key={`${event.event}-${index}`} style={{ background: '#0b1220', borderRadius: 8, padding: '8px 10px', fontSize: 12, color: '#dce7ff' }}>
                              <strong>{event.event}</strong>
                              {event.details && Object.keys(event.details).length ? (
                                <div style={{ color: '#8fa3bf', marginTop: 4 }}>{JSON.stringify(event.details)}</div>
                              ) : null}
                            </div>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div style={{ background: '#0f1b2e', border: '1px solid #24324d', borderRadius: 16, padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h2 style={{ margin: 0 }}>Findings</h2>
              <select value={filter} onChange={(event) => setFilter(event.target.value)} style={{ background: '#13233c', color: '#f5f7fb', border: '1px solid #24324d', borderRadius: 8, padding: '6px 8px' }}>
                <option value="all">Todas</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div style={{ display: 'grid', gap: 12 }}>
              {filteredFindings.length === 0 ? (
                <div style={{ color: '#8fa3bf' }}>Nenhum finding encontrado.</div>
              ) : (
                filteredFindings.map((finding) => (
                  <div key={finding.id} style={{ background: '#13233c', borderRadius: 12, padding: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong>{finding.title}</strong>
                      <span style={{ color: severityColors[finding.severity] || '#8fa3bf', fontWeight: 700, textTransform: 'uppercase', fontSize: 12 }}>
                        {finding.severity}
                      </span>
                    </div>
                    <div style={{ color: '#8fa3bf', marginTop: 6, fontSize: 13 }}>{finding.description}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
