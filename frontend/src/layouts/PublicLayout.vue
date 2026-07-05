<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'

const auth   = useAuthStore()
const router = useRouter()
const route  = useRoute()

// Mobile menu
const menuOpen    = ref(false)
const userDropdown = ref(false)
const scrolled    = ref(true)

function toggleMenu() { menuOpen.value = !menuOpen.value; userDropdown.value = false }
function toggleDropdown() { userDropdown.value = !userDropdown.value; menuOpen.value = false }
function closeAll() { menuOpen.value = false; userDropdown.value = false }

// Navbar background on scroll — always visible, becomes glassy on scroll
function onScroll() { scrolled.value = true }
onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

// Close dropdown when clicking outside
function onClickOutside(e) {
  if (!e.target.closest('.user-menu')) userDropdown.value = false
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

function goToDashboard() {
  closeAll()
  if (auth.user?.role === 'directeur')       router.push('/directeur/dashboard')
  else if (auth.user?.role === 'conseiller') router.push('/conseiller/dashboard')
  else                                        router.push('/etudiant/dashboard')
}

function logout() {
  auth.logout()
  closeAll()
  router.push('/')
}

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  if (u.first_name && u.last_name) return (u.first_name[0] + u.last_name[0]).toUpperCase()
  if (u.first_name) return u.first_name[0].toUpperCase()
  return u.username[0].toUpperCase()
})

const displayName = computed(() => {
  const u = auth.user
  if (!u) return ''
  return (u.first_name + ' ' + (u.last_name || '')).trim() || u.username
})

const roleLabel = computed(() => {
  const roles = { directeur: 'مدير', conseiller: 'مستشار', etudiant: 'طالب' }
  return roles[auth.user?.role] || ''
})

// Annonces panel
const annonces    = ref([])
const panelOpen   = ref(false)
const newCount    = ref(0)

onMounted(async () => {
  try {
    const { data } = await api.get('/annonces/')
    annonces.value = data.filter(a => a.publie)
    newCount.value = annonces.value.length
  } catch { /* silent */ }
})

function openPanel()  { panelOpen.value = true;  newCount.value = 0 }
function closePanel() { panelOpen.value = false }

const CAT_COLORS = { info:'#3b82f6', urgence:'#ef4444', evenement:'#7c3aed', alerte:'#f59e0b' }
const CAT_BG     = { info:'#dbeafe', urgence:'#fee2e2', evenement:'#ede9fe', alerte:'#fef3c7' }
const CAT_ICONS  = { urgence:'🚨', evenement:'📅', alerte:'⚠️', info:'📢' }

const navLinks = [
  { to: '/',             label: 'الرئيسية' },
  { to: '/about',        label: 'من نحن'   },
  { to: '/activites',    label: 'الأنشطة'  },
  { to: '/evenements',   label: 'الفعاليات'},
  { to: '/professeurs',  label: 'الأساتذة' },
  { to: '/contact',      label: 'اتصل بنا' },
]

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<template>
  <div class="site">

    <!-- ── Navbar ── -->
    <header :class="['navbar', scrolled && 'navbar-scrolled']">
      <div class="nav-inner">

        <!-- Logo -->
        <RouterLink to="/" class="nav-logo" @click="closeAll">
          <div class="logo-shield">
            <svg width="18" height="18" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <span>SafeSchool</span>
        </RouterLink>

        <!-- Desktop nav links -->
        <nav class="nav-links">
          <RouterLink v-for="l in navLinks" :key="l.to" :to="l.to"
                      :class="['nav-link', isActive(l.to) && 'active']"
                      @click="closeAll">
            {{ l.label }}
          </RouterLink>
        </nav>

        <!-- Right zone -->
        <div class="nav-right">

          <!-- NOT logged in -->
          <RouterLink v-if="!auth.isLoggedIn" to="/login" class="btn-login" @click="closeAll">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>
            </svg>
            تسجيل الدخول
          </RouterLink>

          <!-- Logged in — user dropdown -->
          <div v-else class="user-menu">
            <button class="user-btn" @click.stop="toggleDropdown">
              <div class="user-avatar" v-if="auth.user?.photo_url">
                <img :src="auth.user.photo_url" alt="Photo" />
              </div>
              <div class="user-avatar initials-av" v-else>{{ initials }}</div>
              <div class="user-info">
                <span class="user-name">{{ displayName }}</span>
                <span class="user-role">{{ roleLabel }}</span>
              </div>
              <svg :class="['chevron', userDropdown && 'open']" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>
            </button>

            <!-- Dropdown -->
            <transition name="dropdown">
              <div v-if="userDropdown" class="dropdown-menu">
                <div class="dropdown-header">
                  <div class="drop-av" v-if="auth.user?.photo_url">
                    <img :src="auth.user.photo_url" alt="" />
                  </div>
                  <div class="drop-av drop-initials" v-else>{{ initials }}</div>
                  <div>
                    <div class="drop-name">{{ displayName }}</div>
                    <div class="drop-role">{{ roleLabel }}</div>
                  </div>
                </div>
                <div class="dropdown-divider"></div>
                <button class="drop-item" @click="goToDashboard">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                  فضائي
                </button>
                <div class="dropdown-divider"></div>
                <button class="drop-item danger" @click="logout">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                  تسجيل الخروج
                </button>
              </div>
            </transition>
          </div>

          <!-- Hamburger -->
          <button class="hamburger" @click.stop="toggleMenu" :class="{ open: menuOpen }">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <transition name="mobile-menu">
        <div v-if="menuOpen" class="mobile-nav">
          <RouterLink v-for="l in navLinks" :key="l.to" :to="l.to"
                      :class="['mob-link', isActive(l.to) && 'active']"
                      @click="closeAll">
            {{ l.label }}
          </RouterLink>
          <div class="mob-divider"></div>
          <template v-if="!auth.isLoggedIn">
            <RouterLink to="/login" class="mob-btn-login" @click="closeAll">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
              تسجيل الدخول
            </RouterLink>
            <RouterLink to="/register" class="mob-btn-register" @click="closeAll">
              إنشاء حساب طالب
            </RouterLink>
          </template>
          <template v-else>
            <div class="mob-user">
              <div class="mob-av" v-if="auth.user?.photo_url"><img :src="auth.user.photo_url" /></div>
              <div class="mob-av mob-initials" v-else>{{ initials }}</div>
              <div>
                <div class="mob-name">{{ displayName }}</div>
                <div class="mob-role">{{ roleLabel }}</div>
              </div>
            </div>
            <button class="mob-link" @click="goToDashboard">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              فضائي
            </button>
            <button class="mob-link danger" @click="logout">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/></svg>
              تسجيل الخروج
            </button>
          </template>
        </div>
      </transition>
    </header>

    <!-- ── Floating news button ── -->
    <div v-if="annonces.length" class="news-fab-wrap" :class="{ pulsing: newCount > 0 }">
      <div class="news-fab-label">
        <span class="fab-label-dot"></span>
        الأخبار
      </div>
      <button class="news-fab" @click="openPanel">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <span v-if="newCount > 0" class="news-badge">{{ newCount }}</span>
      </button>
    </div>

    <!-- ── News slide panel ── -->
    <transition name="panel-slide">
      <div v-if="panelOpen" class="news-panel">
        <div class="panel-header">
          <div class="panel-title">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            الأخبار والإعلانات
          </div>
          <button class="panel-close" @click="closePanel">
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="panel-body">
          <div v-for="a in annonces" :key="a.id" class="panel-item">
            <div class="pi-accent" :style="{ background: CAT_COLORS[a.categorie] || '#3b82f6' }"></div>
            <div class="pi-content">
              <div class="pi-meta">
                <span class="pi-cat" :style="{ color: CAT_COLORS[a.categorie] || '#3b82f6', background: CAT_BG[a.categorie] || '#eff6ff' }">
                  {{ CAT_ICONS[a.categorie] || '📢' }} {{ a.categorie }}
                </span>
              </div>
              <p class="pi-title">{{ a.titre }}</p>
              <p class="pi-text">{{ a.contenu }}</p>
            </div>
          </div>
        </div>
        <div class="panel-footer">
          <RouterLink to="/evenements" class="panel-link" @click="closePanel">
            ← عرض جميع الفعاليات
          </RouterLink>
        </div>
      </div>
    </transition>
    <!-- Overlay -->
    <div v-if="panelOpen" class="panel-overlay" @click="closePanel"></div>

    <!-- Page content -->
    <main class="site-main">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="logo-shield sm">
            <svg width="14" height="14" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <span>SafeSchool</span>
          <p>منصة الحماية المدرسية من التحرش</p>
        </div>
        <nav class="footer-links">
          <RouterLink v-for="l in navLinks" :key="l.to" :to="l.to">{{ l.label }}</RouterLink>
        </nav>
        <div class="footer-copy">© {{ new Date().getFullYear() }} SafeSchool — جميع الحقوق محفوظة</div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.site { display: flex; flex-direction: column; min-height: 100vh; }

/* ── Navbar ── */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 500;
  background: rgba(255,255,255,0.97);
  transition: background 0.35s, box-shadow 0.35s, backdrop-filter 0.35s;
}
.navbar-scrolled {
  background: rgba(255,255,255,0.97);
  backdrop-filter: blur(14px);
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
}
.nav-inner {
  max-width: 1200px; margin: 0 auto;
  display: flex; align-items: center; gap: 0;
  padding: 0 24px; height: 68px;
}

/* Logo */
.nav-logo {
  display: flex; align-items: center; gap: 10px;
  text-decoration: none; flex-shrink: 0; margin-left: 40px;
}
.logo-shield {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg,#1d4ed8,#0891b2);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 10px rgba(29,78,216,0.3);
}
.logo-shield.sm { width: 28px; height: 28px; border-radius: 7px; }
.nav-logo span { font-size: 1.1rem; font-weight: 900; color: #1e293b; }
.navbar:not(.navbar-scrolled) .nav-logo span { color: white; }

/* Desktop links */
.nav-links { display: flex; align-items: center; gap: 2px; flex: 1; }
.nav-link {
  padding: 8px 14px; border-radius: 8px;
  font-size: 0.875rem; font-weight: 600;
  color: rgba(255,255,255,0.85); text-decoration: none;
  transition: all 0.2s; position: relative;
}
.navbar-scrolled .nav-link { color: #475569; }
.nav-link:hover, .nav-link.active { color: white; background: rgba(255,255,255,0.15); }
.navbar-scrolled .nav-link:hover, .navbar-scrolled .nav-link.active { color: #1d4ed8; background: #eff6ff; }

/* Right zone */
.nav-right { display: flex; align-items: center; gap: 10px; margin-right: auto; }

/* Login button */
.btn-login {
  display: flex; align-items: center; gap: 7px;
  background: white; color: #1d4ed8;
  font-weight: 800; font-size: 0.85rem;
  padding: 9px 18px; border-radius: 10px;
  text-decoration: none; transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.btn-login:hover { background: #1d4ed8; color: white; box-shadow: 0 4px 14px rgba(29,78,216,0.35); }
.navbar-scrolled .btn-login { background: linear-gradient(135deg,#1d4ed8,#0891b2); color: white; }

/* User dropdown */
.user-menu { position: relative; }
.user-btn {
  display: flex; align-items: center; gap: 9px;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.3);
  border-radius: 12px; padding: 6px 12px 6px 6px;
  cursor: pointer; transition: all 0.2s;
}
.navbar-scrolled .user-btn { background: #f8fafc; border-color: #e2e8f0; }
.user-btn:hover { background: rgba(255,255,255,0.25); }
.navbar-scrolled .user-btn:hover { background: #f1f5f9; }
.user-avatar { width: 32px; height: 32px; border-radius: 50%; overflow: hidden; flex-shrink: 0; }
.user-avatar img { width: 100%; height: 100%; object-fit: cover; }
.initials-av { background: linear-gradient(135deg,#1d4ed8,#0891b2); display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 900; color: white; }
.user-info { display: flex; flex-direction: column; align-items: flex-start; }
.user-name { font-size: 0.8rem; font-weight: 800; color: white; line-height: 1.2; }
.user-role { font-size: 0.65rem; color: rgba(255,255,255,0.65); font-weight: 600; }
.navbar-scrolled .user-name { color: #1e293b; }
.navbar-scrolled .user-role { color: #94a3b8; }
.chevron { color: rgba(255,255,255,0.7); transition: transform 0.2s; }
.navbar-scrolled .chevron { color: #94a3b8; }
.chevron.open { transform: rotate(180deg); }

/* Dropdown */
.dropdown-menu {
  position: absolute; top: calc(100% + 10px); right: 0;
  background: white; border-radius: 14px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  border: 1px solid #f1f5f9;
  min-width: 220px; overflow: hidden;
  z-index: 600;
}
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.2s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-8px) scale(0.97); }

.dropdown-header { display: flex; align-items: center; gap: 11px; padding: 14px 16px; }
.drop-av { width: 38px; height: 38px; border-radius: 50%; overflow: hidden; flex-shrink: 0; }
.drop-av img { width: 100%; height: 100%; object-fit: cover; }
.drop-initials { background: linear-gradient(135deg,#1d4ed8,#0891b2); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 900; color: white; }
.drop-name { font-size: 0.85rem; font-weight: 800; color: #1e293b; }
.drop-role { font-size: 0.72rem; color: #94a3b8; font-weight: 600; }
.dropdown-divider { height: 1px; background: #f1f5f9; }
.drop-item {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 12px 16px; border: none; background: none;
  font-size: 0.85rem; font-weight: 600; color: #374151; cursor: pointer;
  transition: background 0.15s; text-align: right;
}
.drop-item:hover { background: #f8fafc; }
.drop-item.danger { color: #dc2626; }
.drop-item.danger:hover { background: #fef2f2; }

/* Hamburger */
.hamburger { display: none; flex-direction: column; gap: 5px; background: none; border: none; cursor: pointer; padding: 4px; }
.hamburger span { display: block; width: 22px; height: 2.5px; background: white; border-radius: 2px; transition: all 0.3s; }
.navbar-scrolled .hamburger span { background: #374151; }
.hamburger.open span:nth-child(1) { transform: translateY(7.5px) rotate(45deg); }
.hamburger.open span:nth-child(2) { opacity: 0; }
.hamburger.open span:nth-child(3) { transform: translateY(-7.5px) rotate(-45deg); }

/* Mobile nav */
.mobile-nav {
  background: white; border-top: 1px solid #f1f5f9;
  padding: 16px 20px; display: flex; flex-direction: column; gap: 4px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.mobile-menu-enter-active, .mobile-menu-leave-active { transition: all 0.25s ease; }
.mobile-menu-enter-from, .mobile-menu-leave-to { opacity: 0; transform: translateY(-10px); }

.mob-link {
  display: flex; align-items: center; gap: 9px;
  padding: 11px 12px; border-radius: 10px;
  font-size: 0.875rem; font-weight: 700; color: #374151;
  text-decoration: none; transition: background 0.15s;
  background: none; border: none; cursor: pointer; text-align: right; width: 100%;
}
.mob-link:hover { background: #f8fafc; }
.mob-link.active { color: #1d4ed8; background: #eff6ff; }
.mob-link.danger { color: #dc2626; }
.mob-divider { height: 1px; background: #f1f5f9; margin: 4px 0; }
.mob-btn-login { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; background: linear-gradient(135deg,#1d4ed8,#0891b2); color: white; font-weight: 800; font-size: 0.875rem; border-radius: 11px; text-decoration: none; margin-top: 4px; }
.mob-btn-register { display: flex; align-items: center; justify-content: center; padding: 11px; background: #f8fafc; border: 1.5px solid #e2e8f0; color: #1d4ed8; font-weight: 700; font-size: 0.875rem; border-radius: 11px; text-decoration: none; margin-top: 4px; }
.mob-user { display: flex; align-items: center; gap: 11px; padding: 12px; background: #f8fafc; border-radius: 11px; margin-bottom: 4px; }
.mob-av { width: 38px; height: 38px; border-radius: 50%; overflow: hidden; flex-shrink: 0; }
.mob-av img { width: 100%; height: 100%; object-fit: cover; }
.mob-initials { background: linear-gradient(135deg,#1d4ed8,#0891b2); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 900; color: white; }
.mob-name { font-size: 0.85rem; font-weight: 800; color: #1e293b; }
.mob-role { font-size: 0.72rem; color: #94a3b8; font-weight: 600; }

/* ── Floating news button ── */
.news-fab-wrap {
  position: fixed; bottom: 28px; right: 24px; z-index: 490;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.news-fab-wrap.pulsing { animation: fab-shake 2.5s ease-in-out infinite; }
@keyframes fab-shake {
  0%,100% { transform: translateX(0); }
  10%     { transform: translateX(-12px); }
  20%     { transform: translateX(12px); }
  30%     { transform: translateX(-10px); }
  40%     { transform: translateX(10px); }
  50%     { transform: translateX(-6px); }
  60%     { transform: translateX(6px); }
  70%     { transform: translateX(0); }
}
.news-fab-label {
  display: flex; align-items: center; gap: 6px;
  background: linear-gradient(135deg, #1d4ed8, #7c3aed);
  color: white; font-size: 0.72rem; font-weight: 800;
  letter-spacing: 0.06em; text-transform: uppercase;
  padding: 5px 14px; border-radius: 20px;
  box-shadow: 0 4px 16px rgba(29,78,216,0.4);
  white-space: nowrap;
}
.fab-label-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #fbbf24;
  box-shadow: 0 0 0 0 rgba(251,191,36,0.7);
  animation: dot-ping 1.4s ease-out infinite;
}
@keyframes dot-ping {
  0%  { box-shadow: 0 0 0 0 rgba(251,191,36,0.7); }
  70% { box-shadow: 0 0 0 7px rgba(251,191,36,0); }
  100%{ box-shadow: 0 0 0 0 rgba(251,191,36,0); }
}
.news-fab {
  width: 58px; height: 58px; border-radius: 50%;
  background: linear-gradient(135deg, #1d4ed8, #7c3aed);
  border: none; cursor: pointer; position: relative;
  display: flex; align-items: center; justify-content: center;
  color: white;
  box-shadow: 0 6px 24px rgba(29,78,216,0.45);
  transition: transform 0.2s, box-shadow 0.2s;
}
.news-fab:hover { transform: scale(1.1); box-shadow: 0 10px 32px rgba(29,78,216,0.55); }
.news-badge {
  position: absolute; top: -4px; right: -4px;
  background: #ef4444; color: white;
  font-size: 0.62rem; font-weight: 900;
  min-width: 20px; height: 20px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid white; padding: 0 4px;
}

/* ── News panel ── */
.news-panel {
  position: fixed; right: 0; top: 0; bottom: 0; z-index: 600;
  width: 380px; max-width: 95vw;
  background: white;
  box-shadow: -8px 0 40px rgba(0,0,0,0.18);
  display: flex; flex-direction: column;
}
.panel-slide-enter-active, .panel-slide-leave-active { transition: transform 0.3s cubic-bezier(.4,0,.2,1); }
.panel-slide-enter-from, .panel-slide-leave-to { transform: translateX(100%); }

.panel-overlay {
  position: fixed; inset: 0; z-index: 590;
  background: rgba(0,0,0,0.3); backdrop-filter: blur(2px);
}

.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}
.panel-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.95rem; font-weight: 900; color: #1e293b;
}
.panel-close {
  width: 34px; height: 34px; border-radius: 50%;
  border: none; background: #f1f5f9; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: #64748b; transition: background 0.15s;
}
.panel-close:hover { background: #e2e8f0; }

.panel-body { flex: 1; overflow-y: auto; padding: 12px 0; }

.panel-item {
  display: flex; gap: 0;
  padding: 14px 20px;
  border-bottom: 1px solid #f8fafc;
  transition: background 0.15s;
}
.panel-item:hover { background: #f8fafc; }
.pi-accent { width: 4px; border-radius: 4px; flex-shrink: 0; margin-left: 14px; align-self: stretch; }
.pi-content { flex: 1; min-width: 0; }
.pi-meta { margin-bottom: 5px; }
.pi-cat {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.68rem; font-weight: 800;
  padding: 3px 10px; border-radius: 20px; text-transform: capitalize;
}
.pi-title { font-size: 0.88rem; font-weight: 800; color: #1e293b; margin: 0 0 4px; line-height: 1.35; }
.pi-text {
  font-size: 0.78rem; color: #64748b; line-height: 1.55; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

.panel-footer {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
}
.panel-link {
  display: block; text-align: center;
  background: linear-gradient(135deg, #1d4ed8, #7c3aed);
  color: white; font-size: 0.85rem; font-weight: 800;
  padding: 11px; border-radius: 12px;
  text-decoration: none; transition: opacity 0.2s;
}
.panel-link:hover { opacity: 0.88; }

/* Main */
.site-main { flex: 1; padding-top: 68px; }

/* Footer */
.site-footer { background: #0f172a; padding: 40px 24px 24px; }
.footer-inner { max-width: 1200px; margin: 0 auto; }
.footer-brand { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
.footer-brand span { font-size: 1rem; font-weight: 900; color: white; }
.footer-brand p { width: 100%; font-size: 0.78rem; color: rgba(255,255,255,0.45); margin: 0; }
.footer-links { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 24px; }
.footer-links a { font-size: 0.82rem; font-weight: 600; color: rgba(255,255,255,0.55); text-decoration: none; padding: 5px 10px; border-radius: 7px; transition: color 0.2s; }
.footer-links a:hover { color: white; }
.footer-copy { font-size: 0.75rem; color: rgba(255,255,255,0.3); border-top: 1px solid rgba(255,255,255,0.08); padding-top: 18px; }

/* Responsive */
@media(max-width: 768px) {
  .nav-links { display: none; }
  .btn-login { display: none; }
  .user-menu { display: none; }
  .hamburger { display: flex; }
  .user-info { display: none; }
}
</style>
