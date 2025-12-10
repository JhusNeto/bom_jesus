"""
Schemas Pydantic para validação e serialização
"""
# Núcleo Técnico - Autenticação
from .user import UserCreate, UserUpdate, UserRead, UserLogin
from .auth import TokenResponse, RefreshTokenRequest, RefreshTokenResponse

# Núcleo Operacional
from .carga import CargaCreate, CargaUpdate, CargaRead
from .camara import CamaraCreate, CamaraUpdate, CamaraRead
from .movimentacao_camara import MovimentacaoCamaraCreate, MovimentacaoCamaraUpdate, MovimentacaoCamaraRead
from .pesagem import PesagemCreate, PesagemUpdate, PesagemRead
from .perda import PerdaCreate, PerdaUpdate, PerdaRead

# Núcleo Comercial
from .cliente import ClienteCreate, ClienteUpdate, ClienteRead
from .pedido import PedidoCreate, PedidoUpdate, PedidoRead
from .item_pedido import ItemPedidoCreate, ItemPedidoUpdate, ItemPedidoRead
from .devolucao import DevolucaoCreate, DevolucaoUpdate, DevolucaoRead

# Núcleo Financeiro
from .gasto_interno import GastoInternoCreate, GastoInternoUpdate, GastoInternoRead

# Núcleo Técnico
from .log_operacional import LogOperacionalCreate, LogOperacionalRead

# Núcleo IA/Futuro
from .ocr_input import OCRInputCreate, OCRInputUpdate, OCRInputRead
from .rota import RotaCreate, RotaUpdate, RotaRead
from .entrega_cliente import EntregaClienteCreate, EntregaClienteUpdate, EntregaClienteRead

__all__ = [
    # Núcleo Técnico - Autenticação
    "UserCreate", "UserUpdate", "UserRead", "UserLogin",
    "TokenResponse", "RefreshTokenRequest", "RefreshTokenResponse",
    # Núcleo Operacional
    "CargaCreate", "CargaUpdate", "CargaRead",
    "CamaraCreate", "CamaraUpdate", "CamaraRead",
    "MovimentacaoCamaraCreate", "MovimentacaoCamaraUpdate", "MovimentacaoCamaraRead",
    "PesagemCreate", "PesagemUpdate", "PesagemRead",
    "PerdaCreate", "PerdaUpdate", "PerdaRead",
    # Núcleo Comercial
    "ClienteCreate", "ClienteUpdate", "ClienteRead",
    "PedidoCreate", "PedidoUpdate", "PedidoRead",
    "ItemPedidoCreate", "ItemPedidoUpdate", "ItemPedidoRead",
    "DevolucaoCreate", "DevolucaoUpdate", "DevolucaoRead",
    # Núcleo Financeiro
    "GastoInternoCreate", "GastoInternoUpdate", "GastoInternoRead",
    # Núcleo Técnico
    "LogOperacionalCreate", "LogOperacionalRead",
    # Núcleo IA/Futuro
    "OCRInputCreate", "OCRInputUpdate", "OCRInputRead",
    "RotaCreate", "RotaUpdate", "RotaRead",
    "EntregaClienteCreate", "EntregaClienteUpdate", "EntregaClienteRead",
]
