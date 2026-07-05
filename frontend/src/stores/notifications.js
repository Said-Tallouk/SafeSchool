import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotifStore = defineStore('notifications', () => {
  const toasts = ref([])
  let nextId = 1

  function push(type, message, duration = 4000) {
    const id = nextId++
    toasts.value.push({ id, type, message })
    setTimeout(() => remove(id), duration)
    return id
  }

  function remove(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  const success = (msg, dur) => push('success', msg, dur)
  const error   = (msg, dur) => push('error',   msg, dur)
  const info    = (msg, dur) => push('info',    msg, dur)
  const warning = (msg, dur) => push('warning', msg, dur)

  return { toasts, push, remove, success, error, info, warning }
})
