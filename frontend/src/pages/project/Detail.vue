<template>
  <div class="project-detail" v-loading="loading">
    <div class="page-header">
      <div>
        <el-button text @click="$router.back()">← 返回</el-button>
        <h2>{{ project?.name }}</h2>
      </div>
      <div>
        <el-button @click="editMode = true">编辑</el-button>
        <el-button type="primary" @click="$router.push(`/projects/${id}/board`)">进入看板</el-button>
      </div>
    </div>

    <!-- 概览卡片 -->
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card>
          <div style="text-align:center">
            <el-progress type="circle" :percentage="project?.progress || 0" :color="progressColor" />
            <p style="margin-top:12px;color:#606266">整体进度</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="任务" :value="`${doneTasks}/${totalTasks}`" />
          <el-statistic title="日期" :value="`${project?.start_date} ~ ${project?.end_date}`" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="状态">
            <StatusTag :status="project?.status" />
          </el-statistic>
          <el-statistic title="可见性" :value="project?.visibility === 'public' ? '公开' : '私密'" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 成员 & 里程碑 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card header="团队成员">
          <div v-for="m in members" :key="m.id" class="member-row">
            <el-avatar :size="28">{{ m.user?.username?.[0] }}</el-avatar>
            <span>{{ m.user?.username }}</span>
            <el-tag size="small">{{ roleLabel(m.role) }}</el-tag>
          </div>
          <el-button text type="primary" style="margin-top:8px">+ 邀请成员</el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="里程碑">
          <div v-for="m in milestones" :key="m.id" class="milestone-item">
            <el-icon :color="m.status === 'completed' ? '#67C23A' : '#909399'">
              <component :is="m.status === 'completed' ? 'CircleCheckFilled' : 'CircleCheck'" />
            </el-icon>
            <span>{{ m.name }}</span>
            <span class="milestone-date">{{ m.due_date }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import StatusTag from '@/components/common/StatusTag.vue'

const route = useRoute()
const id = route.params.id
const store = useProjectStore()

const loading = ref(false)
const editMode = ref(false)
const project = ref(null)
const members = ref([])
const milestones = ref([])
const totalTasks = ref(0)
const doneTasks = ref(0)

function roleLabel(role) {
  return { manager: '管理者', member: '成员', viewer: '观察者' }[role] || role
}

const progressColor = computed(() => {
  const p = project.value?.progress || 0
  return p < 30 ? '#F56C6C' : p < 80 ? '#409EFF' : '#67C23A'
})

import { computed } from 'vue'

onMounted(async () => {
  loading.value = true
  try {
    project.value = await store.fetchProject(id)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.member-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
.milestone-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
.milestone-date { font-size: 12px; color: #909399; margin-left: auto; }
</style>
