import type { PropsWithChildren } from 'react';

interface PageTitleProps extends PropsWithChildren {
  subtitle?: string;
}

export function PageTitle({ children, subtitle }: PageTitleProps) {
  return (
    <section className="page-title">
      <h1>{children}</h1>
      {subtitle ? <p>{subtitle}</p> : null}
    </section>
  );
}
