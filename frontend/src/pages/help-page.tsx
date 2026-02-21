import { Link } from 'react-router-dom';
import { PageTitle } from '../components/page-title';

const guides = [
  {
    to: '/help/pesagem',
    title: 'Como registrar pesagem',
    subtitle: 'Entrada de lote na balança',
  },
  {
    to: '/help/devolucao',
    title: 'Como registrar devoluções com foto',
    subtitle: 'Devolução com evidência fotográfica',
  },
  {
    to: '/help/dashboard',
    title: 'Como interpretar o dashboard',
    subtitle: 'Indicadores e tendências',
  },
];

export function HelpPage() {
  return (
    <>
      <PageTitle subtitle="Instruções rápidas por fluxo">Ajuda & Onboarding</PageTitle>
      <section className="panel">
        <h3>Guias passo a passo</h3>
        <ul className="help-guides">
          {guides.map((g) => (
            <li key={g.to}>
              <Link to={g.to} className="help-guide-link">
                <strong>{g.title}</strong>
                <span className="muted">{g.subtitle}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <h3>Checklist diário</h3>
        <p className="muted">
          Conferir se registrou tudo, consultou o dashboard e revisou pendências.
        </p>
        <Link to="/checklist" className="big-action">
          Abrir checklist diário
        </Link>
      </section>
    </>
  );
}
