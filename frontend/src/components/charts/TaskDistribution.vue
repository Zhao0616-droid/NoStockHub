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
  data: { type: Array, default: () => [] },
  type: { type: String, default: 'pie' },
  groupBy: { type: String, default: 'status' },
  height: { type: [String, Number], default: '300px' },
  loading: { type: Boolean, default: false },
  showLegend: { type: Boolean, default: true }
})

defineEmits(['click'])

const chartOption = computed(() => {
  const items = props.data.map(d => ({
    name: d.name,
    value: d.value,
    itemStyle: { color: d.color, borderRadius: 4 }
  }))

  const baseOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: props.showLegend
      ? { bottom: 0, textStyle: { fontSize: 12 }, itemWidth: 10, itemHeight: 10 }
      : { show: false }
  }

  if (props.type === 'pie') {
    return {
      ...baseOption,
      series: [{
        type: 'pie',
        radius: ['50%', '75%'],
        center: ['50%', '45%'],
        data: items,
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' },
          scaleSize: 8
        }
      }]
    }
  }

  // Bar chart
  return {
    ...baseOption,
    grid: { left: 40, right: 20, top: 10, bottom: 40 },
    xAxis: {
      type: 'category',
      data: items.map(d => d.name),
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: items,
      barWidth: '50%',
      emphasis: {
        itemStyle: { borderRadius: 4 }
      }
    }]
  }
})
</script>
