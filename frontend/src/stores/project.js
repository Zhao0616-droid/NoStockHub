import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectAPI } from '@/api'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const currentProject = ref(null)
  const loading = ref(false)

  async function fetchProjects(params = {}) {
    loading.value = true
    try {
      const res = await projectAPI.list(params)
      projects.value = res.results || res
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id) {
    const res = await projectAPI.detail(id)
    currentProject.value = res
    return res
  }

  async function createProject(data) {
    const res = await projectAPI.create(data)
    projects.value.unshift(res)
    return res
  }

  async function updateProject(id, data) {
    const res = await projectAPI.update(id, data)
    currentProject.value = res
    return res
  }

  async function deleteProject(id) {
    await projectAPI.delete(id)
    projects.value = projects.value.filter(p => p.id !== id)
  }

  return { projects, currentProject, loading, fetchProjects, fetchProject, createProject, updateProject, deleteProject }
})
