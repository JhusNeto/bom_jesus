#!/usr/bin/env python3
"""
Script para criar usuário de teste no banco de dados
Uso: python scripts/create-test-user.py
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_test_user():
    """Cria usuário de teste"""
    db: Session = SessionLocal()
    
    try:
        # Verifica se usuário já existe
        existing_user = db.query(User).filter(User.email == "admin@bomjesus.com").first()
        if existing_user:
            print("❌ Usuário admin@bomjesus.com já existe!")
            print(f"   ID: {existing_user.id}")
            print(f"   Role: {existing_user.role.value}")
            return
        
        # Cria novo usuário
        user = User(
            name="Administrador",
            email="admin@bomjesus.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active="Y"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ Usuário de teste criado com sucesso!")
        print(f"   Email: {user.email}")
        print(f"   Senha: admin123")
        print(f"   Role: {user.role.value}")
        print(f"   ID: {user.id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar usuário: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()

