<template>
  <div class="task-list-page">
    <div class="page-header">
      <h2>任务列表</h2>
      <el-button type="primary" @click="showCreate = true">+ 新任务</el-button>
    </div>

    <!-- 筛选 -->
    <div class="toolbar">
      <el-input v-model="search" placeholder="搜索任务..." prefix-icon="Search" clearable style="width:240px" />
      <el-select v-model="filters.status" placeholder="状态" clearable style="width:130px" multiple collapse-tags>
        <el-option label="待办" value="todo" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="审核" value="review" />
        <el-option label="已完成" value="done" />
        <el-option label="阻塞" value="blocked" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="优先级" clearable style="width:120px">
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
    </div>

    <!-- 表格 -->
    <el-table :data="tasks" stripe @row-click="showDetail" style="width:100%">
      <el-table-column width="40">
        <template #default="{ row }">
          <el-checkbox
            :model-value="row.status === 'done'"
            :disabled="row.status !== 'review'"
            @change="toggleDone(row)"
            @click.stop
          />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="任务名称" min-width="200" />
      <el-table-column prop="priority" label="优先级" width="90">
        <template #default="{ row }">
          <PriorityTag :priority="row.priority" />
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="100">
        <template #default="{ row }">{{ row.assignee?.username || '-' }}</template>
      </el-table-column>
      <el-table-column prop="due_date" label="截止日期" width="110" sortable />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <StatusTag :status="row.status" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button text size="small" @click.stop="editTask(row)">编辑</el-button>
          <el-button text size="small" type="danger" @click.stop="deleteTask(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <TaskDialog v-model="dialogVisible" :task="editingTask" :project-id="projectId" @saved="loadTasks" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTaskStore } from '@/stores/task'
import TaskDialog from '@/components/common/TaskDialog.vue'
import PriorityTag from '@/components/common/PriorityTag.vue'
import StatusTag from '@/components/common/StatusTag.vue'

const route = useRoute()
const projectId = route.params.id
const taskStore = useTaskStore()

const search = ref('')
const filters = ref({ status: [], priority: '' })
const tasks = ref([])
const dialogVisible = ref(false)
const editingTask = ref(null)
const showCreate = ref(false)

watch(showCreate, (v) => { if (v) { editingTask.value = null; dialogVisible.value = true; showCreate.value = false } })

function showDetail(row) { editingTask.value = row; dialogVisible.value = true }
function editTask(row) { editingTask.value = { ...row }; dialogVisible.value = true }
async function deleteTask(row) {
  await ElMessageBox.confirm('确定删除？', '确认', { type: 'warning' })
  await taskStore.deleteTask(row.id)
  ElMessage.success('删除成功')
  loadTasks()
}
async function toggleDone(row) {
  await taskStore.updateStatus(row.id, 'done')
  ElMessage.success('任务完成')
  loadTasks()
}

async function loadTasks() {
  tasks.value = [
    { id: 't1', title: '设计数据库ER图', priority: 'high', status: 'in_progress', assignee: { username: '张三' }, due_date: '2026-05-07' },
    { id: 't2', title: '编写API接口文档', priority: 'medium', status: 'todo', assignee: { username: '李四' }, due_date: '2026-05-10' },
    { id: 't3', title: '代码审查', priority: 'low', status: 'todo', assignee: { username: '王五' }, due_date: '2026-05-12' },
    { id: 't4', title: '部署测试', priority: 'high', status: 'blocked', assignee: { username: '张三' }, due_date: '2026-05-15' }
  ]
}

onMounted(loadTasks)
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
</style>
