<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const annonces    = ref([])
const loading     = ref(true)
const activeTab   = ref('all')

const TABS = [
  { key: 'all',       label: 'الكل' },
  { key: 'info',      label: 'معلومات' },
  { key: 'evenement', label: 'فعاليات' },
  { key: 'urgence',   label: 'عاجل' },
  { key: 'alerte',    label: 'تنبيهات' },
]

const CAT_COLORS = { info:'#3b82f6', urgence:'#ef4444', evenement:'#7c3aed', alerte:'#f59e0b' }
const CAT_BG     = { info:'#dbeafe', urgence:'#fee2e2', evenement:'#ede9fe', alerte:'#fef3c7' }
const CAT_ICONS  = { urgence:'🚨', evenement:'📅', alerte:'⚠️', info:'📢' }

const filtered = computed(() => {
  if (activeTab.value === 'all') return annonces.value
  return annonces.value.filter(a => a.categorie === activeTab.value)
})

const expanded = ref(new Set())
function toggleExpand(id) {
  const s = new Set(expanded.value)
  s.has(id) ? s.delete(id) : s.add(id)
  expanded.value = s
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ar-MA', { day: 'numeric', month: 'long', year: 'numeric' })
}
function getDay(d)   { return d ? new Date(d).getDate() : '' }
function getMonth(d) { return d ? new Date(d).toLocaleDateString('ar-MA', { month: 'short' }).toUpperCase() : '' }

onMounted(async () => {
  try {
    const { data } = await api.get('/annonces/')
    annonces.value = data.filter(a => a.publie)
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
        <span>الفعاليات</span>
      </div>
      <h1>الفعاليات & <span class="highlight">الإعلانات</span></h1>
      <p>ابقَ على اطلاع بجميع أخبار وفعاليات المؤسسة.</p>
    </div>
  </section>

  <!-- Content -->
  <section class="content-section">
    <div class="container">

      <!-- Tabs -->
      <div class="tabs">
        <button
          v-for="t in TABS" :key="t.key"
          class="tab-btn"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          {{ t.label }}
          <span class="tab-count">
            {{ t.key === 'all' ? annonces.length : annonces.filter(a => a.categorie === t.key).length }}
          </span>
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="empty-state">
        <div class="spinner"></div>
        <p>جارٍ التحميل…</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filtered.length === 0" class="empty-state">
        <svg width="56" height="56" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <p>لا توجد إعلانات في هذه الفئة.</p>
      </div>

      <!-- Grid -->
      <div v-else class="annonces-grid">
        <article v-for="a in filtered" :key="a.id" class="annonce-card">

          <!-- Image zone -->
          <div class="card-visual" :style="!a.photo_url ? { background: CAT_COLORS[a.categorie] || '#7c3aed' } : {}">
            <img v-if="a.photo_url" :src="a.photo_url" :alt="a.titre" class="card-img" />
            <div v-else class="card-no-img">
              <span class="card-no-img-icon">{{ CAT_ICONS[a.categorie] || '📢' }}</span>
            </div>
            <!-- Gradient overlay -->
            <div class="card-overlay"></div>
            <!-- Category badge on image -->
            <span class="card-cat-badge" :style="{ background: CAT_COLORS[a.categorie] || '#7c3aed' }">
              {{ CAT_ICONS[a.categorie] }} {{ a.categorie }}
            </span>
          </div>

          <!-- Content -->
          <div class="card-content">
            <!-- Date row -->
            <div class="card-date-row">
              <div class="card-date-block">
                <span class="date-day">{{ getDay(a.created_at || a.date) }}</span>
                <span class="date-month">{{ getMonth(a.created_at || a.date) }}</span>
              </div>
              <span class="card-date-full">{{ formatDate(a.created_at || a.date) }}</span>
            </div>

            <h2 class="card-title">{{ a.titre }}</h2>
            <p class="card-excerpt" :class="{ expanded: expanded.has(a.id) }">{{ a.contenu }}</p>
            <button class="read-more-btn" @click="toggleExpand(a.id)">
              {{ expanded.has(a.id) ? '▲ عرض أقل' : '▼ عرض المزيد' }}
            </button>

            <!-- Footer line -->
            <div class="card-footer">
              <span class="card-tag" :style="{ color: CAT_COLORS[a.categorie] || '#7c3aed', borderColor: CAT_BG[a.categorie] || '#ede9fe', background: CAT_BG[a.categorie] || '#ede9fe' }">
                {{ CAT_ICONS[a.categorie] }} {{ a.categorie }}
              </span>
            </div>
          </div>

          <!-- Accent bar bottom -->
          <div class="card-accent" :style="{ background: CAT_COLORS[a.categorie] || '#7c3aed' }"></div>
        </article>
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
.breadcrumb { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 20px; color: rgba(255,255,255,0.6); font-size: 0.85rem; }
.breadcrumb a { color: rgba(255,255,255,0.7); text-decoration: none; }
.breadcrumb a:hover { color: white; }
.page-hero h1 { font-size: 2.6rem; font-weight: 900; color: white; margin: 0 0 14px; }
.highlight { color: #a78bfa; }
.page-hero p { color: rgba(255,255,255,0.75); font-size: 1rem; max-width: 500px; margin: 0 auto; }

/* Content */
.content-section { padding: 52px 0 80px; background: #f1f5f9; }

/* Tabs */
.tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 40px; }
.tab-btn {
  display: flex; align-items: center; gap: 7px;
  padding: 9px 20px; border-radius: 50px;
  border: 1.5px solid #e2e8f0; background: white;
  color: #64748b; font-size: 0.85rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.tab-btn:hover { border-color: #7c3aed; color: #7c3aed; }
.tab-btn.active { background: #7c3aed; border-color: #7c3aed; color: white; }
.tab-count {
  background: #e2e8f0; color: #475569;
  font-size: 0.7rem; font-weight: 800; padding: 1px 7px; border-radius: 20px;
}
.tab-btn.active .tab-count { background: rgba(255,255,255,0.25); color: white; }

/* States */
.empty-state { text-align: center; padding: 80px 0; color: #94a3b8; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.empty-state p { font-size: 0.95rem; color: #64748b; }
.spinner { width: 36px; height: 36px; border: 3px solid #e2e8f0; border-top-color: #7c3aed; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Grid */
.annonces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 28px;
}

/* Card */
.annonce-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.25s, box-shadow 0.25s;
}
.annonce-card:hover { transform: translateY(-5px); box-shadow: 0 20px 50px rgba(0,0,0,0.12); }

/* Visual zone (image or color) */
.card-visual {
  position: relative;
  height: 220px;
  overflow: hidden;
  flex-shrink: 0;
}
.card-img {
  width: 100%; height: 100%;
  object-fit: cover; object-position: center top;
  display: block;
  transition: transform 0.4s;
}
.annonce-card:hover .card-img { transform: scale(1.05); }

.card-no-img {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
}
.card-no-img-icon { font-size: 4rem; opacity: 0.5; }

/* Gradient over image */
.card-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, transparent 40%, rgba(0,0,0,0.55) 100%);
}

/* Category badge on image */
.card-cat-badge {
  position: absolute; top: 16px; left: 16px;
  color: white; font-size: 0.72rem; font-weight: 800;
  padding: 5px 14px; border-radius: 50px;
  text-transform: capitalize; letter-spacing: 0.03em;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Content */
.card-content { padding: 22px 24px 16px; flex: 1; display: flex; flex-direction: column; gap: 10px; }

/* Date row */
.card-date-row { display: flex; align-items: center; gap: 12px; }
.card-date-block {
  display: flex; flex-direction: column; align-items: center;
  background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 10px; padding: 6px 10px; flex-shrink: 0;
}
.date-day { font-size: 1.3rem; font-weight: 900; color: #1e293b; line-height: 1; }
.date-month { font-size: 0.6rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }
.card-date-full { font-size: 0.78rem; color: #94a3b8; font-weight: 600; }

/* Title */
.card-title {
  font-size: 1.1rem; font-weight: 900; color: #0f172a;
  margin: 0; line-height: 1.35;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* Excerpt */
.card-excerpt {
  font-size: 0.85rem; color: #64748b; line-height: 1.7; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  white-space: pre-wrap;
}
.card-excerpt.expanded {
  display: block; -webkit-line-clamp: unset; overflow: visible;
}
.read-more-btn {
  align-self: flex-start;
  background: none; border: none; padding: 4px 0; margin-top: 2px;
  font-size: 0.78rem; font-weight: 700; color: #7c3aed;
  cursor: pointer; letter-spacing: 0.01em;
  transition: opacity 0.15s;
}
.read-more-btn:hover { opacity: 0.7; }

/* Footer */
.card-footer { margin-top: auto; padding-top: 12px; border-top: 1px solid #f1f5f9; }
.card-tag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.72rem; font-weight: 800;
  padding: 4px 12px; border-radius: 20px;
  border: 1px solid transparent; text-transform: capitalize;
}

/* Bottom accent bar */
.card-accent { height: 4px; flex-shrink: 0; }

@media (max-width: 700px) {
  .page-hero h1 { font-size: 1.8rem; }
  .annonces-grid { grid-template-columns: 1fr; }
}
</style>
