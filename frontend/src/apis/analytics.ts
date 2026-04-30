import api from './index'

export function fetchWeakPoints() {
  return api.get('/analytics/weak-points')
}

export function fetchDailyStats(mode: string = 'daily') {
  return api.get('/analytics/daily-stats', { params: { mode } })
}

export function fetchDashboardStats() {
  return api.get('/analytics/dashboard-stats')
}
