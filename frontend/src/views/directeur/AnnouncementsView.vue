<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const annonces = ref([])
const loading  = ref(false)
const saving   = ref(false)
const alert    = ref({ show: false, type: '', msg: '' })
const showModal   = ref(false)
const deleteModal = ref({ show: false, id: null, titre: '' })
const isEdit      = ref(false)
const search      = ref('')
const filterCat   = ref('all')

const form       = ref({ titre: '', contenu: '', categorie: 'info', publie: true })
const editId     = ref(null)
const imageFile  = ref(null)
const previewUrl = ref(null)

function onImageChange(e) {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value  = file
  previewUrl.value = URL.createObjectURL(file)
}
function removeImage() { imageFile.value = null; previewUrl.value = null }

const CATS = [
  { value: 'info',      label: 'معلومة',  color: '#3b82f6', bg: '#eff6ff' },
  { value: 'urgence',   label: 'عاجل',    color: '#ef4444', bg: '#fef2f2' },
  { value: 'evenement', label: 'فعالية',  color: '#8b5cf6', bg: '#f5f3ff' },
  { value: 'alerte',    label: 'تنبيه',   color: '#f59e0b', bg: '#fffbeb' },
]

function catInfo(val) {
  return CATS.find(c => c.value === val) || CATS[0]
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/annonces/')
    annonces.value = data
  } catch { showAlert('error', 'حدث خطأ أثناء التحميل.') }
  finally { loading.value = false }
}

onMounted(load)

const filtered = computed(() => {
  let list = annonces.value
  if (filterCat.value !== 'all') list = list.filter(a => a.categorie === filterCat.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(a => a.titre.toLowerCase().includes(q) || a.contenu.toLowerCase().includes(q))
  }
  return list
})

const counts = computed(() => {
  const r = { all: annonces.value.length }
  CATS.forEach(c => { r[c.value] = annonces.value.filter(a => a.categorie === c.value).length })
  return r
})

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = { titre: '', contenu: '', categorie: 'info', publie: true }
  imageFile.value = null
  previewUrl.value = null
  showModal.value = true
}

function openEdit(a) {
  isEdit.value = true
  editId.value = a.id
  form.value = { titre: a.titre, contenu: a.contenu, categorie: a.categorie, publie: a.publie }
  imageFile.value = null
  previewUrl.value = a.photo_url || null
  showModal.value = true
}

async function save() {
  if (!form.value.titre.trim() || !form.value.contenu.trim()) {
    showAlert('error', 'العنوان والمحتوى إلزاميان.')
    return
  }
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('titre',     form.value.titre)
    fd.append('contenu',   form.value.contenu)
    fd.append('categorie', form.value.categorie)
    fd.append('publie',    form.value.publie)
    if (imageFile.value) fd.append('photo', imageFile.value)
    const headers = { 'Content-Type': 'multipart/form-data' }

    if (isEdit.value) {
      const { data } = await api.patch(`/annonces/${editId.value}/`, fd, { headers })
      const i = annonces.value.findIndex(a => a.id === editId.value)
      if (i !== -1) annonces.value[i] = data
      showAlert('success', 'تم تعديل الإعلان بنجاح.')
    } else {
      const { data } = await api.post('/annonces/', fd, { headers })
      annonces.value.unshift(data)
      showAlert('success', 'تم إنشاء الإعلان بنجاح.')
    }
    showModal.value = false
  } catch { showAlert('error', 'حدث خطأ أثناء الحفظ.') }
  finally { saving.value = false }
}

async function togglePublie(a) {
  try {
    const { data } = await api.patch(`/annonces/${a.id}/`, { publie: !a.publie })
    const i = annonces.value.findIndex(x => x.id === a.id)
    if (i !== -1) annonces.value[i] = data
  } catch { showAlert('error', 'حدث خطأ.') }
}

function askDelete(a) {
  deleteModal.value = { show: true, id: a.id, titre: a.titre }
}

async function confirmDelete() {
  try {
    await api.delete(`/annonces/${deleteModal.value.id}/`)
    annonces.value = annonces.value.filter(a => a.id !== deleteModal.value.id)
    showAlert('success', 'تم حذف الإعلان.')
  } catch { showAlert('error', 'حدث خطأ أثناء الحذف.') }
  finally { deleteModal.value.show = false }
}

function showAlert(type, msg) {
  alert.value = { show: true, type, msg }
  setTimeout(() => { alert.value.show = false }, 3500)
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ar-MA', { day:'2-digit', month:'short', year:'numeric' })
}
</script>

<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="20" height="20" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </div>
        <div>
          <h1>الإعلانات</h1>
          <p>أدِر الإعلانات الموجهة للطلاب والموظفين</p>
        </div>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        إعلان جديد
      </button>
    </div>

    <!-- Alert -->
    <transition name="slide-down">
      <div v-if="alert.show" :class="['alert', alert.type]">
        <svg v-if="alert.type === 'success'" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-5"/></svg>
        <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ alert.msg }}
      </div>
    </transition>

    <!-- Stats chips -->
    <div class="filter-row">
      <button :class="['chip', filterCat === 'all' && 'active-all']" @click="filterCat = 'all'">
        الكل <span class="chip-count">{{ counts.all }}</span>
      </button>
      <button v-for="c in CATS" :key="c.value"
              :class="['chip', filterCat === c.value && 'active-cat']"
              :style="filterCat === c.value ? `background:${c.bg};color:${c.color};border-color:${c.color}` : ''"
              @click="filterCat = c.value">
        {{ c.label }} <span class="chip-count">{{ counts[c.value] }}</span>
      </button>
      <div class="search-wrap">
        <svg width="14" height="14" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="search" placeholder="بحث…" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-row">
      <div class="spinner"></div>
      <span>جارٍ التحميل…</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!filtered.length" class="empty-state">
      <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
      <p>لم يتم العثور على إعلانات</p>
      <button class="btn-primary sm" @click="openCreate">إنشاء إعلان</button>
    </div>

    <!-- Table -->
    <div v-else class="table-wrap">
      <table class="ann-table">
        <thead>
          <tr>
            <th class="th-img"></th>
            <th class="th-title">الإعلان</th>
            <th class="th-cat">الفئة</th>
            <th class="th-date">التاريخ</th>
            <th class="th-status">الحالة</th>
            <th class="th-actions">إجراءات</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in filtered" :key="a.id" class="ann-row">

            <!-- Miniature -->
            <td class="td-img">
              <div class="thumb-wrap">
                <img v-if="a.photo_url" :src="a.photo_url" :alt="a.titre" class="thumb" />
                <div v-else class="thumb-empty">
                  <svg width="16" height="16" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                </div>
              </div>
            </td>

            <!-- Titre + extrait -->
            <td class="td-title">
              <div class="row-title">{{ a.titre }}</div>
              <div class="row-excerpt">{{ a.contenu }}</div>
            </td>

            <!-- Catégorie -->
            <td class="td-cat">
              <span class="cat-badge"
                :style="`background:${catInfo(a.categorie).bg};color:${catInfo(a.categorie).color};border-color:${catInfo(a.categorie).color}`">
                {{ catInfo(a.categorie).label }}
              </span>
            </td>

            <!-- Date -->
            <td class="td-date">{{ formatDate(a.created_at) }}</td>

            <!-- Statut -->
            <td class="td-status">
              <button :class="['toggle-btn', a.publie ? 'on' : 'off']" @click="togglePublie(a)">
                <span class="toggle-dot"></span>
                {{ a.publie ? 'منشور' : 'مخفي' }}
              </button>
            </td>

            <!-- Actions -->
            <td class="td-actions">
              <div class="action-group">
                <button class="icon-btn edit" @click="openEdit(a)" title="تعديل">
                  <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4z"/></svg>
                </button>
                <button class="icon-btn del" @click="askDelete(a)" title="حذف">
                  <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Modal créer / modifier ── -->
    <teleport to="body">
      <div v-if="showModal" class="overlay" @click.self="showModal = false">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEdit ? 'تعديل الإعلان' : 'إعلان جديد' }}</h2>
            <button class="close-btn" @click="showModal = false">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="mfield">
              <label>العنوان <span class="req">*</span></label>
              <input v-model="form.titre" type="text" placeholder="عنوان الإعلان" autofocus />
            </div>
            <div class="mfield">
              <label>الفئة</label>
              <div class="cat-select">
                <button v-for="c in CATS" :key="c.value"
                        :class="['cat-opt', form.categorie === c.value && 'selected']"
                        :style="form.categorie === c.value ? `background:${c.bg};color:${c.color};border-color:${c.color}` : ''"
                        type="button" @click="form.categorie = c.value">
                  {{ c.label }}
                </button>
              </div>
            </div>
            <div class="mfield">
              <label>المحتوى <span class="req">*</span></label>
              <textarea v-model="form.contenu" rows="5" placeholder="اكتب إعلانك هنا…"></textarea>
            </div>
            <!-- Image upload -->
            <div class="mfield">
              <label>صورة <span class="opt">(اختياري)</span></label>
              <div class="upload-zone" @click="$refs.imgInput.click()">
                <img v-if="previewUrl" :src="previewUrl" class="upload-preview" />
                <div v-else class="upload-placeholder">
                  <svg width="28" height="28" fill="none" stroke="#94a3b8" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                  <span>انقر لإضافة صورة</span>
                  <small>JPG, PNG — بحد أقصى 5 ميغابايت</small>
                </div>
                <div v-if="previewUrl" class="upload-change">تغيير الصورة</div>
              </div>
              <input ref="imgInput" type="file" accept="image/*" hidden @change="onImageChange" />
              <button v-if="previewUrl" type="button" class="btn-remove-img" @click.stop="removeImage">
                <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                حذف الصورة
              </button>
            </div>

            <div class="mfield row-check">
              <label class="check-label">
                <input type="checkbox" v-model="form.publie" />
                <span class="checkmark"></span>
                نشر فوراً
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showModal = false">إلغاء</button>
            <button class="btn-primary" :disabled="saving" @click="save">
              <div v-if="saving" class="spin-sm"></div>
              {{ isEdit ? 'حفظ التعديلات' : 'إنشاء الإعلان' }}
            </button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- ── Modal suppression ── -->
    <teleport to="body">
      <div v-if="deleteModal.show" class="overlay" @click.self="deleteModal.show = false">
        <div class="modal sm-modal">
          <div class="del-icon">
            <svg width="28" height="28" fill="none" stroke="#ef4444" stroke-width="2" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
          </div>
          <h3>حذف الإعلان؟</h3>
          <p>سيتم حذف « {{ deleteModal.titre }} » نهائياً.</p>
          <div class="del-actions">
            <button class="btn-cancel" @click="deleteModal.show = false">إلغاء</button>
            <button class="btn-danger" @click="confirmDelete">حذف</button>
          </div>
        </div>
      </div>
    </teleport>

  </div>
</template>

<style scoped lang="scss">
// ── Variables ──────────────────────────────────────────
$blue:        #1d4ed8;
$blue-light:  #eff6ff;
$teal:        #0891b2;
$green:       #16a34a;
$red:         #ef4444;
$slate-50:    #f8fafc;
$slate-100:   #f1f5f9;
$slate-200:   #e2e8f0;
$slate-400:   #94a3b8;
$slate-500:   #64748b;
$slate-900:   #0f172a;
$white:       #ffffff;
$radius-sm:   8px;
$radius-md:   12px;
$radius-lg:   16px;
$shadow-card: 0 1px 4px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.04);
$transition:  all 0.18s ease;

// ── Mixins ─────────────────────────────────────────────
@mixin flex-center { display: flex; align-items: center; justify-content: center; }
@mixin flex-between { display: flex; align-items: center; justify-content: space-between; }
@mixin truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
@mixin pill($bg, $color, $border) {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 11px; border-radius: 99px;
  background: $bg; color: $color; border: 1px solid $border;
  font-size: 0.71rem; font-weight: 700; cursor: pointer;
  transition: background 0.15s; white-space: nowrap;
}

* { box-sizing: border-box; }

.page { padding: 0; }

// ── Page Header ────────────────────────────────────────
.page-header {
  @include flex-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;

  .header-left {
    display: flex; align-items: center; gap: 14px;

    .header-icon {
      width: 44px; height: 44px;
      border-radius: 13px;
      background: linear-gradient(135deg, $blue, $teal);
      @include flex-center;
      flex-shrink: 0;
      box-shadow: 0 4px 14px rgba(29,78,216,0.3);
    }

    h1 { font-size: 1.3rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
    p  { font-size: 0.8rem; color: $slate-400; margin: 0; }
  }
}

// ── Buttons ────────────────────────────────────────────
.btn-primary {
  display: flex; align-items: center; gap: 7px;
  background: linear-gradient(135deg, $blue, $teal);
  color: $white; font-weight: 800; font-size: 0.875rem;
  padding: 10px 20px; border: none; border-radius: $radius-sm;
  cursor: pointer; transition: opacity 0.2s;
  box-shadow: 0 4px 12px rgba(29,78,216,0.28);

  &:hover:not(:disabled) { opacity: 0.88; }
  &:disabled { opacity: 0.6; cursor: default; }
  &.sm { padding: 8px 14px; font-size: 0.82rem; }
}

.btn-cancel {
  background: $slate-50; border: 1.5px solid $slate-200;
  color: $slate-500; font-weight: 700; font-size: 0.875rem;
  padding: 10px 18px; border-radius: $radius-sm; cursor: pointer;
  transition: border-color 0.15s;
  &:hover { border-color: $slate-400; }
}

.btn-danger {
  background: $red; color: $white;
  font-weight: 800; font-size: 0.875rem;
  padding: 10px 18px; border: none; border-radius: $radius-sm; cursor: pointer;
  transition: background 0.15s;
  &:hover { background: #dc2626; }
}

// ── Alert ──────────────────────────────────────────────
.alert {
  display: flex; align-items: center; gap: 9px;
  padding: 11px 15px; border-radius: 11px;
  font-size: 0.83rem; font-weight: 600;
  margin-bottom: 18px; border-right: 3px solid;

  &.success { background: #f0fdf4; border-color: $green; color: #15803d; }
  &.error   { background: #fef2f2; border-color: $red;   color: $red; }
}

.slide-down-enter-active, .slide-down-leave-active { transition: all .3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

// ── Filters ────────────────────────────────────────────
.filter-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 20px; flex-wrap: wrap;
}

.chip {
  display: flex; align-items: center; gap: 5px;
  padding: 7px 13px; border: 1.5px solid $slate-200;
  border-radius: 20px; background: $white;
  font-size: 0.8rem; font-weight: 700; color: $slate-500;
  cursor: pointer; transition: $transition;

  &:hover { border-color: $blue; color: $blue; }
  &.active-all { background: $blue; color: $white; border-color: $blue; }

  .chip-count {
    background: $slate-100; color: $slate-500;
    font-size: 0.7rem; font-weight: 800;
    padding: 1px 6px; border-radius: 10px;
  }
  &.active-all .chip-count { background: rgba(255,255,255,0.25); color: $white; }
}

.search-wrap {
  display: flex; align-items: center; gap: 7px;
  border: 1.5px solid $slate-200; border-radius: $radius-sm;
  padding: 7px 12px; background: $white; margin-right: auto;
  transition: border-color 0.15s;
  &:focus-within { border-color: $blue; }

  input {
    border: none; outline: none;
    font-size: 0.82rem; color: #1e293b; width: 180px;
  }
}

// ── Loading / Empty ────────────────────────────────────
.loading-row {
  display: flex; align-items: center; gap: 10px;
  color: $slate-400; font-size: 0.85rem;
  padding: 40px 0; justify-content: center;
}

.spinner {
  width: 20px; height: 20px;
  border: 2.5px solid $slate-200; border-top-color: $blue;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

.empty-state {
  text-align: center; padding: 60px 20px;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  p { color: $slate-400; font-size: 0.9rem; margin: 0; }
}

// ── Table ──────────────────────────────────────────────
.table-wrap {
  background: $white;
  border-radius: $radius-lg;
  border: 1px solid $slate-200;
  box-shadow: $shadow-card;
  overflow: hidden;
}

.ann-table {
  width: 100%;
  border-collapse: collapse;

  // En-têtes
  thead tr {
    background: $slate-50;
    border-bottom: 1px solid $slate-200;
  }

  th {
    padding: 11px 16px;
    font-size: 0.68rem; font-weight: 700;
    color: $slate-400; text-transform: uppercase;
    letter-spacing: 0.08em; text-align: right; white-space: nowrap;

    &.th-img     { width: 68px; }
    &.th-title   { min-width: 260px; }
    &.th-cat     { width: 130px; }
    &.th-date    { width: 120px; }
    &.th-status  { width: 120px; }
    &.th-actions { width: 90px; text-align: center; }
  }

  td { padding: 12px 16px; vertical-align: middle; }

  // Lignes
  .ann-row {
    border-bottom: 1px solid $slate-100;
    transition: background 0.13s;

    &:last-child { border-bottom: none; }
    &:hover { background: $slate-50; }
  }
}

// Miniature
.td-img { padding: 10px 8px 10px 16px; }

.thumb-wrap {
  width: 52px; height: 40px;
  border-radius: $radius-sm; overflow: hidden;
}

.thumb { width: 100%; height: 100%; object-fit: cover; display: block; }

.thumb-empty {
  width: 100%; height: 100%;
  background: $slate-100;
  @include flex-center;
  border-radius: $radius-sm;
}

// Titre + extrait
.row-title {
  font-size: 0.86rem; font-weight: 700;
  color: $slate-900; line-height: 1.35;
  @include truncate;
  max-width: 380px;
}

.row-excerpt {
  font-size: 0.75rem; color: $slate-400;
  margin-top: 3px; line-height: 1.4;
  @include truncate;
  max-width: 380px;
}

// Badge catégorie
.cat-badge {
  display: inline-block;
  font-size: 0.67rem; font-weight: 700;
  padding: 3px 10px; border-radius: 99px;
  letter-spacing: 0.05em; text-transform: uppercase;
  border: 1px solid; white-space: nowrap;
}

// Date
.td-date { font-size: 0.77rem; color: $slate-500; font-weight: 500; white-space: nowrap; }

// Toggle statut
.toggle-btn {
  &.on  { @include pill(#f0fdf4, #16a34a, #bbf7d0); &:hover { background: #dcfce7; } }
  &.off { @include pill($slate-50, $slate-400, $slate-200); &:hover { background: $slate-100; } }
}
.toggle-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

// Actions
.td-actions { text-align: center; }
.action-group { display: flex; align-items: center; justify-content: center; gap: 6px; }

.icon-btn {
  width: 30px; height: 30px; border-radius: $radius-sm;
  border: 1px solid; cursor: pointer;
  @include flex-center;
  transition: $transition;

  &.edit {
    color: $teal; border-color: #bae6fd; background: #f0f9ff;
    &:hover { background: $teal; color: $white; border-color: $teal; }
  }
  &.del {
    color: $red; border-color: #fecaca; background: #fef2f2;
    &:hover { background: $red; color: $white; border-color: $red; }
  }
}

// ── Modal ──────────────────────────────────────────────
.overlay {
  position: fixed; inset: 0;
  background: rgba(15,23,42,0.45);
  z-index: 200; @include flex-center;
  padding: 20px; backdrop-filter: blur(4px);
}

.modal {
  background: $white; border-radius: 18px;
  width: 100%; max-width: 520px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden;

  &.sm-modal {
    max-width: 380px; padding: 28px 24px;
    text-align: center;
    display: flex; flex-direction: column; align-items: center; gap: 10px;

    h3 { font-size: 1rem; font-weight: 900; color: #1e293b; margin: 0; }
    p  { font-size: 0.83rem; color: $slate-500; margin: 0; }
  }
}

.modal-header {
  @include flex-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid $slate-100;
  h2 { font-size: 1rem; font-weight: 900; color: #1e293b; margin: 0; }
}

.close-btn {
  background: $slate-50; border: none;
  border-radius: $radius-sm; cursor: pointer; padding: 6px;
  display: flex; transition: background 0.15s;
  &:hover { background: $slate-200; }
}

.modal-body {
  padding: 20px 24px;
  display: flex; flex-direction: column; gap: 14px;
}

.modal-footer {
  display: flex; justify-content: flex-end; gap: 10px;
  padding: 16px 24px; border-top: 1px solid $slate-100;
}

// Champs formulaire
.mfield {
  label {
    display: block; font-size: 0.78rem; font-weight: 700;
    color: #374151; margin-bottom: 6px;
  }

  input, textarea {
    width: 100%; border: 1.5px solid $slate-200;
    border-radius: $radius-sm; padding: 10px 12px;
    font-size: 0.875rem; outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    resize: vertical; font-family: inherit;

    &:focus {
      border-color: $blue;
      box-shadow: 0 0 0 3px rgba(29,78,216,0.07);
    }
  }

  &.row-check { flex-direction: row; align-items: center; }
}

.cat-select { display: flex; gap: 8px; flex-wrap: wrap; }

.cat-opt {
  padding: 6px 14px; border: 1.5px solid $slate-200;
  border-radius: 20px; background: $white;
  font-size: 0.78rem; font-weight: 700; color: $slate-500;
  cursor: pointer; transition: $transition;
  &:hover { border-color: $slate-400; }
}

.check-label {
  display: flex; align-items: center; gap: 9px;
  cursor: pointer; font-size: 0.83rem; font-weight: 600; color: #374151;
  input { accent-color: $blue; width: 16px; height: 16px; cursor: pointer; }
}

// Upload
.upload-zone {
  border: 2px dashed $slate-200; border-radius: $radius-md;
  cursor: pointer; overflow: hidden; position: relative;
  min-height: 130px; @include flex-center;
  transition: border-color 0.2s;
  &:hover { border-color: $blue; }
}

.upload-placeholder {
  display: flex; flex-direction: column; align-items: center; gap: 7px; padding: 20px;
  span  { font-size: 0.82rem; font-weight: 600; color: $slate-500; }
  small { font-size: 0.72rem; color: $slate-400; }
}

.upload-preview { width: 100%; max-height: 200px; object-fit: cover; display: block; }

.upload-change {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(0,0,0,0.5); color: $white;
  text-align: center; padding: 6px; font-size: 0.75rem; font-weight: 600;
}

.btn-remove-img {
  display: flex; align-items: center; gap: 6px;
  background: #fef2f2; color: #dc2626; border: none;
  font-size: 0.75rem; font-weight: 700; padding: 5px 12px;
  border-radius: $radius-sm; cursor: pointer; margin-top: 6px;
  transition: background 0.15s;
  &:hover { background: #fee2e2; }
}

// Misc
.del-icon {
  width: 56px; height: 56px; border-radius: 50%;
  background: #fef2f2; @include flex-center; margin-bottom: 4px;
}
.del-actions { display: flex; gap: 10px; margin-top: 6px; }
.req { color: $red; }
.opt { color: #9ca3af; font-weight: 500; font-size: 0.72rem; }
.spin-sm {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.35); border-top-color: $white;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
