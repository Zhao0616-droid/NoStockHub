<template>
  <div class="gantt-page">
    <div class="page-header">
      <h2>甘特图</h2>
      <div>
        <el-button-group>
          <el-button :type="viewMode === 'day' ? 'primary' : ''" @click="viewMode = 'day'">日</el-button>
          <el-button :type="viewMode === 'week' ? 'primary' : ''" @click="viewMode = 'week'">周</el-button>
          <el-button :type="viewMode === 'month' ? 'primary' : ''" @click="viewMode = 'month'">月</el-button>
        </el-button-group>
        <el-button style="margin-left:8px" @click="goToday">今天</el-button>
      </div>
    </div>

    <div v-if="!tasks.length" class="empty-state">
      <el-empty description="当前项目暂无任务，请先创建任务" />
      <el-button type="primary" @click="$router.push(`/projects/${projectId}/tasks`)">前往任务列表</el-button>
    </div>

    <div v-else class="gantt-container" ref="ganttRef">
      <!-- Gantt chart rendered by ECharts / v-gantt-chart -->
      <div class="gantt-placeholder">
        <p>甘特图区域 — 使用 ECharts 或 v-gantt-chart 渲染</p>
        <table class="gantt-table">
          <thead>
            <tr><th style="width:200px">任务</th><th v-for="d in days" :key="d">{{ d }}</th></tr>
          </thead>
          <tbody>
            <tr v-for="t in tasks" :key="t.id">
              <td>{{ t.title }}</td>
              <td v-for="d in days" :key="d" :class="{ bar: isBar(t, d) }"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 图例 -->
    <div class="legend">
      <span><span class="legend-color" style="background:#409EFF"></span> 任务</span>
      <span><span class="legend-color" style="background:#67C23A;border-radius:50%"></span> 里程碑</span>
      <span>── 依赖连线</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = route.params.id
const viewMode = ref('week')
const ganttRef = ref(null)

const tasks = ref([
  { id: 't1', title: '设计ER图', start_date: '2026-05-01', due_date: '2026-05-05', type: 'task' },
  { id: 't2', title: '编写API', start_date: '2026-05-04', due_date: '2026-05-10', type: 'task' },
  { id: 't3', title: '代码审查', start_date: '2026-05-09', due_date: '2026-05-13', type: 'task' },
  { id: 't4', title: '部署测试', start_date: '2026-05-12', due_date: '2026-05-20', type: 'task' }
])

const milestones = ref([
  { name: '需求评审', date: '2026-05-01' }
])

const days = computed(() => {
  const d = []
  for (let i = 1; i <= 31; i++) d.push(`5/${i}`)
  return d
})

function isBar(task, day) {
  const d = parseInt(day.split('/')[1])
  const start = parseInt(task.start_date.split('-')[2])
  const end = parseInt(task.due_date.split('-')[2])
  return d >= start && d <= end
}

function goToday() { /* scroll to today */ }
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.empty-state { text-align: center; padding: 80px 0; }
.gantt-placeholder { overflow-x: auto; }
.gantt-table { border-collapse: collapse; width: 100%; font-size: 12px;
  th, td { border: 1px solid #e4e7ed; padding: 4px; min-width: 24px; text-align: center; }
  .bar { background: #409EFF; }
}
.legend { display: flex; gap: 24px; margin-top: 12px; font-size: 13px; align-items: center; }
.legend-color { display: inline-block; width: 14px; height: 10px; margin-right: 4px; }
</style>
