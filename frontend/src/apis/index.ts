import axios from 'axios'

interface ApiResponse {
  code: number
  msg: string
  data: any
}

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

api.interceptors.response.use(
  (res): any => {
    if (res.status === 204) return res
    const body = res.data as ApiResponse
    if (body.code !== 200 && body.code !== 201) {
      return Promise.reject(new Error(body.msg || '请求失败'))
    }
    return body
  },
  (err) => {
    return Promise.reject(err)
  },
)

export default api
