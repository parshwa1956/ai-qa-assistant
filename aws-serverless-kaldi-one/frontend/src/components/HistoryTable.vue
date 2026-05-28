<script setup lang="ts">
import type { HistoryItem } from '@/types'
import EmptyState from './EmptyState.vue'
import LoadingSkeleton from './LoadingSkeleton.vue'

defineProps<{ items: HistoryItem[]; loading?: boolean }>()
defineEmits<{ view: [item: HistoryItem]; delete: [item: HistoryItem] }>()
</script>

<template>
  <div class="glass-card overflow-hidden">
    <div v-if="loading" class="p-6"><LoadingSkeleton :lines="5" /></div>
    <EmptyState v-else-if="!items.length" title="No history yet" description="Saved generations will appear here." icon="📂" />
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50/80 dark:bg-white/5">
          <tr>
            <th class="px-4 py-3 text-left font-semibold">Title</th>
            <th class="px-4 py-3 text-left font-semibold">Type</th>
            <th class="px-4 py-3 text-left font-semibold">Created</th>
            <th class="px-4 py-3 text-right font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.itemId"
            class="border-t border-gray-100 transition hover:bg-accent/5 dark:border-white/5"
          >
            <td class="px-4 py-3 font-medium">{{ item.title }}</td>
            <td class="px-4 py-3 text-muted-light dark:text-muted-dark">{{ item.itemType }}</td>
            <td class="px-4 py-3 text-muted-light dark:text-muted-dark">{{ item.createdAt?.slice(0, 10) }}</td>
            <td class="px-4 py-3 text-right">
              <button type="button" class="btn-secondary !py-1 !text-xs mr-2" @click="$emit('view', item)">View</button>
              <button type="button" class="text-xs text-red-500 hover:underline" @click="$emit('delete', item)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
