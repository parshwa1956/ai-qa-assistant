import { getIdToken } from './cognito'

const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || ''

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message)
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getIdToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${baseUrl}${path}`, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new ApiError((data as { error?: string }).error || res.statusText, res.status)
  }
  return data as T
}

export const api = {
  bootstrap: () => request<{ userId: string; email: string; projects: unknown[] }>('/auth/bootstrap', { method: 'POST', body: '{}' }),
  getProjects: () => request<{ projects: unknown[] }>('/projects'),
  createProject: (name: string) => request('/projects', { method: 'POST', body: JSON.stringify({ name }) }),
  updateProject: (projectId: string, name: string) =>
    request(`/projects/${projectId}`, { method: 'PUT', body: JSON.stringify({ name }) }),
  deleteProject: (projectId: string) => request(`/projects/${projectId}`, { method: 'DELETE' }),
  generate: (body: Record<string, unknown>) => request('/generate', { method: 'POST', body: JSON.stringify(body) }),
  getHistory: (params?: Record<string, string>) => {
    const q = new URLSearchParams(params).toString()
    return request<{ items: unknown[] }>(`/history${q ? `?${q}` : ''}`)
  },
  saveHistory: (body: Record<string, unknown>) => request('/history', { method: 'POST', body: JSON.stringify(body) }),
  deleteHistory: (itemId: string) => request(`/history/${itemId}`, { method: 'DELETE' }),
  exportHistory: (itemId: string, format: string, tableData?: unknown[]) =>
    request<{ downloadUrl: string }>(`/history/${itemId}/export`, {
      method: 'POST',
      body: JSON.stringify({ format, tableData }),
    }),
  presignUpload: (body: { filename: string; contentType: string; projectId: string }) =>
    request<{ uploadUrl: string; objectKey: string }>('/files/presign', { method: 'POST', body: JSON.stringify(body) }),
  getDashboard: () => request<import('@/types').DashboardStats>('/dashboard'),
  getJira: () => request<{ configured: boolean; config: unknown }>('/jira'),
  saveJira: (body: Record<string, string>) => request('/jira', { method: 'PUT', body: JSON.stringify(body) }),
  testJira: (body?: Record<string, string>) => request<{ success: boolean; message: string }>('/jira/test', { method: 'POST', body: JSON.stringify(body || { action: 'test' }) }),
  createJiraIssue: (body: Record<string, unknown>) => request('/jira/issues', { method: 'POST', body: JSON.stringify(body) }),
  deleteJira: () => request('/jira', { method: 'DELETE' }),
}
