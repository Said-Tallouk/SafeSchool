import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useReportsStore = defineStore('reports', () => {
  const reports = ref([])
  const stats   = ref({})
  const loading = ref(false)

  async function fetchReports() {
    loading.value = true
    try {
      const { data } = await api.get('/reports/')
      reports.value = data
    } finally { loading.value = false }
  }

  async function fetchStats() {
    const { data } = await api.get('/stats/')
    stats.value = data
  }

  async function createReport(payload) {
    let body, headers = {}
    if (payload.photo instanceof File) {
      body = new FormData()
      Object.entries(payload).forEach(([k, v]) => { if (v !== null && v !== undefined) body.append(k, v) })
      headers = { 'Content-Type': 'multipart/form-data' }
    } else {
      body = Object.fromEntries(Object.entries(payload).filter(([, v]) => v !== null && v !== undefined && v !== ''))
      delete body.photo
    }
    const { data } = await api.post('/reports/', body, { headers })
    reports.value.unshift(data)
    return data
  }

  async function assignCounselor(reportId, counselorId) {
    const { data } = await api.post(`/reports/${reportId}/assign/`, { counselor_id: counselorId })
    const i = reports.value.findIndex(r => r.id === reportId)
    if (i !== -1) reports.value[i] = data
    return data
  }

  async function addAppointment(reportId, payload) {
    const { data } = await api.post(`/reports/${reportId}/appointment/`, payload)
    const i = reports.value.findIndex(r => r.id === reportId)
    if (i !== -1) reports.value[i].appointment = data
    return data
  }

  async function submitSessionReport(reportId, payload) {
    const { data } = await api.post(`/reports/${reportId}/session-report/`, payload)
    const i = reports.value.findIndex(r => r.id === reportId)
    if (i !== -1) { reports.value[i].session_report = data; reports.value[i].status = 'تم الحل' }
    return data
  }

  async function deleteReport(reportId) {
    await api.delete(`/reports/${reportId}/`)
    reports.value = reports.value.filter(r => r.id !== reportId)
  }

  async function respondAppointment(reportId, action) {
    const { data } = await api.post(`/reports/${reportId}/appointment/respond/`, { action })
    const i = reports.value.findIndex(r => r.id === reportId)
    if (i !== -1 && reports.value[i].appointment) {
      reports.value[i].appointment.status = data.status
      if (action === 'reject') reports.value[i].status = 'قيد المعالجة'
    }
    return data
  }

  async function uploadSchedule(reportId, file) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(`/reports/${reportId}/schedule/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const i = reports.value.findIndex(r => r.id === reportId)
    if (i !== -1) reports.value[i].schedule = data
    return data
  }

  return { reports, stats, loading, fetchReports, fetchStats, createReport,
           assignCounselor, addAppointment, submitSessionReport, deleteReport,
           respondAppointment, uploadSchedule }
})
