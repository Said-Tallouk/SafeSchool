<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReportsStore }    from '../../stores/reports'
import { useCounselorsStore } from '../../stores/counselors'

const reportsStore   = useReportsStore()
const counselorsStore = useCounselorsStore()

const filterStatus = ref('all')
const selected     = ref(null)
const modal        = ref('') // 'assign' | 'detail'
const assignId     = ref('')
const assignError  = ref('')
const assignLoading = ref(false)

onMounted(() => {
  reportsStore.fetchReports().catch(() => {})
  counselorsStore.fetch().catch(() => {})
})

const filtered = computed(() => {
  const list = reportsStore.reports
  if (filterStatus.value === 'all') return list
  return list.filter(r => r.status === filterStatus.value)
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

const FILTER_OPTIONS = [
  { value: 'all',           label: 'الكل' },
  { value: 'جديد',         label: 'جديد' },
  { value: 'قيد المعالجة', label: 'قيد المعالجة' },
  { value: 'موعد محدد',    label: 'موعد محدد' },
  { value: 'تم الحل',      label: 'تم الحل' },
]

function openAssign(r) {
  selected.value  = r
  modal.value     = 'assign'
  assignId.value  = r.counselor || ''
  assignError.value = ''
}
function openDetail(r) { selected.value = r; modal.value = 'detail' }
function closeModal() { modal.value = ''; selected.value = null }

async function saveAssign() {
  if (!assignId.value) { assignError.value = 'الرجاء اختيار مستشار.'; return }
  assignLoading.value = true
  assignError.value   = ''
  try {
    await reportsStore.assignCounselor(selected.value.id, Number(assignId.value))
    closeModal()
  } catch (e) {
    assignError.value = e.response?.data?.error || 'حدث خطأ ما.'
  } finally { assignLoading.value = false }
}

async function deleteReport(id) {
  if (!confirm('هل أنت متأكد من حذف هذا البلاغ؟')) return
  await reportsStore.deleteReport(id)
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>البلاغات</h2>
      <p class="subtitle">إدارة جميع البلاغات وإسنادها للمستشارين</p>
    </div>

    <!-- Filter -->
    <div class="filter-bar">
      <button v-for="opt in FILTER_OPTIONS" :key="opt.value"
              :class="['filter-btn', filterStatus === opt.value && 'active']"
              @click="filterStatus = opt.value">
        {{ opt.label }}
        <span v-if="opt.value !== 'all'" class="count">
          {{ reportsStore.reports.filter(r => r.status === opt.value).length }}
        </span>
      </button>
    </div>

    <div v-if="reportsStore.loading" class="empty">جارٍ التحميل...</div>
    <div v-else-if="filtered.length === 0" class="empty">لا توجد بلاغات.</div>

    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>النوع</th>
            <th>الطالب</th>
            <th>الحالة</th>
            <th>المستشار</th>
            <th>التاريخ</th>
            <th>الإجراءات</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filtered" :key="r.id">
            <td class="id-cell">{{ r.id }}</td>
            <td><span class="type-text">{{ TYPES_LABELS[r.report_type] || r.report_type }}</span></td>
            <td>
              <div>{{ r.student_name }}</div>
              <div class="meta-sub">{{ r.student_classe }}</div>
            </td>
            <td><span :class="['badge', STATUS_MAP[r.status]]">{{ STATUS_LABELS[r.status] || r.status }}</span></td>
            <td>{{ r.counselor_name || '—' }}</td>
            <td class="date-cell">{{ new Date(r.created_at).toLocaleDateString('fr-FR') }}</td>
            <td>
              <div class="row-actions">
                <button class="btn-sm blue" @click="openDetail(r)">عرض</button>
                <button v-if="r.status !== 'تم الحل'" class="btn-sm teal" @click="openAssign(r)">
                  {{ r.counselor_name ? 'إعادة إسناد' : 'إسناد' }}
                </button>
                <button class="btn-sm red" @click="deleteReport(r.id)">حذف</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Detail Modal -->
    <div v-if="modal === 'detail'" class="overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-top">
          <h3>تفاصيل البلاغ #{{ selected?.id }}</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="detail-grid">
          <div class="detail-row"><label>النوع</label><span>{{ TYPES_LABELS[selected?.report_type] || selected?.report_type }}</span></div>
          <div class="detail-row"><label>الحالة</label><span :class="['badge', STATUS_MAP[selected?.status]]">{{ STATUS_LABELS[selected?.status] || selected?.status }}</span></div>
          <div class="detail-row"><label>الطالب</label><span>{{ selected?.student_name }} {{ selected?.student_classe ? '— ' + selected?.student_classe : '' }}</span></div>
          <div class="detail-row"><label>المستشار</label><span>{{ selected?.counselor_name || '—' }}</span></div>
          <div class="detail-row"><label>المكان</label><span>{{ selected?.location || '—' }}</span></div>
          <div class="detail-row"><label>المعتدي</label><span>{{ selected?.perpetrator || '—' }}</span></div>
          <div class="detail-row full"><label>الوصف</label><p>{{ selected?.description }}</p></div>
          <div v-if="selected?.appointment" class="detail-row full">
            <label>الموعد</label>
            <span>{{ selected.appointment.date }} — {{ selected.appointment.time }}</span>
          </div>
          <div v-if="selected?.session_report" class="detail-row full">
            <label>تقرير الجلسة</label>
            <p>{{ selected.session_report.summary }}</p>
          </div>
        </div>
        <div class="modal-actions">
          <button v-if="selected?.status !== 'تم الحل'" class="btn-teal" @click="openAssign(selected)">
            {{ selected?.counselor_name ? 'إعادة إسناد المستشار' : 'إسناد مستشار' }}
          </button>
          <button class="btn-outline" @click="closeModal">إغلاق</button>
        </div>
      </div>
    </div>

    <!-- Assign Modal -->
    <div v-if="modal === 'assign'" class="overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-top">
          <h3>إسناد البلاغ #{{ selected?.id }} لمستشار</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div v-if="assignError" class="alert error">{{ assignError }}</div>
        <div v-if="counselorsStore.counselors.length === 0" class="alert error">
          لا يوجد مستشار متاح. أنشئ مستشاراً أولاً في قسم "المستشارون".
        </div>
        <div v-else class="field">
          <label>اختر المستشار</label>
          <select v-model="assignId">
            <option value="">— اختر —</option>
            <option v-for="c in counselorsStore.counselors" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.gender === 'male' ? 'ذكر' : 'أنثى' }}) — {{ c.active_report_count }} ملف نشط
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-outline" @click="closeModal">إلغاء</button>
          <button class="btn-teal" :disabled="assignLoading" @click="saveAssign">
            {{ assignLoading ? 'جارٍ الإسناد...' : 'تأكيد الإسناد' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom:24px; }
.page-header h2 { font-size:1.6rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; }
.filter-bar { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; }
.filter-btn { display:flex; align-items:center; gap:6px; padding:7px 16px; border:1.5px solid #e5e7eb; border-radius:20px; background:white; font-size:0.85rem; font-weight:600; color:#6b7280; cursor:pointer; transition:all 0.2s; }
.filter-btn.active { background:#1d4ed8; border-color:#1d4ed8; color:white; }
.count { background:rgba(0,0,0,0.08); border-radius:20px; padding:1px 7px; font-size:0.75rem; }
.filter-btn.active .count { background:rgba(255,255,255,0.25); }
.empty { text-align:center; padding:48px; color:#9ca3af; background:white; border-radius:16px; }
.table-wrap { background:white; border-radius:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); overflow:auto; }
table { width:100%; border-collapse:collapse; min-width:700px; }
th { background:#f8fafc; padding:12px 16px; font-size:0.8rem; font-weight:700; color:#6b7280; text-align:left; border-bottom:1px solid #f1f5f9; white-space:nowrap; }
td { padding:14px 16px; font-size:0.875rem; color:#374151; border-bottom:1px solid #f8fafc; vertical-align:middle; }
tr:last-child td { border-bottom:none; }
tr:hover td { background:#fafafa; }
.id-cell { color:#9ca3af; font-size:0.8rem; }
.type-text { font-weight:600; }
.meta-sub { font-size:0.78rem; color:#9ca3af; }
.date-cell { font-size:0.8rem; color:#9ca3af; white-space:nowrap; }
.badge { font-size:0.75rem; font-weight:700; padding:4px 10px; border-radius:20px; white-space:nowrap; }
.badge-new      { background:#eff6ff; color:#1d4ed8; }
.badge-progress { background:#fff7ed; color:#c2410c; }
.badge-appt     { background:#fefce8; color:#a16207; }
.badge-done     { background:#f0fdf4; color:#16a34a; }
.row-actions { display:flex; gap:6px; }
.btn-sm { font-size:0.78rem; font-weight:700; padding:5px 12px; border:none; border-radius:8px; cursor:pointer; transition:opacity 0.2s; white-space:nowrap; }
.btn-sm.blue { background:#eff6ff; color:#1d4ed8; }
.btn-sm.teal { background:#f0fdfa; color:#0d9488; }
.btn-sm.red  { background:#fef2f2; color:#dc2626; }
.btn-sm:hover { opacity:0.8; }
/* Modal */
.overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:200; padding:16px; }
.modal { background:white; border-radius:20px; padding:28px; width:100%; max-width:560px; max-height:90vh; overflow-y:auto; }
.modal-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.modal-top h3 { font-size:1.1rem; font-weight:800; color:#1e293b; }
.close-btn { background:none; border:none; font-size:1.1rem; color:#9ca3af; cursor:pointer; }
.alert.error { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:10px 14px; font-size:0.875rem; margin-bottom:14px; }
.detail-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:20px; }
.detail-row { background:#f8fafc; border-radius:10px; padding:12px; }
.detail-row.full { grid-column:span 2; }
.detail-row label { font-size:0.75rem; font-weight:700; color:#9ca3af; display:block; margin-bottom:4px; }
.detail-row span, .detail-row p { font-size:0.9rem; color:#374151; margin:0; line-height:1.5; }
.field label { display:block; font-size:0.875rem; font-weight:700; color:#374151; margin-bottom:8px; }
.field select { width:100%; border:1.5px solid #e5e7eb; border-radius:10px; padding:11px 14px; font-size:0.9rem; outline:none; box-sizing:border-box; background:white; }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:20px; }
.btn-outline { background:white; color:#374151; font-weight:700; font-size:0.9rem; padding:10px 20px; border:1.5px solid #e5e7eb; border-radius:10px; cursor:pointer; }
.btn-teal { background:#0d9488; color:white; font-weight:700; font-size:0.9rem; padding:10px 20px; border:none; border-radius:10px; cursor:pointer; transition:opacity 0.2s; }
.btn-teal:disabled { opacity:0.7; }
</style>
