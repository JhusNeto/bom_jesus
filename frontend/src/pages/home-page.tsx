import { Link } from 'react-router-dom';
import { PageTitle } from '../components/page-title';

const actions = [
  { to: '/entry', label: 'Registrar entrada de lote' },
  { to: '/move', label: 'Mover lote' },
  { to: '/loss', label: 'Registrar perda' },
  { to: '/return', label: 'Registrar devolucao' },
  { to: '/dashboard', label: 'Ver dashboard' },
];

export function HomePage() {
  return (
    <>
      <PageTitle subtitle="Acoes rapidas para registrar em menos de 10 segundos">
        Operacao
      </PageTitle>
      <div className="quick-actions">
        {actions.map((action) => (
          <Link key={action.to} to={action.to} className="big-action">
            {action.label}
          </Link>
        ))}
      </div>
      <p className="muted">
        Offline-first ativo: registros sao salvos localmente e sincronizados depois.
      </p>
    </>
  );
}
