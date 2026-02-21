import {
  createContext,
  useContext,
  useMemo,
  useState,
} from 'react';
import type { PropsWithChildren } from 'react';
import {
  AUTH_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  apiRequest,
} from '../api/client';
import type { AuthUser } from '../types';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const STORAGE_KEY = 'bom-jesus-auth-user';

const AuthContext = createContext<AuthContextValue | null>(null);

function getInitialUser(): AuthUser | null {
  if (typeof window === 'undefined') return null;
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved ? (JSON.parse(saved) as AuthUser) : null;
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(getInitialUser);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      async login(email: string, password: string) {
        const data = await apiRequest<{
          accessToken: string;
          refreshToken: string;
          user: AuthUser;
        }>('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data.user));
        localStorage.setItem(AUTH_TOKEN_KEY, data.accessToken);
        localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken);
        setUser(data.user);
      },
      async logout() {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        if (refreshToken) {
          try {
            await apiRequest('/auth/logout', {
              method: 'POST',
              body: JSON.stringify({ refreshToken }),
            });
          } catch {
            // Best effort logout request; local cleanup still happens.
          }
        }
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        setUser(null);
      },
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider');
  return context;
}
