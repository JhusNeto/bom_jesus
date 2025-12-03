#!/bin/bash

# Script de setup inicial do projeto
# Sistema Operacional Bom Jesus - Backend

set -e

echo "🚀 Configurando Sistema Operacional Bom Jesus - Backend"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.11+"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Configurar .env
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp env.example .env
    echo "✅ Arquivo .env criado. Por favor, edite com suas configurações."
else
    echo "✅ Arquivo .env já existe"
fi

echo ""
echo "✅ Setup concluído!"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com suas configurações"
echo "2. Certifique-se de que o PostgreSQL está rodando"
echo "3. Execute: source venv/bin/activate"
echo "4. Execute: uvicorn main:app --reload"
echo ""
echo "Ou use Docker Compose:"
echo "docker-compose up -d"
echo ""

