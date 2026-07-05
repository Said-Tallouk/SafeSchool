<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useRouter } from 'vue-router'
import api from '../../api'

const auth   = useAuthStore()
const router = useRouter()
const annonces      = ref([])
const activites     = ref([])
const sc            = ref({})
const actPhotos     = ref([])
const lightboxPhoto = ref(null)

const g = (key, fallback = '') => sc.value[key] || fallback

onMounted(async () => {
  try {
    const [a, b, c, d, e] = await Promise.all([
      api.get('/annonces/'),
      api.get('/activites/'),
      api.get('/site-content/'),
      api.get('/photos/?category=activites'),
      api.get('/photos/?category=accueil'),
    ])
    annonces.value  = a.data.filter(x => x.publie).slice(0, 3)
    activites.value = b.data.filter(x => x.statut !== 'annulee').slice(0, 3)
    c.data.forEach(item => { sc.value[item.key] = item.value })
    actPhotos.value = d.data
    bgImages.value  = e.data.map(p => p.image_url)
    if (bgImages.value.length > 1) {
      slideshowTimer = setInterval(() => {
        currentBg.value = (currentBg.value + 1) % bgImages.value.length
      }, 5000)
    }
  } catch { /* silent */ }
})

function goReport() {
  if (auth.isLoggedIn) router.push('/etudiant/new-report')
  else router.push('/login')
}

const bgImages  = ref([])
const currentBg = ref(0)
let slideshowTimer = null

onUnmounted(() => clearInterval(slideshowTimer))

const CAT_COLORS = {
  info: '#3b82f6', urgence: '#ef4444', evenement: '#8b5cf6', alerte: '#f59e0b'
}
const CAT_LABELS = { info: 'معلومة', urgence: 'عاجل', evenement: 'فعالية', alerte: 'تنبيه' }
const STATUT_BG = { planifiee:'#eff6ff', en_cours:'#fffbeb', terminee:'#f0fdf4' }
const STATUT_C  = { planifiee:'#3b82f6', en_cours:'#f59e0b', terminee:'#22c55e' }
const STATUT_L  = { planifiee:'مجدولة', en_cours:'جارية', terminee:'منتهية' }


</script>

<template>
  <div class="home">

    <!-- ── Hero ── -->
    <section class="hero">

      <!-- Moitié gauche : texte -->
      <div class="hero-left">
        <div class="hero-blob blob-1"></div>
        <div class="hero-blob blob-2"></div>
        <div class="hero-content">
          <div class="hero-badge">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            {{ g('hero_subtitle', 'منصة الحماية المدرسية') }}
          </div>
          <h1>{{ g('hero_title', 'معاً ضد التحرش المدرسي') }}</h1>
          <p>{{ g('hero_desc', 'SafeSchool يتيح لك الإبلاغ عن التحرش بأمان وسرية تامة. كل بلاغ يُعالَج بعناية من قِبَل فريق مستشارينا.') }}</p>
          <div class="hero-actions">
            <button class="btn-hero-primary" @click="goReport">
              <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              {{ g('hero_btn', 'إرسال بلاغ') }}
            </button>
            <RouterLink to="/about" class="btn-hero-outline">
              اعرف المزيد
              <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
            </RouterLink>
          </div>
          <div class="hero-stats">
            <div class="hstat"><strong>100%</strong><span>سري</span></div>
            <div class="hstat-sep"></div>
            <div class="hstat"><strong>24 ساعة</strong><span>وقت الاستجابة</span></div>
            <div class="hstat-sep"></div>
            <div class="hstat"><strong>مؤمَّن</strong><span>بيانات محمية</span></div>
          </div>
        </div>
      </div>

      <!-- Moitié droite : image -->
      <div class="hero-right">
        <transition name="photo-fade" mode="out-in">
          <img v-if="bgImages.length > 0" :key="currentBg" :src="bgImages[currentBg]" alt="" class="hero-right-img" />
          <div v-else class="hero-right-placeholder">
            <svg width="48" height="48" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
          </div>
        </transition>
        <!-- Dots -->
        <div v-if="bgImages.length > 1" class="hero-right-dots">
          <button
            v-for="(_, i) in bgImages" :key="i"
            class="widget-dot"
            :class="{ active: i === currentBg }"
            @click="currentBg = i"
          ></button>
        </div>
      </div>

    </section>

    <!-- ── Valeurs ── -->
    <section class="values">
      <div class="section-inner">
        <div class="section-header">
          <div class="section-badge">التزاماتنا</div>
          <h2>لماذا تختار SafeSchool؟</h2>
          <p>منصة مصممة لأمان ورفاهية الطلاب</p>
        </div>
        <div class="values-grid">
          <div v-for="v in [
            { icon:'shield', title:'سرية تامة',       desc:'بياناتك وهويتك محمية. يمكنك الإبلاغ بشكل مجهول.', color:'#1d4ed8', bg:'#eff6ff' },
            { icon:'users',  title:'فريق متخصص',      desc:'مستشارون متخصصون يحللون كل بلاغ بجدية واهتمام.', color:'#7c3aed', bg:'#f5f3ff' },
            { icon:'clock',  title:'استجابة سريعة',   desc:'كل بلاغ يحظى برد خلال 24 ساعة عمل.', color:'#059669', bg:'#f0fdf4' },
            { icon:'heart',  title:'متابعة شخصية',    desc:'مرافقة فردية لكل حالة حتى الحل الكامل.', color:'#dc2626', bg:'#fef2f2' },
          ]" :key="v.title" class="value-card">
            <div class="val-icon" :style="`background:${v.bg};color:${v.color}`">
              <svg v-if="v.icon==='shield'" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <svg v-else-if="v.icon==='users'" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
              <svg v-else-if="v.icon==='clock'" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <svg v-else width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
            </div>
            <h3>{{ v.title }}</h3>
            <p>{{ v.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Annonces récentes ── -->
    <section v-if="annonces.length" class="announcements">
      <div class="section-inner">
        <div class="section-header">
          <div class="section-badge">معلومات</div>
          <h2>آخر الإعلانات</h2>
          <p>أحدث أخبار وإعلانات المؤسسة</p>
        </div>
        <div class="ann-grid">
          <div v-for="a in annonces" :key="a.id" class="ann-card">
            <div class="ann-cat" :style="`background:${(CAT_COLORS[a.categorie]||'#3b82f6')}15;color:${CAT_COLORS[a.categorie]||'#3b82f6'}`">
              {{ CAT_LABELS[a.categorie] || a.categorie }}
            </div>
            <h3>{{ a.titre }}</h3>
            <p>{{ a.contenu.slice(0, 150) }}{{ a.contenu.length > 150 ? '…' : '' }}</p>
          </div>
        </div>
      </div>
    </section>


    <!-- ── Galerie photos activités ── -->
    <section v-if="actPhotos.length > 0" class="gallery-section">
      <div class="section-inner">
        <div class="section-header">
          <div class="section-badge" style="background:#fff7ed;color:#ea580c">معرض الصور</div>
          <h2>أنشطتنا بالصور</h2>
          <p>اكتشف الحياة المدرسية من خلال أنشطتنا وفعالياتنا</p>
        </div>
        <div class="gallery-grid">
          <div v-for="(p, i) in actPhotos.slice(0,9)" :key="p.id"
            class="gallery-item"
            :class="i === 0 ? 'large' : ''"
            @click="lightboxPhoto = p">
            <img :src="p.image_url" :alt="p.title" />
            <div class="gallery-overlay">
              <span class="gallery-title">{{ p.title }}</span>
            </div>
          </div>
        </div>
        <div v-if="actPhotos.length > 9" class="see-more-row">
          <RouterLink to="/activites" class="btn-see-more">← عرض جميع الأنشطة</RouterLink>
        </div>
      </div>
    </section>

    <!-- Lightbox -->
    <transition name="fade">
      <div v-if="lightboxPhoto" class="lightbox" @click="lightboxPhoto = null">
        <button class="lb-close" @click="lightboxPhoto = null">
          <svg width="22" height="22" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <div class="lb-content" @click.stop>
          <img :src="lightboxPhoto.image_url" :alt="lightboxPhoto.title" />
          <div v-if="lightboxPhoto.title" class="lb-caption">{{ lightboxPhoto.title }}</div>
        </div>
      </div>
    </transition>

    <!-- ── CTA ── -->
    <section class="cta">
      <div class="cta-inner">
        <div class="cta-icon">
          <svg width="28" height="28" fill="none" stroke="white" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h2>هل تعرضت للتحرش؟</h2>
        <p>{{ g('awareness_msg1', 'لست وحدك. التحدث هو التصرف. بلاغك سري وسيُعالَج بسرعة.') }}</p>
        <button class="btn-cta" @click="goReport">
          <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          {{ g('hero_btn', 'أرسل بلاغاً الآن') }}
        </button>
      </div>
    </section>

  </div>
</template>

<style scoped>
* { box-sizing: border-box; }
.home { display: flex; flex-direction: column; }

/* ── Hero ── */
.hero {
  display: flex; min-height: 85vh; overflow: hidden;
}

/* Moitié gauche */
.hero-left {
  flex: 0 0 45%; position: relative; overflow: hidden;
  background: linear-gradient(145deg, #1e3a8a 0%, #1d4ed8 60%, #0891b2 100%);
  display: flex; align-items: center;
  padding: 80px 48px 80px 60px;
}
.hero-blob { position: absolute; border-radius: 50%; opacity: 0.12; pointer-events: none; }
.blob-1 { width: 500px; height: 500px; background: white; top: -150px; right: -100px; }
.blob-2 { width: 350px; height: 350px; background: white; bottom: -120px; left: -80px; }
.hero-content { position: relative; z-index: 1; max-width: 540px; }

/* Moitié droite */
.hero-right {
  flex: 0 0 55%; position: relative; overflow: hidden; background: #0f172a;
}
.hero-right-img {
  width: 100%; height: 100%;
  object-fit: cover; object-position: center top; display: block;
}
.hero-right-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center; background: #1e293b;
}
.hero-right-dots {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 8px;
}
.widget-dot {
  width: 8px; height: 8px; border-radius: 50%;
  border: none; cursor: pointer; padding: 0;
  background: rgba(255,255,255,0.5); transition: all 0.3s;
}
.widget-dot.active { background: white; width: 24px; border-radius: 4px; }
.photo-fade-enter-active, .photo-fade-leave-active { transition: opacity 0.8s ease; }
.photo-fade-enter-from, .photo-fade-leave-to { opacity: 0; }

@media(max-width:900px){
  .hero { flex-direction: column; }
  .hero-left { padding: 60px 24px; }
  .hero-right { min-height: 300px; flex: none; width: 100%; }
}

.hero-badge { display: inline-flex; align-items: center; gap: 7px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); color: rgba(255,255,255,0.9); font-size: 0.78rem; font-weight: 700; padding: 6px 14px; border-radius: 20px; margin-bottom: 20px; }
.hero-content h1 { font-size: clamp(2rem, 5vw, 3rem); font-weight: 900; color: white; line-height: 1.15; margin: 0 0 20px; }
.hero-highlight { color: #fbbf24; }
.hero-content p { font-size: 1rem; color: rgba(255,255,255,0.8); line-height: 1.75; margin: 0 0 32px; max-width: 500px; }
.hero-actions { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 36px; }
.btn-hero-primary { display: flex; align-items: center; gap: 8px; background: white; color: #1d4ed8; font-weight: 900; font-size: 0.95rem; padding: 13px 24px; border-radius: 12px; border: none; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: all 0.2s; }
.btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.25); }
.btn-hero-outline { display: flex; align-items: center; gap: 7px; border: 2px solid rgba(255,255,255,0.5); color: white; font-weight: 700; font-size: 0.9rem; padding: 12px 22px; border-radius: 12px; text-decoration: none; transition: all 0.2s; }
.btn-hero-outline:hover { background: rgba(255,255,255,0.1); border-color: white; }
.hero-stats { display: flex; align-items: center; gap: 20px; }
.hstat { display: flex; flex-direction: column; }
.hstat strong { font-size: 1.1rem; font-weight: 900; color: white; }
.hstat span { font-size: 0.7rem; color: rgba(255,255,255,0.6); font-weight: 600; }
.hstat-sep { width: 1px; height: 30px; background: rgba(255,255,255,0.2); }

/* Hero card */
.hero-visual { display: flex; justify-content: center; }
.hero-card { background: rgba(255,255,255,0.1); border: 1.5px solid rgba(255,255,255,0.2); border-radius: 22px; padding: 28px; backdrop-filter: blur(10px); width: 100%; max-width: 340px; }
.hcard-icon { width: 56px; height: 56px; border-radius: 16px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }
.hcard-title { font-size: 1.1rem; font-weight: 900; color: white; margin-bottom: 4px; }
.hcard-sub { font-size: 0.78rem; color: rgba(255,255,255,0.65); margin-bottom: 20px; }
.hcard-steps { display: flex; flex-direction: column; gap: 10px; }
.hstep { display: flex; align-items: center; gap: 12px; }
.hstep-num { width: 28px; height: 28px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 900; color: white; flex-shrink: 0; }
.hstep span { font-size: 0.85rem; font-weight: 700; color: rgba(255,255,255,0.85); }

/* ── Sections ── */
.section-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.section-header { text-align: center; margin-bottom: 48px; }
.section-badge { display: inline-block; background: #eff6ff; color: #1d4ed8; font-size: 0.75rem; font-weight: 800; padding: 5px 14px; border-radius: 20px; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.06em; }
.section-header h2 { font-size: clamp(1.5rem, 3vw, 2rem); font-weight: 900; color: #1e293b; margin: 0 0 10px; }
.section-header p { font-size: 0.95rem; color: #64748b; margin: 0; }

/* Values */
.values { padding: 80px 0; background: #f8fafc; }
.values-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
.value-card { background: white; border-radius: 18px; padding: 28px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s; }
.value-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
.val-icon { width: 52px; height: 52px; border-radius: 15px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px; }
.value-card h3 { font-size: 0.95rem; font-weight: 900; color: #1e293b; margin: 0 0 10px; }
.value-card p { font-size: 0.83rem; color: #64748b; line-height: 1.65; margin: 0; }

/* Announcements */
.announcements { padding: 80px 0; }
.ann-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 18px; }
.ann-card { background: white; border-radius: 16px; padding: 22px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #f1f5f9; }
.ann-cat { display: inline-block; font-size: 0.7rem; font-weight: 800; padding: 4px 11px; border-radius: 20px; margin-bottom: 12px; text-transform: uppercase; }
.ann-card h3 { font-size: 0.92rem; font-weight: 800; color: #1e293b; margin: 0 0 9px; line-height: 1.35; }
.ann-card p { font-size: 0.82rem; color: #64748b; line-height: 1.6; margin: 0; }

/* Activities */
.activities { padding: 80px 0; background: #f8fafc; }
.act-grid { display: flex; flex-direction: column; gap: 14px; margin-bottom: 28px; }

.act-pub-card {
  background: white; border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}
.act-pub-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.09); transform: translateY(-2px); }

/* Photo */
.act-img-top {
  position: relative; width: 100%; height: 200px; overflow: hidden;
  background: #f1f5f9;
}
.act-img-top img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.4s; }
.act-pub-card:hover .act-img-top img { transform: scale(1.04); }
.act-img-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
}
.act-statut-over {
  position: absolute; top: 12px; right: 12px;
  font-size: 0.7rem; font-weight: 800;
  padding: 4px 11px; border-radius: 20px;
  backdrop-filter: blur(4px);
}

/* Card body */
.act-card-body { display: flex; align-items: center; gap: 16px; padding: 16px 20px; }

.act-date-block { display: flex; flex-direction: column; align-items: center; background: #eff6ff; color: #1d4ed8; border-radius: 12px; padding: 10px 14px; flex-shrink: 0; min-width: 56px; }
.act-day { font-size: 1.4rem; font-weight: 900; line-height: 1; }
.act-mon { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }

.act-info { flex: 1; min-width: 0; }
.act-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; flex-wrap: wrap; }
.act-info h3 { font-size: 0.92rem; font-weight: 800; color: #1e293b; margin: 0; }
.act-info p { font-size: 0.8rem; color: #64748b; margin: 0 0 8px; line-height: 1.5; }
.act-meta-row { display: flex; gap: 14px; flex-wrap: wrap; }
.act-meta-item { display: flex; align-items: center; gap: 5px; font-size: 0.74rem; color: #94a3b8; font-weight: 600; }
.act-statut { font-size: 0.7rem; font-weight: 800; padding: 4px 11px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; }
.see-more-row { text-align: center; }
.btn-see-more { display: inline-block; color: #1d4ed8; font-weight: 700; font-size: 0.88rem; text-decoration: none; padding: 10px 20px; border: 1.5px solid #1d4ed8; border-radius: 10px; transition: all 0.2s; }
.btn-see-more:hover { background: #1d4ed8; color: white; }

/* ── Gallery ── */
.gallery-section { padding: 80px 0; background: white; }

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 200px;
  gap: 10px;
  margin-bottom: 28px;
}
.gallery-item {
  position: relative; overflow: hidden; border-radius: 12px; cursor: pointer;
  background: #f1f5f9;
}
.gallery-item.large {
  grid-column: span 2;
  grid-row: span 2;
}
.gallery-item img {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.4s ease;
  display: block;
}
.gallery-item:hover img { transform: scale(1.07); }

.gallery-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 60%);
  display: flex; align-items: flex-end; padding: 12px 14px;
  opacity: 0; transition: opacity 0.25s;
}
.gallery-item:hover .gallery-overlay { opacity: 1; }
.gallery-title { color: white; font-size: 0.82rem; font-weight: 700; line-height: 1.3; }

/* Lightbox */
.lightbox {
  position: fixed; inset: 0; background: rgba(0,0,0,0.9);
  z-index: 9999; display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.lb-close {
  position: absolute; top: 20px; right: 20px;
  background: rgba(255,255,255,0.1); border: none; border-radius: 50%;
  width: 44px; height: 44px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.lb-close:hover { background: rgba(255,255,255,0.2); }
.lb-content { display: flex; flex-direction: column; align-items: center; gap: 12px; max-width: 90vw; max-height: 90vh; }
.lb-content img { max-width: 100%; max-height: 80vh; border-radius: 12px; object-fit: contain; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
.lb-caption { color: white; font-size: 0.9rem; font-weight: 600; text-align: center; }

@media (max-width: 768px) {
  .gallery-grid { grid-template-columns: repeat(2, 1fr); grid-auto-rows: 150px; }
  .gallery-item.large { grid-column: span 2; grid-row: span 1; }
}
@media (max-width: 480px) {
  .gallery-grid { grid-template-columns: 1fr 1fr; grid-auto-rows: 120px; }
  .gallery-item.large { grid-column: span 2; }
}

/* CTA */
.cta { background: linear-gradient(135deg,#1d4ed8,#0891b2); padding: 80px 24px; text-align: center; }
.cta-inner { max-width: 600px; margin: 0 auto; }
.cta-icon { width: 64px; height: 64px; border-radius: 20px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
.cta h2 { font-size: clamp(1.4rem, 3vw, 1.8rem); font-weight: 900; color: white; margin: 0 0 14px; }
.cta p { font-size: 0.95rem; color: rgba(255,255,255,0.8); line-height: 1.7; margin: 0 0 30px; }
.btn-cta { display: inline-flex; align-items: center; gap: 9px; background: white; color: #1d4ed8; font-weight: 900; font-size: 0.95rem; padding: 14px 28px; border-radius: 12px; border: none; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: all 0.2s; }
.btn-cta:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.25); }
</style>
