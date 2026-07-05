<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const reports      = ref([])
const loading      = ref(false)
const filterStatus = ref('all')
const search       = ref('')

onMounted(load)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/reports/')
    reports.value = data
  } finally { loading.value = false }
}

const withAppt = computed(() => reports.value.filter(r => r.appointment))
const needsAppt = computed(() =>
  reports.value.filter(r => !r.appointment && r.counselor && r.status !== 'تم الحل')
)

const filtered = computed(() => {
  let list = withAppt.value
  if (filterStatus.value !== 'all')
    list = list.filter(r => r.appointment.status === filterStatus.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(r =>
      (r.student_name || '').toLowerCase().includes(q) ||
      (r.counselor_name || '').toLowerCase().includes(q) ||
      (r.student_classe || '').toLowerCase().includes(q)
    )
  }
  return list
})

const counts = computed(() => ({
  all:    withAppt.value.length,
  مقترح: withAppt.value.filter(r => r.appointment.status === 'مقترح').length,
  مقبول: withAppt.value.filter(r => r.appointment.status === 'مقبول').length,
  مرفوض: withAppt.value.filter(r => r.appointment.status === 'مرفوض').length,
}))

const APPT_STATUS = {
  'مقترح': { label: 'مقترح',  color: '#f59e0b', bg: '#fffbeb' },
  'مقبول': { label: 'مقبول',  color: '#22c55e', bg: '#f0fdf4' },
  'مرفوض': { label: 'مرفوض',  color: '#ef4444', bg: '#fef2f2' },
}

const REPORT_STATUS = {
  'جديد':         { label: 'جديد',         color: '#3b82f6', bg: '#eff6ff' },
  'قيد المعالجة': { label: 'قيد المعالجة', color: '#f59e0b', bg: '#fffbeb' },
  'موعد محدد':    { label: 'موعد محدد',    color: '#7c3aed', bg: '#f5f3ff' },
  'تم الحل':      { label: 'تم الحل',      color: '#22c55e', bg: '#f0fdf4' },
}

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

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return new Date(y, m - 1, day).toLocaleDateString('ar-MA', { day: '2-digit', month: 'short', year: 'numeric' })
}
function formatTime(t) { return t ? t.slice(0, 5) : '—' }
function initials(name) {
  if (!name || name === 'مجهول الهوية') return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}
const AVATAR_COLORS = ['#1d4ed8', '#7c3aed', '#0891b2', '#059669', '#d97706', '#dc2626']
function avatarColor(name) {
  if (!name) return AVATAR_COLORS[0]
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length]
}
</script>

<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="20" height="20" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
            <rect x="3" y="4" width="18" height="18" rx="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <div>
          <h1>المواعيد</h1>
          <p>متابعة الجلسات المجدولة من قِبل المستشارين</p>
        </div>
      </div>
      <div class="info-note">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        الجدولة تتم من قِبل المستشارين
      </div>
    </div>

    <!-- KPI chips -->
    <div class="kpi-row">
      <div class="kpi-chip" style="border-top:3px solid #64748b">
        <span class="kpi-n">{{ counts.all }}</span>
        <span class="kpi-l">إجمالي المواعيد</span>
      </div>
      <div class="kpi-chip" style="border-top:3px solid #f59e0b">
        <span class="kpi-n" style="color:#f59e0b">{{ counts['مقترح'] }}</span>
        <span class="kpi-l">مقترحة</span>
      </div>
      <div class="kpi-chip" style="border-top:3px solid #22c55e">
        <span class="kpi-n" style="color:#22c55e">{{ counts['مقبول'] }}</span>
        <span class="kpi-l">مقبولة</span>
      </div>
      <div class="kpi-chip" style="border-top:3px solid #ef4444">
        <span class="kpi-n" style="color:#ef4444">{{ counts['مرفوض'] }}</span>
        <span class="kpi-l">مرفوضة</span>
      </div>
      <div class="kpi-chip" style="border-top:3px solid #a855f7">
        <span class="kpi-n" style="color:#a855f7">{{ needsAppt.length }}</span>
        <span class="kpi-l">بدون موعد</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-row">
      <button :class="['chip', filterStatus==='all' && 'active-all']" @click="filterStatus='all'">
        الكل <span class="chip-count">{{ counts.all }}</span>
      </button>
      <button v-for="(info, key) in APPT_STATUS" :key="key"
              :class="['chip', filterStatus===key && 'active-cat']"
              :style="filterStatus===key ? `background:${info.bg};color:${info.color};border-color:${info.color}` : ''"
              @click="filterStatus=key">
        {{ info.label }} <span class="chip-count">{{ counts[key] }}</span>
      </button>
      <div class="search-wrap">
        <svg width="14" height="14" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="search" placeholder="البحث عن طالب، مستشار..." />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-row">
      <div class="spinner"></div><span>جارٍ التحميل...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!filtered.length" class="empty-state">
      <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24">
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <p>لا توجد مواعيد</p>
      <p class="empty-hint">يمكن للمستشارين جدولة المواعيد من مساحتهم الخاصة.</p>
    </div>

    <!-- Cards list -->
    <div v-else class="appt-list">
      <div v-for="r in filtered" :key="r.id" class="appt-card">

        <!-- Numéro dossier -->
        <div class="dossier-num">#{{ r.numero_dossier || r.id }}</div>

        <!-- Student -->
        <div class="student-col">
          <div class="avatar" :style="`background:${avatarColor(r.student_name)}`">
            {{ initials(r.student_name) }}
          </div>
          <div>
            <div class="student-name">{{ r.student_name }}</div>
            <div class="student-meta">
              <span v-if="r.student_classe" class="classe-badge">{{ r.student_classe }}</span>
              <span class="type-txt">{{ TYPES[r.report_type] || r.report_type }}</span>
            </div>
          </div>
        </div>

        <!-- Counselor -->
        <div class="info-col">
          <div class="info-label">المستشار</div>
          <div class="info-value">{{ r.counselor_name || '—' }}</div>
        </div>

        <!-- Date & time -->
        <div class="info-col">
          <div class="info-label">التاريخ والوقت</div>
          <div class="info-value date-val">
            <svg width="13" height="13" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {{ formatDate(r.appointment.date) }}
            <svg width="13" height="13" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ formatTime(r.appointment.time) }}
          </div>
        </div>

        <!-- Note -->
        <div class="note-col">
          <div class="info-label">ملاحظة</div>
          <div class="note-val">{{ r.appointment.note || '—' }}</div>
        </div>

        <!-- Statuts -->
        <div class="status-col">
          <div class="appt-status-badge"
               :style="`background:${(APPT_STATUS[r.appointment.status]||{bg:'#f1f5f9'}).bg};color:${(APPT_STATUS[r.appointment.status]||{color:'#64748b'}).color}`">
            {{ (APPT_STATUS[r.appointment.status] || { label: r.appointment.status }).label }}
          </div>
          <div class="report-status-badge"
               :style="`background:${(REPORT_STATUS[r.status]||{bg:'#f1f5f9'}).bg};color:${(REPORT_STATUS[r.status]||{color:'#64748b'}).color}`">
            {{ (REPORT_STATUS[r.status] || { label: r.status }).label }}
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.page { padding: 0; }

.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon { width: 44px; height: 44px; border-radius: 13px; background: linear-gradient(135deg,#1d4ed8,#0891b2); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 14px rgba(29,78,216,0.3); }
.header-left h1 { font-size: 1.3rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
.header-left p  { font-size: 0.8rem; color: #94a3b8; margin: 0; }

.info-note { display: flex; align-items: center; gap: 7px; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 9px 14px; border-radius: 10px; font-size: 0.8rem; font-weight: 700; }

/* KPI */
.kpi-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.kpi-chip { background: white; border-radius: 12px; padding: 14px 18px; min-width: 110px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 3px; flex: 1; }
.kpi-n { font-size: 1.5rem; font-weight: 900; color: #1e293b; line-height: 1; }
.kpi-l { font-size: 0.72rem; color: #94a3b8; font-weight: 600; }

/* Filters */
.filter-row { display: flex; align-items: center; gap: 8px; margin-bottom: 18px; flex-wrap: wrap; }
.chip { display: flex; align-items: center; gap: 5px; padding: 7px 13px; border: 1.5px solid #e2e8f0; border-radius: 20px; background: white; font-size: 0.8rem; font-weight: 700; color: #64748b; cursor: pointer; transition: all 0.2s; }
.chip.active-all { background: #1d4ed8; color: white; border-color: #1d4ed8; }
.chip-count { background: #f1f5f9; color: #64748b; font-size: 0.7rem; font-weight: 800; padding: 1px 6px; border-radius: 10px; }
.chip.active-all .chip-count { background: rgba(255,255,255,0.25); color: white; }
.search-wrap { display: flex; align-items: center; gap: 7px; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 7px 12px; background: white; margin-right: auto; }
.search-wrap input { border: none; outline: none; font-size: 0.82rem; color: #1e293b; width: 200px; }

/* Loading / empty */
.loading-row { display: flex; align-items: center; gap: 10px; color: #94a3b8; font-size: 0.85rem; padding: 40px 0; justify-content: center; }
.spinner { width: 20px; height: 20px; border: 2.5px solid #e2e8f0; border-top-color: #1d4ed8; border-radius: 50%; animation: spin 0.7s linear infinite; }
.empty-state { text-align: center; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.empty-state p { color: #94a3b8; font-size: 0.9rem; margin: 0; }
.empty-hint { font-size: 0.78rem !important; color: #c0cfe0 !important; }

/* Cards */
.appt-list { display: flex; flex-direction: column; gap: 10px; }
.appt-card { background: white; border-radius: 14px; padding: 16px 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; transition: box-shadow 0.2s; flex-wrap: wrap; }
.appt-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.08); }

.dossier-num { font-size: 0.75rem; font-weight: 900; color: #94a3b8; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 8px; flex-shrink: 0; }

.student-col { display: flex; align-items: center; gap: 11px; min-width: 180px; flex: 1.5; }
.avatar { width: 40px; height: 40px; border-radius: 50%; color: white; font-weight: 800; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.student-name { font-size: 0.88rem; font-weight: 800; color: #1e293b; }
.student-meta { display: flex; align-items: center; gap: 6px; margin-top: 3px; flex-wrap: wrap; }
.classe-badge { font-size: 0.68rem; font-weight: 800; background: #eff6ff; color: #1d4ed8; padding: 2px 7px; border-radius: 20px; }
.type-txt { font-size: 0.72rem; color: #94a3b8; font-weight: 600; }

.info-col { min-width: 120px; flex: 1; }
.info-label { font-size: 0.68rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
.info-value { font-size: 0.82rem; font-weight: 700; color: #374151; }
.date-val { display: flex; align-items: center; gap: 5px; }

.note-col { flex: 1.5; min-width: 140px; }
.note-val { font-size: 0.78rem; color: #64748b; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.status-col { display: flex; flex-direction: column; gap: 5px; flex-shrink: 0; }
.appt-status-badge, .report-status-badge { font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 20px; white-space: nowrap; text-align: center; }

@keyframes spin { to { transform: rotate(360deg) } }
</style>
