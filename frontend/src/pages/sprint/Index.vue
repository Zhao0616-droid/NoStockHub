<template>
  <div class="sprint-page">
    <div class="page-header">
      <h2>冲刺管理</h2>
      <el-button type="primary" @click="showCreate = true">+ 新建冲刺</el-button>
    </div>

    <div v-loading="loading">
      <!-- 进行中冲刺 -->
      <div v-if="activeSprint" class="active-sprint">
        <el-card>
          <template #header>
            <div class="sprint-header">
              <span>{{ activeSprint.name }} (进行中)</span>
              <el-tag type="warning">{{ activeSprint.status }}</el-tag>
            </div>
          </template>
          <p class="sprint-goal">目标: {{ activeSprint.goal || '暂无' }}</p>
          <p class="sprint-date">{{ activeSprint.start_date }} ~ {{ activeSprint.end_date }}</p>
          <el-progress :percentage="activeSprint.progress || 0" />
          <div class="sprint-tasks">
            <el-tag v-for="t in sprintTasks" :key="t.id" closable style="margin:4px" @close="removeTask(t.id)">{{ t.title }}</el-tag>
            <el-empty v-if="!sprintTasks.length" description="暂无任务" :image-size="40" />
          </div>
          <div class="sprint-actions">
            <el-button @click="openBurndown(activeSprint.id)">查看燃尽图</el-button>
            <el-button type="warning" @click="handleComplete">完成冲刺</el-button>
          </div>
        </el-card>
      </div>

      <!-- 规划中的冲刺 -->
      <el-card v-for="s in plannedSprints" :key="s.id" class="planned-sprint">
        <div class="sprint-header">
          <span>{{ s.name }} ({{ s.status === 'planning' ? '规划中' : '已完成' }})</span>
          <div class="sprint-header-actions">
            <el-button v-if="s.status === 'planning'" size="small" type="primary" @click="handleStart(s.id)">启动冲刺</el-button>
            <el-button size="small" type="danger" @click="handleDeleteSprint(s)">删除</el-button>
          </div>
        </div>
        <p>{{ s.start_date }} ~ {{ s.end_date }}</p>
        <p v-if="s.goal" class="sprint-goal">{{ s.goal }}</p>
      </el-card>

      <el-empty v-if="!loading && !activeSprint && !plannedSprints.length" description="暂无冲刺" />
    </div>

    <!-- 燃尽图对话框 -->
    <el-dialog v-model="showBurndown" title="燃尽图" width="720px" @opened="onBurndownOpened">
      <BurndownChart
        :dates="burndownDates"
        :ideal="burndownIdeal"
        :actual="burndownActual"
        height="380px"
      />
    </el-dialog>

    <!-- 创建冲刺对话框 -->
    <el-dialog v-model="showCreate" title="新建冲刺" width="480px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="冲刺名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入冲刺名称" />
        </el-form-item>
        <el-form-item label="冲刺目标">
          <el-input v-model="form.goal" type="textarea" :rows="2" placeholder="冲刺目标（选填）" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="开始日期"><el-date-picker v-model="form.start_date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结束日期"><el-date-picker v-model="form.end_date" style="width:100%" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sprintAPI } from '@/api'
import { BurndownChart } from '@/components/charts'

const route = useRoute()
const projectId = computed(() => route.params.id)

const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)
const showBurndown = ref(false)
const formRef = ref(null)

const sprints = ref([])
const sprintTasks = ref([])

const form = ref({ name: '', goal: '', start_date: '', end_date: '' })
const rules = {
  name: [{ required: true, message: '请输入冲刺名称', trigger: 'blur' }]
}

const activeSprint = computed(() => sprints.value.find(s => s.status === 'active'))
const plannedSprints = computed(() => sprints.value.filter(s => s.status !== 'active'))

// --- Burndown ---
const burndownDates = ref([])
const burndownIdeal = ref([])
const burndownActual = ref([])

function fmtDate(d) {
  if (!d) return null
  return new Date(d).toISOString().slice(0, 10)
}

async function fetchSprints() {
  loading.value = true
  try {
    const res = await sprintAPI.list({ project_id: projectId.value })
    sprints.value = res.results || res
    if (activeSprint.value) {
      await fetchSprintTasks(activeSprint.value.id)
    }
  } catch {
    ElMessage.warning('加载冲刺数据失败')
  } finally {
    loading.value = false
  }
}

async function fetchSprintTasks(sprintId) {
  try {
    const res = await sprintAPI.listTasks(sprintId)
    // The backend returns a list directly, or via the manage_tasks endpoint
    sprintTasks.value = Array.isArray(res) ? res : (res.results || [])
  } catch { /* ignore */ }
}

async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await sprintAPI.create({
      name: form.value.name,
      goal: form.value.goal,
      start_date: fmtDate(form.value.start_date),
      end_date: fmtDate(form.value.end_date),
      project_id: projectId.value,
    })
    ElMessage.success('冲刺创建成功')
    showCreate.value = false
    fetchSprints()
  } catch (e) {
    const data = e.response?.data || {}
    ElMessage.error(data.detail || data.name?.[0] || '创建失败')
  } finally {
    creating.value = false
  }
}

async function handleStart(id) {
  try {
    await sprintAPI.start(id)
    ElMessage.success('冲刺已启动')
    fetchSprints()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '启动失败')
  }
}

async function handleComplete() {
  if (!activeSprint.value) return
  try {
    await sprintAPI.complete(activeSprint.value.id)
    ElMessage.success('冲刺已完成')
    fetchSprints()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '完成失败')
  }
}

async function handleDeleteSprint(sprint) {
  try {
    await ElMessageBox.confirm(
      `确定删除冲刺「${sprint.name}」？`,
      '确认删除',
      { type: 'warning' }
    )
    await sprintAPI.delete(sprint.id)
    ElMessage.success('冲刺已删除')
    fetchSprints()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function removeTask(taskId) {
  if (!activeSprint.value) return
  try {
    await sprintAPI.removeTask(activeSprint.value.id, taskId)
    sprintTasks.value = sprintTasks.value.filter(t => t.id !== taskId)
  } catch {
    ElMessage.warning('移除任务失败')
  }
}

async function openBurndown(sprintId) {
  try {
    const res = await sprintAPI.burndown(sprintId)
    burndownDates.value = (res.ideal_line || []).map(p => p.date)
    burndownIdeal.value = (res.ideal_line || []).map(p => p.remaining)
    burndownActual.value = (res.actual_line || []).map(p => p.remaining)
  } catch {
    ElMessage.warning('加载燃尽图失败')
  }
  showBurndown.value = true
}

function onBurndownOpened() {
  nextTick(() => {
    setTimeout(() => window.dispatchEvent(new Event('resize')), 100)
  })
}

function resetForm() {
  form.value = { name: '', goal: '', start_date: '', end_date: '' }
}

onMounted(fetchSprints)
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.active-sprint { margin-bottom: 16px; }
.sprint-header { display: flex; justify-content: space-between; align-items: center; }
.sprint-header-actions { display: flex; gap: 8px; }
.sprint-goal { color: #606266; }
.sprint-date { font-size: 13px; color: #909399; margin: 8px 0; }
.sprint-tasks { margin: 12px 0; }
.sprint-actions { display: flex; gap: 8px; margin-top: 12px; }
.planned-sprint { margin-bottom: 12px; }
</style>
