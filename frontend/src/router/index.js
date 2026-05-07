import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/settings/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/dashboard/Index.vue')
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/pages/project/List.vue')
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/pages/project/Detail.vue')
      },
      {
        path: 'projects/:id/tasks',
        name: 'TaskList',
        component: () => import('@/pages/task/List.vue')
      },
      {
        path: 'projects/:id/board',
        name: 'Board',
        component: () => import('@/pages/task/Board.vue')
      },
      {
        path: 'projects/:id/gantt',
        name: 'Gantt',
        component: () => import('@/pages/gantt/Index.vue')
      },
      {
        path: 'projects/:id/sprints',
        name: 'Sprints',
        component: () => import('@/pages/sprint/Index.vue')
      },
      {
        path: 'projects/:id/reports',
        name: 'Reports',
        component: () => import('@/pages/report/Index.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/pages/settings/Index.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
