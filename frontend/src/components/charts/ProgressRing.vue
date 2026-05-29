<template>
  <BaseChart
    ref="chart"
    :option="chartOption"
    :height="size"
    :loading="loading"
    @chart-click="$emit('click', $event)"
  />
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  percent: { type: Number, default: 0 },
  color: { type: String, default: '#409EFF' },
  size: { type: [String, Number], default: '180px' },
  label: { type: String, default: '' },
  sublabel: { type: String, default: '' },
  lineWidth: { type: Number, default: 12 },
  loading: { type: Boolean, default: false }
})

defineEmits(['click'])

const theme = useThemeStore()

function cssVar(name, fallback) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

const chartOption = computed(() => {
  // 依赖 theme.isDark，切换主题时自动重算
  void theme.isDark
  return {
    series: [
      {
        type: 'pie',
        radius: ['65%', '85%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        silent: true,
        label: { show: false },
        emphasis: { disabled: true },
        data: [
          { value: Math.min(Math.max(props.percent, 0), 100), itemStyle: { color: props.color, borderRadius: 4 } },
          { value: 100 - Math.min(Math.max(props.percent, 0), 100), itemStyle: { color: cssVar('--el-fill-color', '#ebeef5') } }
        ]
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '38%',
        style: {
          text: `${Math.round(props.percent)}%`,
          textAlign: 'center',
          fill: cssVar('--el-text-color-primary', '#303133'),
          fontSize: 22,
          fontWeight: 'bold'
        }
      },
      ...(props.label ? [{
        type: 'text',
        left: 'center',
        top: '58%',
        style: {
          text: props.label,
          textAlign: 'center',
          fill: cssVar('--el-text-color-secondary', '#909399'),
          fontSize: 12
        }
      }] : []),
      ...(props.sublabel ? [{
        type: 'text',
        left: 'center',
        top: '70%',
        style: {
          text: props.sublabel,
          textAlign: 'center',
          fill: cssVar('--el-text-color-placeholder', '#c0c4cc'),
          fontSize: 11
        }
      }] : [])
    ]
  }
})
</script>
