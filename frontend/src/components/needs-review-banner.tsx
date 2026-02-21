import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiRequest } from '../api/client';

export function NeedsReviewBanner() {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    async function fetchCount() {
      try {
        const data = await apiRequest<{
          items: unknown[];
          totalPages: number;
        }>('/reviews/validation-issues?resolved=false&page=1&pageSize=1');
        const hasIssues = data.items.length > 0 || (data.totalPages ?? 0) > 0;
        setCount(hasIssues ? 1 : 0);
      } catch {
        setCount(0);
      }
    }
    void fetchCount();
  }, []);

  if (count === null || count === 0) return null;

  return (
    <div className="needs-review-banner" role="alert">
      <span>
        Há inconsistências pendentes de revisão.
      </span>
      <Link to="/admin">Revisar no Admin</Link>
    </div>
  );
}
