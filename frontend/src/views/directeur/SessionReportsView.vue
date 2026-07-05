<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportsStore } from '../../stores/reports'

const store = useReportsStore()
onMounted(() => store.fetchReports())

const resolved = computed(() =>
  store.reports.filter(r => r.status === 'تم الحل' && r.session_report)
)

const expanded = ref(null)
function toggle(id) { expanded.value = expanded.value === id ? null : id }

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
</script>

<template>
  <div>
    <div class="page-header">
      <h2>تقارير الجلسات</h2>
      <p class="subtitle">جميع الملفات المغلقة مع تقارير جلساتها</p>
    </div>

    <div v-if="store.loading" class="empty">جارٍ التحميل...</div>

    <div v-else-if="resolved.length === 0" class="empty">
      لا توجد تقارير جلسات حتى الآن.
    </div>

    <div v-else class="list">
      <div v-for="r in resolved" :key="r.id" class="item">
        <div class="item-header" @click="toggle(r.id)">
          <div class="header-left">
            <span class="num">#{{ r.id }}</span>
            <span class="type">{{ TYPES_LABELS[r.report_type] || r.report_type }}</span>
            <span class="badge-done">تم الحل</span>
          </div>
          <div class="header-right">
            <span class="student">{{ r.student_name }}</span>
            <span v-if="r.counselor_name" class="counselor">{{ r.counselor_name }}</span>
            <span class="date">{{ new Date(r.created_at).toLocaleDateString('ar-MA') }}</span>
            <span class="chevron">{{ expanded === r.id ? '▲' : '▼' }}</span>
          </div>
        </div>

        <div v-if="expanded === r.id" class="item-body">
          <div v-if="r.appointment" class="appt-row">
            📅 الموعد: {{ r.appointment.date }} — {{ r.appointment.time }}
          </div>
          <div class="sr-grid">
            <div class="sr-field">
              <label>ملخص الجلسة</label>
              <p>{{ r.session_report.summary || '—' }}</p>
            </div>
            <div class="sr-field">
              <label>الحلول المقترحة</label>
              <p>{{ r.session_report.solutions || '—' }}</p>
            </div>
            <div v-if="r.session_report.notes" class="sr-field">
              <label>ملاحظات إضافية</label>
              <p>{{ r.session_report.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom:28px; }
.page-header h2 { font-size:1.6rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; }
.empty { text-align:center; padding:48px; color:#9ca3af; background:white; border-radius:16px; }
.list { display:flex; flex-direction:column; gap:12px; }
.item { background:white; border-radius:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); overflow:hidden; }
.item-header { display:flex; justify-content:space-between; align-items:center; padding:16px 20px; cursor:pointer; transition:background 0.2s; }
.item-header:hover { background:#f8fafc; }
.header-left  { display:flex; align-items:center; gap:10px; }
.header-right { display:flex; align-items:center; gap:12px; font-size:0.85rem; color:#6b7280; }
.num  { font-size:0.8rem; color:#9ca3af; }
.type { font-weight:700; color:#1e293b; }
.badge-done { background:#f0fdf4; color:#16a34a; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:20px; }
.student { color:#374151; font-weight:600; }
.counselor { background:#f0fdfa; color:#0d9488; font-size:0.78rem; font-weight:700; padding:2px 8px; border-radius:20px; }
.date { white-space:nowrap; }
.chevron { color:#9ca3af; }
.item-body { border-top:1px solid #f3f4f6; padding:20px; }
.appt-row { font-size:0.85rem; background:#f0fdf4; border-radius:8px; padding:8px 12px; color:#166534; margin-bottom:14px; }
.sr-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
@media (max-width:560px) { .sr-grid { grid-template-columns:1fr; } }
.sr-field label { font-size:0.8rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:0.05em; display:block; margin-bottom:4px; }
.sr-field p { font-size:0.9rem; color:#374151; line-height:1.5; }
</style>
