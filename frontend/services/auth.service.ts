import api from "./api"
import type { LoginCredentials, AuthResponse, User } from "@/types"

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/login", credentials)
    
    if (response.data.access_token && typeof window !== "undefined") {
      localStorage.setItem("access_token", response.data.access_token)
      localStorage.setItem("refresh_token", response.data.refresh_token)
      if (response.data.user) {
        localStorage.setItem("user", JSON.stringify(response.data.user))
      }
    }
    
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await api.post<{ access_token: string; token_type: string }>(
      "/auth/refresh",
      { refresh_token: refreshToken }
    )
    
    if (response.data.access_token && typeof window !== "undefined") {
      localStorage.setItem("access_token", response.data.access_token)
    }
    
    return { access_token: response.data.access_token }
  },

  async logout(refreshToken?: string): Promise<void> {
    try {
      if (refreshToken) {
        await api.post("/auth/logout", { refresh_token: refreshToken })
      }
    } catch (error) {
      // Ignora erros no logout (pode estar offline)
      console.error("Erro ao fazer logout no servidor:", error)
    } finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token")
        localStorage.removeItem("user")
      }
    }
  },

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get<User>("/auth/me")
      if (response.data && typeof window !== "undefined") {
        localStorage.setItem("user", JSON.stringify(response.data))
      }
      return response.data
    } catch (error) {
      return null
    }
  },

  getStoredUser(): User | null {
    if (typeof window === "undefined") return null
    const userStr = localStorage.getItem("user")
    if (!userStr) return null
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  },

  getToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem("access_token")
  },

  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem("refresh_token")
  },

  isAuthenticated(): boolean {
    return !!this.getToken()
  },
}
