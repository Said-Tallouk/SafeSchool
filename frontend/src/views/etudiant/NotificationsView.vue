<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const notifications = ref([])
const loading = ref(false)
const markingAll = ref(false)

onMounted(fetchNotifications)

async function fetchNotifications() {
  loading.value = true
  try {
    const { data } = await api.get('/notifications/')
    notifications.value = data
  } finally { loading.value = false }
}

async function markRead(n) {
  if (n.is_read) return
  await api.post(`/notifications/${n.id}/read/`)
  n.is_read = true
}

async function markAllRead() {
  markingAll.value = true
  try {
    await api.post('/notifications/read-all/')
    notifications.value.forEach(n => n.is_read = true)
  } finally { markingAll.value = false }
}

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

function formatDate(d) {
  if (!d) return '—'
  const date = new Date(d)
  if (isNaN(date)) return '—'
  const diff = Date.now() - date.getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return 'الآن'
  if (m < 60) return `منذ ${m} دقيقة`
  const h = Math.floor(m / 60)
  if (h < 24) return `منذ ${h} ساعة`
  return date.toLocaleDateString('ar-MA', { day: '2-digit', month: 'short', year: 'numeric' })
}

const typeConfig = {
  appointment: { label: 'موعد',    bg: '#eff6ff', color: '#1d4ed8', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2z' },
  update:      { label: 'تحديث',   bg: '#f0fdf4', color: '#16a34a', icon: 'M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z' },
  info:        { label: 'معلومة',  bg: '#fff7ed', color: '#c2410c', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z' },
}
</script>

<template>
  <div class="notif-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>الإشعارات</h2>
        <p class="subtitle">
          {{ unreadCount > 0 ? `${unreadCount} إشعار غير مقروء` : 'تمت قراءة الكل' }}
        </p>
      </div>
      <button v-if="unreadCount > 0" class="btn-mark-all" :disabled="markingAll" @click="markAllRead">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20 6 9 17l-5-5"/></svg>
        {{ markingAll ? 'جارٍ...' : 'تحديد الكل كمقروء' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="empty-state">
      <svg class="spin" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
      جارٍ التحميل...
    </div>

    <!-- Empty -->
    <div v-else-if="notifications.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.2">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span>لا توجد إشعارات حتى الآن.</span>
    </div>

    <!-- List -->
    <div v-else class="notif-list">
      <div
        v-for="n in notifications"
        :key="n.id"
        :class="['notif-card', !n.is_read && 'unread']"
        @click="markRead(n)"
      >
        <div class="notif-icon" :style="`background:${typeConfig[n.type]?.bg || '#f1f5f9'};color:${typeConfig[n.type]?.color || '#475569'}`">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path :d="typeConfig[n.type]?.icon || 'M12 22c1.1 0 2-.9 2-2H10c0 1.1.9 2 2 2zm6-6V11c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5S10.5 3.17 10.5 4v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z'" />
          </svg>
        </div>
        <div class="notif-body">
          <div class="notif-msg">{{ n.message }}</div>
          <div class="notif-meta">
            <span class="notif-type" :style="`color:${typeConfig[n.type]?.color || '#475569'}`">
              {{ typeConfig[n.type]?.label || n.type }}
            </span>
            <span class="notif-date">{{ formatDate(n.created_at) }}</span>
          </div>
        </div>
        <div v-if="!n.is_read" class="unread-dot"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notif-page { max-width:720px; margin:0 auto; }

.page-header {
  display:flex; align-items:flex-start; justify-content:space-between;
  gap:12px; flex-wrap:wrap; margin-bottom:28px;
}
.page-header h2 { font-size:1.5rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; font-size:0.9rem; }

.btn-mark-all {
  display:inline-flex; align-items:center; gap:7px; padding:9px 18px;
  background:#f1f5f9; color:#1d4ed8; border:none; border-radius:12px;
  font-size:0.85rem; font-weight:700; cursor:pointer; transition:background 0.2s; font-family:inherit; white-space:nowrap;
}
.btn-mark-all:hover:not(:disabled) { background:#dbeafe; }
.btn-mark-all:disabled { opacity:0.6; cursor:default; }

.empty-state {
  display:flex; flex-direction:column; align-items:center; gap:14px;
  padding:64px 24px; color:#9ca3af; background:white; border-radius:18px;
  font-size:0.95rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
}
@keyframes spin { to { transform:rotate(360deg); } }
.spin { animation:spin 0.9s linear infinite; }

.notif-list { display:flex; flex-direction:column; gap:10px; }

.notif-card {
  display:flex; align-items:flex-start; gap:14px; padding:16px 20px;
  background:white; border-radius:16px; box-shadow:0 1px 4px rgba(0,0,0,0.06);
  cursor:pointer; transition:box-shadow 0.2s, transform 0.15s; position:relative;
  border:1.5px solid transparent;
}
.notif-card:hover { box-shadow:0 4px 16px rgba(0,0,0,0.1); transform:translateY(-1px); }
.notif-card.unread { border-color:#bfdbfe; background:#f8fbff; }

.notif-icon {
  width:40px; height:40px; border-radius:12px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
}

.notif-body { flex:1; min-width:0; }
.notif-msg { font-size:0.9rem; color:#1e293b; line-height:1.6; font-weight:500; }
.notif-meta { display:flex; align-items:center; gap:10px; margin-top:6px; flex-wrap:wrap; }
.notif-type { font-size:0.75rem; font-weight:700; }
.notif-date { font-size:0.75rem; color:#94a3b8; }

.unread-dot {
  width:9px; height:9px; border-radius:50%; background:#1d4ed8; flex-shrink:0; margin-top:6px;
}
</style>
