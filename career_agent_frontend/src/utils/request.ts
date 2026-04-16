// src/utils/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 60000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data, config } = error.response
      const isLoginRequest = config.url?.includes('/login')  // 判断是否为登录接口

      switch (status) {
        case 401:
          if (isLoginRequest) {
            // 登录失败：提取后端返回的错误信息，交给调用方处理
            const errorMsg = data?.detail || data?.message || '用户名或密码错误'
            return Promise.reject(new Error(errorMsg))
          } else {
            // 非登录接口的 401：未授权或 token 过期
            ElMessage.error('登录已过期，请重新登录')
            localStorage.removeItem('token')
            window.location.href = '/login'
            return Promise.reject(error)
          }

        case 403:
          ElMessage.error('没有权限访问该资源')
          break

        case 404:
          ElMessage.error(data?.detail || '请求的资源不存在')
          break

        case 422:
          // 参数校验错误（常见于 FastAPI 等后端）
          const msg = data?.detail?.[0]?.msg || '参数校验失败'
          ElMessage.error(msg)
          break

        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break

        default:
          ElMessage.error(data?.detail || data?.message || '请求失败')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error(error.message || '未知错误')
    }
    return Promise.reject(error)
  }
)

export default request