import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notificationAPI } from '@/api'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)

  async function fetchNotifications() {
    try {
      const res = await notificationAPI.list({ unread: 'true' })
      notifications.value = res.results || res
      // fetch unread count separately
      const countRes = await notificationAPI.list()
      unreadCount.value = countRes.results ? countRes.results.filter(n => !n.is_read).length : 0
    } catch {
      // silent fail for notifications
    }
  }

  async function markRead(id) {
    try {
      await notificationAPI.markRead(id)
      const n = notifications.value.find(n => n.id === id)
      if (n) n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch { /* ignore */ }
  }

  async function markAllRead() {
    try {
      await notificationAPI.markAllRead()
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    } catch { /* ignore */ }
  }

  function incrementUnread() { unreadCount.value++ }

  return { notifications, unreadCount, fetchNotifications, markRead, markAllRead, incrementUnread }
})
