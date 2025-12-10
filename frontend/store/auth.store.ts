import { create } from "zustand"
import { persist, createJSONStorage } from "zustand/middleware"
import type { User } from "@/types"
import { authService } from "@/services/auth.service"

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  refreshUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await authService.login({ email, password })
          set({
            user: response.user || null,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        const refreshToken = authService.getRefreshToken()
        await authService.logout(refreshToken || undefined)
        set({
          user: null,
          isAuthenticated: false,
        })
      },

      checkAuth: async () => {
        const token = authService.getToken()
        const storedUser = authService.getStoredUser()
        
        if (token && storedUser) {
          set({
            user: storedUser,
            isAuthenticated: true,
          })
          // Tenta atualizar dados do usuário
          try {
            const currentUser = await authService.getCurrentUser()
            if (currentUser) {
              set({ user: currentUser })
            }
          } catch (error) {
            // Se falhar, mantém usuário do storage
            console.error("Erro ao buscar usuário atual:", error)
          }
        } else {
          set({
            user: null,
            isAuthenticated: false,
          })
        }
      },

      refreshUser: async () => {
        try {
          const currentUser = await authService.getCurrentUser()
          if (currentUser) {
            set({ user: currentUser })
          }
        } catch (error) {
          console.error("Erro ao atualizar dados do usuário:", error)
        }
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => {
        if (typeof window !== "undefined") {
          return localStorage
        }
        // Return a no-op storage for SSR
        return {
          getItem: () => null,
          setItem: () => {},
          removeItem: () => {},
        }
      }),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
