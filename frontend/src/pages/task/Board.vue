<template>
  <div class="board-page" v-loading="boardStore.loading">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>任务看板</h2>
      <div class="header-actions">
        <el-select
          v-model="selectedBoardId"
          placeholder="选择看板"
          style="width: 180px"
          @change="onBoardChange"
        >
          <el-option
            v-for="b in boardStore.boards"
            :key="b.id"
            :label="b.name"
            :value="b.id"
          />
        </el-select>
        <el-button @click="showAddBoard = true">+ 看板</el-button>
        <el-button @click="showAddColumn = true" :disabled="!selectedBoardId">+ 列</el-button>
        <el-button type="danger" :disabled="!selectedBoardId" @click="handleDeleteBoard">删除看板</el-button>
        <el-button type="primary" @click="openCreateTask()">+ 任务</el-button>
      </div>
    </div>

    <!-- 看板列区域 -->
    <div class="board-columns" v-if="boardStore.columns.length > 0">
      <div
        v-for="col in boardStore.columns"
        :key="col.id"
        class="board-column"
        :class="{ 'drag-over': dragOverColumnId === col.id }"
        @dragover.prevent="onDragOver(col.id)"
        @dragleave="onDragLeave(col.id)"
        @drop="onDrop(col.id)"
      >
        <!-- 列头部 -->
        <div class="column-header" :class="{ 'wip-exceeded': isWipExceeded(col) }">
          <div class="column-title">
            <span>{{ col.name }}</span>
            <el-tag
              size="small"
              :type="isWipExceeded(col) ? 'danger' : 'info'"
              class="column-count"
            >
              {{ col.tasks?.length || 0 }}
              <template v-if="col.wip_limit > 0">/ {{ col.wip_limit }}</template>
            </el-tag>
          </div>
          <el-dropdown trigger="click" @command="(cmd) => onColumnCommand(cmd, col)">
            <el-button text size="small" :icon="MoreFilled" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit">编辑列名</el-dropdown-item>
                <el-dropdown-item command="wip">设置 WIP 限制</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除列</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- 列内容 -->
        <div class="column-body">
          <div
            v-for="task in col.tasks"
            :key="task.id"
            class="task-card-wrapper"
            draggable="true"
            @dragstart="onDragStart($event, task, col.id)"
            @dragend="onDragEnd"
          >
            <TaskCard :task="task" @click="showTaskDetail(task)" />
          </div>

          <el-button
            text
            class="add-task-btn"
            @click="openCreateTask(col.id)"
          >
            + 添加任务
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空看板提示 -->
    <el-empty
      v-else-if="!boardStore.loading && selectedBoardId"
      description="该看板暂无列，请点击「+ 列」创建"
    />
    <el-empty
      v-else-if="!boardStore.loading && !selectedBoardId"
      description="请选择一个看板或创建新看板"
    >
      <el-button type="primary" @click="showAddBoard = true">创建看板</el-button>
    </el-empty>

    <!-- 任务详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="currentTask?.title || '任务详情'"
      size="480px"
    >
      <template v-if="currentTask">
        <el-descriptions :column="1" border style="margin-bottom: 16px">
          <el-descriptions-item label="状态">
            <StatusTag :status="currentTask.status" />
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <PriorityTag :priority="currentTask.priority" />
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ currentTask.assignee?.username || '未分配' }}
          </el-descriptions-item>
          <el-descriptions-item label="截止日期">
            {{ currentTask.due_date || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ typeLabel(currentTask.type) }}
          </el-descriptions-item>
          <el-descriptions-item label="预估工时">
            {{ currentTask.estimated_hours ? currentTask.estimated_hours + 'h' : '未设置' }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="task-description" v-if="currentTask.description">
          <h4>描述</h4>
          <p>{{ currentTask.description }}</p>
        </div>
        <div class="drawer-actions">
          <el-button type="primary" @click="editTask(currentTask)">编辑</el-button>
          <el-button type="danger" @click="handleDeleteTask(currentTask)">删除</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 创建/编辑任务对话框 -->
    <TaskDialog
      v-model="taskDialogVisible"
      :task="editingTask"
      :project-id="projectId"
      @saved="onTaskSaved"
    />

    <!-- 创建看板对话框 -->
    <el-dialog v-model="showAddBoard" title="创建看板" width="400px">
      <el-form :model="newBoardForm" label-position="top">
        <el-form-item label="看板名称" required>
          <el-input v-model="newBoardForm.name" placeholder="输入看板名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="newBoardForm.type" style="width: 100%">
            <el-option label="团队看板" value="team" />
            <el-option label="版本看板" value="version" />
            <el-option label="子项目看板" value="sub_project" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddBoard = false">取消</el-button>
        <el-button type="primary" :loading="creatingBoard" @click="handleCreateBoard">创建</el-button>
      </template>
    </el-dialog>

    <!-- 添加列对话框 -->
    <el-dialog v-model="showAddColumn" title="添加列" width="400px">
      <el-form :model="newColumnForm" label-position="top">
        <el-form-item label="列名称" required>
          <el-input v-model="newColumnForm.name" placeholder="如：待办、进行中、已完成" />
        </el-form-item>
        <el-form-item label="WIP 限制（0=无限制）">
          <el-input-number v-model="newColumnForm.wip_limit" :min="0" :step="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddColumn = false">取消</el-button>
        <el-button type="primary" :loading="addingColumn" @click="handleAddColumn">添加</el-button>
      </template>
    </el-dialog>

    <!-- 编辑列对话框 -->
    <el-dialog v-model="showEditColumn" title="编辑列" width="400px">
      <el-form :model="editColumnForm" label-position="top">
        <el-form-item label="列名称" required>
          <el-input v-model="editColumnForm.name" placeholder="列名称" />
        </el-form-item>
        <el-form-item label="WIP 限制（0=无限制）">
          <el-input-number v-model="editColumnForm.wip_limit" :min="0" :step="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditColumn = false">取消</el-button>
        <el-button type="primary" :loading="savingColumn" @click="handleUpdateColumn">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled } from '@element-plus/icons-vue'
import { useBoardStore } from '@/stores/board'
import { useTaskStore } from '@/stores/task'
import TaskCard from '@/components/common/TaskCard.vue'
import TaskDialog from '@/components/common/TaskDialog.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import PriorityTag from '@/components/common/PriorityTag.vue'

const route = useRoute()
const projectId = route.params.id
const boardStore = useBoardStore()
const taskStore = useTaskStore()

// --------------- 看板选择 ---------------
const selectedBoardId = ref('')
const showAddBoard = ref(false)
const creatingBoard = ref(false)
const newBoardForm = ref({ name: '', type: 'team' })

async function onBoardChange(boardId) {
  if (!boardId) return
  await boardStore.fetchBoard(boardId)
}

async function handleDeleteBoard() {
  if (!selectedBoardId.value) return
  const board = boardStore.boards.find(b => b.id === selectedBoardId.value)
  try {
    await ElMessageBox.confirm(
      `确定删除看板「${board?.name || ''}」？看板中的列也会被删除。`,
      '确认删除',
      { type: 'warning' }
    )
    await boardStore.deleteBoard(selectedBoardId.value)
    selectedBoardId.value = ''
    ElMessage.success('看板已删除')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function handleCreateBoard() {
  if (!newBoardForm.value.name) {
    ElMessage.warning('请输入看板名称')
    return
  }
  creatingBoard.value = true
  try {
    const board = await boardStore.createBoard({
      name: newBoardForm.value.name,
      type: newBoardForm.value.type,
      project_id: projectId
    })
    selectedBoardId.value = board.id
    showAddBoard.value = false
    newBoardForm.value = { name: '', type: 'team' }
    ElMessage.success('看板创建成功')
    await boardStore.fetchBoard(board.id)
  } catch {
    ElMessage.error('创建看板失败')
  } finally {
    creatingBoard.value = false
  }
}

// --------------- 列管理 ---------------
const showAddColumn = ref(false)
const addingColumn = ref(false)
const newColumnForm = ref({ name: '', wip_limit: 0 })

const showEditColumn = ref(false)
const savingColumn = ref(false)
const editingColumn = ref(null)
const editColumnForm = ref({ name: '', wip_limit: 0 })

async function handleAddColumn() {
  if (!newColumnForm.value.name) {
    ElMessage.warning('请输入列名称')
    return
  }
  addingColumn.value = true
  try {
    await boardStore.addColumn(selectedBoardId.value, {
      name: newColumnForm.value.name,
      wip_limit: newColumnForm.value.wip_limit
    })
    showAddColumn.value = false
    newColumnForm.value = { name: '', wip_limit: 0 }
    ElMessage.success('列添加成功')
  } catch {
    ElMessage.error('添加列失败')
  } finally {
    addingColumn.value = false
  }
}

function onColumnCommand(cmd, col) {
  switch (cmd) {
    case 'edit':
    case 'wip':
      editingColumn.value = col
      editColumnForm.value = { name: col.name, wip_limit: col.wip_limit || 0 }
      showEditColumn.value = true
      break
    case 'delete':
      handleDeleteColumn(col)
      break
  }
}

async function handleUpdateColumn() {
  if (!editColumnForm.value.name) {
    ElMessage.warning('请输入列名称')
    return
  }
  savingColumn.value = true
  try {
    await boardStore.updateColumn(selectedBoardId.value, editingColumn.value.id, editColumnForm.value)
    showEditColumn.value = false
    ElMessage.success('列更新成功')
  } catch {
    ElMessage.error('更新列失败')
  } finally {
    savingColumn.value = false
  }
}

async function handleDeleteColumn(col) {
  try {
    await ElMessageBox.confirm(
      `确定删除列「${col.name}」？列中的任务不会被删除。`,
      '确认删除',
      { type: 'warning' }
    )
    await boardStore.deleteColumn(selectedBoardId.value, col.id)
    ElMessage.success('列已删除')
  } catch {
    // 取消操作
  }
}

// --------------- WIP 检查 ---------------
function isWipExceeded(col) {
  return col.wip_limit > 0 && (col.tasks?.length || 0) > col.wip_limit
}

// --------------- 拖拽 ---------------
const dragOverColumnId = ref(null)
let dragTask = null
let dragFromColumnId = null

function onDragStart(event, task, columnId) {
  dragTask = task
  dragFromColumnId = columnId
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', task.id)
  event.target.closest('.task-card-wrapper')?.classList.add('dragging')
}

function onDragEnd(event) {
  event.target.closest('.task-card-wrapper')?.classList.remove('dragging')
  dragTask = null
  dragFromColumnId = null
  dragOverColumnId.value = null
}

function onDragOver(columnId) {
  if (dragFromColumnId !== columnId) {
    dragOverColumnId.value = columnId
  }
}

function onDragLeave(columnId) {
  if (dragOverColumnId.value === columnId) {
    dragOverColumnId.value = null
  }
}

async function onDrop(toColumnId) {
  dragOverColumnId.value = null
  if (!dragTask || !dragFromColumnId) return
  if (dragFromColumnId === toColumnId) return

  await boardStore.moveTask(selectedBoardId.value, {
    taskId: dragTask.id,
    fromColumnId: dragFromColumnId,
    toColumnId: toColumnId,
    order: 0
  })
  dragTask = null
  dragFromColumnId = null
}

// --------------- 任务详情抽屉 ---------------
const drawerVisible = ref(false)
const currentTask = ref(null)

function showTaskDetail(task) {
  currentTask.value = task
  drawerVisible.value = true
}

// --------------- 任务创建/编辑 ---------------
const taskDialogVisible = ref(false)
const editingTask = ref(null)
const targetColumnId = ref(null)

function openCreateTask(columnId) {
  editingTask.value = null
  targetColumnId.value = columnId || null
  taskDialogVisible.value = true
}

function editTask(task) {
  editingTask.value = task
  drawerVisible.value = false
  taskDialogVisible.value = true
}

async function handleDeleteTask(task) {
  try {
    await ElMessageBox.confirm('确定删除该任务？', '确认删除', { type: 'warning' })
    await taskStore.deleteTask(task.id)
    boardStore.removeTaskFromColumn(task.id)
    drawerVisible.value = false
    currentTask.value = null
    ElMessage.success('任务已删除')
  } catch {
    // 取消操作
  }
}

async function onTaskSaved(task) {
  taskDialogVisible.value = false
  if (selectedBoardId.value) {
    // If we have a target column, add the new task to it
    if (task && targetColumnId.value) {
      try {
        await boardAPI.moveTask(selectedBoardId.value, {
          task_id: task.id,
          target_column_id: targetColumnId.value,
          order: 0
        })
      } catch { /* task still exists, just not on board yet */ }
      targetColumnId.value = null
    }
    boardStore.fetchBoard(selectedBoardId.value)
  }
}

// --------------- 工具函数 ---------------
function typeLabel(type) {
  return { task: '任务', bug: '缺陷', epic: '史诗' }[type] || type || '任务'
}

// --------------- 初始化 ---------------
onMounted(async () => {
  await boardStore.fetchBoards(projectId)
  if (boardStore.boards.length > 0) {
    selectedBoardId.value = boardStore.boards[0].id
    await boardStore.fetchBoard(selectedBoardId.value)
  }
})
</script>

<style scoped lang="scss">
.board-page {
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
    color: var(--el-text-color-primary);
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

// ---------- 看板列容器 ----------
.board-columns {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 16px;
  flex: 1;
  min-height: calc(100vh - 200px);
  align-items: flex-start;

  &::-webkit-scrollbar {
    height: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: #c0c4cc;
    border-radius: 3px;
  }
}

// ---------- 列 ----------
.board-column {
  min-width: 280px;
  max-width: 320px;
  flex-shrink: 0;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  max-height: 100%;
  transition: background 0.2s, box-shadow 0.2s;

  &.drag-over {
    background: var(--el-color-primary-light-9);
    box-shadow: inset 0 0 0 2px var(--el-color-primary);
  }
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 2px solid var(--el-border-color);
  flex-shrink: 0;

  &.wip-exceeded {
    border-bottom-color: var(--el-color-danger);
  }
}

.column-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.column-count {
  font-size: 11px;
}

// ---------- 列内容 ----------
.column-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--el-border-color-darker);
    border-radius: 2px;
  }
}

.task-card-wrapper {
  cursor: grab;

  &.dragging {
    opacity: 0.5;
  }

  &:active {
    cursor: grabbing;
  }
}

.add-task-btn {
  width: 100%;
  border: 1px dashed var(--el-border-color) !important;
  color: var(--el-text-color-secondary);
  border-radius: 6px;
  padding: 6px;

  &:hover {
    border-color: var(--el-color-primary) !important;
    color: var(--el-color-primary);
  }
}

// ---------- 任务详情抽屉 ----------
.task-description {
  background: var(--el-fill-color-light);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;

  h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: var(--el-text-color-primary);
  }

  p {
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.6;
    white-space: pre-wrap;
  }
}

.drawer-actions {
  display: flex;
  gap: 8px;
}
</style>
