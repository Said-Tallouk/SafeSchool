<script setup>
import { ref, onMounted } from 'vue'
import { useCounselorsStore } from '../../stores/counselors'

const store           = useCounselorsStore()
const modal           = ref(false)
const loading         = ref(false)
const error           = ref('')
const viewedCounselor = ref(null)
const confirmModal    = ref(false)
const counselorToDelete = ref(null)
const deleteLoading   = ref(false)
const successBanner   = ref(null) // { name, email, emailSent }

const form = ref({
  name: '', specialty: '', gender: 'female',
  email: '', username: ''
})

onMounted(() => store.fetch())

function openModal() {
  form.value  = { name: '', specialty: '', gender: 'female', email: '', username: '' }
  error.value = ''
  modal.value = true
}

async function save() {
  if (!form.value.name || !form.value.username || !form.value.email) {
    error.value = 'الرجاء ملء جميع الحقول الإلزامية (الاسم، اسم المستخدم، والبريد الإلكتروني).'
    return
  }
  loading.value = true
  error.value   = ''
  try {
    const result = await store.create(form.value)
    modal.value = false
    successBanner.value = {
      name: form.value.name,
      email: form.value.email,
      emailSent: result?.email_sent ?? false
    }
    setTimeout(() => { successBanner.value = null }, 8000)
  } catch (e) {
    error.value = e.response?.data?.error || JSON.stringify(e.response?.data) || 'حدث خطأ ما.'
  } finally { loading.value = false }
}

function askDelete(c) {
  counselorToDelete.value = c
  confirmModal.value = true
}

async function confirmDelete() {
  if (!counselorToDelete.value) return
  deleteLoading.value = true
  try {
    await store.remove(counselorToDelete.value.id)
    confirmModal.value = false
    counselorToDelete.value = null
  } finally {
    deleteLoading.value = false
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>المستشارون</h2>
        <p class="subtitle">إدارة المستشارين النفسيين والاجتماعيين</p>
      </div>
      <button class="btn-primary" @click="openModal">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        إضافة مستشار
      </button>
    </div>

    <!-- Success / email banner -->
    <div v-if="successBanner" :class="['result-banner', successBanner.emailSent ? 'banner-ok' : 'banner-warn']">
      <div class="banner-icon">
        <svg v-if="successBanner.emailSent" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <div class="banner-body">
        <div class="banner-title">
          {{ successBanner.emailSent
            ? `تم إنشاء الحساب — تم إرسال البريد إلى ${successBanner.email}`
            : `تم إنشاء حساب ${successBanner.name}` }}
        </div>
        <div class="banner-sub">
          {{ successBanner.emailSent
            ? `سيتلقى ${successBanner.name} بيانات تسجيل الدخول خلال لحظات.`
            : `⚠️ تعذّر إرسال البريد الإلكتروني. تحقق من إعداد SMTP في ملف .env` }}
        </div>
      </div>
      <button class="banner-close" @click="successBanner = null">✕</button>
    </div>

    <!-- Info bar -->
    <div class="info-bar">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      الحد الأقصى: مستشار ذكر واحد و2 مستشارات إناث لكل مؤسسة.
    </div>

    <!-- Empty -->
    <div v-if="store.counselors.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      </div>
      <p>لم يتم إضافة أي مستشار بعد.</p>
      <button class="btn-primary" @click="openModal">إضافة أول مستشار</button>
    </div>

    <!-- Cards grid -->
    <div v-else class="grid">
      <div v-for="c in store.counselors" :key="c.id" class="counselor-card">

        <!-- Top with avatar -->
        <div class="card-top" :class="c.gender === 'male' ? 'card-top-male' : 'card-top-female'">
          <div class="avatar-wrap" @click="c.photo_url && (viewedCounselor = c)"
               :class="{ 'avatar-clickable': c.photo_url }">
            <img v-if="c.photo_url" :src="c.photo_url" :alt="c.name" class="avatar-img" />
            <span v-else class="avatar-initials" :class="c.gender === 'male' ? 'initials-male' : 'initials-female'">
              {{ c.name?.[0]?.toUpperCase() || '?' }}
            </span>
            <div v-if="c.photo_url" class="avatar-zoom">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
              </svg>
            </div>
          </div>
          <span :class="['gender-tag', c.gender]">
            {{ c.gender === 'male' ? 'ذكر' : 'أنثى' }}
          </span>
        </div>

        <!-- Info -->
        <div class="card-body">
          <h3 class="c-name">{{ c.name }}</h3>
          <p class="c-specialty">{{ c.specialty || 'مستشار/ة مدرسي/ة' }}</p>
          <div v-if="c.email" class="c-email">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
            {{ c.email }}
          </div>
        </div>

        <!-- Footer -->
        <div class="card-footer">
          <div class="stat-box">
            <div class="stat-num">{{ c.active_report_count }}</div>
            <div class="stat-lbl">ملف نشط</div>
          </div>
          <button class="btn-del" @click="askDelete(c)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
              <path d="M10 11v6"/><path d="M14 11v6"/>
            </svg>
            حذف
          </button>
        </div>
      </div>
    </div>

    <!-- ── Photo Lightbox ── -->
    <div v-if="viewedCounselor" class="overlay" @click.self="viewedCounselor = null">
      <div class="profile-modal">
        <button class="profile-close" @click="viewedCounselor = null">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <img :src="viewedCounselor.photo_url" :alt="viewedCounselor.name" class="profile-full-img" />
        <div class="profile-info">
          <div class="profile-name">{{ viewedCounselor.name }}</div>
          <div class="profile-specialty">{{ viewedCounselor.specialty || 'مستشار/ة مدرسي/ة' }}</div>
          <div v-if="viewedCounselor.email" class="profile-email">{{ viewedCounselor.email }}</div>
          <span :class="['gender-tag', viewedCounselor.gender]">
            {{ viewedCounselor.gender === 'male' ? 'ذكر' : 'أنثى' }}
          </span>
        </div>
      </div>
    </div>

    <!-- ── Delete Confirm Modal ── -->
    <div v-if="confirmModal" class="overlay" @click.self="confirmModal = false; counselorToDelete = null">
      <div class="confirm-modal">
        <div class="confirm-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6"/><path d="M14 11v6"/>
            <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
          </svg>
        </div>
        <h3 class="confirm-title">حذف المستشار</h3>
        <p class="confirm-msg">
          أنت على وشك حذف <strong>{{ counselorToDelete?.name }}</strong>.<br/>
          سيُحذف حسابه وجميع ملفاته بشكل نهائي.
        </p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="confirmModal = false; counselorToDelete = null">إلغاء</button>
          <button class="btn-confirm-del" :disabled="deleteLoading" @click="confirmDelete">
            {{ deleteLoading ? 'جارٍ الحذف...' : 'نعم، احذف' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Add Modal ── -->
    <div v-if="modal" class="overlay" @click.self="modal = false">
      <div class="modal">
        <div class="modal-top">
          <div>
            <h3>مستشار جديد</h3>
            <p class="modal-sub">إنشاء حساب مستشار للمؤسسة</p>
          </div>
          <button class="close-btn" @click="modal = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div v-if="error" class="alert-error">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ error }}
        </div>

        <div class="form-sections">
          <div class="form-section">
            <div class="form-section-title">المعلومات الشخصية</div>
            <div class="row">
              <div class="field">
                <label>الاسم الكامل <span class="req">*</span></label>
                <input v-model="form.name" type="text" placeholder="الاسم الأول والعائلي" />
              </div>
              <div class="field">
                <label>التخصص</label>
                <input v-model="form.specialty" type="text" placeholder="مستشار نفسي..." />
              </div>
            </div>
            <div class="field">
              <label>الجنس <span class="req">*</span></label>
              <div class="radio-group">
                <label :class="['radio-opt', form.gender === 'female' ? 'radio-selected' : '']">
                  <input type="radio" v-model="form.gender" value="female" style="display:none" />
                  أنثى (مستشارة)
                </label>
                <label :class="['radio-opt', form.gender === 'male' ? 'radio-selected' : '']">
                  <input type="radio" v-model="form.gender" value="male" style="display:none" />
                  ذكر (مستشار)
                </label>
              </div>
            </div>
            <div class="field">
              <label>البريد الإلكتروني <span class="req">*</span></label>
              <input v-model="form.email" type="email" placeholder="example@school.ma" />
              <span class="field-hint">إلزامي — سيتم إرسال بيانات الدخول لهذا البريد.</span>
            </div>
          </div>

          <div class="form-section">
            <div class="form-section-title">بيانات تسجيل الدخول</div>
            <div class="field">
              <label>اسم المستخدم <span class="req">*</span></label>
              <input v-model="form.username" type="text" placeholder="مثال: zahira.benali" />
            </div>
            <div class="auto-pass-box">
              <div class="auto-pass-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </div>
              <div>
                <div class="auto-pass-title">كلمة المرور تُولَّد تلقائياً</div>
                <div class="auto-pass-desc">
                  يولّد النظام كلمة مرور آمنة ويرسلها مباشرة إلى بريد المستشار.
                  لا يلزم إدخال يدوي.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-outline" @click="modal = false">إلغاء</button>
          <button class="btn-primary" :disabled="loading" @click="save">
            {{ loading ? 'جارٍ الإضافة...' : 'إضافة المستشار' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; }
.page-header h2 { font-size:1.6rem; font-weight:900; color:#1e293b; }
.subtitle { color:#6b7280; margin-top:4px; font-size:0.875rem; }

.btn-primary {
  display:flex; align-items:center; gap:8px;
  background:linear-gradient(135deg,#1d4ed8,#0891b2);
  color:white; font-weight:700; font-size:0.875rem;
  padding:10px 20px; border:none; border-radius:12px;
  cursor:pointer; transition:opacity 0.2s; white-space:nowrap; font-family:inherit;
}
.btn-primary:disabled { opacity:0.7; cursor:default; }
.btn-primary:hover:not(:disabled) { opacity:0.9; }

/* Result banner */
.result-banner {
  display:flex; align-items:flex-start; gap:14px;
  border-radius:14px; padding:16px 18px; margin-bottom:16px;
  border:1.5px solid; animation:slide-in 0.3s ease;
}
@keyframes slide-in { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
.banner-ok   { background:#f0fdf4; border-color:#86efac; color:#166534; }
.banner-warn { background:#fffbeb; border-color:#fde68a; color:#92400e; }
.banner-icon { flex-shrink:0; margin-top:1px; }
.banner-body { flex:1; }
.banner-title { font-weight:800; font-size:0.875rem; margin-bottom:3px; }
.banner-sub   { font-size:0.78rem; opacity:0.85; line-height:1.5; }
.banner-close { background:none; border:none; cursor:pointer; opacity:0.5; font-size:1rem; padding:0; flex-shrink:0; color:inherit; }
.banner-close:hover { opacity:1; }

.info-bar {
  display:flex; align-items:center; gap:8px;
  background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af;
  border-radius:10px; padding:10px 16px;
  font-size:0.82rem; font-weight:600; margin-bottom:24px;
}

/* Empty */
.empty-state {
  text-align:center; padding:60px 24px; background:white; border-radius:16px;
  display:flex; flex-direction:column; align-items:center; gap:16px;
}
.empty-icon { width:80px; height:80px; border-radius:50%; background:#f8fafc; display:flex; align-items:center; justify-content:center; }
.empty-state p { color:#94a3b8; font-size:0.95rem; margin:0; }

/* Grid */
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:18px; }

/* Card */
.counselor-card {
  background:white; border-radius:20px;
  box-shadow:0 2px 12px rgba(0,0,0,0.07);
  overflow:hidden; display:flex; flex-direction:column;
  transition:transform 0.2s, box-shadow 0.2s;
}
.counselor-card:hover { transform:translateY(-3px); box-shadow:0 8px 28px rgba(0,0,0,0.12); }

.card-top {
  padding:28px 20px 20px; display:flex; flex-direction:column;
  align-items:center; gap:14px;
}
.card-top-female { background:linear-gradient(135deg,#fdf4ff,#fce7f3); }
.card-top-male   { background:linear-gradient(135deg,#eff6ff,#e0f2fe); }

.avatar-wrap {
  width:88px; height:88px; border-radius:50%;
  position:relative; overflow:hidden;
  box-shadow:0 4px 16px rgba(0,0,0,0.15);
}
.avatar-clickable { cursor:pointer; }
.avatar-img { width:100%; height:100%; object-fit:cover; border-radius:50%; }
.avatar-initials {
  width:100%; height:100%; border-radius:50%;
  color:white; font-size:2rem; font-weight:900;
  display:flex; align-items:center; justify-content:center;
}
.initials-female { background:linear-gradient(135deg,#a855f7,#ec4899); }
.initials-male   { background:linear-gradient(135deg,#1d4ed8,#0891b2); }
.avatar-zoom {
  position:absolute; inset:0; border-radius:50%;
  background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center;
  opacity:0; transition:opacity 0.2s;
}
.avatar-wrap:hover .avatar-zoom { opacity:1; }

.gender-tag { font-size:0.72rem; font-weight:800; padding:4px 12px; border-radius:20px; }
.gender-tag.female { background:#fae8ff; color:#9333ea; }
.gender-tag.male   { background:#dbeafe; color:#1d4ed8; }

.card-body { padding:16px 20px; flex:1; }
.c-name     { font-size:1rem; font-weight:900; color:#1e293b; margin:0 0 4px; }
.c-specialty { font-size:0.82rem; color:#64748b; margin:0 0 8px; }
.c-email    { display:flex; align-items:center; gap:6px; font-size:0.78rem; color:#94a3b8; }

.card-footer {
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 20px; border-top:1px solid #f1f5f9; background:#fafafa;
}
.stat-num { font-size:1.4rem; font-weight:900; color:#1e293b; line-height:1; }
.stat-lbl { font-size:0.7rem; color:#94a3b8; margin-top:2px; }
.btn-del {
  display:flex; align-items:center; gap:6px;
  background:#fef2f2; color:#dc2626; font-size:0.78rem; font-weight:700;
  padding:7px 14px; border:none; border-radius:10px; cursor:pointer;
  transition:background 0.2s; font-family:inherit;
}
.btn-del:hover { background:#fee2e2; }

/* Overlay */
.overlay {
  position:fixed; inset:0; background:rgba(0,0,0,0.5);
  display:flex; align-items:center; justify-content:center;
  z-index:300; padding:16px; backdrop-filter:blur(4px);
}

/* Profile lightbox */
.profile-modal {
  background:white; border-radius:20px; overflow:hidden;
  width:320px; box-shadow:0 24px 60px rgba(0,0,0,0.25); position:relative;
}
.profile-close {
  position:absolute; top:12px; right:12px; z-index:10;
  background:rgba(0,0,0,0.4); color:white; border:none;
  width:32px; height:32px; border-radius:50%; cursor:pointer;
  display:flex; align-items:center; justify-content:center; transition:background 0.2s;
}
.profile-close:hover { background:rgba(0,0,0,0.65); }
.profile-full-img { width:100%; height:260px; object-fit:cover; display:block; }
.profile-info { padding:20px 24px 24px; text-align:center; }
.profile-name     { font-size:1.15rem; font-weight:900; color:#1e293b; margin-bottom:4px; }
.profile-specialty { font-size:0.85rem; color:#64748b; margin-bottom:4px; }
.profile-email    { font-size:0.78rem; color:#94a3b8; margin-bottom:10px; }

/* Confirm modal */
.confirm-modal {
  background:white; border-radius:20px; padding:32px 28px;
  width:100%; max-width:400px; text-align:center;
  box-shadow:0 20px 60px rgba(0,0,0,0.2);
}
.confirm-icon { width:60px; height:60px; border-radius:50%; background:#fef2f2; display:flex; align-items:center; justify-content:center; margin:0 auto 18px; }
.confirm-title { font-size:1.1rem; font-weight:900; color:#1e293b; margin:0 0 10px; }
.confirm-msg { font-size:0.875rem; color:#6b7280; margin:0 0 24px; line-height:1.6; }
.confirm-msg strong { color:#1e293b; }
.confirm-actions { display:flex; gap:10px; }
.btn-cancel {
  flex:1; padding:11px; border:1.5px solid #e5e7eb; border-radius:12px;
  background:white; color:#374151; font-weight:700; font-size:0.875rem;
  cursor:pointer; font-family:inherit; transition:background 0.2s;
}
.btn-cancel:hover { background:#f9fafb; }
.btn-confirm-del {
  flex:1; padding:11px; border:none; border-radius:12px;
  background:#dc2626; color:white; font-weight:700; font-size:0.875rem;
  cursor:pointer; transition:opacity 0.2s; font-family:inherit;
}
.btn-confirm-del:disabled { opacity:0.7; cursor:default; }
.btn-confirm-del:hover:not(:disabled) { opacity:0.85; }

/* Add modal */
.modal {
  background:white; border-radius:20px; padding:28px;
  width:100%; max-width:580px; max-height:90vh; overflow-y:auto;
  box-shadow:0 20px 60px rgba(0,0,0,0.2);
}
.modal-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:22px; }
.modal-top h3 { font-size:1.1rem; font-weight:900; color:#1e293b; margin:0 0 4px; }
.modal-sub { font-size:0.78rem; color:#94a3b8; margin:0; }
.close-btn {
  background:#f1f5f9; border:none; border-radius:8px;
  width:32px; height:32px; cursor:pointer; flex-shrink:0;
  display:flex; align-items:center; justify-content:center; color:#64748b;
}
.close-btn:hover { background:#e2e8f0; }

.alert-error {
  display:flex; align-items:center; gap:8px;
  background:#fef2f2; border:1px solid #fecaca; color:#dc2626;
  border-radius:10px; padding:10px 14px; font-size:0.875rem; margin-bottom:18px;
}
.form-sections { display:flex; flex-direction:column; gap:20px; }
.form-section  { display:flex; flex-direction:column; gap:12px; }
.form-section-title {
  font-size:0.72rem; font-weight:800; color:#94a3b8;
  text-transform:uppercase; letter-spacing:0.08em;
  padding-bottom:8px; border-bottom:1px solid #f1f5f9;
}
.row { display:flex; gap:12px; }
.row .field { flex:1; }
.field { display:flex; flex-direction:column; gap:6px; }
.field label { font-size:0.82rem; font-weight:700; color:#374151; }
.req { color:#dc2626; }
.field input {
  border:1.5px solid #e5e7eb; border-radius:10px;
  padding:10px 13px; font-size:0.875rem; outline:none;
  transition:border-color 0.2s; box-sizing:border-box; font-family:inherit;
}
.field input:focus { border-color:#1d4ed8; }

.radio-group { display:flex; gap:10px; flex-wrap:wrap; }
.radio-opt {
  display:flex; align-items:center; gap:8px; font-size:0.875rem;
  cursor:pointer; padding:9px 16px; border-radius:10px;
  border:1.5px solid #e5e7eb; color:#374151; font-weight:600;
  transition:all 0.15s; user-select:none;
}
.radio-selected { border-color:#1d4ed8; background:#eff6ff; color:#1d4ed8; }

.field-hint { font-size:0.72rem; color:#0d9488; font-weight:600; margin-top:2px; }

.auto-pass-box {
  display:flex; align-items:flex-start; gap:14px;
  background:#f0fdf4; border:1.5px solid #bbf7d0;
  border-radius:12px; padding:14px 16px;
}
.auto-pass-icon {
  width:36px; height:36px; border-radius:10px;
  background:#dcfce7; display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.auto-pass-title { font-size:0.82rem; font-weight:800; color:#065f46; margin-bottom:4px; }
.auto-pass-desc  { font-size:0.75rem; color:#047857; line-height:1.5; }
.modal-actions {
  display:flex; justify-content:flex-end; gap:10px;
  margin-top:24px; padding-top:18px; border-top:1px solid #f1f5f9;
}
.btn-outline {
  padding:10px 20px; border:1.5px solid #e5e7eb; border-radius:12px;
  background:white; color:#374151; font-weight:700; font-size:0.875rem;
  cursor:pointer; font-family:inherit; transition:background 0.2s;
}
.btn-outline:hover { background:#f9fafb; }
</style>
