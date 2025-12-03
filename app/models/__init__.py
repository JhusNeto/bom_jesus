"""
Models do SQLAlchemy
Aqui ficarão os models do banco de dados
"""
# Núcleo Técnico
from .user import User, UserRole
from .auth_token import AuthToken
from .log_operacional import LogOperacional, TipoLog

# Núcleo Operacional
from .carga import Carga, TipoBanana, StatusCarga
from .camara import Camara, StatusCamara
from .movimentacao_camara import MovimentacaoCamara, TipoMovimento
from .pesagem import Pesagem, StatusPesagem
from .perda import Perda

# Núcleo Comercial
from .cliente import Cliente, TipoCliente
from .pedido import Pedido, OrigemPedido, StatusPedido
from .item_pedido import ItemPedido
from .devolucao import Devolucao

# Núcleo Financeiro
from .gasto_interno import GastoInterno, TipoGasto

# Núcleo IA/Futuro
from .ocr_input import OCRInput
from .rota import Rota, StatusRota
from .entrega_cliente import EntregaCliente

__all__ = [
    # Núcleo Técnico
    "User",
    "UserRole",
    "AuthToken",
    "LogOperacional",
    "TipoLog",
    # Núcleo Operacional
    "Carga",
    "TipoBanana",
    "StatusCarga",
    "Camara",
    "StatusCamara",
    "MovimentacaoCamara",
    "TipoMovimento",
    "Pesagem",
    "StatusPesagem",
    "Perda",
    # Núcleo Comercial
    "Cliente",
    "TipoCliente",
    "Pedido",
    "OrigemPedido",
    "StatusPedido",
    "ItemPedido",
    "Devolucao",
    # Núcleo Financeiro
    "GastoInterno",
    "TipoGasto",
    # Núcleo IA/Futuro
    "OCRInput",
    "Rota",
    "StatusRota",
    "EntregaCliente",
]
