<script setup>
import { onMounted, onUnmounted } from 'vue'
import ToastNotifications from './components/ToastNotifications.vue'
import { useAuthStore } from './stores/auth'
import { useReportsStore } from './stores/reports'
import { useNotifStore } from './stores/notifications'

const auth    = useAuthStore()
const reports = useReportsStore()
const notif   = useNotifStore()

let pollInterval = null
let prevStats    = null

async function pollStats() {
  if (!auth.user) return
  try {
    await reports.fetchStats()
    const s = reports.stats
    if (prevStats !== null) {
      if ((s.new || 0) > (prevStats.new || 0)) {
        const diff = (s.new || 0) - (prevStats.new || 0)
        notif.info(`تم استلام ${diff} بلاغ جديد`)
      }
      if (auth.user.role === 'conseiller') {
        const prevNeedsAppt = (prevStats.in_progress || 0)
        const currNeedsAppt = (s.in_progress || 0)
        if (currNeedsAppt > prevNeedsAppt) {
          notif.info('تم تعيين ملف جديد لك')
        }
      }
    }
    prevStats = { ...s }
  } catch { /* silent */ }
}

onMounted(() => {
  if (auth.user) {
    pollStats()
    pollInterval = setInterval(pollStats, 30000)
  }
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <RouterView />
  <ToastNotifications />
</template>
