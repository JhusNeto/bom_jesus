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
  checkAuth: () => void
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
          // Atualiza o estado imediatamente
          set({
            user: response.user || null,
            isAuthenticated: true,
            isLoading: false,
          })
          // Aguarda um tick para garantir que o estado foi persistido
          await new Promise((resolve) => setTimeout(resolve, 50))
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        await authService.logout()
        set({
          user: null,
          isAuthenticated: false,
        })
      },

      checkAuth: () => {
        const user = authService.getCurrentUser()
        const isAuthenticated = authService.isAuthenticated()
        set({
          user,
          isAuthenticated,
        })
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => (typeof window !== "undefined" ? localStorage : undefined)),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

