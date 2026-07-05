<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'
import { useAuthStore } from '../../stores/auth'

const router  = useRouter()
const auth    = useAuthStore()

const form    = ref({ old_password: '', new_password: '', confirm: '' })
const error   = ref('')
const loading = ref(false)
const done    = ref(false)

function skip() {
  auth.updateUser({ must_change_password: false })
  router.push('/etudiant/dashboard')
}

async function submit() {
  error.value = ''
  if (form.value.new_password !== form.value.confirm) {
    error.value = 'كلمتا المرور غير متطابقتين.'
    return
  }
  if (form.value.new_password.length < 6) {
    error.value = 'يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل.'
    return
  }
  loading.value = true
  try {
    await api.post('/auth/change-password/', {
      old_password: form.value.old_password,
      new_password: form.value.new_password,
    })
    auth.updateUser({ must_change_password: false })
    done.value = true
    setTimeout(() => router.push('/etudiant/dashboard'), 1800)
  } catch (e) {
    error.value = e.response?.data?.error || 'حدث خطأ أثناء تغيير كلمة المرور.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="cp-page">
    <div class="cp-card">
      <div class="cp-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
      </div>

      <h2>تغيير كلمة المرور</h2>
      <p class="cp-subtitle">لأمانك، يرجى تعيين كلمة مرور شخصية جديدة.</p>

      <div v-if="done" class="success-msg">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        تم تغيير كلمة المرور بنجاح! جارٍ التحويل...
      </div>

      <form v-else @submit.prevent="submit" class="cp-form">
        <div class="field">
          <label>كلمة المرور الحالية (المؤقتة)</label>
          <input v-model="form.old_password" type="password" required autocomplete="current-password" placeholder="كلمة المرور الواردة من المدير" />
        </div>
        <div class="field">
          <label>كلمة المرور الجديدة</label>
          <input v-model="form.new_password" type="password" required autocomplete="new-password" placeholder="6 أحرف على الأقل" />
        </div>
        <div class="field">
          <label>تأكيد كلمة المرور الجديدة</label>
          <input v-model="form.confirm" type="password" required autocomplete="new-password" placeholder="أعد إدخال كلمة المرور" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'جارٍ الحفظ...' : 'حفظ كلمة المرور' }}
        </button>

        <button type="button" class="btn-skip" @click="skip">
          تخطي في الوقت الحالي
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.cp-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
  padding: 24px;
}

.cp-card {
  background: white;
  border-radius: 24px;
  padding: 40px 36px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 16px 48px rgba(29,78,216,0.12);
  text-align: center;
}

.cp-icon {
  width: 64px; height: 64px; border-radius: 18px;
  background: #eff6ff; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px;
}

.cp-card h2 { font-size: 1.3rem; font-weight: 900; color: #1e293b; margin-bottom: 8px; }
.cp-subtitle { font-size: 0.875rem; color: #6b7280; line-height: 1.6; margin-bottom: 28px; }

.cp-form { text-align: right; }

.field { margin-bottom: 18px; }
.field label { display: block; font-size: 0.8rem; font-weight: 700; color: #374151; margin-bottom: 6px; }
.field input {
  width: 100%; box-sizing: border-box; border: 1.5px solid #e5e7eb; border-radius: 12px;
  padding: 11px 14px; font-size: 0.9rem; outline: none; transition: border-color 0.2s; font-family: inherit;
}
.field input:focus { border-color: #1d4ed8; }

.error-msg { background: #fef2f2; color: #dc2626; font-size: 0.85rem; padding: 10px 14px; border-radius: 10px; margin-bottom: 16px; text-align: center; }

.btn-submit {
  width: 100%; padding: 13px; border: none; border-radius: 14px;
  background: #1d4ed8; color: white; font-weight: 800; font-size: 0.95rem;
  cursor: pointer; transition: opacity 0.2s; font-family: inherit;
}
.btn-submit:disabled { opacity: 0.7; cursor: default; }
.btn-submit:hover:not(:disabled) { opacity: 0.88; }

.btn-skip {
  width: 100%; padding: 11px; border: none; border-radius: 14px;
  background: transparent; color: #94a3b8; font-size: 0.875rem; font-weight: 600;
  cursor: pointer; margin-top: 8px; font-family: inherit; transition: color 0.2s;
}
.btn-skip:hover { color: #64748b; }

.success-msg {
  background: #f0fdf4; color: #16a34a; border-radius: 12px; padding: 16px 20px;
  display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 0.9rem;
  justify-content: center;
}
</style>
