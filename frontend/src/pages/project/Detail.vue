<template>
  <div class="project-detail" v-loading="loading">
    <div class="page-header">
      <div>
        <el-button text @click="$router.back()">← 返回</el-button>
        <h2>{{ project?.name }}</h2>
      </div>
      <div>
        <el-button @click="openEditDialog">编辑</el-button>
        <el-button type="primary" @click="$router.push(`/projects/${id}/board`)">进入看板</el-button>
        <el-button type="danger" @click="handleDeleteProject">删除项目</el-button>
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
          <el-button text type="primary" style="margin-top:8px" @click="openInviteDialog">+ 邀请成员</el-button>
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

    <!-- 编辑项目对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑项目" width="520px" :close-on-click-modal="false">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="80px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="editForm.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker v-model="editForm.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width:100%">
            <el-option label="规划中" value="planning" />
            <el-option label="进行中" value="active" />
            <el-option label="已完成" value="completed" />
            <el-option label="暂停" value="on_hold" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="可见性">
          <el-radio-group v-model="editForm.visibility">
            <el-radio value="public">公开</el-radio>
            <el-radio value="private">私密</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProject" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 邀请成员对话框 -->
    <el-dialog v-model="showInviteDialog" title="邀请成员" width="440px" :close-on-click-modal="false">
      <el-form ref="inviteFormRef" :model="inviteForm" :rules="inviteRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-select
            v-model="inviteForm.username"
            filterable
            remote
            reserve-keyword
            placeholder="输入用户名搜索"
            :remote-method="searchUsers"
            :loading="searchingUsers"
            style="width:100%"
          >
            <el-option
              v-for="u in userOptions"
              :key="u.id"
              :label="`${u.username} (${u.email})`"
              :value="u.username"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="inviteForm.role" style="width:100%">
            <el-option label="成员" value="member" />
            <el-option label="观察者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInviteDialog = false">取消</el-button>
        <el-button type="primary" @click="inviteMember" :loading="inviting">邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import { projectAPI, taskAPI, userAPI } from '@/api'
import StatusTag from '@/components/common/StatusTag.vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const store = useProjectStore()

const loading = ref(false)
const saving = ref(false)
const inviting = ref(false)
const project = ref(null)
const members = ref([])
const milestones = ref([])
const taskStats = ref({ total: 0, done: 0 })
const totalTasks = computed(() => taskStats.value.total)
const doneTasks = computed(() => taskStats.value.done)

// --------------- 编辑 ---------------
const showEditDialog = ref(false)
const editFormRef = ref(null)
const editForm = reactive({
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  status: '',
  visibility: 'public',
})
const editRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

function openEditDialog() {
  if (!project.value) return
  Object.assign(editForm, {
    name: project.value.name || '',
    description: project.value.description || '',
    start_date: project.value.start_date || '',
    end_date: project.value.end_date || '',
    status: project.value.status || 'planning',
    visibility: project.value.visibility || 'public',
  })
  showEditDialog.value = true
}

async function saveProject() {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = { ...editForm }
    project.value = await projectAPI.update(id, payload)
    ElMessage.success('项目已更新')
    showEditDialog.value = false
  } catch {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

// --------------- 邀请成员 ---------------
const showInviteDialog = ref(false)
const inviteFormRef = ref(null)
const inviteForm = reactive({ username: '', role: 'member' })
const inviteRules = {
  username: [{ required: true, message: '请选择用户', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}
const searchingUsers = ref(false)
const userOptions = ref([])

function openInviteDialog() {
  inviteForm.username = ''
  inviteForm.role = 'member'
  userOptions.value = []
  showInviteDialog.value = true
}

async function searchUsers(query) {
  if (!query || query.trim().length < 1) {
    userOptions.value = []
    return
  }
  searchingUsers.value = true
  try {
    const res = await userAPI.search(query.trim())
    userOptions.value = res || []
  } catch {
    userOptions.value = []
  } finally {
    searchingUsers.value = false
  }
}

async function inviteMember() {
  const valid = await inviteFormRef.value?.validate().catch(() => false)
  if (!valid) return
  inviting.value = true
  try {
    await projectAPI.addMember(id, { username: inviteForm.username, role: inviteForm.role })
    ElMessage.success('成员已邀请')
    showInviteDialog.value = false
    const res = await projectAPI.members(id)
    members.value = res.results || res || []
  } catch (e) {
    ElMessage.error(formatErrors(e.response?.data) || '邀请失败')
  } finally {
    inviting.value = false
  }
}

async function handleDeleteProject() {
  try {
    await ElMessageBox.confirm(
      `确定删除项目「${project.value?.name}」？删除后所有任务、看板、冲刺等数据也将被删除，此操作不可恢复。`,
      '确认删除项目',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await store.deleteProject(id)
    ElMessage.success('项目已删除')
    router.push('/projects')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function formatErrors(data) {
  if (!data) return null
  if (typeof data === 'string') return data
  return Object.entries(data)
    .map(([k, v]) => {
      const label = { user_id: '用户ID', username: '用户名', non_field_errors: '' }[k] || k
      const msg = Array.isArray(v) ? v.join(', ') : v
      return label ? `${label}: ${msg}` : msg
    })
    .join('; ')
}

function roleLabel(role) {
  return { manager: '管理者', member: '成员', viewer: '观察者' }[role] || role
}

const progressColor = computed(() => {
  const p = project.value?.progress || 0
  return p < 30 ? '#F56C6C' : p < 80 ? '#409EFF' : '#67C23A'
})

onMounted(async () => {
  loading.value = true
  try {
    project.value = await store.fetchProject(id)
    const [membersRes, milestonesRes, tasksRes] = await Promise.all([
      projectAPI.members(id).catch(() => []),
      projectAPI.milestones(id).catch(() => []),
      taskAPI.list({ project_id: id }).catch(() => []),
    ])
    members.value = membersRes.results || membersRes || []
    milestones.value = milestonesRes.results || milestonesRes || []
    const taskList = tasksRes.results || tasksRes || []
    taskStats.value = {
      total: taskList.length,
      done: taskList.filter(t => t.status === 'done').length,
    }
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
