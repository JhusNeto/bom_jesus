"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth.store"

export default function HomePage() {
  const router = useRouter()
  const { isAuthenticated, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    // Aguarda verificar autenticação antes de redirecionar
    if (isAuthenticated === undefined) return // Ainda não verificou
    
    const timer = setTimeout(() => {
      if (isAuthenticated) {
        router.push("/dashboard")
      } else {
        router.push("/login")
      }
    }, 100)

    return () => clearTimeout(timer)
  }, [isAuthenticated, router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p>Carregando...</p>
    </div>
  )
}

