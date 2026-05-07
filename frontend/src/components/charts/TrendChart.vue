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
  xData: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  height: { type: [String, Number], default: '300px' },
  loading: { type: Boolean, default: false },
  smooth: { type: Boolean, default: true },
  showArea: { type: Boolean, default: false },
  showLegend: { type: Boolean, default: true }
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
  legend: props.showLegend
    ? { bottom: 0, textStyle: { fontSize: 12 } }
    : { show: false },
  grid: { left: 40, right: 20, top: 20, bottom: props.showLegend ? 40 : 20 },
  xAxis: {
    type: 'category',
    data: props.xData,
    boundaryGap: false,
    axisLabel: {
      fontSize: 11,
      rotate: props.xData.length > 10 ? 45 : 0
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: { fontSize: 11 },
    splitLine: { lineStyle: { color: '#ebeef5' } }
  },
  series: props.series.map(s => ({
    name: s.name,
    type: 'line',
    data: s.data,
    smooth: props.smooth,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: { color: s.color || '#409EFF', width: 2.5 },
    itemStyle: { color: s.color || '#409EFF' },
    areaStyle: props.showArea ? {
      color: {
        type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: (s.color || '#409EFF').replace(')', ',0.25)').replace('rgb', 'rgba') },
          { offset: 1, color: 'rgba(255,255,255,0.02)' }
        ]
      }
    } : undefined
  }))
}))
</script>
