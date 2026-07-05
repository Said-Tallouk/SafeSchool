<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportsStore } from '../../stores/reports'
import { useNotifStore }   from '../../stores/notifications'

const store        = useReportsStore()
const notif        = useNotifStore()
const filterStatus = ref('all')
const search       = ref('')
const selected     = ref(null)
const modal        = ref('')   // 'appointment' | 'session'
const expanded     = ref(new Set())  // ids dont la description est dépliée

function toggleExpand(id) {
  const s = new Set(expanded.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expanded.value = s
}

// Appointment form — now also includes optional session report fields
const apptForm = ref({
  date: '', time: '', note: '',
  summary: '', solutions: '', sess_notes: '',
})
const sessForm = ref({ summary: '', solutions: '', notes: '' })

const loadingAppt = ref(false)
const loadingSess = ref(false)
const apptError   = ref('')
const sessError   = ref('')

onMounted(() => store.fetchReports())

const filtered = computed(() => {
  let list = store.reports
  if (filterStatus.value !== 'all')
    list = list.filter(r => r.status === filterStatus.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(r =>
      (r.student_name   || '').toLowerCase().includes(q) ||
      (r.student_classe || '').toLowerCase().includes(q) ||
      (r.report_type    || '').toLowerCase().includes(q) ||
      (r.description    || '').toLowerCase().includes(q) ||
      String(r.numero_dossier || r.id).includes(q)
    )
  }
  return list
})

const STATUS_MAP = {
  'جديد':         'badge-new',
  'قيد المعالجة': 'badge-progress',
  'موعد محدد':    'badge-appt',
  'تم الحل':      'badge-done',
}

const STATUS_LABELS = {
  'جديد':         'جديد',
  'قيد المعالجة': 'قيد المعالجة',
  'موعد محدد':    'موعد محدد',
  'تم الحل':      'تم الحل',
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

const APPT_STATUS = {
  'مقترح': { cls: 'appt-proposed', label: 'في انتظار رد الطالب' },
  'مقبول': { cls: 'appt-accepted', label: 'مقبول من الطالب' },
  'مرفوض': { cls: 'appt-rejected', label: 'مرفوض — اقترح موعداً جديداً' },
}

const FILTER_OPTIONS = [
  { value: 'all',           label: 'الكل' },
  { value: 'قيد المعالجة', label: 'قيد المعالجة' },
  { value: 'موعد محدد',    label: 'موعد محدد' },
  { value: 'تم الحل',      label: 'تم الحل' },
]

function openModal(report, type) {
  selected.value  = report
  modal.value     = type
  apptError.value = ''
  sessError.value = ''
  apptForm.value  = { date: '', time: '', note: '', summary: '', solutions: '', sess_notes: '' }
  sessForm.value  = { summary: '', solutions: '', notes: '' }
}
function closeModal() { modal.value = ''; selected.value = null }

async function saveAppointment() {
  apptError.value = ''
  if (!apptForm.value.date || !apptForm.value.time) {
    apptError.value = 'الرجاء إدخال التاريخ والوقت.'
    return
  }
  loadingAppt.value = true
  try {
    await store.addAppointment(selected.value.id, {
      date: apptForm.value.date,
      time: apptForm.value.time,
      note: apptForm.value.note,
    })
    notif.success('تم إرسال الموعد إلى الطالب بنجاح!')
    closeModal()
  } catch (e) {
    apptError.value = e.response?.data?.error ||
      Object.values(e.response?.data || {}).flat()[0] ||
      'حدث خطأ ما.'
    notif.error('خطأ أثناء الحفظ.')
  } finally { loadingAppt.value = false }
}

async function saveSession() {
  sessError.value = ''
  if (!sessForm.value.summary.trim()) {
    sessError.value = 'الرجاء إدخال ملخص الجلسة.'
    return
  }
  loadingSess.value = true
  try {
    await store.submitSessionReport(selected.value.id, sessForm.value)
    notif.success('تم إغلاق الملف بنجاح!')
    closeModal()
  } catch (e) {
    sessError.value = e.response?.data?.error ||
      Object.values(e.response?.data || {}).flat()[0] ||
      'حدث خطأ ما.'
    notif.error('خطأ أثناء إغلاق الملف.')
  } finally { loadingSess.value = false }
}

function needsNewAppointment(r) {
  return r.status === 'قيد المعالجة' ||
    (r.appointment && r.appointment.status === 'مرفوض')
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>ملفاتي</h2>
      <p class="subtitle">البلاغات المُسندة إليك</p>
    </div>

    <!-- Barre de recherche + filtres -->
    <div class="toolbar">
      <div class="search-box">
        <svg width="15" height="15" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="search" type="text" placeholder="البحث عن طالب، قسم، نوع، رقم الملف..." />
        <button v-if="search" class="search-clear" @click="search = ''">
          <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="filter-chips">
        <button v-for="opt in FILTER_OPTIONS" :key="opt.value"
                :class="['filter-btn', filterStatus === opt.value && 'active']"
                @click="filterStatus = opt.value">
          {{ opt.label }}
          <span class="chip-count">{{ opt.value === 'all' ? store.reports.length : store.reports.filter(r => r.status === opt.value).length }}</span>
        </button>
      </div>
    </div>

    <div v-if="store.loading" class="empty">جارٍ التحميل...</div>
    <div v-else-if="filtered.length === 0" class="empty">
      <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <p>لا يوجد ملف<span v-if="search"> لـ « {{ search }} »</span>.</p>
    </div>

    <div v-else class="reports-list">
      <div v-for="r in filtered" :key="r.id" :class="['dossier-card', 'status-' + r.status.replace(/\s/g,'_')]">

        <!-- ── Card Header ── -->
        <div class="dossier-header">
          <div class="dossier-header-left">
            <span class="dossier-id">ملف #{{ r.numero_dossier || r.id }}</span>
            <span class="type-chip">{{ TYPES_LABELS[r.report_type] || r.report_type }}</span>
          </div>
          <div class="dossier-header-right">
            <span class="created-date">{{ new Date(r.created_at).toLocaleDateString('ar-MA', {day:'2-digit',month:'short',year:'numeric'}) }}</span>
            <span :class="['status-badge', STATUS_MAP[r.status]]">
              <span class="status-dot"></span>
              {{ STATUS_LABELS[r.status] || r.status }}
            </span>
          </div>
        </div>

        <!-- ── Card Body ── -->
        <div class="dossier-body">

          <!-- Left column -->
          <div class="dossier-main">

            <!-- Incident description -->
            <div class="section">
              <div class="section-title">وصف الحادثة</div>
              <p class="incident-text" :class="{ truncated: !expanded.has(r.id) }">{{ r.description }}</p>
              <button v-if="r.description && r.description.length > 180" class="expand-btn" @click="toggleExpand(r.id)">
                {{ expanded.has(r.id) ? '▲ تصغير' : '▼ عرض المزيد' }}
              </button>
              <div v-if="r.location" class="location-tag">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ r.location }}
              </div>
            </div>

            <!-- Appointment block -->
            <div v-if="r.appointment" :class="['appt-block', APPT_STATUS[r.appointment.status]?.cls]">
              <div class="appt-block-icon">📅</div>
              <div class="appt-block-content">
                <div class="appt-block-label">الموعد</div>
                <div class="appt-block-datetime">
                  {{ new Date(r.appointment.date).toLocaleDateString('ar-MA', {weekday:'long',day:'2-digit',month:'long',year:'numeric'}) }}
                  &nbsp;·&nbsp; {{ r.appointment.time.slice(0,5) }}
                </div>
                <div v-if="r.appointment.note" class="appt-block-note">{{ r.appointment.note }}</div>
              </div>
              <div class="appt-block-status">{{ APPT_STATUS[r.appointment.status]?.label }}</div>
            </div>

            <!-- Session report -->
            <div v-if="r.session_report" class="session-block">
              <div class="session-block-header">
                <span class="session-icon">📋</span>
                <span>تقرير الجلسة</span>
              </div>
              <div class="session-grid">
                <div class="session-field">
                  <div class="session-field-label">التقرير / الملاحظات</div>
                  <p>{{ r.session_report.summary }}</p>
                </div>
                <div v-if="r.session_report.solutions" class="session-field">
                  <div class="session-field-label">الحلول المقترحة</div>
                  <p>{{ r.session_report.solutions }}</p>
                </div>
                <div v-if="r.session_report.notes" class="session-field session-field-full">
                  <div class="session-field-label">ملاحظات</div>
                  <p>{{ r.session_report.notes }}</p>
                </div>
              </div>
            </div>

            <!-- Schedule badge -->
            <a v-if="r.schedule" :href="r.schedule.file_url" target="_blank" class="schedule-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
              جدول الطالب المشارك — عرض الملف
            </a>
          </div>

          <!-- Right column — Student + actions -->
          <div class="dossier-aside">

            <!-- Student card -->
            <div class="student-card">
              <div class="student-avatar">{{ (r.student_name || '?')[0].toUpperCase() }}</div>
              <div class="student-name">{{ r.student_name }}</div>
              <div v-if="r.student_classe" class="student-classe">{{ r.student_classe }}</div>
              <div class="student-contacts">
                <a v-if="r.student_telephone" :href="'tel:' + r.student_telephone" class="contact-item">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.63 3.37 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.55a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                  {{ r.student_telephone }}
                </a>
                <a v-if="r.student_email" :href="'mailto:' + r.student_email" class="contact-item">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                  {{ r.student_email }}
                </a>
              </div>
            </div>

            <!-- Actions -->
            <div class="aside-actions">
              <template v-if="r.status !== 'تم الحل'">
                <button v-if="needsNewAppointment(r)"
                        class="action-btn action-btn-teal"
                        @click="openModal(r, 'appointment')">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  {{ r.appointment?.status === 'مرفوض' ? 'موعد جديد' : 'تحديد موعد' }}
                </button>
                <button v-if="r.appointment && r.appointment.status === 'مقبول'"
                        class="action-btn action-btn-green action-btn-report"
                        @click="openModal(r, 'session')">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                  كتابة تقرير الجلسة
                </button>
              </template>
              <div v-else class="resolved-stamp">✔ تم إغلاق الملف</div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Modal -->
    <div v-if="modal === 'appointment'" class="overlay" @click.self="closeModal">
      <div class="modal">
        <h3>📅 تحديد موعد — ملف #{{ selected?.id }}</h3>
        <div v-if="apptError" class="alert error">{{ apptError }}</div>
        <div class="form">
          <div class="row2">
            <div class="field">
              <label>التاريخ <span class="req">*</span></label>
              <input v-model="apptForm.date" type="date" />
            </div>
            <div class="field">
              <label>الوقت <span class="req">*</span></label>
              <input v-model="apptForm.time" type="time" />
            </div>
          </div>
          <div class="field">
            <label>رسالة للطالب (اختياري)</label>
            <textarea v-model="apptForm.note" rows="3" placeholder="المكان، القاعة، تعليمات خاصة..."></textarea>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-outline" @click="closeModal">إلغاء</button>
          <button class="btn-teal" :disabled="loadingAppt" @click="saveAppointment">
            {{ loadingAppt ? 'جارٍ الإرسال...' : 'إرسال الموعد' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Session Report Modal -->
    <div v-if="modal === 'session'" class="overlay" @click.self="closeModal">
      <div class="modal modal-report">

        <!-- Modal header -->
        <div class="modal-report-header">
          <div class="modal-report-icon">📋</div>
          <div>
            <div class="modal-report-title">تقرير الجلسة</div>
            <div class="modal-report-sub">
              ملف #{{ selected?.id }} — {{ selected?.student_name }}
              <span v-if="selected?.appointment" class="modal-report-date">
                · جلسة بتاريخ {{ new Date(selected.appointment.date).toLocaleDateString('ar-MA', {day:'2-digit',month:'long',year:'numeric'}) }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="sessError" class="alert error">{{ sessError }}</div>

        <div class="form">
          <!-- Step 1 -->
          <div class="report-step">
            <div class="step-num">1</div>
            <div class="step-body">
              <label>التقرير والملاحظات <span class="req">*</span></label>
              <p class="step-hint">صف سير الجلسة وسلوك الطالب وحالته.</p>
              <textarea v-model="sessForm.summary" rows="4" required
                        placeholder="أظهر الطالب تعاوناً / الوقائع المُبلَّغ عنها هي..."></textarea>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="report-step">
            <div class="step-num">2</div>
            <div class="step-body">
              <label>الحلول والإجراءات المقترحة</label>
              <p class="step-hint">الإجراءات المتخذة والتوصيات والمتابعة المخططة بعد الجلسة.</p>
              <textarea v-model="sessForm.solutions" rows="3"
                        placeholder="وساطة بين الأطراف، إبلاغ الإدارة، متابعة أسبوعية..."></textarea>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="report-step">
            <div class="step-num">3</div>
            <div class="step-body">
              <label>ملاحظات إضافية</label>
              <p class="step-hint">أي ملاحظة سرية أو تعليق إضافي.</p>
              <textarea v-model="sessForm.notes" rows="2"
                        placeholder="المراجعة بعد أسبوعين / يُقترح التواصل مع الأولياء..."></textarea>
            </div>
          </div>
        </div>

        <div class="modal-report-footer">
          <button class="btn-outline" @click="closeModal">إلغاء</button>
          <button class="btn-green" :disabled="loadingSess" @click="saveSession">
            <svg v-if="!loadingSess" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            {{ loadingSess ? 'جارٍ الحفظ...' : 'حفظ وإغلاق الملف' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Page ── */
.page-header { margin-bottom:24px; }
.page-header h2 { font-size:1.6rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; }

/* Toolbar */
.toolbar { display:flex; flex-direction:column; gap:12px; margin-bottom:24px; }
.search-box {
  display:flex; align-items:center; gap:10px;
  background:white; border:1.5px solid #e2e8f0;
  border-radius:12px; padding:10px 14px;
  transition:border-color 0.2s;
}
.search-box:focus-within { border-color:#1d4ed8; }
.search-box input { flex:1; border:none; outline:none; font-size:0.9rem; color:#1e293b; }
.search-box input::placeholder { color:#94a3b8; }
.search-clear { background:none; border:none; cursor:pointer; color:#94a3b8; padding:0; display:flex; }
.search-clear:hover { color:#1e293b; }
.filter-chips { display:flex; gap:8px; flex-wrap:wrap; }
.filter-btn { display:flex; align-items:center; gap:6px; padding:7px 14px; border:1.5px solid #e2e8f0; border-radius:20px; background:white; font-size:0.82rem; font-weight:700; color:#64748b; cursor:pointer; transition:all 0.2s; }
.filter-btn:hover { border-color:#1d4ed8; color:#1d4ed8; }
.filter-btn.active { background:#1d4ed8; border-color:#1d4ed8; color:white; }
.chip-count { background:rgba(0,0,0,0.08); font-size:0.7rem; font-weight:900; padding:1px 6px; border-radius:10px; }
.filter-btn.active .chip-count { background:rgba(255,255,255,0.25); }
.empty { text-align:center; padding:56px; color:#9ca3af; background:white; border-radius:20px; display:flex; flex-direction:column; align-items:center; gap:12px; }
.empty p { margin:0; font-size:0.9rem; }

/* Description truncate */
.incident-text.truncated { display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
.expand-btn { background:none; border:none; cursor:pointer; font-size:0.75rem; font-weight:700; color:#1d4ed8; padding:4px 0; margin-top:2px; }
.expand-btn:hover { color:#1e40af; }

/* ── Dossier Card ── */
.reports-list { display:flex; flex-direction:column; gap:16px; }

.dossier-card {
  background:white;
  border-radius:16px;
  box-shadow:0 2px 12px rgba(0,0,0,0.07);
  overflow:hidden;
  border-right:4px solid #e5e7eb;
  transition:box-shadow 0.2s;
}
.dossier-card:hover { box-shadow:0 6px 24px rgba(0,0,0,0.1); }
.dossier-card.status-جديد         { border-right-color:#1d4ed8; }
.dossier-card.status-قيد_المعالجة  { border-right-color:#f97316; }
.dossier-card.status-موعد_محدد     { border-right-color:#f59e0b; }
.dossier-card.status-تم_الحل       { border-right-color:#16a34a; }

/* ── Header ── */
.dossier-header {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 20px;
  background:#f8fafc;
  border-bottom:1px solid #f1f5f9;
}
.dossier-header-left { display:flex; align-items:center; gap:10px; }
.dossier-id { font-size:0.78rem; font-weight:700; color:#94a3b8; letter-spacing:0.04em; }
.type-chip {
  background:#1e293b; color:white;
  font-size:0.75rem; font-weight:700;
  padding:3px 10px; border-radius:20px;
}
.dossier-header-right { display:flex; align-items:center; gap:12px; }
.created-date { font-size:0.78rem; color:#94a3b8; }
.status-badge {
  display:flex; align-items:center; gap:5px;
  font-size:0.78rem; font-weight:700;
  padding:4px 12px; border-radius:20px;
}
.status-dot { width:6px; height:6px; border-radius:50%; background:currentColor; }
.badge-new      { background:#eff6ff; color:#1d4ed8; }
.badge-progress { background:#fff7ed; color:#c2410c; }
.badge-appt     { background:#fefce8; color:#a16207; }
.badge-done     { background:#f0fdf4; color:#16a34a; }

/* ── Body ── */
.dossier-body {
  display:grid;
  grid-template-columns:1fr 220px;
  gap:0;
}
@media (max-width:700px) {
  .dossier-body { grid-template-columns:1fr; }
}

/* ── Main column ── */
.dossier-main { padding:20px; border-left:1px solid #f1f5f9; display:flex; flex-direction:column; gap:16px; }

.section-title {
  font-size:0.72rem; font-weight:800;
  color:#94a3b8; text-transform:uppercase; letter-spacing:0.07em;
  margin-bottom:8px;
}
.incident-text {
  font-size:0.9rem; color:#334155; line-height:1.65;
  background:#f8fafc; border-radius:10px;
  padding:12px 14px;
  word-break:break-word; overflow-wrap:anywhere;
  border-right:3px solid #e2e8f0;
}
.location-tag {
  display:inline-flex; align-items:center; gap:5px;
  font-size:0.78rem; color:#64748b; margin-top:8px;
}

/* Appointment block */
.appt-block {
  display:flex; align-items:flex-start; gap:12px;
  border-radius:12px; padding:14px 16px;
  border:1px solid;
}
.appt-proposed { background:#f0f9ff; border-color:#bae6fd; color:#0369a1; }
.appt-accepted { background:#f0fdf4; border-color:#bbf7d0; color:#166534; }
.appt-rejected { background:#fef2f2; border-color:#fecaca; color:#dc2626; }
.appt-block-icon { font-size:1.4rem; flex-shrink:0; margin-top:2px; }
.appt-block-content { flex:1; }
.appt-block-label { font-size:0.72rem; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; opacity:0.7; margin-bottom:4px; }
.appt-block-datetime { font-size:0.95rem; font-weight:700; }
.appt-block-note { font-size:0.82rem; opacity:0.8; margin-top:4px; }
.appt-block-status { font-size:0.75rem; font-weight:700; white-space:nowrap; align-self:center; }

/* Session report */
.session-block {
  background:#f8fafc;
  border:1px solid #e2e8f0;
  border-radius:12px;
  overflow:hidden;
}
.session-block-header {
  display:flex; align-items:center; gap:8px;
  padding:10px 14px;
  background:#f1f5f9;
  font-size:0.78rem; font-weight:800;
  color:#475569; text-transform:uppercase; letter-spacing:0.06em;
  border-bottom:1px solid #e2e8f0;
}
.session-grid {
  display:grid; grid-template-columns:1fr 1fr; gap:1px;
  background:#e2e8f0;
}
.session-field {
  background:white; padding:12px 14px;
}
.session-field-full { grid-column:span 2; }
.session-field-label {
  font-size:0.72rem; font-weight:700; color:#94a3b8;
  text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;
}
.session-field p { font-size:0.875rem; color:#334155; line-height:1.6; margin:0; }

/* Schedule badge */
.schedule-badge {
  display:inline-flex; align-items:center; gap:6px;
  background:#fefce8; border:1px solid #fde68a;
  color:#92400e; font-size:0.82rem; font-weight:600;
  padding:8px 14px; border-radius:10px;
  text-decoration:none; transition:background 0.2s;
}
.schedule-badge:hover { background:#fef9c3; }

/* ── Aside column ── */
.dossier-aside {
  padding:20px 16px;
  display:flex; flex-direction:column; gap:16px;
  background:#fafafa;
}

/* Student card */
.student-card {
  background:white; border:1px solid #f1f5f9;
  border-radius:12px; padding:16px; text-align:center;
}
.student-avatar {
  width:48px; height:48px; border-radius:50%;
  background:linear-gradient(135deg,#0d9488,#0891b2);
  color:white; font-size:1.2rem; font-weight:800;
  display:flex; align-items:center; justify-content:center;
  margin:0 auto 10px;
}
.student-name { font-size:0.95rem; font-weight:800; color:#1e293b; margin-bottom:2px; }
.student-classe {
  display:inline-block;
  background:#f1f5f9; color:#64748b;
  font-size:0.75rem; font-weight:700;
  padding:2px 10px; border-radius:20px; margin-bottom:12px;
}
.student-contacts { display:flex; flex-direction:column; gap:6px; }
.contact-item {
  display:flex; align-items:center; gap:6px;
  font-size:0.8rem; color:#1d4ed8;
  text-decoration:none; padding:5px 8px;
  background:#f8fafc; border-radius:8px;
  transition:background 0.2s;
}
.contact-item:hover { background:#eff6ff; }

/* Actions */
.aside-actions { display:flex; flex-direction:column; gap:8px; }
.action-btn {
  display:flex; align-items:center; justify-content:center; gap:7px;
  width:100%; padding:10px 14px;
  font-size:0.85rem; font-weight:700;
  border:none; border-radius:10px; cursor:pointer;
  transition:opacity 0.2s;
}
.action-btn:disabled { opacity:0.6; cursor:default; }
.action-btn-teal  { background:#0d9488; color:white; }
.action-btn-green { background:#16a34a; color:white; }
.action-btn-pdf   { background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; }
.action-btn-pdf:hover { background:#e2e8f0; opacity:1; }
.action-btn-report { font-size:0.82rem; }
.action-btn:hover:not(:disabled) { opacity:0.88; }

.resolved-stamp {
  text-align:center; font-size:0.82rem; font-weight:700;
  color:#16a34a; background:#f0fdf4;
  border:1px solid #bbf7d0; border-radius:10px;
  padding:10px;
}

/* ── Modal ── */
.overlay { position:fixed; inset:0; background:rgba(15,23,42,0.5); display:flex; align-items:center; justify-content:center; z-index:200; padding:16px; }
.modal { background:white; border-radius:20px; padding:28px; width:100%; max-width:540px; max-height:90vh; overflow-y:auto; }
.modal h3 { font-size:1.1rem; font-weight:800; margin-bottom:20px; color:#1e293b; }
.alert.error { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:10px 14px; font-size:0.875rem; margin-bottom:14px; }
.form { display:flex; flex-direction:column; gap:14px; }
.field label { display:block; font-size:0.85rem; font-weight:700; color:#374151; margin-bottom:5px; }
.req { color:#dc2626; }
.field input, .field textarea { width:100%; border:1.5px solid #e5e7eb; border-radius:10px; padding:10px 12px; font-size:0.9rem; outline:none; resize:vertical; transition:border-color 0.2s; box-sizing:border-box; font-family:inherit; }
.field input:focus, .field textarea:focus { border-color:#0d9488; }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:20px; }
.btn-outline { background:white; color:#374151; font-weight:700; font-size:0.9rem; padding:10px 20px; border:1.5px solid #e5e7eb; border-radius:10px; cursor:pointer; }
.btn-teal  { background:#0d9488; color:white; font-weight:700; font-size:0.9rem; padding:10px 22px; border:none; border-radius:10px; cursor:pointer; transition:opacity 0.2s; }
.btn-teal:disabled { opacity:0.7; }
.btn-green { background:#16a34a; color:white; font-weight:700; font-size:0.9rem; padding:10px 22px; border:none; border-radius:10px; cursor:pointer; transition:opacity 0.2s; }
.btn-green:disabled { opacity:0.7; }
.row2 { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.section-label { font-size:0.78rem; font-weight:800; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; padding-bottom:8px; border-bottom:1px solid #f1f5f9; margin-bottom:2px; }
.section-label-report { color:#0d9488; border-color:#ccfbf1; margin-top:6px; display:flex; align-items:center; gap:8px; }
.optional-tag { font-size:0.72rem; font-weight:600; background:#f0fdfa; color:#0d9488; padding:2px 8px; border-radius:20px; text-transform:none; letter-spacing:0; }

/* ── Session Report Modal ── */
.modal-report { max-width:600px; padding:0; overflow:hidden; }

.modal-report-header {
  display:flex; align-items:center; gap:14px;
  padding:22px 28px;
  background:linear-gradient(135deg,#16a34a,#0d9488);
  color:white;
}
.modal-report-icon { font-size:2rem; flex-shrink:0; }
.modal-report-title { font-size:1.05rem; font-weight:900; }
.modal-report-sub { font-size:0.8rem; opacity:0.85; margin-top:2px; }
.modal-report-date { opacity:0.75; }

.modal-report .form {
  padding:20px 28px;
  display:flex; flex-direction:column; gap:0;
}

.report-step {
  display:flex; gap:14px;
  padding:16px 0;
  border-bottom:1px solid #f1f5f9;
}
.report-step:last-child { border-bottom:none; }

.step-num {
  width:26px; height:26px; border-radius:50%;
  background:#16a34a; color:white;
  font-size:0.78rem; font-weight:900;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0; margin-top:2px;
}
.step-body { flex:1; display:flex; flex-direction:column; gap:6px; }
.step-body label { font-size:0.87rem; font-weight:700; color:#1e293b; }
.step-hint { font-size:0.78rem; color:#94a3b8; line-height:1.4; margin:0; }
.step-body textarea {
  width:100%; border:1.5px solid #e5e7eb; border-radius:10px;
  padding:10px 12px; font-size:0.875rem; resize:vertical;
  outline:none; transition:border-color 0.2s; box-sizing:border-box;
}
.step-body textarea:focus { border-color:#16a34a; }

.modal-report-footer {
  display:flex; justify-content:flex-end; gap:10px;
  padding:16px 28px;
  background:#f8fafc;
  border-top:1px solid #e2e8f0;
}
.modal-report .alert.error { margin:0 28px 0; }
</style>
