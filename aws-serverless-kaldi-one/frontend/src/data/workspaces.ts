import type { WorkspaceId, WorkspaceTool } from '@/types'

export const WORKSPACES: Record<WorkspaceId, { label: string; icon: string; tools: WorkspaceTool[] }> = {
  qa: {
    label: 'QA Workspace',
    icon: '🧪',
    tools: [
      { id: 'Bug Report', label: 'Bug Report', description: 'Structured defect report with optional screenshot vision.', icon: '🐛' },
      { id: 'Test Cases', label: 'Test Cases', description: 'Detailed functional and edge-case test cases.', icon: '✅' },
      { id: 'Test Scenarios', label: 'Test Scenarios', description: 'High-level scenarios for planning and coverage.', icon: '📋' },
    ],
  },
  ba: {
    label: 'BA Workspace',
    icon: '📐',
    tools: [
      { id: 'Requirement to User Story', label: 'Requirement → User Story', description: 'Convert requirements into INVEST-style stories.', icon: '📝' },
      { id: 'Acceptance Criteria Generator', label: 'Acceptance Criteria', description: 'Generate testable acceptance criteria.', icon: '☑️' },
      { id: 'Business Requirement Breakdown', label: 'Requirement Breakdown', description: 'Structured business requirement sections.', icon: '📑' },
      { id: 'User Story + Acceptance Criteria + Traceability', label: 'Story + AC + Traceability', description: 'Rich stories with traceability references.', icon: '🔗' },
      { id: 'Business Process Flow', label: 'Business Process Flow', description: 'Mermaid process flow from requirements.', icon: '🔀' },
      { id: 'Data Flow Diagram', label: 'Data Flow Diagram', description: 'Data movement diagram and step table.', icon: '🗂️' },
    ],
  },
  dev: {
    label: 'Dev Workspace',
    icon: '💻',
    tools: [
      { id: 'Technical Task Breakdown', label: 'Technical Tasks', description: 'Engineering work breakdown.', icon: '⚙️' },
      { id: 'API / Backend Tasks', label: 'API / Backend Tasks', description: 'Endpoint and service implementation tasks.', icon: '🔌' },
      { id: 'Developer Checklist', label: 'Developer Checklist', description: 'Pre-ship engineering checklist.', icon: '✔️' },
      { id: 'Smart Code Review', label: 'Smart Code Review', description: 'AI-assisted code review with severity tiers.', icon: '🔍' },
      { id: 'Technical Flow Diagram', label: 'Technical Flow Diagram', description: 'Technical process / sequence style flow.', icon: '📊' },
    ],
  },
  flow: {
    label: 'Flow to Requirement',
    icon: '🔄',
    tools: [
      { id: 'Flow to Requirement', label: 'Flow to Requirement', description: 'Generate business requirements from diagrams or files.', icon: '🎯' },
    ],
  },
}
