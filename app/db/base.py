"""
Base para models do SQLAlchemy
Todos os models devem herdar de Base
"""
from sqlalchemy.orm import declarative_base

# Base para todos os models
Base = declarative_base()

__all__ = ["Base"]

