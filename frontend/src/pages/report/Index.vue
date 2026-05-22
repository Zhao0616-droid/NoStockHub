<template>
  <div class="report-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>项目报表</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :shortcuts="dateShortcuts"
          size="default"
          style="width:280px"
          @change="applyDateRange"
        />
        <el-dropdown @command="handleExport">
          <el-button type="primary">
            导出报表 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="pdf">
                <el-icon><Document /></el-icon> PDF
              </el-dropdown-item>
              <el-dropdown-item command="excel">
                <el-icon><Grid /></el-icon> Excel
              </el-dropdown-item>
              <el-dropdown-item command="csv">
                <el-icon><List /></el-icon> CSV
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 报表 Tab -->
    <el-tabs v-model="activeTab" type="border-card" class="report-tabs" @tab-change="onTabChange">
      <!-- ====== Tab 1: 概览 ====== -->
      <el-tab-pane label="概览" name="overview">
        <div class="tab-content">
          <!-- 统计卡片行 -->
          <div class="stat-row">
            <StatCard :value="stats.totalTasks" label="任务总数" color="#409EFF" :icon="List" />
            <StatCard :value="stats.completedTasks" label="已完成" color="#67C23A" :icon="CircleCheck" />
            <StatCard :value="stats.totalHours" label="总工时" color="#E6A23C" suffix="h" :icon="Timer" />
            <StatCard :value="stats.completionRate" label="完成率" color="#F56C6C" suffix="%" :icon="TrendCharts" :decimals="1" />
          </div>

          <!-- 进度环形图 + 任务分布 -->
          <div class="chart-row">
            <div class="chart-card">
              <h4>项目进度</h4>
              <ProgressRing :percent="stats.completionRate" color="#67C23A" label="完成率" :sublabel="`${stats.completedTasks}/${stats.totalTasks} 任务`" />
            </div>
            <div class="chart-card chart-wide">
              <h4>任务状态分布</h4>
              <TaskDistribution :data="statusDistData" type="pie" height="260px" />
            </div>
            <div class="chart-card chart-wide">
              <h4>任务优先级分布</h4>
              <TaskDistribution :data="priorityDistData" type="pie" height="260px" />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ====== Tab 2: 任务统计 ====== -->
      <el-tab-pane label="任务统计" name="tasks">
        <div class="tab-content">
          <div class="chart-row">
            <div class="chart-card chart-wide">
              <h4>每日完成任务趋势</h4>
              <TrendChart
                :x-data="trendDates"
                :series="completionTrendSeries"
                :show-area="true"
                height="300px"
              />
            </div>
            <div class="chart-card chart-wide">
              <h4>新增 vs 完成任务</h4>
              <TrendChart
                :x-data="trendDates"
                :series="createVsCompleteSeries"
                height="300px"
              />
            </div>
          </div>
          <div class="chart-row">
            <div class="chart-card">
              <h4>按负责人统计</h4>
              <TaskDistribution :data="assigneeDistData" type="bar" height="260px" />
            </div>
            <div class="chart-card">
              <h4>按类型统计</h4>
              <TaskDistribution :data="typeDistData" type="bar" height="260px" />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ====== Tab 3: 工时分析 ====== -->
      <el-tab-pane label="工时分析" name="worklog">
        <div class="tab-content">
          <div class="stat-row">
            <StatCard :value="worklogStats.totalHours" label="总工时" color="#409EFF" suffix="h" :icon="Timer" />
            <StatCard :value="worklogStats.avgHoursPerDay" label="日均工时" color="#67C23A" suffix="h" :decimals="1" :icon="TrendCharts" />
            <StatCard :value="worklogStats.billableHours" label="可计费工时" color="#E6A23C" suffix="h" :icon="Coin" />
            <StatCard :value="worklogStats.activeMembers" label="活跃成员" color="#909399" :icon="User" />
          </div>
          <div class="chart-row">
            <div class="chart-card chart-wide">
              <h4>每日工时趋势</h4>
              <TrendChart
                :x-data="worklogDates"
                :series="worklogTrendSeries"
                :show-area="true"
                height="280px"
              />
            </div>
            <div class="chart-card chart-wide">
              <h4>成员工时分布</h4>
              <TaskDistribution :data="memberWorklogData" type="bar" height="280px" />
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- ====== Tab 4: 燃尽图 ====== -->
      <el-tab-pane label="燃尽图" name="burndown">
        <div class="tab-content">
          <el-select
            v-model="selectedSprint"
            placeholder="选择冲刺"
            style="width:200px;margin-bottom:16px"
          >
            <el-option
              v-for="s in sprintList"
              :key="s.id"
              :label="`Sprint ${s.name} (${s.dateRange})`"
              :value="s.id"
            />
          </el-select>
          <div class="chart-row">
            <div class="chart-card" style="width:100%">
              <h4>燃尽图 — {{ currentSprint?.name || '' }}</h4>
              <BurndownChart
                :dates="burndownDates"
                :ideal="burndownIdeal"
                :actual="burndownActual"
                height="380px"
              />
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 报表历史 -->
    <el-card class="history-card">
      <template #header>
        <span>报表历史</span>
      </template>
      <el-table :data="reports" stripe>
        <el-table-column prop="name" label="报表名称" min-width="200" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">{{ typeLabel(row.type) }}</template>
        </el-table-column>
        <el-table-column label="格式" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="formatTag(row.parameters?.format)">{{ (row.parameters?.format || 'csv').toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="170" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'ready'"
              text
              size="small"
              type="primary"
              @click="downloadReport(row)"
            >
              下载
            </el-button>
            <el-tag v-else-if="row.status === 'generating'" size="small" type="warning">生成中</el-tag>
            <el-button text size="small" type="danger" @click="deleteReport(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!reports.length" description="暂无报表历史" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Document, Grid, List, CircleCheck, Timer, TrendCharts, Coin, User } from '@element-plus/icons-vue'
import {
  StatCard, ProgressRing, BurndownChart,
  TaskDistribution, TrendChart
} from '@/components/charts'
import { reportAPI, taskAPI, worklogAPI, sprintAPI } from '@/api'

const route = useRoute()
const projectId = route.params.id

// --------------- 日期范围 ---------------
const dateRange = ref([
  new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  new Date()
])

const dateShortcuts = [
  { text: '本周', value: () => { const e = new Date(); const s = new Date(e); s.setDate(s.getDate() - s.getDay() + 1); return [s, e] } },
  { text: '本月', value: () => { const e = new Date(); return [new Date(e.getFullYear(), e.getMonth(), 1), e] } },
  { text: '上个月', value: () => { const e = new Date(); const s = new Date(e.getFullYear(), e.getMonth() - 1, 1); return [s, new Date(e.getFullYear(), e.getMonth(), 0)] } }
]

// --------------- Tab ---------------
const activeTab = ref('overview')

function applyDateRange() {
  // 日期范围变更时重新加载数据
  loadAllData()
}

function onTabChange() {
  nextTick(() => {
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50)
  })
}

// --------------- Data loading ---------------
const loading = ref(false)
const allTasks = ref([])
const allWorklogs = ref([])
const sprintList = ref([])

function formatDateStr(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const statusColors = { todo: '#909399', in_progress: '#409EFF', review: '#E6A23C', done: '#67C23A', blocked: '#F56C6C' }
const statusLabels = { todo: '待办', in_progress: '进行中', review: '审核中', done: '已完成', blocked: '阻塞' }
const priorityColors = { low: '#909399', medium: '#409EFF', high: '#E6A23C', urgent: '#F56C6C' }
const priorityLabels = { low: '低', medium: '中', high: '高', urgent: '紧急' }

// --------------- 概览统计 (computed from real data) ---------------
const stats = computed(() => {
  const total = allTasks.value.length
  const completed = allTasks.value.filter(t => t.status === 'done').length
  const hours = allWorklogs.value.reduce((sum, w) => sum + (Number(w.hours) || 0), 0)
  const rate = total > 0 ? Math.round((completed / total) * 1000) / 10 : 0
  return { totalTasks: total, completedTasks: completed, totalHours: hours, completionRate: rate }
})

const statusDistData = computed(() => {
  const map = {}
  allTasks.value.forEach(t => {
    const key = t.status || 'todo'
    map[key] = (map[key] || 0) + 1
  })
  return Object.entries(map).map(([k, v]) => ({ name: statusLabels[k] || k, value: v, color: statusColors[k] || '#909399' }))
})

const priorityDistData = computed(() => {
  const map = {}
  allTasks.value.forEach(t => {
    const key = t.priority || 'medium'
    map[key] = (map[key] || 0) + 1
  })
  return Object.entries(map).map(([k, v]) => ({ name: priorityLabels[k] || k, value: v, color: priorityColors[k] || '#409EFF' }))
})

// --------------- 任务统计 ---------------
const trendDates = computed(() => {
  const dates = new Set()
  allTasks.value.forEach(t => {
    if (t.due_date) dates.add(t.due_date)
    if (t.created_at) dates.add(t.created_at.slice(0, 10))
  })
  return [...dates].sort().map(d => formatDateStr(d))
})

const completionTrendSeries = computed(() => {
  const byDate = {}
  allTasks.value.filter(t => t.status === 'done' && t.due_date).forEach(t => {
    byDate[t.due_date] = (byDate[t.due_date] || 0) + 1
  })
  const dates = [...new Set(allTasks.value.filter(t => t.due_date).map(t => t.due_date))].sort()
  let acc = 0
  return [{ name: '完成任务(累计)', data: dates.map(d => { acc += (byDate[d] || 0); return acc }), color: '#67C23A' }]
})

const createVsCompleteSeries = computed(() => {
  const created = {}, completed = {}
  allTasks.value.forEach(t => {
    const cd = t.created_at ? t.created_at.slice(0, 10) : null
    if (cd) created[cd] = (created[cd] || 0) + 1
    if (t.status === 'done' && t.due_date) completed[t.due_date] = (completed[t.due_date] || 0) + 1
  })
  const dates = [...new Set([...Object.keys(created), ...Object.keys(completed)])].sort()
  return [
    { name: '新增任务', data: dates.map(d => created[d] || 0), color: '#F56C6C' },
    { name: '完成任务', data: dates.map(d => completed[d] || 0), color: '#67C23A' }
  ]
})

const assigneeDistData = computed(() => {
  const map = {}
  allTasks.value.forEach(t => {
    const name = t.assignee_detail?.username || t.assignee?.username || '未分配'
    map[name] = (map[name] || 0) + 1
  })
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  return Object.entries(map).map(([name, value], i) => ({ name, value, color: colors[i % colors.length] }))
})

const typeDistData = computed(() => {
  const map = {}
  allTasks.value.forEach(t => {
    const key = t.type || 'task'
    const label = { task: '任务', bug: '缺陷', epic: '史诗' }[key] || key
    map[label] = (map[label] || 0) + 1
  })
  return Object.entries(map).map(([name, value], i) => ({
    name, value,
    color: ['#409EFF', '#F56C6C', '#E6A23C'][i] || '#909399'
  }))
})

// --------------- 工时分析 ---------------
const worklogStats = computed(() => {
  const totalHours = allWorklogs.value.reduce((s, w) => s + (Number(w.hours) || 0), 0)
  const uniqueDays = new Set(allWorklogs.value.map(w => w.date || w.created_at?.slice(0, 10))).size
  const billableHours = allWorklogs.value.filter(w => w.is_billable !== false).reduce((s, w) => s + (Number(w.hours) || 0), 0)
  const activeMembers = new Set(allWorklogs.value.map(w => w.user_id || w.user)).size
  return {
    totalHours,
    avgHoursPerDay: uniqueDays > 0 ? Math.round((totalHours / uniqueDays) * 10) / 10 : 0,
    billableHours,
    activeMembers
  }
})

const worklogDates = computed(() => {
  return [...new Set(allWorklogs.value.map(w => (w.date || w.created_at?.slice(0, 10) || '')))]
    .filter(Boolean).sort().map(d => formatDateStr(d))
})

const worklogTrendSeries = computed(() => {
  const byDate = {}
  allWorklogs.value.forEach(w => {
    const d = w.date || w.created_at?.slice(0, 10)
    if (d) byDate[d] = (byDate[d] || 0) + (Number(w.hours) || 0)
  })
  const dates = [...new Set(allWorklogs.value.map(w => w.date || w.created_at?.slice(0, 10)))].filter(Boolean).sort()
  return [{ name: '实际工时', data: dates.map(d => byDate[d] || 0), color: '#409EFF' }]
})

const memberWorklogData = computed(() => {
  const map = {}
  allWorklogs.value.forEach(w => {
    const name = w.user_detail?.username || w.user?.username || '未知'
    map[name] = (map[name] || 0) + (Number(w.hours) || 0)
  })
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  return Object.entries(map).map(([name, value], i) => ({ name, value, color: colors[i % colors.length] }))
})

// --------------- 燃尽图 ---------------
const selectedSprint = ref('')
const currentSprint = computed(() => sprintList.value.find(s => s.id === selectedSprint.value))

const burndownDates = ref([])
const burndownIdeal = ref([])
const burndownActual = ref([])

async function loadBurndown(sprintId) {
  if (!sprintId) return
  try {
    const data = await sprintAPI.burndown(sprintId)
    burndownDates.value = data.dates || []
    burndownIdeal.value = data.ideal_line || []
    burndownActual.value = data.actual_line || []
  } catch {
    burndownDates.value = []
    burndownIdeal.value = []
    burndownActual.value = []
  }
}

watch(selectedSprint, (id) => { if (id) loadBurndown(id) })

// --------------- 报表历史 ---------------
const reports = ref([])

async function loadReports() {
  try {
    const res = await reportAPI.list({ project_id: projectId })
    reports.value = res.results || res || []
  } catch { /* keep empty */ }
}

// --------------- Methods ---------------
async function handleExport(format) {
  try {
    const typeMap = {
      overview: 'progress',
      tasks: 'task_list',
      worklog: 'worklog_summary',
      burndown: 'burndown'
    }
    const name = `${currentSprint.value?.name || '项目'}报表`
    await reportAPI.generate({
      type: typeMap[activeTab.value] || 'progress',
      project_id: projectId,
      name,
      parameters: {
        date_from: dateRange.value[0]?.toISOString?.()?.slice(0, 10),
        date_to: dateRange.value[1]?.toISOString?.()?.slice(0, 10),
        format
      }
    })
    ElMessage.success(`${format.toUpperCase()} 报表生成请求已提交`)
    await loadReports()
  } catch (e) {
    ElMessage.error('生成报表失败')
  }
}

async function downloadReport(row) {
  try {
    const blob = await reportAPI.download(row.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.name || 'report'}.csv`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch {
    ElMessage.error('下载失败，报表可能尚未生成')
  }
}

async function deleteReport(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.name}」？`, '确认删除', { type: 'warning' })
    reports.value = reports.value.filter(r => r.id !== row.id)
    ElMessage.success('已删除')
  } catch { /* cancelled */ }
}

function typeLabel(type) {
  return {
    task_list: '任务列表', worklog_summary: '工时统计',
    gantt: '甘特图', progress: '项目进度', burndown: '燃尽图'
  }[type] || type
}

function formatTag(format) {
  return { pdf: 'danger', excel: 'success', csv: '' }[format] || 'info'
}

// --------------- Init ---------------
async function loadAllData() {
  loading.value = true
  try {
    const [tasksRes, worklogsRes, sprintsRes] = await Promise.all([
      taskAPI.list({ project_id: projectId }).catch(() => ({ results: [] })),
      worklogAPI.list({ project_id: projectId }).catch(() => ({ results: [] })),
      sprintAPI.list({ project_id: projectId }).catch(() => ({ results: [] })),
    ])
    allTasks.value = tasksRes.results || tasksRes || []
    allWorklogs.value = worklogsRes.results || worklogsRes || []
    sprintList.value = (sprintsRes.results || sprintsRes || []).map(s => ({
      ...s,
      dateRange: `${formatDateStr(s.start_date)} - ${formatDateStr(s.end_date)}`
    }))
    if (sprintList.value.length) {
      selectedSprint.value = sprintList.value[0].id
      loadBurndown(selectedSprint.value)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAllData()
  loadReports()
})
</script>

<style scoped lang="scss">
.report-page {
  padding-bottom: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

// ---------- Tabs ----------
.report-tabs {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  min-height: 500px;

  :deep(.el-tabs__content) {
    overflow: visible;
  }
}

.tab-content {
  padding: 8px 0;
}

// ---------- Stat Row ----------
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;

  @media (max-width: 1100px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

// ---------- Chart Row ----------
.chart-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;

  @media (max-width: 1100px) {
    flex-direction: column;
  }
}

.chart-card {
  flex: 1;
  min-width: 0;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;

  &.chart-wide {
    flex: 1;
    min-width: 0;
  }

  h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #606266;
    font-weight: 600;
  }
}

// ---------- History ----------
.history-card {
  flex-shrink: 0;
  border-radius: 8px;
}
</style>
