<script setup>
import { ref, reactive } from 'vue'
import api from '../../api'

const form = reactive({ nom: '', email: '', sujet: '', message: '' })
const sending = ref(false)
const success = ref(false)
const error = ref('')

const subjects = [
  'بلاغ عاجل',
  'طلب معلومات',
  'مشكلة تقنية',
  'شراكة',
  'أخرى',
]

async function submit() {
  error.value = ''
  if (!form.nom || !form.email || !form.sujet || !form.message) {
    error.value = 'يرجى ملء جميع الحقول.'
    return
  }
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRe.test(form.email)) {
    error.value = 'عنوان البريد الإلكتروني غير صالح.'
    return
  }
  sending.value = true
  try {
    // Simulated send — replace with real endpoint if available
    await new Promise(r => setTimeout(r, 1200))
    success.value = true
    Object.assign(form, { nom: '', email: '', sujet: '', message: '' })
  } catch (e) {
    error.value = 'حدث خطأ ما. يرجى المحاولة مجدداً.'
  } finally {
    sending.value = false
  }
}

const infos = [
  {
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
    label: 'العنوان',
    value: '12، شارع المدرسة، الدار البيضاء، المغرب',
    color: '#1d4ed8',
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 9.91a16 16 0 0 0 6.1 6.1l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>`,
    label: 'الهاتف',
    value: '+212 5 22 XX XX XX',
    color: '#7c3aed',
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`,
    label: 'البريد الإلكتروني',
    value: 'contact@safeschool.ma',
    color: '#059669',
  },
  {
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
    label: 'ساعات العمل',
    value: 'الاثنين–الجمعة: 08:00 – 17:00',
    color: '#d97706',
  },
]
</script>

<template>
  <!-- Hero -->
  <section class="page-hero">
    <div class="blob b1"></div>
    <div class="blob b2"></div>
    <div class="container">
      <div class="breadcrumb">
        <RouterLink to="/">الرئيسية</RouterLink>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        <span>اتصل بنا</span>
      </div>
      <h1>تواصل <span class="highlight">معنا</span></h1>
      <p>لديك سؤال أو تحتاج مساعدة أو بلاغ عاجل؟ فريقنا يرد عليك في أقرب وقت.</p>
    </div>
  </section>

  <!-- Main -->
  <section class="main-section">
    <div class="container">
      <div class="grid-2">

        <!-- Left: Infos -->
        <div class="infos-side">
          <h2>ابقَ على تواصل</h2>
          <p class="infos-sub">نحن متاحون للإجابة على جميع أسئلتك المتعلقة بأمان ورفاهية الطلاب.</p>

          <div class="info-cards">
            <div v-for="info in infos" :key="info.label" class="info-card">
              <div class="info-icon" :style="{ background: info.color + '15', color: info.color }" v-html="info.icon"></div>
              <div>
                <div class="info-label">{{ info.label }}</div>
                <div class="info-value">{{ info.value }}</div>
              </div>
            </div>
          </div>

          <div class="emergency-box">
            <div class="emergency-header">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              طوارئ مدرسية
            </div>
            <p>في حالة الطوارئ، اتصل مباشرة برقم الطوارئ للمؤسسة أو سجّل الدخول لإرسال بلاغ فوري.</p>
            <RouterLink to="/register" class="emergency-btn">أبلِّغ الآن</RouterLink>
          </div>
        </div>

        <!-- Right: Form -->
        <div class="form-side">
          <div class="form-card">

            <!-- Success -->
            <div v-if="success" class="success-state">
              <div class="success-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
              <h3>تم إرسال الرسالة!</h3>
              <p>شكراً على رسالتك. سيتصل بك فريقنا خلال 24 ساعة.</p>
              <button class="btn-new" @click="success = false">إرسال رسالة أخرى</button>
            </div>

            <!-- Form -->
            <template v-else>
              <h3>إرسال رسالة</h3>
              <p class="form-sub">جميع الحقول إلزامية.</p>

              <div v-if="error" class="alert-error">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                {{ error }}
              </div>

              <div class="form-row">
                <div class="field">
                  <label>الاسم الكامل</label>
                  <input v-model="form.nom" type="text" placeholder="اسمك الأول واسم العائلة" />
                </div>
                <div class="field">
                  <label>البريد الإلكتروني</label>
                  <input v-model="form.email" type="email" placeholder="بريدك@مثال.com" />
                </div>
              </div>

              <div class="field">
                <label>الموضوع</label>
                <div class="select-wrap">
                  <select v-model="form.sujet">
                    <option value="">اختر موضوعاً...</option>
                    <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
                  </select>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
              </div>

              <div class="field">
                <label>الرسالة</label>
                <textarea v-model="form.message" rows="5" placeholder="اشرح طلبك أو وضعك..."></textarea>
                <div class="char-count" :class="{ warn: form.message.length > 900 }">
                  {{ form.message.length }}/1000
                </div>
              </div>

              <button class="submit-btn" :disabled="sending" @click="submit">
                <span v-if="sending" class="spinner"></span>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                {{ sending ? 'جارٍ الإرسال...' : 'إرسال الرسالة' }}
              </button>
            </template>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<style scoped>
* { box-sizing: border-box; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }

/* Hero */
.page-hero {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0369a1 100%);
  padding: 120px 0 80px; text-align: center;
}
.blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; pointer-events: none; }
.b1 { width: 400px; height: 400px; background: #38bdf8; top: -100px; right: -80px; }
.b2 { width: 250px; height: 250px; background: #60a5fa; bottom: -60px; left: -60px; }
.breadcrumb { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 24px; color: rgba(255,255,255,0.6); font-size: 0.85rem; }
.breadcrumb a { color: rgba(255,255,255,0.7); text-decoration: none; }
.breadcrumb a:hover { color: white; }
.page-hero h1 { font-size: 2.8rem; font-weight: 900; color: white; margin: 0 0 16px; }
.highlight { color: #38bdf8; }
.page-hero p { color: rgba(255,255,255,0.75); font-size: 1.05rem; max-width: 540px; margin: 0 auto; line-height: 1.7; }

/* Main */
.main-section { padding: 72px 0 80px; background: #f8fafc; }
.grid-2 { display: grid; grid-template-columns: 1fr 1.2fr; gap: 48px; align-items: start; }

/* Infos side */
.infos-side h2 { font-size: 1.7rem; font-weight: 800; color: #0f172a; margin: 0 0 12px; }
.infos-sub { color: #64748b; line-height: 1.7; margin-bottom: 32px; font-size: 0.95rem; }
.info-cards { display: flex; flex-direction: column; gap: 14px; margin-bottom: 32px; }
.info-card { display: flex; align-items: flex-start; gap: 16px; background: white; border-radius: 14px; padding: 16px; border: 1px solid #e2e8f0; }
.info-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.info-label { font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
.info-value { font-size: 0.9rem; font-weight: 600; color: #0f172a; }
.emergency-box { background: #fef2f2; border: 1px solid #fecaca; border-radius: 16px; padding: 20px; }
.emergency-header { display: flex; align-items: center; gap: 8px; font-weight: 800; color: #dc2626; font-size: 0.95rem; margin-bottom: 8px; }
.emergency-box p { color: #7f1d1d; font-size: 0.85rem; line-height: 1.6; margin: 0 0 14px; }
.emergency-btn { display: inline-block; background: #dc2626; color: white; padding: 10px 24px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; text-decoration: none; transition: background 0.2s; }
.emergency-btn:hover { background: #b91c1c; }

/* Form side */
.form-card { background: white; border-radius: 24px; padding: 36px; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.form-card h3 { font-size: 1.3rem; font-weight: 800; color: #0f172a; margin: 0 0 6px; }
.form-sub { color: #64748b; font-size: 0.85rem; margin-bottom: 24px; }
.alert-error { display: flex; align-items: center; gap: 8px; background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 12px 16px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 20px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.field label { font-size: 0.82rem; font-weight: 700; color: #374151; }
.field input, .field textarea {
  padding: 11px 14px; border: 1px solid #e2e8f0;
  border-radius: 10px; font-size: 0.9rem; color: #0f172a;
  outline: none; transition: border-color 0.2s; background: #f8fafc;
  font-family: inherit; resize: none;
}
.field input:focus, .field textarea:focus { border-color: #1d4ed8; background: white; }
.select-wrap { position: relative; }
.select-wrap select {
  width: 100%; padding: 11px 36px 11px 14px;
  border: 1px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; color: #0f172a; outline: none;
  background: #f8fafc; appearance: none; cursor: pointer;
  font-family: inherit; transition: border-color 0.2s;
}
.select-wrap select:focus { border-color: #1d4ed8; background: white; }
.select-wrap svg { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; }
.char-count { font-size: 0.72rem; color: #94a3b8; text-align: right; margin-top: 4px; }
.char-count.warn { color: #ef4444; }
.submit-btn {
  width: 100%; padding: 14px; border-radius: 12px;
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  color: white; font-weight: 700; font-size: 0.95rem;
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.2s; margin-top: 4px;
}
.submit-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(29,78,216,0.35); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.4); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Success */
.success-state { text-align: center; padding: 24px 0; }
.success-icon { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #059669, #10b981); display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
.success-state h3 { font-size: 1.4rem; font-weight: 800; color: #0f172a; margin: 0 0 8px; }
.success-state p { color: #64748b; line-height: 1.6; margin-bottom: 24px; }
.btn-new { background: #f8fafc; border: 1px solid #e2e8f0; color: #374151; padding: 10px 24px; border-radius: 10px; font-weight: 600; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.btn-new:hover { background: #f1f5f9; }

@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
  .form-row { grid-template-columns: 1fr; }
}
@media (max-width: 580px) {
  .page-hero h1 { font-size: 2rem; }
  .form-card { padding: 24px; }
}
</style>
