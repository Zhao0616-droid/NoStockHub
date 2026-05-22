import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { taskAPI } from '@/api'

// --------------- mock data ---------------
let _mockTaskId = 0
function _tid() { return `t_${Date.now()}_${++_mockTaskId}` }

function _mockTasks(projectId) {
  return [
    { id: 't1', title: '设计数据库ER图', description: '完成核心业务表的ER关系设计，包括用户、项目、任务、看板等模块', type: 'task', priority: 'high', status: 'in_progress', assignee: { id: 'u1', username: '张三' }, reporter: { id: 'u1', username: '张三' }, due_date: '2026-05-07', start_date: '2026-05-01', estimated_hours: 8, project_id: projectId, created_at: '2026-05-01T08:00:00Z' },
    { id: 't2', title: '编写API接口文档', description: '使用Swagger/OpenAPI规范编写后端API文档', type: 'task', priority: 'medium', status: 'todo', assignee: { id: 'u2', username: '李四' }, reporter: { id: 'u1', username: '张三' }, due_date: '2026-05-10', start_date: '', estimated_hours: 4, project_id: projectId, created_at: '2026-05-02T09:00:00Z' },
    { id: 't3', title: '代码审查', description: '对前端Vue组件和后端API代码进行交叉审查', type: 'task', priority: 'low', status: 'todo', assignee: { id: 'u3', username: '王五' }, reporter: { id: 'u2', username: '李四' }, due_date: '2026-05-12', start_date: '', estimated_hours: 2, project_id: projectId, created_at: '2026-05-03T10:00:00Z' },
    { id: 't4', title: '部署测试环境', description: '配置Docker Compose测试环境并验证各服务连通性', type: 'task', priority: 'high', status: 'blocked', assignee: { id: 'u1', username: '张三' }, reporter: { id: 'u1', username: '张三' }, due_date: '2026-05-15', start_date: '2026-05-05', estimated_hours: 6, project_id: projectId, created_at: '2026-05-04T11:00:00Z' },
    { id: 't5', title: '用户认证模块开发', description: '实现JWT登录、注册、Token刷新、双因素认证', type: 'epic', priority: 'urgent', status: 'in_progress', assignee: { id: 'u1', username: '张三' }, reporter: { id: 'u3', username: '王五' }, due_date: '2026-05-08', start_date: '2026-05-03', estimated_hours: 16, project_id: projectId, created_at: '2026-05-02T08:00:00Z' },
    { id: 't6', title: '修复登录页样式错乱', description: '在Chrome 120+下登录卡片居中偏移', type: 'bug', priority: 'medium', status: 'review', assignee: { id: 'u2', username: '李四' }, reporter: { id: 'u3', username: '王五' }, due_date: '2026-05-09', start_date: '', estimated_hours: 1, project_id: projectId, created_at: '2026-05-05T14:00:00Z' },
    { id: 't7', title: '编写单元测试', description: '为核心模块编写pytest单元测试，覆盖率≥80%', type: 'task', priority: 'medium', status: 'todo', assignee: { id: 'u3', username: '王五' }, reporter: { id: 'u2', username: '李四' }, due_date: '2026-05-18', start_date: '', estimated_hours: 12, project_id: projectId, created_at: '2026-05-06T09:00:00Z' },
    { id: 't8', title: '需求文档评审', description: '组织项目干系人评审需求规格说明书', type: 'task', priority: 'high', status: 'done', assignee: { id: 'u1', username: '张三' }, reporter: { id: 'u1', username: '张三' }, due_date: '2026-04-30', start_date: '2026-04-25', estimated_hours: 3, project_id: projectId, created_at: '2026-04-24T09:00:00Z' }
  ]
}

export const useTaskStore = defineStore('task', () => {
  // --------------- state ---------------
  const tasks = ref([])
  const currentTask = ref(null)
  const total = ref(0)
  const loading = ref(false)
  const useMock = ref(true)
  const filters = ref({
    status: [],
    priority: '',
    assignee_id: '',
    project_id: '',
    search: '',
    type: ''
  })
  const page = ref(1)
  const pageSize = ref(10)
  const sortField = ref('')
  const sortOrder = ref('asc')

  // --------------- computed ---------------
  const filteredTasks = computed(() => {
    let list = [...tasks.value]

    // 搜索
    if (filters.value.search) {
      const q = filters.value.search.toLowerCase()
      list = list.filter(t =>
        t.title.toLowerCase().includes(q) ||
        (t.description || '').toLowerCase().includes(q) ||
        (t.assignee?.username || '').toLowerCase().includes(q)
      )
    }

    // 状态筛选（多选）
    if (filters.value.status && filters.value.status.length > 0) {
      list = list.filter(t => filters.value.status.includes(t.status))
    }

    // 优先级筛选
    if (filters.value.priority) {
      list = list.filter(t => t.priority === filters.value.priority)
    }

    // 负责人筛选
    if (filters.value.assignee_id) {
      list = list.filter(t => t.assignee?.id === filters.value.assignee_id)
    }

    // 类型筛选
    if (filters.value.type) {
      list = list.filter(t => t.type === filters.value.type)
    }

    // 项目筛选 (API returns 'project', mock uses 'project_id')
    if (filters.value.project_id) {
      list = list.filter(t => (t.project_id || t.project) === filters.value.project_id)
    }

    // 排序
    if (sortField.value) {
      list.sort((a, b) => {
        const va = a[sortField.value] ?? ''
        const vb = b[sortField.value] ?? ''
        const cmp = typeof va === 'string' ? va.localeCompare(vb) : vb - va
        return sortOrder.value === 'desc' ? -cmp : cmp
      })
    }

    total.value = list.length
    const start = (page.value - 1) * pageSize.value
    return list.slice(start, start + pageSize.value)
  })

  // --------------- actions ---------------
  async function fetchTasks(params = {}) {
    loading.value = true
    try {
      const merged = { ...filters.value, ...params, page: page.value, page_size: pageSize.value }
      if (sortField.value) {
        merged.ordering = sortOrder.value === 'desc' ? `-${sortField.value}` : sortField.value
      }
      const res = await taskAPI.list(merged)
      tasks.value = res.results || res
      total.value = res.count || tasks.value.length
      useMock.value = false
    } catch {
      useMock.value = true
      const projectId = filters.value.project_id || params.project_id || ''
      tasks.value = _mockTasks(projectId)
    } finally {
      loading.value = false
    }
    return tasks.value
  }

  async function fetchTask(id) {
    loading.value = true
    try {
      const res = await taskAPI.detail(id)
      currentTask.value = res
      useMock.value = false
    } catch {
      useMock.value = true
      currentTask.value = tasks.value.find(t => t.id === id) || null
    } finally {
      loading.value = false
    }
    return currentTask.value
  }

  async function createTask(data) {
    const res = await taskAPI.create(data)
    tasks.value.unshift(res)
    return res
  }

  async function updateTask(id, data) {
    const res = await taskAPI.update(id, data)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx !== -1) tasks.value[idx] = { ...tasks.value[idx], ...res }
    if (currentTask.value?.id === id) currentTask.value = { ...currentTask.value, ...res }
    return res
  }

  async function updateStatus(id, status) {
    await taskAPI.updateStatus(id, status)
    const t = tasks.value.find(t => t.id === id)
    if (t) t.status = status
    if (currentTask.value?.id === id) currentTask.value.status = status
  }

  async function deleteTask(id) {
    await taskAPI.delete(id)
    tasks.value = tasks.value.filter(t => t.id !== id)
    if (currentTask.value?.id === id) currentTask.value = null
  }

  // --------------- filter helpers ---------------
  function setFilters(newFilters) {
    Object.assign(filters.value, newFilters)
    page.value = 1
  }

  function resetFilters() {
    filters.value = { status: [], priority: '', assignee_id: '', project_id: filters.value.project_id, search: '', type: '' }
    page.value = 1
  }

  function setPage(p) { page.value = p }
  function setPageSize(s) { pageSize.value = s; page.value = 1 }
  function setSort(field) {
    if (sortField.value === field) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortField.value = field
      sortOrder.value = 'asc'
    }
  }

  return {
    tasks, currentTask, total, loading, useMock,
    filters, page, pageSize, sortField, sortOrder,
    filteredTasks,
    fetchTasks, fetchTask, createTask, updateTask, updateStatus, deleteTask,
    setFilters, resetFilters, setPage, setPageSize, setSort
  }
})
