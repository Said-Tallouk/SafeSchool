<script setup>
import { ref } from 'vue'

const values = [
  {
    icon: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    title: 'الأمان أولاً',
    desc: 'كل طالب يستحق بيئة آمنة. نضع بروتوكولات صارمة لحماية كل بلاغ.',
    color: '#1d4ed8',
  },
  {
    icon: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    title: 'فريق محترف',
    desc: 'مستشارون تربويون وعلماء نفس مدرَّبون يتدخلون بسرعة لمرافقة كل حالة.',
    color: '#7c3aed',
  },
  {
    icon: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
    title: 'شفافية تامة',
    desc: 'يمكن للطلاب وأولياء الأمور متابعة تقدم كل ملف بشكل فوري.',
    color: '#059669',
  },
  {
    icon: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>`,
    title: 'سرية مضمونة',
    desc: 'جميع البيانات مشفرة ولا يمكن الوصول إليها إلا للموظفين المعتمدين في المؤسسة.',
    color: '#d97706',
  },
]

const team = [
  { name: 'د. أمينة بنعلي', role: 'مديرة تربوية', specialty: 'علم النفس المدرسي', initials: 'أب', color: '#1d4ed8' },
  { name: 'أ. كريم زيدان', role: 'مستشار رئيسي', specialty: 'الوساطة المدرسية', initials: 'كز', color: '#7c3aed' },
  { name: 'أ. فاطمة أوهبي', role: 'مسؤولة الرفاه', specialty: 'مرافقة الطلاب', initials: 'فأ', color: '#059669' },
  { name: 'أ. يوسف العلمي', role: 'منسق', specialty: 'علاقات الأسرة-المدرسة', initials: 'يع', color: '#d97706' },
]

const stats = [
  { number: '+500', label: 'طالب مُرافَق' },
  { number: '98%', label: 'نسبة الرضا' },
  { number: '24 ساعة', label: 'متوسط وقت الاستجابة' },
  { number: '5 سنوات', label: 'من الخبرة' },
]
</script>

<template>
  <!-- Hero -->
  <section class="about-hero">
    <div class="hero-blob blob1"></div>
    <div class="hero-blob blob2"></div>
    <div class="container">
      <div class="breadcrumb">
        <RouterLink to="/">الرئيسية</RouterLink>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        <span>من نحن</span>
      </div>
      <h1>حول <span class="gradient-text">SafeSchool</span></h1>
      <p class="hero-sub">منصة مصممة لحماية ومرافقة ودعم كل طالب في بيئة مدرسية آمنة.</p>
    </div>
  </section>

  <!-- Mission -->
  <section class="mission-section">
    <div class="container grid-2">
      <div class="mission-text">
        <span class="section-tag">مهمتنا</span>
        <h2>بناء مدارس أكثر أماناً، معاً</h2>
        <p>وُلد SafeSchool من ملاحظة بسيطة: كثير من المواقف الصعبة تبقى طي الكتمان لعدم وجود قناة آمنة وسرية. مهمتنا كسر هذا الصمت بتوفير منصة في متناول الجميع، مؤمَّنة ورحيمة.</p>
        <p>نؤمن بأن كل طالب له حق التعلم في بيئة يشعر فيها بالاحترام والإنصات والحماية. لهذا صممنا نظاماً يُيسِّر الإبلاغ مع ضمان السرية والمتابعة المهنية.</p>
        <div class="mission-badges">
          <span class="badge-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            الإبلاغ المجهول ممكن
          </span>
          <span class="badge-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            متابعة فورية
          </span>
          <span class="badge-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            فريق مدرَّب ومعتمد
          </span>
        </div>
      </div>
      <div class="mission-visual">
        <div class="visual-card main-card">
          <div class="visual-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <div class="visual-title">منصة مؤمَّنة</div>
          <div class="visual-sub">بيانات مشفرة ومحمية</div>
        </div>
        <div class="visual-card side-card top">
          <div class="side-icon" style="background:#ede9fe">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
          </div>
          <div>
            <div class="side-num">12</div>
            <div class="side-label">مستشار نشط</div>
          </div>
        </div>
        <div class="visual-card side-card bottom">
          <div class="side-icon" style="background:#dcfce7">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          </div>
          <div>
            <div class="side-num">98%</div>
            <div class="side-label">ملفات محلولة</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Stats -->
  <section class="stats-section">
    <div class="container">
      <div class="stats-grid">
        <div v-for="s in stats" :key="s.label" class="stat-item">
          <div class="stat-number">{{ s.number }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Values -->
  <section class="values-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">قيمنا</span>
        <h2>ما يوجهنا كل يوم</h2>
        <p>مبادئ أساسية تُوجِّه كل قرار وكل إجراء نتخذه.</p>
      </div>
      <div class="values-grid">
        <div v-for="v in values" :key="v.title" class="value-card">
          <div class="value-icon" :style="{ background: v.color + '18', color: v.color }" v-html="v.icon"></div>
          <h3>{{ v.title }}</h3>
          <p>{{ v.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Team -->
  <section class="team-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">فريقنا</span>
        <h2>محترفون في خدمتكم</h2>
        <p>فريق متعدد التخصصات مكرَّس لرفاه كل طالب.</p>
      </div>
      <div class="team-grid">
        <div v-for="m in team" :key="m.name" class="team-card">
          <div class="team-avatar" :style="{ background: m.color + '18', color: m.color }">{{ m.initials }}</div>
          <div class="team-info">
            <div class="team-name">{{ m.name }}</div>
            <div class="team-role">{{ m.role }}</div>
            <div class="team-specialty">{{ m.specialty }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="cta-section">
    <div class="container">
      <div class="cta-box">
        <h2>هل تحتاج إلى مساعدة؟</h2>
        <p>فريقنا متاح لمرافقتك. أرسل بلاغاً بكل ثقة.</p>
        <div class="cta-actions">
          <RouterLink to="/register" class="btn-primary">إنشاء حساب</RouterLink>
          <RouterLink to="/contact" class="btn-outline">اتصل بنا</RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
* { box-sizing: border-box; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }

/* Hero */
.about-hero {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1d4ed8 100%);
  padding: 120px 0 80px; text-align: center;
}
.hero-blob {
  position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15; pointer-events: none;
}
.blob1 { width: 400px; height: 400px; background: #60a5fa; top: -100px; left: -100px; }
.blob2 { width: 300px; height: 300px; background: #a78bfa; bottom: -80px; right: -80px; }
.breadcrumb {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  margin-bottom: 24px; color: rgba(255,255,255,0.6); font-size: 0.85rem;
}
.breadcrumb a { color: rgba(255,255,255,0.7); text-decoration: none; }
.breadcrumb a:hover { color: white; }
.about-hero h1 { font-size: 2.8rem; font-weight: 900; color: white; margin: 0 0 16px; }
.gradient-text { background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.1rem; color: rgba(255,255,255,0.75); max-width: 580px; margin: 0 auto; line-height: 1.7; }

/* Mission */
.mission-section { padding: 80px 0; background: white; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: center; }
.section-tag {
  display: inline-block; background: #eff6ff; color: #1d4ed8;
  padding: 4px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px;
}
.mission-text h2 { font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0 0 16px; line-height: 1.3; }
.mission-text p { color: #475569; line-height: 1.75; margin-bottom: 16px; }
.mission-badges { display: flex; flex-direction: column; gap: 10px; margin-top: 24px; }
.badge-item {
  display: flex; align-items: center; gap: 8px;
  color: #334155; font-size: 0.88rem; font-weight: 600;
}
.badge-item svg { color: #059669; flex-shrink: 0; }
.mission-visual { position: relative; height: 320px; }
.visual-card {
  position: absolute; background: white;
  border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  padding: 24px; border: 1px solid #e2e8f0;
}
.main-card {
  left: 50%; top: 50%; transform: translate(-50%, -50%);
  text-align: center; width: 200px;
}
.visual-icon { margin-bottom: 12px; display: flex; justify-content: center; }
.visual-title { font-weight: 800; color: #0f172a; font-size: 0.95rem; }
.visual-sub { color: #64748b; font-size: 0.78rem; margin-top: 4px; }
.side-card { display: flex; align-items: center; gap: 12px; width: 180px; }
.side-card.top { top: 20px; left: 0; }
.side-card.bottom { bottom: 20px; right: 0; }
.side-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.side-num { font-size: 1.4rem; font-weight: 900; color: #0f172a; }
.side-label { font-size: 0.75rem; color: #64748b; }

/* Stats */
.stats-section { background: linear-gradient(135deg, #1d4ed8, #1e3a5f); padding: 60px 0; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px; text-align: center; }
.stat-number { font-size: 2.5rem; font-weight: 900; color: white; }
.stat-label { color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 4px; }

/* Values */
.values-section { padding: 80px 0; background: #f8fafc; }
.section-header { text-align: center; margin-bottom: 48px; }
.section-header h2 { font-size: 2rem; font-weight: 800; color: #0f172a; margin: 12px 0 12px; }
.section-header p { color: #64748b; font-size: 1rem; }
.values-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.value-card { background: white; border-radius: 16px; padding: 28px 24px; border: 1px solid #e2e8f0; }
.value-card:hover { box-shadow: 0 8px 30px rgba(0,0,0,0.08); transform: translateY(-4px); transition: all 0.3s; }
.value-icon { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }
.value-card h3 { font-size: 1rem; font-weight: 700; color: #0f172a; margin: 0 0 10px; }
.value-card p { color: #64748b; font-size: 0.87rem; line-height: 1.65; margin: 0; }

/* Team */
.team-section { padding: 80px 0; background: white; }
.team-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.team-card { background: #f8fafc; border-radius: 16px; padding: 28px 20px; text-align: center; border: 1px solid #e2e8f0; transition: all 0.2s; }
.team-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08); transform: translateY(-3px); }
.team-avatar { width: 72px; height: 72px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 900; margin: 0 auto 16px; }
.team-name { font-weight: 800; color: #0f172a; font-size: 0.95rem; margin-bottom: 4px; }
.team-role { color: #1d4ed8; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px; }
.team-specialty { color: #64748b; font-size: 0.78rem; }

/* CTA */
.cta-section { padding: 80px 0; background: #f8fafc; }
.cta-box {
  background: linear-gradient(135deg, #0f172a, #1d4ed8);
  border-radius: 24px; padding: 60px 48px; text-align: center;
}
.cta-box h2 { font-size: 2rem; font-weight: 900; color: white; margin: 0 0 12px; }
.cta-box p { color: rgba(255,255,255,0.75); font-size: 1rem; margin-bottom: 32px; }
.cta-actions { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
.btn-primary {
  background: white; color: #1d4ed8; padding: 14px 32px;
  border-radius: 50px; font-weight: 700; font-size: 0.95rem; text-decoration: none;
  transition: all 0.2s;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.2); }
.btn-outline {
  border: 2px solid rgba(255,255,255,0.5); color: white; padding: 14px 32px;
  border-radius: 50px; font-weight: 700; font-size: 0.95rem; text-decoration: none;
  transition: all 0.2s;
}
.btn-outline:hover { border-color: white; background: rgba(255,255,255,0.1); }

@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
  .mission-visual { height: 200px; }
  .values-grid, .team-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 580px) {
  .about-hero h1 { font-size: 2rem; }
  .values-grid, .team-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
