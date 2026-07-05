<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router      = useRouter()
const code        = ref('')
const maskedEmail = ref('')
const email       = ref('')
const loading     = ref(false)
const error       = ref('')

onMounted(() => {
  email.value       = sessionStorage.getItem('reset_email') || ''
  maskedEmail.value = sessionStorage.getItem('masked_email') || ''
  if (!email.value) router.push('/forgot-password')
})

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/verify-code/', { email: email.value, code: code.value })
    sessionStorage.setItem('reset_token', data.reset_token)
    router.push('/reset-password')
  } catch (e) {
    error.value = e.response?.data?.error || 'الرمز غير صحيح.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-bg">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-icon">📧</div>
        <h1>رمز التحقق</h1>
        <p>تم إرسال الرمز إلى <strong>{{ maskedEmail }}</strong></p>
      </div>

      <div v-if="error" class="alert error">{{ error }}</div>

      <form @submit.prevent="submit" class="auth-form">
        <div class="field">
          <label>رمز التحقق (6 أرقام)</label>
          <input v-model="code" type="text" inputmode="numeric" maxlength="6" required
                 placeholder="_ _ _ _ _ _" class="otp-input" />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading || code.length < 6">
          {{ loading ? 'جارٍ التحقق...' : 'تأكيد الرمز' }}
        </button>
      </form>

      <div class="auth-links">
        <RouterLink to="/forgot-password" class="link">→ إعادة إرسال الرمز</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-bg { min-height:100vh; background:linear-gradient(135deg,#eff6ff,#e0f2fe); display:flex; align-items:center; justify-content:center; padding:24px; }
.auth-card { background:white; border-radius:20px; padding:40px 36px; width:100%; max-width:420px; box-shadow:0 8px 32px rgba(0,0,0,0.1); }
.auth-logo { text-align:center; margin-bottom:28px; }
.logo-icon { font-size:3rem; margin-bottom:8px; }
.auth-logo h1 { font-size:1.5rem; font-weight:900; color:#1d4ed8; }
.auth-logo p  { font-size:0.875rem; color:#6b7280; margin-top:6px; }
.alert.error { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:12px 16px; font-size:0.875rem; margin-bottom:16px; }
.auth-form { display:flex; flex-direction:column; gap:16px; }
.field label { display:block; font-size:0.875rem; font-weight:700; color:#374151; margin-bottom:6px; }
.otp-input { width:100%; border:2px solid #e5e7eb; border-radius:12px; padding:16px; font-size:1.8rem; font-weight:900; letter-spacing:12px; text-align:center; outline:none; transition:border-color 0.2s; box-sizing:border-box; }
.otp-input:focus { border-color:#1d4ed8; }
.btn-primary { background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; font-weight:700; font-size:1rem; padding:13px; border:none; border-radius:12px; transition:opacity 0.2s; cursor:pointer; }
.btn-primary:disabled { opacity:0.7; }
.auth-links { margin-top:20px; text-align:center; font-size:0.875rem; }
.link { color:#1d4ed8; }
</style>
