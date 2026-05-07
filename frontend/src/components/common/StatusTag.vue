<template>
  <el-tag :type="typeMap[status]" size="small">
    {{ labelMap[status] || status }}
  </el-tag>
</template>

<script setup>
defineProps({
  status: { type: String, default: 'todo' }
})

const typeMap = { todo: 'info', in_progress: undefined, review: 'warning', done: 'success', blocked: 'danger' }
const labelMap = { todo: '待办', in_progress: '进行中', review: '审核中', done: '已完成', blocked: '阻塞' }
</script>
