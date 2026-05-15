<template>
  <BaseChart
    ref="chart"
    :option="chartOption"
    :height="height"
    :loading="loading"
    @chart-click="$emit('click', $event)"
  />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  dates: { type: Array, default: () => [] },
  ideal: { type: Array, default: () => [] },
  actual: { type: Array, default: () => [] },
  height: { type: [String, Number], default: '340px' },
  loading: { type: Boolean, default: false }
})

defineEmits(['click'])

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: (params) => {
      let html = `<strong>${params[0]?.axisValue || ''}</strong><br/>`
      params.forEach(p => {
        html += `${p.marker} ${p.seriesName}: ${p.value}<br/>`
      })
      return html
    }
  },
  legend: {
    data: ['理想剩余', '实际剩余'],
    bottom: 0
  },
  grid: { left: 75, right: 20, top: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: props.dates,
    boundaryGap: false,
    axisLabel: { fontSize: 11, rotate: props.dates.length > 10 ? 45 : 0 }
  },
  yAxis: {
    type: 'value',
    name: '剩余任务',
    nameLocation: 'middle',
    nameGap: 45,
    nameTextStyle: { fontSize: 12 },
    axisLabel: { fontSize: 11 }
  },
  series: [
    {
      name: '理想剩余',
      type: 'line',
      data: props.ideal,
      smooth: false,
      lineStyle: { color: '#909399', type: 'dashed', width: 2 },
      itemStyle: { color: '#909399' },
      symbol: 'none'
    },
    {
      name: '实际剩余',
      type: 'line',
      data: props.actual,
      smooth: true,
      lineStyle: { color: '#409EFF', width: 2.5 },
      itemStyle: { color: '#409EFF' },
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64,158,255,0.25)' },
            { offset: 1, color: 'rgba(64,158,255,0.02)' }
          ]
        }
      }
    }
  ]
}))
</script>
