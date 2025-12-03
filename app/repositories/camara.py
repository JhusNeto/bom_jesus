"""Repository para Camara"""
from typing import List
from sqlalchemy.orm import Session
from app.models.camara import Camara, StatusCamara
from app.repositories.base import BaseRepository

class CamaraRepository(BaseRepository[Camara]):
    def __init__(self, db: Session):
        super().__init__(Camara, db)
    
    def get_by_status(self, status: StatusCamara) -> List[Camara]:
        return self.db.query(Camara).filter(Camara.status == status).all()
    
    def get_disponiveis(self) -> List[Camara]:
        return self.get_by_status(StatusCamara.DISPONIVEL)
