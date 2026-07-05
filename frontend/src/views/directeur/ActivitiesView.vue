<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const activites = ref([])
const loading   = ref(false)
const saving    = ref(false)
const alert     = ref({ show: false, type: '', msg: '' })
const showModal    = ref(false)
const deleteModal  = ref({ show: false, id: null, titre: '' })
const isEdit       = ref(false)
const editId       = ref(null)
const search       = ref('')
const filterStatut = ref('all')

const form        = ref({ titre: '', description: '', date: '', heure: '', lieu: '', responsable: '', statut: 'planifiee' })
const photoFile   = ref(null)
const photoPreview = ref(null)

function onPhotoChange(e) {
  const f = e.target.files[0]
  if (!f) return
  photoFile.value   = f
  photoPreview.value = URL.createObjectURL(f)
}
function clearPhoto() {
  photoFile.value   = null
  photoPreview.value = null
}

const STATUTS = [
  { value: 'planifiee', label: 'مجدولة',  color: '#3b82f6', bg: '#eff6ff' },
  { value: 'en_cours',  label: 'جارية',   color: '#f59e0b', bg: '#fffbeb' },
  { value: 'terminee',  label: 'منتهية',  color: '#22c55e', bg: '#f0fdf4' },
  { value: 'annulee',   label: 'ملغاة',   color: '#94a3b8', bg: '#f8fafc' },
]

function statutInfo(val) {
  return STATUTS.find(s => s.value === val) || STATUTS[0]
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/activites/')
    activites.value = data
  } catch { showAlert('error', 'حدث خطأ أثناء التحميل.') }
  finally { loading.value = false }
}

onMounted(load)

const filtered = computed(() => {
  let list = activites.value
  if (filterStatut.value !== 'all') list = list.filter(a => a.statut === filterStatut.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.titre.toLowerCase().includes(q) ||
      (a.responsable || '').toLowerCase().includes(q) ||
      (a.lieu || '').toLowerCase().includes(q)
    )
  }
  return list
})

const counts = computed(() => {
  const r = { all: activites.value.length }
  STATUTS.forEach(s => { r[s.value] = activites.value.filter(a => a.statut === s.value).length })
  return r
})

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = { titre: '', description: '', date: '', heure: '', lieu: '', responsable: '', statut: 'planifiee' }
  clearPhoto()
  showModal.value = true
}

function openEdit(a) {
  isEdit.value = true
  editId.value = a.id
  form.value = {
    titre: a.titre, description: a.description || '',
    date: a.date, heure: a.heure || '',
    lieu: a.lieu || '', responsable: a.responsable || '',
    statut: a.statut
  }
  photoFile.value   = null
  photoPreview.value = a.photo_url || null
  showModal.value = true
}

async function save() {
  if (!form.value.titre.trim() || !form.value.date) {
    showAlert('error', 'العنوان والتاريخ إلزاميان.')
    return
  }
  saving.value = true
  try {
    let payload
    if (photoFile.value) {
      payload = new FormData()
      Object.entries(form.value).forEach(([k, v]) => { if (v !== '' && v != null) payload.append(k, v) })
      payload.append('photo', photoFile.value)
    } else {
      payload = { ...form.value }
      if (!payload.heure) delete payload.heure
    }
    const headers = photoFile.value ? { 'Content-Type': 'multipart/form-data' } : {}

    if (isEdit.value) {
      const { data } = await api.patch(`/activites/${editId.value}/`, payload, { headers })
      const i = activites.value.findIndex(a => a.id === editId.value)
      if (i !== -1) activites.value[i] = data
      showAlert('success', 'تم تعديل النشاط بنجاح.')
    } else {
      const { data } = await api.post('/activites/', payload, { headers })
      activites.value.unshift(data)
      showAlert('success', 'تم إنشاء النشاط بنجاح.')
    }
    showModal.value = false
  } catch { showAlert('error', 'حدث خطأ أثناء الحفظ.') }
  finally { saving.value = false }
}

async function changeStatut(a, newStatut) {
  try {
    const { data } = await api.patch(`/activites/${a.id}/`, { statut: newStatut })
    const i = activites.value.findIndex(x => x.id === a.id)
    if (i !== -1) activites.value[i] = data
  } catch { showAlert('error', 'حدث خطأ.') }
}

function askDelete(a) {
  deleteModal.value = { show: true, id: a.id, titre: a.titre }
}

async function confirmDelete() {
  try {
    await api.delete(`/activites/${deleteModal.value.id}/`)
    activites.value = activites.value.filter(a => a.id !== deleteModal.value.id)
    showAlert('success', 'تم حذف النشاط.')
  } catch { showAlert('error', 'حدث خطأ أثناء الحذف.') }
  finally { deleteModal.value.show = false }
}

function showAlert(type, msg) {
  alert.value = { show: true, type, msg }
  setTimeout(() => { alert.value.show = false }, 3500)
}

function formatDate(d) {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  return new Date(y, m - 1, day).toLocaleDateString('ar-MA', { day:'2-digit', month:'short', year:'numeric' })
}

function formatHeure(h) {
  if (!h) return ''
  return h.slice(0, 5)
}

// Today's date for input min
const today = new Date().toISOString().split('T')[0]
</script>

<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="20" height="20" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
            <path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>
          </svg>
        </div>
        <div>
          <h1>الأنشطة</h1>
          <p>خطّط وأدِر الأنشطة المدرسية</p>
        </div>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        نشاط جديد
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

    <!-- KPI row -->
    <div class="kpi-row">
      <div v-for="s in STATUTS" :key="s.value" class="kpi-card"
           :style="`border-top: 3px solid ${s.color}`">
        <div class="kpi-num" :style="`color:${s.color}`">{{ counts[s.value] }}</div>
        <div class="kpi-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-row">
      <button :class="['chip', filterStatut==='all' && 'active-all']" @click="filterStatut='all'">
        الكل <span class="chip-count">{{ counts.all }}</span>
      </button>
      <button v-for="s in STATUTS" :key="s.value"
              :class="['chip', filterStatut===s.value && 'active-cat']"
              :style="filterStatut===s.value ? `background:${s.bg};color:${s.color};border-color:${s.color}` : ''"
              @click="filterStatut = s.value">
        {{ s.label }} <span class="chip-count">{{ counts[s.value] }}</span>
      </button>
      <div class="search-wrap">
        <svg width="14" height="14" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="search" placeholder="بحث…" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-row">
      <div class="spinner"></div><span>جارٍ التحميل…</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!filtered.length" class="empty-state">
      <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24">
        <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <p>لم يتم العثور على أنشطة</p>
      <button class="btn-primary sm" @click="openCreate">جدولة نشاط</button>
    </div>

    <!-- List -->
    <div v-else class="act-list">
      <div v-for="a in filtered" :key="a.id" class="act-card">

        <!-- Photo thumbnail -->
        <div v-if="a.photo_url" class="act-thumb">
          <img :src="a.photo_url" :alt="a.titre" />
        </div>

        <!-- Left: date block -->
        <div class="date-block" :style="`background:${statutInfo(a.statut).bg};color:${statutInfo(a.statut).color}`">
          <span class="date-day">{{ a.date ? a.date.split('-')[2] : '--' }}</span>
          <span class="date-mon">{{ a.date ? new Date(a.date+'T00:00').toLocaleDateString('fr-FR',{month:'short'}) : '' }}</span>
          <span class="date-yr">{{ a.date ? a.date.split('-')[0] : '' }}</span>
        </div>

        <!-- Center: info -->
        <div class="act-info">
          <div class="act-top-row">
            <h3>{{ a.titre }}</h3>
            <div class="statut-badge" :style="`background:${statutInfo(a.statut).bg};color:${statutInfo(a.statut).color}`">
              {{ statutInfo(a.statut).label }}
            </div>
          </div>
          <p v-if="a.description" class="act-desc">{{ a.description }}</p>
          <div class="act-meta">
            <span v-if="a.heure" class="meta-item">
              <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {{ formatHeure(a.heure) }}
            </span>
            <span v-if="a.lieu" class="meta-item">
              <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ a.lieu }}
            </span>
            <span v-if="a.responsable" class="meta-item">
              <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              {{ a.responsable }}
            </span>
          </div>
        </div>

        <!-- Right: actions -->
        <div class="act-actions">
          <!-- Statut quick-change -->
          <select class="statut-select" :value="a.statut" @change="changeStatut(a, $event.target.value)">
            <option v-for="s in STATUTS" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
          <div class="icon-btns">
            <button class="icon-btn edit" @click="openEdit(a)" title="تعديل">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4z"/></svg>
            </button>
            <button class="icon-btn del" @click="askDelete(a)" title="حذف">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal créer / modifier ── -->
    <teleport to="body">
      <div v-if="showModal" class="overlay" @click.self="showModal=false">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ isEdit ? 'تعديل النشاط' : 'نشاط جديد' }}</h2>
            <button class="close-btn" @click="showModal=false">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="mfield">
              <label>العنوان <span class="req">*</span></label>
              <input v-model="form.titre" type="text" placeholder="عنوان النشاط" autofocus />
            </div>
            <div class="mrow">
              <div class="mfield">
                <label>التاريخ <span class="req">*</span></label>
                <input v-model="form.date" type="date" />
              </div>
              <div class="mfield">
                <label>الوقت</label>
                <input v-model="form.heure" type="time" />
              </div>
            </div>
            <div class="mrow">
              <div class="mfield">
                <label>المكان</label>
                <input v-model="form.lieu" type="text" placeholder="قاعة، ملعب، ..." />
              </div>
              <div class="mfield">
                <label>المسؤول</label>
                <input v-model="form.responsable" type="text" placeholder="اسم المسؤول" />
              </div>
            </div>
            <div class="mfield">
              <label>الوصف</label>
              <textarea v-model="form.description" rows="3" placeholder="تفاصيل النشاط…"></textarea>
            </div>
            <!-- Image upload -->
            <div class="mfield">
              <label>صورة النشاط <span class="opt">(اختياري)</span></label>
              <div class="upload-zone" @click="$refs.photoInput.click()">
                <img v-if="photoPreview" :src="photoPreview" class="upload-preview" />
                <div v-else class="upload-placeholder">
                  <svg width="26" height="26" fill="none" stroke="#94a3b8" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                  <span>انقر لإضافة صورة</span>
                </div>
                <div v-if="photoPreview" class="upload-change">تغيير الصورة</div>
              </div>
              <input ref="photoInput" type="file" accept="image/*" hidden @change="onPhotoChange" />
            </div>

            <div class="mfield">
              <label>الحالة</label>
              <div class="statut-opts">
                <button v-for="s in STATUTS" :key="s.value" type="button"
                        :class="['sopt', form.statut===s.value && 'selected']"
                        :style="form.statut===s.value ? `background:${s.bg};color:${s.color};border-color:${s.color}` : ''"
                        @click="form.statut=s.value">
                  {{ s.label }}
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showModal=false">إلغاء</button>
            <button class="btn-primary" :disabled="saving" @click="save">
              <div v-if="saving" class="spin-sm"></div>
              {{ isEdit ? 'حفظ التعديلات' : 'إنشاء النشاط' }}
            </button>
          </div>
        </div>
      </div>
    </teleport>

    <!-- ── Modal suppression ── -->
    <teleport to="body">
      <div v-if="deleteModal.show" class="overlay" @click.self="deleteModal.show=false">
        <div class="modal sm-modal">
          <div class="del-icon">
            <svg width="28" height="28" fill="none" stroke="#ef4444" stroke-width="2" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
          </div>
          <h3>حذف النشاط؟</h3>
          <p>سيتم حذف « {{ deleteModal.titre }} » نهائياً.</p>
          <div class="del-actions">
            <button class="btn-cancel" @click="deleteModal.show=false">إلغاء</button>
            <button class="btn-danger" @click="confirmDelete">حذف</button>
          </div>
        </div>
      </div>
    </teleport>

  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.page { padding: 0; }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon { width: 44px; height: 44px; border-radius: 13px; background: linear-gradient(135deg,#7c3aed,#a855f7); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 14px rgba(124,58,237,0.3); }
.header-left h1 { font-size: 1.3rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
.header-left p  { font-size: 0.8rem; color: #94a3b8; margin: 0; }

/* Alert */
.alert { display: flex; align-items: center; gap: 9px; padding: 11px 15px; border-radius: 11px; font-size: 0.83rem; font-weight: 600; margin-bottom: 18px; border-right: 3px solid; }
.alert.success { background: #f0fdf4; border-color: #16a34a; color: #15803d; }
.alert.error   { background: #fef2f2; border-color: #dc2626; color: #dc2626; }
.slide-down-enter-active, .slide-down-leave-active { transition: all .3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* KPI row */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 22px; }
.kpi-card { background: white; border-radius: 12px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); text-align: center; }
.kpi-num { font-size: 1.6rem; font-weight: 900; line-height: 1; }
.kpi-label { font-size: 0.73rem; color: #94a3b8; font-weight: 600; margin-top: 4px; }

/* Filters */
.filter-row { display: flex; align-items: center; gap: 8px; margin-bottom: 18px; flex-wrap: wrap; }
.chip { display: flex; align-items: center; gap: 5px; padding: 7px 13px; border: 1.5px solid #e2e8f0; border-radius: 20px; background: white; font-size: 0.8rem; font-weight: 700; color: #64748b; cursor: pointer; transition: all 0.2s; }
.chip.active-all { background: #1d4ed8; color: white; border-color: #1d4ed8; }
.chip-count { background: #f1f5f9; color: #64748b; font-size: 0.7rem; font-weight: 800; padding: 1px 6px; border-radius: 10px; }
.chip.active-all .chip-count { background: rgba(255,255,255,0.25); color: white; }
.search-wrap { display: flex; align-items: center; gap: 7px; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 7px 12px; background: white; margin-right: auto; }
.search-wrap input { border: none; outline: none; font-size: 0.82rem; color: #1e293b; width: 160px; }

/* Loading / empty */
.loading-row { display: flex; align-items: center; gap: 10px; color: #94a3b8; font-size: 0.85rem; padding: 40px 0; justify-content: center; }
.spinner { width: 20px; height: 20px; border: 2.5px solid #e2e8f0; border-top-color: #7c3aed; border-radius: 50%; animation: spin 0.7s linear infinite; }
.empty-state { text-align: center; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.empty-state p { color: #94a3b8; font-size: 0.9rem; margin: 0; }

/* Activity list */
.act-list { display: flex; flex-direction: column; gap: 12px; }
.act-card { background: white; border-radius: 14px; padding: 16px 20px; display: flex; align-items: center; gap: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; transition: box-shadow 0.2s; }
.act-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.08); }

/* Date block */
.date-block { width: 58px; flex-shrink: 0; border-radius: 12px; padding: 10px 0; display: flex; flex-direction: column; align-items: center; gap: 1px; }
.date-day { font-size: 1.4rem; font-weight: 900; line-height: 1; }
.date-mon { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
.date-yr  { font-size: 0.65rem; font-weight: 600; opacity: 0.7; }

/* Info */
.act-info { flex: 1; min-width: 0; }
.act-top-row { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; flex-wrap: wrap; }
.act-top-row h3 { font-size: 0.95rem; font-weight: 800; color: #1e293b; margin: 0; }
.statut-badge { font-size: 0.7rem; font-weight: 800; padding: 3px 9px; border-radius: 20px; white-space: nowrap; }
.act-desc { font-size: 0.8rem; color: #64748b; margin: 0 0 8px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.act-meta { display: flex; gap: 14px; flex-wrap: wrap; }
.meta-item { display: flex; align-items: center; gap: 5px; font-size: 0.75rem; color: #94a3b8; font-weight: 600; }

/* Actions */
.act-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; flex-shrink: 0; }
.statut-select { border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 6px 10px; font-size: 0.78rem; font-weight: 700; color: #374151; outline: none; cursor: pointer; background: white; }
.statut-select:focus { border-color: #7c3aed; }
.icon-btns { display: flex; gap: 6px; }
.icon-btn { width: 30px; height: 30px; border-radius: 8px; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.icon-btn.edit { background: #f0f9ff; color: #0891b2; }
.icon-btn.edit:hover { background: #0891b2; color: white; }
.icon-btn.del  { background: #fef2f2; color: #ef4444; }
.icon-btn.del:hover  { background: #ef4444; color: white; }

/* Buttons */
.btn-primary { display: flex; align-items: center; gap: 7px; background: linear-gradient(135deg,#7c3aed,#a855f7); color: white; font-weight: 800; font-size: 0.875rem; padding: 10px 18px; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s; box-shadow: 0 4px 12px rgba(124,58,237,0.28); }
.btn-primary:hover:not(:disabled) { opacity: 0.9; }
.btn-primary:disabled { opacity: 0.65; cursor: default; }
.btn-primary.sm { padding: 8px 14px; font-size: 0.82rem; }
.btn-cancel { background: #f8fafc; border: 1.5px solid #e2e8f0; color: #64748b; font-weight: 700; font-size: 0.875rem; padding: 10px 18px; border-radius: 10px; cursor: pointer; }
.btn-danger { background: #ef4444; color: white; font-weight: 800; font-size: 0.875rem; padding: 10px 18px; border: none; border-radius: 10px; cursor: pointer; }
.btn-danger:hover { background: #dc2626; }

/* Modal */
.overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 20px; backdrop-filter: blur(3px); }
.modal { background: white; border-radius: 18px; width: 100%; max-width: 560px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); overflow: hidden; max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px 16px; border-bottom: 1px solid #f1f5f9; position: sticky; top: 0; background: white; z-index: 1; }
.modal-header h2 { font-size: 1rem; font-weight: 900; color: #1e293b; margin: 0; }
.close-btn { background: #f8fafc; border: none; border-radius: 8px; cursor: pointer; padding: 6px; display: flex; }
.modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
.mrow { display: flex; gap: 12px; }
.mrow .mfield { flex: 1; }
.mfield label { display: block; font-size: 0.78rem; font-weight: 700; color: #374151; margin-bottom: 6px; }
.mfield input, .mfield textarea, .mfield select { width: 100%; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; font-size: 0.875rem; outline: none; transition: border-color 0.2s; resize: vertical; font-family: inherit; background: white; }
.mfield input:focus, .mfield textarea:focus { border-color: #7c3aed; box-shadow: 0 0 0 3px rgba(124,58,237,0.07); }
.statut-opts { display: flex; gap: 8px; flex-wrap: wrap; }
.sopt { padding: 6px 14px; border: 1.5px solid #e2e8f0; border-radius: 20px; background: white; font-size: 0.78rem; font-weight: 700; color: #64748b; cursor: pointer; transition: all 0.2s; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px; border-top: 1px solid #f1f5f9; position: sticky; bottom: 0; background: white; }
.sm-modal { max-width: 380px; padding: 28px 24px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.del-icon { width: 56px; height: 56px; border-radius: 50%; background: #fef2f2; display: flex; align-items: center; justify-content: center; margin-bottom: 4px; }
.sm-modal h3 { font-size: 1rem; font-weight: 900; color: #1e293b; margin: 0; }
.sm-modal p  { font-size: 0.83rem; color: #64748b; margin: 0; }
.del-actions { display: flex; gap: 10px; margin-top: 6px; }
/* Activity photo thumbnail */
.act-thumb {
  width: 70px; height: 70px; flex-shrink: 0;
  border-radius: 12px; overflow: hidden; border: 2px solid #f1f5f9;
}
.act-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }

/* Upload zone in modal */
.upload-zone {
  border: 2px dashed #e2e8f0; border-radius: 12px;
  cursor: pointer; overflow: hidden; position: relative;
  min-height: 120px; display: flex; align-items: center; justify-content: center;
  transition: border-color 0.2s; background: #f9fafb;
}
.upload-zone:hover { border-color: #7c3aed; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 7px; padding: 20px; color: #94a3b8; }
.upload-placeholder span { font-size: 0.82rem; font-weight: 600; color: #64748b; }
.upload-preview { width: 100%; max-height: 180px; object-fit: cover; display: block; }
.upload-change {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(0,0,0,0.5); color: white;
  text-align: center; padding: 6px; font-size: 0.75rem; font-weight: 600;
}
.opt { color: #9ca3af; font-weight: 500; font-size: 0.72rem; }

.req { color: #dc2626; }
.spin-sm { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.35); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg) } }
</style>
