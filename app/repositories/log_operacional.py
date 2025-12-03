"""Repository para LogOperacional"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.log_operacional import LogOperacional, TipoLog
from app.repositories.base import BaseRepository

class LogOperacionalRepository(BaseRepository[LogOperacional]):
    def __init__(self, db: Session):
        super().__init__(LogOperacional, db)
    
    def get_by_tipo(self, tipo: TipoLog) -> List[LogOperacional]:
        return self.db.query(LogOperacional).filter(LogOperacional.tipo == tipo).all()
    
    def get_by_usuario(self, usuario_id: UUID) -> List[LogOperacional]:
        return self.db.query(LogOperacional).filter(LogOperacional.usuario_id == usuario_id).all()
