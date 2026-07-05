import { createRouter, createWebHistory } from 'vue-router'

const routes = [

  // Auth (guest only)
  { path: '/login',   component: () => import('../views/LoginView.vue'),    meta: { guest: true } },
  { path: '/register',component: () => import('../views/RegisterView.vue'), meta: { guest: true } },
  { path: '/forgot-password', component: () => import('../views/ForgotPasswordView.vue'), meta: { guest: true } },
  { path: '/verify-code',     component: () => import('../views/VerifyCodeView.vue'),     meta: { guest: true } },
  { path: '/reset-password',  component: () => import('../views/ResetPasswordView.vue'),  meta: { guest: true } },

  // Directeur
  {
    path: '/directeur',
    component: () => import('../layouts/DirecteurLayout.vue'),
    meta: { role: 'directeur' },
    children: [
      { path: '',         redirect: '/directeur/dashboard' },
      { path: 'dashboard',component: () => import('../views/directeur/DashboardView.vue') },
      { path: 'reports',  component: () => import('../views/directeur/ReportsView.vue') },
      { path: 'counselors',component: () => import('../views/directeur/CounselorsView.vue') },
      { path: 'students', component: () => import('../views/directeur/StudentsView.vue') },
      { path: 'appointments',    component: () => import('../views/directeur/AppointmentsView.vue') },
      { path: 'session-reports', component: () => import('../views/directeur/SessionReportsView.vue') },
      { path: 'settings',        component: () => import('../views/directeur/SettingsView.vue') },
    ],
  },

  // Conseiller
  {
    path: '/conseiller',
    component: () => import('../layouts/ConseillerLayout.vue'),
    meta: { role: 'conseiller' },
    children: [
      { path: '',         redirect: '/conseiller/dashboard' },
      { path: 'dashboard',component: () => import('../views/conseiller/DashboardView.vue') },
      { path: 'reports',  component: () => import('../views/conseiller/ReportsView.vue') },
      { path: 'session-reports', component: () => import('../views/conseiller/SessionReportsView.vue') },
      { path: 'profile',  component: () => import('../views/conseiller/ProfileView.vue') },
    ],
  },

  // Etudiant — force change password (standalone, no layout)
  { path: '/etudiant/change-password', component: () => import('../views/etudiant/ChangePasswordView.vue'), meta: { role: 'etudiant' } },

  // Etudiant
  {
    path: '/etudiant',
    component: () => import('../layouts/EtudiantLayout.vue'),
    meta: { role: 'etudiant' },
    children: [
      { path: '',              redirect: '/etudiant/dashboard' },
      { path: 'dashboard',     component: () => import('../views/etudiant/DashboardView.vue') },
      { path: 'new-report',    component: () => import('../views/etudiant/NewReportView.vue') },
      { path: 'profile',       component: () => import('../views/etudiant/ProfileView.vue') },
      { path: 'notifications', component: () => import('../views/etudiant/NotificationsView.vue') },
    ],
  },

  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  // Pages guest (login, register…) : redirige si déjà connecté
  if (to.meta.guest) {
    if (user) return redirectByRole(user.role)
    return true
  }

  // Pages protégées : doit être connecté
  if (!user) return '/login'

  if (to.meta.role && to.meta.role !== user.role) {
    return redirectByRole(user.role)
  }

  return true
})

function redirectByRole(role) {
  if (role === 'directeur')  return '/directeur/dashboard'
  if (role === 'conseiller') return '/conseiller/dashboard'
  return '/etudiant/dashboard'
}

export default router
