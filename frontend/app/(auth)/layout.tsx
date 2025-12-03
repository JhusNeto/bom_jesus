"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth.store"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { LogOut, Menu, Home } from "lucide-react"

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { isAuthenticated, user, logout, checkAuth } = useAuthStore()

  useEffect(() => {
    // Verifica autenticação tanto no store quanto no localStorage
    checkAuth()
    
    // Verifica diretamente no localStorage também
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
    
    if (!token && !isAuthenticated) {
      // Usa window.location para forçar navegação completa
      window.location.href = "/login"
    }
  }, [isAuthenticated, checkAuth])

  const handleLogout = async () => {
    await logout()
    router.push("/login")
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              <Home className="h-5 w-5" />
              <span className="font-bold text-lg">Bom Jesus</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <span className="text-sm text-muted-foreground">
                {user.email}
              </span>
            )}
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}

