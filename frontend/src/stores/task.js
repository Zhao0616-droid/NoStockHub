import { defineStore } from 'pinia'
import { ref } from 'vue'
import { taskAPI } from '@/api'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const currentTask = ref(null)
  const filters = ref({ status: '', priority: '', assignee_id: '', project_id: '', search: '' })

  async function fetchTasks(params = {}) {
    const res = await taskAPI.list({ ...filters.value, ...params })
    tasks.value = res.results || res
    return res
  }

  async function fetchTask(id) {
    const res = await taskAPI.detail(id)
    currentTask.value = res
    return res
  }

  async function createTask(data) {
    const res = await taskAPI.create(data)
    tasks.value.unshift(res)
    return res
  }

  async function updateTask(id, data) {
    const res = await taskAPI.update(id, data)
    if (currentTask.value?.id === id) currentTask.value = res
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
  }

  return { tasks, currentTask, filters, fetchTasks, fetchTask, createTask, updateTask, updateStatus, deleteTask }
})
