export interface Project {
  projectId: string
  name: string
  isDefault?: boolean
  createdAt?: string
  updatedAt?: string
}

export interface HistoryItem {
  itemId: string
  projectId: string
  itemType: string
  title: string
  inputContext?: string
  outputText?: string
  outputJson?: unknown
  mermaidCode?: string
  screenshotPath?: string
  sourceFilename?: string
  workspace?: string
  createdAt?: string
}

export interface GenerationResult {
  outputType: string
  outputText: string
  outputJson?: unknown
  tableData?: Record<string, unknown>[]
  mermaidCode?: string | null
  workspace?: string
  projectId?: string
}

export interface JiraConfig {
  jiraBaseUrl?: string
  jiraEmail?: string
  jiraProjectKey?: string
  configured?: boolean
}

export interface DashboardStats {
  totalProjects: number
  totalTestCases: number
  totalBugReports: number
  totalItems: number
  recentProjects: Project[]
  recentItems: Partial<HistoryItem>[]
}

export type WorkspaceId = 'qa' | 'ba' | 'dev' | 'flow'

export interface WorkspaceTool {
  id: string
  label: string
  description: string
  icon: string
}
