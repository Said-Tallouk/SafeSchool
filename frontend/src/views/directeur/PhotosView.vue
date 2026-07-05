<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const photos   = ref([])
const loading  = ref(false)
const tab      = ref('professeurs')   // 'professeurs' | 'activites' | 'accueil'
const showForm = ref(false)
const saving   = ref(false)
const alert    = ref({ show: false, type: '', msg: '' })
const editId   = ref(null)

const SUBJECTS = [
  { value: 'education_islamique', label: 'التربية الإسلامية' },
  { value: 'histoire_geo',        label: 'التاريخ والجغرافيا' },
  { value: 'mathematiques',       label: 'الرياضيات' },
  { value: 'physique',            label: 'الفيزياء' },
  { value: 'francais',            label: 'الفرنسية' },
  { value: 'informatique',        label: 'الإعلاميات' },
  { value: 'anglais',             label: 'الإنجليزية' },
  { value: 'sport',               label: 'رياضة' },
  { value: 'svt',                 label: 'علوم الحياة والأرض' },
  { value: 'autre',               label: 'أخرى' },
]

const form = ref({ title: '', description: '', subject: '', order: 0, image: null })
const previewUrl = ref(null)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/photos/')
    photos.value = data
  } finally { loading.value = false }
}

onMounted(load)

const filtered = computed(() => photos.value.filter(p => p.category === tab.value))

const professeursCount = computed(() => photos.value.filter(p => p.category === 'professeurs').length)
const activitesCount   = computed(() => photos.value.filter(p => p.category === 'activites').length)
const accueilCount     = computed(() => photos.value.filter(p => p.category === 'accueil').length)

function openAdd() {
  editId.value = null
  form.value = { title: '', description: '', subject: '', order: 0, image: null }
  previewUrl.value = null
  showForm.value = true
}

function openEdit(p) {
  editId.value = p.id
  form.value = { title: p.title, description: p.description, subject: p.subject || '', order: p.order, image: null }
  previewUrl.value = p.image_url
  showForm.value = true
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  form.value.image = file
  previewUrl.value = URL.createObjectURL(file)
}

function closeForm() { showForm.value = false; editId.value = null }

function showMsg(type, msg) {
  alert.value = { show: true, type, msg }
  setTimeout(() => { alert.value.show = false }, 3500)
}

async function save() {
  if (!form.value.title.trim()) return showMsg('error', 'العنوان إلزامي.')
  if (!editId.value && !form.value.image) return showMsg('error', 'يرجى اختيار صورة.')
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('category', tab.value)
    fd.append('title', form.value.title)
    fd.append('description', form.value.description)
    fd.append('subject', form.value.subject)
    fd.append('order', form.value.order)
    if (form.value.image) fd.append('image', form.value.image)

    if (editId.value) {
      const { data } = await api.patch(`/photos/${editId.value}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      const i = photos.value.findIndex(p => p.id === editId.value)
      if (i !== -1) photos.value[i] = data
    } else {
      const { data } = await api.post('/photos/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      photos.value.unshift(data)
    }
    showMsg('success', editId.value ? 'تم تعديل الصورة.' : 'تمت إضافة الصورة.')
    closeForm()
  } catch { showMsg('error', 'حدث خطأ أثناء الحفظ.') }
  finally { saving.value = false }
}

async function remove(p) {
  if (!confirm(`هل تريد حذف "${p.title}"؟`)) return
  try {
    await api.delete(`/photos/${p.id}/`)
    photos.value = photos.value.filter(x => x.id !== p.id)
    showMsg('success', 'تم حذف الصورة.')
  } catch { showMsg('error', 'حدث خطأ أثناء الحذف.') }
}
</script>

<template>
  <div class="page">

    <!-- Alert -->
    <transition name="fade">
      <div v-if="alert.show" :class="['alert', alert.type]">
        <svg v-if="alert.type==='success'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
        <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ alert.msg }}
      </div>
    </transition>

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>إدارة الصور</h2>
        <p class="subtitle">نظّم صور الأساتذة وشريحة الاستقبال</p>
      </div>
      <button class="btn-add" @click="openAdd">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        إضافة صورة
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="['tab', tab==='professeurs' && 'active']" @click="tab='professeurs'">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
        الأساتذة
        <span class="tab-count">{{ professeursCount }}</span>
      </button>
      <button :class="['tab', tab==='accueil' && 'active']" @click="tab='accueil'">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        شريحة الاستقبال
        <span class="tab-count">{{ accueilCount }}</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="empty-state">
      <div class="spinner"></div><p>جارٍ التحميل…</p>
    </div>

    <!-- Empty -->
    <div v-else-if="filtered.length === 0" class="empty-state">
      <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
      <p>لا توجد صور لهذه الفئة</p>
      <span>انقر على "إضافة صورة" للبدء</span>
    </div>

    <!-- Grid -->
    <div v-else class="photo-grid">
      <div v-for="p in filtered" :key="p.id" class="photo-card">
        <div class="photo-wrap">
          <img :src="p.image_url" :alt="p.title" class="photo-img" />
          <div class="photo-overlay">
            <button class="ov-btn edit" @click="openEdit(p)" title="تعديل">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="ov-btn del" @click="remove(p)" title="حذف">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
            </button>
          </div>
        </div>
        <div class="photo-info">
          <div class="photo-title">{{ p.title }}</div>
          <div v-if="p.subject_label" class="photo-subject">{{ p.subject_label }}</div>
          <div v-if="p.description" class="photo-desc">{{ p.description }}</div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <transition name="modal">
      <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
        <div class="modal">

          <div class="modal-header">
            <h3>{{ editId ? 'تعديل الصورة' : 'إضافة صورة' }}</h3>
            <button class="modal-close" @click="closeForm">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <div class="modal-body">

            <!-- Upload zone -->
            <div class="upload-zone" @click="$refs.fileInput.click()">
              <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
              <div v-else class="upload-placeholder">
                <svg width="32" height="32" fill="none" stroke="#94a3b8" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                <span>انقر لاختيار صورة</span>
                <small>JPG, PNG, WebP — بحد أقصى 5 ميغابايت</small>
              </div>
              <div v-if="previewUrl" class="change-hint">انقر للتغيير</div>
            </div>
            <input ref="fileInput" type="file" accept="image/*" hidden @change="onFileChange" />

            <div class="form-grid">
              <div class="field full">
                <label>العنوان <span class="req">*</span></label>
                <input v-model="form.title" type="text" :placeholder="tab==='professeurs' ? 'مثال: الأستاذ أحمد بنعلي' : tab==='activites' ? 'مثال: يوم رياضي 2025' : 'مثال: منظر المؤسسة'" />
              </div>

              <div v-if="tab==='professeurs'" class="field">
                <label>المادة المدرَّسة</label>
                <select v-model="form.subject">
                  <option value="">— اختر —</option>
                  <option v-for="s in SUBJECTS" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>

              <div class="field" :class="tab!=='professeurs' && 'full'">
                <label>ترتيب العرض</label>
                <input v-model.number="form.order" type="number" min="0" placeholder="0" />
              </div>

              <div class="field full">
                <label>الوصف <span class="opt">(اختياري)</span></label>
                <textarea v-model="form.description" rows="2" :placeholder="tab==='professeurs' ? 'اللقب، سنوات الخبرة…' : 'وصف مختصر للنشاط…'"></textarea>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="closeForm">إلغاء</button>
            <button class="btn-save" :disabled="saving" @click="save">
              <div v-if="saving" class="btn-spin"></div>
              <svg v-else width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
              {{ saving ? 'جارٍ الحفظ…' : (editId ? 'تعديل' : 'إضافة') }}
            </button>
          </div>

        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
.page { padding: 0; }

/* Alert */
.alert {
  display: flex; align-items: center; gap: 9px;
  padding: 12px 16px; border-radius: 11px;
  font-size: 0.875rem; font-weight: 600;
  margin-bottom: 20px;
}
.alert.success { background: #f0fdf4; color: #15803d; }
.alert.error   { background: #fef2f2; color: #dc2626; }
.fade-enter-active, .fade-leave-active { transition: all 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* Header */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.page-header h2 { font-size: 1.6rem; font-weight: 900; color: #1e293b; margin: 0; }
.subtitle { color: #6b7280; margin-top: 4px; font-size: 0.875rem; }

.btn-add {
  display: flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  color: white; border: none; border-radius: 11px;
  padding: 11px 20px; font-size: 0.875rem; font-weight: 800;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(29,78,216,0.3);
}
.btn-add:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(29,78,216,0.4); }

/* Tabs */
.tabs { display: flex; gap: 8px; margin-bottom: 24px; }
.tab {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 18px; border-radius: 11px; border: 1.5px solid #e2e8f0;
  font-size: 0.875rem; font-weight: 700; color: #64748b;
  background: white; cursor: pointer; transition: all 0.2s;
}
.tab:hover { border-color: #1d4ed8; color: #1d4ed8; }
.tab.active { background: #eff6ff; border-color: #1d4ed8; color: #1d4ed8; }
.tab-count {
  background: #e2e8f0; color: #475569;
  font-size: 0.72rem; font-weight: 800;
  padding: 1px 8px; border-radius: 20px;
}
.tab.active .tab-count { background: #bfdbfe; color: #1d4ed8; }

/* Empty / Loading */
.empty-state { text-align: center; padding: 60px 24px; background: white; border-radius: 16px; display: flex; flex-direction: column; align-items: center; gap: 10px; color: #94a3b8; }
.empty-state p { font-size: 1rem; font-weight: 700; color: #64748b; margin: 0; }
.empty-state span { font-size: 0.85rem; }
.spinner { width: 30px; height: 30px; border: 3px solid #e2e8f0; border-top-color: #1d4ed8; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Photo grid */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}

.photo-card {
  background: white; border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  border: 1.5px solid #f1f5f9;
  overflow: hidden; transition: transform 0.2s, box-shadow 0.2s;
}
.photo-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }

.photo-wrap { position: relative; aspect-ratio: 3/4; overflow: hidden; background: #f8fafc; }
.photo-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.photo-card:hover .photo-img { transform: scale(1.04); }

.photo-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center; gap: 10px;
  opacity: 0; transition: opacity 0.2s;
}
.photo-card:hover .photo-overlay { opacity: 1; }

.ov-btn {
  width: 38px; height: 38px; border-radius: 50%; border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.ov-btn.edit { background: white; color: #1d4ed8; }
.ov-btn.del  { background: #fef2f2; color: #dc2626; }
.ov-btn:hover { transform: scale(1.1); }

.photo-info { padding: 12px 14px; }
.photo-title   { font-size: 0.875rem; font-weight: 800; color: #1e293b; margin-bottom: 3px; }
.photo-subject { display: inline-block; background: #eff6ff; color: #1d4ed8; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 20px; margin-bottom: 5px; }
.photo-desc    { font-size: 0.78rem; color: #6b7280; line-height: 1.4; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 999; padding: 20px;
}
.modal {
  background: white; border-radius: 20px;
  width: 100%; max-width: 560px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  max-height: 90vh; overflow-y: auto;
}
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95) translateY(-10px); }

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 22px 24px 18px; border-bottom: 1px solid #f1f5f9;
}
.modal-header h3 { font-size: 1.1rem; font-weight: 900; color: #1e293b; margin: 0; }
.modal-close {
  width: 32px; height: 32px; border-radius: 8px; border: none;
  background: #f8fafc; color: #64748b; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.modal-close:hover { background: #f1f5f9; }

.modal-body { padding: 20px 24px; }

/* Upload zone */
.upload-zone {
  border: 2px dashed #e2e8f0; border-radius: 14px;
  cursor: pointer; overflow: hidden; margin-bottom: 20px;
  transition: border-color 0.2s; position: relative;
  min-height: 160px; display: flex; align-items: center; justify-content: center;
}
.upload-zone:hover { border-color: #1d4ed8; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 24px; color: #94a3b8; }
.upload-placeholder span { font-size: 0.875rem; font-weight: 600; color: #64748b; }
.upload-placeholder small { font-size: 0.75rem; }
.preview-img { width: 100%; max-height: 220px; object-fit: cover; display: block; }
.change-hint {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(0,0,0,0.5); color: white;
  text-align: center; padding: 8px; font-size: 0.78rem; font-weight: 600;
}

/* Form */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.full { grid-column: 1 / -1; }
.field label { font-size: 0.78rem; font-weight: 800; color: #374151; text-transform: uppercase; letter-spacing: 0.05em; }
.req { color: #ef4444; }
.opt { color: #9ca3af; font-weight: 600; text-transform: none; letter-spacing: 0; }
.field input, .field select, .field textarea {
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  padding: 9px 12px; font-size: 0.875rem; color: #1e293b;
  font-family: inherit; background: #f9fafb;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.field textarea { resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus {
  outline: none; border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(29,78,216,0.08); background: white;
}

.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid #f1f5f9;
}
.btn-cancel {
  padding: 10px 20px; border-radius: 10px; border: 1.5px solid #e2e8f0;
  background: white; color: #64748b; font-weight: 700; font-size: 0.875rem;
  cursor: pointer; transition: all 0.2s;
}
.btn-cancel:hover { background: #f8fafc; }
.btn-save {
  display: flex; align-items: center; gap: 7px;
  padding: 10px 22px; border-radius: 10px; border: none;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  color: white; font-weight: 800; font-size: 0.875rem;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 3px 10px rgba(29,78,216,0.3);
}
.btn-save:disabled { opacity: 0.65; cursor: not-allowed; }
.btn-save:not(:disabled):hover { transform: translateY(-1px); }
.btn-spin { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.4); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
</style>
