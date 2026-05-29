<template>
  <div class="gantt-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>甘特图</h2>
      <div class="header-actions">
        <div class="date-nav">
          <el-button text :icon="ArrowLeft" @click="shiftDate(-1)" />
          <span class="date-label">{{ dateRangeLabel }}</span>
          <el-button text :icon="ArrowRight" @click="shiftDate(1)" />
        </div>
        <el-button-group>
          <el-button
            v-for="m in viewModes"
            :key="m.value"
            size="small"
            :type="viewMode === m.value ? 'primary' : ''"
            @click="setViewMode(m.value)"
          >{{ m.label }}</el-button>
        </el-button-group>
        <el-button size="small" @click="goToday">今天</el-button>
        <el-popover placement="bottom" :width="200" trigger="click">
          <template #reference>
            <el-button size="small" :icon="Filter">筛选</el-button>
          </template>
          <el-checkbox
            v-model="filters.showMilestones"
            style="width:100%;margin-bottom:4px"
            @change="applyFilters"
          >显示里程碑</el-checkbox>
          <el-checkbox
            v-model="filters.showDependencies"
            style="width:100%"
            @change="applyFilters"
          >显示依赖关系</el-checkbox>
        </el-popover>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && tasks.length === 0"
      description="当前项目暂无任务，请先创建任务"
    >
      <el-button
        type="primary"
        @click="$router.push(`/projects/${projectId}/tasks`)"
      >前往任务列表</el-button>
    </el-empty>

    <!-- 甘特图容器 -->
    <div
      v-else
      ref="chartRef"
      class="gantt-chart"
      v-loading="loading"
    />

    <!-- 图例 -->
    <div class="legend">
      <span class="legend-item">
        <span class="legend-bar task-bar"></span> 任务
      </span>
      <span class="legend-item">
        <span class="legend-bar milestone-diamond"></span> 里程碑
      </span>
      <span class="legend-item">
        <span class="legend-line"></span> 依赖连线
      </span>
      <span class="legend-item">
        <span class="legend-bar today-line"></span> 今天
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ArrowLeft, ArrowRight, Filter } from '@element-plus/icons-vue'
import { projectAPI } from '@/api'

const route = useRoute()
const projectId = route.params.id

// --------------- 视图模式 ---------------
const viewMode = ref('week')
const viewModes = [
  { label: '日', value: 'day' },
  { label: '周', value: 'week' },
  { label: '月', value: 'month' }
]

const viewModeDays = computed(() => ({ day: 14, week: 35, month: 90 }[viewMode.value]))

const dateOffset = ref(0)

function setViewMode(mode) {
  viewMode.value = mode
  dateOffset.value = 0
}

function shiftDate(dir) {
  dateOffset.value += dir
}

function goToday() {
  dateOffset.value = 0
}

function getStatusColor(status) {
  return { todo: '#909399', in_progress: '#409EFF', review: '#E6A23C', done: '#67C23A', blocked: '#F56C6C' }[status] || '#909399'
}

// --------------- 数据 ---------------
const loading = ref(false)
const tasks = ref([])
const milestones = ref([])
const dependencies = ref([])

const baseDate = ref(new Date())

const dateRangeLabel = computed(() => {
  const days = viewModeDays.value
  const offset = dateOffset.value * days
  const start = new Date(baseDate.value)
  start.setDate(start.getDate() + offset)
  const end = new Date(start)
  end.setDate(end.getDate() + days - 1)
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} - ${fmt(end)}`
})

// --------------- 筛选 ---------------
const filters = reactive({
  showMilestones: true,
  showDependencies: true
})

function applyFilters() {
  nextTick(renderChart)
}

// --------------- ECharts ---------------
const chartRef = ref(null)
let chartInstance = null

const BAR_HEIGHT = 24
const dayMs = 1000 * 60 * 60 * 24
const hourMs = 1000 * 60 * 60

function renderChart() {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const viewDays = viewModeDays.value
  const viewStart = new Date(baseDate.value)
  viewStart.setDate(viewStart.getDate() + dateOffset.value * viewDays)
  const viewStartTime = +viewStart
  const viewEndTime = viewStartTime + viewDays * dayMs

  const items = tasks.value
  const showMilestones = filters.showMilestones
  const showDeps = filters.showDependencies
  const todayTime = +new Date()

  const yData = items.map(t => t.title)

  const barData = items.map((t, i) => {
    const start = +new Date(t.start_date)
    const end = +new Date(t.due_date)
    const duration = Math.max((end - start) / dayMs, 1)
    return {
      name: t.title,
      value: [i, start, end, duration, t.progress],
      itemStyle: { color: t.color || getStatusColor(t.status) },
      task: t
    }
  })

  const milestoneData = showMilestones
    ? milestones.value.map(m => {
        const mt = +new Date(m.due_date || m.date)
        const row = Math.max(0, items.length ? items.length - 1 : 0)
        return {
          name: m.name,
          value: [row, mt],
          symbolSize: 14,
          itemStyle: { color: '#67C23A', borderColor: '#fff', borderWidth: 2 }
        }
      })
    : []

  const depLines = []
  if (showDeps) {
    dependencies.value.forEach(dep => {
      const fromId = dep.predecessor_id || dep.from
      const toId = dep.successor_id || dep.to
      const fromIdx = items.findIndex(t => t.id === fromId)
      const toIdx = items.findIndex(t => t.id === toId)
      if (fromIdx === -1 || toIdx === -1) return
      const fromTask = items[fromIdx]
      const toTask = items[toIdx]
      depLines.push({
        coords: [
          [+new Date(fromTask.due_date), fromIdx],
          [+new Date(toTask.start_date), toIdx]
        ]
      })
    })
  }

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.seriesType === 'custom' && params.data?.task) {
          const t = params.data.task
          return `<strong>${t.title}</strong><br/>
            ${t.start_date} → ${t.due_date}<br/>
            进度: ${t.progress}%<br/>
            状态: ${statusLabel(t.status)}`
        }
        if (params.seriesType === 'scatter' && params.name) {
          return `◆ 里程碑: ${params.name}`
        }
        return ''
      }
    },
    grid: { left: 180, right: 30, top: 10, bottom: 30 },
    xAxis: {
      type: 'time',
      min: viewStartTime,
      max: viewEndTime,
      minInterval: hourMs,
      maxInterval: viewMode.value === 'day' ? dayMs : viewMode.value === 'week' ? dayMs * 2 : dayMs * 7,
      axisLabel: {
        formatter: (val) => {
          const d = new Date(val)
          const M = d.getMonth() + 1
          const D = d.getDate()
          if (viewMode.value === 'day') return `${M}/${D}`
          if (viewMode.value === 'week') return `${M}/${D} 周${'日一二三四五六'[d.getDay()]}`
          return `${M}/${D}`
        }
      },
      splitLine: { show: true, lineStyle: { color: '#ebeef5', type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: yData,
      inverse: true,
      axisLabel: { width: 160, overflow: 'truncate', fontSize: 12 },
      axisTick: { show: false },
      axisLine: { show: false }
    },
    series: [
      {
        type: 'custom',
        renderItem: (params, api) => {
          const y = api.coord([0, api.value(0)])
          const x1 = api.coord([api.value(1), 0])
          const x2 = api.coord([api.value(2), 0])
          const progress = api.value(4) || 0

          const barY = y[1] - BAR_HEIGHT / 2
          const barX = x1[0]
          const barW = Math.max(x2[0] - x1[0], 4)
          const radius = 4
          const color = api.visual('color')

          const children = []

          children.push({
            type: 'rect',
            shape: { x: barX, y: barY, width: barW, height: BAR_HEIGHT },
            style: { fill: color, opacity: 0.2 },
            z: 1
          })

          if (progress > 0) {
            children.push({
              type: 'rect',
              shape: { x: barX, y: barY, width: barW * (progress / 100), height: BAR_HEIGHT },
              style: { fill: color, borderRadius: [radius, 0, 0, radius] },
              z: 2
            })
          }

          children.push({
            type: 'rect',
            shape: { x: barX, y: barY, width: barW, height: BAR_HEIGHT },
            style: { fill: 'transparent', stroke: color, lineWidth: 1.5, borderRadius: radius },
            z: 3
          })

          return { type: 'group', children }
        },
        data: barData,
        encode: { x: [1, 2], y: 0 },
        z: 10
      },
      {
        type: 'line',
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#F56C6C', type: 'solid', width: 1.5 },
          data: [{ xAxis: todayTime }],
          label: { show: true, formatter: '今天', fontSize: 11, color: '#F56C6C' }
        }
      },
      {
        type: 'scatter',
        data: milestoneData,
        symbol: 'diamond',
        symbolSize: 12,
        z: 20,
        encode: { x: 1, y: 0 }
      },
      {
        type: 'lines',
        coordinateSystem: 'cartesian2d',
        polyline: false,
        data: depLines,
        lineStyle: { color: '#909399', width: 1, type: 'dashed', curveness: 0.3 },
        effect: { show: false },
        z: 5
      }
    ],
    dataZoom: [
      {
        type: 'slider',
        xAxisIndex: 0,
        bottom: 0,
        height: 22,
        start: 0,
        end: 100,
        borderColor: '#dcdfe6',
        fillerColor: 'rgba(64,158,255,0.1)',
        handleStyle: { color: '#409EFF' }
      }
    ]
  }

  chartInstance.setOption(option, true)
}

function statusLabel(s) {
  return { todo: '待办', in_progress: '进行中', review: '审核中', done: '已完成', blocked: '阻塞' }[s] || s
}

// --------------- 响应式 ---------------
function handleResize() { chartInstance?.resize() }

async function loadGanttData() {
  loading.value = true
  try {
    const res = await projectAPI.gantt(projectId)
    tasks.value = (res.tasks || []).map(t => ({
      ...t,
      color: getStatusColor(t.status),
    }))
    milestones.value = res.milestones || []
    dependencies.value = (res.dependencies || []).map(d => ({
      from: d.predecessor_id,
      to: d.successor_id,
    }))

    // Base view on earliest task date
    const dates = tasks.value.flatMap(t => [t.start_date, t.due_date].filter(Boolean))
    if (dates.length) {
      baseDate.value = new Date(Math.min(...dates.map(d => +new Date(d))))
    }
  } catch {
    // silently fail, empty state shows
  } finally {
    loading.value = false
    nextTick(renderChart)
  }
}

onMounted(() => {
  loadGanttData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

watch([viewMode, dateOffset], () => { nextTick(renderChart) })
</script>

<style scoped lang="scss">
.gantt-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 8px;

  h2 {
    margin: 0;
    font-size: 20px;
    color: var(--el-text-color-primary);
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.date-nav {
  display: flex;
  align-items: center;
  gap: 2px;
}

.date-label {
  display: inline-block;
  min-width: 100px;
  text-align: center;
  font-size: 13px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}

// ---------- 图表 ----------
.gantt-chart {
  flex: 1;
  min-height: 400px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

// ---------- 图例 ----------
.legend {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 12px;
  padding: 8px 0;
  font-size: 13px;
  color: var(--el-text-color-regular);
  flex-shrink: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-bar {
  display: inline-block;
  width: 18px;
  height: 10px;
  border-radius: 2px;

  &.task-bar {
    background: #409EFF;
    opacity: 0.3;
    border: 1.5px solid #409EFF;
  }

  &.milestone-diamond {
    width: 10px;
    height: 10px;
    background: #67C23A;
    transform: rotate(45deg);
    border-radius: 1px;
  }

  &.today-line {
    width: 18px;
    height: 0;
    border-top: 2px solid #F56C6C;
  }
}

.legend-line {
  display: inline-block;
  width: 18px;
  height: 0;
  border-top: 1px dashed #909399;
}
</style>
