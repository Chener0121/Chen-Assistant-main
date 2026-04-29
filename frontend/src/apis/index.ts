import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => {
    if (res.data.code !== 200 && res.data.code !== 201) {
      return Promise.reject(new Error(res.data.msg || '请求失败'))
    }
    return res.data
  },
  (err) => {
    return Promise.reject(err)
  },
)

export default api
