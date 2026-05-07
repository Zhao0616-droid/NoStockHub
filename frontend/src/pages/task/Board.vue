<template>
  <div class="board-page">
    <div class="page-header">
      <h2>任务看板</h2>
      <div>
        <el-select v-model="currentBoard" placeholder="选择看板" style="width:160px">
          <el-option v-for="b in boards" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
        <el-button style="margin-left:8px" @click="showAddColumn = true">+ 列</el-button>
        <el-button type="primary" @click="showCreateTask = true">+ 任务</el-button>
      </div>
    </div>

    <!-- 看板列 -->
    <div class="board-columns">
      <div v-for="col in columns" :key="col.id" class="board-column">
        <div class="column-header" :class="{ 'wip-exceeded': col.wip_limit && col.tasks?.length > col.wip_limit }">
          <span>{{ col.name }}</span>
          <el-tag size="small" :type="col.wip_limit && col.tasks?.length > col.wip_limit ? 'danger' : 'info'">
            {{ col.tasks?.length || 0 }}
          </el-tag>
        </div>
        <div class="column-body">
          <TaskCard
            v-for="task in col.tasks"
            :key="task.id"
            :task="task"
            @click="showTaskDetail(task)"
          />
          <el-button text class="add-task-btn" @click="quickCreate(col.id)">+ 添加任务</el-button>
        </div>
      </div>
    </div>

    <!-- 任务详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="任务详情" size="480px">
      <template v-if="currentTask">
        <h3>{{ currentTask.title }}</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentTask.status)">{{ currentTask.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <PriorityTag :priority="currentTask.priority" />
          </el-descriptions-item>
          <el-descriptions-item label="负责人">{{ currentTask.assignee?.username || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截止日期">{{ currentTask.due_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ currentTask.description || '暂无描述' }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px">
          <el-button type="primary" @click="editTask(currentTask)">编辑</el-button>
          <el-button type="danger" @click="deleteTask(currentTask)">删除</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 创建/编辑任务对话框 -->
    <TaskDialog v-model="taskDialogVisible" :task="editingTask" :project-id="projectId"
      @saved="onTaskSaved" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTaskStore } from '@/stores/task'
import TaskCard from '@/components/common/TaskCard.vue'
import TaskDialog from '@/components/common/TaskDialog.vue'
import PriorityTag from '@/components/common/PriorityTag.vue'

const route = useRoute()
const projectId = route.params.id
const taskStore = useTaskStore()

const boards = ref([])
const currentBoard = ref('')
const columns = ref([])
const drawerVisible = ref(false)
const currentTask = ref(null)
const taskDialogVisible = ref(false)
const editingTask = ref(null)
const showCreateTask = ref(false)
const showAddColumn = ref(false)

function statusType(status) {
  return { todo: 'info', in_progress: '', review: 'warning', done: 'success', blocked: 'danger' }[status] || 'info'
}

function showTaskDetail(task) {
  currentTask.value = task
  drawerVisible.value = true
}

function quickCreate(colId) {
  editingTask.value = null
  taskDialogVisible.value = true
}

function editTask(task) {
  editingTask.value = task
  taskDialogVisible.value = true
}

async function deleteTask(task) {
  await ElMessageBox.confirm('确定删除该任务？', '确认删除', { type: 'warning' })
  await taskStore.deleteTask(task.id)
  ElMessage.success('任务已删除')
}

function onTaskSaved() {
  taskDialogVisible.value = false
  loadBoard()
}

async function loadBoard() {
  // TODO: replace with real API: boardAPI.detail(currentBoard.value)
  columns.value = [
    { id: 'c1', name: '待办', wip_limit: 0, tasks: [
      { id: 't1', title: '设计数据库ER图', status: 'todo', priority: 'high', assignee: { username: '张三' }, due_date: '2026-05-07' },
      { id: 't2', title: '编写API文档', status: 'todo', priority: 'medium', assignee: { username: '李四' }, due_date: '2026-05-10' }
    ]},
    { id: 'c2', name: '进行中', wip_limit: 5, tasks: [
      { id: 't3', title: '前端页面开发', status: 'in_progress', priority: 'high', assignee: { username: '王五' }, due_date: '2026-05-12' }
    ]},
    { id: 'c3', name: '审核', wip_limit: 3, tasks: [] },
    { id: 'c4', name: '已完成', wip_limit: 0, tasks: [
      { id: 't4', title: '需求分析', status: 'done', priority: 'high', assignee: { username: '张三' }, due_date: '2026-04-30' }
    ]}
  ]
}

onMounted(loadBoard)
</script>

<style scoped lang="scss">
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.board-columns { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 16px; min-height: calc(100vh - 200px); }
.board-column {
  min-width: 280px; max-width: 320px; flex-shrink: 0;
  background: #f2f3f5; border-radius: 8px; padding: 12px;
}
.column-header {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: 8px; margin-bottom: 8px; border-bottom: 2px solid #dcdfe6;
  &.wip-exceeded { border-bottom-color: #F56C6C; }
}
.column-body { display: flex; flex-direction: column; gap: 8px; }
.add-task-btn { width: 100%; }
</style>
