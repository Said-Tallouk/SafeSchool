<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const activites = ref([])
const loading = ref(true)
const activeFilter = ref('all')

const filters = [
  { key: 'all', label: 'الكل' },
  { key: 'planifiee', label: 'مجدولة' },
  { key: 'en_cours', label: 'جارية' },
  { key: 'terminee', label: 'منتهية' },
]

const statusConfig = {
  planifiee: { label: 'مجدولة', color: '#1d4ed8', bg: '#eff6ff' },
  en_cours:  { label: 'جارية',  color: '#d97706', bg: '#fffbeb' },
  terminee:  { label: 'منتهية', color: '#059669', bg: '#f0fdf4' },
  annulee:   { label: 'ملغاة',  color: '#6b7280', bg: '#f9fafb' },
}

const filtered = computed(() => {
  if (activeFilter.value === 'all') return activites.value.filter(a => a.statut !== 'annulee')
  return activites.value.filter(a => a.statut === activeFilter.value)
})

function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d)
  return dt.toLocaleDateString('ar-MA', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}
function formatTime(t) {
  if (!t) return ''
  return t.slice(0, 5)
}
function getMonth(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ar-MA', { month: 'short' }).toUpperCase()
}
function getDay(d) {
  if (!d) return ''
  return new Date(d).getDate()
}

onMounted(async () => {
  try {
    const { data } = await api.get('/activites/')
    activites.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
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
        <span>الأنشطة</span>
      </div>
      <h1><span class="highlight">أنشطتنا</span></h1>
      <p>اكتشف جميع الأنشطة التي تنظمها مؤسستنا لتعزيز رفاه وازدهار الطلاب.</p>
    </div>
  </section>

  <!-- Content -->
  <section class="content-section">
    <div class="container">

      <!-- Filters -->
      <div class="filters">
        <button
          v-for="f in filters" :key="f.key"
          class="filter-btn"
          :class="{ active: activeFilter === f.key }"
          @click="activeFilter = f.key"
        >{{ f.label }}</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>جارٍ تحميل الأنشطة...</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filtered.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        <p>لا توجد أنشطة في هذه الفئة حالياً.</p>
      </div>

      <!-- Grid -->
      <div v-else class="activities-grid">
        <div v-for="a in filtered" :key="a.id" class="activity-card">

          <!-- Image -->
          <div v-if="a.photo_url" class="activity-img-wrap">
            <img :src="a.photo_url" :alt="a.titre" class="activity-img" />
          </div>

          <!-- Bas de carte -->
          <div class="activity-bottom">
          <!-- Date block -->
          <div class="date-block">
            <div class="date-month">{{ getMonth(a.date) }}</div>
            <div class="date-day">{{ getDay(a.date) }}</div>
          </div>

          <!-- Info -->
          <div class="activity-info">
            <div class="activity-header">
              <h3>{{ a.titre }}</h3>
              <span
                class="status-badge"
                :style="{ background: statusConfig[a.statut]?.bg, color: statusConfig[a.statut]?.color }"
              >{{ statusConfig[a.statut]?.label }}</span>
            </div>

            <p v-if="a.description" class="activity-desc">{{ a.description }}</p>

            <div class="activity-meta">
              <span v-if="a.heure" class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {{ formatTime(a.heure) }}
              </span>
              <span v-if="a.lieu" class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ a.lieu }}
              </span>
              <span v-if="a.responsable" class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                {{ a.responsable }}
              </span>
              <span class="meta-item date-full">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                {{ formatDate(a.date) }}
              </span>
            </div>
          </div>
          </div><!-- end activity-bottom -->
        </div>
      </div>

    </div>
  </section>

  <!-- Join CTA -->
  <section class="join-section">
    <div class="container">
      <div class="join-box">
        <div class="join-icon">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div>
          <h3>شارك في الحياة المدرسية</h3>
          <p>سجّل الدخول لعرض التفاصيل والانضمام إلى الأنشطة.</p>
        </div>
        <RouterLink to="/login" class="join-btn">تسجيل الدخول</RouterLink>
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
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #7c3aed 100%);
  padding: 120px 0 80px; text-align: center;
}
.blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; pointer-events: none; }
.b1 { width: 400px; height: 400px; background: #a78bfa; top: -100px; right: -80px; }
.b2 { width: 250px; height: 250px; background: #60a5fa; bottom: -60px; left: -60px; }
.breadcrumb { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 24px; color: rgba(255,255,255,0.6); font-size: 0.85rem; }
.breadcrumb a { color: rgba(255,255,255,0.7); text-decoration: none; }
.breadcrumb a:hover { color: white; }
.page-hero h1 { font-size: 2.8rem; font-weight: 900; color: white; margin: 0 0 16px; }
.highlight { color: #a78bfa; }
.page-hero p { color: rgba(255,255,255,0.75); font-size: 1.05rem; max-width: 560px; margin: 0 auto; line-height: 1.7; }

/* Content */
.content-section { padding: 60px 0 80px; background: #f8fafc; }

/* Filters */
.filters { display: flex; gap: 10px; margin-bottom: 40px; flex-wrap: wrap; }
.filter-btn {
  padding: 8px 20px; border-radius: 50px;
  border: 1px solid #e2e8f0; background: white;
  color: #64748b; font-size: 0.88rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.filter-btn:hover { border-color: #7c3aed; color: #7c3aed; }
.filter-btn.active { background: #7c3aed; border-color: #7c3aed; color: white; }

/* States */
.loading-state, .empty-state { text-align: center; padding: 80px 0; color: #94a3b8; }
.spinner { width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #7c3aed; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Activities grid */
.activities-grid { display: flex; flex-direction: column; gap: 16px; }
.activity-card {
  background: white; border-radius: 16px;
  border: 1px solid #e2e8f0; overflow: hidden;
  transition: all 0.2s;
}
.activity-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-2px); }

.activity-img-wrap { width: 100%; height: 300px; overflow: hidden; }
.activity-img { width: 100%; height: 100%; object-fit: cover; object-position: center top; display: block; }
.activity-card:hover .activity-img { transform: scale(1.03); }

.activity-bottom {
  display: flex; gap: 24px; align-items: flex-start; padding: 20px 24px;
}

.date-block {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  border-radius: 12px; padding: 12px 16px; text-align: center;
  flex-shrink: 0; min-width: 60px;
}
.date-month { color: rgba(255,255,255,0.8); font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.date-day { color: white; font-size: 1.8rem; font-weight: 900; line-height: 1; margin-top: 2px; }

.activity-info { flex: 1; min-width: 0; }
.activity-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 8px; }
.activity-header h3 { font-size: 1.05rem; font-weight: 800; color: #0f172a; margin: 0; }
.status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }
.activity-desc { color: #64748b; font-size: 0.88rem; line-height: 1.6; margin: 0 0 12px; }
.activity-meta { display: flex; flex-wrap: wrap; gap: 16px; }
.meta-item { display: flex; align-items: center; gap: 5px; color: #64748b; font-size: 0.8rem; }
.meta-item svg { flex-shrink: 0; opacity: 0.6; }
.date-full { color: #94a3b8; }

/* Join CTA */
.join-section { padding: 60px 0; background: white; }
.join-box {
  background: linear-gradient(135deg, #7c3aed, #1d4ed8);
  border-radius: 20px; padding: 32px 40px;
  display: flex; align-items: center; gap: 24px;
}
.join-icon {
  width: 64px; height: 64px; border-radius: 16px;
  background: rgba(255,255,255,0.15);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.join-box h3 { font-size: 1.1rem; font-weight: 800; color: white; margin: 0 0 4px; }
.join-box p { color: rgba(255,255,255,0.75); font-size: 0.88rem; margin: 0; }
.join-box > div { flex: 1; }
.join-btn {
  background: white; color: #7c3aed; padding: 12px 28px;
  border-radius: 50px; font-weight: 700; font-size: 0.9rem;
  text-decoration: none; flex-shrink: 0; transition: all 0.2s;
}
.join-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.2); }

@media (max-width: 700px) {
  .page-hero h1 { font-size: 2rem; }
  .activity-card { flex-direction: column; gap: 16px; }
  .join-box { flex-direction: column; text-align: center; }
  .activity-header { flex-direction: column; }
}
</style>
