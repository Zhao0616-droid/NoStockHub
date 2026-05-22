<template>
  <div class="worklog-page">
    <div class="page-header">
      <h2>工时管理</h2>
      <el-button type="primary" @click="openCreate">+ 记录工时</el-button>
    </div>

    <el-card>
      <el-table :data="worklogs" stripe v-loading="loading">
        <el-table-column label="用户" width="120">
          <template #default="{ row }">{{ row.user?.username || '-' }}</template>
        </el-table-column>
        <el-table-column label="关联任务" min-width="180">
          <template #default="{ row }">{{ row.task_title || '-' }}</template>
        </el-table-column>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="hours" label="工时(h)" width="100" />
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !worklogs.length" description="暂无工时记录" />
    </el-card>

    <el-dialog v-model="showCreate" title="记录工时" width="440px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="任务" prop="task">
          <el-select
            v-model="form.task"
            placeholder="选择关联任务"
            filterable
            style="width:100%"
            :loading="loadingTasks"
          >
            <el-option
              v-for="t in tasks"
              :key="t.id"
              :label="`${t.title} (${t.status})`"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="工时" prop="hours">
          <el-input-number v-model="form.hours" :min="0.5" :max="24" :step="0.5" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { worklogAPI, taskAPI } from '@/api'

const route = useRoute()
const projectId = computed(() => route.params.id)

const loading = ref(false)
const creating = ref(false)
const loadingTasks = ref(false)
const showCreate = ref(false)
const worklogs = ref([])
const tasks = ref([])
const formRef = ref(null)

const form = ref({ task: '', date: '', hours: 1, description: '' })
const rules = {
  task: [{ required: true, message: '请选择任务', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'blur' }],
  hours: [{ required: true, message: '请输入工时', trigger: 'blur' }],
}

async function fetchWorklogs() {
  loading.value = true
  try {
    const res = await worklogAPI.list({ project_id: projectId.value })
    worklogs.value = res.results || res || []
  } catch {
    ElMessage.warning('加载工时记录失败')
  } finally {
    loading.value = false
  }
}

async function fetchTasks() {
  loadingTasks.value = true
  try {
    const res = await taskAPI.list({ project_id: projectId.value, page_size: 200 })
    tasks.value = res.results || res || []
  } catch {
    tasks.value = []
  } finally {
    loadingTasks.value = false
  }
}

async function openCreate() {
  await fetchTasks()
  showCreate.value = true
}

function formatErrors(data) {
  if (!data) return '记录失败'
  if (typeof data === 'string') return data
  return Object.entries(data)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    .join('; ')
}

async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await worklogAPI.create({
      task: form.value.task,
      date: form.value.date,
      hours: form.value.hours,
      description: form.value.description,
    })
    ElMessage.success('工时记录成功')
    showCreate.value = false
    fetchWorklogs()
  } catch (e) {
    ElMessage.error(formatErrors(e.response?.data))
  } finally {
    creating.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该工时记录？', '确认删除', { type: 'warning' })
    await worklogAPI.delete(row.id)
    worklogs.value = worklogs.value.filter(w => w.id !== row.id)
    ElMessage.success('已删除')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  form.value = { task: '', date: '', hours: 1, description: '' }
}

onMounted(fetchWorklogs)
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
