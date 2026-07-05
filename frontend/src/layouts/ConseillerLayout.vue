<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useReportsStore } from '../stores/reports'
import { useRouter } from 'vue-router'
import api from '../api'

const auth    = useAuthStore()
const store   = useReportsStore()
const router  = useRouter()
const profile = ref(null)

onMounted(async () => {
  store.fetchStats()
  try {
    const { data } = await api.get('/counselors/me/')
    profile.value = data
  } catch { /* silent */ }
})

function logout() { auth.logout(); router.push('/') }
</script>

<template>
  <div class="layout">
    <aside class="sidebar">

      <!-- Brand -->
      <div class="sidebar-logo">🛡️ SafeSchool</div>

      <!-- Profile avatar -->
      <RouterLink to="/conseiller/profile" class="profile-block">
        <div class="avatar-wrap">
          <img v-if="profile?.photo_url" :src="profile.photo_url" alt="صورة" class="avatar-img" />
          <div v-else class="avatar-placeholder">
            {{ (profile?.name || auth.user?.first_name || '?')[0].toUpperCase() }}
          </div>
          <span class="avatar-online"></span>
        </div>
        <div class="profile-info">
          <div class="profile-name">{{ auth.user?.first_name || profile?.name || auth.user?.username }}</div>
          <div v-if="auth.user?.last_name" class="profile-lastname">{{ auth.user.last_name }}</div>
          <div class="profile-role">{{ profile?.gender === 'female' ? 'مستشارة' : 'مستشار' }}</div>
        </div>
      </RouterLink>

      <div class="divider"></div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <RouterLink to="/conseiller/dashboard">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          لوحة القيادة
        </RouterLink>
        <RouterLink to="/conseiller/reports">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          ملفاتي
          <span v-if="store.stats.needs_appt > 0" class="badge">{{ store.stats.needs_appt }}</span>
        </RouterLink>
        <RouterLink to="/conseiller/session-reports">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          تقارير الجلسات
        </RouterLink>
        <RouterLink to="/conseiller/profile">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          ملفي الشخصي
        </RouterLink>
      </nav>

      <button class="logout-btn" @click="logout">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        تسجيل الخروج
      </button>
    </aside>

    <main class="main-content"><RouterView /></main>
  </div>
</template>

<style scoped>
.layout { display:flex; min-height:100vh; }

/* ── Sidebar ── */
.sidebar {
  width:240px;
  background:linear-gradient(180deg,#0f172a 0%,#1e3a5f 60%,#1d4ed8 100%);
  display:flex; flex-direction:column;
  padding:20px 12px;
  position:fixed; right:0; top:0; bottom:0;
  z-index:100;
}

.sidebar-logo {
  color:white; font-size:1.05rem; font-weight:900;
  padding:8px 12px; margin-bottom:20px;
  letter-spacing:0.02em;
}

/* ── Profile block ── */
.profile-block {
  display:flex; align-items:center; gap:11px;
  padding:10px 12px; border-radius:14px;
  text-decoration:none;
  background:rgba(255,255,255,0.1);
  transition:background 0.2s;
  margin-bottom:4px;
}
.profile-block:hover { background:rgba(255,255,255,0.18); }

.avatar-wrap { position:relative; flex-shrink:0; }

.avatar-img {
  width:46px; height:46px; border-radius:50%;
  object-fit:cover;
  border:2.5px solid rgba(255,255,255,0.5);
}
.avatar-placeholder {
  width:46px; height:46px; border-radius:50%;
  background:rgba(255,255,255,0.25);
  color:white; font-size:1.2rem; font-weight:900;
  display:flex; align-items:center; justify-content:center;
  border:2.5px solid rgba(255,255,255,0.4);
}
.avatar-online {
  position:absolute; bottom:1px; left:1px;
  width:11px; height:11px; border-radius:50%;
  background:#4ade80;
  border:2px solid #1d4ed8;
}

.profile-info { flex:1; min-width:0; }
.profile-name { font-size:0.875rem; font-weight:800; color:white; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.profile-lastname { font-size:0.8rem; font-weight:700; color:rgba(255,255,255,0.85); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.profile-role { font-size:0.72rem; color:rgba(255,255,255,0.65); margin-top:1px; }

.divider {
  height:1px; background:rgba(255,255,255,0.12);
  margin:14px 4px;
}

/* ── Nav ── */
.sidebar-nav { display:flex; flex-direction:column; gap:2px; flex:1; }
.sidebar-nav a {
  color:rgba(255,255,255,0.72);
  padding:10px 12px; border-radius:10px;
  font-size:0.875rem; font-weight:600;
  transition:all 0.2s;
  display:flex; align-items:center; gap:9px;
  text-decoration:none;
}
.sidebar-nav a:hover,
.sidebar-nav a.router-link-active {
  background:rgba(255,255,255,0.15);
  color:white;
}
.sidebar-nav a svg { flex-shrink:0; opacity:0.8; }

.badge {
  margin-right:auto;
  background:#ef4444; color:white;
  font-size:0.68rem; font-weight:900;
  padding:2px 7px; border-radius:20px;
  min-width:20px; text-align:center;
}

/* ── Logout ── */
.logout-btn {
  display:flex; align-items:center; gap:9px;
  background:rgba(255,255,255,0.07);
  color:rgba(255,255,255,0.65);
  border:none; padding:10px 12px;
  border-radius:10px; font-size:0.875rem; font-weight:600;
  text-align:right; width:100%; cursor:pointer;
  transition:all 0.2s; margin-top:8px;
}
.logout-btn:hover { background:#dc2626; color:white; }

.main-content { margin-right:240px; flex:1; padding:32px; }
</style>
