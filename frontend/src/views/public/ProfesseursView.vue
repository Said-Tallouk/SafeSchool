<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const photos  = ref([])
const loading = ref(true)

const SUBJECT_LABELS = {
  education_islamique: 'التربية الإسلامية',
  histoire_geo:        'التاريخ والجغرافيا',
  mathematiques:       'الرياضيات',
  physique:            'الفيزياء',
  francais:            'الفرنسية',
  informatique:        'الإعلاميات',
  anglais:             'الإنجليزية',
  sport:               'رياضة',
  svt:                 'علوم الحياة والأرض',
  autre:               'أخرى',
}

onMounted(async () => {
  try {
    const { data } = await api.get('/photos/?category=professeurs')
    photos.value = data
  } catch { /* silent */ }
  finally { loading.value = false }
})
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
        <span>الأساتذة</span>
      </div>
      <h1><span class="highlight">هيئة التدريس</span></h1>
      <p>أساتذة مؤهلون ومتحمسون، مكرَّسون لنجاح وازدهار كل طالب.</p>
    </div>
  </section>

  <!-- Grid -->
  <section class="content-section">
    <div class="container">

      <div v-if="loading" class="empty-state">
        <div class="spinner"></div>
        <p>جارٍ التحميل…</p>
      </div>

      <div v-else-if="photos.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
        <p>لا يوجد أساتذة متاحون حالياً.</p>
      </div>

      <div v-else class="prof-grid">
        <div v-for="p in photos" :key="p.id" class="prof-card">
          <div class="prof-img-wrap">
            <img :src="p.image_url" :alt="p.title" class="prof-img" />
          </div>
          <div class="prof-info">
            <div class="prof-name">{{ p.title }}</div>
            <span v-if="p.subject" class="prof-subject">
              {{ SUBJECT_LABELS[p.subject] || p.subject }}
            </span>
            <p v-if="p.description" class="prof-desc">{{ p.description }}</p>
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
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #059669 100%);
  padding: 120px 0 80px; text-align: center;
}
.blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; pointer-events: none; }
.b1 { width: 400px; height: 400px; background: #34d399; top: -100px; left: -80px; }
.b2 { width: 250px; height: 250px; background: #60a5fa; bottom: -60px; right: -60px; }
.breadcrumb { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 24px; color: rgba(255,255,255,0.6); font-size: 0.85rem; }
.breadcrumb a { color: rgba(255,255,255,0.7); text-decoration: none; }
.breadcrumb a:hover { color: white; }
.page-hero h1 { font-size: 2.8rem; font-weight: 900; color: white; margin: 0 0 16px; }
.highlight { color: #34d399; }
.page-hero p { color: rgba(255,255,255,0.75); font-size: 1.05rem; max-width: 560px; margin: 0 auto; line-height: 1.7; }

/* Content */
.content-section { padding: 60px 0 80px; background: #f8fafc; }

/* States */
.empty-state { text-align: center; padding: 80px 0; color: #94a3b8; display: flex; flex-direction: column; align-items: center; gap: 14px; }
.empty-state p { font-size: 0.95rem; color: #64748b; margin: 0; }
.spinner { width: 36px; height: 36px; border: 3px solid #e2e8f0; border-top-color: #059669; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Prof grid */
.prof-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 36px;
}

.prof-card {
  background: white;
  border-radius: 18px;
  overflow: hidden;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: transform 0.25s, box-shadow 0.25s;
}
.prof-card:hover { transform: translateY(-5px); box-shadow: 0 12px 32px rgba(0,0,0,0.12); }

.prof-img-wrap {
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f1f5f9;
  margin: 12px 12px 0 12px;
  border-radius: 12px;
}
.prof-img {
  width: 100%; height: 100%;
  object-fit: cover; object-position: center top;
  display: block;
  transition: transform 0.4s;
}
.prof-card:hover .prof-img { transform: scale(1.04); }

.prof-info { padding: 14px 16px; }
.prof-name { font-size: 0.95rem; font-weight: 900; color: #1e293b; margin-bottom: 6px; }
.prof-subject {
  display: inline-block;
  background: #eff6ff; color: #1d4ed8;
  font-size: 0.72rem; font-weight: 700;
  padding: 3px 10px; border-radius: 20px;
  margin-bottom: 7px;
}
.prof-desc { font-size: 0.8rem; color: #6b7280; line-height: 1.5; margin: 0; }

@media (max-width: 768px) {
  .page-hero h1 { font-size: 2rem; }
  .prof-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
}
@media (max-width: 480px) {
  .prof-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
}
</style>
