<template>
  <div class="files-page">
    <div class="page-header">
      <h2>文件管理</h2>
      <el-upload
        :action="uploadUrl"
        :headers="uploadHeaders"
        :data="{ project_id: projectId }"
        :on-success="onUploadSuccess"
        :on-error="onUploadError"
        :show-file-list="false"
        accept=".jpg,.jpeg,.png,.gif,.svg,.webp,.bmp,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.md,.json,.xml,.yaml,.yml,.zip,.rar,.7z,.tar,.gz,.py,.js,.ts,.vue,.html,.css,.java,.go"
      >
        <el-button type="primary">+ 上传文件</el-button>
      </el-upload>
    </div>

    <el-card>
      <el-table :data="files" stripe v-loading="loading">
        <el-table-column prop="filename" label="文件名" min-width="220" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="mime_type" label="类型" width="140" />
        <el-table-column label="上传时间" width="170">
          <template #default="{ row }">{{ row.created_at || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button text size="small" type="primary" @click="handleDownload(row)">下载</el-button>
            <el-button text size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !files.length" description="暂无上传文件" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fileAPI } from '@/api'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const route = useRoute()
const projectId = computed(() => route.params.id)

const loading = ref(false)
const files = ref([])

const uploadUrl = computed(() => `${API_BASE}/files/`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`
}))

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`
}

async function fetchFiles() {
  loading.value = true
  try {
    const res = await fileAPI.list({ project_id: projectId.value })
    files.value = res.results || res || []
  } catch {
    ElMessage.warning('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

function onUploadSuccess(response) {
  ElMessage.success('上传成功')
  files.value.unshift(response)
}

function onUploadError() {
  ElMessage.error('上传失败')
}

async function handleDownload(row) {
  try {
    const blob = await fileAPI.download(row.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = row.filename
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除文件「${row.filename}」？`, '确认删除', { type: 'warning' })
    await fileAPI.delete(row.id)
    files.value = files.value.filter(f => f.id !== row.id)
    ElMessage.success('已删除')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(fetchFiles)
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
