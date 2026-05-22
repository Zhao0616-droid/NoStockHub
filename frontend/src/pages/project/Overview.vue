<template>
  <div class="project-overview">
    <el-card class="overview-card">
      <template #header>
        <div class="card-header">
          <h3>{{ project?.name || '项目概览' }}</h3>
          <el-tag :type="getStatusType(project?.status)">
            {{ getStatusText(project?.status) }}
          </el-tag>
        </div>
      </template>

      <div class="overview-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="总任务数" :value="stats.totalTasks" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="已完成任务" :value="stats.completedTasks" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="进行中任务" :value="stats.inProgressTasks" />
          </el-col>
        </el-row>

        <el-divider />

        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="sub-card">
              <template #header>
                <span>项目信息</span>
              </template>
              <p><strong>描述：</strong>{{ project?.description || '暂无描述' }}</p>
              <p><strong>开始日期：</strong>{{ formatDate(project?.start_date) }}</p>
              <p><strong>结束日期：</strong>{{ formatDate(project?.end_date) }}</p>
              <p><strong>负责人：</strong>{{ project?.owner?.username || '未设置' }}</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="sub-card">
              <template #header>
                <span>团队成员</span>
              </template>
              <el-space wrap>
                <el-tag
                  v-for="member in project?.members"
                  :key="member.id"
                  size="small"
                >
                  {{ member.username }}
                </el-tag>
              </el-space>
              <p v-if="!project?.members?.length">暂无成员</p>
            </el-card>
          </el-col>
        </el-row>

        <el-divider />

        <el-row>
          <el-col :span="24">
            <el-card class="sub-card">
              <template #header>
                <span>进度图表</span>
              </template>
              <div class="chart-container">
                <BurndownChart
                  v-if="project"
                  :project-id="projectId"
                  :tasks="tasks"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-divider />

        <el-row>
          <el-col :span="24">
            <el-card class="sub-card">
              <template #header>
                <span>最近活动</span>
              </template>
              <el-timeline v-if="activities.length">
                <el-timeline-item
                  v-for="a in activities"
                  :key="a.id"
                  :timestamp="formatDateTime(a.time)"
                  placement="top"
                  :color="activityColor(a.type)"
                >
                  {{ a.content }}
                  <span class="activity-user">（{{ a.user }}）</span>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-else description="暂无活动记录" />
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectAPI, taskAPI } from '@/api'
import BurndownChart from '@/components/charts/BurndownChart.vue'

const route = useRoute()
const projectId = route.params.id
const project = ref(null)
const tasks = ref([])
const activities = ref([])

const stats = computed(() => {
  const total = tasks.value.length
  const completed = tasks.value.filter(task => task.status === 'done').length
  const inProgress = tasks.value.filter(task => task.status === 'in_progress').length
  return {
    totalTasks: total,
    completedTasks: completed,
    inProgressTasks: inProgress
  }
})

const getStatusType = (status) => {
  const types = {
    'planning': 'info',
    'active': 'success',
    'completed': 'success',
    'on_hold': 'warning',
    'cancelled': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'planning': '规划中',
    'active': '进行中',
    'completed': '已完成',
    'on_hold': '暂停',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

const formatDate = (date) => {
  if (!date) return '未设置'
  return new Date(date).toLocaleDateString('zh-CN')
}

const loadProject = async () => {
  try {
    project.value = await projectAPI.detail(projectId)
  } catch (error) {
    ElMessage.error('加载项目信息失败')
  }
}

const loadTasks = async () => {
  try {
    const res = await taskAPI.list({ project_id: projectId })
    tasks.value = res.results || res
  } catch (error) {
    ElMessage.error('加载任务信息失败')
  }
}

const loadActivities = async () => {
  try {
    const res = await projectAPI.activity(projectId)
    activities.value = res.results || res || []
  } catch { /* activity is optional */ }
}

function formatDateTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

function activityColor(type) {
  return { task_created: '#67C23A', task_updated: '#409EFF', milestone: '#E6A23C' }[type] || '#909399'
}

onMounted(() => {
  loadProject()
  loadTasks()
  loadActivities()
})
</script>

<style lang="scss" scoped>
.project-overview {
  padding: 20px;

  .overview-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .overview-content {
    .sub-card {
      height: 100%;
    }

    .chart-container {
      height: 300px;
    }
  }

  .activity-user {
    font-size: 12px;
    color: #909399;
  }
}
</style>