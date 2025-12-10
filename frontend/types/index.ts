// User types
export interface User {
  id: string
  email: string
  name: string
  role?: string
  is_active?: string
  created_at?: string
  updated_at?: string
}

// Auth types
export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
}

// Export audit types
export * from "./audit"

