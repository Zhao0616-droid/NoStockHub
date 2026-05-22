<template>
  <div class="task-list-page" v-loading="taskStore.loading">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>任务列表</h2>
      <div class="header-right">
        <span class="total-count">共 {{ taskStore.total }} 条</span>
        <el-button type="primary" @click="openCreate()">+ 新任务</el-button>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索任务名称或描述..."
        :prefix-icon="Search"
        clearable
        style="width: 260px"
        @input="onSearchDebounced"
      />
      <el-select
        v-model="filters.status"
        placeholder="状态"
        clearable
        style="width: 180px"
        multiple
        collapse-tags
        collapse-tags-tooltip
        @change="applyFilters"
      >
        <el-option label="待办" value="todo" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="审核中" value="review" />
        <el-option label="已完成" value="done" />
        <el-option label="阻塞" value="blocked" />
      </el-select>
      <el-select
        v-model="filters.priority"
        placeholder="优先级"
        clearable
        style="width: 130px"
        @change="applyFilters"
      >
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
      <el-select
        v-model="filters.type"
        placeholder="类型"
        clearable
        style="width: 120px"
        @change="applyFilters"
      >
        <el-option label="任务" value="task" />
        <el-option label="缺陷" value="bug" />
        <el-option label="史诗" value="epic" />
      </el-select>
      <el-select
        v-model="filters.assignee_id"
        placeholder="负责人"
        clearable
        filterable
        style="width: 140px"
        @change="applyFilters"
      >
        <el-option
          v-for="m in memberOptions"
          :key="m.id"
          :label="m.username"
          :value="m.id"
        />
      </el-select>
      <el-button
        v-if="hasActiveFilters"
        text
        type="primary"
        @click="clearAllFilters"
      >
        清除筛选
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table
      :data="taskStore.filteredTasks"
      stripe
      style="width: 100%"
      @sort-change="onSortChange"
      @row-click="showDetail"
      row-class-name="task-row"
    >
      <el-table-column width="48">
        <template #default="{ row }">
          <el-checkbox
            :model-value="row.status === 'done'"
            :disabled="row.status === 'done'"
            @change="toggleDone(row)"
            @click.stop
          />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="任务名称" min-width="220" sortable="custom" />
      <el-table-column prop="type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag size="small" :type="typeTagType(row.type)">{{ typeLabel(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="90" sortable="custom">
        <template #default="{ row }">
          <PriorityTag :priority="row.priority" />
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="100">
        <template #default="{ row }">
          <span class="assignee-cell">
            <el-avatar :size="20">{{ row.assignee?.username?.[0] || '?' }}</el-avatar>
            {{ row.assignee?.username || '未分配' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="due_date" label="截止日期" width="120" sortable="custom">
        <template #default="{ row }">
          <span :class="{ 'overdue': isOverdue(row) }">{{ row.due_date || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" sortable="custom">
        <template #default="{ row }">
          <StatusTag :status="row.status" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button text size="small" @click.stop="editTask(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button text size="small" type="danger" @click.stop="handleDelete(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="taskStore.total > taskStore.pageSize">
      <el-pagination
        v-model:current-page="taskStore.page"
        :page-size="taskStore.pageSize"
        :total="taskStore.total"
        :page-sizes="[5, 10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="onPageChange"
        @size-change="onPageSizeChange"
      />
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!taskStore.loading && taskStore.total === 0"
      :description="hasActiveFilters ? '没有匹配的任务，请调整筛选条件' : '暂无任务，点击「+ 新任务」创建'"
    >
      <el-button v-if="!hasActiveFilters" type="primary" @click="openCreate()">创建第一个任务</el-button>
      <el-button v-else @click="clearAllFilters">清除筛选</el-button>
    </el-empty>

    <!-- 任务创建/编辑对话框 -->
    <TaskDialog
      v-model="dialogVisible"
      :task="editingTask"
      :project-id="projectId"
      @saved="onTaskSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Edit, Delete } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { projectAPI } from '@/api'
import TaskDialog from '@/components/common/TaskDialog.vue'
import PriorityTag from '@/components/common/PriorityTag.vue'
import StatusTag from '@/components/common/StatusTag.vue'

const route = useRoute()
const projectId = route.params.id
const taskStore = useTaskStore()

// --------------- 筛选 ---------------
const searchText = ref('')
const memberOptions = ref([])
const filters = ref({
  status: [],
  priority: '',
  type: '',
  assignee_id: ''
})

let searchTimer = null
function onSearchDebounced() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    taskStore.setFilters({ search: searchText.value })
  }, 300)
}

const hasActiveFilters = computed(() => {
  return searchText.value ||
    filters.value.status.length > 0 ||
    filters.value.priority ||
    filters.value.type ||
    filters.value.assignee_id
})

function applyFilters() {
  taskStore.setFilters({
    status: filters.value.status,
    priority: filters.value.priority,
    type: filters.value.type,
    assignee_id: filters.value.assignee_id
  })
}

function clearAllFilters() {
  searchText.value = ''
  filters.value = { status: [], priority: '', type: '', assignee_id: '' }
  taskStore.resetFilters()
}

// --------------- 排序 ---------------
function onSortChange({ prop, order }) {
  if (prop) {
    taskStore.setSort(prop)
  } else {
    taskStore.sortField = ''
    taskStore.sortOrder = 'asc'
  }
}

// --------------- 分页 ---------------
function onPageChange(p) { taskStore.setPage(p) }
function onPageSizeChange(s) { taskStore.setPageSize(s) }

// --------------- 任务操作 ---------------
const dialogVisible = ref(false)
const editingTask = ref(null)

function openCreate() {
  editingTask.value = null
  dialogVisible.value = true
}

function showDetail(row) {
  editingTask.value = row
  dialogVisible.value = true
}

function editTask(row) {
  editingTask.value = { ...row }
  dialogVisible.value = true
}

async function toggleDone(row) {
  if (row.status === 'done') return
  try {
    await taskStore.updateStatus(row.id, 'done')
    ElMessage.success('任务已完成')
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除任务「${row.title}」？此操作不可撤销。`,
      '确认删除',
      { type: 'warning' }
    )
    await taskStore.deleteTask(row.id)
    ElMessage.success('任务已删除')
  } catch {
    // 取消操作
  }
}

function onTaskSaved() {
  dialogVisible.value = false
  loadTasks()
}

// --------------- 工具函数 ---------------
function typeLabel(type) {
  return { task: '任务', bug: '缺陷', epic: '史诗' }[type] || type || '任务'
}

function typeTagType(type) {
  return { task: undefined, bug: 'danger', epic: 'primary' }[type] || 'info'
}

function isOverdue(row) {
  if (!row.due_date || row.status === 'done') return false
  return new Date(row.due_date) < new Date()
}

// --------------- 数据加载 ---------------
async function loadTasks() {
  await taskStore.fetchTasks({ project_id: projectId })
}

onMounted(async () => {
  taskStore.setFilters({ project_id: projectId })
  await loadTasks()
  // 加载项目成员用于筛选
  if (projectId) {
    try {
      const res = await projectAPI.members(projectId)
      const list = res.results || res || []
      memberOptions.value = list.map(m => ({ id: m.user?.id, username: m.user?.username || '-' }))
    } catch { /* keep empty */ }
  }
})

// 监听项目切换
watch(() => route.params.id, (newId) => {
  if (newId) {
    taskStore.setFilters({ project_id: newId })
    loadTasks()
  }
})
</script>

<style scoped lang="scss">
.task-list-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;

  h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-count {
  font-size: 13px;
  color: #909399;
}

// ---------- 筛选工具栏 ----------
.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

// ---------- 表格 ----------
:deep(.task-row) {
  cursor: pointer;

  &:hover {
    background-color: #f5f7fa;
  }
}

.assignee-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.overdue {
  color: #f56c6c;
  font-weight: 500;
}

// ---------- 分页 ----------
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
</style>
