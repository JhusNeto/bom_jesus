#!/usr/bin/env python3
"""
Script para criar usuários de teste com diferentes roles
Uso: python scripts/create-test-users.py
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_test_users():
    """Cria usuários de teste com diferentes roles"""
    db: Session = SessionLocal()
    
    users_to_create = [
        {
            "name": "Administrador",
            "email": "admin@bomjesus.com",
            "password": "admin123",
            "role": UserRole.ADMIN,
        },
        {
            "name": "Gerente Teste",
            "email": "gerente@bomjesus.com",
            "password": "gerente123",
            "role": UserRole.MANAGER,
        },
        {
            "name": "Operador Teste",
            "email": "operador@bomjesus.com",
            "password": "operador123",
            "role": UserRole.OPERATOR,
        },
        {
            "name": "Visualizador Teste",
            "email": "viewer@bomjesus.com",
            "password": "viewer123",
            "role": UserRole.VIEWER,
        },
    ]
    
    created = []
    skipped = []
    
    try:
        for user_data in users_to_create:
            # Verifica se usuário já existe
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"⏭️  Usuário {user_data['email']} já existe (Role: {existing_user.role.value})")
                skipped.append(user_data)
                continue
            
            # Cria novo usuário
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active="Y"
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            created.append({
                **user_data,
                "id": str(user.id)
            })
            
            print(f"✅ Usuário criado: {user_data['email']} (Role: {user_data['role'].value})")
        
        print("\n" + "="*60)
        print("📋 RESUMO DE USUÁRIOS DE TESTE")
        print("="*60)
        
        if created:
            print("\n✅ Usuários Criados:")
            for user in created:
                print(f"   • {user['email']} / {user['password']} (Role: {user['role'].value})")
        
        if skipped:
            print("\n⏭️  Usuários Já Existentes:")
            for user in skipped:
                print(f"   • {user['email']} (Role: {user['role'].value})")
        
        print("\n" + "="*60)
        print("🧪 CREDENCIAIS PARA TESTES")
        print("="*60)
        print("\n1. ADMIN:")
        print("   Email: admin@bomjesus.com")
        print("   Senha: admin123")
        print("   Permissões: Todas")
        
        print("\n2. MANAGER:")
        print("   Email: gerente@bomjesus.com")
        print("   Senha: gerente123")
        print("   Permissões: Gerenciais (sem gerenciar usuários)")
        
        print("\n3. OPERATOR:")
        print("   Email: operador@bomjesus.com")
        print("   Senha: operador123")
        print("   Permissões: Operacionais (criar/editar, sem deletar)")
        
        print("\n4. VIEWER:")
        print("   Email: viewer@bomjesus.com")
        print("   Senha: viewer123")
        print("   Permissões: Somente leitura")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar usuários: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()

