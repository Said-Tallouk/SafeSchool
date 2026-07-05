<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import api from '../api'
const auth   = useAuthStore()
const router = useRouter()

onMounted(async () => {
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

      <div class="sidebar-logo">🛡️ SafeSchool</div>

      <!-- Profile block -->
      <RouterLink to="/etudiant/profile" class="profile-block">
        <div class="avatar-wrap">
          <img v-if="auth.user?.photo_url" :src="auth.user.photo_url" class="avatar-photo" alt="صورة" />
          <div v-else class="avatar-placeholder">{{ initials() }}</div>
          <span class="avatar-online"></span>
        </div>
        <div class="profile-info">
          <div class="profile-name">{{ auth.user?.first_name }}</div>
          <div v-if="auth.user?.last_name" class="profile-lastname">{{ auth.user.last_name }}</div>
          <div class="profile-role">طالب</div>
        </div>
      </RouterLink>

      <div class="divider"></div>

      <nav class="sidebar-nav">
        <RouterLink to="/etudiant/dashboard">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          بلاغاتي
        </RouterLink>
        <RouterLink to="/etudiant/new-report">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
          بلاغ جديد
        </RouterLink>
        <RouterLink to="/etudiant/notifications">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          الإشعارات
        </RouterLink>
        <RouterLink to="/etudiant/profile">
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

.sidebar {
  width:240px;
  background:linear-gradient(180deg,#1e3a5f 0%,#1d4ed8 100%);
  display:flex; flex-direction:column;
  padding:20px 12px;
  position:fixed; right:0; top:0; bottom:0; z-index:100;
}

.sidebar-logo { color:white; font-size:1.05rem; font-weight:900; padding:8px 12px; margin-bottom:20px; }

.profile-block {
  display:flex; align-items:center; gap:11px;
  padding:10px 12px; border-radius:14px;
  text-decoration:none;
  background:rgba(255,255,255,0.1);
  transition:background 0.2s; margin-bottom:4px;
}
.profile-block:hover { background:rgba(255,255,255,0.18); }

.avatar-wrap { position:relative; flex-shrink:0; }
.avatar-photo {
  width:46px; height:46px; border-radius:50%;
  object-fit:cover;
  border:2.5px solid rgba(255,255,255,0.7);
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
  background:#4ade80; border:2px solid #1d4ed8;
}

.profile-info { flex:1; min-width:0; }
.profile-name { font-size:0.875rem; font-weight:800; color:white; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.profile-lastname { font-size:0.8rem; font-weight:700; color:rgba(255,255,255,0.85); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.profile-role { font-size:0.72rem; color:rgba(255,255,255,0.65); margin-top:1px; }

.divider { height:1px; background:rgba(255,255,255,0.12); margin:14px 4px; }

.sidebar-nav { display:flex; flex-direction:column; gap:2px; flex:1; }
.sidebar-nav a {
  color:rgba(255,255,255,0.72); padding:10px 12px;
  border-radius:10px; font-size:0.875rem; font-weight:600;
  transition:all 0.2s; display:flex; align-items:center; gap:9px; text-decoration:none;
}
.sidebar-nav a:hover,
.sidebar-nav a.router-link-active { background:rgba(255,255,255,0.15); color:white; }

.logout-btn {
  display:flex; align-items:center; gap:9px;
  background:rgba(255,255,255,0.07); color:rgba(255,255,255,0.65);
  border:none; padding:10px 12px; border-radius:10px;
  font-size:0.875rem; font-weight:600; text-align:right;
  width:100%; cursor:pointer; transition:all 0.2s; margin-top:8px;
}
.logout-btn:hover { background:#dc2626; color:white; }

.main-content { margin-right:240px; flex:1; padding:32px; }
</style>
