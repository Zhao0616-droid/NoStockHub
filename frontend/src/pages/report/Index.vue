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
            <StatCard :value="stats.totalTasks" label="任务总数" color="#409EFF" :icon="List" :trend="8" />
            <StatCard :value="stats.completedTasks" label="已完成" color="#67C23A" :icon="CircleCheck" :trend="12" />
            <StatCard :value="stats.totalHours" label="总工时" color="#E6A23C" suffix="h" :icon="Timer" :trend="-3" />
            <StatCard :value="stats.completionRate" label="完成率" color="#F56C6C" suffix="%" :icon="TrendCharts" :trend="5" :decimals="1" />
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
        <el-table-column prop="format" label="格式" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="formatTag(row.format)">{{ row.format.toUpperCase() }}</el-tag>
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
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Document, Grid, List, CircleCheck, Timer, TrendCharts, Coin, User } from '@element-plus/icons-vue'
import {
  StatCard, ProgressRing, BurndownChart,
  TaskDistribution, TrendChart
} from '@/components/charts'

const route = useRoute()
const projectId = route.params.id

// --------------- 日期范围 ---------------
const dateRange = ref([
  new Date(2026, 4, 1),
  new Date(2026, 4, 31)
])

const dateShortcuts = [
  { text: '本周', value: () => { const e = new Date(); const s = new Date(e); s.setDate(s.getDate() - s.getDay() + 1); return [s, e] } },
  { text: '本月', value: () => { const e = new Date(); return [new Date(e.getFullYear(), e.getMonth(), 1), e] } },
  { text: '上个月', value: () => { const e = new Date(); const s = new Date(e.getFullYear(), e.getMonth() - 1, 1); return [s, new Date(e.getFullYear(), e.getMonth(), 0)] } }
]

function applyDateRange() { /* filter data by date range */ }

// --------------- Tab ---------------
const activeTab = ref('overview')

function onTabChange() {
  nextTick(() => {
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50)
  })
}

// --------------- 概览统计 ---------------
const stats = reactive({
  totalTasks: 30,
  completedTasks: 18,
  totalHours: 256.5,
  completionRate: 60
})

const statusDistData = [
  { name: '待办', value: 8, color: '#909399' },
  { name: '进行中', value: 5, color: '#409EFF' },
  { name: '审核中', value: 3, color: '#E6A23C' },
  { name: '已完成', value: 12, color: '#67C23A' },
  { name: '阻塞', value: 2, color: '#F56C6C' }
]

const priorityDistData = [
  { name: '低', value: 6, color: '#909399' },
  { name: '中', value: 10, color: '#409EFF' },
  { name: '高', value: 8, color: '#E6A23C' },
  { name: '紧急', value: 4, color: '#F56C6C' }
]

// --------------- 任务统计 ---------------
const trendDates = ['5/1','5/2','5/3','5/4','5/5','5/6','5/7','5/8','5/9','5/10','5/11','5/12','5/13','5/14']

const completionTrendSeries = [
  { name: '完成任务', data: [1,2,3,1,4,2,5,3,2,6,4,3,5,4], color: '#67C23A' }
]

const createVsCompleteSeries = [
  { name: '新增任务', data: [3,4,5,2,6,3,7,4,5,3,6,4,8,5], color: '#F56C6C' },
  { name: '完成任务', data: [1,2,3,1,4,2,5,3,2,6,4,3,5,4], color: '#67C23A' }
]

const assigneeDistData = [
  { name: '张三', value: 12, color: '#409EFF' },
  { name: '李四', value: 8, color: '#67C23A' },
  { name: '王五', value: 6, color: '#E6A23C' },
  { name: '赵六', value: 4, color: '#909399' }
]

const typeDistData = [
  { name: '任务', value: 18, color: '#409EFF' },
  { name: '缺陷', value: 7, color: '#F56C6C' },
  { name: '史诗', value: 5, color: '#E6A23C' }
]

// --------------- 工时分析 ---------------
const worklogStats = reactive({
  totalHours: 256.5,
  avgHoursPerDay: 6.4,
  billableHours: 210,
  activeMembers: 4
})

const worklogDates = ['5/1','5/2','5/3','5/4','5/5','5/6','5/7','5/8','5/9','5/10','5/11','5/12','5/13','5/14']

const worklogTrendSeries = [
  { name: '计划工时', data: [8,8,8,8,8,0,0,8,8,8,8,8,8,8], color: '#909399' },
  { name: '实际工时', data: [7,8.5,6,9,7.5,0,0,8,6.5,7,8,9,7,6], color: '#409EFF' }
]

const memberWorklogData = [
  { name: '张三', value: 85, color: '#409EFF' },
  { name: '李四', value: 62, color: '#67C23A' },
  { name: '王五', value: 48, color: '#E6A23C' },
  { name: '赵六', value: 61.5, color: '#F56C6C' }
]

// --------------- 燃尽图 ---------------
const selectedSprint = ref('s1')
const sprintList = [
  { id: 's1', name: 'Sprint 1', dateRange: '5/1 - 5/14' },
  { id: 's2', name: 'Sprint 2', dateRange: '5/15 - 5/28' }
]

const currentSprint = computed(() => sprintList.find(s => s.id === selectedSprint.value))

const burndownDates = ['5/1','5/2','5/3','5/4','5/5','5/6','5/7','5/8','5/9','5/10','5/11','5/12','5/13','5/14']
const burndownIdeal = [20,18.5,17,15.5,14,12.5,11,9.5,8,6.5,5,3.5,2,0]
const burndownActual = [20,19,18,16,15,14,13,11,10,9,8,6,5,3]

// --------------- 报表历史 ---------------
const reports = ref([
  { id: 'r1', name: 'Sprint1 进度报告', type: 'progress', format: 'pdf', status: 'ready', file_path: '/reports/r1.pdf', created_at: '2026-05-07 14:30' },
  { id: 'r2', name: '5月工时统计表', type: 'worklog_summary', format: 'excel', status: 'ready', file_path: '/reports/r2.xlsx', created_at: '2026-05-01 09:00' },
  { id: 'r3', name: '任务完成趋势报告', type: 'task_list', format: 'csv', status: 'generating', file_path: '', created_at: '2026-05-15 10:15' }
])

// --------------- Methods ---------------
function handleExport(format) {
  ElMessage.success(`正在生成 ${format.toUpperCase()} 报表，请稍候...`)
  // 模拟：3 秒后将报表加入历史
  const typeMap = {
    overview: 'progress',
    tasks: 'task_list',
    worklog: 'worklog_summary',
    burndown: 'burndown'
  }
  setTimeout(() => {
    reports.value.unshift({
      id: `r${Date.now()}`,
      name: `${currentSprint.value?.name || '项目'}报表`,
      type: typeMap[activeTab.value] || 'progress',
      format,
      status: 'ready',
      file_path: `/reports/r${Date.now()}.${format}`,
      created_at: new Date().toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
    })
    ElMessage.success(`${format.toUpperCase()} 报表已生成`)
  }, 2000)
}

function downloadReport(row) {
  ElMessage.success(`开始下载: ${row.name}`)
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
