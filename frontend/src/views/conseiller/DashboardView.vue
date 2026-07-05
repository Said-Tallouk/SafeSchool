<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const auth    = ref(useAuthStore())
const stats   = ref({})
const reports = ref([])
const loading = ref(true)

// Salutation dynamique
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'صباح الخير'
  if (h < 18) return 'مساء الخير'
  return 'مساء النور'
})

const displayName = computed(() => {
  const u = auth.value.user
  if (!u) return ''
  return u.first_name || u.username
})

const todayStr = computed(() => new Date().toLocaleDateString('ar-MA', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
}))

onMounted(async () => {
  try {
    const [statsRes, reportsRes] = await Promise.all([
      api.get('/stats/'),
      api.get('/reports/'),
    ])
    stats.value   = statsRes.data
    reports.value = reportsRes.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// Dossiers actifs (non résolus)
const activeReports = computed(() =>
  reports.value.filter(r => r.status !== 'تم الحل').slice(0, 5)
)

// Prochains RDV acceptés
const upcomingAppts = computed(() =>
  reports.value
    .filter(r => r.appointment?.status === 'مقبول')
    .sort((a, b) => new Date(a.appointment.date) - new Date(b.appointment.date))
    .slice(0, 4)
)

// RDV en attente de réponse
const pendingAppts = computed(() =>
  reports.value.filter(r => r.appointment?.status === 'مقترح').length
)

const TYPES = {
  'التحرش الجسدي':           'تحرش جسدي',
  'التحرش اللفظي':           'تحرش لفظي',
  'التحرش الإلكتروني':       'تحرش إلكتروني',
  'العنف اللفظي أو التهديد': 'عنف لفظي / تهديد',
  'الإقصاء الاجتماعي':       'إقصاء اجتماعي',
  'التمييز':                 'تمييز',
  'التمييز العرقي':           'تمييز عرقي',
  'التمييز الجنسي':           'تمييز جنسي',
  'التمييز الديني':           'تمييز ديني',
  'التحرش الجنسي':           'تحرش جنسي',
  'أخرى':                    'أخرى',
}

const STATUS_CFG = {
  'جديد':         { label: 'جديد',         color: '#3b82f6', bg: '#eff6ff' },
  'قيد المعالجة': { label: 'قيد المعالجة', color: '#f59e0b', bg: '#fffbeb' },
  'موعد محدد':    { label: 'موعد محدد',    color: '#7c3aed', bg: '#f5f3ff' },
  'تم الحل':      { label: 'تم الحل',      color: '#22c55e', bg: '#f0fdf4' },
}

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return new Date(y, m - 1, day).toLocaleDateString('ar-MA', { day: '2-digit', month: 'short' })
}

function initials(name) {
  if (!name || name === 'مجهول الهوية') return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const COLORS = ['#1d4ed8', '#1d4ed8', '#7c3aed', '#d97706', '#059669', '#dc2626']
function avatarColor(name) {
  if (!name) return COLORS[0]
  return COLORS[name.charCodeAt(0) % COLORS.length]
}

// Taux de résolution
const resolutionRate = computed(() => {
  const t = stats.value.total || 0
  const r = stats.value.resolved || 0
  return t ? Math.round((r / t) * 100) : 0
})
</script>

<template>
  <div class="dash">

    <!-- ── Hero header ── -->
    <div class="dash-hero">
      <div class="hero-left">
        <div class="hero-greeting">{{ greeting }},</div>
        <h1 class="hero-name">{{ displayName }} <span class="wave">👋</span></h1>
        <div class="hero-date">{{ todayStr }}</div>
      </div>
      <div class="hero-right">
        <div class="hero-stat">
          <div class="hero-stat-n" style="color:#1d4ed8">{{ stats.total || 0 }}</div>
          <div class="hero-stat-l">الملفات المُسندة</div>
        </div>
        <div class="hero-divider"></div>
        <div class="hero-stat">
          <div class="hero-stat-n" style="color:#7c3aed">{{ resolutionRate }}%</div>
          <div class="hero-stat-l">معدل الحل</div>
        </div>
        <div class="hero-divider"></div>
        <div class="hero-stat">
          <div class="hero-stat-n" :style="pendingAppts > 0 ? 'color:#ef4444' : 'color:#22c55e'">{{ pendingAppts }}</div>
          <div class="hero-stat-l">مواعيد في الانتظار</div>
        </div>
      </div>
    </div>

    <!-- ── KPI Cards ── -->
    <div class="kpi-grid">
      <div class="kpi-card" style="--accent:#1d4ed8">
        <div class="kpi-icon" style="background:#eff6ff; color:#1d4ed8">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ stats.total || 0 }}</div>
          <div class="kpi-label">إجمالي الملفات</div>
        </div>
        <div class="kpi-bar" style="background:#dbeafe">
          <div class="kpi-fill" style="background:#1d4ed8; width:100%"></div>
        </div>
      </div>

      <div class="kpi-card" style="--accent:#f59e0b">
        <div class="kpi-icon" style="background:#fffbeb; color:#f59e0b">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ stats.in_progress || 0 }}</div>
          <div class="kpi-label">قيد المعالجة</div>
        </div>
        <div class="kpi-bar" style="background:#fffbeb">
          <div class="kpi-fill" style="background:#f59e0b"
               :style="{ width: stats.total ? (stats.in_progress / stats.total * 100) + '%' : '0%' }"></div>
        </div>
      </div>

      <div class="kpi-card" style="--accent:#7c3aed">
        <div class="kpi-icon" style="background:#f5f3ff; color:#7c3aed">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ stats.appointed || 0 }}</div>
          <div class="kpi-label">مواعيد محددة</div>
        </div>
        <div class="kpi-bar" style="background:#f5f3ff">
          <div class="kpi-fill" style="background:#7c3aed"
               :style="{ width: stats.total ? (stats.appointed / stats.total * 100) + '%' : '0%' }"></div>
        </div>
      </div>

      <div class="kpi-card" style="--accent:#22c55e">
        <div class="kpi-icon" style="background:#f0fdf4; color:#22c55e">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ stats.resolved || 0 }}</div>
          <div class="kpi-label">تمت معالجتها</div>
        </div>
        <div class="kpi-bar" style="background:#f0fdf4">
          <div class="kpi-fill" style="background:#22c55e"
               :style="{ width: stats.total ? (stats.resolved / stats.total * 100) + '%' : '0%' }"></div>
        </div>
      </div>
    </div>

    <!-- ── Content grid ── -->
    <div class="content-grid">

      <!-- Dossiers actifs -->
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title">
            <div class="panel-icon" style="background:#eff6ff; color:#1d4ed8">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            </div>
            <span>الملفات النشطة</span>
          </div>
          <RouterLink to="/conseiller/reports" class="panel-link">عرض الكل ←</RouterLink>
        </div>

        <div v-if="loading" class="panel-loading">
          <div class="spinner"></div>
        </div>
        <div v-else-if="activeReports.length === 0" class="panel-empty">
          <svg width="40" height="40" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <p>لا توجد ملفات نشطة</p>
        </div>
        <div v-else class="report-list">
          <RouterLink to="/conseiller/reports" class="report-row" v-for="r in activeReports" :key="r.id">
            <div class="r-avatar" :style="{ background: avatarColor(r.student_name) }">
              {{ initials(r.student_name) }}
            </div>
            <div class="r-info">
              <div class="r-name">{{ r.student_name }}</div>
              <div class="r-type">{{ TYPES[r.report_type] || r.report_type }}</div>
            </div>
            <div class="r-meta">
              <span v-if="r.student_classe" class="r-classe">{{ r.student_classe }}</span>
              <span class="r-status" :style="{ background: STATUS_CFG[r.status]?.bg, color: STATUS_CFG[r.status]?.color }">
                {{ STATUS_CFG[r.status]?.label || r.status }}
              </span>
            </div>
          </RouterLink>
        </div>
      </div>

      <!-- Sidebar droite -->
      <div class="side-col">

        <!-- Prochains RDV -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-title">
              <div class="panel-icon" style="background:#f5f3ff; color:#7c3aed">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              </div>
              <span>المواعيد القادمة</span>
            </div>
          </div>
          <div v-if="upcomingAppts.length === 0" class="panel-empty sm">
            <p>لا توجد مواعيد مؤكدة</p>
          </div>
          <div v-else class="appt-list">
            <div v-for="r in upcomingAppts" :key="r.id" class="appt-row">
              <div class="appt-date">
                <div class="appt-day">{{ new Date(r.appointment.date).getDate() }}</div>
                <div class="appt-month">{{ new Date(r.appointment.date).toLocaleDateString('ar-MA', { month: 'short' }) }}</div>
              </div>
              <div class="appt-info">
                <div class="appt-name">{{ r.student_name }}</div>
                <div class="appt-time">
                  <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  {{ r.appointment.time?.slice(0, 5) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Accès rapide -->
        <div class="panel">
          <div class="panel-header">
            <div class="panel-title">
              <div class="panel-icon" style="background:#f0fdf4; color:#059669">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
              </div>
              <span>الوصول السريع</span>
            </div>
          </div>
          <div class="quick-list">
            <RouterLink to="/conseiller/reports" class="quick-item">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <span>ملفاتي</span>
              <span v-if="(stats.in_progress || 0) > 0" class="quick-badge">{{ stats.in_progress }}</span>
              <svg class="arrow" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>
            <RouterLink to="/conseiller/session-reports" class="quick-item">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4z"/></svg>
              <span>تقارير الجلسات</span>
              <svg class="arrow" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>
            <RouterLink to="/conseiller/profile" class="quick-item">
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span>ملفي الشخصي</span>
              <svg class="arrow" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
            </RouterLink>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.dash { display: flex; flex-direction: column; gap: 24px; }

/* Hero */
.dash-hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #1d4ed8 100%);
  border-radius: 20px; padding: 28px 32px;
  display: flex; align-items: center; justify-content: space-between; gap: 24px;
  flex-wrap: wrap;
}
.hero-greeting { font-size: 0.85rem; color: rgba(255,255,255,0.6); font-weight: 600; margin-bottom: 4px; }
.hero-name { font-size: 1.8rem; font-weight: 900; color: white; margin: 0 0 6px; }
.wave { font-style: normal; }
.hero-date { font-size: 0.78rem; color: rgba(255,255,255,0.5); text-transform: capitalize; }
.hero-right { display: flex; align-items: center; gap: 20px; }
.hero-stat { text-align: center; }
.hero-stat-n { font-size: 1.8rem; font-weight: 900; line-height: 1; }
.hero-stat-l { font-size: 0.7rem; color: rgba(255,255,255,0.55); font-weight: 600; margin-top: 4px; white-space: nowrap; }
.hero-divider { width: 1px; height: 40px; background: rgba(255,255,255,0.15); }

/* KPI grid */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card {
  background: white; border-radius: 16px; padding: 20px;
  border: 1px solid #f1f5f9; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex; flex-direction: column; gap: 12px;
  border-top: 3px solid var(--accent);
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.kpi-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.kpi-body { flex: 1; }
.kpi-num { font-size: 2rem; font-weight: 900; color: #0f172a; line-height: 1; }
.kpi-label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; margin-top: 4px; }
.kpi-bar { height: 4px; border-radius: 4px; overflow: hidden; }
.kpi-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }

/* Content grid */
.content-grid { display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start; }

/* Panel */
.panel { background: white; border-radius: 16px; border: 1px solid #f1f5f9; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow: hidden; }
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #f8fafc; }
.panel-title { display: flex; align-items: center; gap: 10px; font-size: 0.9rem; font-weight: 800; color: #0f172a; }
.panel-icon { width: 30px; height: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.panel-link { font-size: 0.78rem; font-weight: 700; color: #1d4ed8; text-decoration: none; }
.panel-link:hover { color: #1e40af; }
.panel-loading { display: flex; justify-content: center; padding: 40px; }
.spinner { width: 24px; height: 24px; border: 2.5px solid #e2e8f0; border-top-color: #1d4ed8; border-radius: 50%; animation: spin 0.7s linear infinite; }
.panel-empty { text-align: center; padding: 40px 20px; color: #94a3b8; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.panel-empty.sm { padding: 24px 20px; }
.panel-empty p { font-size: 0.85rem; margin: 0; }

/* Report list */
.report-list { display: flex; flex-direction: column; }
.report-row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px; border-bottom: 1px solid #f8fafc;
  text-decoration: none; transition: background 0.15s;
}
.report-row:last-child { border-bottom: none; }
.report-row:hover { background: #f8fafc; }
.r-avatar { width: 36px; height: 36px; border-radius: 50%; color: white; font-size: 0.75rem; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.r-info { flex: 1; min-width: 0; }
.r-name { font-size: 0.85rem; font-weight: 800; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.r-type { font-size: 0.72rem; color: #94a3b8; margin-top: 2px; }
.r-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; flex-shrink: 0; }
.r-classe { font-size: 0.65rem; font-weight: 800; background: #eff6ff; color: #1d4ed8; padding: 2px 7px; border-radius: 10px; }
.r-status { font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 10px; white-space: nowrap; }

/* Side col */
.side-col { display: flex; flex-direction: column; gap: 20px; }

/* Appt list */
.appt-list { display: flex; flex-direction: column; }
.appt-row { display: flex; align-items: center; gap: 12px; padding: 12px 20px; border-bottom: 1px solid #f8fafc; }
.appt-row:last-child { border-bottom: none; }
.appt-date { background: linear-gradient(135deg, #7c3aed, #5b21b6); border-radius: 10px; padding: 8px 10px; text-align: center; flex-shrink: 0; min-width: 44px; }
.appt-day { font-size: 1.2rem; font-weight: 900; color: white; line-height: 1; }
.appt-month { font-size: 0.55rem; color: rgba(255,255,255,0.75); font-weight: 700; text-transform: uppercase; margin-top: 2px; }
.appt-info { flex: 1; min-width: 0; }
.appt-name { font-size: 0.82rem; font-weight: 800; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.appt-time { display: flex; align-items: center; gap: 4px; font-size: 0.72rem; color: #64748b; margin-top: 3px; }

/* Quick links */
.quick-list { display: flex; flex-direction: column; padding: 8px 12px; gap: 2px; }
.quick-item {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 10px; border-radius: 10px;
  text-decoration: none; color: #374151;
  font-size: 0.85rem; font-weight: 700;
  transition: background 0.15s;
}
.quick-item:hover { background: #eff6ff; color: #1d4ed8; }
.quick-item span:first-of-type { flex: 1; }
.quick-badge { background: #fee2e2; color: #dc2626; font-size: 0.65rem; font-weight: 900; padding: 2px 7px; border-radius: 10px; }
.arrow { color: #cbd5e1; flex-shrink: 0; }
.quick-item:hover .arrow { color: #1d4ed8; }

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1000px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .content-grid { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .dash-hero { flex-direction: column; align-items: flex-start; }
  .hero-right { width: 100%; justify-content: space-around; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
