<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useReportsStore } from '../stores/reports'
import { useRouter } from 'vue-router'
import api from '../api'

const auth   = useAuthStore()
const store  = useReportsStore()
const router = useRouter()

onMounted(async () => {
  store.fetchStats()
  try {
    const { data } = await api.get('/auth/me/')
    auth.updateUser(data)
  } catch { /* silent */ }
})

function logout() { auth.logout(); router.push('/') }

function initials() {
  const u = auth.user
  if (!u) return '?'
  if (u.first_name && u.last_name) return (u.first_name[0] + u.last_name[0]).toUpperCase()
  if (u.first_name) return u.first_name[0].toUpperCase()
  return u.username[0].toUpperCase()
}

</script>

<template>
  <div class="layout">
    <aside class="sidebar">

      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-shield">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <span>SafeSchool</span>
      </div>

      <!-- Profile block -->
      <RouterLink to="/directeur/settings" class="profile-block">
        <div class="avatar-wrap">
          <img v-if="auth.user?.photo_url" :src="auth.user.photo_url" alt="صورة" class="avatar-img" />
          <div v-else class="avatar-placeholder">{{ initials() }}</div>
          <span class="avatar-online"></span>
        </div>
        <div class="profile-info">
          <div class="profile-name">{{ auth.user?.first_name }}</div>
          <div v-if="auth.user?.last_name" class="profile-lastname">{{ auth.user.last_name }}</div>
          <div class="profile-role">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            مدير
          </div>
        </div>
      </RouterLink>

      <div class="divider"></div>

      <nav class="sidebar-nav">

        <div class="nav-group-label">عام</div>
        <RouterLink to="/directeur/dashboard">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          لوحة القيادة
        </RouterLink>

        <div class="nav-group-label">البلاغات</div>
        <RouterLink to="/directeur/reports">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          البلاغات
          <span v-if="store.stats.new > 0" class="badge">{{ store.stats.new }}</span>
        </RouterLink>
        <RouterLink to="/directeur/appointments">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          المواعيد
        </RouterLink>
        <RouterLink to="/directeur/session-reports">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          تقارير الجلسات
        </RouterLink>

        <div class="nav-group-label">المستخدمون</div>
        <RouterLink to="/directeur/counselors">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          المستشارون
        </RouterLink>
        <RouterLink to="/directeur/students">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
            <path d="M6 12v5c3 3 9 3 12 0v-5"/>
          </svg>
          الطلاب
          <span v-if="store.stats.pending > 0" class="badge">{{ store.stats.pending }}</span>
        </RouterLink>

        <div class="nav-group-label">النظام</div>
        <RouterLink to="/directeur/settings">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          الإعدادات
        </RouterLink>

      </nav>

      <button class="logout-btn" @click="logout">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        تسجيل الخروج
      </button>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.sidebar {
  width: 230px; flex-shrink: 0;
  background: linear-gradient(180deg, #0f172a 0%, #1e3a5f 60%, #1d4ed8 100%);
  display: flex; flex-direction: column;
  padding: 16px 10px;
  position: fixed; right: 0; top: 0; bottom: 0; z-index: 100;
  overflow-y: auto;
}

/* scrollbar */
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }

/* Logo */
.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 10px; margin-bottom: 16px;
}
.logo-shield {
  width: 34px; height: 34px; border-radius: 9px;
  background: rgba(255,255,255,0.15);
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(255,255,255,0.25); flex-shrink: 0;
}
.sidebar-logo span { color: white; font-size: 1rem; font-weight: 900; letter-spacing: -0.3px; }

/* Profile */
.profile-block {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; border-radius: 12px;
  text-decoration: none;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  transition: background 0.2s; margin-bottom: 4px;
}
.profile-block:hover { background: rgba(255,255,255,0.14); }
.avatar-wrap { position: relative; flex-shrink: 0; }
.avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.4); }
.avatar-placeholder {
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(255,255,255,0.2); color: white;
  font-size: 1rem; font-weight: 900;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid rgba(255,255,255,0.3);
}
.avatar-online {
  position: absolute; bottom: 1px; left: 1px;
  width: 10px; height: 10px; border-radius: 50%;
  background: #4ade80; border: 2px solid #1d4ed8;
}
.profile-info { flex: 1; min-width: 0; }
.profile-name { font-size: 0.82rem; font-weight: 800; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.profile-lastname { font-size: 0.78rem; font-weight: 700; color: rgba(255,255,255,0.85); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.profile-role { display: flex; align-items: center; gap: 4px; font-size: 0.68rem; color: rgba(255,255,255,0.55); margin-top: 1px; }

.divider { height: 1px; background: rgba(255,255,255,0.1); margin: 12px 4px; }

/* Nav groups */
.sidebar-nav { display: flex; flex-direction: column; gap: 1px; flex: 1; }

.nav-group-label {
  font-size: 0.62rem; font-weight: 800;
  color: rgba(255,255,255,0.35);
  text-transform: uppercase; letter-spacing: 0.07em;
  padding: 10px 10px 4px;
}

.sidebar-nav a {
  color: rgba(255,255,255,0.65);
  padding: 9px 10px;
  border-radius: 9px;
  font-size: 0.82rem; font-weight: 600;
  transition: all 0.18s;
  display: flex; align-items: center; gap: 9px;
  text-decoration: none; position: relative;
}
.sidebar-nav a:hover { background: rgba(255,255,255,0.1); color: white; }
.sidebar-nav a.router-link-active {
  background: rgba(255,255,255,0.16);
  color: white;
}
.sidebar-nav a.router-link-active::before {
  content: '';
  position: absolute; right: 0; top: 50%;
  transform: translateY(-50%);
  width: 3px; height: 60%;
  background: white; border-radius: 3px 0 0 3px;
}
.sidebar-nav a svg { flex-shrink: 0; opacity: 0.75; }
.sidebar-nav a.router-link-active svg { opacity: 1; }

.badge {
  margin-right: auto;
  background: #ef4444; color: white;
  font-size: 0.65rem; font-weight: 900;
  padding: 2px 6px; border-radius: 20px;
  min-width: 18px; text-align: center;
}

/* Logout */
.logout-btn {
  display: flex; align-items: center; gap: 9px;
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.08);
  padding: 9px 10px; border-radius: 9px;
  font-size: 0.82rem; font-weight: 600;
  width: 100%; cursor: pointer;
  transition: all 0.2s; margin-top: 10px;
}
.logout-btn:hover { background: #dc2626; color: white; border-color: #dc2626; }

/* ── Main content ── */
.main-content { margin-right: 230px; flex: 1; padding: 28px 30px; background: #f1f5f9; min-height: 100vh; }
</style>
