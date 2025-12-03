"""
Repositories - Camada de acesso a dados
"""
from .base import BaseRepository
from .carga import CargaRepository
from .camara import CamaraRepository
from .cliente import ClienteRepository
from .pedido import PedidoRepository
from .item_pedido import ItemPedidoRepository
from .pesagem import PesagemRepository
from .perda import PerdaRepository
from .devolucao import DevolucaoRepository
from .movimentacao_camara import MovimentacaoCamaraRepository
from .gasto_interno import GastoInternoRepository
from .log_operacional import LogOperacionalRepository
from .rota import RotaRepository
from .entrega_cliente import EntregaClienteRepository
from .ocr_input import OCRInputRepository

__all__ = [
    "BaseRepository",
    "CargaRepository",
    "CamaraRepository",
    "ClienteRepository",
    "PedidoRepository",
    "ItemPedidoRepository",
    "PesagemRepository",
    "PerdaRepository",
    "DevolucaoRepository",
    "MovimentacaoCamaraRepository",
    "GastoInternoRepository",
    "LogOperacionalRepository",
    "RotaRepository",
    "EntregaClienteRepository",
    "OCRInputRepository",
]
