<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useReportsStore } from '../../stores/reports'

const router  = useRouter()
const store   = useReportsStore()
const loading = ref(false)
const success = ref(false)
const error   = ref('')

// Wizard step: 1, 2, 3
const currentStep = ref(1)

const TYPES = [
  {
    value: 'التحرش الجسدي',
    label: 'تحرش جسدي',
    color: '#ef4444', bg: '#fef2f2',
    img: '/types/physique.jpg',
    svg: `
      <!-- Victime (gauche) -->
      <circle cx="24" cy="12" r="6" fill="#fca5a5"/>
      <rect x="20" y="20" width="8" height="14" rx="3" fill="#fca5a5"/>
      <line x1="24" y1="26" x2="18" y2="34" stroke="#fca5a5" stroke-width="3" stroke-linecap="round"/>
      <line x1="24" y1="26" x2="30" y2="34" stroke="#fca5a5" stroke-width="3" stroke-linecap="round"/>
      <!-- Agresseur (droite) -->
      <circle cx="56" cy="12" r="6" fill="#ef4444"/>
      <rect x="52" y="20" width="8" height="14" rx="3" fill="#ef4444"/>
      <line x1="56" y1="26" x2="62" y2="34" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>
      <line x1="56" y1="26" x2="50" y2="34" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>
      <!-- Poing frappant -->
      <ellipse cx="40" cy="24" rx="7" ry="5" fill="#ef4444"/>
      <line x1="33" y1="24" x2="24" y2="26" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>
      <!-- Étoiles choc -->
      <text x="14" y="20" font-size="10" fill="#fbbf24">✦</text>
      <text x="8" y="32" font-size="8" fill="#fbbf24">✦</text>
    `
  },
  {
    value: 'التحرش اللفظي',
    label: 'تحرش لفظي',
    color: '#f97316', bg: '#fff7ed',
    img: '/types/verbal.jpg',
    svg: `
      <!-- Personnage -->
      <circle cx="22" cy="13" r="7" fill="#fdba74"/>
      <rect x="17" y="22" width="10" height="15" rx="3" fill="#fdba74"/>
      <!-- Bouche ouverte agressive -->
      <ellipse cx="22" cy="16" rx="4" ry="2.5" fill="#c2410c"/>
      <!-- Bulles de mots méchants -->
      <rect x="35" y="8" width="34" height="14" rx="7" fill="#f97316"/>
      <polygon points="35,18 30,24 40,20" fill="#f97316"/>
      <text x="38" y="19" font-size="8" fill="white" font-weight="bold">STOP!</text>
      <rect x="37" y="28" width="28" height="12" rx="6" fill="#fb923c"/>
      <polygon points="37,36 32,42 42,38" fill="#fb923c"/>
      <text x="40" y="37" font-size="7" fill="white" font-weight="bold">NON!</text>
    `
  },
  {
    value: 'التحرش الإلكتروني',
    label: 'تحرش إلكتروني',
    color: '#8b5cf6', bg: '#f5f3ff',
    img: '/types/cyber.jpg',
    svg: `
      <!-- Écran téléphone -->
      <rect x="27" y="6" width="26" height="42" rx="4" fill="#ddd6fe" stroke="#8b5cf6" stroke-width="2"/>
      <rect x="30" y="12" width="20" height="28" rx="2" fill="white"/>
      <!-- Messages négatifs -->
      <rect x="32" y="14" width="16" height="5" rx="2" fill="#8b5cf6"/>
      <text x="34" y="18" font-size="4.5" fill="white" font-weight="bold">😡 honte!</text>
      <rect x="32" y="21" width="14" height="5" rx="2" fill="#a78bfa"/>
      <text x="34" y="25" font-size="4.5" fill="white">nul...</text>
      <rect x="32" y="28" width="15" height="5" rx="2" fill="#c4b5fd"/>
      <text x="34" y="32" font-size="4.5" fill="#4c1d95">🚫 loser</text>
      <!-- Notification rouge -->
      <circle cx="50" cy="10" r="5" fill="#ef4444"/>
      <text x="47" y="13" font-size="6" fill="white" font-weight="bold">3</text>
    `
  },
  {
    value: 'العنف اللفظي أو التهديد',
    label: 'عنف لفظي / تهديد',
    color: '#dc2626', bg: '#fef2f2',
    img: '/types/menace.jpg',
    svg: `
      <!-- Personnage menaçant -->
      <circle cx="28" cy="12" r="7" fill="#fca5a5"/>
      <rect x="23" y="21" width="10" height="15" rx="3" fill="#fca5a5"/>
      <!-- Bras pointant -->
      <line x1="33" y1="26" x2="50" y2="22" stroke="#fca5a5" stroke-width="3.5" stroke-linecap="round"/>
      <!-- Doigt pointé -->
      <circle cx="52" cy="21" r="3" fill="#dc2626"/>
      <!-- Bouche criante -->
      <ellipse cx="28" cy="15" rx="4" ry="3" fill="#dc2626"/>
      <!-- Triangle danger -->
      <polygon points="58,14 70,38 46,38" fill="#fbbf24" stroke="#dc2626" stroke-width="2"/>
      <text x="58" y="34" font-size="14" text-anchor="middle" fill="#dc2626" font-weight="bold">!</text>
      <!-- Ondes de cri -->
      <path d="M 36 10 Q 40 8 38 14" stroke="#dc2626" fill="none" stroke-width="2"/>
      <path d="M 37 7 Q 43 4 41 12" stroke="#f97316" fill="none" stroke-width="1.5"/>
    `
  },
  {
    value: 'الإقصاء الاجتماعي',
    label: 'إقصاء اجتماعي',
    color: '#0891b2', bg: '#f0f9ff',
    img: '/types/exclusion.jpg',
    svg: `
      <!-- Groupe (3 personnages groupés) -->
      <circle cx="32" cy="12" r="5" fill="#7dd3fc"/>
      <rect x="28" y="19" width="8" height="12" rx="3" fill="#7dd3fc"/>
      <circle cx="44" cy="12" r="5" fill="#7dd3fc"/>
      <rect x="40" y="19" width="8" height="12" rx="3" fill="#7dd3fc"/>
      <circle cx="38" cy="10" r="5" fill="#0891b2"/>
      <rect x="34" y="17" width="8" height="12" rx="3" fill="#0891b2"/>
      <!-- Barre d'exclusion -->
      <line x1="54" y1="8" x2="54" y2="42" stroke="#94a3b8" stroke-width="2.5" stroke-dasharray="4,2"/>
      <!-- Personnage isolé -->
      <circle cx="66" cy="14" r="5" fill="#cbd5e1"/>
      <rect x="62" y="21" width="8" height="12" rx="3" fill="#cbd5e1"/>
      <!-- Flèche repoussée -->
      <line x1="57" y1="24" x2="62" y2="24" stroke="#ef4444" stroke-width="2"/>
      <polygon points="60,21 64,24 60,27" fill="#ef4444"/>
    `
  },
  {
    value: 'التمييز',
    label: 'تمييز',
    color: '#d97706', bg: '#fffbeb',
    img: '/types/discrimination.jpg',
    hasSubtypes: true,
    subtypes: [
      { value: 'التمييز العرقي',  label: 'عرقي',    icon: '🌍', desc: 'الأصل، لون البشرة، الإثنية',  img: '/types/discrimination_raciale.jpg'  },
      { value: 'التمييز الجنسي',  label: 'جنسي',    icon: '⚧',  desc: 'مرتبط بالجنس',               img: '/types/discrimination_sexiste.jpg'  },
      { value: 'التمييز الديني',  label: 'ديني',    icon: '🕊️', desc: 'المعتقد أو الممارسة الدينية', img: '/types/discrimination_religieuse.jpg' },
    ],
    svg: `
      <!-- Deux figures différentes -->
      <circle cx="20" cy="12" r="6" fill="#fbbf24"/>
      <rect x="16" y="20" width="8" height="13" rx="3" fill="#fbbf24"/>
      <circle cx="60" cy="12" r="6" fill="#d97706"/>
      <rect x="56" y="20" width="8" height="13" rx="3" fill="#d97706"/>
      <!-- Barrière -->
      <rect x="36" y="8" width="8" height="30" rx="3" fill="#ef4444"/>
      <line x1="32" y1="14" x2="44" y2="14" stroke="#ef4444" stroke-width="2"/>
      <line x1="32" y1="22" x2="44" y2="22" stroke="#ef4444" stroke-width="2"/>
      <line x1="32" y1="30" x2="44" y2="30" stroke="#ef4444" stroke-width="2"/>
      <!-- Flèche rejetée -->
      <line x1="30" y1="20" x2="37" y2="20" stroke="#ef4444" stroke-width="2.5"/>
      <polygon points="34,17 38,20 34,23" fill="#ef4444"/>
    `
  },
  {
    value: 'التحرش الجنسي',
    label: 'تحرش جنسي',
    color: '#be185d', bg: '#fdf2f8',
    img: '/types/sexuel.jpg',
    svg: `
      <!-- Personnage mal à l'aise -->
      <circle cx="24" cy="12" r="6" fill="#f9a8d4"/>
      <rect x="20" y="20" width="8" height="13" rx="3" fill="#f9a8d4"/>
      <!-- Bras croisés défensivement -->
      <line x1="20" y1="26" x2="14" y2="22" stroke="#f9a8d4" stroke-width="3" stroke-linecap="round"/>
      <line x1="28" y1="26" x2="34" y2="22" stroke="#f9a8d4" stroke-width="3" stroke-linecap="round"/>
      <!-- Bulle de malaise -->
      <circle cx="52" cy="20" r="14" fill="#fce7f3" stroke="#be185d" stroke-width="1.5"/>
      <text x="52" y="17" font-size="11" text-anchor="middle" fill="#be185d">⚠</text>
      <text x="52" y="27" font-size="6.5" text-anchor="middle" fill="#be185d" font-weight="bold">STOP</text>
      <!-- Bouclier protection -->
      <path d="M24 38 Q24 46 24 46 Q24 46 30 42 Q30 38 24 38 Z" fill="#be185d" opacity="0.4"/>
    `
  },
  {
    value: 'أخرى',
    label: 'أخرى',
    color: '#6b7280', bg: '#f9fafb',
    img: '/types/autre.jpg',
    svg: `
      <!-- Clipboard -->
      <rect x="18" y="10" width="32" height="38" rx="4" fill="#e5e7eb" stroke="#9ca3af" stroke-width="2"/>
      <rect x="28" y="6" width="12" height="8" rx="3" fill="#9ca3af"/>
      <!-- Lignes de texte -->
      <line x1="24" y1="22" x2="44" y2="22" stroke="#9ca3af" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="24" y1="29" x2="40" y2="29" stroke="#9ca3af" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="24" y1="36" x2="42" y2="36" stroke="#9ca3af" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Point d'interrogation -->
      <circle cx="60" cy="20" r="12" fill="#6b7280"/>
      <text x="60" y="25" font-size="16" text-anchor="middle" fill="white" font-weight="bold">?</text>
    `
  },
]

const STEPS = [
  { num: 1, title: 'النوع',   desc: 'تصنيف البلاغ'       },
  { num: 2, title: 'الوصف',   desc: 'تفاصيل الحادثة'     },
  { num: 3, title: 'التفاصيل', desc: 'معلومات اختيارية'  },
]

const form = ref({
  report_type:       '',
  description:       '',
  location:          '',
  perpetrator:       '',
  perpetrator_classe:'',
  is_anonymous:      false,
  photo:             null,
})

const photoPreview = ref('')
const photoError   = ref('')

function onPhotoChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { photoError.value = 'حجم الملف كبير جداً (الحد الأقصى 5 ميغابايت).'; return }
  if (!file.type.startsWith('image/')) { photoError.value = 'يُقبل فقط ملفات الصور.'; return }
  photoError.value  = ''
  form.value.photo  = file
  photoPreview.value = URL.createObjectURL(file)
}

function removePhoto() {
  form.value.photo   = null
  photoPreview.value = ''
  photoError.value   = ''
}

// Sous-type discrimination
const showSubtypes = ref(false)
const selectedParentType = ref(null)

function selectType(t) {
  if (t.hasSubtypes) {
    selectedParentType.value = t
    showSubtypes.value = true
    form.value.report_type = ''
  } else {
    showSubtypes.value = false
    selectedParentType.value = null
    form.value.report_type = t.value
    nextStepAuto()
  }
}

function selectSubtype(sub) {
  form.value.report_type = sub.value
  showSubtypes.value = false
  nextStepAuto()
}

function nextStepAuto() {
  error.value = ''
  currentStep.value = 2
}

// Can go to next step?
const canNext = computed(() => {
  if (currentStep.value === 1) return !!form.value.report_type
  if (currentStep.value === 2) return form.value.description.trim().length >= 10
  return true
})

function nextStep() {
  if (!canNext.value) return
  error.value = ''
  if (currentStep.value < 3) currentStep.value++
}

function prevStep() {
  if (currentStep.value > 1) currentStep.value--
}

function stepState(num) {
  if (num < currentStep.value) return 'done'
  if (num === currentStep.value) return 'active'
  return 'locked'
}

async function submit() {
  error.value   = ''
  loading.value = true
  try {
    await store.createReport(form.value)
    success.value = true
    setTimeout(() => router.push('/etudiant/dashboard'), 2500)
  } catch (e) {
    error.value = e.response?.data?.error || 'حدث خطأ ما. حاول مجدداً.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">

    <!-- Page header -->
    <div class="page-header">
      <div class="header-icon">
        <svg width="22" height="22" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24">
          <path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        </svg>
      </div>
      <div>
        <h2>بلاغ جديد</h2>
        <p class="subtitle">معلوماتك محمية وتُعالج بسرية تامة</p>
      </div>
    </div>

    <!-- Success screen -->
    <div v-if="success" class="success-card">
      <div class="success-icon">
        <svg width="40" height="40" fill="none" stroke="#16a34a" stroke-width="2.5" viewBox="0 0 24 24">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>
      <h3>تم إرسال البلاغ بنجاح!</h3>
      <p>تم استلام بلاغك. سيتواصل معك مستشار قريباً.</p>
      <div class="success-loader"></div>
    </div>

    <div v-else class="form-card">

      <!-- ── Stepper ── -->
      <div class="stepper">
        <template v-for="(s, i) in STEPS" :key="s.num">
          <div :class="['step', stepState(s.num)]">
            <div class="step-circle">
              <!-- Done: check icon -->
              <svg v-if="stepState(s.num) === 'done'" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
              <!-- Active or locked: number -->
              <span v-else>{{ s.num }}</span>
            </div>
            <div class="step-text">
              <span class="step-title">{{ s.title }}</span>
              <span class="step-desc">{{ s.desc }}</span>
            </div>
          </div>
          <!-- Connector line between steps -->
          <div v-if="i < STEPS.length - 1" :class="['step-line', s.num < currentStep ? 'line-done' : '']"></div>
        </template>
      </div>

      <!-- ── Error ── -->
      <div v-if="error" class="alert-err">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>

      <!-- ── Step 1 : Type ── -->
      <section v-if="currentStep === 1" class="step-body">
        <div class="step-head">
          <h4>ما نوع المشكلة التي تريد الإبلاغ عنها؟ <span class="req">*</span></h4>
          <p>اختر الفئة التي تناسب وضعك</p>
        </div>
        <!-- Vue principale : grille des types -->
        <div v-if="!showSubtypes" class="type-grid">
          <button
            v-for="t in TYPES" :key="t.value || t.label" type="button"
            :class="['type-btn', form.report_type === t.value && 'active']"
            :style="`--tc:${t.color}`"
            @click="selectType(t)">
            <div class="type-illustration">
              <img :src="t.img" :alt="t.label" class="type-photo"
                   @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
              <div class="type-svg-fallback" :style="`background:${t.bg}`" style="display:none">
                <svg v-html="t.svg" viewBox="0 0 80 60" width="80" height="60"></svg>
              </div>
            </div>
            <span class="type-label">{{ t.label }}</span>
            <span v-if="t.hasSubtypes" class="type-sub-arrow">←</span>
            <span v-if="form.report_type === t.value" class="type-check" :style="`background:${t.color}`">
              <svg width="11" height="11" fill="none" stroke="white" stroke-width="3" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
            </span>
          </button>
        </div>

        <!-- Vue drill-down : sous-types Discrimination -->
        <div v-else class="drilldown" style="animation:fadeIn 0.2s ease">
          <!-- Breadcrumb retour -->
          <button type="button" class="drilldown-back" @click="showSubtypes=false; form.report_type=''">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
            العودة للأنواع
          </button>

          <div class="drilldown-title">
            <div class="drilldown-parent-img">
              <img :src="selectedParentType.img" :alt="selectedParentType.label" class="drilldown-img"
                   @error="$event.target.style.display='none'" />
            </div>
            <div>
              <p class="drilldown-label">تمييز</p>
              <p class="drilldown-sub">اختر نوع التمييز:</p>
            </div>
          </div>

          <div class="subtype-grid">
            <button
              v-for="sub in selectedParentType.subtypes" :key="sub.value" type="button"
              :class="['subtype-btn', form.report_type === sub.value && 'active']"
              @click="selectSubtype(sub)">
              <!-- Miniature photo -->
              <div class="sub-thumb">
                <img :src="sub.img" :alt="sub.label" class="sub-thumb-img"
                     @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                <div class="sub-thumb-fallback" style="display:none">{{ sub.icon }}</div>
              </div>
              <div class="sub-info">
                <span class="sub-label">{{ sub.label }}</span>
                <span class="sub-desc">{{ sub.desc }}</span>
              </div>
              <span v-if="form.report_type === sub.value" class="sub-check">
                <svg width="11" height="11" fill="none" stroke="white" stroke-width="3" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
            </button>
          </div>
        </div>
        <p class="hint-select">
          <svg width="13" height="13" fill="none" stroke="#94a3b8" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          انقر على فئة للانتقال إلى الخطوة التالية
        </p>
      </section>

      <!-- ── Step 2 : Description ── -->
      <section v-else-if="currentStep === 2" class="step-body">
        <div class="step-head">
          <h4>ما الذي حدث؟ <span class="req">*</span></h4>
          <p>صف الوقائع بأكبر قدر من التفاصيل — التاريخ والمكان والأشخاص المعنيون</p>
        </div>

        <!-- Selected type recap -->
        <div class="type-recap" v-if="form.report_type">
          <div class="recap-mini-img" :style="`background:${TYPES.find(t=>t.value===form.report_type)?.bg}`">
            <svg v-html="TYPES.find(t=>t.value===form.report_type)?.svg" viewBox="0 0 80 60" width="36" height="27"></svg>
          </div>
          <span :style="`color:${TYPES.find(t=>t.value===form.report_type)?.color}`" style="font-weight:800">
            {{ TYPES.find(t => t.value === form.report_type)?.label }}
          </span>
          <button type="button" class="recap-change" @click="currentStep = 1">تعديل</button>
        </div>

        <textarea v-model="form.description" rows="7"
                  placeholder="مثال: يوم الثلاثاء 8 أبريل، في الفناء، قام زميلي بـ..."></textarea>
        <div class="char-bar">
          <div class="char-fill" :style="`width:${Math.min(form.description.length/200*100,100)}%`"></div>
        </div>
        <div class="char-count" :class="form.description.length > 0 && form.description.length < 10 ? 'warn' : ''">
          {{ form.description.length }} حرف
          <span v-if="form.description.length > 0 && form.description.length < 10"> — قصير جداً (الحد الأدنى 10)</span>
        </div>
      </section>

      <!-- ── Step 3 : Détails ── -->
      <section v-else-if="currentStep === 3" class="step-body">
        <div class="step-head">
          <h4>معلومات إضافية</h4>
          <p>هذه الحقول اختيارية لكنها تساعد المستشار على مساندتك بشكل أفضل</p>
        </div>

        <div class="two-col">
          <div class="field">
            <label>
              <svg width="13" height="13" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              مكان الحادثة
            </label>
            <input v-model="form.location" type="text" placeholder="مثال: ساحة المدرسة، الممر، الفصل..." />
          </div>
          <div class="field">
            <label>
              <svg width="13" height="13" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>
              المتحرش / المعتدي
              <span class="lbl-opt">اختياري</span>
            </label>
            <input v-model="form.perpetrator" type="text" placeholder="الاسم أو وصف الشخص..." />
          </div>
        </div>

        <div class="two-col">
          <div class="field">
            <label>
              <svg width="13" height="13" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
              قسم المتحرش
              <span class="lbl-opt">اختياري</span>
            </label>
            <input v-model="form.perpetrator_classe" type="text" placeholder="مثال: 3ب، 4أ..." />
          </div>
          <div class="field field-notice">
            <div class="notice-box">
              <svg width="14" height="14" fill="none" stroke="#0891b2" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <p>هذه المعلومات <strong>اختيارية</strong>. أدخل فقط ما تتذكره — سلامتك هي الأولوية.</p>
            </div>
          </div>
        </div>

        <!-- Photo upload -->
        <div class="photo-section">
          <div class="field-label">
            <svg width="13" height="13" fill="none" stroke="#64748b" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            صورة أو دليل (اختياري)
          </div>
          <p class="field-sub">أضف لقطة شاشة أو صورة لإثبات الوقائع (الحد الأقصى 5 ميغابايت)</p>

          <!-- Drop zone / preview -->
          <div v-if="!photoPreview" class="drop-zone" @click="$refs.photoInput.click()">
            <svg width="32" height="32" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            <p>انقر لاختيار صورة</p>
            <span>JPG، PNG، WEBP — الحد الأقصى 5 ميغابايت</span>
            <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="onPhotoChange" />
          </div>

          <div v-else class="photo-preview-wrap">
            <img :src="photoPreview" class="photo-preview" alt="معاينة" />
            <button type="button" class="photo-remove" @click="removePhoto">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              حذف
            </button>
          </div>

          <p v-if="photoError" class="photo-err">{{ photoError }}</p>
        </div>

        <!-- Anonymous -->
        <div class="anon-row" :class="{ 'anon-on': form.is_anonymous }">
          <div class="anon-left">
            <div class="anon-icon">
              <svg width="18" height="18" fill="none" :stroke="form.is_anonymous ? '#1d4ed8' : '#94a3b8'" stroke-width="2" viewBox="0 0 24 24">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
              </svg>
            </div>
            <div>
              <strong>بلاغ مجهول</strong>
              <p>لن يظهر اسمك للمستشار المسؤول</p>
            </div>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="form.is_anonymous" />
            <span class="slider"></span>
          </label>
        </div>
      </section>

      <!-- ── Navigation ── -->
      <div class="nav-bar">
        <div class="nav-left">
          <RouterLink to="/etudiant/dashboard" class="btn-cancel">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            إلغاء
          </RouterLink>
          <button v-if="currentStep > 1" type="button" class="btn-prev" @click="prevStep">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
            رجوع
          </button>
        </div>

        <!-- Step 1 & 2 : Suivant -->
        <button v-if="currentStep < 3" type="button" class="btn-next"
                :disabled="!canNext" @click="nextStep">
          التالي
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </button>

        <!-- Step 3 : إرسال -->
        <button v-else type="button" class="btn-submit" :disabled="loading" @click="submit">
          <svg v-if="!loading" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          <div v-else class="btn-spinner"></div>
          {{ loading ? 'جارٍ الإرسال...' : 'إرسال البلاغ' }}
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.page { display:flex; flex-direction:column; gap:24px; }

/* Header */
.page-header { display:flex; align-items:center; gap:16px; }
.header-icon { width:48px; height:48px; border-radius:14px; background:linear-gradient(135deg,#1d4ed8,#0891b2); display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.page-header h2 { font-size:1.5rem; font-weight:900; color:#1e293b; margin:0; }
.subtitle { color:#94a3b8; margin:3px 0 0; font-size:0.875rem; }

/* Success */
.success-card { background:white; border-radius:20px; padding:52px 32px; text-align:center; box-shadow:0 2px 12px rgba(0,0,0,0.06); max-width:680px; }
.success-icon { width:80px; height:80px; background:#f0fdf4; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px; border:2px solid #bbf7d0; }
.success-card h3 { font-size:1.2rem; font-weight:800; color:#1e293b; margin:0 0 10px; }
.success-card p { font-size:0.9rem; color:#64748b; margin:0 0 28px; line-height:1.6; }
.success-loader { height:5px; background:#e2e8f0; border-radius:5px; overflow:hidden; }
.success-loader::after { content:''; display:block; height:100%; background:linear-gradient(90deg,#1d4ed8,#0891b2); border-radius:5px; animation:load 2.5s linear forwards; }
@keyframes load { from{width:0} to{width:100%} }

/* Form card */
.form-card { background:white; border-radius:20px; box-shadow:0 2px 12px rgba(0,0,0,0.06); overflow:hidden; max-width:720px; }

/* ── Stepper ── */
.stepper { display:flex; align-items:center; padding:24px 28px; background:#fafbff; border-bottom:1px solid #f1f5f9; gap:0; }
.step { display:flex; align-items:center; gap:10px; flex-shrink:0; }
.step-circle { width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.8rem; font-weight:900; transition:all 0.3s; flex-shrink:0; }
.step.active .step-circle { background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; box-shadow:0 0 0 4px #dbeafe; }
.step.done   .step-circle { background:#16a34a; color:white; }
.step.locked .step-circle { background:#e2e8f0; color:#94a3b8; }
.step-text { display:flex; flex-direction:column; }
.step-title { font-size:0.82rem; font-weight:800; line-height:1; }
.step.active .step-title { color:#1d4ed8; }
.step.done   .step-title { color:#16a34a; }
.step.locked .step-title { color:#94a3b8; }
.step-desc { font-size:0.72rem; color:#94a3b8; margin-top:2px; }
.step.locked .step-desc { color:#c4cdd5; }
.step-line { flex:1; height:2px; margin:0 10px; border-radius:2px; transition:background 0.3s; background:#e2e8f0; }
.step-line.line-done { background:linear-gradient(90deg,#16a34a,#22c55e); }

/* Alert */
.alert-err { display:flex; align-items:center; gap:10px; background:#fef2f2; border-bottom:1px solid #fecaca; color:#dc2626; font-size:0.875rem; font-weight:600; padding:14px 24px; }

/* Step body */
.step-body { padding:28px 28px 20px; animation:fadeIn 0.25s ease; }
@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none} }
.step-head { margin-bottom:20px; }
.step-head h4 { font-size:1rem; font-weight:800; color:#1e293b; margin:0 0 5px; }
.step-head p  { font-size:0.82rem; color:#94a3b8; margin:0; }
.req { color:#dc2626; }

/* Type grid */
.type-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
@media(max-width:560px){ .type-grid { grid-template-columns:repeat(2,1fr); } }
.type-btn { position:relative; display:flex; flex-direction:column; align-items:center; background:white; border:2px solid #e2e8f0; border-radius:16px; padding:0 0 14px; font-size:0.84rem; font-weight:700; color:#475569; cursor:pointer; transition:all 0.22s; text-align:center; overflow:hidden; }
.type-btn:hover { border-color:var(--tc); transform:translateY(-2px); box-shadow:0 6px 18px rgba(0,0,0,0.08); }
.type-btn.active { border-color:var(--tc); box-shadow:0 0 0 3px color-mix(in srgb,var(--tc) 20%,transparent); }
.type-illustration { width:100%; height:110px; overflow:hidden; border-radius:14px 14px 0 0; margin-bottom:10px; position:relative; }
.type-photo { width:100%; height:110px; object-fit:cover; display:block; transition:transform 0.3s; filter:brightness(0.92); }
.type-btn:hover .type-photo { transform:scale(1.06); filter:brightness(1); }
.type-btn.active .type-photo { filter:brightness(1); }
.type-svg-fallback { width:100%; height:110px; display:flex; align-items:center; justify-content:center; }
.type-label { line-height:1.35; padding:0 10px; color:#1e293b; font-size:0.82rem; }
.type-btn.active .type-label { color:var(--tc); }
.type-check { position:absolute; top:8px; right:8px; width:20px; height:20px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.type-sub-arrow { font-size:0.72rem; color:#d97706; font-weight:800; margin-top:2px; }
.hint-select { display:flex; align-items:center; gap:6px; font-size:0.78rem; color:#94a3b8; margin-top:14px; }

/* Drill-down */
.drilldown { display:flex; flex-direction:column; gap:14px; }
.drilldown-back { display:inline-flex; align-items:center; gap:6px; background:#f1f5f9; border:none; color:#475569; font-size:0.82rem; font-weight:700; padding:8px 14px; border-radius:10px; cursor:pointer; transition:all 0.2s; width:fit-content; }
.drilldown-back:hover { background:#e2e8f0; color:#1e293b; }
.drilldown-title { display:flex; align-items:center; gap:14px; background:#fffbeb; border:1.5px solid #fde68a; border-radius:14px; padding:14px 16px; }
.drilldown-parent-img { width:52px; height:40px; border-radius:8px; overflow:hidden; flex-shrink:0; }
.drilldown-img { width:100%; height:100%; object-fit:cover; }
.drilldown-label { font-size:0.95rem; font-weight:800; color:#92400e; margin:0 0 2px; }
.drilldown-sub { font-size:0.8rem; color:#a16207; margin:0; }
.subtype-grid { display:flex; flex-direction:column; gap:10px; }
.subtype-btn { position:relative; display:flex; align-items:center; gap:14px; background:white; border:2px solid #e2e8f0; border-radius:14px; padding:14px 18px; font-size:0.875rem; cursor:pointer; transition:all 0.2s; text-align:left; }
.subtype-btn:hover { border-color:#d97706; background:#fffbeb; transform:translateX(-4px); }
.subtype-btn.active { background:#fffbeb; border-color:#d97706; }
.sub-thumb { width:64px; height:48px; border-radius:10px; overflow:hidden; flex-shrink:0; background:#f1f5f9; }
.sub-thumb-img { width:100%; height:100%; object-fit:cover; display:block; }
.sub-thumb-fallback { width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:1.4rem; }
.sub-icon { font-size:1.6rem; flex-shrink:0; }
.sub-info { flex:1; display:flex; flex-direction:column; gap:2px; }
.sub-label { font-weight:800; color:#1e293b; font-size:0.9rem; }
.sub-desc { font-size:0.76rem; color:#94a3b8; }
.subtype-btn.active .sub-label { color:#d97706; }
.sub-check { width:22px; height:22px; border-radius:50%; background:#d97706; display:flex; align-items:center; justify-content:center; flex-shrink:0; }

/* Type recap */
.type-recap { display:inline-flex; align-items:center; gap:8px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:8px 14px; font-size:0.84rem; font-weight:700; color:#1d4ed8; margin-bottom:16px; }
.recap-icon { font-size:1rem; }
.recap-change { background:none; border:none; color:#94a3b8; font-size:0.78rem; font-weight:600; cursor:pointer; padding:0; margin-right:8px; text-decoration:underline; }
.recap-change:hover { color:#1d4ed8; }

/* Textarea */
textarea { width:100%; border:1.5px solid #e2e8f0; border-radius:12px; padding:13px 15px; font-size:0.9rem; outline:none; resize:vertical; transition:border-color 0.2s; box-sizing:border-box; font-family:inherit; color:#1e293b; line-height:1.65; }
textarea:focus { border-color:#1d4ed8; background:#fafcff; }
.char-bar { height:3px; background:#f1f5f9; border-radius:3px; margin-top:8px; overflow:hidden; }
.char-fill { height:100%; background:linear-gradient(90deg,#1d4ed8,#0891b2); border-radius:3px; transition:width 0.3s; }
.char-count { font-size:0.75rem; color:#94a3b8; margin-top:5px; text-align:right; }
.char-count.warn { color:#f97316; font-weight:600; }

/* Two columns */
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:20px; }
@media(max-width:540px){ .two-col { grid-template-columns:1fr; } }
.field label { display:flex; align-items:center; gap:6px; font-size:0.8rem; font-weight:700; color:#475569; margin-bottom:7px; flex-wrap:wrap; }
.lbl-opt { font-size:0.7rem; font-weight:600; color:#94a3b8; background:#f1f5f9; border-radius:6px; padding:1px 7px; margin-left:2px; }
.field input { width:100%; border:1.5px solid #e2e8f0; border-radius:10px; padding:11px 13px; font-size:0.875rem; outline:none; transition:border-color 0.2s; box-sizing:border-box; color:#1e293b; }
.field input:focus { border-color:#1d4ed8; }
.field-notice { display:flex; align-items:center; }
.notice-box { display:flex; gap:10px; align-items:flex-start; background:#f0f9ff; border:1px solid #bae6fd; border-radius:12px; padding:12px 14px; }
.notice-box p { margin:0; font-size:0.78rem; color:#0c4a6e; line-height:1.5; }

/* Photo upload */
.photo-section { margin-bottom:20px; }
.field-label { display:flex; align-items:center; gap:6px; font-size:0.8rem; font-weight:700; color:#475569; margin-bottom:4px; }
.field-sub { font-size:0.78rem; color:#94a3b8; margin:0 0 12px; }
.drop-zone { border:2px dashed #e2e8f0; border-radius:14px; padding:28px 20px; text-align:center; cursor:pointer; transition:all 0.2s; background:#fafbff; }
.drop-zone:hover { border-color:#93c5fd; background:#eff6ff; }
.drop-zone p { font-size:0.875rem; font-weight:600; color:#64748b; margin:10px 0 4px; }
.drop-zone span { font-size:0.75rem; color:#94a3b8; }
.photo-preview-wrap { position:relative; display:inline-block; border-radius:12px; overflow:hidden; border:1.5px solid #e2e8f0; }
.photo-preview { display:block; max-width:100%; max-height:220px; object-fit:cover; border-radius:12px; }
.photo-remove { position:absolute; top:8px; right:8px; display:flex; align-items:center; gap:5px; background:rgba(0,0,0,0.55); color:white; font-size:0.78rem; font-weight:700; border:none; border-radius:8px; padding:6px 10px; cursor:pointer; backdrop-filter:blur(4px); transition:background 0.2s; }
.photo-remove:hover { background:rgba(220,38,38,0.85); }
.photo-err { font-size:0.78rem; color:#dc2626; margin-top:8px; font-weight:600; }

/* Anonymous */
.anon-row { display:flex; align-items:center; justify-content:space-between; gap:14px; padding:16px 18px; background:#f8fafc; border-radius:14px; border:1.5px solid #e2e8f0; transition:all 0.2s; }
.anon-row.anon-on { background:#eff6ff; border-color:#bfdbfe; }
.anon-left { display:flex; align-items:center; gap:14px; }
.anon-icon { width:38px; height:38px; border-radius:10px; background:white; display:flex; align-items:center; justify-content:center; border:1.5px solid #e2e8f0; flex-shrink:0; }
.anon-row strong { font-size:0.875rem; color:#1e293b; display:block; margin-bottom:2px; }
.anon-row p { font-size:0.78rem; color:#94a3b8; margin:0; }
.toggle { position:relative; display:inline-block; width:46px; height:26px; flex-shrink:0; }
.toggle input { opacity:0; width:0; height:0; }
.slider { position:absolute; cursor:pointer; inset:0; background:#d1d5db; border-radius:26px; transition:0.3s; }
.slider:before { content:''; position:absolute; height:20px; width:20px; left:3px; bottom:3px; background:white; border-radius:50%; transition:0.3s; box-shadow:0 1px 4px rgba(0,0,0,0.15); }
.toggle input:checked + .slider { background:#1d4ed8; }
.toggle input:checked + .slider:before { transform:translateX(20px); }

/* Navigation bar */
.nav-bar { display:flex; justify-content:space-between; align-items:center; padding:18px 28px; border-top:1px solid #f1f5f9; background:#fafbff; }
.nav-left { display:flex; align-items:center; gap:10px; }
.btn-cancel { display:flex; align-items:center; gap:6px; background:white; color:#94a3b8; font-weight:600; font-size:0.875rem; padding:10px 16px; border:1.5px solid #e2e8f0; border-radius:10px; text-decoration:none; transition:all 0.2s; }
.btn-cancel:hover { color:#475569; border-color:#cbd5e1; }
.btn-prev { display:flex; align-items:center; gap:6px; background:white; color:#475569; font-weight:700; font-size:0.875rem; padding:10px 18px; border:1.5px solid #e2e8f0; border-radius:10px; cursor:pointer; transition:all 0.2s; }
.btn-prev:hover { background:#f8fafc; }
.btn-next { display:flex; align-items:center; gap:7px; background:linear-gradient(135deg,#1d4ed8,#0891b2); color:white; font-weight:700; font-size:0.875rem; padding:10px 22px; border:none; border-radius:10px; cursor:pointer; transition:opacity 0.2s; }
.btn-next:disabled { opacity:0.45; cursor:not-allowed; }
.btn-submit { display:flex; align-items:center; gap:8px; background:linear-gradient(135deg,#15803d,#16a34a); color:white; font-weight:700; font-size:0.875rem; padding:10px 22px; border:none; border-radius:10px; cursor:pointer; transition:opacity 0.2s; }
.btn-submit:disabled { opacity:0.7; cursor:default; }
.btn-spinner { width:14px; height:14px; border:2px solid rgba(255,255,255,0.4); border-top-color:white; border-radius:50%; animation:spin 0.7s linear infinite; }
@keyframes spin { to{transform:rotate(360deg)} }
</style>
