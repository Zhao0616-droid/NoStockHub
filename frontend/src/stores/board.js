import { defineStore } from 'pinia'
import { ref } from 'vue'
import { boardAPI } from '@/api'

// --------------- mock data (后端未就绪时的兜底) ---------------
let _mockBoardId = 0
let _mockColId = 0
function _uid(prefix) { return `${prefix}_${Date.now()}_${++_mockBoardId}` }

const _mockBoards = [
  { id: 'b1', name: '团队看板', type: 'team', project_id: '' },
  { id: 'b2', name: '版本1.0看板', type: 'version', project_id: '' }
]

function _mockColumns() {
  return [
    { id: 'c1', name: '待办', order: 0, wip_limit: 0, tasks: [
      { id: 't1', title: '设计数据库ER图', status: 'todo', priority: 'high', type: 'task', assignee: { username: '张三' }, due_date: '2026-05-07', description: '完成核心表结构设计' },
      { id: 't2', title: '编写API接口文档', status: 'todo', priority: 'medium', type: 'task', assignee: { username: '李四' }, due_date: '2026-05-10', description: '' }
    ]},
    { id: 'c2', name: '进行中', order: 1, wip_limit: 5, tasks: [
      { id: 't3', title: '前端页面开发', status: 'in_progress', priority: 'high', type: 'task', assignee: { username: '王五' }, due_date: '2026-05-12', description: '使用 Vue3 + Element Plus' },
      { id: 't5', title: '用户认证模块', status: 'in_progress', priority: 'urgent', type: 'epic', assignee: { username: '张三' }, due_date: '2026-05-08', description: 'JWT + 双因素认证' }
    ]},
    { id: 'c3', name: '审核中', order: 2, wip_limit: 3, tasks: [
      { id: 't6', title: '代码审查', status: 'review', priority: 'medium', type: 'task', assignee: { username: '李四' }, due_date: '2026-05-09', description: '' }
    ]},
    { id: 'c4', name: '已完成', order: 3, wip_limit: 0, tasks: [
      { id: 't4', title: '需求分析', status: 'done', priority: 'high', type: 'task', assignee: { username: '张三' }, due_date: '2026-04-30', description: '完成需求文档评审' },
      { id: 't7', title: '技术选型', status: 'done', priority: 'medium', type: 'task', assignee: { username: '王五' }, due_date: '2026-04-28', description: '' }
    ]}
  ]
}

function _getMockBoard(id) {
  return _mockBoards.find(b => b.id === id) || _mockBoards[0]
}

export const useBoardStore = defineStore('board', () => {
  // --------------- state ---------------
  const boards = ref([])
  const currentBoard = ref(null)
  const columns = ref([])
  const loading = ref(false)
  const useMock = ref(false) // 后端不可用时自动切换 mock

  // --------------- boards ---------------
  async function fetchBoards(projectId) {
    loading.value = true
    try {
      const res = await boardAPI.list({ project_id: projectId })
      boards.value = res.results || res
      useMock.value = false
    } catch {
      // 后端不可用，使用 mock 数据
      useMock.value = true
      boards.value = _mockBoards.map(b => ({ ...b, project_id: projectId }))
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
      useMock.value = false
    } catch {
      useMock.value = true
      currentBoard.value = _getMockBoard(boardId)
      columns.value = _mockColumns()
    } finally {
      loading.value = false
    }
    return currentBoard.value
  }

  async function createBoard(data) {
    if (!useMock.value) {
      const res = await boardAPI.create(data)
      boards.value.push(res)
      return res
    }
    // mock 模式
    const board = { id: _uid('b'), ...data, created_at: new Date().toISOString() }
    boards.value.push(board)
    return board
  }

  async function deleteBoard(boardId) {
    if (!useMock.value) {
      await boardAPI.delete(boardId)
    }
    boards.value = boards.value.filter(b => b.id !== boardId)
    if (currentBoard.value?.id === boardId) {
      currentBoard.value = null
      columns.value = []
    }
  }

  // --------------- columns ---------------
  async function addColumn(boardId, data) {
    if (!useMock.value) {
      const res = await boardAPI.addColumn(boardId, data)
      columns.value.push({ ...res, tasks: [] })
      return res
    }
    const col = { id: _uid('col'), ...data, order: columns.value.length, tasks: [] }
    columns.value.push(col)
    return col
  }

  async function updateColumn(boardId, colId, data) {
    if (!useMock.value) {
      const res = await boardAPI.updateColumn(boardId, colId, data)
      const idx = columns.value.findIndex(c => c.id === colId)
      if (idx !== -1) columns.value[idx] = { ...columns.value[idx], ...res }
      return res
    }
    const idx = columns.value.findIndex(c => c.id === colId)
    if (idx !== -1) Object.assign(columns.value[idx], data)
    return columns.value[idx]
  }

  async function deleteColumn(boardId, colId) {
    if (!useMock.value) {
      await boardAPI.deleteColumn(boardId, colId)
    }
    columns.value = columns.value.filter(c => c.id !== colId)
  }

  // --------------- task move ---------------
  async function moveTask(boardId, { taskId, fromColumnId, toColumnId, order }) {
    const fromCol = columns.value.find(c => c.id === fromColumnId)
    const toCol = columns.value.find(c => c.id === toColumnId)
    const task = fromCol?.tasks?.find(t => t.id === taskId)

    // 乐观更新：先从源列移除，再插入目标列
    if (fromCol && task) {
      fromCol.tasks = fromCol.tasks.filter(t => t.id !== taskId)
    }
    if (toCol && task) {
      const updatedTask = { ...task, status: toCol.name }
      if (toCol.tasks) {
        toCol.tasks.push(updatedTask)
      } else {
        toCol.tasks = [updatedTask]
      }
    }

    if (!useMock.value) {
      try {
        await boardAPI.moveTask(boardId, { task_id: taskId, from_column_id: fromColumnId, to_column_id: toColumnId, order })
      } catch {
        await fetchBoard(boardId) // 回滚
      }
    }
    // mock 模式下乐观更新即最终态
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

  function updateTaskInColumn(taskId, data) {
    for (const col of columns.value) {
      if (col.tasks) {
        const idx = col.tasks.findIndex(t => t.id === taskId)
        if (idx !== -1) {
          col.tasks[idx] = { ...col.tasks[idx], ...data }
          return
        }
      }
    }
  }

  return {
    boards, currentBoard, columns, loading, useMock,
    fetchBoards, fetchBoard, createBoard, deleteBoard,
    addColumn, updateColumn, deleteColumn,
    moveTask, addTaskToColumn, removeTaskFromColumn, updateTaskInColumn
  }
})
