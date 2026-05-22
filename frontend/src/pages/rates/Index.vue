<template>
  <div class="rates-page">
    <div class="page-header">
      <h2>工时费率管理</h2>
      <el-button type="primary" @click="openCreate">+ 新增费率</el-button>
    </div>

    <el-card>
      <el-table :data="rates" stripe v-loading="loading">
        <el-table-column label="用户" width="150">
          <template #default="{ row }">{{ row.user_summary?.username || row.user || '-' }}</template>
        </el-table-column>
        <el-table-column label="时薪(元)" width="120">
          <template #default="{ row }">{{ row.rate }}</template>
        </el-table-column>
        <el-table-column prop="effective_from" label="生效日期" width="130" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !rates.length" description="暂无费率记录" />
    </el-card>

    <el-dialog v-model="showCreate" title="新增费率" width="400px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户" prop="user">
          <el-select v-model="form.user" style="width:100%" filterable placeholder="选择用户（默认自己）" clearable>
            <el-option
              v-for="m in members"
              :key="m.user?.id"
              :label="m.user?.username"
              :value="m.user?.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时薪" prop="rate">
          <el-input-number v-model="form.rate" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="生效日期" prop="effective_from">
          <el-date-picker v-model="form.effective_from" type="date" value-format="YYYY-MM-DD" style="width:100%" />
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
import { rateAPI, projectAPI } from '@/api'

const route = useRoute()
const projectId = computed(() => route.params.id)

const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)
const rates = ref([])
const members = ref([])
const formRef = ref(null)

const form = ref({ user: '', rate: 100, effective_from: '' })
const rules = {
  rate: [{ required: true, message: '请输入时薪', trigger: 'blur' }],
  effective_from: [{ required: true, message: '请选择生效日期', trigger: 'blur' }],
}

async function fetchRates() {
  loading.value = true
  try {
    const res = await rateAPI.list({ project_id: projectId.value })
    rates.value = res.results || res || []
  } catch {
    ElMessage.warning('加载费率记录失败')
  } finally {
    loading.value = false
  }
}

async function loadMembers() {
  try {
    const res = await projectAPI.members(projectId.value)
    members.value = res.results || res || []
  } catch {
    members.value = []
  }
}

function openCreate() {
  loadMembers()
  showCreate.value = true
}

async function handleCreate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  const payload = {
    rate: form.value.rate,
    effective_from: form.value.effective_from,
    project: projectId.value,
  }
  if (form.value.user) payload.user = form.value.user
  try {
    await rateAPI.create(payload)
    ElMessage.success('费率创建成功')
    showCreate.value = false
    fetchRates()
  } catch (e) {
    ElMessage.error(formatErrors(e.response?.data))
  } finally {
    creating.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该费率记录？', '确认删除', { type: 'warning' })
    await rateAPI.delete(row.id)
    rates.value = rates.value.filter(r => r.id !== row.id)
    ElMessage.success('已删除')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  form.value = { user: '', rate: 100, effective_from: '' }
}

function formatErrors(data) {
  if (!data) return '操作失败'
  if (typeof data === 'string') return data
  return Object.entries(data)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    .join('; ')
}

onMounted(fetchRates)
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
