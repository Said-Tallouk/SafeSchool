import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useCounselorsStore = defineStore('counselors', () => {
  const counselors = ref([])

  async function fetch() {
    const { data } = await api.get('/counselors/')
    counselors.value = data
  }

  async function create(payload) {
    const { data } = await api.post('/counselors/', payload)
    counselors.value.push(data)
    return data
  }

  async function remove(id) {
    await api.delete(`/counselors/${id}/`)
    counselors.value = counselors.value.filter(c => c.id !== id)
  }

  return { counselors, fetch, create, remove }
})
