import request from './request'

// 认证
export const authAPI = {
  login: (data) => request.post('/auth/login/', data),
  register: (data) => request.post('/auth/register/', data),
  refreshToken: (data) => request.post('/auth/token/refresh/', data),
  profile: () => request.get('/auth/profile/'),
  updateProfile: (data) => request.put('/auth/profile/', data),
  changePassword: (data) => request.post('/auth/change-password/', data),
  enableTwoFactor: () => request.post('/auth/enable-two-factor/'),
  disableTwoFactor: () => request.post('/auth/disable-two-factor/'),
  verifyTwoFactor: (data) => request.post('/auth/verify-two-factor/', data),
}

// 项目
export const projectAPI = {
  list: (params) => request.get('/projects/', { params }),
  detail: (id) => request.get(`/projects/${id}/`),
  create: (data) => request.post('/projects/', data),
  update: (id, data) => request.put(`/projects/${id}/`, data),
  delete: (id) => request.delete(`/projects/${id}/`),
  members: (id) => request.get(`/projects/${id}/members/`),
  addMember: (id, data) => request.post(`/projects/${id}/members/`, data),
  removeMember: (id, memberId) => request.delete(`/projects/${id}/members/${memberId}/`),
  milestones: (id) => request.get(`/projects/${id}/milestones/`),
  createMilestone: (id, data) => request.post(`/projects/${id}/milestones/`, data),
  gantt: (id) => request.get(`/projects/${id}/gantt/`),
  activity: (id, params) => request.get(`/projects/${id}/activity/`, { params }),
  templates: () => request.get('/projects/templates/'),
}

// 任务
export const taskAPI = {
  list: (params) => request.get('/tasks/', { params }),
  detail: (id) => request.get(`/tasks/${id}/`),
  create: (data) => request.post('/tasks/', data),
  update: (id, data) => request.put(`/tasks/${id}/`, data),
  delete: (id) => request.delete(`/tasks/${id}/`),
  updateStatus: (id, status) => request.patch(`/tasks/${id}/status/`, { status }),
  dependencies: (id) => request.get(`/tasks/${id}/dependencies/`),
  addDependency: (id, data) => request.post(`/tasks/${id}/dependencies/`, data),
  removeDependency: (id, depId) => request.delete(`/tasks/${id}/dependencies/${depId}/`),
  comments: (id, params) => request.get(`/tasks/${id}/comments/`, { params }),
  addComment: (id, data) => request.post(`/tasks/${id}/comments/`, data),
  attachments: (id) => request.get(`/tasks/${id}/attachments/`),
  uploadAttachment: (id, file) => {
    const fd = new FormData(); fd.append('file', file)
    return request.post(`/tasks/${id}/attachments/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

// 看板
export const boardAPI = {
  list: (params) => request.get('/boards/', { params }),
  detail: (id) => request.get(`/boards/${id}/`),
  create: (data) => request.post('/boards/', data),
  delete: (id) => request.delete(`/boards/${id}/`),
  columns: (id) => request.get(`/boards/${id}/columns/`),
  addColumn: (id, data) => request.post(`/boards/${id}/columns/`, data),
  updateColumn: (id, colId, data) => request.put(`/boards/${id}/columns/${colId}/`, data),
  deleteColumn: (id, colId) => request.delete(`/boards/${id}/columns/${colId}/`),
  moveTask: (id, data) => request.post(`/boards/${id}/move-task/`, data),
}

// 冲刺
export const sprintAPI = {
  list: (params) => request.get('/sprints/', { params }),
  detail: (id) => request.get(`/sprints/${id}/`),
  create: (data) => request.post('/sprints/', data),
  update: (id, data) => request.put(`/sprints/${id}/`, data),
  delete: (id) => request.delete(`/sprints/${id}/`),
  start: (id) => request.post(`/sprints/${id}/start/`),
  complete: (id) => request.post(`/sprints/${id}/complete/`),
  addTask: (id, data) => request.post(`/sprints/${id}/tasks/`, data),
  removeTask: (id, taskId) => request.delete(`/sprints/${id}/tasks/${taskId}/`),
  listTasks: (id) => request.get(`/sprints/${id}/tasks/`),
  burndown: (id) => request.get(`/sprints/${id}/burndown/`),
}

// 工时
export const worklogAPI = {
  list: (params) => request.get('/worklogs/', { params }),
  create: (data) => request.post('/worklogs/', data),
  update: (id, data) => request.put(`/worklogs/${id}/`, data),
  delete: (id) => request.delete(`/worklogs/${id}/`),
  summary: (params) => request.get('/worklogs/summary/', { params }),
}

// 通知
export const notificationAPI = {
  list: (params) => request.get('/notifications/', { params }),
  markRead: (id) => request.post(`/notifications/${id}/read/`),
  markAllRead: () => request.post('/notifications/read-all/'),
  unreadCount: () => request.get('/notifications/unread-count/'),
  getNotificationPreferences: () => Promise.resolve({
    task_assigned: true, status_change: true, comment_mention: true, email_notification: false
  }),
  updateNotificationPreferences: (data) => Promise.resolve(data),
}

// 报表
export const reportAPI = {
  list: (params) => request.get('/reports/', { params }),
  generate: (data) => request.post('/reports/', data),
  detail: (id) => request.get(`/reports/${id}/`),
  download: (id) => request.get(`/reports/${id}/download/`, { responseType: 'blob' }),
}

// 文件
export const fileAPI = {
  upload: (file, taskId, projectId) => {
    const fd = new FormData(); fd.append('file', file)
    if (taskId) fd.append('task_id', taskId)
    if (projectId) fd.append('project_id', projectId)
    return request.post('/files/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  download: (id) => request.get(`/files/${id}/`, { responseType: 'blob' }),
  delete: (id) => request.delete(`/files/${id}/`),
}

// 仪表盘
export const dashboardAPI = {
  summary: () => request.get('/dashboard/'),
}
