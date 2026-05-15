import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/settings/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/two-factor',
    name: 'TwoFactor',
    component: () => import('@/pages/auth/TwoFactor.vue'),
    meta: { requiresAuth: false, title: '双因素认证' }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/dashboard/Index.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/pages/project/List.vue'),
        meta: { title: '项目列表' }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/pages/project/Detail.vue'),
        meta: { title: '项目详情' }
      },
      {
        path: 'projects/:id/overview',
        name: 'ProjectOverview',
        component: () => import('@/pages/project/Overview.vue'),
        meta: { title: '项目概览' }
      },
      {
        path: 'projects/:id/tasks',
        name: 'TaskList',
        component: () => import('@/pages/task/List.vue'),
        meta: { title: '任务列表' }
      },
      {
        path: 'projects/:id/board',
        name: 'Board',
        component: () => import('@/pages/task/Board.vue'),
        meta: { title: '任务看板' }
      },
      {
        path: 'projects/:id/gantt',
        name: 'Gantt',
        component: () => import('@/pages/gantt/Index.vue'),
        meta: { title: '甘特图' }
      },
      {
        path: 'projects/:id/sprints',
        name: 'Sprints',
        component: () => import('@/pages/sprint/Index.vue'),
        meta: { title: '冲刺管理' }
      },
      {
        path: 'projects/:id/reports',
        name: 'Reports',
        component: () => import('@/pages/report/Index.vue'),
        meta: { title: '报表' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/pages/settings/Index.vue'),
        meta: { title: '系统设置' }
      },
      {
        path: 'demo/charts',
        name: 'ChartDemo',
        component: () => import('@/pages/demo/Charts.vue'),
        meta: { title: '图表示例' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/error/404.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const token = localStorage.getItem('access_token')
  
  // 更新页面标题
  document.title = `${to.meta.title || '软件项目管理平台'} - NoStackHub`
  
  // 检查是否需要认证
  if (to.meta.requiresAuth === false) {
    // 不需要认证的页面
    if (token && to.path === '/login') {
      // 已登录且尝试访问登录页，重定向到仪表盘
      next('/dashboard')
    } else {
      next()
    }
  } else {
    // 需要认证的页面
    if (!token) {
      // 未登录，重定向到登录页
      next('/login')
    } else if (auth.twoFactorRequired) {
      // 需要双因素认证
      if (to.path === '/two-factor') {
        next()
      } else {
        next('/two-factor')
      }
    } else {
      // 已认证，允许访问
      next()
    }
  }
})

router.afterEach((to, from) => {
  // 可以在这里添加页面加载完成的处理
})

export default router
