<template>
  <div class="task-card" @click="$emit('click')">
    <div class="card-top">
      <PriorityTag :priority="task.priority" size="small" />
      <div class="card-meta">
        <span class="task-due" v-if="task.due_date">{{ task.due_date }}</span>
        <span class="task-hours" v-if="task.estimated_hours">{{ task.estimated_hours }}h</span>
      </div>
    </div>
    <p class="task-title">{{ task.title }}</p>
    <div class="card-bottom">
      <el-avatar :size="20" :src="task.assignee?.avatar">{{ task.assignee?.username?.[0] }}</el-avatar>
      <span class="assignee-name">{{ task.assignee?.username || '未分配' }}</span>
    </div>
  </div>
</template>

<script setup>
import PriorityTag from './PriorityTag.vue'
defineProps({ task: { type: Object, required: true } })
defineEmits(['click'])
</script>

<style scoped lang="scss">
.task-card {
  background: var(--el-bg-color);
  border-radius: 8px; padding: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08); cursor: pointer;
  transition: box-shadow 0.2s;
  &:hover { box-shadow: 0 3px 8px rgba(0,0,0,0.12); }
}
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.task-due { font-size: 11px; color: var(--el-text-color-secondary); }
.task-hours { font-size: 11px; color: var(--el-color-primary); font-weight: 500; }
.card-meta { display: flex; gap: 8px; align-items: center; }
.task-title { font-size: 14px; margin: 0 0 8px 0; color: var(--el-text-color-primary); }
.card-bottom { display: flex; align-items: center; gap: 6px; }
.assignee-name { font-size: 12px; color: var(--el-text-color-regular); }
</style>
