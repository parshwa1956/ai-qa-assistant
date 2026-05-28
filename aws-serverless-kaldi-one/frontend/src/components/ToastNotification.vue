<script setup lang="ts">
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
</script>

<template>
  <div class="fixed bottom-20 right-4 z-50 flex flex-col gap-2 md:bottom-6">
    <div
      v-for="t in toast.items"
      :key="t.id"
      class="glass-card min-w-[240px] max-w-sm px-4 py-3 text-sm shadow-lift page-enter"
      :class="{
        'border-l-4 border-l-green-500': t.type === 'success',
        'border-l-4 border-l-red-500': t.type === 'error',
        'border-l-4 border-l-blue-500': t.type === 'info',
      }"
      role="status"
    >
      {{ t.message }}
    </div>
  </div>
</template>
