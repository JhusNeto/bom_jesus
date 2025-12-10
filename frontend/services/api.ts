import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
})

// Flag para evitar loops de refresh
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
}> = []

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token")
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Se for 401 e não for login/refresh, tenta refresh
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      // Evita loop de refresh
      if (isRefreshing) {
        // Adiciona à fila
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            if (originalRequest.headers && token) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            return api(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null

      if (!refreshToken) {
        // Não tem refresh token, faz logout
        processQueue(error, null)
        isRefreshing = false
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
          localStorage.removeItem("user")
          window.location.href = "/login"
        }
        return Promise.reject(error)
      }

      try {
        // Tenta refresh
        const { authService } = await import("./auth.service")
        const response = await authService.refreshToken(refreshToken)
        const newToken = response.access_token

        // Atualiza token no header
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }

        // Processa fila com sucesso
        processQueue(null, newToken)
        isRefreshing = false

        // Retenta requisição original
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh falhou, faz logout
        processQueue(refreshError as AxiosError, null)
        isRefreshing = false
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
          localStorage.removeItem("user")
          window.location.href = "/login"
        }
        return Promise.reject(refreshError)
      }
    }

    // Outros erros
    return Promise.reject(error)
  }
)

export default api
