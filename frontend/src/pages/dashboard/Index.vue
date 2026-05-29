<template>
  <div class="dashboard">
    <h2>你好，{{ user.username }}</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="(s, i) in stats" :key="s.label">
        <el-card shadow="hover" class="stat-card" :class="{ clickable: s.link }" @click="s.link && $router.push(s.link)">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 我的任务 -->
      <el-col :span="14">
        <el-card header="我的任务">
          <template v-if="myTasks.length">
            <div v-for="t in myTasks" :key="t.id" class="task-row" @click="goTask(t)">
              <el-checkbox :model-value="t.status === 'done'" @change.stop="toggleDone(t)" />
              <span class="task-title">{{ t.title }}</span>
              <PriorityTag :priority="t.priority" />
              <span class="task-due">{{ t.due_date || '-' }}</span>
            </div>
          </template>
          <el-empty v-else description="暂无待办任务" />
        </el-card>
      </el-col>

      <!-- 最近项目 -->
      <el-col :span="10">
        <el-card header="最近项目">
          <div v-for="p in recentProjects" :key="p.id" class="project-row" @click="$router.push(`/projects/${p.id}`)">
            <el-icon><Folder /></el-icon>
            <span>{{ p.name }}</span>
            <el-progress :percentage="p.progress || 0" :stroke-width="6" />
          </div>
          <el-empty v-if="!recentProjects.length" description="暂无项目" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card header="最近活动" style="margin-top:16px">
      <el-timeline v-if="activities.length">
        <el-timeline-item v-for="a in activities" :key="a.id" :timestamp="a.time" placement="top">
          {{ a.content }}
          <span class="activity-project">（{{ a.project_name }}）</span>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无活动" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/task'
import { dashboardAPI } from '@/api'
import { Folder } from '@element-plus/icons-vue'
import PriorityTag from '@/components/common/PriorityTag.vue'

const router = useRouter()
const auth = useAuthStore()
const taskStore = useTaskStore()

const user = computed(() => auth.user || { username: '...' })

const stats = ref([
  { label: '参与项目', value: 0 },
  { label: '待办任务', value: 0 },
  { label: '进行中冲刺', value: 0 },
  { label: '完成率', value: '0%' }
])

const myTasks = ref([])
const recentProjects = ref([])
const activities = ref([])
const loading = ref(false)

async function fetchDashboard() {
  loading.value = true
  try {
    const res = await dashboardAPI.summary()
    stats.value = [
      { label: '参与项目', value: res.stats.project_count, link: '/projects' },
      { label: '待办任务', value: res.stats.pending_task_count, link: '/projects' },
      { label: '进行中冲刺', value: res.stats.active_sprint_count, link: '/projects' },
      { label: '完成率', value: res.stats.completion_rate + '%' }
    ]
    myTasks.value = res.my_tasks
    recentProjects.value = res.recent_projects
    activities.value = res.activities
  } catch {
    ElMessage.warning('加载仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

function goTask(task) {
  if (task.project_id) {
    router.push(`/projects/${task.project_id}/board`)
  }
}

function toggleDone(task) {
  const newStatus = task.status === 'done' ? 'in_progress' : 'done'
  taskStore.updateStatus(task.id, newStatus).then(() => {
    task.status = newStatus
    if (newStatus === 'done') {
      myTasks.value = myTasks.value.filter(t => t.id !== task.id)
      stats.value[1].value = Math.max(0, stats.value[1].value - 1)
    }
  })
}

onMounted(fetchDashboard)
</script>

<style scoped lang="scss">
.stats-row { margin-bottom: 16px; }
.stat-card { text-align: center; }
.stat-card.clickable { cursor: pointer; }
.stat-card.clickable:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.stat-value { font-size: 28px; font-weight: bold; color: #409EFF; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
.task-row {
  display: flex; align-items: center; gap: 10px; padding: 8px 0; cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  &:hover { background: #f5f7fa; }
}
.task-title { flex: 1; }
.task-due { font-size: 12px; color: #909399; }
.project-row {
  display: flex; align-items: center; gap: 8px; padding: 8px 0; cursor: pointer;
  &:hover { background: #f5f7fa; }
}
.activity-project { font-size: 12px; color: #909399; }
</style>
