<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router   = useRouter()
const password = ref('')
const confirm  = ref('')
const loading  = ref(false)
const error    = ref('')
const success  = ref('')
let   resetToken = ''

onMounted(() => {
  resetToken = sessionStorage.getItem('reset_token') || ''
  if (!resetToken) router.push('/forgot-password')
})

async function submit() {
  error.value   = ''
  success.value = ''
  if (password.value.length < 6) { error.value = 'يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.'; return }
  if (password.value !== confirm.value) { error.value = 'كلمتا المرور غير متطابقتين.'; return }
  loading.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/auth/reset-password/', {
      password: password.value,
      confirm:  confirm.value,
    }, { headers: { Authorization: `Bearer ${resetToken}` } })
    success.value = 'تم تغيير كلمة المرور بنجاح!'
    sessionStorage.clear()
    setTimeout(() => router.push('/login'), 2000)
  } catch (e) {
    error.value = e.response?.data?.error || 'حدث خطأ ما.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-bg">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-icon">🔒</div>
        <h1>كلمة مرور جديدة</h1>
        <p>اختر كلمة مرور آمنة</p>
      </div>

      <div v-if="error"   class="alert error">{{ error }}</div>
      <div v-if="success" class="alert success">✅ {{ success }}</div>

      <form @submit.prevent="submit" class="auth-form">
        <div class="field">
          <label>كلمة المرور الجديدة</label>
          <input v-model="password" type="password" required placeholder="6 أحرف على الأقل" />
        </div>
        <div class="field">
          <label>تأكيد كلمة المرور</label>
          <input v-model="confirm" type="password" required placeholder="••••••••" />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'جارٍ الحفظ...' : 'حفظ كلمة المرور' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-bg { min-height:100vh; background:linear-gradient(135deg,#eff6ff,#e0f2fe); display:flex; align-items:center; justify-content:center; padding:24px; }
.auth-card { background:white; border-radius:20px; padding:40px 36px; width:100%; max-width:420px; box-shadow:0 8px 32px rgba(0,0,0,0.1); }
.auth-logo { text-align:center; margin-bottom:28px; }
.logo-icon { font-size:3rem; margin-bottom:8px; }
.auth-logo h1 { font-size:1.5rem; font-weight:900; color:#1d4ed8; }
.auth-logo p  { font-size:0.85rem; color:#6b7280; margin-top:6px; }
.alert.error   { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:12px 16px; font-size:0.875rem; margin-bottom:16px; }
.alert.success { background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a; border-radius:10px; padding:12px 16px; font-size:0.875rem; margin-bottom:16px; }
.auth-form { display:flex; flex-direction:column; gap:16px; }
.field label { display:block; font-size:0.875rem; font-weight:700; color:#374151; margin-bottom:6px; }
.field input { width:100%; border:1.5px solid #e5e7eb; border-radius:10px; padding:11px 14px; font-size:0.95rem; outline:none; transition:border-color 0.2s; box-sizing:border-box; }
.field input:focus { border-color:#1d4ed8; }
.btn-primary { background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; font-weight:700; font-size:1rem; padding:13px; border:none; border-radius:12px; transition:opacity 0.2s; cursor:pointer; }
.btn-primary:disabled { opacity:0.7; }
</style>
