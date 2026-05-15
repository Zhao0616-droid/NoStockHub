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
          <el-select
            v-model="filters.assignee_id"
            placeholder="负责人"
            clearable
            style="width:100%;margin-bottom:8px"
            @change="applyFilters"
          >
            <el-option label="张三" value="u1" />
            <el-option label="李四" value="u2" />
            <el-option label="王五" value="u3" />
          </el-select>
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

const route = useRoute()
const projectId = route.params.id

// --------------- 视图模式 ---------------
const viewMode = ref('week')
const viewModes = [
  { label: '日', value: 'day' },
  { label: '周', value: 'week' },
  { label: '月', value: 'month' }
]

const viewModeDays = computed(() => ({ day: 1, week: 7, month: 31 }[viewMode.value]))

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

const dateRangeLabel = computed(() => {
  const days = viewModeDays.value
  const offset = dateOffset.value * days
  const start = new Date(2026, 4, 1)
  start.setDate(start.getDate() + offset)
  const end = new Date(start)
  end.setDate(end.getDate() + days - 1)
  const fmt = (d) => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} - ${fmt(end)}`
})

// --------------- 筛选 ---------------
const filters = reactive({
  assignee_id: '',
  showMilestones: true,
  showDependencies: true
})

function applyFilters() {
  nextTick(renderChart)
}

// --------------- Mock 数据 ---------------
const loading = ref(false)

const tasks = ref([
  { id: 't1', title: '设计ER图', type: 'task', status: 'done', priority: 'high', start_date: '2026-05-01', due_date: '2026-05-05', assignee: { id: 'u1', username: '张三' }, progress: 100, color: '#67C23A' },
  { id: 't2', title: '编写API文档', type: 'task', status: 'in_progress', priority: 'medium', start_date: '2026-05-04', due_date: '2026-05-10', assignee: { id: 'u2', username: '李四' }, progress: 60, color: '#409EFF' },
  { id: 't3', title: '用户认证模块', type: 'epic', status: 'in_progress', priority: 'urgent', start_date: '2026-05-03', due_date: '2026-05-14', assignee: { id: 'u1', username: '张三' }, progress: 45, color: '#E6A23C' },
  { id: 't4', title: '代码审查', type: 'task', status: 'todo', priority: 'low', start_date: '2026-05-09', due_date: '2026-05-13', assignee: { id: 'u3', username: '王五' }, progress: 0, color: '#909399' },
  { id: 't5', title: '部署测试', type: 'task', status: 'blocked', priority: 'high', start_date: '2026-05-12', due_date: '2026-05-20', assignee: { id: 'u1', username: '张三' }, progress: 10, color: '#F56C6C' },
  { id: 't6', title: '前端页面开发', type: 'task', status: 'in_progress', priority: 'high', start_date: '2026-05-07', due_date: '2026-05-18', assignee: { id: 'u2', username: '李四' }, progress: 30, color: '#409EFF' },
  { id: 't7', title: '编写单元测试', type: 'task', status: 'todo', priority: 'medium', start_date: '2026-05-15', due_date: '2026-05-25', assignee: { id: 'u3', username: '王五' }, progress: 0, color: '#909399' }
])

const milestones = ref([
  { id: 'm1', name: '需求评审', date: '2026-05-01' },
  { id: 'm2', name: '原型交付', date: '2026-05-15' },
  { id: 'm3', name: '测试完成', date: '2026-05-25' }
])

const dependencies = ref([
  { from: 't1', to: 't2' },
  { from: 't1', to: 't3' },
  { from: 't2', to: 't4' },
  { from: 't3', to: 't5' },
  { from: 't4', to: 't5' },
  { from: 't2', to: 't6' }
])

const filteredTasks = computed(() => {
  let list = tasks.value
  if (filters.assignee_id) {
    list = list.filter(t => t.assignee?.id === filters.assignee_id)
  }
  return list
})

// --------------- ECharts ---------------
const chartRef = ref(null)
let chartInstance = null

const BAR_HEIGHT = 24
const dayMs = 1000 * 60 * 60 * 24

function renderChart() {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const baseDate = new Date(2026, 4, 1)
  const viewDays = viewModeDays.value
  const viewStart = new Date(baseDate)
  viewStart.setDate(viewStart.getDate() + dateOffset.value * viewDays)
  const viewStartTime = +viewStart
  const viewEndTime = viewStartTime + viewDays * dayMs

  const items = filteredTasks.value
  const showMilestones = filters.showMilestones
  const showDeps = filters.showDependencies
  const todayTime = +new Date(2026, 4, 7)

  const yData = items.map(t => t.title)

  // 任务条数据
  const barData = items.map((t, i) => {
    const start = +new Date(t.start_date)
    const end = +new Date(t.due_date)
    const duration = Math.max((end - start) / dayMs, 1)
    return {
      name: t.title,
      value: [i, start, end, duration, t.progress],
      itemStyle: { color: t.color || '#409EFF' },
      task: t
    }
  })

  // 里程碑
  const milestoneData = showMilestones
    ? milestones.value.map(m => {
        const mt = +new Date(m.date)
        const row = Math.max(0, items.length ? items.length - 1 : 0)
        return {
          name: m.name,
          value: [row, mt],
          symbolSize: 14,
          itemStyle: { color: '#67C23A', borderColor: '#fff', borderWidth: 2 }
        }
      })
    : []

  // 依赖连线
  const depLines = []
  if (showDeps) {
    dependencies.value.forEach(dep => {
      const fromIdx = items.findIndex(t => t.id === dep.from)
      const toIdx = items.findIndex(t => t.id === dep.to)
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
            负责人: ${t.assignee?.username || '-'}<br/>
            进度: ${t.progress}%<br/>
            状态: ${statusLabel(t.status)}`
        }
        if (params.seriesType === 'scatter' && params.name) {
          return `◆ 里程碑: ${params.name}<br/>${params.value[1]}`
        }
        return ''
      }
    },
    grid: { left: 180, right: 30, top: 10, bottom: 30 },
    xAxis: {
      type: 'time',
      min: viewStartTime,
      max: viewEndTime,
      axisLabel: {
        formatter: (val) => {
          const d = new Date(val)
          return `${d.getMonth() + 1}/${d.getDate()}`
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
      // 任务条
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

          // 背景半透明条
          children.push({
            type: 'rect',
            shape: { x: barX, y: barY, width: barW, height: BAR_HEIGHT },
            style: { fill: color, opacity: 0.2 },
            z: 1
          })

          // 进度条
          if (progress > 0) {
            children.push({
              type: 'rect',
              shape: { x: barX, y: barY, width: barW * (progress / 100), height: BAR_HEIGHT },
              style: { fill: color, borderRadius: [radius, 0, 0, radius] },
              z: 2
            })
          }

          // 边框
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
      // 今天标记线
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
      // 里程碑
      {
        type: 'scatter',
        data: milestoneData,
        symbol: 'diamond',
        symbolSize: 12,
        z: 20,
        encode: { x: 1, y: 0 }
      },
      // 依赖连线
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

onMounted(() => {
  nextTick(renderChart)
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
    color: #303133;
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
  color: #606266;
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
  color: #606266;
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
