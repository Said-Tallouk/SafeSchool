<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()

const profile     = ref(null)
const loading     = ref(true)
const uploading   = ref(false)
const saving      = ref(false)
const uploadError = ref('')
const saveSuccess = ref(false)
const specialty   = ref('')

// ── Password change ──
const currentPass  = ref('')
const newPass      = ref('')
const confirmPass  = ref('')
const showCurrent  = ref(false)
const showNew      = ref(false)
const showConfirm  = ref(false)
const passLoading  = ref(false)
const passError    = ref('')
const passSuccess  = ref(false)

const strengthPct = computed(() => {
  const p = newPass.value
  if (!p) return 0
  let s = 0
  if (p.length >= 6)  s += 25
  if (p.length >= 10) s += 25
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) s += 25
  if (/[0-9]/.test(p) || /[^a-zA-Z0-9]/.test(p)) s += 25
  return s
})
const strengthColor = computed(() => {
  if (strengthPct.value <= 25) return '#ef4444'
  if (strengthPct.value <= 50) return '#f59e0b'
  if (strengthPct.value <= 75) return '#3b82f6'
  return '#16a34a'
})
const strengthLabel = computed(() => {
  if (strengthPct.value <= 25) return 'ضعيف'
  if (strengthPct.value <= 50) return 'متوسط'
  if (strengthPct.value <= 75) return 'جيد'
  return 'قوي'
})
const passwordsMatch = computed(() =>
  confirmPass.value && newPass.value === confirmPass.value
)

async function changePassword() {
  passError.value   = ''
  passSuccess.value = false
  if (!currentPass.value) { passError.value = 'أدخل كلمة المرور الحالية.'; return }
  if (newPass.value.length < 6) { passError.value = 'يجب أن تحتوي كلمة المرور الجديدة على 6 أحرف على الأقل.'; return }
  if (newPass.value !== confirmPass.value) { passError.value = 'كلمتا المرور غير متطابقتين.'; return }
  passLoading.value = true
  try {
    await api.post('/auth/reset-password/', {
      current_password: currentPass.value,
      password:         newPass.value,
      confirm:          confirmPass.value,
    })
    auth.savePassword(newPass.value)
    passSuccess.value = true
    currentPass.value = ''
    newPass.value     = ''
    confirmPass.value = ''
    setTimeout(() => passSuccess.value = false, 4000)
  } catch (e) {
    passError.value = e.response?.data?.error || 'خطأ أثناء تغيير كلمة المرور.'
  } finally {
    passLoading.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/counselors/me/')
    profile.value  = data
    specialty.value = data.specialty || ''
  } finally {
    loading.value = false
  }
})

async function handlePhotoUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadError.value = ''
  uploading.value   = true
  try {
    const form = new FormData()
    form.append('photo', file)
    const { data } = await api.patch('/counselors/me/', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    profile.value = data
  } catch {
    uploadError.value = 'فشل رفع الصورة. حاول مجدداً.'
  } finally {
    uploading.value = false
    e.target.value  = ''
  }
}

async function saveSpecialty() {
  saving.value   = true
  saveSuccess.value = false
  try {
    const form = new FormData()
    form.append('specialty', specialty.value)
    const { data } = await api.patch('/counselors/me/', form)
    profile.value = data
    saveSuccess.value = true
    setTimeout(() => saveSuccess.value = false, 3000)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="profile-page">

    <div class="page-header">
      <h2>ملفي الشخصي</h2>
      <p class="subtitle">إدارة صورتك ومعلوماتك المهنية</p>
    </div>

    <div v-if="loading" class="loading">جارٍ التحميل...</div>

    <div v-else-if="profile" class="profile-layout">

      <!-- Photo card -->
      <div class="photo-card">
        <div class="photo-wrap">
          <img v-if="profile.photo_url" :src="profile.photo_url" alt="Photo" class="photo-img" />
          <div v-else class="photo-placeholder">
            {{ (profile.name || '?')[0].toUpperCase() }}
          </div>
          <label class="photo-overlay" :class="{ uploading }">
            <input type="file" accept="image/*" style="display:none"
                   :disabled="uploading" @change="handlePhotoUpload" />
            <svg v-if="!uploading" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            <span v-else class="spin">⏳</span>
          </label>
        </div>

        <div class="photo-name">{{ profile.name }}</div>
        <div class="photo-role">{{ profile.gender === 'female' ? 'مستشارة' : 'مستشار' }}</div>
        <div v-if="uploadError" class="upload-err">{{ uploadError }}</div>

        <label class="btn-upload-label">
          <input type="file" accept="image/*" style="display:none"
                 :disabled="uploading" @change="handlePhotoUpload" />
          {{ uploading ? 'جارٍ الرفع...' : '📷 تغيير الصورة' }}
        </label>
        <p class="upload-hint">JPG، PNG — الحجم الأقصى 5 ميغابايت</p>
      </div>

      <!-- Info card -->
      <div class="info-card">
        <div class="info-section">
          <div class="info-title">معلومات الحساب</div>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">الاسم الكامل</span>
              <span class="info-val">{{ profile.name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">البريد الإلكتروني</span>
              <span class="info-val">{{ profile.email || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">الجنس</span>
              <span class="info-val">{{ profile.gender === 'male' ? 'ذكر' : 'أنثى' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">الحالة</span>
              <span class="info-val">
                <span :class="['status-dot-badge', profile.is_active ? 'active' : 'inactive']">
                  {{ profile.is_active ? 'نشط' : 'غير نشط' }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <div class="info-section">
          <div class="info-title">التخصص المهني</div>
          <p class="info-hint">صف مجال خبرتك (يُعرض في ملفك الشخصي)</p>
          <textarea v-model="specialty" rows="3"
                    placeholder="مثال: علم النفس المدرسي، الوساطة الاجتماعية، إدارة النزاعات..."
                    class="specialty-input"></textarea>
          <div class="save-row">
            <span v-if="saveSuccess" class="save-ok">✔ تم الحفظ</span>
            <button class="btn-save" :disabled="saving" @click="saveSpecialty">
              {{ saving ? 'جارٍ الحفظ...' : 'حفظ' }}
            </button>
          </div>
        </div>

        <div class="info-section stats-mini">
          <div class="info-title">النشاط</div>
          <div class="mini-stats">
            <div class="mini-stat">
              <div class="mini-num">{{ profile.active_report_count }}</div>
              <div class="mini-label">ملفات نشطة</div>
            </div>
          </div>
        </div>

        <!-- ── Changer le mot de passe ── -->
        <div class="info-section">
          <div class="info-title">الأمان — كلمة المرور</div>

          <div class="pw-fields">
            <div class="pw-field">
              <label>كلمة المرور الحالية</label>
              <div class="pw-input-wrap">
                <input :type="showCurrent ? 'text' : 'password'"
                       v-model="currentPass"
                       placeholder="أدخل كلمة المرور الحالية" />
                <button type="button" class="eye-btn" @click="showCurrent = !showCurrent">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path v-if="!showCurrent" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle v-if="!showCurrent" cx="12" cy="12" r="3"/>
                    <path v-if="showCurrent" d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line v-if="showCurrent" x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="pw-field">
              <label>كلمة المرور الجديدة</label>
              <div class="pw-input-wrap">
                <input :type="showNew ? 'text' : 'password'"
                       v-model="newPass"
                       placeholder="6 أحرف على الأقل" />
                <button type="button" class="eye-btn" @click="showNew = !showNew">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path v-if="!showNew" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle v-if="!showNew" cx="12" cy="12" r="3"/>
                    <path v-if="showNew" d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line v-if="showNew" x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <!-- Barre de force -->
              <div v-if="newPass" class="strength-bar-wrap">
                <div class="strength-bar">
                  <div class="strength-fill"
                       :style="{ width: strengthPct + '%', background: strengthColor }"></div>
                </div>
                <span class="strength-label" :style="{ color: strengthColor }">{{ strengthLabel }}</span>
              </div>
            </div>

            <div class="pw-field">
              <label>تأكيد كلمة المرور</label>
              <div class="pw-input-wrap">
                <input :type="showConfirm ? 'text' : 'password'"
                       v-model="confirmPass"
                       placeholder="أعد إدخال كلمة المرور الجديدة" />
                <button type="button" class="eye-btn" @click="showConfirm = !showConfirm">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path v-if="!showConfirm" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle v-if="!showConfirm" cx="12" cy="12" r="3"/>
                    <path v-if="showConfirm" d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line v-if="showConfirm" x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <p v-if="confirmPass" class="match-hint"
                 :style="{ color: passwordsMatch ? '#16a34a' : '#ef4444' }">
                {{ passwordsMatch ? '✔ كلمتا المرور متطابقتان' : '✘ غير متطابقتين' }}
              </p>
            </div>
          </div>

          <div v-if="passError"   class="pw-error">{{ passError }}</div>
          <div v-if="passSuccess" class="pw-success">✔ تم تغيير كلمة المرور بنجاح</div>

          <div class="save-row">
            <button class="btn-save" :disabled="passLoading" @click="changePassword">
              {{ passLoading ? 'جارٍ التغيير...' : 'تغيير كلمة المرور' }}
            </button>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<style scoped>
.profile-page { max-width:860px; }
.page-header { margin-bottom:28px; }
.page-header h2 { font-size:1.6rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; }
.loading { text-align:center; padding:60px; color:#9ca3af; }

.profile-layout {
  display:grid;
  grid-template-columns:240px 1fr;
  gap:20px;
  align-items:start;
}
@media (max-width:640px) {
  .profile-layout { grid-template-columns:1fr; }
}

/* ── Photo card ── */
.photo-card {
  background:white; border-radius:20px;
  padding:28px 20px;
  box-shadow:0 2px 12px rgba(0,0,0,0.07);
  text-align:center;
  display:flex; flex-direction:column; align-items:center; gap:10px;
}

.photo-wrap {
  position:relative;
  width:120px; height:120px;
}
.photo-img {
  width:120px; height:120px;
  border-radius:50%;
  object-fit:cover;
  border:3px solid #e2e8f0;
}
.photo-placeholder {
  width:120px; height:120px; border-radius:50%;
  background:linear-gradient(135deg,#0d9488,#0891b2);
  color:white; font-size:2.8rem; font-weight:900;
  display:flex; align-items:center; justify-content:center;
  border:3px solid #ccfbf1;
}
.photo-overlay {
  position:absolute; inset:0; border-radius:50%;
  background:rgba(0,0,0,0.45);
  display:flex; align-items:center; justify-content:center;
  opacity:0; cursor:pointer;
  transition:opacity 0.2s;
}
.photo-wrap:hover .photo-overlay { opacity:1; }
.photo-overlay.uploading { opacity:1; }

.photo-name { font-size:1rem; font-weight:800; color:#1e293b; margin-top:4px; }
.photo-role { font-size:0.8rem; color:#64748b; }

.upload-err { font-size:0.78rem; color:#dc2626; }

.btn-upload-label {
  display:inline-block;
  background:#f0fdfa; color:#0d9488;
  border:1.5px solid #99f6e4;
  font-size:0.82rem; font-weight:700;
  padding:8px 16px; border-radius:10px;
  cursor:pointer; transition:background 0.2s;
  margin-top:4px;
}
.btn-upload-label:hover { background:#ccfbf1; }
.upload-hint { font-size:0.72rem; color:#94a3b8; }

/* ── Info card ── */
.info-card {
  background:white; border-radius:20px;
  box-shadow:0 2px 12px rgba(0,0,0,0.07);
  overflow:hidden;
  display:flex; flex-direction:column;
}

.info-section {
  padding:22px 24px;
  border-bottom:1px solid #f1f5f9;
}
.info-section:last-child { border-bottom:none; }

.info-title {
  font-size:0.75rem; font-weight:800;
  color:#94a3b8; text-transform:uppercase;
  letter-spacing:0.07em; margin-bottom:14px;
}
.info-hint { font-size:0.78rem; color:#94a3b8; margin-bottom:10px; }

.info-grid { display:flex; flex-direction:column; gap:0; }
.info-row {
  display:flex; justify-content:space-between; align-items:center;
  padding:10px 0;
  border-bottom:1px solid #f8fafc;
}
.info-row:last-child { border-bottom:none; }
.info-label { font-size:0.82rem; color:#64748b; font-weight:600; }
.info-val   { font-size:0.88rem; color:#1e293b; font-weight:700; }

.status-dot-badge {
  font-size:0.75rem; font-weight:700;
  padding:3px 10px; border-radius:20px;
}
.status-dot-badge.active   { background:#dcfce7; color:#16a34a; }
.status-dot-badge.inactive { background:#fee2e2; color:#dc2626; }

.specialty-input {
  width:100%; border:1.5px solid #e5e7eb; border-radius:10px;
  padding:10px 12px; font-size:0.875rem; resize:vertical;
  outline:none; transition:border-color 0.2s; box-sizing:border-box;
}
.specialty-input:focus { border-color:#0d9488; }

.save-row {
  display:flex; justify-content:flex-end; align-items:center;
  gap:12px; margin-top:10px;
}
.save-ok { font-size:0.82rem; color:#16a34a; font-weight:700; }
.btn-save {
  background:#0d9488; color:white;
  font-weight:700; font-size:0.875rem;
  padding:9px 22px; border:none; border-radius:10px;
  cursor:pointer; transition:opacity 0.2s;
}
.btn-save:disabled { opacity:0.7; }

.mini-stats { display:flex; gap:16px; }
.mini-stat  { text-align:center; }
.mini-num   { font-size:1.8rem; font-weight:900; color:#1d4ed8; }
.mini-label { font-size:0.75rem; color:#64748b; margin-top:2px; }

/* ── Password section ── */
.pw-fields { display:flex; flex-direction:column; gap:14px; margin-bottom:16px; }

.pw-field { display:flex; flex-direction:column; gap:5px; }
.pw-field label { font-size:0.78rem; font-weight:700; color:#374151; }

.pw-input-wrap {
  display:flex; align-items:center;
  border:1.5px solid #e2e8f0; border-radius:10px;
  background:#f9fafb; overflow:hidden;
  transition:border-color 0.2s;
}
.pw-input-wrap:focus-within { border-color:#1d4ed8; background:white; }
.pw-input-wrap input {
  flex:1; border:none; background:none;
  padding:10px 13px; font-size:0.875rem; color:#1e293b;
  outline:none;
}
.eye-btn {
  padding:0 12px; background:none; border:none;
  color:#94a3b8; cursor:pointer; transition:color 0.2s;
  display:flex; align-items:center;
}
.eye-btn:hover { color:#1d4ed8; }

.strength-bar-wrap { display:flex; align-items:center; gap:8px; margin-top:4px; }
.strength-bar { flex:1; height:5px; background:#e2e8f0; border-radius:99px; overflow:hidden; }
.strength-fill { height:100%; border-radius:99px; transition:width 0.3s, background 0.3s; }
.strength-label { font-size:0.72rem; font-weight:700; min-width:36px; }

.match-hint { font-size:0.78rem; font-weight:600; margin:0; }

.pw-error   { background:#fef2f2; color:#dc2626; border-radius:9px; padding:10px 14px; font-size:0.82rem; font-weight:600; margin-bottom:10px; }
.pw-success { background:#f0fdf4; color:#16a34a; border-radius:9px; padding:10px 14px; font-size:0.82rem; font-weight:600; margin-bottom:10px; }
</style>
