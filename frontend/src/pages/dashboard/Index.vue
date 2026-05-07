<template>
  <div class="dashboard">
    <h2>你好，{{ user.username }}</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="s in stats" :key="s.label">
        <el-card shadow="hover" class="stat-card">
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
              <el-checkbox :model-value="t.status === 'done'" @change="toggleDone(t)" />
              <span class="task-title">{{ t.title }}</span>
              <PriorityTag :priority="t.priority" />
              <span class="task-due">{{ t.due_date }}</span>
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
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无活动" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTaskStore } from '@/stores/task'
import { useProjectStore } from '@/stores/project'
import PriorityTag from '@/components/common/PriorityTag.vue'

const router = useRouter()
const auth = useAuthStore()
const taskStore = useTaskStore()
const projectStore = useProjectStore()

const user = computed(() => auth.user || { username: '...' })

const stats = ref([
  { label: '参与项目', value: 2 },
  { label: '待办任务', value: 12 },
  { label: '进行中冲刺', value: 1 },
  { label: '完成率', value: '85%' }
])

const myTasks = ref([
  { id: '1', title: '设计数据库ER图', priority: 'high', due_date: '2026-05-07', status: 'in_progress' },
  { id: '2', title: '编写API接口文档', priority: 'medium', due_date: '2026-05-10', status: 'todo' }
])

const recentProjects = computed(() => projectStore.projects.slice(0, 5))

const activities = ref([
  { id: '1', content: '张三 将任务「设计ER图」标记为已完成', time: '10分钟前' },
  { id: '2', content: '李四 创建了新任务「API开发」', time: '1小时前' }
])

function goTask(task) { router.push(`/tasks/${task.id}`) }
function toggleDone(task) { taskStore.updateStatus(task.id, task.status === 'done' ? 'in_progress' : 'done') }
</script>

<style scoped lang="scss">
.stats-row { margin-bottom: 16px; }
.stat-card { text-align: center; }
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
</style>
