<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-icon class="collapse-btn" @click="$emit('toggleSidebar')">
        <Fold />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentProject">{{ currentProject.name }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="navbar-right">
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99">
        <el-icon class="bell-icon" @click="showNotifications"><Bell /></el-icon>
      </el-badge>
      <el-dropdown trigger="click" @command="handleCommand">
        <span class="user-info">
          <el-avatar :size="32" :src="user.avatar" />
          <span class="username">{{ user.username }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="settings">系统设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { Fold, Bell } from '@element-plus/icons-vue'

defineEmits(['toggleSidebar'])
const router = useRouter()
const auth = useAuthStore()
const notification = useNotificationStore()

const user = computed(() => auth.user || {})
const unreadCount = computed(() => notification.unreadCount)
const currentProject = computed(() => null)

function showNotifications() {
  notification.fetchNotifications()
}

function handleCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (cmd === 'settings') {
    router.push('/settings')
  } else if (cmd === 'profile') {
    router.push('/settings')
  }
}
</script>

<style scoped lang="scss">
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  height: 100%;
}
.navbar-left { display: flex; align-items: center; gap: 12px; }
.collapse-btn { cursor: pointer; font-size: 20px; color: #606266; }
.navbar-right { display: flex; align-items: center; gap: 20px; }
.bell-icon { font-size: 20px; cursor: pointer; color: #606266; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.username { font-size: 14px; color: #303133; }
</style>
