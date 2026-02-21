import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../state/auth-context';
import { NeedsReviewBanner } from './needs-review-banner';
import { OnboardingModal } from './onboarding-modal';

const navItems = [
  { to: '/', label: 'Home' },
  { to: '/entry', label: 'Entrada' },
  { to: '/move', label: 'Mover' },
  { to: '/loss', label: 'Perda' },
  { to: '/return', label: 'Devolucao' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/history', label: 'Historico' },
  { to: '/help', label: 'Ajuda' },
  { to: '/admin', label: 'Admin' },
];

export function AppLayout() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <OnboardingModal />
      <NeedsReviewBanner />
      <header className="topbar">
        <div>
          <strong>Bom Jesus Operacao</strong>
          <p>{user?.name}</p>
        </div>
        <div className="topbar-actions">
          <Link to="/help" className="topbar-link">Ajuda</Link>
          <button
          type="button"
          onClick={async () => {
            await logout();
            navigate('/login');
          }}
          >
            Sair
          </button>
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
      <nav className="bottom-nav">
        {navItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={
              pathname === item.to ||
              (item.to !== '/' && pathname.startsWith(item.to + '/'))
                ? 'active'
                : ''
            }
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}
