import { Navigate } from 'react-router-dom';
import type { PropsWithChildren } from 'react';
import { useAuth } from '../state/auth-context';

export function PrivateRoute({ children }: PropsWithChildren) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
