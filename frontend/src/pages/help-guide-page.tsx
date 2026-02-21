import { Link, useParams } from 'react-router-dom';
import { PageTitle } from '../components/page-title';

const guides: Record<
  string,
  { title: string; steps: string[] }
> = {
  pesagem: {
    title: 'Como registrar pesagem',
    steps: [
      'Selecione o produto na balança.',
      'Informe a localização (câmara ou área).',
      'Digite caixas ou kg (um dos dois obrigatório).',
      'Toque em Salvar entrada.',
      'Em modo offline, o registro fica na fila e sincroniza depois.',
    ],
  },
  devolucao: {
    title: 'Como registrar devolução com foto',
    steps: [
      'Selecione o cliente e a loja.',
      'Informe o produto devolvido.',
      'Selecione o motivo (ex.: madura demais).',
      'Digite caixas ou kg.',
      'Anexe uma foto do produto (recomendado; offline permite pendente).',
      'Toque em Salvar devolução.',
    ],
  },
  dashboard: {
    title: 'Como interpretar o dashboard',
    steps: [
      'Caixas vendidas hoje: saídas do dia.',
      'Estoque por maturação: verde, de vez, madura.',
      'Perdas: hoje e no mês.',
      'Devoluções 7d: por cliente.',
      'Série 7 dias: tendência vendas vs perdas vs devoluções.',
    ],
  },
};

export function HelpGuidePage() {
  const { slug } = useParams<{ slug: string }>();
  const guide = slug ? guides[slug] : null;

  if (!guide) {
    return (
      <>
        <PageTitle>Guia não encontrado</PageTitle>
        <Link to="/help">Voltar à Ajuda</Link>
      </>
    );
  }

  return (
    <>
      <PageTitle subtitle="Passo a passo">{guide.title}</PageTitle>
      <section className="panel">
        <ol className="help-steps">
          {guide.steps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </section>
      <Link to="/help" className="big-action">
        Voltar à Ajuda
      </Link>
    </>
  );
}
