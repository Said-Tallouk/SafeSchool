<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const auth         = useAuthStore()
const loading      = ref(false)
const photoLoading = ref(false)
const success      = ref('')
const error        = ref('')

function showMsg(type, msg) {
  if (type === 'success') { success.value = msg; error.value = '' }
  else                    { error.value = msg;   success.value = '' }
  setTimeout(() => { success.value = ''; error.value = '' }, 3500)
}
const showLightbox = ref(false)

const form = ref({ current: auth.savedPassword || '', password: '', confirm: '' })
const showCurrent = ref(false)
const showPass    = ref(false)
const showConfirm = ref(false)

const photoUrl = ref(auth.user?.photo_url || '')

async function changePassword() {
  success.value = ''
  error.value   = ''
  if (!form.value.current)               { error.value = 'أدخل كلمة المرور الحالية.'; return }
  if (form.value.password.length < 6)    { error.value = 'يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.'; return }
  if (form.value.password !== form.value.confirm) { error.value = 'كلمتا المرور غير متطابقتين.'; return }
  loading.value = true
  try {
    await api.post('/auth/change-password/', {
      old_password: form.value.current,
      new_password: form.value.password,
    })
    auth.savePassword(form.value.password)
    showMsg('success', 'تم تغيير كلمة المرور بنجاح.')
    form.value = { current: '', password: '', confirm: '' }
    showCurrent.value = false; showPass.value = false; showConfirm.value = false
  } catch (e) {
    showMsg('error', e.response?.data?.error || 'كلمة المرور الحالية غير صحيحة.')
  } finally {
    loading.value = false
  }
}

// Compresse l'image avant upload (max 800px, qualité 0.75)
function compressImage(file) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (ev) => {
      const img = new Image()
      img.onload = () => {
        const MAX = 800
        let { width, height } = img
        if (width > MAX || height > MAX) {
          if (width > height) { height = Math.round(height * MAX / width); width = MAX }
          else                { width  = Math.round(width  * MAX / height); height = MAX }
        }
        const canvas = document.createElement('canvas')
        canvas.width = width; canvas.height = height
        canvas.getContext('2d').drawImage(img, 0, 0, width, height)
        canvas.toBlob(blob => resolve(new File([blob], file.name, { type: 'image/jpeg' })),
          'image/jpeg', 0.75)
      }
      img.src = ev.target.result
    }
    reader.readAsDataURL(file)
  })
}

async function onPhotoChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) { showMsg('error', 'الصورة كبيرة جداً (الحد الأقصى 10 ميغابايت).'); return }

  // Aperçu immédiat
  const localUrl = URL.createObjectURL(file)
  photoUrl.value = localUrl
  photoLoading.value = true

  try {
    const compressed = await compressImage(file)
    // Convertir en base64 → JSON (évite le parsing multipart lent de Django)
    const b64 = await new Promise((res) => {
      const reader = new FileReader()
      reader.onload = (ev) => res(ev.target.result)
      reader.readAsDataURL(compressed)
    })
    const { data } = await api.post('/auth/upload-photo/', { photo_base64: b64 })
    auth.updateUser(data)
    photoUrl.value = data.photo_url
    URL.revokeObjectURL(localUrl)
    showMsg('success', 'تم تحديث الصورة بنجاح.')
  } catch {
    photoUrl.value = auth.user?.photo_url || ''
    URL.revokeObjectURL(localUrl)
    showMsg('error', 'فشل تحديث الصورة.')
  } finally {
    photoLoading.value = false
    e.target.value = ''
  }
}
</script>

<template>
  <div class="page">

    <!-- Header -->
    <div class="page-header">
      <div class="header-icon">
        <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
        </svg>
      </div>
      <div>
        <h2>ملفي الشخصي</h2>
        <p class="subtitle">معلوماتك الشخصية وإعدادات الحساب</p>
      </div>
    </div>

    <!-- Toast notification -->
    <Transition name="toast">
      <div v-if="success || error" :class="['toast', success ? 'toast-success' : 'toast-error']">
        <div class="toast-icon">
          <svg v-if="success" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
          <svg v-else width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="toast-body">
          <span class="toast-title">{{ success ? 'نجاح' : 'خطأ' }}</span>
          <span class="toast-msg">{{ success || error }}</span>
        </div>
        <div class="toast-progress" :class="success ? 'prog-green' : 'prog-red'"></div>
      </div>
    </Transition>

    <div class="grid">

      <!-- ── Carte profil ── -->
      <div class="profile-card">

        <!-- Photo -->
        <div class="photo-section">
          <div class="photo-wrap">
            <!-- Image ou initiale -->
            <img v-if="photoUrl" :src="photoUrl" class="photo-img" alt="Photo"
                 :class="{ 'photo-uploading': photoLoading }"
                 @click="!photoLoading && (showLightbox = true)" />
            <div v-else class="photo-initiale">
              {{ (auth.user?.first_name?.[0] || auth.user?.username?.[0] || '?').toUpperCase() }}
            </div>

            <!-- Overlay chargement plein écran photo -->
            <div v-if="photoLoading" class="photo-loading-overlay">
              <div class="upload-spinner"></div>
              <span>جارٍ الحفظ...</span>
            </div>

            <!-- Bouton caméra (caché pendant chargement) -->
            <label v-if="!photoLoading" class="photo-overlay">
              <input type="file" accept="image/*" style="display:none" @change="onPhotoChange" />
              <svg width="16" height="16" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
            </label>
          </div>

          <!-- Voir photo en grand -->
          <button v-if="photoUrl" type="button" class="view-photo-btn" @click="showLightbox = true">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            عرض الصورة
          </button>
          <p class="photo-hint">انقر على الصورة للتغيير</p>
        </div>

        <!-- Nom & rôle -->
        <div class="profile-name">
          <h3>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</h3>
          <div class="role-pill">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            طالب
          </div>
        </div>

        <!-- Infos -->
        <div class="info-list">
          <div class="info-row">
            <div class="info-left">
              <div class="info-icon blue">
                <svg width="13" height="13" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              </div>
              <span class="info-label">اسم المستخدم</span>
            </div>
            <span class="info-val">{{ auth.user?.username }}</span>
          </div>
          <div class="info-row">
            <div class="info-left">
              <div class="info-icon teal">
                <svg width="13" height="13" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              </div>
              <span class="info-label">البريد الإلكتروني</span>
            </div>
            <span class="info-val">{{ auth.user?.email || '—' }}</span>
          </div>
          <div class="info-row">
            <div class="info-left">
              <div class="info-icon green">
                <svg width="13" height="13" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
              </div>
              <span class="info-label">القسم</span>
            </div>
            <span class="info-val">{{ auth.user?.classe || '—' }}</span>
          </div>
          <div class="info-row no-border">
            <div class="info-left">
              <div class="info-icon orange">
                <svg width="13" height="13" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81a19.79 19.79 0 01-3.07-8.68A2 2 0 012 .84h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 8.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>
              </div>
              <span class="info-label">الهاتف</span>
            </div>
            <span class="info-val">{{ auth.user?.telephone || '—' }}</span>
          </div>
        </div>
      </div>

      <!-- ── Changer mot de passe ── -->
      <div class="password-card">
        <div class="card-head">
          <div class="card-head-icon">
            <svg width="18" height="18" fill="none" stroke="#1d4ed8" stroke-width="2" viewBox="0 0 24 24">
              <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
          </div>
          <div>
            <h4>تغيير كلمة المرور</h4>
            <p>اختر كلمة مرور قوية وفريدة</p>
          </div>
        </div>

        <form @submit.prevent="changePassword" class="pw-form">
          <div class="field">
            <label>كلمة المرور الحالية</label>
            <div class="pw-wrap">
              <input v-model="form.current" :type="showCurrent ? 'text' : 'password'"
                     placeholder="كلمة المرور الحالية" autocomplete="current-password" />
              <button type="button" class="eye-btn" @click="showCurrent = !showCurrent">
                <svg v-if="!showCurrent" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else              width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>
          <div class="divider-line"></div>
          <div class="field">
            <label>كلمة المرور الجديدة</label>
            <div class="pw-wrap">
              <input v-model="form.password" :type="showPass ? 'text' : 'password'"
                     placeholder="6 أحرف على الأقل" />
              <button type="button" class="eye-btn" @click="showPass = !showPass">
                <svg v-if="!showPass" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>
          <div class="field">
            <label>تأكيد كلمة المرور</label>
            <div class="pw-wrap">
              <input v-model="form.confirm" :type="showConfirm ? 'text' : 'password'"
                     placeholder="أعد إدخال كلمة المرور" />
              <button type="button" class="eye-btn" @click="showConfirm = !showConfirm">
                <svg v-if="!showConfirm" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <!-- Match indicator -->
          <div v-if="form.password && form.confirm" class="match-row">
            <template v-if="form.password === form.confirm">
              <svg width="13" height="13" fill="none" stroke="#16a34a" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
              <span style="color:#16a34a">كلمتا المرور متطابقتان</span>
            </template>
            <template v-else>
              <svg width="13" height="13" fill="none" stroke="#dc2626" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              <span style="color:#dc2626">غير متطابقتين</span>
            </template>
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <svg v-if="!loading" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
            <div v-else class="btn-spin"></div>
            {{ loading ? 'جارٍ الحفظ...' : 'حفظ' }}
          </button>
        </form>

        <!-- Security tips -->
        <div class="security-tips">
          <p class="tips-title">
            <svg width="13" height="13" fill="none" stroke="#d97706" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            نصائح الأمان
          </p>
          <ul>
            <li>8 أحرف على الأقل</li>
            <li>اجمع بين الحروف والأرقام والرموز</li>
            <li>لا تشارك كلمة مرورك أبداً</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="showLightbox && photoUrl" class="lightbox" @click.self="showLightbox = false">
      <div class="lightbox-content">
        <button class="lb-close" @click="showLightbox = false">
          <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <img :src="photoUrl" class="lb-img" alt="صورة الملف الشخصي" />
        <p class="lb-name">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</p>
      </div>
    </div>

  </div>
</template>

<style scoped>
.page { display:flex; flex-direction:column; gap:22px; }

/* Header */
.page-header { display:flex; align-items:center; gap:16px; }
.header-icon { width:48px; height:48px; border-radius:14px; background:linear-gradient(135deg,#1d4ed8,#0891b2); display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.page-header h2 { font-size:1.5rem; font-weight:900; color:#1e293b; margin:0; }
.subtitle { color:#94a3b8; margin:3px 0 0; font-size:0.875rem; }

/* Alerts */
/* ── Toast ── */
.toast { position:fixed; bottom:28px; right:28px; z-index:9999; display:flex; align-items:center; gap:14px; background:white; border-radius:16px; padding:16px 20px; min-width:300px; max-width:380px; box-shadow:0 8px 32px rgba(0,0,0,0.14); overflow:hidden; }
.toast-success { border-right:4px solid #16a34a; }
.toast-error   { border-right:4px solid #dc2626; }
.toast-icon { width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.toast-success .toast-icon { background:#f0fdf4; color:#16a34a; }
.toast-error   .toast-icon { background:#fef2f2; color:#dc2626; }
.toast-body { display:flex; flex-direction:column; gap:2px; flex:1; }
.toast-title { font-size:0.85rem; font-weight:800; color:#1e293b; }
.toast-msg   { font-size:0.8rem;  color:#64748b; line-height:1.4; }
.toast-progress { position:absolute; bottom:0; right:0; height:3px; border-radius:3px 0 0 3px; animation:progress 3.5s linear forwards; }
.prog-green { background:#16a34a; }
.prog-red   { background:#dc2626; }
@keyframes progress { from{width:100%} to{width:0%} }

/* Transition Vue */
.toast-enter-active { animation:toastIn 0.35s cubic-bezier(0.34,1.56,0.64,1); }
.toast-leave-active { animation:toastOut 0.3s ease forwards; }
@keyframes toastIn  { from{opacity:0;transform:translateX(60px) scale(0.9)} to{opacity:1;transform:none} }
@keyframes toastOut { from{opacity:1;transform:none} to{opacity:0;transform:translateX(60px)} }

/* Grid */
.grid { display:grid; grid-template-columns:1fr 1fr; gap:22px; align-items:start; }
@media(max-width:700px){ .grid { grid-template-columns:1fr; } }

/* ── Profile card ── */
.profile-card { background:white; border-radius:20px; box-shadow:0 2px 12px rgba(0,0,0,0.06); overflow:hidden; }

/* Photo */
.photo-section { background:linear-gradient(135deg,#1d4ed8,#0891b2); padding:32px 24px 20px; text-align:center; }
.photo-wrap { position:relative; width:96px; height:96px; margin:0 auto 10px; }
.photo-img { width:96px; height:96px; border-radius:50%; object-fit:cover; border:3px solid white; cursor:pointer; transition:opacity 0.2s; }
.photo-img:hover { opacity:0.85; }
.photo-initiale { width:96px; height:96px; border-radius:50%; background:rgba(255,255,255,0.25); color:white; font-size:2.2rem; font-weight:900; display:flex; align-items:center; justify-content:center; border:3px solid rgba(255,255,255,0.5); }
.photo-overlay { position:absolute; bottom:0; right:0; width:30px; height:30px; border-radius:50%; background:#1e293b; display:flex; align-items:center; justify-content:center; cursor:pointer; border:2px solid white; transition:background 0.2s; }
.photo-overlay:hover { background:#0891b2; }
.mini-spin { width:12px; height:12px; border:2px solid rgba(255,255,255,0.4); border-top-color:white; border-radius:50%; animation:spin 0.7s linear infinite; }
.photo-uploading { opacity:0.4; }
.photo-loading-overlay { position:absolute; inset:0; border-radius:50%; background:rgba(15,23,42,0.65); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; }
.upload-spinner { width:28px; height:28px; border:3px solid rgba(255,255,255,0.3); border-top-color:white; border-radius:50%; animation:spin 0.7s linear infinite; }
.photo-loading-overlay span { color:white; font-size:0.68rem; font-weight:700; letter-spacing:0.5px; }
.view-photo-btn { display:inline-flex; align-items:center; gap:5px; background:rgba(255,255,255,0.2); border:1px solid rgba(255,255,255,0.4); color:white; font-size:0.75rem; font-weight:600; padding:5px 12px; border-radius:20px; cursor:pointer; margin-bottom:4px; transition:background 0.2s; }
.view-photo-btn:hover { background:rgba(255,255,255,0.3); }
.photo-hint { font-size:0.72rem; color:rgba(255,255,255,0.65); margin:0; }

/* Name & role */
.profile-name { padding:20px 24px 4px; text-align:center; }
.profile-name h3 { font-size:1.1rem; font-weight:900; color:#1e293b; margin:0 0 8px; }
.role-pill { display:inline-flex; align-items:center; gap:6px; background:#eff6ff; color:#1d4ed8; font-size:0.78rem; font-weight:700; padding:5px 14px; border-radius:20px; }

/* Info list */
.info-list { padding:8px 24px 24px; display:flex; flex-direction:column; }
.info-row { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid #f1f5f9; }
.info-row.no-border { border-bottom:none; }
.info-left { display:flex; align-items:center; gap:10px; }
.info-icon { width:26px; height:26px; border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.info-icon.blue   { background:linear-gradient(135deg,#1d4ed8,#3b82f6); }
.info-icon.teal   { background:linear-gradient(135deg,#0891b2,#06b6d4); }
.info-icon.green  { background:linear-gradient(135deg,#15803d,#16a34a); }
.info-icon.orange { background:linear-gradient(135deg,#d97706,#f59e0b); }
.info-label { font-size:0.82rem; font-weight:700; color:#475569; }
.info-val { font-size:0.85rem; color:#1e293b; font-weight:500; }

/* ── Password card ── */
.password-card { background:white; border-radius:20px; box-shadow:0 2px 12px rgba(0,0,0,0.06); padding:28px; display:flex; flex-direction:column; gap:20px; }
.card-head { display:flex; align-items:center; gap:14px; }
.card-head-icon { width:44px; height:44px; border-radius:12px; background:#eff6ff; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.card-head h4 { font-size:0.95rem; font-weight:800; color:#1e293b; margin:0 0 3px; }
.card-head p  { font-size:0.78rem; color:#94a3b8; margin:0; }

.pw-form { display:flex; flex-direction:column; gap:14px; }
.divider-line { height:1px; background:#f1f5f9; margin:2px 0; }
.field label { display:block; font-size:0.8rem; font-weight:700; color:#475569; margin-bottom:7px; }
.pw-wrap { position:relative; }
.pw-wrap input { width:100%; border:1.5px solid #e2e8f0; border-radius:10px; padding:11px 13px 11px 42px; font-size:0.875rem; outline:none; transition:border-color 0.2s; box-sizing:border-box; color:#1e293b; }
.pw-wrap input:focus { border-color:#1d4ed8; }
.eye-btn { position:absolute; left:12px; top:50%; transform:translateY(-50%); background:none; border:none; color:#94a3b8; cursor:pointer; padding:0; display:flex; }
.eye-btn:hover { color:#475569; }
.match-row { display:flex; align-items:center; gap:6px; font-size:0.78rem; font-weight:600; }
.btn-submit { display:flex; align-items:center; justify-content:center; gap:8px; background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; font-weight:700; font-size:0.9rem; padding:12px; border:none; border-radius:12px; cursor:pointer; transition:opacity 0.2s; }
.btn-submit:disabled { opacity:0.7; }
.btn-spin { width:15px; height:15px; border:2px solid rgba(255,255,255,0.4); border-top-color:white; border-radius:50%; animation:spin 0.7s linear infinite; }

/* Security tips */
.security-tips { background:#fffbeb; border:1px solid #fde68a; border-radius:12px; padding:14px 16px; }
.tips-title { display:flex; align-items:center; gap:7px; font-size:0.82rem; font-weight:800; color:#92400e; margin:0 0 8px; }
.security-tips ul { margin:0; padding-right:16px; padding-left:0; display:flex; flex-direction:column; gap:4px; }
.security-tips ul li { font-size:0.78rem; color:#a16207; }

/* Lightbox */
.lightbox { position:fixed; inset:0; background:rgba(0,0,0,0.75); display:flex; align-items:center; justify-content:center; z-index:1000; backdrop-filter:blur(4px); }
.lightbox-content { position:relative; text-align:center; }
.lb-close { position:absolute; top:-14px; right:-14px; width:36px; height:36px; border-radius:50%; background:white; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; color:#374151; box-shadow:0 2px 8px rgba(0,0,0,0.2); }
.lb-img { max-width:340px; max-height:340px; border-radius:50%; object-fit:cover; border:4px solid white; box-shadow:0 8px 32px rgba(0,0,0,0.3); }
.lb-name { color:white; font-weight:800; font-size:1rem; margin-top:14px; }

@keyframes spin { to{transform:rotate(360deg)} }
</style>
