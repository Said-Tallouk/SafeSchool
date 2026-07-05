<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth   = useAuthStore()

const regUsername  = sessionStorage.getItem('reg_user') || ''
const regPassword  = sessionStorage.getItem('reg_pass') || ''
const registerDone = ref(sessionStorage.getItem('reg_ok') === '1')

sessionStorage.removeItem('reg_ok')
sessionStorage.removeItem('reg_user')
sessionStorage.removeItem('reg_pass')

const form    = ref({ username: regUsername, password: regPassword })
const error   = ref('')
const loading = ref(false)
const type    = ref('etudiant')
const showPw  = ref(false)

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    // الطلاب يدخلون فقط الرقم التعريفي، نضيف @safeschool.ma
    let username = form.value.username.trim()
    if (type.value === 'etudiant' && !username.includes('@')) {
      username = username + '@safeschool.ma'
    }
    const user = await auth.login(username, form.value.password)

    // التحقق من أن دور الحساب يطابق التبويب المحدد
    const isStaff   = user.role === 'directeur' || user.role === 'conseiller'
    const isEtudiant = user.role === 'etudiant'

    if (type.value === 'etudiant' && !isEtudiant) {
      auth.logout()
      error.value = 'هذا الحساب مخصص للطاقم. الرجاء تحديد تبويب "الطاقم".'
      return
    }
    if (type.value === 'staff' && !isStaff) {
      auth.logout()
      error.value = 'هذا حساب طالب. الرجاء تحديد تبويب "طالب".'
      return
    }

    // Redirection selon le rôle
    if (user.role === 'directeur')       router.push('/directeur/dashboard')
    else if (user.role === 'conseiller') router.push('/conseiller/dashboard')
    else                                 router.push('/etudiant/dashboard')

  } catch (e) {
    error.value = e.response?.data?.error || 'بيانات الدخول غير صحيحة.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">

    <!-- ── اللوحة اليسرى ── -->
    <div class="left-panel">
      <!-- دوائر زخرفية -->
      <div class="deco deco-1"></div>
      <div class="deco deco-2"></div>
      <div class="deco deco-3"></div>

      <div class="left-content">
        <!-- الشعار + زر الرئيسية -->
        <div class="brand-row">
          <div class="brand">
            <div class="brand-shield">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <span>SafeSchool</span>
          </div>
          <RouterLink to="/" class="btn-home">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            الرئيسية
          </RouterLink>
        </div>

        <!-- رسم توضيحي للمدرسة -->
        <div class="illustration">
          <svg viewBox="0 0 320 280" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Bâtiment école -->
            <rect x="60" y="100" width="200" height="150" rx="4" fill="rgba(255,255,255,0.12)"/>
            <rect x="80" y="80" width="160" height="30" rx="4" fill="rgba(255,255,255,0.18)"/>
            <!-- Toit / Triangle -->
            <polygon points="100,80 160,30 220,80" fill="rgba(255,255,255,0.22)"/>
            <!-- Drapeau -->
            <line x1="160" y1="30" x2="160" y2="10" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
            <rect x="160" y="10" width="18" height="12" rx="1" fill="#fbbf24"/>
            <!-- Fenêtres -->
            <rect x="90"  y="115" width="28" height="28" rx="3" fill="rgba(255,255,255,0.2)"/>
            <rect x="146" y="115" width="28" height="28" rx="3" fill="rgba(255,255,255,0.2)"/>
            <rect x="202" y="115" width="28" height="28" rx="3" fill="rgba(255,255,255,0.2)"/>
            <rect x="90"  y="158" width="28" height="28" rx="3" fill="rgba(255,255,255,0.15)"/>
            <rect x="202" y="158" width="28" height="28" rx="3" fill="rgba(255,255,255,0.15)"/>
            <!-- Porte -->
            <rect x="137" y="175" width="46" height="75" rx="4" fill="rgba(255,255,255,0.25)"/>
            <circle cx="176" cy="213" r="3" fill="rgba(255,255,255,0.5)"/>
            <!-- Sol -->
            <rect x="40" y="248" width="240" height="6" rx="3" fill="rgba(255,255,255,0.15)"/>
            <!-- Arbres -->
            <rect x="28" y="200" width="8" height="48" rx="2" fill="rgba(255,255,255,0.2)"/>
            <ellipse cx="32" cy="190" rx="18" ry="22" fill="rgba(255,255,255,0.15)"/>
            <rect x="284" y="200" width="8" height="48" rx="2" fill="rgba(255,255,255,0.2)"/>
            <ellipse cx="288" cy="190" rx="18" ry="22" fill="rgba(255,255,255,0.15)"/>
            <!-- Élèves stylisés -->
            <circle cx="100" cy="230" r="10" fill="rgba(255,255,255,0.3)"/>
            <rect x="94" y="241" width="12" height="18" rx="4" fill="rgba(255,255,255,0.2)"/>
            <circle cx="220" cy="228" r="10" fill="rgba(255,255,255,0.3)"/>
            <rect x="214" y="239" width="12" height="18" rx="4" fill="rgba(255,255,255,0.2)"/>
            <!-- Livre flottant -->
            <rect x="240" y="70" width="36" height="28" rx="3" fill="rgba(255,255,255,0.18)" transform="rotate(-10 240 70)"/>
            <line x1="258" y1="68" x2="258" y2="96" stroke="rgba(255,255,255,0.4)" stroke-width="1.5" transform="rotate(-10 258 82)"/>
            <!-- Crayon -->
            <rect x="44" y="60" width="8" height="36" rx="2" fill="rgba(255,255,255,0.2)" transform="rotate(20 44 60)"/>
            <polygon points="44,96 52,96 48,106" fill="#fbbf24" transform="rotate(20 48 96)"/>
          </svg>
        </div>

        <!-- نص -->
        <div class="left-text">
          <h2>منصة الحماية المدرسية</h2>
          <p>أبلغ عن التحرش بأمان وسرية تامة. كل بلاغ مهم.</p>
        </div>

        <!-- إحصائيات -->
        <div class="stats-row">
          <div class="stat">
            <strong>100%</strong>
            <span>سري</span>
          </div>
          <div class="stat-sep"></div>
          <div class="stat">
            <strong>24 ساعة</strong>
            <span>وقت الاستجابة</span>
          </div>
          <div class="stat-sep"></div>
          <div class="stat">
            <strong>آمن</strong>
            <span>بيانات محمية</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── اللوحة اليمنى (النموذج) ── -->
    <div class="right-panel">
      <div class="auth-card">

        <div class="auth-logo">
          <div class="logo-shield">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h1>تسجيل الدخول</h1>
          <p>ادخل إلى فضائك في SafeSchool</p>
        </div>

        <!-- تبويبات -->
        <div class="type-tabs">
          <button :class="['tab', type==='etudiant' && 'active']" @click="type='etudiant'">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            طالب
          </button>
          <button :class="['tab', type==='staff' && 'active']" @click="type='staff'">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>
            الطاقم
          </button>
        </div>

        <!-- نجاح التسجيل -->
        <div v-if="registerDone" class="alert-ok">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-5"/></svg>
          تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.
        </div>

        <!-- خطأ -->
        <div v-if="error" class="alert-err">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          {{ error }}
        </div>

        <form @submit.prevent="submit" class="auth-form">
          <div class="field">
            <label>{{ type === 'etudiant' ? 'البريد الإلكتروني' : 'اسم المستخدم' }}</label>
            <div class="input-wrap">
              <svg class="input-icon" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              <input v-model="form.username" type="text" required autofocus :placeholder="type === 'etudiant' ? 'مثال: K172008894@safeschool.ma' : 'معرّفك'" />
            </div>
          </div>
          <div class="field">
            <label>كلمة المرور</label>
            <div class="input-wrap">
              <svg class="input-icon" width="16" height="16" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input v-model="form.password" :type="showPw ? 'text' : 'password'" required placeholder="••••••••" />
              <button type="button" class="eye-btn" @click="showPw = !showPw">
                <svg v-if="!showPw" width="15" height="15" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="15" height="15" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <div v-if="loading" class="btn-spin"></div>
            <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
            {{ loading ? 'جارٍ الدخول...' : 'تسجيل الدخول' }}
          </button>
        </form>

        <div class="auth-links">
          <RouterLink to="/forgot-password" class="link-forgot">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            نسيت كلمة المرور؟
          </RouterLink>
          <div v-if="type === 'etudiant'" class="register-row">
            ليس لديك حساب؟
            <RouterLink to="/register" class="link-register">إنشاء حساب</RouterLink>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
* { box-sizing:border-box; }
.page { display:flex; min-height:100vh; }

/* ── Panneau gauche ── */
.left-panel { flex:1; background:linear-gradient(145deg,#1e3a8a 0%,#1d4ed8 40%,#0891b2 100%); position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; padding:48px 40px; }
@media(max-width:768px){ .left-panel { display:none; } }

/* Cercles décoratifs */
.deco { position:absolute; border-radius:50%; opacity:0.12; }
.deco-1 { width:500px; height:500px; background:white; top:-180px; right:-150px; }
.deco-2 { width:300px; height:300px; background:white; bottom:-100px; left:-80px; }
.deco-3 { width:180px; height:180px; background:#fbbf24; bottom:120px; right:-40px; opacity:0.15; }

.left-content { position:relative; z-index:1; width:100%; max-width:400px; display:flex; flex-direction:column; gap:36px; }

/* Brand */
.brand-row { display:flex; align-items:center; justify-content:space-between; width:100%; }
.brand { display:flex; align-items:center; gap:12px; }
.btn-home { display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.3); color:white; font-size:0.82rem; font-weight:700; padding:8px 16px; border-radius:50px; text-decoration:none; transition:all 0.2s; }
.btn-home:hover { background:rgba(255,255,255,0.28); }
.brand-shield { width:48px; height:48px; border-radius:14px; background:rgba(255,255,255,0.2); display:flex; align-items:center; justify-content:center; border:1.5px solid rgba(255,255,255,0.3); }
.brand span { font-size:1.5rem; font-weight:900; color:white; letter-spacing:-0.5px; }

/* Illustration */
.illustration { width:100%; display:flex; justify-content:center; }
.illustration svg { width:100%; max-width:320px; filter:drop-shadow(0 8px 24px rgba(0,0,0,0.15)); }

/* Texte */
.left-text h2 { font-size:1.35rem; font-weight:900; color:white; margin:0 0 10px; line-height:1.3; }
.left-text p  { font-size:0.875rem; color:rgba(255,255,255,0.75); line-height:1.65; margin:0; }

/* Stats */
.stats-row { display:flex; align-items:center; gap:20px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.15); border-radius:16px; padding:16px 20px; }
.stat { display:flex; flex-direction:column; gap:2px; flex:1; text-align:center; }
.stat strong { font-size:1rem; font-weight:900; color:white; }
.stat span   { font-size:0.7rem; color:rgba(255,255,255,0.65); font-weight:600; }
.stat-sep { width:1px; height:32px; background:rgba(255,255,255,0.2); flex-shrink:0; }

/* ── Panneau droit ── */
.right-panel { width:480px; flex-shrink:0; background:#f8fafc; display:flex; align-items:center; justify-content:center; padding:40px 32px; }
@media(max-width:768px){ .right-panel { width:100%; } }

.auth-card { width:100%; max-width:400px; }

/* Logo */
.auth-logo { text-align:center; margin-bottom:28px; }
.logo-shield { width:56px; height:56px; border-radius:18px; background:linear-gradient(135deg,#1d4ed8,#0891b2); display:flex; align-items:center; justify-content:center; margin:0 auto 14px; box-shadow:0 4px 16px rgba(29,78,216,0.3); }
.auth-logo h1 { font-size:1.5rem; font-weight:900; color:#1e293b; margin:0 0 5px; }
.auth-logo p  { font-size:0.82rem; color:#94a3b8; margin:0; }

/* Tabs */
.type-tabs { display:flex; gap:6px; background:#f1f5f9; border-radius:12px; padding:4px; margin-bottom:24px; }
.tab { flex:1; display:flex; align-items:center; justify-content:center; gap:7px; padding:10px; border:none; border-radius:10px; background:transparent; font-weight:700; font-size:0.85rem; color:#64748b; transition:all 0.2s; cursor:pointer; }
.tab.active { background:white; color:#1d4ed8; box-shadow:0 2px 8px rgba(0,0,0,0.08); }

/* Error */
.alert-err { display:flex; align-items:center; gap:8px; background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:11px 14px; font-size:0.83rem; font-weight:600; margin-bottom:18px; }
.alert-ok  { display:flex; align-items:center; gap:8px; background:#f0fdf4; border:1px solid #bbf7d0; border-right:3px solid #16a34a; color:#15803d; border-radius:10px; padding:11px 14px; font-size:0.83rem; font-weight:600; margin-bottom:18px; animation:slideDown 0.3s ease; }
@keyframes slideDown { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:none} }

/* Form */
.auth-form { display:flex; flex-direction:column; gap:16px; }
.field label { display:block; font-size:0.8rem; font-weight:700; color:#374151; margin-bottom:7px; }
.input-wrap { position:relative; display:flex; align-items:center; }
.input-icon { position:absolute; right:13px; flex-shrink:0; }
.input-wrap input { width:100%; border:1.5px solid #e2e8f0; border-radius:11px; padding:12px 42px; font-size:0.9rem; outline:none; transition:all 0.2s; color:#1e293b; background:white; }
.input-wrap input:focus { border-color:#1d4ed8; background:#fafcff; box-shadow:0 0 0 3px rgba(29,78,216,0.08); }
.eye-btn { position:absolute; left:13px; background:none; border:none; cursor:pointer; padding:0; display:flex; }

/* Submit */
.btn-submit { display:flex; align-items:center; justify-content:center; gap:9px; background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; font-weight:800; font-size:0.95rem; padding:13px; border:none; border-radius:12px; cursor:pointer; transition:opacity 0.2s; margin-top:4px; width:100%; box-shadow:0 4px 14px rgba(29,78,216,0.3); }
.btn-submit:disabled { opacity:0.7; cursor:default; }
.btn-submit:hover:not(:disabled) { opacity:0.92; }
.btn-spin { width:16px; height:16px; border:2px solid rgba(255,255,255,0.4); border-top-color:white; border-radius:50%; animation:spin 0.7s linear infinite; }

/* Links */
.auth-links { margin-top:20px; display:flex; flex-direction:column; align-items:center; gap:12px; }
.link-forgot { display:flex; align-items:center; gap:6px; font-size:0.82rem; color:#64748b; font-weight:600; text-decoration:none; transition:color 0.2s; }
.link-forgot:hover { color:#1d4ed8; }
.register-row { font-size:0.82rem; color:#64748b; }
.link-register { color:#1d4ed8; font-weight:800; margin-right:5px; text-decoration:none; }
.link-register:hover { text-decoration:underline; }

@keyframes spin { to{transform:rotate(360deg)} }
</style>
