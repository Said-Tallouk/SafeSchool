<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router  = useRouter()
const email   = ref('')
const role    = ref('etudiant')
const loading = ref(false)
const error   = ref('')

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/forgot-password/', { email: email.value, role: role.value })
    sessionStorage.setItem('reset_email',  email.value)
    sessionStorage.setItem('reset_role',   role.value)
    sessionStorage.setItem('masked_email', data.masked_email)
    router.push('/verify-code')
  } catch (e) {
    error.value = e.response?.data?.error || 'حدث خطأ ما. حاول مجدداً.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-bg">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-icon">🔑</div>
        <h1>نسيت كلمة المرور؟</h1>
        <p>أدخل بريدك الإلكتروني لاستقبال رمز التحقق</p>
      </div>

      <div class="role-tabs">
        <button :class="['tab', role === 'etudiant' && 'active']" @click="role = 'etudiant'">🎓 طالب</button>
        <button :class="['tab', role === 'staff'    && 'active']" @click="role = 'staff'">👔 طاقم العمل</button>
      </div>

      <div v-if="error" class="alert error">{{ error }}</div>

      <form @submit.prevent="submit" class="auth-form">
        <div class="field">
          <label>البريد الإلكتروني</label>
          <input v-model="email" type="email" required placeholder="exemple@gmail.com" />
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'جارٍ الإرسال...' : 'إرسال الرمز' }}
        </button>
      </form>

      <div class="auth-links">
        <RouterLink to="/login" class="link">→ العودة لتسجيل الدخول</RouterLink>
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
.auth-logo p  { font-size:0.85rem; color:#6b7280; margin-top:6px; }
.role-tabs { display:flex; gap:8px; margin-bottom:24px; background:#f3f4f6; border-radius:12px; padding:4px; }
.tab { flex:1; padding:10px; border:none; border-radius:10px; background:transparent; font-weight:700; font-size:0.9rem; color:#6b7280; transition:all 0.2s; cursor:pointer; }
.tab.active { background:white; color:#1d4ed8; box-shadow:0 2px 8px rgba(0,0,0,0.1); }
.alert.error { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:12px 16px; font-size:0.875rem; margin-bottom:16px; }
.auth-form { display:flex; flex-direction:column; gap:16px; }
.field label { display:block; font-size:0.875rem; font-weight:700; color:#374151; margin-bottom:6px; }
.field input { width:100%; border:1.5px solid #e5e7eb; border-radius:10px; padding:11px 14px; font-size:0.95rem; outline:none; transition:border-color 0.2s; box-sizing:border-box; }
.field input:focus { border-color:#1d4ed8; }
.btn-primary { background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; font-weight:700; font-size:1rem; padding:13px; border:none; border-radius:12px; transition:opacity 0.2s; cursor:pointer; }
.btn-primary:disabled { opacity:0.7; }
.auth-links { margin-top:20px; text-align:center; font-size:0.875rem; }
.link { color:#1d4ed8; }
</style>
