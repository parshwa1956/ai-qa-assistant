<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '@/components/AppShell.vue'
import { api } from '@/services/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const form = ref({
  jiraBaseUrl: '',
  jiraEmail: '',
  jiraProjectKey: '',
  jiraApiToken: '',
})
const configured = ref(false)
const saving = ref(false)

onMounted(async () => {
  const res = await api.getJira()
  configured.value = res.configured
  if (res.config) {
    const c = res.config as Record<string, string>
    form.value.jiraBaseUrl = c.jiraBaseUrl || ''
    form.value.jiraEmail = c.jiraEmail || ''
    form.value.jiraProjectKey = c.jiraProjectKey || ''
  }
})

async function save() {
  saving.value = true
  try {
    await api.saveJira(form.value)
    configured.value = true
    form.value.jiraApiToken = ''
    toast.push('Jira configuration saved (token not shown again)', 'success')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  try {
    const body = form.value.jiraApiToken
      ? form.value
      : { action: 'test' }
    const res = await api.testJira(body as Record<string, string>)
    toast.push(res.message, res.success ? 'success' : 'error')
  } catch (e) {
    toast.push((e as Error).message, 'error')
  }
}

async function remove() {
  await api.deleteJira()
  configured.value = false
  toast.push('Jira integration removed', 'info')
}
</script>

<template>
  <AppShell>
    <template #title>Settings</template>
    <template #subtitle>Jira integration and account</template>

    <div class="glass-card max-w-2xl space-y-4 p-6">
      <h3 class="font-semibold">Jira Integration</h3>
      <p class="text-sm text-muted-light dark:text-muted-dark">API token is stored securely in DynamoDB and never returned to the browser after save.</p>
      <input v-model="form.jiraBaseUrl" class="input-field" placeholder="https://your-domain.atlassian.net" />
      <input v-model="form.jiraEmail" class="input-field" placeholder="Jira email" />
      <input v-model="form.jiraProjectKey" class="input-field" placeholder="Project key (e.g. QA)" />
      <input
        v-model="form.jiraApiToken"
        type="password"
        class="input-field"
        :placeholder="configured ? 'Leave blank to keep existing token' : 'Jira API token'"
      />
      <div class="flex flex-wrap gap-3">
        <button type="button" class="btn-primary" :disabled="saving" @click="save">Save</button>
        <button type="button" class="btn-secondary" @click="testConnection">Test connection</button>
        <button v-if="configured" type="button" class="text-sm text-red-500" @click="remove">Remove</button>
      </div>
    </div>
  </AppShell>
</template>
