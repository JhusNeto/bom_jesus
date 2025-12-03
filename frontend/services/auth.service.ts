import api from "./api"
import type { LoginCredentials, AuthResponse, User } from "@/types"

// Mock login for now - will be replaced with real API call
export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // TODO: Replace with real API call
    // For now, fake login that works with any credentials
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockToken = "mock-jwt-token-" + Date.now()
        const mockUser: User = {
          id: "1",
          email: credentials.email,
          name: credentials.email.split("@")[0],
        }

        // Store token and user
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", mockToken)
          localStorage.setItem("user", JSON.stringify(mockUser))
        }

        resolve({
          access_token: mockToken,
          token_type: "bearer",
          user: mockUser,
        })
      }, 500)
    })

    // Real implementation (commented for now):
    // const response = await api.post<AuthResponse>('/auth/login', credentials)
    // if (response.data.access_token && typeof window !== 'undefined') {
    //   localStorage.setItem('access_token', response.data.access_token)
    //   if (response.data.user) {
    //     localStorage.setItem('user', JSON.stringify(response.data.user))
    //   }
    // }
    // return response.data
  },

  async logout(): Promise<void> {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token")
      localStorage.removeItem("user")
    }
    // TODO: Call logout endpoint when available
    // await api.post('/auth/logout')
  },

  getCurrentUser(): User | null {
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

  isAuthenticated(): boolean {
    return !!this.getToken()
  },
}

