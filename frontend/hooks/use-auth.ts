"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth.store"

export function useAuth(requireAuth: boolean = false) {
  const router = useRouter()
  const { user, isAuthenticated, isLoading, checkAuth, refreshUser } = useAuthStore()

  useEffect(() => {
    // Verifica autenticação ao montar
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    // Se requer autenticação e não está autenticado, redireciona
    if (requireAuth && !isLoading && !isAuthenticated) {
      router.push("/login")
    }
  }, [requireAuth, isLoading, isAuthenticated, router])

  return {
    user,
    isAuthenticated,
    isLoading,
    refreshUser,
  }
}

