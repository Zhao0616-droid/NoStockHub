import { defineStore } from 'pinia'
import { ref } from 'vue'
import { boardAPI, taskAPI } from '@/api'

// 看板列名 → 任务状态码
const COLUMN_STATUS_MAP = {
  '待办': 'todo',
  '进行中': 'in_progress',
  '审核中': 'review',
  '已完成': 'done',
}

export const useBoardStore = defineStore('board', () => {
  const boards = ref([])
  const currentBoard = ref(null)
  const columns = ref([])
  const loading = ref(false)

  // --------------- boards ---------------
  async function fetchBoards(projectId) {
    loading.value = true
    try {
      const res = await boardAPI.list({ project_id: projectId })
      boards.value = res.results || res
    } finally {
      loading.value = false
    }
    return boards.value
  }

  async function fetchBoard(boardId) {
    loading.value = true
    try {
      const res = await boardAPI.detail(boardId)
      currentBoard.value = res
      const cols = await boardAPI.columns(boardId)
      columns.value = (cols.results || cols).map(c => ({ ...c, tasks: c.tasks || [] }))
    } finally {
      loading.value = false
    }
    return currentBoard.value
  }

  async function createBoard(data) {
    const res = await boardAPI.create(data)
    boards.value.push(res)
    return res
  }

  async function deleteBoard(boardId) {
    await boardAPI.delete(boardId)
    boards.value = boards.value.filter(b => b.id !== boardId)
    if (currentBoard.value?.id === boardId) {
      currentBoard.value = null
      columns.value = []
    }
  }

  // --------------- columns ---------------
  async function addColumn(boardId, data) {
    const res = await boardAPI.addColumn(boardId, data)
    columns.value.push({ ...res, tasks: [] })
    return res
  }

  async function updateColumn(boardId, colId, data) {
    const res = await boardAPI.updateColumn(boardId, colId, data)
    const idx = columns.value.findIndex(c => c.id === colId)
    if (idx !== -1) columns.value[idx] = { ...columns.value[idx], ...res }
    return res
  }

  async function deleteColumn(boardId, colId) {
    await boardAPI.deleteColumn(boardId, colId)
    columns.value = columns.value.filter(c => c.id !== colId)
  }

  // --------------- task move ---------------
  async function moveTask(boardId, { taskId, fromColumnId, toColumnId, order }) {
    const fromCol = columns.value.find(c => c.id === fromColumnId)
    const toCol = columns.value.find(c => c.id === toColumnId)
    const task = fromCol?.tasks?.find(t => t.id === taskId)
    const statusCode = COLUMN_STATUS_MAP[toCol?.name] || 'todo'

    // 乐观更新
    if (fromCol && task) {
      fromCol.tasks = fromCol.tasks.filter(t => t.id !== taskId)
    }
    if (toCol && task) {
      const updatedTask = { ...task, status: statusCode }
      if (toCol.tasks) {
        toCol.tasks.push(updatedTask)
      } else {
        toCol.tasks = [updatedTask]
      }
    }

    try {
      await boardAPI.moveTask(boardId, { task_id: taskId, target_column_id: toColumnId, order })
      await taskAPI.updateStatus(taskId, statusCode)
    } catch {
      await fetchBoard(boardId) // 回滚
    }
  }

  // --------------- column task helpers ---------------
  function addTaskToColumn(columnId, task) {
    const col = columns.value.find(c => c.id === columnId)
    if (col) {
      if (!col.tasks) col.tasks = []
      col.tasks.push(task)
    }
  }

  function removeTaskFromColumn(taskId) {
    for (const col of columns.value) {
      if (col.tasks) {
        col.tasks = col.tasks.filter(t => t.id !== taskId)
      }
    }
  }

  return {
    boards, currentBoard, columns, loading,
    fetchBoards, fetchBoard, createBoard, deleteBoard,
    addColumn, updateColumn, deleteColumn,
    moveTask, addTaskToColumn, removeTaskFromColumn,
  }
})
