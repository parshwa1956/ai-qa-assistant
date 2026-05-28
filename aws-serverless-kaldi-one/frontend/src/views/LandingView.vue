<script setup lang="ts">
import { useRouter } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-blue-50/60 via-white to-surface-light dark:from-slate-900 dark:via-surface-dark dark:to-surface-dark">
    <header class="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
      <div class="flex items-center gap-3">
        <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-accent to-accent-soft text-xl font-bold text-white shadow-lift">K</div>
        <span class="text-xl font-bold">Kaldi One</span>
      </div>
      <div class="flex items-center gap-3">
        <ThemeToggle />
        <button type="button" class="btn-secondary" @click="router.push('/auth/login')">Sign in</button>
        <button type="button" class="btn-primary" @click="router.push('/auth/register')">Get started</button>
      </div>
    </header>

    <section class="mx-auto max-w-6xl px-6 pb-24 pt-12 text-center page-enter">
      <p class="inline-block rounded-full bg-accent/10 px-4 py-1 text-sm font-medium text-accent">AWS Serverless · Pay as you go</p>
      <h1 class="mt-6 text-4xl font-bold tracking-tight md:text-6xl">AI workspaces for QA, BA, and Dev teams</h1>
      <p class="mx-auto mt-6 max-w-2xl text-lg text-muted-light dark:text-muted-dark">
        Generate bug reports, test cases, user stories, technical tasks, and more — with secure Cognito auth, project history, and Jira integration.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <button type="button" class="btn-primary text-base" @click="router.push('/auth/login')">Launch Kaldi One</button>
        <button type="button" class="btn-secondary text-base" @click="router.push('/auth/login')">View pricing</button>
      </div>
      <div class="mt-20 grid gap-6 md:grid-cols-4">
        <div v-for="w in ['QA Workspace','BA Workspace','Dev Workspace','Flow to Requirement']" :key="w" class="glass-card p-6 text-left transition hover:-translate-y-1 hover:shadow-lift">
          <h3 class="font-semibold">{{ w }}</h3>
          <p class="mt-2 text-sm text-muted-light dark:text-muted-dark">Same mental model as the classic Kaldi One Streamlit app, rebuilt for production.</p>
        </div>
      </div>
    </section>
  </div>
</template>
