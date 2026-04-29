import api from './index'

export function fetchGraph() {
  return api.get('/graph')
}
