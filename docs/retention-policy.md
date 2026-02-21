# Políticas de Retenção (MVP)

*Valores assumidos; ajustar com dono do negócio.*

| Dado | Retenção Mínima | Observação |
|------|-----------------|------------|
| RAW events | 2 anos | Auditoria e disputas; nunca deletar sem arquivar |
| Fotos (S3/bucket) | 1 ano | Versionamento; após 1 ano → arquivar (cold storage) |
| Logs técnicos | 30–90 dias | Rotação; definir exato conforme volume |
| AuditLog | 2 anos | Alinhar com RAW |
| Backups Postgres | 7 diários + 4 semanais | Rodar job diário; rotação via script |

## Implementação Futura

- **Job de purge**: cron que remove RAW com `occurredAt` &gt; 2 anos (após export/archive)
- **Lifecycle S3**: regra no bucket para mover objetos &gt; 1 ano para Glacier
- **Rotação de logs**: logrotate ou similar para aplicação
