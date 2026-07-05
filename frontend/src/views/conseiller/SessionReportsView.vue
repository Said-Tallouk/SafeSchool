<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportsStore } from '../../stores/reports'

const store = useReportsStore()
onMounted(() => store.fetchReports())

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

const PROGRESS_LABELS = {
  en_cours:     { label: 'قيد المتابعة',    color: '#f59e0b', bg: '#fffbeb' },
  amelioration: { label: 'تحسن ملحوظ',     color: '#3b82f6', bg: '#eff6ff' },
  resolu:       { label: 'تم الحل',         color: '#16a34a', bg: '#f0fdf4' },
}

// Reports with accepted appointment → need a session report form
const pending = computed(() =>
  store.reports.filter(r =>
    r.appointment?.status === 'مقبول' && !r.session_report
  )
)

// Reports already completed
const completed = computed(() =>
  store.reports.filter(r => r.session_report)
)

// Expanded completed cards
const expanded = ref(new Set())
function toggleExpand(id) {
  const s = new Set(expanded.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expanded.value = s
}

// Form state per report
const forms   = ref({})
const saving  = ref({})
const errors  = ref({})

function getForm(id) {
  if (!forms.value[id]) {
    forms.value[id] = { summary: '', solutions: '', progress: 'en_cours', notes: '' }
  }
  return forms.value[id]
}

async function submit(reportId) {
  const f = getForm(reportId)
  if (!f.summary.trim() || !f.solutions.trim()) {
    errors.value[reportId] = 'الملخص والحلول حقول مطلوبة.'
    return
  }
  errors.value[reportId] = ''
  saving.value[reportId] = true
  try {
    await store.submitSessionReport(reportId, f)
  } catch {
    errors.value[reportId] = 'خطأ أثناء الحفظ. حاول مجدداً.'
  } finally {
    saving.value[reportId] = false
  }
}
</script>

<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>تقارير الجلسات</h2>
        <p class="subtitle">نماذج ما بعد الموعد · الملفات المغلقة</p>
      </div>
      <div class="header-chips">
        <span class="chip chip-orange">{{ pending.length }} في الانتظار</span>
        <span class="chip chip-green">{{ completed.length }} مغلق</span>
      </div>
    </div>

    <div v-if="store.loading" class="empty-state">
      <div class="spinner"></div>
      <p>جارٍ التحميل...</p>
    </div>

    <template v-else>

      <!-- ── Section : formulaires en attente ── -->
      <section v-if="pending.length > 0" class="section">
        <div class="section-title">
          <div class="section-dot dot-orange"></div>
          نماذج للإكمال
          <span class="section-count">{{ pending.length }}</span>
        </div>

        <div class="cards">
          <div v-for="r in pending" :key="r.id" class="form-card">

            <!-- Card header -->
            <div class="card-top">
              <div class="card-top-left">
                <span class="dossier-num">#{{ r.numero_dossier || r.id }}</span>
                <div class="student-info">
                  <div class="student-avatar">{{ (r.student_name || '?')[0].toUpperCase() }}</div>
                  <div>
                    <div class="student-name">{{ r.student_name }}</div>
                    <div class="report-type">{{ TYPES_LABELS[r.report_type] || r.report_type }}</div>
                  </div>
                </div>
              </div>
              <div class="card-top-right">
                <div class="appt-block">
                  <svg width="14" height="14" fill="none" stroke="#1d4ed8" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  <span>{{ r.appointment?.date }} · {{ (r.appointment?.time || '').slice(0,5) }}</span>
                </div>
                <span class="badge-pending">نموذج مطلوب</span>
              </div>
            </div>

            <!-- Form body -->
            <div class="form-body">
              <div class="form-grid">

                <div class="field full">
                  <label>ملخص الجلسة <span class="required">*</span></label>
                  <textarea v-model="getForm(r.id).summary" rows="3"
                    placeholder="صف سير الجلسة والنقاط التي تمت مناقشتها مع الطالب..."></textarea>
                </div>

                <div class="field full">
                  <label>الحلول المقترحة <span class="required">*</span></label>
                  <textarea v-model="getForm(r.id).solutions" rows="3"
                    placeholder="اذكر الإجراءات والإجراءات والتوصيات المتخذة..."></textarea>
                </div>

                <div class="field">
                  <label>حالة التقدم</label>
                  <div class="progress-options">
                    <label v-for="(info, key) in PROGRESS_LABELS" :key="key"
                      :class="['progress-opt', getForm(r.id).progress === key && 'selected']"
                      :style="getForm(r.id).progress === key ? { borderColor: info.color, background: info.bg, color: info.color } : {}">
                      <input type="radio" :value="key" v-model="getForm(r.id).progress" hidden />
                      <span class="opt-dot" :style="{ background: info.color }"></span>
                      {{ info.label }}
                    </label>
                  </div>
                </div>

                <div class="field">
                  <label>ملاحظات إضافية <span class="optional">(اختياري)</span></label>
                  <textarea v-model="getForm(r.id).notes" rows="2"
                    placeholder="ملاحظات إضافية، الخطوات التالية..."></textarea>
                </div>

              </div>

              <div v-if="errors[r.id]" class="form-error">{{ errors[r.id] }}</div>

              <div class="form-actions">
                <button class="btn-submit" :disabled="saving[r.id]" @click="submit(r.id)">
                  <svg v-if="!saving[r.id]" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                  <div v-else class="btn-spinner"></div>
                  {{ saving[r.id] ? 'جارٍ الحفظ...' : 'تأكيد وإغلاق الملف' }}
                </button>
              </div>
            </div>

          </div>
        </div>
      </section>

      <!-- Empty pending -->
      <div v-else-if="completed.length === 0" class="empty-state">
        <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/></svg>
        <p>لا توجد نماذج في الانتظار</p>
        <span>تظهر النماذج بعد قبول موعد من قِبل الطالب</span>
      </div>

      <!-- ── Section : rapports clôturés ── -->
      <section v-if="completed.length > 0" class="section">
        <div class="section-title">
          <div class="section-dot dot-green"></div>
          الملفات المغلقة
          <span class="section-count">{{ completed.length }}</span>
        </div>

        <div class="completed-list">
          <div v-for="r in completed" :key="r.id" class="completed-card">

            <div class="completed-header" @click="toggleExpand(r.id)">
              <div class="completed-left">
                <span class="dossier-num">#{{ r.numero_dossier || r.id }}</span>
                <div class="student-avatar sm">{{ (r.student_name || '?')[0].toUpperCase() }}</div>
                <div>
                  <div class="student-name">{{ r.student_name }}</div>
                  <div class="report-type">{{ TYPES_LABELS[r.report_type] || r.report_type }}</div>
                </div>
              </div>
              <div class="completed-right">
                <span class="progress-badge"
                  :style="{
                    color: PROGRESS_LABELS[r.session_report.progress]?.color || '#16a34a',
                    background: PROGRESS_LABELS[r.session_report.progress]?.bg || '#f0fdf4'
                  }">
                  {{ PROGRESS_LABELS[r.session_report.progress]?.label || 'تم الحل' }}
                </span>
                <span class="date-label">{{ new Date(r.session_report.created_at).toLocaleDateString('ar-MA') }}</span>
                <svg :class="['chevron', expanded.has(r.id) && 'open']" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>
              </div>
            </div>

            <div v-if="expanded.has(r.id)" class="completed-body">
              <div v-if="r.appointment" class="appt-info">
                <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                جلسة بتاريخ {{ r.appointment.date }} الساعة {{ (r.appointment.time || '').slice(0,5) }}
              </div>
              <div class="detail-grid">
                <div class="detail-field">
                  <label>ملخص الجلسة</label>
                  <p>{{ r.session_report.summary || '—' }}</p>
                </div>
                <div class="detail-field">
                  <label>الحلول المقترحة</label>
                  <p>{{ r.session_report.solutions || '—' }}</p>
                </div>
                <div v-if="r.session_report.notes" class="detail-field full">
                  <label>ملاحظات إضافية</label>
                  <p>{{ r.session_report.notes }}</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

    </template>
  </div>
</template>

<style scoped>
.page { padding: 0; }

/* ── Header ── */
.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 32px; flex-wrap: wrap; gap: 12px;
}
.page-header h2 { font-size: 1.6rem; font-weight: 900; color: #1e293b; margin: 0; }
.subtitle { color: #6b7280; margin-top: 4px; font-size: 0.875rem; }
.header-chips { display: flex; gap: 8px; align-items: center; }
.chip { font-size: 0.78rem; font-weight: 700; padding: 5px 12px; border-radius: 20px; }
.chip-orange { background: #fff7ed; color: #ea580c; }
.chip-green  { background: #f0fdf4; color: #16a34a; }

/* ── Loading / Empty ── */
.empty-state { text-align: center; padding: 60px 24px; color: #94a3b8; display: flex; flex-direction: column; align-items: center; gap: 12px; background: white; border-radius: 16px; }
.empty-state p { font-size: 1rem; font-weight: 700; color: #64748b; margin: 0; }
.empty-state span { font-size: 0.85rem; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #1d4ed8; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Sections ── */
.section { margin-bottom: 36px; }
.section-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.8rem; font-weight: 800; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.07em;
  margin-bottom: 14px;
}
.section-dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-orange { background: #f59e0b; }
.dot-green  { background: #16a34a; }
.section-count {
  margin-left: 4px; background: #f1f5f9; color: #475569;
  font-size: 0.72rem; padding: 1px 8px; border-radius: 20px;
}

/* ── Form cards ── */
.cards { display: flex; flex-direction: column; gap: 16px; }

.form-card {
  background: white; border-radius: 18px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  border: 1.5px solid #e2e8f0;
  overflow: hidden;
}

.card-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 22px; background: #f8fafc;
  border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; gap: 12px;
}
.card-top-left { display: flex; align-items: center; gap: 14px; }
.card-top-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.dossier-num { font-size: 0.8rem; font-weight: 800; color: #94a3b8; }

.student-info { display: flex; align-items: center; gap: 10px; }
.student-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  color: white; font-weight: 900; font-size: 0.9rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.student-avatar.sm { width: 30px; height: 30px; font-size: 0.75rem; }
.student-name { font-size: 0.9rem; font-weight: 800; color: #1e293b; }
.report-type  { font-size: 0.75rem; color: #6b7280; margin-top: 1px; }

.appt-block {
  display: flex; align-items: center; gap: 6px;
  background: #eff6ff; border-radius: 8px; padding: 5px 11px;
  font-size: 0.8rem; font-weight: 700; color: #1d4ed8;
}
.badge-pending {
  background: #fff7ed; color: #ea580c;
  font-size: 0.72rem; font-weight: 800;
  padding: 4px 10px; border-radius: 20px;
}

/* ── Form body ── */
.form-body { padding: 22px; }
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}
@media (max-width: 700px) { .form-grid { grid-template-columns: 1fr; } }

.field { display: flex; flex-direction: column; gap: 6px; }
.field.full { grid-column: 1 / -1; }

.field label {
  font-size: 0.78rem; font-weight: 800; color: #374151;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.required { color: #ef4444; }
.optional  { color: #9ca3af; font-weight: 600; text-transform: none; letter-spacing: 0; }

.field textarea {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 10px 13px; font-size: 0.875rem; color: #1e293b;
  resize: vertical; font-family: inherit; line-height: 1.5;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #f9fafb;
}
.field textarea:focus {
  outline: none; border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(29,78,216,0.08);
  background: white;
}

/* Progress options */
.progress-options { display: flex; flex-direction: column; gap: 8px; }
.progress-opt {
  display: flex; align-items: center; gap: 9px;
  padding: 9px 13px; border-radius: 10px;
  border: 1.5px solid #e2e8f0; cursor: pointer;
  font-size: 0.85rem; font-weight: 600; color: #64748b;
  transition: all 0.18s; background: #f9fafb;
}
.progress-opt:hover { border-color: #cbd5e1; background: #f1f5f9; }
.opt-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

.form-error {
  background: #fef2f2; color: #dc2626; border-radius: 9px;
  padding: 10px 14px; font-size: 0.85rem; font-weight: 600;
  margin-bottom: 14px;
}

.form-actions { display: flex; justify-content: flex-end; }
.btn-submit {
  display: flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  color: white; border: none; border-radius: 11px;
  padding: 11px 24px; font-size: 0.875rem; font-weight: 800;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(29,78,216,0.3);
}
.btn-submit:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(29,78,216,0.4); }
.btn-submit:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
.btn-spinner {
  width: 15px; height: 15px; border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ── Completed list ── */
.completed-list { display: flex; flex-direction: column; gap: 8px; }

.completed-card {
  background: white; border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
  overflow: hidden;
}

.completed-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; cursor: pointer; transition: background 0.15s;
  flex-wrap: wrap; gap: 10px;
}
.completed-header:hover { background: #f8fafc; }

.completed-left  { display: flex; align-items: center; gap: 10px; }
.completed-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.progress-badge {
  font-size: 0.72rem; font-weight: 800;
  padding: 3px 10px; border-radius: 20px;
}
.date-label { font-size: 0.78rem; color: #9ca3af; font-weight: 600; }
.chevron { transition: transform 0.2s; }
.chevron.open { transform: rotate(180deg); }

.completed-body { border-top: 1px solid #f1f5f9; padding: 18px; }

.appt-info {
  display: flex; align-items: center; gap: 7px;
  font-size: 0.82rem; color: #1d4ed8; font-weight: 700;
  background: #eff6ff; border-radius: 8px; padding: 7px 12px;
  margin-bottom: 16px;
}

.detail-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
@media (max-width: 560px) { .detail-grid { grid-template-columns: 1fr; } }

.detail-field { display: flex; flex-direction: column; gap: 5px; }
.detail-field.full { grid-column: 1 / -1; }
.detail-field label {
  font-size: 0.72rem; font-weight: 800; color: #9ca3af;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.detail-field p { font-size: 0.875rem; color: #374151; line-height: 1.55; margin: 0; }
</style>
