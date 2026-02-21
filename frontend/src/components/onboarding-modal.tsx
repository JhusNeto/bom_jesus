import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const STORAGE_KEY = 'bom-jesus-onboarding-seen';

export function OnboardingModal() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const seen = localStorage.getItem(STORAGE_KEY);
    if (!seen) {
      setVisible(true);
    }
  }, []);

  function dismiss() {
    localStorage.setItem(STORAGE_KEY, '1');
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
      <div className="onboarding-modal">
        <h2 id="onboarding-title">Bem-vindo ao Bom Jesus Operação</h2>
        <p>
          App para registrar pesagens, movimentações, perdas e devoluções em tempo real.
        </p>
        <ul>
          <li><strong>Entrada</strong> — pesagem e localização</li>
          <li><strong>Mover</strong> — transferências entre câmaras</li>
          <li><strong>Perda</strong> — registro de perdas</li>
          <li><strong>Devolução</strong> — com foto quando possível</li>
        </ul>
        <p className="muted">
          Funciona offline: os dados são salvos localmente e sincronizados quando houver conexão.
        </p>
        <div className="onboarding-actions">
          <Link to="/help" className="big-action" onClick={dismiss}>
            Ver ajuda e guias
          </Link>
          <button type="button" onClick={dismiss}>
            Entendi, começar
          </button>
        </div>
      </div>
    </div>
  );
}
