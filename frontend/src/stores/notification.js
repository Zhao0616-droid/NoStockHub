import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)

  async function fetchNotifications() {
    // TODO: replace with real API call
    // const res = await notificationAPI.list()
    // notifications.value = res.results
    // unreadCount.value = res.unread_count
  }

  function incrementUnread() { unreadCount.value++ }

  return { notifications, unreadCount, fetchNotifications, incrementUnread }
})
