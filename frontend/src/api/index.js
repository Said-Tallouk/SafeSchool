import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Attach token automatically
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh if 401
api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh')
      // Pas de refresh token = requête publique anonyme, on rejette silencieusement
      if (!refresh) return Promise.reject(err)
      try {
        const { data } = await axios.post('/api/auth/token/refresh/', { refresh }, { timeout: 8000 })
        localStorage.setItem('access', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        localStorage.clear()
        window.location.href = '/'
        return Promise.reject(err)
      }
    }
    return Promise.reject(err)
  }
)

export default api
