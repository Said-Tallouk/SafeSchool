<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const auth = useAuthStore()

// Photo upload
const photoUploading = ref(false)
const photoError     = ref('')
const showFullPhoto  = ref(false)

async function handlePhotoUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  photoError.value   = ''
  photoUploading.value = true
  try {
    const form = new FormData()
    form.append('photo', file)
    const { data } = await api.patch('/auth/me/', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    auth.updateUser({ photo_url: data.photo_url })
  } catch {
    photoError.value = 'فشل رفع الصورة. حاول مجدداً.'
  } finally {
    photoUploading.value = false
    e.target.value = ''
  }
}

// Profile form
const firstName  = ref('')
const lastName   = ref('')
const email      = ref('')
const telephone  = ref('')
const profileMsg = ref('')
const profileErr = ref('')
const profileLoading = ref(false)

// Password form
const currentPass  = ref('')
const newPass      = ref('')
const confirmPass  = ref('')
const passMsg      = ref('')
const passErr      = ref('')
const passLoading  = ref(false)

// Affichage sécurisé du mot de passe sauvegardé
const showSaved    = ref(false)
const showCurrent  = ref(false)
const showNew      = ref(false)
const showConfirm  = ref(false)

const savedPassword = auth.savedPassword  // depuis le store (localStorage)

// Indicateur de force du mot de passe
const strengthPct = computed(() => {
  const p = newPass.value
  if (!p) return 0
  let score = 0
  if (p.length >= 6)  score += 25
  if (p.length >= 10) score += 25
  if (/[A-Z]/.test(p)) score += 25
  if (/[0-9!@#$%^&*]/.test(p)) score += 25
  return score
})
const strengthColor = computed(() => {
  if (strengthPct.value <= 25) return '#ef4444'
  if (strengthPct.value <= 50) return '#f59e0b'
  if (strengthPct.value <= 75) return '#3b82f6'
  return '#22c55e'
})
const strengthLabel = computed(() => {
  if (strengthPct.value <= 25) return 'ضعيف'
  if (strengthPct.value <= 50) return 'متوسط'
  if (strengthPct.value <= 75) return 'قوي'
  return 'قوي جداً'
})

onMounted(async () => {
  const { data } = await api.get('/auth/me/')
  auth.updateUser(data)          // sync photo_url + all fields into store
  firstName.value = data.first_name || ''
  lastName.value  = data.last_name  || ''
  email.value     = data.email      || ''
  telephone.value = data.telephone  || ''
})

async function saveProfile() {
  profileErr.value = ''
  profileMsg.value = ''
  profileLoading.value = true
  try {
    await api.patch('/auth/me/', {
      first_name: firstName.value,
      last_name:  lastName.value,
      email:      email.value,
      telephone:  telephone.value,
    })
    profileMsg.value = 'تم حفظ المعلومات بنجاح.'
    setTimeout(() => { profileMsg.value = '' }, 2000)
  } catch (e) {
    profileErr.value = e.response?.data?.error || 'حدث خطأ أثناء الحفظ.'
    setTimeout(() => { profileErr.value = '' }, 2000)
  } finally {
    profileLoading.value = false
  }
}

async function changePassword() {
  passErr.value = ''
  passMsg.value = ''
  if (!currentPass.value) { passErr.value = 'الرجاء إدخال كلمة المرور الحالية.'; return }
  if (newPass.value.length < 6) { passErr.value = 'يجب أن تحتوي كلمة المرور الجديدة على 6 أحرف على الأقل.'; return }
  if (newPass.value !== confirmPass.value) { passErr.value = 'كلمتا المرور غير متطابقتين.'; return }
  passLoading.value = true
  try {
    await api.post('/auth/reset-password/', {
      current_password: currentPass.value,
      password: newPass.value,
      confirm: confirmPass.value,
    })
    passMsg.value   = 'تم تغيير كلمة المرور بنجاح.'
    // Mettre à jour le mot de passe sauvegardé
    auth.savePassword(newPass.value)
    currentPass.value = ''
    newPass.value     = ''
    confirmPass.value = ''
    setTimeout(() => { passMsg.value = '' }, 3000)
  } catch (e) {
    passErr.value = e.response?.data?.error || 'حدث خطأ ما.'
    setTimeout(() => { passErr.value = '' }, 4000)
  } finally {
    passLoading.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-header">
      <h2>الإعدادات</h2>
      <p class="subtitle">إدارة معلومات الحساب وكلمة المرور</p>
    </div>

    <div class="sections">

      <!-- Photo Section -->
      <div class="card photo-card">
        <!-- Hidden file input triggered by the upload button -->
        <input ref="photoInput" type="file" accept="image/*" style="display:none"
               :disabled="photoUploading" @change="handlePhotoUpload" />

        <div class="photo-wrap">
          <!-- Click on photo → lightbox -->
          <img v-if="auth.user?.photo_url" :src="auth.user.photo_url" alt="Photo"
               class="photo-img" title="Cliquer pour agrandir"
               @click="showFullPhoto = true" />
          <div v-else class="photo-initials">
            {{ ((auth.user?.first_name || auth.user?.username || '?')[0]).toUpperCase() }}
          </div>
        </div>

        <div class="photo-info">
          <div class="photo-name">{{ auth.user?.first_name || auth.user?.username }}</div>
          <div class="photo-role">مدير</div>
          <button class="btn-photo" :class="{ loading: photoUploading }"
                  :disabled="photoUploading" @click="$refs.photoInput.click()">
            {{ photoUploading ? 'جارٍ الرفع...' : '📷 تغيير صورة الملف الشخصي' }}
          </button>
          <div v-if="photoError" class="photo-err">{{ photoError }}</div>
          <p class="photo-hint">JPG، PNG — الحجم الأقصى 5 ميغابايت</p>
        </div>
      </div>

      <!-- Profile Section -->
      <div class="card">
        <h3 class="card-title">المعلومات الشخصية</h3>

        <div v-if="profileMsg" class="alert success">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-5"/></svg>
          <span>{{ profileMsg }}</span>
          <button class="alert-close" @click="profileMsg = ''">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div v-if="profileErr" class="alert error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>{{ profileErr }}</span>
          <button class="alert-close" @click="profileErr = ''">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div class="form-grid">
          <div class="field">
            <label>الاسم</label>
            <input v-model="firstName" type="text" placeholder="الاسم" />
          </div>
          <div class="field">
            <label>اللقب</label>
            <input v-model="lastName" type="text" placeholder="اللقب" />
          </div>
          <div class="field">
            <label>البريد الإلكتروني</label>
            <input v-model="email" type="email" placeholder="example@school.ma" />
          </div>
          <div class="field">
            <label>رقم الهاتف</label>
            <input v-model="telephone" type="tel" placeholder="06XXXXXXXX" />
          </div>
        </div>

        <div class="card-footer">
          <button class="btn-primary" :disabled="profileLoading" @click="saveProfile">
            {{ profileLoading ? 'جارٍ الحفظ...' : 'حفظ التغييرات' }}
          </button>
        </div>
      </div>

      <!-- Password Section -->
      <div class="card">
        <h3 class="card-title">الأمان — كلمة المرور</h3>

        <div v-if="savedPassword" class="saved-pw-box">
          <div class="saved-pw-label">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            كلمة المرور المحفوظة
          </div>
          <div class="saved-pw-value">
            <span class="pw-text">{{ showSaved ? savedPassword : '••••••••••••' }}</span>
            <button class="eye-btn" @click="showSaved = !showSaved" :title="showSaved ? 'إخفاء' : 'إظهار'">
              <svg v-if="!showSaved" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </div>

        <div v-if="passMsg" class="alert success">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-5"/></svg>
          <span>{{ passMsg }}</span>
          <button class="alert-close" @click="passMsg = ''">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div v-if="passErr" class="alert error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span>{{ passErr }}</span>
          <button class="alert-close" @click="passErr = ''">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div class="pw-fields">
          <div class="field">
            <label>كلمة المرور الحالية <span class="req">*</span></label>
            <div class="pw-input-wrap">
              <input v-model="currentPass" :type="showCurrent ? 'text' : 'password'" placeholder="أدخل كلمة المرور الحالية" />
              <button class="eye-btn" @click="showCurrent = !showCurrent">
                <svg v-if="!showCurrent" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <div class="form-grid">
            <div class="field">
              <label>كلمة المرور الجديدة <span class="req">*</span></label>
              <div class="pw-input-wrap">
                <input v-model="newPass" :type="showNew ? 'text' : 'password'" placeholder="6 أحرف على الأقل" />
                <button class="eye-btn" @click="showNew = !showNew">
                  <svg v-if="!showNew" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
              <!-- Indicateur de force -->
              <div v-if="newPass" class="pw-strength">
                <div class="strength-bar">
                  <div class="strength-fill" :style="{ width: strengthPct + '%', background: strengthColor }"></div>
                </div>
                <span :style="{ color: strengthColor }">{{ strengthLabel }}</span>
              </div>
            </div>
            <div class="field">
              <label>تأكيد كلمة المرور <span class="req">*</span></label>
              <div class="pw-input-wrap">
                <input v-model="confirmPass" :type="showConfirm ? 'text' : 'password'" placeholder="أعد إدخال كلمة المرور الجديدة" />
                <button class="eye-btn" @click="showConfirm = !showConfirm">
                  <svg v-if="!showConfirm" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
              <div v-if="confirmPass && newPass" class="match-hint" :class="newPass === confirmPass ? 'match-ok' : 'match-no'">
                <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <template v-if="newPass === confirmPass"><polyline points="20 6 9 17 4 12"/></template>
                  <template v-else><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></template>
                </svg>
                {{ newPass === confirmPass ? 'كلمتا المرور متطابقتان' : 'غير متطابقتان' }}
              </div>
            </div>
          </div>
        </div>

        <div class="card-footer">
          <button class="btn-primary" :disabled="passLoading" @click="changePassword">
            <svg v-if="!passLoading" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            {{ passLoading ? 'جارٍ التغيير...' : 'تغيير كلمة المرور' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Photo Lightbox -->
  <div v-if="showFullPhoto && auth.user?.photo_url" class="lightbox" @click="showFullPhoto = false">
    <div class="lightbox-box" @click.stop>
      <button class="lightbox-close" @click="showFullPhoto = false">✕</button>
      <img :src="auth.user.photo_url" alt="Photo" class="lightbox-img" />
      <div class="lightbox-name">{{ auth.user?.first_name || auth.user?.username }}</div>
      <div class="lightbox-role">مدير</div>
    </div>
  </div>
</template>

<style scoped>
/* Photo */
.photo-card { display:flex; align-items:center; gap:24px; flex-wrap:wrap; }
.photo-wrap { position:relative; width:90px; height:90px; flex-shrink:0; }
.photo-img { width:90px; height:90px; border-radius:50%; object-fit:cover; border:3px solid #e2e8f0; cursor:pointer; transition:transform 0.2s, box-shadow 0.2s; }
.photo-img:hover { transform:scale(1.05); box-shadow:0 4px 16px rgba(0,0,0,0.18); }
.photo-initials { width:90px; height:90px; border-radius:50%; background:linear-gradient(135deg,#1e3a5f,#1d4ed8); color:white; font-size:2rem; font-weight:900; display:flex; align-items:center; justify-content:center; border:3px solid #bfdbfe; }
.photo-overlay { position:absolute; inset:0; border-radius:50%; background:rgba(0,0,0,0.45); display:flex; align-items:center; justify-content:center; opacity:0; cursor:pointer; transition:opacity 0.2s; }
.photo-wrap:hover .photo-overlay { opacity:1; }
.photo-info { display:flex; flex-direction:column; gap:6px; }
.photo-name { font-size:1.1rem; font-weight:900; color:#1e293b; }
.photo-role { font-size:0.8rem; color:#64748b; }
.btn-photo { display:inline-block; background:#eff6ff; color:#1d4ed8; border:1.5px solid #bfdbfe; font-size:0.82rem; font-weight:700; padding:8px 16px; border-radius:10px; cursor:pointer; transition:background 0.2s; font-family:inherit; }
.btn-photo:hover:not(:disabled) { background:#dbeafe; }
.btn-photo:disabled, .btn-photo.loading { opacity:0.7; cursor:default; }
.photo-err { font-size:0.78rem; color:#dc2626; }
.photo-hint { font-size:0.72rem; color:#94a3b8; margin:0; }

.page-header { margin-bottom:28px; }
.page-header h2 { font-size:1.6rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; }
.sections { display:flex; flex-direction:column; gap:20px; }
.card { background:white; border-radius:20px; padding:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.card-title { font-size:1.05rem; font-weight:800; color:#1e293b; margin:0 0 20px; padding-bottom:14px; border-bottom:1px solid #f1f5f9; }
.form-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
@media (max-width:560px) { .form-grid { grid-template-columns:1fr; } }
.field label { display:block; font-size:0.875rem; font-weight:700; color:#374151; margin-bottom:7px; }
.field input { width:100%; border:1.5px solid #e5e7eb; border-radius:10px; padding:11px 14px; font-size:0.9rem; outline:none; box-sizing:border-box; transition:border-color 0.2s; }
.field input:focus { border-color:#1d4ed8; }
.card-footer { margin-top:20px; display:flex; justify-content:flex-end; }
.btn-primary { background:#1d4ed8; color:white; font-weight:700; font-size:0.9rem; padding:11px 24px; border:none; border-radius:10px; cursor:pointer; transition:opacity 0.2s; }
.btn-primary:disabled { opacity:0.7; cursor:default; }
.btn-primary:hover:not(:disabled) { opacity:0.9; }
.alert {
  display:flex; align-items:center; gap:10px;
  border-radius:12px; padding:13px 16px;
  font-size:0.875rem; font-weight:600;
  margin-bottom:18px;
  border-right:4px solid;
  box-shadow:0 2px 8px rgba(0,0,0,0.07);
  animation:alertIn 0.25s ease;
}
.alert span { flex:1; }
.alert.success { background:#f0fdf4; border-color:#16a34a; color:#15803d; }
.alert.success svg { color:#16a34a; flex-shrink:0; }
.alert.error   { background:#fef2f2; border-color:#dc2626; color:#b91c1c; }
.alert.error svg { color:#dc2626; flex-shrink:0; }
.alert-close {
  background:none; border:none; cursor:pointer; padding:2px;
  display:flex; align-items:center; justify-content:center;
  border-radius:6px; opacity:0.55; transition:opacity 0.15s;
  color:inherit; flex-shrink:0;
}
.alert-close:hover { opacity:1; }
@keyframes alertIn { from { opacity:0; transform:translateY(-6px); } to { opacity:1; transform:translateY(0); } }

/* Password section */
.saved-pw-box { display:flex; align-items:center; justify-content:space-between; gap:12px; background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:12px; padding:14px 18px; margin-bottom:20px; }
.saved-pw-label { display:flex; align-items:center; gap:8px; font-size:0.8rem; font-weight:700; color:#64748b; }
.saved-pw-value { display:flex; align-items:center; gap:10px; }
.pw-text { font-size:0.9rem; font-weight:700; color:#1e293b; letter-spacing:0.05em; font-family:monospace; }
.eye-btn { background:none; border:none; cursor:pointer; padding:4px; display:flex; align-items:center; color:#94a3b8; border-radius:6px; transition:color 0.2s; }
.eye-btn:hover { color:#1d4ed8; }
.pw-fields { display:flex; flex-direction:column; gap:14px; }
.pw-input-wrap { position:relative; }
.pw-input-wrap input { width:100%; border:1.5px solid #e5e7eb; border-radius:10px; padding:11px 14px 11px 40px; font-size:0.9rem; outline:none; box-sizing:border-box; transition:border-color 0.2s; }
.pw-input-wrap input:focus { border-color:#1d4ed8; }
.pw-input-wrap .eye-btn { position:absolute; left:10px; top:50%; transform:translateY(-50%); }
.pw-strength { display:flex; align-items:center; gap:8px; margin-top:6px; }
.strength-bar { flex:1; height:4px; background:#e2e8f0; border-radius:4px; overflow:hidden; }
.strength-fill { height:100%; border-radius:4px; transition:width 0.3s, background 0.3s; }
.pw-strength span { font-size:0.72rem; font-weight:700; min-width:55px; }
.match-hint { display:flex; align-items:center; gap:5px; font-size:0.75rem; font-weight:700; margin-top:6px; }
.match-ok { color:#16a34a; }
.match-no { color:#dc2626; }
.req { color:#dc2626; }
.btn-primary { display:flex; align-items:center; gap:8px; }

/* Lightbox */
.lightbox { position:fixed; inset:0; background:rgba(0,0,0,0.75); display:flex; align-items:center; justify-content:center; z-index:9999; }
.lightbox-box { background:white; border-radius:20px; overflow:hidden; width:340px; text-align:center; position:relative; box-shadow:0 20px 60px rgba(0,0,0,0.3); }
.lightbox-close { position:absolute; top:12px; right:12px; background:rgba(0,0,0,0.4); color:white; border:none; width:32px; height:32px; border-radius:50%; cursor:pointer; font-size:0.9rem; z-index:10; transition:background 0.2s; }
.lightbox-close:hover { background:rgba(0,0,0,0.65); }
.lightbox-img { width:100%; height:280px; object-fit:cover; display:block; }
.lightbox-name { font-size:1.1rem; font-weight:900; color:#1e293b; padding:16px 16px 4px; }
.lightbox-role { font-size:0.8rem; color:#64748b; padding-bottom:20px; }
</style>
