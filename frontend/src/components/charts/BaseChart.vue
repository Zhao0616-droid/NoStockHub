<template>
  <div ref="chartRef" class="base-chart" v-loading="loading" :style="chartStyle" />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: [String, Number], default: '300px' },
  loading: { type: Boolean, default: false },
  theme: { type: String, default: '' }
})

const emit = defineEmits(['chart-ready', 'chart-click'])

const chartRef = ref(null)
let chartInstance = null

const chartStyle = computed(() => ({
  width: '100%',
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value, props.theme)
  chartInstance.setOption(props.option, true)

  chartInstance.on('click', (params) => {
    emit('chart-click', params)
  })

  emit('chart-ready', chartInstance)
}

function resize() {
  chartInstance?.resize()
}

function setOption(option, notMerge = false) {
  chartInstance?.setOption(option, notMerge)
}

onMounted(() => {
  nextTick(initChart)
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
  chartInstance = null
})

watch(() => props.option, (newOpt) => {
  if (chartInstance) {
    chartInstance.setOption(newOpt, true)
  }
}, { deep: true })

defineExpose({ chartInstance, setOption, resize })
</script>

<style scoped lang="scss">
.base-chart {
  width: 100%;
  border-radius: 8px;
}
</style>
