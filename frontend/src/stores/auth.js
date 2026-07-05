import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user          = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token         = ref(localStorage.getItem('access') || null)
  const savedPassword = ref(localStorage.getItem('saved_pw') || '')

  const isLoggedIn    = computed(() => !!token.value)
  const isDirecteur   = computed(() => user.value?.role === 'directeur')
  const isConseiller  = computed(() => user.value?.role === 'conseiller')
  const isEtudiant    = computed(() => user.value?.role === 'etudiant')

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    token.value = data.access
    user.value  = data.user
    localStorage.setItem('access',  data.access)
    localStorage.setItem('refresh', data.refresh)
    localStorage.setItem('user',    JSON.stringify(data.user))
    if (data.user.role === 'etudiant') {
      savedPassword.value = password
      localStorage.setItem('saved_pw', password)
    }
    return data.user
  }

  async function register(payload) {
    const { data } = await api.post('/auth/register/', payload)
    return data
  }

  function logout() {
    token.value         = null
    user.value          = null
    savedPassword.value = ''
    localStorage.clear()
  }

  function updateUser(data) {
    user.value = { ...user.value, ...data }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function savePassword(pw) {
    savedPassword.value = pw
    localStorage.setItem('saved_pw', pw)
  }

  return { user, token, savedPassword, isLoggedIn, isDirecteur, isConseiller, isEtudiant, login, register, logout, updateUser, savePassword }
})
