<template>
  <el-tag :type="typeMap[priority]" :size="size" :effect="effect">
    {{ labelMap[priority] }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  priority: { type: String, default: 'medium' },
  size: { type: String, default: 'small' },
  effect: { type: String, default: 'light' }
})

const typeMap = { low: 'info', medium: undefined, high: 'warning', urgent: 'danger' }
const labelMap = { low: '低', medium: '中', high: '高', urgent: '紧急' }
</script>
