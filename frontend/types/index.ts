// User types
export interface User {
  id: string
  email: string
  name?: string
}

// Auth types
export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user?: User
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
}

