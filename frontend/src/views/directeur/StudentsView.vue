<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import JSZip from 'jszip'

// ── State ─────────────────────────────────────────────────────────────────────
const students    = ref([])
const loading     = ref(false)
const search      = ref('')

const selectedLevel  = ref(null)
const selectedClass  = ref(null)
const expandedLevels = ref(new Set())
const sidebarOpen    = ref(true)

// Delete student
const confirmModal    = ref(false)
const studentToDelete = ref(null)
const deleteLoading   = ref(false)

// Delete niveau
const deleteNiveauModal   = ref(false)
const niveauToDelete      = ref(null)
const deleteNiveauLoading = ref(false)

// Import
const importModal   = ref(false)
const importNiveau  = ref('1APIC')
const importFiles   = ref([])   // [{file, detectedClass, name}]
const importLoading = ref(false)
const importResults = ref([])
const importErrors  = ref([])
const importError   = ref('')
const fileInput     = ref(null)
const replaceNiveau = ref(false)

// Reset password
const resetModal   = ref(false)
const resetStudent = ref(null)
const resetResult  = ref(null)
const resetLoading = ref(false)

// Niveaux et leurs classes
const NIVEAUX = {
  '1APIC': ['1APIC-1','1APIC-2','1APIC-3','1APIC-4','1APIC-5','1APIC-6','1APIC-7','1APIC-8'],
  '2APIC': ['2APIC-1','2APIC-2','2APIC-3','2APIC-4','2APIC-5','2APIC-6','2APIC-7'],
}

// ── Fetch ──────────────────────────────────────────────────────────────────────
onMounted(fetchStudents)

async function fetchStudents() {
  loading.value = true
  try {
    const { data } = await api.get('/students/')
    students.value = data
  } finally { loading.value = false }
}

// ── Tree ───────────────────────────────────────────────────────────────────────
function getLevel(classe) {
  if (!classe) return 'بدون قسم'
  const m = classe.match(/^(.+)-\d+$/)
  return m ? m[1] : classe
}

const tree = computed(() => {
  const map = {}
  for (const s of students.value) {
    const level = getLevel(s.classe)
    const cls   = s.classe || 'بدون قسم'
    if (!map[level]) map[level] = {}
    if (!map[level][cls]) map[level][cls] = 0
    map[level][cls]++
  }
  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([level, classes]) => ({
      level,
      total: Object.values(classes).reduce((s, n) => s + n, 0),
      classes: Object.entries(classes)
        .sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
        .map(([cls, count]) => ({ cls, count }))
    }))
})

function toggleLevel(level) {
  const s = new Set(expandedLevels.value)
  s.has(level) ? s.delete(level) : s.add(level)
  expandedLevels.value = s
}
function selectAll()             { selectedLevel.value = null; selectedClass.value = null }
function selectLevel(level)      { selectedLevel.value = level; selectedClass.value = null; if (!expandedLevels.value.has(level)) toggleLevel(level) }
function selectClass(level, cls) { selectedLevel.value = level; selectedClass.value = cls }

const filtered = computed(() => {
  let list = students.value
  if (selectedClass.value)       list = list.filter(s => s.classe === selectedClass.value)
  else if (selectedLevel.value)  list = list.filter(s => getLevel(s.classe) === selectedLevel.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(s => (s.first_name+' '+s.last_name+' '+s.username+' '+(s.classe||'')).toLowerCase().includes(q))
  }
  return list
})

const totalActive = computed(() => students.value.filter(s => s.is_active).length)
const breadcrumb  = computed(() => {
  if (selectedClass.value) return `${selectedLevel.value} › ${selectedClass.value}`
  if (selectedLevel.value) return selectedLevel.value
  return 'جميع الطلاب'
})

// ── Actions élève ──────────────────────────────────────────────────────────────
async function toggleActivate(s) {
  const { data } = await api.post(`/students/${s.id}/activate/`)
  s.is_active = data.is_active
}
function askDelete(s)    { studentToDelete.value = s; confirmModal.value = true }
function cancelDelete()  { confirmModal.value = false; studentToDelete.value = null }
async function confirmDelete() {
  if (!studentToDelete.value) return
  deleteLoading.value = true
  try {
    await api.delete(`/students/${studentToDelete.value.id}/`)
    students.value = students.value.filter(x => x.id !== studentToDelete.value.id)
    confirmModal.value = false; studentToDelete.value = null
  } finally { deleteLoading.value = false }
}

// ── Supprimer niveau ───────────────────────────────────────────────────────────
function askDeleteNiveau(niveau) { niveauToDelete.value = niveau; deleteNiveauModal.value = true }
function cancelDeleteNiveau()    { deleteNiveauModal.value = false; niveauToDelete.value = null }
const niveauToDeleteCount = computed(() => students.value.filter(s => getLevel(s.classe) === niveauToDelete.value).length)

async function confirmDeleteNiveau() {
  if (!niveauToDelete.value) return
  deleteNiveauLoading.value = true
  try {
    await api.delete(`/students/?niveau=${niveauToDelete.value}`)
    const niv = niveauToDelete.value
    students.value = students.value.filter(s => getLevel(s.classe) !== niv)
    if (selectedLevel.value === niv) selectAll()
    deleteNiveauModal.value = false; niveauToDelete.value = null
  } finally { deleteNiveauLoading.value = false }
}

// ── Import ─────────────────────────────────────────────────────────────────────
function openImport(niv = '1APIC') {
  importNiveau.value  = niv
  importFiles.value   = []
  importResults.value = []
  importErrors.value  = []
  importError.value   = ''
  replaceNiveau.value = false
  importModal.value   = true
}
function closeImport() { importModal.value = false }

function detectClass(filename) {
  const stem = filename.replace(/\.(xlsx?|csv)$/i, '').trim().toUpperCase()
  const m1 = stem.match(/^(\d+APIC)-(\d+)$/)
  if (m1) return `${m1[1]}-${m1[2]}`
  const m2 = stem.match(/^(\d+APIC)(\d+)$/)
  if (m2) return `${m2[1]}-${m2[2]}`
  return stem
}

function onFilesChange(e) {
  const newFiles = Array.from(e.target.files)
  for (const f of newFiles) {
    const detectedClass = detectClass(f.name)
    if (!importFiles.value.find(x => x.detectedClass === detectedClass))
      importFiles.value.push({ file: f, detectedClass, name: f.name })
  }
  e.target.value = ''
}
function removeFile(idx) { importFiles.value.splice(idx, 1) }

const coveredClasses    = computed(() => new Set(importFiles.value.map(f => f.detectedClass)))
const niveauExistingCount = computed(() => students.value.filter(s => getLevel(s.classe) === importNiveau.value).length)

async function submitImport() {
  if (importFiles.value.length === 0) { importError.value = 'الرجاء تحديد ملف Excel واحد على الأقل.'; return }
  importLoading.value = true; importError.value = ''; importResults.value = []; importErrors.value = []
  try {
    const form = new FormData()
    for (const f of importFiles.value) form.append('files', f.file)
    if (replaceNiveau.value) form.append('replace_niveau', importNiveau.value)
    const { data } = await api.post('/students/import/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    importResults.value = data.created || []
    importErrors.value  = data.errors  || []
    await fetchStudents()
  } catch (e) {
    importError.value = e.response?.data?.error || 'خطأ أثناء الاستيراد.'
  } finally { importLoading.value = false }
}

const resultsByClass = computed(() => {
  const map = {}
  for (const r of importResults.value) {
    const key = r.classe || 'Sans classe'
    if (!map[key]) map[key] = []
    map[key].push(r)
  }
  return Object.entries(map).sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
})

async function downloadZip(results) {
  const zip  = new JSZip()
  const root = zip.folder('ELEVES')
  for (const r of results) {
    const level = getLevel(r.classe)
    const cls   = r.classe || 'Sans_classe'
    const name  = `${r.last_name}_${r.first_name}`.replace(/\s+/g, '_') || r.username
    const content = [
      '══════════════════════════════',
      '  SafeSchool — Identifiants',
      '══════════════════════════════',
      '',
      `Nom complet  : ${r.first_name} ${r.last_name}`,
      `Classe       : ${cls}`,
      '',
      `Email        : ${r.username}`,
      `Mot de passe : ${r.password}`,
      '',
      '⚠ Changez votre mot de passe à la première connexion.',
      '══════════════════════════════',
    ].join('\n')
    root.folder(level).folder(cls).file(`${name}.txt`, content)
  }
  const blob = await zip.generateAsync({ type: 'blob' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = 'ELEVES.zip'; a.click()
  URL.revokeObjectURL(url)
}

// ── Reset MDP ──────────────────────────────────────────────────────────────────
function askReset(s)   { resetStudent.value = s; resetResult.value = null; resetModal.value = true }
function closeReset()  { resetModal.value = false; resetStudent.value = null; resetResult.value = null }
async function confirmReset() {
  if (!resetStudent.value) return
  resetLoading.value = true
  try {
    const { data } = await api.post(`/students/${resetStudent.value.id}/reset-password/`)
    resetResult.value = data.new_password
  } finally { resetLoading.value = false }
}

// ── Helpers ────────────────────────────────────────────────────────────────────
function formatDate(d) {
  if (!d) return '—'
  const date = new Date(d)
  return isNaN(date) ? '—' : date.toLocaleDateString('ar-MA', { day:'2-digit', month:'short', year:'numeric' })
}
const avatarColors = [
  ['#dbeafe','#1d4ed8'],['#dcfce7','#16a34a'],['#fce7f3','#be185d'],
  ['#fef9c3','#a16207'],['#f3e8ff','#7c3aed'],['#ffedd5','#c2410c'],
]
function avatarColor(name) {
  return avatarColors[(name?.charCodeAt(0) || 0) % avatarColors.length]
}
</script>

<template>
  <div class="page-root">

    <!-- ── Header ── -->
    <div class="page-header">
      <div>
        <h2>الطلاب</h2>
        <p class="subtitle">{{ students.length }} طالب · {{ totalActive }} نشط · {{ tree.length }} مستويات</p>
      </div>
      <div class="import-btns">
        <button class="btn-import btn-1apic" @click="openImport('1APIC')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Import 1APIC
        </button>
        <button class="btn-import btn-2apic" @click="openImport('2APIC')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Import 2APIC
        </button>
      </div>
    </div>

    <div class="content-layout">

      <!-- ── Tree panel ── -->
      <aside :class="['tree-panel', !sidebarOpen && 'tree-panel--hidden']">
        <div :class="['tree-item all-item', !selectedLevel && !selectedClass && 'active']" @click="selectAll">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          <span>جميع الطلاب</span>
          <span class="tree-count">{{ students.length }}</span>
        </div>
        <div class="tree-divider"></div>

        <div v-if="loading" class="tree-loading">
          <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        </div>

        <div v-for="node in tree" :key="node.level" class="level-block">
          <div :class="['level-row', selectedLevel === node.level && !selectedClass && 'active']"
               @click="selectLevel(node.level)">
            <span class="level-chevron" :class="{ open: expandedLevels.has(node.level) }" @click.stop="toggleLevel(node.level)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
            </span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            <span class="level-name">{{ node.level }}</span>
            <span class="tree-count">{{ node.total }}</span>
            <button class="niveau-del-btn" @click.stop="askDeleteNiveau(node.level)" title="Supprimer ce niveau">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            </button>
          </div>
          <div v-if="expandedLevels.has(node.level)" class="class-list">
            <div v-for="c in node.classes" :key="c.cls"
                 :class="['class-row', selectedClass === c.cls && 'active']"
                 @click="selectClass(node.level, c.cls)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
              <span>{{ c.cls }}</span>
              <span class="tree-count">{{ c.count }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- ── Main panel ── -->
      <div class="main-panel">
        <div class="panel-toolbar">
          <button class="sidebar-toggle-btn" @click="sidebarOpen = !sidebarOpen" :title="sidebarOpen ? 'إخفاء اللوحة' : 'إظهار اللوحة'">
            <svg v-if="sidebarOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M15 9l-3 3 3 3"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M12 9l3 3-3 3"/></svg>
          </button>
          <div class="breadcrumb">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            {{ breadcrumb }}
            <span class="bc-count">{{ filtered.length }} طالب</span>
          </div>
          <div class="search-wrap">
            <svg class="search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="search" type="text" placeholder="بحث..." class="search-input" />
          </div>
        </div>

        <div v-if="loading" class="empty">
          <svg class="spin" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          جارٍ التحميل...
        </div>
        <div v-else-if="filtered.length === 0" class="empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
          <span>لا يوجد طالب في هذا التحديد.</span>
        </div>
        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>الطالب</th><th>البريد</th><th>القسم</th>
                <th>الحالة</th><th>التسجيل</th><th>الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in filtered" :key="s.id">
                <td>
                  <div class="name-cell">
                    <div class="avatar" :style="`background:${avatarColor(s.first_name||s.username)[0]};color:${avatarColor(s.first_name||s.username)[1]}`">
                      <img v-if="s.photo_url" :src="s.photo_url" class="avatar-photo" alt="" />
                      <span v-else>{{ (s.first_name||s.username||'?')[0].toUpperCase() }}</span>
                    </div>
                    <div>
                      <div class="full-name">{{ s.first_name }} {{ s.last_name }}</div>
                      <div class="sub-text">{{ s.email || s.username }}</div>
                    </div>
                  </div>
                </td>
                <td><span class="chip">{{ s.username }}</span></td>
                <td>
                  <div class="classe-cell">
                    <span class="level-badge">{{ getLevel(s.classe) }}</span>
                    <span class="class-badge">{{ s.classe || '—' }}</span>
                  </div>
                </td>
                <td>
                  <span :class="['status-badge', s.is_active ? 'active' : 'pending']">
                    <span class="status-dot"></span>
                    {{ s.is_active ? 'نشط' : 'في الانتظار' }}
                  </span>
                </td>
                <td class="date-cell">{{ formatDate(s.date_joined) }}</td>
                <td>
                  <div class="row-actions">
                    <button :class="['action-btn', s.is_active ? 'btn-deactivate' : 'btn-activate']" @click="toggleActivate(s)">
                      <svg v-if="s.is_active" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
                      <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                      {{ s.is_active ? 'إلغاء التفعيل' : 'تفعيل' }}
                    </button>
                    <button class="action-btn btn-reset" @click="askReset(s)">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/></svg>
                      MDP
                    </button>
                    <button class="action-btn btn-delete" @click="askDelete(s)">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
                      حذف
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ── Modal : Supprimer élève ── -->
    <div v-if="confirmModal" class="overlay" @click.self="cancelDelete">
      <div class="confirm-modal">
        <div class="confirm-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg></div>
        <h3 class="confirm-title">حذف الطالب</h3>
        <p class="confirm-msg">أنت على وشك حذف <strong>{{ studentToDelete?.first_name }} {{ studentToDelete?.last_name }}</strong>. هذه العملية لا يمكن التراجع عنها.</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDelete">إلغاء</button>
          <button class="btn-confirm" :disabled="deleteLoading" @click="confirmDelete">{{ deleteLoading ? 'جارٍ الحذف...' : 'نعم، احذف' }}</button>
        </div>
      </div>
    </div>

    <!-- ── Modal : Supprimer niveau ── -->
    <div v-if="deleteNiveauModal" class="overlay" @click.self="cancelDeleteNiveau">
      <div class="confirm-modal">
        <div class="confirm-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg></div>
        <h3 class="confirm-title">حذف المستوى {{ niveauToDelete }}</h3>
        <p class="confirm-msg">سيُحذف <strong>{{ niveauToDeleteCount }} طالب</strong> من المستوى <strong>{{ niveauToDelete }}</strong>. هذه العملية لا يمكن التراجع عنها.</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDeleteNiveau">إلغاء</button>
          <button class="btn-confirm" :disabled="deleteNiveauLoading" @click="confirmDeleteNiveau">
            {{ deleteNiveauLoading ? 'جارٍ الحذف...' : `حذف ${niveauToDelete}` }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Modal : Import par niveau ── -->
    <div v-if="importModal" class="overlay" @click.self="closeImport">
      <div class="import-modal">
        <div class="modal-head">
          <h3>استيراد الطلاب</h3>
          <button class="close-btn" @click="closeImport">✕</button>
        </div>

        <!-- النتائج -->
        <div v-if="importResults.length > 0">
          <div class="import-success-banner">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <div>
              <strong>تم استيراد {{ importResults.length }} طالب</strong>
              <span class="imp-note">أرسل كلمات المرور أدناه إلى الطلاب.</span>
            </div>
          </div>

          <!-- حسب القسم -->
          <div v-for="[cls, rows] in resultsByClass" :key="cls" class="class-result-block">
            <div class="class-result-head">
              <span class="class-badge">{{ cls }}</span>
              <span class="class-result-count">{{ rows.length }} طالب</span>
            </div>
            <div class="results-wrap">
              <table class="results-table">
                <thead><tr><th>الاسم</th><th>البريد الإلكتروني</th><th>كلمة المرور</th></tr></thead>
                <tbody>
                  <tr v-for="r in rows" :key="r.username">
                    <td>{{ r.first_name }} {{ r.last_name }}</td>
                    <td><code>{{ r.username }}</code></td>
                    <td><code class="pw-chip">{{ r.password }}</code></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="importErrors.length > 0" class="import-error-list">
            <strong>{{ importErrors.length }} خطأ :</strong>
            <div v-for="(e, i) in importErrors" :key="i" class="err-row">
              {{ e.fichier || '' }} {{ e.ligne ? `سطر ${e.ligne}` : '' }} — {{ e.erreur }}
            </div>
          </div>

          <div class="modal-actions">
            <button class="btn-zip" @click="downloadZip(importResults)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              تنزيل ZIP
            </button>
            <button class="btn-primary" @click="closeImport">إغلاق</button>
          </div>
        </div>

        <!-- نموذج الاستيراد -->
        <div v-else>

          <!-- اختيار المستوى -->
          <div class="niveau-selector">
            <button v-for="(classes, niv) in NIVEAUX" :key="niv"
              :class="['niveau-tab', importNiveau === niv && 'active']"
              @click="importNiveau = niv; importFiles = []; importError = ''">
              <span class="niv-name">{{ niv }}</span>
              <span class="niv-sub">{{ classes.length }} أقسام</span>
            </button>
          </div>

          <!-- الأقسام المتوقعة -->
          <div class="expected-section">
            <p class="expected-label">الأقسام المتوقعة</p>
            <div class="expected-chips">
              <span v-for="cls in NIVEAUX[importNiveau]" :key="cls"
                    :class="['cls-chip', coveredClasses.has(cls) && 'covered']">
                <svg v-if="coveredClasses.has(cls)" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                {{ cls }}
              </span>
            </div>
          </div>

          <!-- منطقة رفع الملفات -->
          <div class="file-drop" @click="fileInput?.click()">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            <span>انقر لاختيار ملفات Excel</span>
            <span class="file-drop-hint">يمكن اختيار ملفات متعددة · مثال: 1APIC-1.xlsx</span>
            <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv" multiple class="hidden-input" @change="onFilesChange" />
          </div>

          <!-- الملفات المختارة -->
          <div v-if="importFiles.length > 0" class="files-list">
            <div v-for="(f, idx) in importFiles" :key="idx" class="file-row">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <span class="file-name-text">{{ f.name }}</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
              <span class="class-badge">{{ f.detectedClass }}</span>
              <button class="remove-file-btn" @click="removeFile(idx)">✕</button>
            </div>
          </div>

          <!-- خيار الاستبدال -->
          <label v-if="niveauExistingCount > 0" class="replace-toggle">
            <input type="checkbox" v-model="replaceNiveau" />
            <span>
              حذف <strong>{{ niveauExistingCount }} طالب</strong> الحاليين من {{ importNiveau }} قبل الاستيراد
              <span class="toggle-warn">⚠ إجراء لا يمكن التراجع عنه</span>
            </span>
          </label>

          <p v-if="importError" class="import-error">{{ importError }}</p>

          <div class="modal-actions">
            <button class="btn-cancel" @click="closeImport">إلغاء</button>
            <button class="btn-primary" :disabled="importLoading || importFiles.length === 0" @click="submitImport">
              <svg v-if="!importLoading" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              {{ importLoading ? 'جارٍ الاستيراد...' : `استيراد (${importFiles.length} ملف)` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal : Reset MDP ── -->
    <div v-if="resetModal" class="overlay" @click.self="closeReset">
      <div class="confirm-modal">
        <div class="confirm-icon reset-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="2.2"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/></svg></div>
        <h3 class="confirm-title">إعادة تعيين كلمة المرور</h3>
        <div v-if="!resetResult">
          <p class="confirm-msg">إنشاء كلمة مرور مؤقتة جديدة لـ <strong>{{ resetStudent?.first_name }} {{ resetStudent?.last_name }}</strong> ?</p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="closeReset">إلغاء</button>
            <button class="btn-confirm btn-blue" :disabled="resetLoading" @click="confirmReset">{{ resetLoading ? 'جارٍ الإنشاء...' : 'إنشاء' }}</button>
          </div>
        </div>
        <div v-else class="reset-result">
          <p class="reset-label">بيانات دخول الطالب :</p>
          <div class="cred-row"><span class="cred-label">البريد الإلكتروني</span><code class="pw-display">{{ resetStudent?.username }}</code></div>
          <div class="cred-row"><span class="cred-label">كلمة المرور</span><code class="pw-display pw-chip">{{ resetResult }}</code></div>
          <p class="reset-note">أرسل هذه البيانات إلى الطالب. سيُطلب منه تغيير كلمة المرور عند تسجيل الدخول.</p>
          <button class="btn-primary" style="width:100%;margin-top:12px" @click="closeReset">إغلاق</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.page-root { display:flex; flex-direction:column; height:100%; }

.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:20px; }
.page-header h2 { font-size:1.5rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:3px; font-size:0.875rem; }

.import-btns { display:flex; gap:8px; }
.btn-import { display:inline-flex; align-items:center; gap:7px; padding:10px 18px; border:none; border-radius:12px; font-size:0.875rem; font-weight:700; cursor:pointer; transition:opacity 0.2s; font-family:inherit; }
.btn-1apic { background:#1d4ed8; color:white; }
.btn-2apic { background:#7c3aed; color:white; }
.btn-import:hover { opacity:0.88; }

/* Layout */
.content-layout { display:flex; gap:16px; flex:1; min-height:0; }

/* Sidebar toggle button */
.sidebar-toggle-btn { display:inline-flex; align-items:center; justify-content:center; width:34px; height:34px; background:white; border:1.5px solid #e5e7eb; border-radius:10px; cursor:pointer; color:#6b7280; flex-shrink:0; transition:all 0.18s; }
.sidebar-toggle-btn:hover { background:#f1f5f9; border-color:#1d4ed8; color:#1d4ed8; }

/* Tree */
.tree-panel {
  width:220px; flex-shrink:0; background:white; border-radius:16px;
  box-shadow:0 2px 8px rgba(0,0,0,0.06); padding:10px 8px;
  overflow-y:auto; max-height:calc(100vh - 200px);
  transition: width 0.25s ease, opacity 0.2s ease, padding 0.25s ease, margin 0.25s ease;
}
.tree-panel--hidden {
  width:0; padding:0; opacity:0; overflow:hidden;
  pointer-events:none; margin-right:-16px;
}
.tree-loading { display:flex; justify-content:center; padding:16px; }
@keyframes spin { to { transform:rotate(360deg); } }
.spin { animation:spin 0.9s linear infinite; }
.all-item { display:flex; align-items:center; gap:8px; padding:9px 10px; border-radius:10px; cursor:pointer; font-size:0.85rem; font-weight:600; color:#475569; transition:background 0.15s; }
.all-item:hover { background:#f8fafc; }
.all-item.active { background:#eff6ff; color:#1d4ed8; }
.tree-divider { height:1px; background:#f1f5f9; margin:8px 4px; }
.level-block { margin-bottom:2px; }
.level-row { display:flex; align-items:center; gap:7px; padding:8px 10px; border-radius:10px; cursor:pointer; font-size:0.83rem; font-weight:700; color:#374151; transition:background 0.15s; }
.level-row:hover { background:#f8fafc; }
.level-row:hover .niveau-del-btn { opacity:1; }
.level-row.active { background:#eff6ff; color:#1d4ed8; }
.level-chevron { display:flex; align-items:center; padding:2px; border-radius:4px; transition:transform 0.2s; flex-shrink:0; }
.level-chevron:hover { background:#e5e7eb; }
.level-chevron.open { transform:rotate(90deg); }
.level-name { flex:1; }
.niveau-del-btn { opacity:0; background:none; border:none; cursor:pointer; color:#dc2626; padding:3px; border-radius:5px; display:flex; align-items:center; flex-shrink:0; transition:opacity 0.2s, background 0.15s; }
.niveau-del-btn:hover { background:#fef2f2; }
.class-list { padding-left:22px; }
.class-row { display:flex; align-items:center; gap:7px; padding:7px 10px; border-radius:9px; cursor:pointer; font-size:0.81rem; color:#64748b; transition:background 0.15s; margin-bottom:1px; }
.class-row:hover { background:#f8fafc; color:#1e293b; }
.class-row.active { background:#dbeafe; color:#1d4ed8; font-weight:700; }
.tree-count { margin-left:auto; font-size:0.72rem; background:#f1f5f9; color:#94a3b8; padding:2px 7px; border-radius:20px; font-weight:700; flex-shrink:0; }
.level-row.active .tree-count, .class-row.active .tree-count, .all-item.active .tree-count { background:#dbeafe; color:#1d4ed8; }

/* Main */
.main-panel { flex:1; min-width:0; display:flex; flex-direction:column; gap:12px; }
.panel-toolbar { display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.breadcrumb { display:flex; align-items:center; gap:7px; font-size:0.85rem; font-weight:700; color:#475569; flex:1; }
.bc-count { font-size:0.75rem; background:#f1f5f9; color:#94a3b8; padding:3px 9px; border-radius:20px; font-weight:700; }
.search-wrap { position:relative; }
.search-icon { position:absolute; left:11px; top:50%; transform:translateY(-50%); color:#9ca3af; pointer-events:none; }
.search-input { border:1.5px solid #e5e7eb; border-radius:11px; padding:9px 14px 9px 34px; font-size:0.875rem; outline:none; width:220px; box-sizing:border-box; transition:border-color 0.2s; }
.search-input:focus { border-color:#1d4ed8; }
.empty { display:flex; flex-direction:column; align-items:center; gap:12px; padding:56px; color:#9ca3af; background:white; border-radius:16px; font-size:0.95rem; box-shadow:0 2px 8px rgba(0,0,0,0.06); }

/* Table */
.table-wrap { background:white; border-radius:16px; box-shadow:0 2px 8px rgba(0,0,0,0.06); overflow:auto; }
table { width:100%; border-collapse:collapse; }
th { background:#f8fafc; padding:12px 16px; font-size:0.73rem; font-weight:800; color:#94a3b8; text-align:left; border-bottom:1px solid #f1f5f9; white-space:nowrap; text-transform:uppercase; letter-spacing:0.04em; }
td { padding:12px 16px; font-size:0.875rem; color:#374151; border-bottom:1px solid #f8fafc; vertical-align:middle; }
tr:last-child td { border-bottom:none; }
tr:hover td { background:#fafbff; }
.name-cell { display:flex; align-items:center; gap:10px; }
.avatar { width:34px; height:34px; border-radius:50%; font-weight:800; font-size:0.85rem; display:flex; align-items:center; justify-content:center; flex-shrink:0; overflow:hidden; }
.avatar-photo { width:100%; height:100%; object-fit:cover; }
.full-name { font-weight:700; color:#1e293b; }
.sub-text { font-size:0.73rem; color:#94a3b8; margin-top:1px; }
.chip { background:#f1f5f9; color:#475569; font-size:0.76rem; font-weight:700; padding:3px 8px; border-radius:6px; font-family:monospace; }
.classe-cell { display:flex; align-items:center; gap:5px; flex-wrap:wrap; }
.level-badge { background:#f0fdf4; color:#16a34a; font-size:0.72rem; font-weight:800; padding:3px 8px; border-radius:6px; }
.class-badge { background:#eff6ff; color:#1d4ed8; font-size:0.72rem; font-weight:800; padding:3px 8px; border-radius:6px; }
.date-cell { font-size:0.8rem; color:#94a3b8; white-space:nowrap; }
.status-badge { display:inline-flex; align-items:center; gap:5px; font-size:0.73rem; font-weight:700; padding:4px 10px; border-radius:20px; }
.status-badge.active  { background:#f0fdf4; color:#16a34a; }
.status-badge.pending { background:#fef9c3; color:#a16207; }
.status-dot { width:6px; height:6px; border-radius:50%; background:currentColor; flex-shrink:0; }
.row-actions { display:flex; gap:5px; }
.action-btn { display:inline-flex; align-items:center; gap:4px; font-size:0.76rem; font-weight:700; padding:5px 10px; border:none; border-radius:7px; cursor:pointer; transition:all 0.18s; white-space:nowrap; font-family:inherit; }
.btn-activate   { background:#f0fdf4; color:#16a34a; } .btn-activate:hover   { background:#dcfce7; }
.btn-deactivate { background:#fff7ed; color:#c2410c; } .btn-deactivate:hover { background:#ffedd5; }
.btn-reset      { background:#eff6ff; color:#1d4ed8; } .btn-reset:hover      { background:#dbeafe; }
.btn-delete     { background:#fef2f2; color:#dc2626; } .btn-delete:hover     { background:#fee2e2; }

/* Modals */
.overlay { position:fixed; inset:0; background:rgba(15,23,42,0.5); display:flex; align-items:center; justify-content:center; z-index:300; padding:16px; backdrop-filter:blur(2px); }
@keyframes modalIn { from { opacity:0; transform:scale(0.95) translateY(8px); } to { opacity:1; transform:none; } }
.confirm-modal { background:white; border-radius:20px; padding:32px 28px; width:100%; max-width:420px; text-align:center; box-shadow:0 24px 64px rgba(0,0,0,0.25); animation:modalIn 0.2s ease; }
.confirm-icon { width:58px; height:58px; border-radius:50%; background:#fef2f2; display:flex; align-items:center; justify-content:center; margin:0 auto 18px; }
.confirm-icon.reset-icon { background:#eff6ff; }
.confirm-title { font-size:1.1rem; font-weight:900; color:#1e293b; margin:0 0 10px; }
.confirm-msg { font-size:0.9rem; color:#6b7280; margin:0 0 24px; line-height:1.65; }
.confirm-msg strong { color:#1e293b; }
.confirm-actions { display:flex; gap:10px; }
.btn-cancel { flex:1; padding:11px; border:1.5px solid #e5e7eb; border-radius:12px; background:white; color:#374151; font-weight:700; font-size:0.9rem; cursor:pointer; font-family:inherit; transition:background 0.2s; }
.btn-cancel:hover { background:#f9fafb; }
.btn-confirm { flex:1; padding:11px; border:none; border-radius:12px; background:#dc2626; color:white; font-weight:700; font-size:0.9rem; cursor:pointer; font-family:inherit; transition:opacity 0.2s; }
.btn-confirm.btn-blue { background:#1d4ed8; }
.btn-confirm:disabled { opacity:0.7; cursor:default; }
.btn-confirm:hover:not(:disabled) { opacity:0.88; }
.reset-result { text-align:center; }
.reset-label { font-size:0.85rem; color:#6b7280; margin-bottom:10px; }
.pw-display { display:inline-block; background:#f8fafc; border:1.5px solid #e5e7eb; border-radius:10px; padding:7px 14px; font-family:monospace; font-size:0.9rem; font-weight:700; color:#1d4ed8; letter-spacing:0.04em; }
.reset-note { font-size:0.8rem; color:#94a3b8; line-height:1.5; margin-top:8px; }
.cred-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.cred-label { font-size:0.78rem; font-weight:700; color:#64748b; width:90px; flex-shrink:0; }

/* Import modal */
.import-modal { background:white; border-radius:20px; padding:28px; width:100%; max-width:620px; box-shadow:0 24px 64px rgba(0,0,0,0.25); animation:modalIn 0.2s ease; max-height:90vh; overflow-y:auto; }
.modal-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.modal-head h3 { font-size:1.1rem; font-weight:900; color:#1e293b; }
.close-btn { background:none; border:none; font-size:1.1rem; color:#94a3b8; cursor:pointer; padding:4px 8px; border-radius:8px; transition:background 0.2s; }
.close-btn:hover { background:#f1f5f9; color:#1e293b; }

/* Niveau selector */
.niveau-selector { display:flex; gap:10px; margin-bottom:18px; }
.niveau-tab { flex:1; border:2px solid #e5e7eb; border-radius:14px; padding:12px 16px; background:white; cursor:pointer; font-family:inherit; text-align:center; transition:all 0.18s; }
.niveau-tab:hover { border-color:#1d4ed8; background:#f8fafc; }
.niveau-tab.active { border-color:#1d4ed8; background:#eff6ff; }
.niv-name { display:block; font-size:1rem; font-weight:900; color:#1e293b; }
.niveau-tab.active .niv-name { color:#1d4ed8; }
.niv-sub { display:block; font-size:0.75rem; color:#94a3b8; margin-top:2px; }

/* Expected classes */
.expected-section { margin-bottom:16px; }
.expected-label { font-size:0.78rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px; }
.expected-chips { display:flex; flex-wrap:wrap; gap:6px; }
.cls-chip { display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:8px; font-size:0.78rem; font-weight:700; background:#f1f5f9; color:#94a3b8; border:1.5px solid #e5e7eb; transition:all 0.2s; }
.cls-chip.covered { background:#f0fdf4; color:#16a34a; border-color:#bbf7d0; }

/* File drop */
.file-drop { border:2px dashed #e5e7eb; border-radius:14px; padding:22px 20px; display:flex; flex-direction:column; align-items:center; gap:8px; cursor:pointer; text-align:center; color:#94a3b8; font-size:0.875rem; transition:border-color 0.2s, background 0.2s; margin-bottom:12px; }
.file-drop:hover { border-color:#1d4ed8; background:#f8fafc; }
.file-drop-hint { font-size:0.75rem; color:#cbd5e1; }
.hidden-input { display:none; }

/* Files list */
.files-list { display:flex; flex-direction:column; gap:6px; margin-bottom:14px; }
.file-row { display:flex; align-items:center; gap:8px; background:#f8fafc; border-radius:10px; padding:8px 12px; font-size:0.82rem; }
.file-name-text { flex:1; color:#374151; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.remove-file-btn { background:none; border:none; color:#94a3b8; cursor:pointer; font-size:0.85rem; padding:2px 6px; border-radius:6px; transition:background 0.15s, color 0.15s; }
.remove-file-btn:hover { background:#fef2f2; color:#dc2626; }

/* Replace toggle */
.replace-toggle { display:flex; align-items:flex-start; gap:10px; cursor:pointer; background:#fff7ed; border:1.5px solid #fed7aa; border-radius:12px; padding:12px 14px; margin-bottom:14px; font-size:0.85rem; color:#374151; line-height:1.5; }
.replace-toggle input[type="checkbox"] { margin-top:2px; flex-shrink:0; accent-color:#dc2626; width:15px; height:15px; }
.toggle-warn { display:block; font-size:0.78rem; color:#c2410c; font-weight:600; margin-top:3px; }

/* Modal actions */
.modal-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:16px; }
.btn-primary { padding:10px 24px; border:none; border-radius:12px; background:#1d4ed8; color:white; font-weight:700; font-size:0.9rem; cursor:pointer; display:inline-flex; align-items:center; gap:7px; transition:opacity 0.2s; font-family:inherit; }
.btn-primary:disabled { opacity:0.6; cursor:default; }
.btn-primary:hover:not(:disabled) { opacity:0.88; }
.btn-zip { padding:10px 20px; border:1.5px solid #16a34a; border-radius:12px; background:#f0fdf4; color:#16a34a; font-weight:700; font-size:0.9rem; cursor:pointer; display:inline-flex; align-items:center; gap:7px; transition:background 0.2s; font-family:inherit; }
.btn-zip:hover { background:#dcfce7; }

/* Import error */
.import-error { color:#dc2626; font-size:0.85rem; margin-bottom:12px; background:#fef2f2; padding:10px 14px; border-radius:10px; }
.import-error-list { background:#fef2f2; border-radius:10px; padding:12px 14px; margin-bottom:14px; font-size:0.82rem; color:#dc2626; }
.err-row { margin-top:4px; }

/* Success */
.import-success-banner { background:#f0fdf4; border:1.5px solid #bbf7d0; border-radius:12px; padding:14px 18px; display:flex; align-items:center; gap:10px; font-size:0.9rem; color:#16a34a; font-weight:700; margin-bottom:16px; }
.imp-note { font-weight:400; color:#374151; font-size:0.82rem; display:block; margin-top:2px; }

/* Results by class */
.class-result-block { margin-bottom:16px; }
.class-result-head { display:flex; align-items:center; gap:10px; margin-bottom:6px; }
.class-result-count { font-size:0.78rem; color:#6b7280; }
.results-wrap { overflow-x:auto; max-height:220px; overflow-y:auto; border:1px solid #f1f5f9; border-radius:10px; }
.results-table { width:100%; border-collapse:collapse; font-size:0.82rem; }
.results-table th { background:#f8fafc; padding:8px 12px; font-size:0.71rem; font-weight:800; color:#94a3b8; text-align:left; text-transform:uppercase; letter-spacing:0.04em; }
.results-table td { padding:8px 12px; border-top:1px solid #f8fafc; color:#374151; }
.results-table code { background:#f1f5f9; padding:2px 7px; border-radius:5px; font-size:0.8rem; }
.pw-chip { background:#eff6ff; color:#1d4ed8; font-weight:700; }
</style>
