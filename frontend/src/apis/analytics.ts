import api from './index'

export function fetchWeakPoints() {
  return api.get('/analytics/weak-points')
}
