<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth    = useAuthStore()
const loading = ref(false)
const errors  = ref('')
const step    = ref(1)
const showPass    = ref(false)
const showConfirm = ref(false)

const fieldErrors = ref({
  first_name: '', last_name: '', username: '',
  email: '', telephone: '', password: '', confirm: ''
})

const form = ref({
  username: '', first_name: '', last_name: '',
  emailPrefix: '', password: '', confirm: '',
  telephone: '', classe: ''
})

const fullEmail = computed(() => {
  const p = form.value.emailPrefix.trim()
  return p ? `${p}@gmail.com` : ''
})

function normalize(str) {
  return str.trim()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9]/g, '')
}

function syncUsername() {
  const first = normalize(form.value.first_name)
  const last  = normalize(form.value.last_name)
  if (first && last) form.value.username = `${first}.${last}`
  else if (first)    form.value.username = first
  validateField('username')
}

function validateField(field) {
  const v = form.value
  switch (field) {
    case 'first_name':
      fieldErrors.value.first_name = v.first_name.trim() ? '' : 'الاسم الأول مطلوب.'
      break
    case 'last_name':
      fieldErrors.value.last_name = v.last_name.trim() ? '' : 'اسم العائلة مطلوب.'
      break
    case 'username':
      if (!v.username.trim())
        fieldErrors.value.username = 'اسم المستخدم مطلوب.'
      else if (!/^[a-zA-Z0-9._\-]+$/.test(v.username))
        fieldErrors.value.username = 'أحرف وأرقام ونقاط وشرطات فقط.'
      else
        fieldErrors.value.username = ''
      break
    case 'email':
      fieldErrors.value.email = !form.value.emailPrefix.trim() ? 'البريد الإلكتروني مطلوب.' : ''
      break
    case 'telephone':
      fieldErrors.value.telephone = (v.telephone && !/^\d{10}$/.test(v.telephone))
        ? 'يجب أن يكون 10 أرقام.' : ''
      break
    case 'password': {
      const p = v.password
      if (!p) { fieldErrors.value.password = ''; break }
      if (p.length < 8)        { fieldErrors.value.password = '8 أحرف على الأقل.'; break }
      if (!/[a-z]/.test(p))   { fieldErrors.value.password = 'مطلوب حرف صغير.'; break }
      if (!/[A-Z]/.test(p))   { fieldErrors.value.password = 'مطلوب حرف كبير.'; break }
      if (!/[0-9]/.test(p))   { fieldErrors.value.password = 'مطلوب رقم.'; break }
      if (!/[!@#$%^&*\-_]/.test(p)) { fieldErrors.value.password = 'مطلوب رمز خاص.'; break }
      fieldErrors.value.password = ''
      if (v.confirm) validateField('confirm')
      break
    }
    case 'confirm':
      fieldErrors.value.confirm = (v.confirm && v.confirm !== v.password)
        ? 'كلمتا المرور غير متطابقتين.' : ''
      break
  }
}

const passRules = computed(() => {
  const p = form.value.password
  return {
    len:    p.length >= 8,
    upper:  /[A-Z]/.test(p),
    lower:  /[a-z]/.test(p),
    digit:  /[0-9]/.test(p),
    symbol: /[!@#$%^&*\-_]/.test(p),
  }
})

function validateStep(s) {
  if (s === 1) {
    validateField('first_name'); validateField('last_name')
    return !fieldErrors.value.first_name && !fieldErrors.value.last_name
  }
  if (s === 2) {
    validateField('email'); validateField('username'); validateField('telephone')
    return !fieldErrors.value.email && !fieldErrors.value.username && !fieldErrors.value.telephone
  }
  if (s === 3) {
    validateField('password'); validateField('confirm')
    return !fieldErrors.value.password && !fieldErrors.value.confirm
           && form.value.password && form.value.confirm
  }
  return true
}

function nextStep() { if (validateStep(step.value)) step.value++ }
function prevStep()  { if (step.value > 1) step.value-- }

async function submit() {
  if (!validateStep(3)) return
  Object.keys(fieldErrors.value).forEach(k => { fieldErrors.value[k] = '' })
  errors.value  = ''
  loading.value = true
  try {
    await auth.register({ ...form.value, email: fullEmail.value })
    auth.savePassword(form.value.password)
    sessionStorage.setItem('reg_ok',   '1')
    sessionStorage.setItem('reg_user', form.value.username)
    sessionStorage.setItem('reg_pass', form.value.password)
    window.location.href = '/login'
  } catch (e) {
    loading.value = false
    const data = e.response?.data || {}
    if (data.username)  { fieldErrors.value.username  = data.username[0];  step.value = 2 }
    if (data.email)     { fieldErrors.value.email     = data.email[0];     step.value = 2 }
    if (data.telephone) { fieldErrors.value.telephone = data.telephone[0]; step.value = 2 }
    if (data.password)  { fieldErrors.value.password  = data.password[0];  step.value = 3 }
    errors.value = data.non_field_errors?.[0] || data.error || data.detail
                   || 'حدث خطأ ما. تحقق من اتصالك.'
  }
}

const steps = [
  { n:1, label:'الهوية',  sub:'معلوماتك'         },
  { n:2, label:'الحساب', sub:'الوصول والتواصل'  },
  { n:3, label:'الأمان', sub:'كلمة المرور'      },
]
</script>

<template>
  <div class="page">

    <!-- Fond décoratif -->
    <div class="bg-shape bg-shape-1"></div>
    <div class="bg-shape bg-shape-2"></div>

    <div class="card">

      <!-- ── En-tête ── -->
      <div class="card-header">
        <div class="logo-wrap">
          <div class="logo-shield">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <span class="logo-name">SafeSchool</span>
        </div>
        <div class="header-text">
          <h1>إنشاء حساب طالب</h1>
          <p>بياناتك محمية وآمنة</p>
        </div>
      </div>

      <!-- ── Stepper ── -->
      <div class="stepper">
        <template v-for="(s, i) in steps" :key="s.n">
          <div class="step" :class="{ active: step === s.n, done: step > s.n }">
            <div class="step-circle">
              <svg v-if="step > s.n" width="14" height="14" fill="none" stroke="white" stroke-width="3" viewBox="0 0 24 24">
                <path d="M5 12l5 5 9-9"/>
              </svg>
              <span v-else>{{ s.n }}</span>
            </div>
            <div class="step-info">
              <strong>{{ s.label }}</strong>
              <span>{{ s.sub }}</span>
            </div>
          </div>
          <div v-if="i < steps.length - 1" class="step-connector" :class="{ done: step > s.n }"></div>
        </template>
      </div>

      <!-- ── Erreur globale ── -->
      <div v-if="errors" class="alert-err">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ errors }}
      </div>

      <!-- ── Étape 1 : Identité ── -->
      <div v-if="step === 1" class="step-body">
        <div class="step-title">
          <div class="step-num-badge">1</div>
          <div>
            <h2>المعلومات الشخصية</h2>
            <p>أدخل بياناتك الشخصية</p>
          </div>
        </div>
        <div class="row-2">
          <div class="field">
            <label>الاسم الأول <span class="req">*</span></label>
            <div class="iw" :class="{ err: fieldErrors.first_name }">
              <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              <input v-model="form.first_name" type="text" placeholder="اسمك الأول"
                     @input="syncUsername" @blur="validateField('first_name')" autofocus />
            </div>
            <div v-if="fieldErrors.first_name" class="ferr">
              <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ fieldErrors.first_name }}
            </div>
          </div>
          <div class="field">
            <label>اسم العائلة <span class="req">*</span></label>
            <div class="iw" :class="{ err: fieldErrors.last_name }">
              <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              <input v-model="form.last_name" type="text" placeholder="اسم العائلة"
                     @input="syncUsername" @blur="validateField('last_name')" />
            </div>
            <div v-if="fieldErrors.last_name" class="ferr">
              <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ fieldErrors.last_name }}
            </div>
          </div>
        </div>
        <div class="field">
          <label>القسم <span class="opt">(اختياري)</span></label>
          <div class="iw">
            <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            <input v-model="form.classe" type="text" placeholder="مثال: 3أ" />
          </div>
        </div>
      </div>

      <!-- ── Étape 2 : Compte ── -->
      <div v-if="step === 2" class="step-body">
        <div class="step-title">
          <div class="step-num-badge">2</div>
          <div>
            <h2>معلومات الحساب</h2>
            <p>حدد بيانات تسجيل الدخول</p>
          </div>
        </div>
        <div class="field">
          <label>البريد الإلكتروني <span class="req">*</span></label>
          <div class="email-iw" :class="{ err: fieldErrors.email }">
            <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            <input v-model="form.emailPrefix" type="text" placeholder="مثال" autofocus
                   @blur="validateField('email')" />
            <span class="email-sfx">@gmail.com</span>
          </div>
          <div v-if="fieldErrors.email" class="ferr">
            <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ fieldErrors.email }}
          </div>
        </div>
        <div class="field">
          <label>اسم المستخدم <span class="req">*</span></label>
          <div class="iw" :class="{ err: fieldErrors.username }">
            <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <input v-model="form.username" type="text" placeholder="الاسم.اسم_العائلة"
                   @blur="validateField('username')" />
          </div>
          <span class="hint">يُولَّد تلقائياً — قابل للتعديل إن كان محجوزاً</span>
          <div v-if="fieldErrors.username" class="ferr">
            <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ fieldErrors.username }}
          </div>
        </div>
        <div class="field">
          <label>الهاتف <span class="opt">(اختياري)</span></label>
          <div class="iw" :class="{ err: fieldErrors.telephone }">
            <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81 19.79 19.79 0 01.22 1.18 2 2 0 012.18 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 7.09a16 16 0 006 6l1.06-1.06a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 14.92z"/></svg>
            <input v-model="form.telephone" type="tel" placeholder="06XXXXXXXX"
                   @blur="validateField('telephone')" />
          </div>
          <div v-if="fieldErrors.telephone" class="ferr">
            <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ fieldErrors.telephone }}
          </div>
        </div>
      </div>

      <!-- ── Étape 3 : Sécurité ── -->
      <div v-if="step === 3" class="step-body">
        <div class="step-title">
          <div class="step-num-badge">3</div>
          <div>
            <h2>أمان الحساب</h2>
            <p>اختر كلمة مرور قوية</p>
          </div>
        </div>
        <div class="field">
          <label>كلمة المرور <span class="req">*</span></label>
          <div class="iw pw" :class="{ err: fieldErrors.password }">
            <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            <input v-model="form.password" :type="showPass ? 'text' : 'password'"
                   placeholder="Ex : Said@2025" autofocus @input="validateField('password')" />
            <button type="button" class="eye" @click="showPass = !showPass" tabindex="-1">
              <svg v-if="!showPass" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else           width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
          <div v-if="fieldErrors.password" class="ferr">
            <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ fieldErrors.password }}
          </div>
          <div v-if="form.password" class="pass-rules">
            <div v-for="r in [
              { ok: passRules.len,    text: '8 أحرف على الأقل' },
              { ok: passRules.upper,  text: 'حرف كبير A-Z' },
              { ok: passRules.lower,  text: 'حرف صغير a-z' },
              { ok: passRules.digit,  text: 'رقم 0-9' },
              { ok: passRules.symbol, text: 'رمز !@#$%^&*' },
            ]" :key="r.text" :class="['rule', r.ok ? 'ok' : 'no']">
              <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                <path v-if="r.ok" d="M5 12l5 5 9-9"/><path v-else d="M18 6L6 18M6 6l12 12"/>
              </svg>
              {{ r.text }}
            </div>
          </div>
        </div>
        <div class="field">
          <label>تأكيد كلمة المرور <span class="req">*</span></label>
          <div class="iw pw" :class="{ err: fieldErrors.confirm }">
            <svg class="ico" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            <input v-model="form.confirm" :type="showConfirm ? 'text' : 'password'"
                   placeholder="أعد إدخال كلمة المرور" @input="validateField('confirm')" />
            <button type="button" class="eye" @click="showConfirm = !showConfirm" tabindex="-1">
              <svg v-if="!showConfirm" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else              width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
          <div v-if="fieldErrors.confirm" class="ferr">
            <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ fieldErrors.confirm }}
          </div>
          <div v-if="form.confirm && form.password && !fieldErrors.confirm" class="match-ok">
            <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M5 12l5 5 9-9"/></svg>
            كلمتا المرور متطابقتان
          </div>
        </div>
      </div>

      <!-- ── Navigation ── -->
      <div class="nav-row">
        <button v-if="step > 1" class="btn-back" @click="prevStep">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
          السابق
        </button>
        <div v-else></div>

        <button v-if="step < 3" class="btn-next" @click="nextStep">
          التالي
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <button v-else class="btn-submit" :disabled="loading" @click="submit">
          <div v-if="loading" class="spin"></div>
          <svg v-else width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          {{ loading ? 'جارٍ الإنشاء...' : 'إنشاء حسابي' }}
        </button>
      </div>

      <div class="footer-link">
        لديك حساب؟
        <RouterLink to="/login">تسجيل الدخول</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
* { box-sizing: border-box; }

.page {
  min-height: 100vh;
  background: #f1f5f9;
  display: flex; align-items: center; justify-content: center;
  padding: 32px 16px;
  position: relative; overflow: hidden;
}

/* Formes décoratives subtiles */
.bg-shape { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; }
.bg-shape-1 { width: 600px; height: 600px; background: radial-gradient(circle, rgba(29,78,216,0.07) 0%, transparent 70%); top: -200px; right: -150px; }
.bg-shape-2 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(8,145,178,0.06) 0%, transparent 70%); bottom: -150px; left: -100px; }

/* ── Carte principale ── */
.card {
  position: relative; z-index: 1;
  background: white;
  border-radius: 20px;
  padding: 32px 36px;
  width: 100%; max-width: 520px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.04), 0 10px 40px rgba(0,0,0,0.08);
}

/* ── Header ── */
.card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 28px; }
.logo-wrap { display: flex; align-items: center; gap: 9px; }
.logo-shield { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg,#1d4ed8,#0891b2); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(29,78,216,0.3); }
.logo-name { font-size: 1.05rem; font-weight: 900; color: #1e293b; }
.header-text { border-right: 2px solid #e2e8f0; padding-right: 14px; }
.header-text h1 { font-size: 1.05rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
.header-text p  { font-size: 0.75rem; color: #94a3b8; margin: 0; font-weight: 500; }

/* ── Stepper ── */
.stepper { display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 12px 16px; margin-bottom: 24px; }
.step { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.step-circle { width: 28px; height: 28px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 900; color: #94a3b8; transition: all 0.3s; flex-shrink: 0; }
.step.active .step-circle { background: linear-gradient(135deg,#1d4ed8,#0891b2); color: white; box-shadow: 0 3px 10px rgba(29,78,216,0.35); }
.step.done  .step-circle  { background: #22c55e; color: white; }
.step-info strong { display: block; font-size: 0.75rem; font-weight: 800; color: #374151; line-height: 1.2; }
.step-info span   { font-size: 0.68rem; color: #94a3b8; }
.step.active .step-info strong { color: #1d4ed8; }
.step-connector { flex: 1; height: 2px; background: #e2e8f0; margin: 0 8px; border-radius: 2px; transition: background 0.3s; }
.step-connector.done { background: #22c55e; }

/* ── Alert error ── */
.alert-err { display: flex; align-items: center; gap: 8px; background: #fef2f2; border: 1px solid #fecaca; border-right: 3px solid #dc2626; color: #dc2626; border-radius: 10px; padding: 10px 13px; font-size: 0.81rem; font-weight: 600; margin-bottom: 16px; }

/* ── Step body ── */
.step-body { display: flex; flex-direction: column; gap: 14px; }
.step-title { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; }
.step-num-badge { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg,#1d4ed8,#0891b2); display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 900; color: white; flex-shrink: 0; }
.step-title h2 { font-size: 0.95rem; font-weight: 900; color: #1e293b; margin: 0 0 2px; }
.step-title p  { font-size: 0.75rem; color: #94a3b8; margin: 0; }

.row-2 { display: flex; gap: 12px; }
.row-2 .field { flex: 1; }
.field label { display: block; font-size: 0.78rem; font-weight: 700; color: #374151; margin-bottom: 6px; }
.req { color: #dc2626; }
.opt { color: #94a3b8; font-weight: 500; font-size: 0.7rem; }
.hint { font-size: 0.7rem; color: #94a3b8; margin-top: 4px; display: block; }

/* Input wrapper */
.iw { display: flex; align-items: center; border: 1.5px solid #e2e8f0; border-radius: 10px; background: white; transition: border-color 0.2s, box-shadow 0.2s; position: relative; overflow: hidden; }
.iw:focus-within { border-color: #1d4ed8; box-shadow: 0 0 0 3px rgba(29,78,216,0.07); }
.iw.err { border-color: #dc2626; background: #fff8f8; }
.iw.err:focus-within { box-shadow: 0 0 0 3px rgba(220,38,38,0.07); }
.ico { position: absolute; right: 11px; color: #94a3b8; flex-shrink: 0; pointer-events: none; }
.iw input { flex: 1; border: none; outline: none; padding: 10px 34px 10px 11px; font-size: 0.875rem; background: transparent; color: #1e293b; width: 100%; }
.iw.pw input { padding-left: 38px; }
.eye { position: absolute; left: 9px; background: none; border: none; cursor: pointer; padding: 0; display: flex; }

/* Email */
.email-iw { display: flex; align-items: center; border: 1.5px solid #e2e8f0; border-radius: 10px; background: white; position: relative; transition: border-color 0.2s, box-shadow 0.2s; overflow: hidden; }
.email-iw:focus-within { border-color: #1d4ed8; box-shadow: 0 0 0 3px rgba(29,78,216,0.07); }
.email-iw.err { border-color: #dc2626; background: #fff8f8; }
.email-iw input { flex: 1; border: none; outline: none; padding: 10px 34px 10px 4px; font-size: 0.875rem; background: transparent; color: #1e293b; min-width: 0; }
.email-sfx { padding: 10px 0 10px 11px; font-size: 0.82rem; color: #64748b; white-space: nowrap; font-weight: 600; }

/* Errors / feedback */
.ferr { display: flex; align-items: center; gap: 5px; font-size: 0.73rem; font-weight: 600; color: #dc2626; margin-top: 4px; animation: errIn 0.2s ease; }
@keyframes errIn { from{opacity:0;transform:translateY(-3px)} to{opacity:1;transform:none} }
.match-ok { display: flex; align-items: center; gap: 5px; font-size: 0.73rem; font-weight: 600; color: #16a34a; margin-top: 4px; }

/* Password rules */
.pass-rules { display: grid; grid-template-columns: 1fr 1fr; gap: 5px 12px; margin-top: 8px; padding: 10px 12px; background: #f8fafc; border-radius: 9px; border: 1px solid #e2e8f0; }
.rule { display: flex; align-items: center; gap: 5px; font-size: 0.7rem; font-weight: 600; transition: color 0.2s; }
.rule.ok { color: #16a34a; }
.rule.no { color: #94a3b8; }

/* Navigation */
.nav-row { display: flex; justify-content: space-between; align-items: center; margin-top: 22px; gap: 10px; }
.btn-back { display: flex; align-items: center; gap: 6px; background: white; border: 1.5px solid #e2e8f0; color: #64748b; font-weight: 700; font-size: 0.85rem; padding: 10px 16px; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
.btn-back:hover { border-color: #1d4ed8; color: #1d4ed8; }
.btn-next { display: flex; align-items: center; gap: 6px; background: linear-gradient(135deg,#1d4ed8,#0891b2); color: white; font-weight: 800; font-size: 0.875rem; padding: 10px 20px; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s; box-shadow: 0 4px 12px rgba(29,78,216,0.28); }
.btn-next:hover { opacity: 0.9; }
.btn-submit { display: flex; align-items: center; gap: 7px; background: linear-gradient(135deg,#1d4ed8,#0891b2); color: white; font-weight: 800; font-size: 0.875rem; padding: 10px 20px; border: none; border-radius: 10px; cursor: pointer; transition: opacity 0.2s; box-shadow: 0 4px 12px rgba(29,78,216,0.28); }
.btn-submit:disabled { opacity: 0.7; cursor: default; }
.btn-submit:hover:not(:disabled) { opacity: 0.9; }
.spin { width: 15px; height: 15px; border: 2px solid rgba(255,255,255,0.35); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg) } }

/* Footer */
.footer-link { margin-top: 18px; text-align: center; font-size: 0.8rem; color: #94a3b8; }
.footer-link a { color: #1d4ed8; font-weight: 800; margin-right: 4px; text-decoration: none; }
.footer-link a:hover { text-decoration: underline; }
</style>
