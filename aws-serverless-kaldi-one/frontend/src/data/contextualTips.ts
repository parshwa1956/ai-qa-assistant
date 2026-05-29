export interface ContextualTip {
  id: string
  title: string
  steps: string[]
}

export const TIPS_BY_ROUTE: Record<string, ContextualTip> = {
  '/app/dashboard': {
    id: 'tip-dashboard',
    title: 'How to use your dashboard',
    steps: [
      'Stats update as you save test cases, bug reports, and other outputs to History.',
      'Recent projects and outputs help you jump back into ongoing work.',
      'Start in Workspace to generate your first artifact, then return here to track progress.',
    ],
  },
  '/app/workspace': {
    id: 'tip-workspace',
    title: 'Generating with AI',
    steps: [
      '1. Select a project in the header (required before Generate).',
      '2. Pick a workspace tab: QA, BA, Dev, or Flow to Requirement.',
      '3. Choose an AI tool card, then enter title and context.',
      '4. Attach screenshots or documents for richer results.',
      '5. Review output, then Save, Export, or Create Jira issue.',
    ],
  },
  '/app/history': {
    id: 'tip-history',
    title: 'Managing saved outputs',
    steps: [
      'Search across titles, types, and output text.',
      'Filter by the project selected in the header.',
      'Delete items you no longer need; exports are available per item.',
    ],
  },
  '/app/projects': {
    id: 'tip-projects',
    title: 'Project best practices',
    steps: [
      'General is your default project and cannot be deleted.',
      'Create a project per release, feature, or client for cleaner history.',
      'Renaming updates the label everywhere; deleting removes linked history.',
    ],
  },
  '/app/settings': {
    id: 'tip-settings',
    title: 'Integrations & preferences',
    steps: [
      'Save Jira URL, email, project key, and API token once.',
      'Test connection before creating issues from Workspace.',
      'Use the theme toggle for comfortable light or dark viewing.',
    ],
  },
}

export function tipForRoute(path: string): ContextualTip | null {
  for (const key of Object.keys(TIPS_BY_ROUTE)) {
    if (path.startsWith(key)) return TIPS_BY_ROUTE[key]
  }
  return null
}
