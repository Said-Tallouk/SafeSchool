<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportsStore } from '../../stores/reports'
import { useAuthStore } from '../../stores/auth'

const reportsStore = useReportsStore()
const auth         = useAuthStore()
const fetchError   = ref(false)

async function retryFetch() {
  fetchError.value = false
  try {
    await reportsStore.fetchReports()
  } catch {
    fetchError.value = true
  }
}

onMounted(() => {
  reportsStore.fetchReports().catch(() => { fetchError.value = true })
  reportsStore.fetchStats().catch(() => {})
})

const STATUS_MAP = {
  'جديد':         { label: 'جديد',         cls: 'badge-new' },
  'قيد المعالجة': { label: 'قيد المعالجة', cls: 'badge-progress' },
  'موعد محدد':    { label: 'موعد محدد',    cls: 'badge-appt' },
  'تم الحل':      { label: 'تم الحل',      cls: 'badge-done' },
}

const TYPES_LABELS = {
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

const APPT_LABELS = {
  'مقترح': 'مقترح',
  'مقبول': 'مقبول',
  'مرفوض': 'مرفوض',
}

const pendingAppts = computed(() =>
  reportsStore.reports.filter(r =>
    r.appointment && r.appointment.status === 'مقترح' && r.status !== 'تم الحل'
  )
)

const expanded       = ref(new Set())
const respondLoading = ref({})
const uploadLoading  = ref({})
const uploadError    = ref({})

function toggleExpand(id) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
  expanded.value = new Set(expanded.value)
}

async function respond(reportId, action) {
  respondLoading.value[reportId] = true
  try {
    await reportsStore.respondAppointment(reportId, action)
  } finally {
    respondLoading.value[reportId] = false
  }
}

async function handleUpload(reportId, event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploadError.value[reportId]   = ''
  uploadLoading.value[reportId] = true
  try {
    await reportsStore.uploadSchedule(reportId, file)
  } catch {
    uploadError.value[reportId] = 'فشل الإرسال. حاول مجدداً.'
  } finally {
    uploadLoading.value[reportId] = false
    event.target.value = ''
  }
}

function greet() {
  const h = new Date().getHours()
  if (h < 12) return 'صباح الخير'
  if (h < 18) return 'مساء الخير'
  return 'مساء النور'
}
</script>

<template>
  <div class="dash">

    <!-- Header -->
    <div class="dash-header">
      <div class="header-left">
        <div class="header-avatar">
          {{ (auth.user?.first_name?.[0] || auth.user?.username?.[0] || '?').toUpperCase() }}
        </div>
        <div>
          <h2>{{ greet() }}, <span class="name-accent">{{ auth.user?.first_name || auth.user?.username }}</span> 👋</h2>
          <p class="subtitle">إليك ملخص بلاغاتك</p>
        </div>
      </div>
      <RouterLink to="/etudiant/new-report" class="btn-new">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        بلاغ جديد
      </RouterLink>
    </div>

    <!-- KPI cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon kpi-blue">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ reportsStore.stats.total || 0 }}</div>
          <div class="kpi-label">إجمالي البلاغات</div>
        </div>
        <div class="kpi-bar blue-bar"></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon kpi-amber">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ reportsStore.stats.new || 0 }}</div>
          <div class="kpi-label">جديدة</div>
        </div>
        <div class="kpi-bar amber-bar"></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon kpi-orange">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ reportsStore.stats.in_progress || 0 }}</div>
          <div class="kpi-label">قيد المعالجة</div>
        </div>
        <div class="kpi-bar orange-bar"></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon kpi-green">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ reportsStore.stats.resolved || 0 }}</div>
          <div class="kpi-label">تمت معالجتها</div>
        </div>
        <div class="kpi-bar green-bar"></div>
      </div>
    </div>

    <!-- Pending appointments banner -->
    <div v-if="pendingAppts.length > 0" class="appt-banner">
      <div class="banner-pulse"></div>
      <svg width="22" height="22" fill="none" stroke="#92400e" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      <div class="banner-text">
        <strong>{{ pendingAppts.length }} موعد في انتظار الرد</strong>
        <span>يرجى قبول أو رفض الموعد المقترح من مستشارك</span>
      </div>
    </div>

    <!-- Reports card -->
    <div class="reports-card">
      <div class="reports-head">
        <div class="rh-left">
          <svg width="18" height="18" fill="none" stroke="#1d4ed8" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          <h3>بلاغاتي</h3>
          <span v-if="reportsStore.reports.length" class="count-pill">{{ reportsStore.reports.length }}</span>
        </div>
      </div>

      <div v-if="reportsStore.loading" class="empty-state">
        <div class="spinner"></div>
        <p>جارٍ التحميل...</p>
      </div>

      <div v-else-if="fetchError" class="empty-state">
        <div class="empty-icon error-icon">
          <svg width="36" height="36" fill="none" stroke="#dc2626" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <p class="empty-title" style="color:#dc2626">خطأ في التحميل</p>
        <p class="empty-sub">تعذر الاتصال بالخادم. تحقق من اتصالك.</p>
        <button @click="retryFetch" class="btn-new-sm" style="border:none;cursor:pointer">إعادة المحاولة</button>
      </div>

      <div v-else-if="reportsStore.reports.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        </div>
        <p class="empty-title">لا توجد بلاغات حتى الآن</p>
        <p class="empty-sub">ستظهر بلاغاتك هنا بعد إرسالها</p>
        <RouterLink to="/etudiant/new-report" class="btn-new-sm">
          + أرسل أول بلاغ
        </RouterLink>
      </div>

      <div v-else class="reports-list">
        <div v-for="r in reportsStore.reports" :key="r.id" class="report-item">

          <!-- Top row -->
          <div class="ri-top">
            <div class="ri-left">
              <div class="ri-type-dot" :class="STATUS_MAP[r.status]?.cls?.replace('badge-','dot-')"></div>
              <span class="ri-type">{{ TYPES_LABELS[r.report_type] || r.report_type }}</span>
            </div>
            <span :class="['badge', STATUS_MAP[r.status]?.cls]">{{ STATUS_MAP[r.status]?.label || r.status }}</span>
          </div>

          <!-- Description -->
          <p :class="['ri-desc', expanded.has(r.id) && 'ri-desc--expanded']">{{ r.description }}</p>
          <button class="btn-expand" @click="toggleExpand(r.id)">
            {{ expanded.has(r.id) ? '▲ عرض أقل' : '▼ عرض الكل' }}
          </button>

          <!-- Meta -->
          <div class="ri-meta">
            <div v-if="r.counselor_name" class="meta-item">
              <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              {{ r.counselor_name }}
            </div>
            <div class="meta-item">
              <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              {{ new Date(r.created_at).toLocaleDateString('ar-MA', {day:'2-digit',month:'short',year:'numeric'}) }}
            </div>
          </div>

          <!-- Appointment block -->
          <div v-if="r.appointment" class="appt-block">
            <div class="appt-row">
              <div class="appt-cal-icon">
                <svg width="16" height="16" fill="none" stroke="#1d4ed8" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              </div>
              <div class="appt-info">
                <div class="appt-datetime">
                  {{ new Date(r.appointment.date).toLocaleDateString('ar-MA', {weekday:'long',day:'2-digit',month:'long',year:'numeric'}) }}
                  &nbsp;·&nbsp; {{ r.appointment.time.slice(0,5) }}
                </div>
                <div v-if="r.appointment.note" class="appt-note">{{ r.appointment.note }}</div>
              </div>
              <span :class="['appt-badge', 'appt-' + r.appointment.status]">
                {{ APPT_LABELS[r.appointment.status] || r.appointment.status }}
              </span>
            </div>

            <!-- Actions for proposed -->
            <div v-if="r.appointment.status === 'مقترح' && r.status !== 'تم الحل'" class="appt-actions">
              <p class="appt-prompt">هل يناسبك هذا الموعد؟</p>
              <div class="appt-btns">
                <button class="btn-accept" :disabled="respondLoading[r.id]" @click="respond(r.id, 'accept')">
                  <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                  قبول
                </button>
                <button class="btn-reject" :disabled="respondLoading[r.id]" @click="respond(r.id, 'reject')">
                  <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  رفض
                </button>
              </div>
            </div>

            <!-- Upload schedule -->
            <div v-if="r.appointment.status === 'مرفوض'" class="upload-block">
              <div class="upload-info">
                <svg width="15" height="15" fill="none" stroke="#92400e" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <p>شارك جدولك الزمني لمساعدة مستشارك في إيجاد موعد مناسب</p>
              </div>
              <div v-if="uploadError[r.id]" class="upload-error">{{ uploadError[r.id] }}</div>
              <label class="btn-upload" :class="{ loading: uploadLoading[r.id] }">
                <input type="file" accept="image/*,.pdf" style="display:none"
                       @change="handleUpload(r.id, $event)" :disabled="uploadLoading[r.id]" />
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/></svg>
                {{ uploadLoading[r.id] ? 'جارٍ الإرسال...' : 'إرسال جدولي الزمني' }}
              </label>
              <div v-if="r.schedule" class="schedule-ok">
                <svg width="13" height="13" fill="none" stroke="#16a34a" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                تم إرسال الجدول —
                <a :href="r.schedule.file_url" target="_blank" class="schedule-link">عرض الملف</a>
              </div>
            </div>
          </div>

          <!-- Waiting counselor -->
          <div v-else-if="r.status === 'قيد المعالجة'" class="waiting-box">
            <div class="wait-dot"></div>
            في انتظار اقتراح موعد من مستشارك
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ── Layout ── */
.dash { display: flex; flex-direction: column; gap: 24px; }

/* ── Header ── */
.dash-header {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 16px; padding: 26px 30px;
  background: linear-gradient(120deg, #0f172a 0%, #1e3a5f 55%, #1d4ed8 100%);
  border-radius: 18px; position: relative; overflow: hidden;
  box-shadow: 0 8px 32px rgba(29,78,216,0.25);
}
.dash-header::before {
  content: ''; position: absolute; top: -60px; right: -60px;
  width: 260px; height: 260px; border-radius: 50%;
  background: rgba(255,255,255,0.04); pointer-events: none;
}
.dash-header::after {
  content: ''; position: absolute; bottom: -70px; left: 35%;
  width: 200px; height: 200px; border-radius: 50%;
  background: rgba(255,255,255,0.03); pointer-events: none;
}

.header-left { display: flex; align-items: center; gap: 16px; position: relative; z-index: 1; }

.header-avatar {
  width: 50px; height: 50px; border-radius: 50%;
  background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.3);
  color: #ffffff; font-size: 1.2rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

.dash-header h2 { font-size: 1.45rem; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: -0.02em; }
.name-accent { color: #93c5fd; font-weight: 800; }
.subtitle { color: rgba(255,255,255,0.5); margin: 4px 0 0; font-size: 0.82rem; font-weight: 500; }

.btn-new {
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 7px;
  background: rgba(255,255,255,0.12); border: 1.5px solid rgba(255,255,255,0.25);
  color: #ffffff; font-weight: 700; font-size: 0.875rem;
  padding: 10px 20px; border-radius: 99px;
  text-decoration: none; cursor: pointer;
  white-space: nowrap; backdrop-filter: blur(8px);
  transition: background 0.2s, border-color 0.2s;
}
.btn-new:hover { background: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.4); }

/* ── KPI Grid ── */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; }

.kpi-card {
  background: #ffffff; border-radius: 14px; padding: 20px 18px;
  display: flex; align-items: center; gap: 15px;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.05), 0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.03);
  border: 1px solid #e2e8f0; position: relative; overflow: hidden;
  transition: transform 0.22s cubic-bezier(.25,.8,.25,1), box-shadow 0.22s, border-color 0.2s;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 0 0 1px rgba(29,78,216,0.1), 0 4px 16px rgba(0,0,0,0.07), 0 16px 40px rgba(0,0,0,0.06);
  border-color: #bfdbfe;
}

.kpi-bar { position: absolute; bottom: 0; left: 0; right: 0; height: 3px; }
.blue-bar   { background: linear-gradient(90deg, #1d4ed8, #3b82f6); }
.amber-bar  { background: linear-gradient(90deg, #d97706, #f59e0b); }
.orange-bar { background: linear-gradient(90deg, #ea580c, #f97316); }
.green-bar  { background: linear-gradient(90deg, #16a34a, #22c55e); }

.kpi-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
.kpi-blue   { background: linear-gradient(135deg, #1d4ed8, #3b82f6); }
.kpi-amber  { background: linear-gradient(135deg, #d97706, #f59e0b); }
.kpi-orange { background: linear-gradient(135deg, #ea580c, #f97316); }
.kpi-green  { background: linear-gradient(135deg, #15803d, #16a34a); }

.kpi-num   { font-size: 1.9rem; font-weight: 800; color: #0f172a; line-height: 1; letter-spacing: -0.03em; }
.kpi-label { font-size: 0.69rem; color: #94a3b8; margin-top: 5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-body  { flex: 1; }

/* ── Appointment Banner ── */
.appt-banner {
  display: flex; align-items: center; gap: 14px;
  background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 14px; padding: 16px 20px;
  position: relative; overflow: hidden;
}
.banner-pulse {
  position: absolute; right: 0; top: 0; bottom: 0; width: 4px;
  background: linear-gradient(180deg, #f59e0b, #d97706);
}
.banner-text { display: flex; flex-direction: column; gap: 2px; }
.banner-text strong { font-size: 0.88rem; color: #92400e; font-weight: 700; }
.banner-text span   { font-size: 0.78rem; color: #a16207; }

/* ── Reports Card ── */
.reports-card {
  background: #ffffff; border-radius: 14px;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.05), 0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.03);
  border: 1px solid #e2e8f0; overflow: hidden;
}

.reports-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 24px; border-bottom: 1px solid #f1f5f9;
}
.rh-left { display: flex; align-items: center; gap: 10px; }
.rh-left h3 { font-size: 0.92rem; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.01em; }
.count-pill {
  background: #eff6ff; color: #1d4ed8;
  font-size: 0.7rem; font-weight: 800;
  padding: 2px 9px; border-radius: 99px; border: 1px solid #bfdbfe;
}

/* ── Empty State ── */
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 52px 24px; color: #94a3b8; }
.empty-icon {
  width: 76px; height: 76px; background: #f8fafc; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; margin-bottom: 6px;
}
.error-icon { background: #fef2f2; }
.empty-title { font-size: 0.95rem; font-weight: 700; color: #64748b; margin: 0; }
.empty-sub   { font-size: 0.83rem; margin: 0; }

.btn-new-sm {
  margin-top: 6px;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  color: #ffffff; font-weight: 700; font-size: 0.84rem;
  padding: 9px 18px; border-radius: 10px; text-decoration: none;
  display: inline-block;
}

/* ── Spinner ── */
.spinner {
  width: 30px; height: 30px;
  border: 3px solid #e2e8f0; border-top-color: #1d4ed8;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Reports List ── */
.reports-list { display: flex; flex-direction: column; }

.report-item { padding: 20px 24px; border-bottom: 1px solid #f1f5f9; transition: background 0.13s; }
.report-item:last-child { border-bottom: none; }
.report-item:hover { background: #f9fbff; }

.ri-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.ri-left { display: flex; align-items: center; gap: 8px; }

.ri-type-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-new      { background: #1d4ed8; box-shadow: 0 0 0 3px #dbeafe; }
.dot-progress { background: #f97316; box-shadow: 0 0 0 3px #ffedd5; }
.dot-appt     { background: #f59e0b; box-shadow: 0 0 0 3px #fef3c7; }
.dot-done     { background: #16a34a; box-shadow: 0 0 0 3px #dcfce7; }

.ri-type { font-weight: 700; color: #0f172a; font-size: 0.92rem; }

.badge { font-size: 0.69rem; font-weight: 700; padding: 4px 12px; border-radius: 99px; letter-spacing: 0.03em; border: 1px solid; }
.badge-new      { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.badge-progress { background: #fff7ed; color: #c2410c; border-color: #fed7aa; }
.badge-appt     { background: #fefce8; color: #a16207; border-color: #fef08a; }
.badge-done     { background: #f0fdf4; color: #16a34a; border-color: #bbf7d0; }

.ri-desc {
  font-size: 0.855rem; color: #64748b; margin: 0 0 6px; line-height: 1.68;
  word-break: break-word;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.ri-desc--expanded { display: block; -webkit-line-clamp: unset; overflow: visible; }

.btn-expand {
  background: none; border: none; cursor: pointer;
  font-size: 0.75rem; font-weight: 700; color: #1d4ed8;
  padding: 0; margin-bottom: 10px; transition: opacity 0.15s;
}
.btn-expand:hover { opacity: 0.7; }

.ri-meta { display: flex; gap: 18px; flex-wrap: wrap; font-size: 0.77rem; color: #94a3b8; font-weight: 500; }
.meta-item { display: flex; align-items: center; gap: 5px; }

/* ── Appointment Block ── */
.appt-block { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 16px; margin-top: 14px; }
.appt-row { display: flex; align-items: flex-start; gap: 12px; }
.appt-cal-icon {
  width: 34px; height: 34px; background: #eff6ff; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.appt-info    { flex: 1; }
.appt-datetime { font-weight: 700; color: #0f172a; font-size: 0.87rem; }
.appt-note    { font-size: 0.79rem; color: #64748b; margin-top: 3px; }

.appt-badge { font-size: 0.69rem; font-weight: 700; padding: 4px 10px; border-radius: 99px; white-space: nowrap; margin-right: auto; border: 1px solid; }
.appt-مقترح { background: #dbeafe; color: #1d4ed8; border-color: #bfdbfe; }
.appt-مقبول { background: #dcfce7; color: #16a34a; border-color: #bbf7d0; }
.appt-مرفوض { background: #fee2e2; color: #dc2626; border-color: #fecaca; }

.appt-actions { margin-top: 14px; padding-top: 14px; border-top: 1px solid #e2e8f0; }
.appt-prompt { font-size: 0.83rem; color: #334155; margin: 0 0 10px; font-weight: 600; }
.appt-btns   { display: flex; gap: 10px; flex-wrap: wrap; }

.btn-accept {
  display: flex; align-items: center; gap: 6px;
  background: linear-gradient(135deg, #15803d, #16a34a);
  color: #ffffff; font-weight: 700; font-size: 0.84rem;
  padding: 9px 18px; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s;
}
.btn-accept:disabled { opacity: 0.6; }

.btn-reject {
  display: flex; align-items: center; gap: 6px;
  background: #ffffff; color: #dc2626; font-weight: 700; font-size: 0.84rem;
  padding: 9px 18px; border: 1px solid #fecaca; border-radius: 10px; cursor: pointer; transition: background 0.15s;
}
.btn-reject:hover { background: #fef2f2; }
.btn-reject:disabled { opacity: 0.6; }

/* ── Upload ── */
.upload-block { margin-top: 14px; padding-top: 14px; border-top: 1px solid #e2e8f0; }
.upload-info {
  display: flex; gap: 8px; align-items: flex-start;
  background: #fffbeb; border-radius: 10px; padding: 10px 12px; margin-bottom: 12px; border: 1px solid #fde68a;
}
.upload-info p { margin: 0; font-size: 0.82rem; color: #92400e; line-height: 1.5; }
.upload-error { font-size: 0.79rem; color: #dc2626; margin-bottom: 8px; }

.btn-upload {
  display: inline-flex; align-items: center; gap: 7px;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  color: #ffffff; font-weight: 700; font-size: 0.84rem;
  padding: 9px 16px; border-radius: 10px; cursor: pointer; transition: opacity 0.2s;
}
.btn-upload.loading { opacity: 0.7; cursor: default; }

.schedule-ok  { display: flex; align-items: center; gap: 6px; font-size: 0.81rem; color: #16a34a; margin-top: 10px; font-weight: 600; }
.schedule-link { color: #1d4ed8; font-weight: 700; text-decoration: none; }
.schedule-link:hover { text-decoration: underline; }

/* ── Waiting ── */
.waiting-box {
  display: flex; align-items: center; gap: 10px; font-size: 0.83rem; color: #92400e;
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px;
  padding: 10px 14px; margin-top: 14px; font-weight: 500;
}
.wait-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #f59e0b;
  flex-shrink: 0; animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{ opacity:1 } 50%{ opacity:0.25 } }
</style>
