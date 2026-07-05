<script setup>
import { computed, onMounted } from 'vue'
import { useReportsStore } from '../../stores/reports'
import { useAuthStore }    from '../../stores/auth'

const store = useReportsStore()
const auth  = useAuthStore()

onMounted(() => {
  store.fetchStats()
})

const resolutionRate = computed(() => {
  const total = store.stats.total || 0
  if (!total) return 0
  return Math.round(((store.stats.resolved || 0) / total) * 100)
})

const today = new Date().toLocaleDateString('ar-MA', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})

const hour = new Date().getHours()
const greeting = computed(() => {
  if (hour < 12) return 'صباح الخير'
  if (hour < 18) return 'مساء الخير'
  return 'مساء الخير'
})

// قائمة الإجراءات العاجلة
const urgentActions = computed(() => {
  const list = []
  if ((store.stats.new || 0) > 0)
    list.push({ color: '#dc2626', bg: '#fef2f2', icon: 'alert', text: `${store.stats.new} بلاغ غير مُسند`, to: '/directeur/reports' })
  if ((store.stats.pending || 0) > 0)
    list.push({ color: '#d97706', bg: '#fffbeb', icon: 'clock', text: `${store.stats.pending} طالب في انتظار التفعيل`, to: '/directeur/students' })
  if ((store.stats.needs_appt || 0) > 0)
    list.push({ color: '#7c3aed', bg: '#f5f3ff', icon: 'cal', text: `${store.stats.needs_appt} ملف يحتاج موعداً`, to: '/directeur/reports' })
  return list
})
</script>

<template>
  <div class="dashboard">

    <!-- ── Header ── -->
    <div class="header">
      <!-- Filigrane bouclier -->
      <div class="header-wm" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z" stroke="white" stroke-width="0.5"/>
          <path d="M9 12l2 2 4-4" stroke="white" stroke-width="0.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>SafeSchool</span>
      </div>

      <div class="header-left">
        <div class="header-greeting">
          {{ greeting }}، <span class="header-name">{{ auth.user?.first_name || auth.user?.username }}</span> 👋
        </div>
        <div class="header-date">{{ today }}</div>
      </div>
      <div :class="['header-status', (store.stats.new||0)>0 ? 'status-alert':'status-ok']">
        <span class="status-dot"></span>
        {{ (store.stats.new||0) > 0
            ? `${store.stats.new} بلاغ غير مُسند`
            : 'جميع البلاغات تمت معالجتها' }}
      </div>
    </div>

    <!-- ── KPI Cards ── -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon-wrap" style="background:linear-gradient(135deg,#1d4ed8,#3b82f6)">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ store.stats.total || 0 }}</div>
          <div class="kpi-label">إجمالي البلاغات</div>
        </div>
      </div>

      <div class="kpi-card" :class="(store.stats.new||0)>0?'kpi-urgent':''">
        <div class="kpi-icon-wrap" style="background:linear-gradient(135deg,#dc2626,#f87171)">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ store.stats.new || 0 }}</div>
          <div class="kpi-label">غير مُسندة</div>
        </div>
        <div v-if="(store.stats.new||0)>0" class="kpi-badge-urgent">عاجل</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon-wrap" style="background:linear-gradient(135deg,#f97316,#fb923c)">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ store.stats.in_progress || 0 }}</div>
          <div class="kpi-label">قيد المعالجة</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon-wrap" style="background:linear-gradient(135deg,#7c3aed,#a78bfa)">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ store.stats.appointed || 0 }}</div>
          <div class="kpi-label">مواعيد محددة</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon-wrap" style="background:linear-gradient(135deg,#059669,#34d399)">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ store.stats.resolved || 0 }}</div>
          <div class="kpi-label">تمت معالجتها</div>
        </div>
        <div class="kpi-trend kpi-up">
          <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
        </div>
      </div>
    </div>

    <!-- ── Mid Row ── -->
    <div class="mid-row">

      <!-- معدل الحل + الخط الزمني -->
      <div class="rate-card">
        <div class="rate-top">
          <div>
            <div class="rate-title">معدل الحل</div>
            <div class="rate-sub">{{ store.stats.resolved||0 }} حالة محلولة من أصل {{ store.stats.total||0 }}</div>
          </div>
          <div class="rate-circle">
            <svg width="72" height="72" viewBox="0 0 72 72">
              <circle cx="36" cy="36" r="30" fill="none" stroke="#f1f5f9" stroke-width="8"/>
              <circle cx="36" cy="36" r="30" fill="none" stroke="url(#rg)" stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="`${resolutionRate*1.885} 188.5`"
                stroke-dashoffset="0"
                transform="rotate(-90 36 36)"
                style="transition:stroke-dasharray 0.8s ease"/>
              <defs>
                <linearGradient id="rg" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#059669"/><stop offset="100%" stop-color="#34d399"/>
                </linearGradient>
              </defs>
              <text x="36" y="40" text-anchor="middle" font-size="14" font-weight="900" fill="#1e293b">{{ resolutionRate }}%</text>
            </svg>
          </div>
        </div>
        <div class="pipeline">
          <div v-for="item in [
            { label:'غير مُسندة',    color:'#dc2626', val: store.stats.new||0 },
            { label:'قيد المعالجة', color:'#f97316', val: store.stats.in_progress||0 },
            { label:'مواعيد محددة', color:'#7c3aed', val: store.stats.appointed||0 },
            { label:'تمت معالجتها', color:'#059669', val: store.stats.resolved||0 },
          ]" :key="item.label" class="pipeline-item">
            <div class="pip-label">
              <span class="pip-dot" :style="`background:${item.color}`"></span>
              {{ item.label }}
            </div>
            <div class="pip-bar-bg">
              <div class="pip-bar-fill" :style="`background:${item.color};width:${store.stats.total ? (item.val/store.stats.total*100) : 0}%`"></div>
            </div>
            <span class="pip-count">{{ item.val }}</span>
          </div>
        </div>
      </div>

      <!-- Colonnes info + actions urgentes -->
      <div class="right-col">

        <!-- إجراءات عاجلة -->
        <div v-if="urgentActions.length" class="urgent-card">
          <div class="urgent-title">
            <svg width="15" height="15" fill="none" stroke="#dc2626" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            إجراءات مطلوبة
          </div>
          <RouterLink v-for="(a, i) in urgentActions" :key="i" :to="a.to" class="urgent-item">
            <div class="urgent-dot" :style="`background:${a.bg}`">
              <!-- alert icon -->
              <svg v-if="a.icon==='alert'" width="14" height="14" fill="none" :stroke="a.color" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <svg v-else-if="a.icon==='clock'" width="14" height="14" fill="none" :stroke="a.color" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <svg v-else width="14" height="14" fill="none" :stroke="a.color" stroke-width="2.5" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <span :style="`color:${a.color}`">{{ a.text }}</span>
            <svg width="14" height="14" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
          </RouterLink>
        </div>

        <!-- Info counts -->
        <div class="info-col">
          <div class="info-card">
            <div class="info-icon-wrap" style="background:#ede9fe">
              <svg width="20" height="20" fill="none" stroke="#7c3aed" stroke-width="2" viewBox="0 0 24 24"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            </div>
            <div class="info-body">
              <div class="info-num">{{ store.stats.students||0 }}</div>
              <div class="info-label">الطلاب المسجلون</div>
            </div>
            <RouterLink to="/directeur/students" class="info-link">عرض ←</RouterLink>
          </div>
          <div class="info-card" :class="(store.stats.pending||0)>0?'info-warn':''">
            <div class="info-icon-wrap" style="background:#fef3c7">
              <svg width="20" height="20" fill="none" stroke="#d97706" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="info-body">
              <div class="info-num">{{ store.stats.pending||0 }}</div>
              <div class="info-label">في انتظار التفعيل</div>
            </div>
            <span v-if="(store.stats.pending||0)>0" class="info-badge">للتحقق</span>
            <RouterLink v-else to="/directeur/students" class="info-link">عرض ←</RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- ── وصول سريع ── -->
    <div class="section-label">وصول سريع</div>
    <div class="quick-grid">

      <RouterLink v-for="item in [
        { to:'/directeur/reports',      grad:'135deg,#1d4ed8,#3b82f6', title:'البلاغات',        sub:'إدارة وإسناد الملفات',    badge:(store.stats.new||0)>0 ? store.stats.new : null, bClass:'red',
          svg:`<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/><line x1='16' y1='13' x2='8' y2='13'/><line x1='16' y1='17' x2='8' y2='17'/>` },
        { to:'/directeur/students',     grad:'135deg,#7c3aed,#a78bfa', title:'الطلاب',           sub:'إدارة حسابات الطلاب',     badge:(store.stats.pending||0)>0 ? store.stats.pending : null, bClass:'amber',
          svg:`<path d='M22 10v6M2 10l10-5 10 5-10 5z'/><path d='M6 12v5c3 3 9 3 12 0v-5'/>` },
        { to:'/directeur/counselors',   grad:'135deg,#0d9488,#2dd4bf', title:'المستشارون',       sub:'إدارة الفريق', badge:null, bClass:'',
          svg:`<path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/><circle cx='9' cy='7' r='4'/><path d='M23 21v-2a4 4 0 0 0-3-3.87'/><path d='M16 3.13a4 4 0 0 1 0 7.75'/>` },
        { to:'/directeur/appointments', grad:'135deg,#d97706,#fbbf24', title:'المواعيد',         sub:'متابعة المواعيد',          badge:(store.stats.appointed||0)>0 ? store.stats.appointed : null, bClass:'yellow',
          svg:`<rect x='3' y='4' width='18' height='18' rx='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/>` },
        { to:'/directeur/session-reports',grad:'135deg,#059669,#34d399',title:'تقارير الجلسات',  sub:'الاطلاع على تقارير الجلسات', badge:null, bClass:'',
          svg:`<path d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'/><path d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'/>` },
      ]" :key="item.to" :to="item.to" class="quick-card">
        <div class="quick-icon" :style="`background:linear-gradient(${item.grad})`">
          <svg width="20" height="20" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24" v-html="item.svg"></svg>
        </div>
        <div class="quick-body">
          <div class="quick-title">{{ item.title }}</div>
          <div class="quick-sub">{{ item.sub }}</div>
        </div>
        <div v-if="item.badge" :class="['quick-badge', item.bClass]">{{ item.badge }}</div>
        <svg class="quick-arrow" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
      </RouterLink>

    </div>

  </div>
</template>

<style scoped>
/* ── Tokens ── */
:root {
  --blue:      #2563eb;
  --blue-dark: #1d4ed8;
  --blue-50:   #eff6ff;
  --slate-50:  #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1e293b;
  --slate-900: #0f172a;
  --card-shadow:       0 0 0 1px rgba(0,0,0,0.05), 0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.03);
  --card-shadow-hover: 0 0 0 1px rgba(37,99,235,0.12), 0 4px 16px rgba(0,0,0,0.07), 0 16px 40px rgba(0,0,0,0.06);
  --radius-card: 14px;
  --radius-icon: 10px;
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 28px;
  animation: fadein 0.4s cubic-bezier(.25,.8,.25,1) both;
  position: relative;
}


@keyframes fadein { from { opacity:0; transform:translateY(12px) } to { opacity:1; transform:none } }


/* ── Header ── */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  padding: 28px 32px;
  background: linear-gradient(120deg, #0f172a 0%, #1e3a5f 55%, #1d4ed8 100%);
  border-radius: 18px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(29,78,216,0.25), 0 2px 8px rgba(0,0,0,0.15);
}

/* Cercles déco */
.header::before {
  content: '';
  position: absolute;
  top: -70px; right: -70px;
  width: 280px; height: 280px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  pointer-events: none;
}
.header::after {
  content: '';
  position: absolute;
  bottom: -90px; left: 38%;
  width: 220px; height: 220px;
  border-radius: 50%;
  background: rgba(255,255,255,0.03);
  pointer-events: none;
}

/* Filigrane */
.header-wm {
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  opacity: 0.1;
  pointer-events: none;
  user-select: none;
}
.header-wm svg  { width: 72px; height: 72px; }
.header-wm span {
  font-size: 2rem;
  font-weight: 900;
  color: white;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-family: 'Inter', sans-serif;
  white-space: nowrap;
}

.header-greeting {
  font-size: 1.55rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.header-name { color: #93c5fd; font-weight: 800; }
.header-date {
  font-size: 0.79rem;
  color: rgba(255,255,255,0.5);
  margin-top: 6px;
  text-transform: capitalize;
  font-weight: 500;
}
.header-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 99px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid;
  backdrop-filter: blur(8px);
}
.status-ok    { background: rgba(34,197,94,0.15);  border-color: rgba(34,197,94,0.35);  color: #86efac; }
.status-alert { background: rgba(239,68,68,0.15);  border-color: rgba(239,68,68,0.35);  color: #fca5a5; }
.status-dot   { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.status-ok .status-dot    { background: #22c55e; box-shadow: 0 0 0 3px rgba(34,197,94,0.3); }
.status-alert .status-dot { background: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.3); animation: blink 1.5s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ── KPI ── */
.kpi-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; }
@media(max-width:1100px){ .kpi-grid { grid-template-columns: repeat(3,1fr); } }
@media(max-width:600px){  .kpi-grid { grid-template-columns: repeat(2,1fr); } }

.kpi-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  padding: 20px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--slate-200);
  position: relative;
  overflow: hidden;
  transition: transform 0.24s cubic-bezier(.25,.8,.25,1), box-shadow 0.24s, border-color 0.2s;
}
.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
  border-color: #bfdbfe;
}
.kpi-urgent {
  border-color: #fecaca;
  background: linear-gradient(150deg, #fff5f5 40%, #ffffff);
}
.kpi-urgent:hover { border-color: #fca5a5; }

.kpi-icon-wrap {
  width: 42px; height: 42px;
  border-radius: var(--radius-icon);
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 10px rgba(0,0,0,0.15);
}
.kpi-body { flex: 1; }
.kpi-num {
  font-size: 2rem;
  font-weight: 800;
  color: var(--slate-900);
  line-height: 1;
  letter-spacing: -0.04em;
}
.kpi-label {
  font-size: 0.7rem;
  color: var(--slate-500);
  margin-top: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.kpi-trend {
  position: absolute; top: 14px; right: 14px;
  width: 24px; height: 24px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.kpi-up { background: #f0fdf4; color: #16a34a; }
.kpi-badge-urgent {
  position: absolute; top: 12px; right: 12px;
  background: #dc2626; color: #fff;
  font-size: 0.58rem; font-weight: 800;
  padding: 3px 8px; border-radius: 99px;
  text-transform: uppercase; letter-spacing: 0.08em;
  animation: blink 1.5s infinite;
}

/* ── Mid Row ── */
.mid-row { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; }
@media(max-width:900px){ .mid-row { grid-template-columns: 1fr; } }

.rate-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  padding: 24px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--slate-200);
  display: flex; flex-direction: column; gap: 22px;
}
.rate-top { display: flex; justify-content: space-between; align-items: flex-start; }
.rate-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--slate-900);
  letter-spacing: -0.01em;
}
.rate-sub { font-size: 0.71rem; color: var(--slate-400); margin-top: 4px; font-weight: 500; }

.pipeline { display: flex; flex-direction: column; gap: 13px; }
.pipeline-item { display: flex; align-items: center; gap: 11px; }
.pip-label {
  display: flex; align-items: center; gap: 7px;
  font-size: 0.74rem;
  color: var(--slate-600);
  width: 120px; flex-shrink: 0; font-weight: 600;
  letter-spacing: 0.01em;
}
.pip-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.pip-bar-bg {
  flex: 1; background: var(--slate-100);
  border-radius: 99px; height: 6px; overflow: hidden;
}
.pip-bar-fill {
  height: 100%; border-radius: 99px;
  transition: width 1s cubic-bezier(.25,.8,.25,1); min-width: 4px;
}
.pip-count { font-size: 0.76rem; font-weight: 700; color: var(--slate-700); width: 26px; text-align: right; }

/* Right col */
.right-col { display: flex; flex-direction: column; gap: 12px; }

/* Urgent actions */
.urgent-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  padding: 18px 20px;
  box-shadow: var(--card-shadow);
  border: 1px solid #fecaca;
  background: linear-gradient(160deg, #fff8f8 30%, #ffffff);
}
.urgent-title {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.72rem; font-weight: 700; color: #b91c1c;
  margin-bottom: 12px;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.urgent-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px;
  border-radius: 9px;
  text-decoration: none;
  transition: background 0.15s;
  margin: 0 -4px;
}
.urgent-item:hover { background: #fff1f1; }
.urgent-dot {
  width: 30px; height: 30px;
  border-radius: 8px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.urgent-item span { flex: 1; font-size: 0.79rem; font-weight: 600; line-height: 1.35; }

/* Info col */
.info-col { display: flex; flex-direction: column; gap: 10px; }
.info-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  padding: 15px 17px;
  display: flex; align-items: center; gap: 13px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--slate-200);
  transition: transform 0.22s, box-shadow 0.22s, border-color 0.2s;
}
.info-card:hover { transform: translateX(4px); box-shadow: var(--card-shadow-hover); border-color: #bfdbfe; }
.info-warn { border-color: #fde68a; background: linear-gradient(135deg,#fffbeb 30%,#ffffff); }
.info-warn:hover { border-color: #fcd34d; }
.info-icon-wrap {
  width: 40px; height: 40px;
  border-radius: var(--radius-icon); flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.info-num   { font-size: 1.5rem; font-weight: 800; color: var(--slate-900); line-height: 1; letter-spacing: -0.03em; }
.info-label { font-size: 0.68rem; color: var(--slate-500); font-weight: 600; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.05em; }
.info-link  { font-size: 0.74rem; font-weight: 700; color: var(--blue); text-decoration: none; white-space: nowrap; }
.info-link:hover { text-decoration: underline; }
.info-badge { background: #fef3c7; color: #92400e; font-size: 0.62rem; font-weight: 700; padding: 3px 9px; border-radius: 99px; white-space: nowrap; border: 1px solid #fde68a; }
.info-body { flex: 1; }

/* ── Quick Access ── */
.section-label {
  font-size: 0.68rem; font-weight: 700;
  color: var(--slate-400);
  text-transform: uppercase; letter-spacing: 0.14em;
}
.quick-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }
.quick-card {
  background: #ffffff;
  border-radius: var(--radius-card);
  padding: 15px 16px;
  display: flex; align-items: center; gap: 13px;
  text-decoration: none; color: var(--slate-900);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--slate-200);
  transition: transform 0.24s cubic-bezier(.25,.8,.25,1), box-shadow 0.24s, border-color 0.2s;
}
.quick-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
  border-color: #bfdbfe;
}
.quick-icon {
  width: 40px; height: 40px;
  border-radius: var(--radius-icon); flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 10px rgba(0,0,0,0.14);
}
.quick-body { flex: 1; min-width: 0; }
.quick-title { font-size: 0.82rem; font-weight: 700; color: var(--slate-900); letter-spacing: -0.01em; }
.quick-sub   { font-size: 0.69rem; color: var(--slate-400); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.quick-arrow { color: var(--slate-300); flex-shrink: 0; transition: color 0.2s, transform 0.2s; }
.quick-card:hover .quick-arrow { color: var(--blue); transform: translateX(3px); }
.quick-badge { font-size: 0.67rem; font-weight: 700; padding: 3px 8px; border-radius: 99px; flex-shrink: 0; letter-spacing: 0.03em; }
.quick-badge.red    { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.quick-badge.amber  { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.quick-badge.yellow { background: #fefce8; color: #854d0e; border: 1px solid #fef08a; }
</style>
