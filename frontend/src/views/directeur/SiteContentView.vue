<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(false)
const saving  = ref(false)
const alert   = ref({ show: false, type: '', msg: '' })

// All editable sections
const sections = ref([
  {
    id: 'hero',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>`,
    label: 'القسم الرئيسي',
    color: '#1d4ed8',
    bg: '#eff6ff',
    fields: [
      { key: 'hero_title',    label: 'العنوان الرئيسي',  type: 'text',     placeholder: 'مرحباً بكم في SafeSchool' },
      { key: 'hero_subtitle', label: 'العنوان الفرعي',   type: 'text',     placeholder: 'منصة الحماية المدرسية' },
      { key: 'hero_desc',     label: 'الوصف',             type: 'textarea', placeholder: 'أرسل بلاغاً بأمان وسرية تامة…' },
      { key: 'hero_btn',      label: 'نص الزر',           type: 'text',     placeholder: 'إرسال بلاغ' },
    ]
  },
  {
    id: 'about',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
    label: 'حول المدرسة',
    color: '#0891b2',
    bg: '#f0fdfe',
    fields: [
      { key: 'about_title', label: 'العنوان',     type: 'text',     placeholder: 'التزامنا' },
      { key: 'about_text',  label: 'النص',        type: 'textarea', placeholder: 'تلتزم مدرستنا بـ…' },
      { key: 'school_name', label: 'اسم المدرسة', type: 'text',     placeholder: 'ثانوية SafeSchool' },
      { key: 'school_city', label: 'المدينة',     type: 'text',     placeholder: 'الدار البيضاء' },
    ]
  },
  {
    id: 'contact',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81 19.79 19.79 0 01.22 1.18 2 2 0 012.18 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 7.09a16 16 0 006 6l1.06-1.06a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92z"/></svg>`,
    label: 'معلومات الاتصال',
    color: '#7c3aed',
    bg: '#f5f3ff',
    fields: [
      { key: 'contact_phone',   label: 'الهاتف',             type: 'text', placeholder: '05 XX XX XX XX' },
      { key: 'contact_email',   label: 'البريد الإلكتروني', type: 'text', placeholder: 'contact@safeschool.ma' },
      { key: 'contact_address', label: 'العنوان',            type: 'text', placeholder: '12 شارع المدرسة، الدار البيضاء' },
      { key: 'contact_hours',   label: 'ساعات العمل',        type: 'text', placeholder: 'الاثنين–الجمعة 08:00–17:00' },
    ]
  },
  {
    id: 'awareness',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`,
    label: 'رسائل التوعية',
    color: '#f59e0b',
    bg: '#fffbeb',
    fields: [
      { key: 'awareness_msg1', label: 'الرسالة 1', type: 'textarea', placeholder: 'لست وحدك. الكلام هو الفعل.' },
      { key: 'awareness_msg2', label: 'الرسالة 2', type: 'textarea', placeholder: 'كل بلاغ يُحدث فرقاً.' },
      { key: 'awareness_msg3', label: 'الرسالة 3', type: 'textarea', placeholder: 'شجاعتك يمكن أن تساعد طلاباً آخرين.' },
    ]
  },
  {
    id: 'footer',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="17" x2="21" y2="17"/><line x1="8" y1="21" x2="8" y2="17"/><line x1="16" y1="21" x2="16" y2="17"/></svg>`,
    label: 'تذييل الصفحة',
    color: '#64748b',
    bg: '#f8fafc',
    fields: [
      { key: 'footer_tagline',  label: 'الشعار',          type: 'text',     placeholder: 'معاً ضد التحرش المدرسي' },
      { key: 'footer_copyright',label: 'حقوق النشر',      type: 'text',     placeholder: '© 2025 SafeSchool. جميع الحقوق محفوظة.' },
      { key: 'footer_legal',    label: 'البيانات القانونية', type: 'textarea', placeholder: 'منصة سرية…' },
    ]
  },
])

// values map: key → value string
const values = ref({})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/site-content/')
    data.forEach(item => { values.value[item.key] = item.value })
  } catch { showAlert('error', 'حدث خطأ أثناء التحميل.') }
  finally { loading.value = false }
}

onMounted(load)

async function saveSection(section) {
  saving.value = section.id
  try {
    const payload = section.fields.map(f => ({
      key:          f.key,
      label:        f.label,
      value:        values.value[f.key] || '',
      content_type: f.type === 'image' ? 'image' : 'text',
    }))
    await api.post('/site-content/', payload)
    showAlert('success', `تم حفظ قسم « ${section.label} ».`)
  } catch { showAlert('error', 'حدث خطأ أثناء الحفظ.') }
  finally { saving.value = null }
}

async function saveAll() {
  saving.value = 'all'
  try {
    const payload = []
    sections.value.forEach(section => {
      section.fields.forEach(f => {
        payload.push({
          key:          f.key,
          label:        f.label,
          value:        values.value[f.key] || '',
          content_type: f.type === 'image' ? 'image' : 'text',
        })
      })
    })
    await api.post('/site-content/', payload)
    showAlert('success', 'تم حفظ جميع المحتوى بنجاح.')
  } catch { showAlert('error', 'حدث خطأ أثناء الحفظ الشامل.') }
  finally { saving.value = null }
}

function showAlert(type, msg) {
  alert.value = { show: true, type, msg }
  setTimeout(() => { alert.value.show = false }, 3500)
}

const activeSection = ref('hero')
</script>

<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="20" height="20" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
            <path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4z"/>
          </svg>
        </div>
        <div>
          <h1>محتوى الموقع</h1>
          <p>عدّل النصوص الظاهرة للزوار دون المساس بالكود</p>
        </div>
      </div>
      <button class="btn-save-all" :disabled="saving === 'all'" @click="saveAll">
        <div v-if="saving === 'all'" class="spin-sm"></div>
        <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
        </svg>
        حفظ الكل
      </button>
    </div>

    <!-- Alert -->
    <transition name="slide-down">
      <div v-if="alert.show" :class="['alert', alert.type]">
        <svg v-if="alert.type==='success'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-5"/></svg>
        <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ alert.msg }}
      </div>
    </transition>

    <!-- Loading -->
    <div v-if="loading" class="loading-row">
      <div class="spinner"></div><span>جارٍ تحميل المحتوى…</span>
    </div>

    <div v-else class="layout">

      <!-- ── Sidebar navigation ── -->
      <nav class="sections-nav">
        <p class="nav-title">الأقسام</p>
        <button v-for="s in sections" :key="s.id"
                :class="['nav-item', activeSection === s.id && 'active']"
                :style="activeSection === s.id ? `background:${s.bg};color:${s.color};border-color:${s.color}` : ''"
                @click="activeSection = s.id">
          <span class="nav-icon" v-html="s.icon"></span>
          {{ s.label }}
          <svg v-if="activeSection === s.id" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
      </nav>

      <!-- ── Section editor ── -->
      <div class="editor-area">
        <div v-for="section in sections" :key="section.id"
             v-show="activeSection === section.id"
             class="section-panel">

          <!-- Panel header -->
          <div class="panel-header" :style="`border-right: 4px solid ${section.color}`">
            <div class="panel-icon" :style="`background:${section.bg};color:${section.color}`"
                 v-html="section.icon"></div>
            <div>
              <h2>{{ section.label }}</h2>
              <p>عدّل نصوص هذا القسم</p>
            </div>
          </div>

          <!-- Fields -->
          <div class="fields-grid">
            <div v-for="field in section.fields" :key="field.key" class="field-block">
              <label>{{ field.label }}</label>
              <textarea v-if="field.type === 'textarea'"
                        v-model="values[field.key]"
                        :placeholder="field.placeholder"
                        rows="3"></textarea>
              <input v-else
                     v-model="values[field.key]"
                     type="text"
                     :placeholder="field.placeholder" />
              <div class="char-count">{{ (values[field.key] || '').length }} حرفاً</div>
            </div>
          </div>

          <!-- Preview -->
          <div class="preview-box">
            <div class="preview-label">
              <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              معاينة
            </div>
            <div class="preview-content">
              <div v-for="field in section.fields" :key="field.key" class="preview-row">
                <span class="preview-key">{{ field.label }}</span>
                <span class="preview-val">{{ values[field.key] || field.placeholder }}</span>
              </div>
            </div>
          </div>

          <!-- Save section -->
          <div class="panel-footer">
            <div class="footer-hint">
              <svg width="14" height="14" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              يتم تطبيق التعديلات فوراً بعد الحفظ.
            </div>
            <button class="btn-save" :style="`background:${section.color}`"
                    :disabled="saving === section.id" @click="saveSection(section)">
              <div v-if="saving === section.id" class="spin-sm"></div>
              <svg v-else width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              {{ saving === section.id ? 'جارٍ الحفظ…' : 'حفظ هذا القسم' }}
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.page { padding: 0; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon { width: 44px; height: 44px; border-radius: 13px; background: linear-gradient(135deg,#0f172a,#1d4ed8); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 14px rgba(29,78,216,0.3); }
.header-left h1 { font-size: 1.3rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
.header-left p  { font-size: 0.8rem; color: #94a3b8; margin: 0; }

.btn-save-all { display: flex; align-items: center; gap: 8px; background: #1e293b; color: white; font-weight: 800; font-size: 0.875rem; padding: 10px 18px; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.btn-save-all:hover:not(:disabled) { opacity: 0.85; }
.btn-save-all:disabled { opacity: 0.6; cursor: default; }

/* Alert */
.alert { display: flex; align-items: center; gap: 9px; padding: 11px 15px; border-radius: 11px; font-size: 0.83rem; font-weight: 600; margin-bottom: 18px; border-right: 3px solid; }
.alert.success { background: #f0fdf4; border-color: #16a34a; color: #15803d; }
.alert.error   { background: #fef2f2; border-color: #dc2626; color: #dc2626; }
.slide-down-enter-active, .slide-down-leave-active { transition: all .3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* Loading */
.loading-row { display: flex; align-items: center; gap: 10px; color: #94a3b8; font-size: 0.85rem; padding: 40px 0; justify-content: center; }
.spinner { width: 20px; height: 20px; border: 2.5px solid #e2e8f0; border-top-color: #1d4ed8; border-radius: 50%; animation: spin 0.7s linear infinite; }

/* Layout: sidebar + editor */
.layout { display: flex; gap: 20px; align-items: flex-start; }

/* Sidebar nav */
.sections-nav { width: 220px; flex-shrink: 0; background: white; border-radius: 14px; padding: 14px 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; position: sticky; top: 20px; }
.nav-title { font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; padding: 0 8px; margin: 0 0 10px; }
.nav-item { display: flex; align-items: center; gap: 9px; width: 100%; padding: 10px 12px; border: 1.5px solid transparent; border-radius: 10px; background: transparent; font-size: 0.82rem; font-weight: 700; color: #64748b; cursor: pointer; text-align: right; transition: all 0.2s; margin-bottom: 3px; }
.nav-item:hover:not(.active) { background: #f8fafc; color: #374151; }
.nav-item .nav-icon { display: flex; align-items: center; flex-shrink: 0; }
.nav-item svg:last-child { margin-right: auto; }

/* Editor area */
.editor-area { flex: 1; min-width: 0; }
.section-panel { display: flex; flex-direction: column; gap: 20px; }

/* Panel header */
.panel-header { display: flex; align-items: center; gap: 14px; background: white; border-radius: 14px; padding: 18px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.panel-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.panel-header h2 { font-size: 1rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
.panel-header p  { font-size: 0.75rem; color: #94a3b8; margin: 0; }

/* Fields grid */
.fields-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
@media(max-width: 900px) { .fields-grid { grid-template-columns: 1fr; } }

.field-block { background: white; border-radius: 12px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; }
.field-block label { display: block; font-size: 0.78rem; font-weight: 700; color: #374151; margin-bottom: 8px; }
.field-block input, .field-block textarea { width: 100%; border: 1.5px solid #e2e8f0; border-radius: 9px; padding: 9px 12px; font-size: 0.875rem; outline: none; transition: border-color 0.2s; resize: vertical; font-family: inherit; color: #1e293b; }
.field-block input:focus, .field-block textarea:focus { border-color: #1d4ed8; box-shadow: 0 0 0 3px rgba(29,78,216,0.07); }
.char-count { font-size: 0.68rem; color: #cbd5e1; text-align: right; margin-top: 5px; font-weight: 600; }

/* Preview */
.preview-box { background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 16px 18px; }
.preview-label { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; font-weight: 800; color: #94a3b8; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
.preview-content { display: flex; flex-direction: column; gap: 8px; }
.preview-row { display: flex; gap: 12px; align-items: baseline; }
.preview-key { font-size: 0.72rem; font-weight: 700; color: #94a3b8; width: 130px; flex-shrink: 0; }
.preview-val { font-size: 0.83rem; color: #374151; font-weight: 500; line-height: 1.5; }

/* Panel footer */
.panel-footer { display: flex; align-items: center; justify-content: space-between; background: white; border-radius: 12px; padding: 14px 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); gap: 12px; flex-wrap: wrap; }
.footer-hint { display: flex; align-items: center; gap: 7px; font-size: 0.77rem; color: #94a3b8; font-weight: 500; }
.btn-save { display: flex; align-items: center; gap: 8px; color: white; font-weight: 800; font-size: 0.875rem; padding: 10px 20px; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.btn-save:hover:not(:disabled) { opacity: 0.88; }
.btn-save:disabled { opacity: 0.65; cursor: default; }

.spin-sm { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.35); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg) } }
</style>
