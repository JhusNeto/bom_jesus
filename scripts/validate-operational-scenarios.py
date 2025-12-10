#!/usr/bin/env python3
"""
Script de Validação de Cenários Operacionais Reais
Simula casos reais do dia a dia da operação do Bom Jesus
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.cliente import Cliente, TipoCliente
from app.models.carga import Carga, TipoBanana, StatusCarga
from app.models.camara import Camara, StatusCamara
from app.models.pedido import Pedido, OrigemPedido, StatusPedido
from app.models.item_pedido import ItemPedido
from app.models.pesagem import Pesagem, StatusPesagem
from app.models.movimentacao_camara import MovimentacaoCamara, TipoMovimento
from app.models.perda import Perda
from app.models.devolucao import Devolucao
from app.models.rota import Rota, StatusRota
from app.models.entrega_cliente import EntregaCliente
from app.models.gasto_interno import GastoInterno, TipoGasto
from app.models.log_operacional import LogOperacional, TipoLog

class OperationalValidator:
    """Validador de cenários operacionais"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.errors = []
        self.warnings = []
        self.success = []
        self.created_entities = {}
        
    def log_success(self, message):
        """Registra sucesso"""
        self.success.append(message)
        print(f"✅ {message}")
    
    def log_error(self, message):
        """Registra erro"""
        self.errors.append(message)
        print(f"❌ {message}")
    
    def log_warning(self, message):
        """Registra aviso"""
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def get_user(self, role: UserRole):
        """Obtém usuário por role"""
        user = self.db.query(User).filter(User.role == role).first()
        if not user:
            self.log_error(f"Usuário com role {role.value} não encontrado")
        return user
    
    def validate_and_create(self):
        """Valida e cria dados de teste"""
        try:
            print("\n" + "="*80)
            print("  VALIDAÇÃO DE CENÁRIOS OPERACIONAIS REAIS")
            print("="*80 + "\n")
            
            # 1. CENÁRIO: Setup Inicial (Câmaras e Usuários)
            self.scenario_1_setup_inicial()
            
            # 2. CENÁRIO: Chegada de Carga de Fornecedor
            self.scenario_2_chegada_carga()
            
            # 3. CENÁRIO: Armazenamento em Câmaras
            self.scenario_3_armazenamento_camaras()
            
            # 4. CENÁRIO: Clientes e Pedidos
            self.scenario_4_clientes_pedidos()
            
            # 5. CENÁRIO: Pesagem e Separação
            self.scenario_5_pesagem_separacao()
            
            # 6. CENÁRIO: Perdas Durante Armazenamento
            self.scenario_6_perdas_armazenamento()
            
            # 7. CENÁRIO: Rotas e Entregas
            self.scenario_7_rotas_entregas()
            
            # 8. CENÁRIO: Devoluções
            self.scenario_8_devolucoes()
            
            # 9. CENÁRIO: Gastos Internos
            self.scenario_9_gastos_internos()
            
            # 10. CENÁRIO: Casos Edge e Validações
            self.scenario_10_casos_edge()
            
            # 11. CENÁRIO: Validação de Integridade
            self.scenario_11_validacao_integridade()
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Erro geral: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            self.db.close()
    
    def scenario_1_setup_inicial(self):
        """CENÁRIO 1: Setup Inicial - Câmaras e Usuários"""
        print("\n" + "-"*80)
        print("CENÁRIO 1: Setup Inicial - Câmaras e Usuários")
        print("-"*80)
        
        # Verificar usuários existentes
        admin = self.get_user(UserRole.ADMIN)
        operator = self.get_user(UserRole.OPERATOR)
        
        if not admin:
            self.log_error("Admin não encontrado - necessário para operação")
        else:
            self.created_entities['admin'] = admin
            self.log_success(f"Admin encontrado: {admin.email}")
        
        if not operator:
            self.log_warning("Operador não encontrado - algumas pesagens ficarão sem operador")
        else:
            self.created_entities['operator'] = operator
            self.log_success(f"Operador encontrado: {operator.email}")
        
        # Criar câmaras
        camaras_data = [
            {"nome": "Câmara 01", "capacidade": 500, "status": StatusCamara.DISPONIVEL},
            {"nome": "Câmara 02", "capacidade": 800, "status": StatusCamara.DISPONIVEL},
            {"nome": "Câmara 03", "capacidade": 600, "status": StatusCamara.DISPONIVEL},
            {"nome": "Câmara 04", "capacidade": 400, "status": StatusCamara.MANUTENCAO},
        ]
        
        self.created_entities['camaras'] = []
        for camara_data in camaras_data:
            existing = self.db.query(Camara).filter(Camara.nome == camara_data["nome"]).first()
            if existing:
                self.created_entities['camaras'].append(existing)
                self.log_warning(f"Câmara {camara_data['nome']} já existe")
            else:
                camara = Camara(**camara_data)
                self.db.add(camara)
                self.db.flush()
                self.created_entities['camaras'].append(camara)
                self.log_success(f"Câmara criada: {camara.nome} (Capacidade: {camara.capacidade} caixas)")
    
    def scenario_2_chegada_carga(self):
        """CENÁRIO 2: Chegada de Carga de Fornecedor"""
        print("\n" + "-"*80)
        print("CENÁRIO 2: Chegada de Carga de Fornecedor")
        print("-"*80)
        
        # Simular chegadas de carga em diferentes dias
        hoje = datetime.utcnow()
        cargas_data = [
            {
                "data_chegada": hoje - timedelta(days=5),
                "fornecedor": "Fazenda São João",
                "fazenda": "Sítio das Bananas",
                "tipo_banana": TipoBanana.NANICA,
                "qualidade_inicial": "A",
                "quantidade_caixas": 300,
                "preco_compra": Decimal("25.50"),
                "status": StatusCarga.EM_ESTOQUE,
            },
            {
                "data_chegada": hoje - timedelta(days=3),
                "fornecedor": "Bananal do Sul",
                "fazenda": None,
                "tipo_banana": TipoBanana.PRATA,
                "qualidade_inicial": "A",
                "quantidade_caixas": 450,
                "preco_compra": Decimal("28.00"),
                "status": StatusCarga.EM_ESTOQUE,
            },
            {
                "data_chegada": hoje - timedelta(days=1),
                "fornecedor": "Cooperativa Verde",
                "fazenda": "Chácara do Vale",
                "tipo_banana": TipoBanana.MACA,
                "qualidade_inicial": "B",
                "quantidade_caixas": 200,
                "preco_compra": Decimal("22.50"),
                "status": StatusCarga.EM_ESTOQUE,
            },
            {
                "data_chegada": hoje - timedelta(days=10),
                "fornecedor": "Fazenda São João",
                "fazenda": "Sítio das Bananas",
                "tipo_banana": TipoBanana.NANICA,
                "qualidade_inicial": "A",
                "quantidade_caixas": 500,
                "preco_compra": Decimal("24.00"),
                "status": StatusCarga.ENCERRADA,  # Carga antiga já encerrada
            },
        ]
        
        self.created_entities['cargas'] = []
        for carga_data in cargas_data:
            carga = Carga(**carga_data)
            self.db.add(carga)
            self.db.flush()
            self.created_entities['cargas'].append(carga)
            self.log_success(
                f"Carga criada: {carga.fornecedor} - {carga.tipo_banana.value} "
                f"({carga.quantidade_caixas} caixas, R$ {carga.preco_compra})"
            )
    
    def scenario_3_armazenamento_camaras(self):
        """CENÁRIO 3: Armazenamento em Câmaras"""
        print("\n" + "-"*80)
        print("CENÁRIO 3: Armazenamento em Câmaras")
        print("-"*80)
        
        camaras = self.created_entities.get('camaras', [])
        cargas = self.created_entities.get('cargas', [])
        
        if not camaras or not cargas:
            self.log_error("Câmaras ou cargas não encontradas")
            return
        
        # Movimentação 1: Entrada na Câmara 01
        if len(cargas) > 0 and len(camaras) > 0:
            mov1 = MovimentacaoCamara(
                camara_id=camaras[0].id,
                carga_id=cargas[0].id,
                data=cargas[0].data_chegada + timedelta(hours=2),
                tipo_movimento=TipoMovimento.ENTRADA,
                quantidade_caixas=300,
                observacao="Carga completa armazenada"
            )
            self.db.add(mov1)
            self.db.flush()
            self.log_success(f"Entrada: {mov1.quantidade_caixas} caixas na {camaras[0].nome}")
            
            # Atualizar status da câmara
            camaras[0].status = StatusCamara.OCUPADA
        
        # Movimentação 2: Entrada na Câmara 02
        if len(cargas) > 1 and len(camaras) > 1:
            mov2 = MovimentacaoCamara(
                camara_id=camaras[1].id,
                carga_id=cargas[1].id,
                data=cargas[1].data_chegada + timedelta(hours=1),
                tipo_movimento=TipoMovimento.ENTRADA,
                quantidade_caixas=450,
                observacao="Carga completa armazenada"
            )
            self.db.add(mov2)
            self.db.flush()
            self.log_success(f"Entrada: {mov2.quantidade_caixas} caixas na {camaras[1].nome}")
            
            # Atualizar status da câmara
            camaras[1].status = StatusCamara.OCUPADA
        
        # Movimentação 3: Entrada parcial na Câmara 01 (câmara já ocupada)
        if len(cargas) > 2 and len(camaras) > 0:
            mov3 = MovimentacaoCamara(
                camara_id=camaras[0].id,
                carga_id=cargas[2].id,
                data=cargas[2].data_chegada + timedelta(hours=3),
                tipo_movimento=TipoMovimento.ENTRADA,
                quantidade_caixas=150,  # Entrada parcial
                observacao="Entrada parcial - câmara já ocupada"
            )
            self.db.add(mov3)
            self.db.flush()
            self.log_success(f"Entrada parcial: {mov3.quantidade_caixas} caixas na {camaras[0].nome}")
    
    def scenario_4_clientes_pedidos(self):
        """CENÁRIO 4: Clientes e Pedidos"""
        print("\n" + "-"*80)
        print("CENÁRIO 4: Clientes e Pedidos")
        print("-"*80)
        
        # Criar clientes diversos
        clientes_data = [
            {
                "nome": "Mercado Central",
                "tipo": TipoCliente.MERCADO,
                "cidade": "São Paulo",
                "bairro": "Centro",
                "endereco": "Rua das Flores, 123",
                "telefone": "(11) 98765-4321",
                "ativo": True,
            },
            {
                "nome": "CEASA Campinas",
                "tipo": TipoCliente.CEASA,
                "cidade": "Campinas",
                "bairro": "Distrito Industrial",
                "endereco": "Av. das Hortaliças, 500",
                "telefone": "(19) 3456-7890",
                "ativo": True,
            },
            {
                "nome": "Atacado Bom Preço",
                "tipo": TipoCliente.ATACADO,
                "cidade": "São Paulo",
                "bairro": "Vila Nova",
                "endereco": "Rua Comercial, 789",
                "telefone": "(11) 2345-6789",
                "ativo": True,
            },
            {
                "nome": "Sacolão do Bairro",
                "tipo": TipoCliente.SACOLAO,
                "cidade": "São Paulo",
                "bairro": "Jardim Primavera",
                "endereco": None,  # Cliente sem endereço completo
                "telefone": "(11) 91234-5678",
                "ativo": True,
            },
            {
                "nome": "Cliente Inativo",
                "tipo": TipoCliente.OUTRO,
                "cidade": "São Paulo",
                "ativo": False,  # Cliente inativo
            },
        ]
        
        self.created_entities['clientes'] = []
        for cliente_data in clientes_data:
            existing = self.db.query(Cliente).filter(Cliente.nome == cliente_data["nome"]).first()
            if existing:
                self.created_entities['clientes'].append(existing)
                self.log_warning(f"Cliente {cliente_data['nome']} já existe")
            else:
                cliente = Cliente(**cliente_data)
                self.db.add(cliente)
                self.db.flush()
                self.created_entities['clientes'].append(cliente)
                self.log_success(f"Cliente criado: {cliente.nome} ({cliente.tipo.value})")
        
        # Criar pedidos diversos
        clientes = self.created_entities.get('clientes', [])
        if not clientes:
            self.log_error("Nenhum cliente criado")
            return
        
        hoje = datetime.utcnow()
        pedidos_data = [
            {
                "data": hoje - timedelta(days=2),
                "cliente_id": clientes[0].id,  # Mercado Central
                "origem_pedido": OrigemPedido.WHATSAPP,
                "status": StatusPedido.ABERTO,
                "observacoes": "Pedido urgente - entregar amanhã",
            },
            {
                "data": hoje - timedelta(days=1),
                "cliente_id": clientes[1].id,  # CEASA
                "origem_pedido": OrigemPedido.TELEFONE,
                "status": StatusPedido.SEPARADO,
                "observacoes": None,
            },
            {
                "data": hoje,
                "cliente_id": clientes[0].id,  # Mercado Central (segundo pedido)
                "origem_pedido": OrigemPedido.MANUAL,
                "status": StatusPedido.ABERTO,
                "observacoes": "Cliente pediu desconto",
            },
            {
                "data": hoje - timedelta(days=3),
                "cliente_id": clientes[2].id,  # Atacado
                "origem_pedido": OrigemPedido.OCR,
                "status": StatusPedido.ENVIADO,
                "observacoes": "Pedido já enviado",
            },
        ]
        
        self.created_entities['pedidos'] = []
        for pedido_data in pedidos_data:
            pedido = Pedido(**pedido_data)
            self.db.add(pedido)
            self.db.flush()
            self.created_entities['pedidos'].append(pedido)
            self.log_success(
                f"Pedido criado: {pedido.origem_pedido.value} - "
                f"Status: {pedido.status.value}"
            )
            
            # Adicionar itens aos pedidos
            if pedido.origem_pedido == OrigemPedido.WHATSAPP:
                # Pedido com múltiplos itens
                itens = [
                    {"tipo_banana": TipoBanana.NANICA, "quantidade_caixas": 50, "preco_unitario": Decimal("30.00")},
                    {"tipo_banana": TipoBanana.PRATA, "quantidade_caixas": 30, "preco_unitario": Decimal("32.00")},
                ]
            elif pedido.origem_pedido == OrigemPedido.TELEFONE:
                itens = [
                    {"tipo_banana": TipoBanana.NANICA, "quantidade_caixas": 100, "preco_unitario": Decimal("28.50")},
                ]
            elif pedido.origem_pedido == OrigemPedido.MANUAL:
                itens = [
                    {"tipo_banana": TipoBanana.MACA, "quantidade_caixas": 25, "preco_unitario": Decimal("27.00")},
                ]
            else:  # OCR
                itens = [
                    {"tipo_banana": TipoBanana.PRATA, "quantidade_caixas": 80, "preco_unitario": Decimal("31.00")},
                ]
            
            for item_data in itens:
                item = ItemPedido(
                    pedido_id=pedido.id,
                    tipo_banana=item_data["tipo_banana"],
                    quantidade_caixas=item_data["quantidade_caixas"],
                    preco_unitario=item_data["preco_unitario"],
                    preco_total=item_data["preco_unitario"] * item_data["quantidade_caixas"],
                )
                self.db.add(item)
                self.log_success(
                    f"  Item: {item.tipo_banana.value} - {item.quantidade_caixas} caixas "
                    f"(R$ {item.preco_unitario}/caixa)"
                )
    
    def scenario_5_pesagem_separacao(self):
        """CENÁRIO 5: Pesagem e Separação"""
        print("\n" + "-"*80)
        print("CENÁRIO 5: Pesagem e Separação")
        print("-"*80)
        
        clientes = self.created_entities.get('clientes', [])
        cargas = self.created_entities.get('cargas', [])
        operator = self.created_entities.get('operator')
        
        if not clientes or not cargas:
            self.log_error("Clientes ou cargas não encontradas")
            return
        
        hoje = datetime.utcnow()
        pesagens_data = [
            {
                "data": hoje - timedelta(days=2),
                "cliente_id": clientes[0].id,  # Mercado Central
                "carga_id": cargas[0].id,
                "quantidade_caixas": 50,
                "peso_total": Decimal("1250.50"),  # ~25kg por caixa
                "operador_id": operator.id if operator else None,
                "status": StatusPesagem.CARREGADO,
            },
            {
                "data": hoje - timedelta(days=1),
                "cliente_id": clientes[1].id,  # CEASA
                "carga_id": cargas[0].id,
                "quantidade_caixas": 100,
                "peso_total": Decimal("2500.00"),
                "operador_id": operator.id if operator else None,
                "status": StatusPesagem.ENVIADO,
            },
            {
                "data": hoje,
                "cliente_id": clientes[2].id,  # Atacado
                "carga_id": cargas[1].id,
                "quantidade_caixas": 200,
                "peso_total": Decimal("5000.00"),
                "operador_id": None,  # Pesagem sem operador (caso edge)
                "status": StatusPesagem.PENDENTE,
            },
        ]
        
        self.created_entities['pesagens'] = []
        for pesagem_data in pesagens_data:
            pesagem = Pesagem(**pesagem_data)
            self.db.add(pesagem)
            self.db.flush()
            self.created_entities['pesagens'].append(pesagem)
            operador_info = f" (Operador: {operator.email})" if pesagem.operador_id else " (Sem operador)"
            self.log_success(
                f"Pesagem criada: {pesagem.quantidade_caixas} caixas, "
                f"{pesagem.peso_total}kg - Status: {pesagem.status.value}{operador_info}"
            )
    
    def scenario_6_perdas_armazenamento(self):
        """CENÁRIO 6: Perdas Durante Armazenamento"""
        print("\n" + "-"*80)
        print("CENÁRIO 6: Perdas Durante Armazenamento")
        print("-"*80)
        
        cargas = self.created_entities.get('cargas', [])
        if not cargas:
            self.log_error("Cargas não encontradas")
            return
        
        hoje = datetime.utcnow()
        perdas_data = [
            {
                "carga_id": cargas[0].id,
                "data": hoje - timedelta(days=4),
                "quantidade_caixas": 5,
                "motivo": "Fruta passou - muito madura",
                "valor_estimado": Decimal("127.50"),  # 5 * 25.50
            },
            {
                "carga_id": cargas[0].id,
                "data": hoje - timedelta(days=2),
                "quantidade_caixas": 3,
                "motivo": "Fruta machucada durante transporte",
                "valor_estimado": Decimal("76.50"),
            },
            {
                "carga_id": cargas[1].id,
                "data": hoje - timedelta(days=1),
                "quantidade_caixas": 10,
                "motivo": "Fruta amoleceu na câmara",
                "valor_estimado": Decimal("280.00"),
            },
        ]
        
        self.created_entities['perdas'] = []
        for perda_data in perdas_data:
            perda = Perda(**perda_data)
            self.db.add(perda)
            self.db.flush()
            self.created_entities['perdas'].append(perda)
            self.log_success(
                f"Perda registrada: {perda.quantidade_caixas} caixas - "
                f"{perda.motivo} (R$ {perda.valor_estimado})"
            )
    
    def scenario_7_rotas_entregas(self):
        """CENÁRIO 7: Rotas e Entregas"""
        print("\n" + "-"*80)
        print("CENÁRIO 7: Rotas e Entregas")
        print("-"*80)
        
        clientes = self.created_entities.get('clientes', [])
        pedidos = self.created_entities.get('pedidos', [])
        
        if not clientes:
            self.log_error("Clientes não encontrados")
            return
        
        hoje = datetime.utcnow()
        
        # Rota 1: Rota concluída
        rota1 = Rota(
            motorista="João Silva",
            veiculo="Caminhão ABC-1234",
            data=hoje - timedelta(days=1),
            status=StatusRota.CONCLUIDA,
            observacoes="Rota executada com sucesso"
        )
        self.db.add(rota1)
        self.db.flush()
        self.log_success(f"Rota criada: {rota1.motorista} - Status: {rota1.status.value}")
        
        # Entregas da Rota 1
        if len(pedidos) > 0:
            entrega1 = EntregaCliente(
                rota_id=rota1.id,
                cliente_id=clientes[0].id,
                pedido_id=pedidos[0].id if len(pedidos) > 0 else None,
                quantidade_caixas=50,
                devolucao=False,
                horario=hoje - timedelta(days=1, hours=10),
            )
            self.db.add(entrega1)
            self.log_success(f"Entrega criada: {clientes[0].nome} - {entrega1.quantidade_caixas} caixas")
        
        if len(pedidos) > 1:
            entrega2 = EntregaCliente(
                rota_id=rota1.id,
                cliente_id=clientes[1].id,
                pedido_id=pedidos[1].id,
                quantidade_caixas=100,
                devolucao=False,
                horario=hoje - timedelta(days=1, hours=14),
            )
            self.db.add(entrega2)
            self.log_success(f"Entrega criada: {clientes[1].nome} - {entrega2.quantidade_caixas} caixas")
        
        # Rota 2: Rota em andamento
        rota2 = Rota(
            motorista="Maria Santos",
            veiculo="Van XYZ-5678",
            data=hoje,
            status=StatusRota.EM_ANDAMENTO,
            observacoes="Rota em execução"
        )
        self.db.add(rota2)
        self.db.flush()
        self.log_success(f"Rota criada: {rota2.motorista} - Status: {rota2.status.value}")
        
        # Rota 3: Rota planejada
        rota3 = Rota(
            motorista="Pedro Costa",
            veiculo="Caminhão DEF-9012",
            data=hoje + timedelta(days=1),
            status=StatusRota.PLANEJADA,
            observacoes="Rota planejada para amanhã"
        )
        self.db.add(rota3)
        self.db.flush()
        self.log_success(f"Rota criada: {rota3.motorista} - Status: {rota3.status.value}")
    
    def scenario_8_devolucoes(self):
        """CENÁRIO 8: Devoluções"""
        print("\n" + "-"*80)
        print("CENÁRIO 8: Devoluções")
        print("-"*80)
        
        clientes = self.created_entities.get('clientes', [])
        pedidos = self.created_entities.get('pedidos', [])
        
        if not clientes:
            self.log_error("Clientes não encontrados")
            return
        
        hoje = datetime.utcnow()
        devolucoes_data = [
            {
                "cliente_id": clientes[0].id,
                "pedido_id": pedidos[0].id if len(pedidos) > 0 else None,
                "data": hoje - timedelta(days=1),
                "quantidade_caixas": 5,
                "motivo": "Cliente reclamou que a fruta estava muito verde",
                "valor_estornado": Decimal("150.00"),
            },
            {
                "cliente_id": clientes[1].id,
                "pedido_id": None,  # Devolução sem pedido (caso edge)
                "data": hoje,
                "quantidade_caixas": 3,
                "motivo": "Devolução direta - cliente não pediu",
                "valor_estornado": Decimal("85.50"),
            },
        ]
        
        self.created_entities['devolucoes'] = []
        for devolucao_data in devolucoes_data:
            devolucao = Devolucao(**devolucao_data)
            self.db.add(devolucao)
            self.db.flush()
            self.created_entities['devolucoes'].append(devolucao)
            pedido_info = f" (Pedido: {devolucao.pedido_id})" if devolucao.pedido_id else " (Sem pedido)"
            self.log_success(
                f"Devolução registrada: {devolucao.quantidade_caixas} caixas - "
                f"R$ {devolucao.valor_estornado}{pedido_info}"
            )
    
    def scenario_9_gastos_internos(self):
        """CENÁRIO 9: Gastos Internos"""
        print("\n" + "-"*80)
        print("CENÁRIO 9: Gastos Internos")
        print("-"*80)
        
        hoje = datetime.utcnow()
        gastos_data = [
            {
                "data": hoje - timedelta(days=5),
                "tipo": TipoGasto.VALE_TRANSPORTE,
                "valor": Decimal("150.00"),
                "descricao": "Vale transporte funcionários - semana",
            },
            {
                "data": hoje - timedelta(days=3),
                "tipo": TipoGasto.GASOLINA,
                "valor": Decimal("350.00"),
                "descricao": "Combustível caminhões",
            },
            {
                "data": hoje - timedelta(days=1),
                "tipo": TipoGasto.MANUTENCAO,
                "valor": Decimal("500.00"),
                "descricao": "Manutenção câmara 04",
            },
            {
                "data": hoje,
                "tipo": TipoGasto.ADMINISTRATIVO,
                "valor": Decimal("200.00"),
                "descricao": "Material de escritório",
            },
        ]
        
        self.created_entities['gastos'] = []
        for gasto_data in gastos_data:
            gasto = GastoInterno(**gasto_data)
            self.db.add(gasto)
            self.db.flush()
            self.created_entities['gastos'].append(gasto)
            self.log_success(
                f"Gasto registrado: {gasto.tipo.value} - R$ {gasto.valor} - {gasto.descricao}"
            )
    
    def scenario_10_casos_edge(self):
        """CENÁRIO 10: Casos Edge e Validações"""
        print("\n" + "-"*80)
        print("CENÁRIO 10: Casos Edge e Validações")
        print("-"*80)
        
        # Caso Edge 1: Movimentação sem carga (ajuste manual)
        camaras = self.created_entities.get('camaras', [])
        if camaras:
            mov_sem_carga = MovimentacaoCamara(
                camara_id=camaras[0].id,
                carga_id=None,  # Movimentação sem carga associada
                data=datetime.utcnow(),
                tipo_movimento=TipoMovimento.SAIDA,
                quantidade_caixas=10,
                observacao="Ajuste manual de estoque"
            )
            self.db.add(mov_sem_carga)
            self.log_success("Movimentação sem carga criada (caso edge)")
        
        # Caso Edge 2: Pedido sem itens (será validado na integridade)
        clientes = self.created_entities.get('clientes', [])
        if clientes:
            pedido_sem_itens = Pedido(
                data=datetime.utcnow(),
                cliente_id=clientes[0].id,
                origem_pedido=OrigemPedido.MANUAL,
                status=StatusPedido.ABERTO,
                observacoes="Pedido criado sem itens (será validado)"
            )
            self.db.add(pedido_sem_itens)
            self.log_warning("Pedido sem itens criado (caso edge - será validado)")
        
        # Caso Edge 3: Saída de câmara maior que entrada
        if camaras and len(self.created_entities.get('cargas', [])) > 0:
            mov_saida = MovimentacaoCamara(
                camara_id=camaras[0].id,
                carga_id=self.created_entities['cargas'][0].id,
                data=datetime.utcnow(),
                tipo_movimento=TipoMovimento.SAIDA,
                quantidade_caixas=400,  # Mais que a entrada (300)
                observacao="Saída maior que entrada (caso edge - possível erro)"
            )
            self.db.add(mov_saida)
            self.log_warning("Saída maior que entrada criada (caso edge - possível erro)")
    
    def scenario_11_validacao_integridade(self):
        """CENÁRIO 11: Validação de Integridade"""
        print("\n" + "-"*80)
        print("CENÁRIO 11: Validação de Integridade")
        print("-"*80)
        
        # Validar relacionamentos
        self.db.flush()
        
        # 1. Validar que pedidos têm itens
        pedidos = self.db.query(Pedido).all()
        pedidos_sem_itens = [p for p in pedidos if not p.itens]
        if pedidos_sem_itens:
            self.log_warning(f"{len(pedidos_sem_itens)} pedidos sem itens encontrados")
        else:
            self.log_success("Todos os pedidos têm itens")
        
        # 2. Validar que pesagens têm cliente e carga
        pesagens = self.db.query(Pesagem).all()
        pesagens_invalidas = [p for p in pesagens if not p.cliente_id or not p.carga_id]
        if pesagens_invalidas:
            self.log_error(f"{len(pesagens_invalidas)} pesagens inválidas encontradas")
        else:
            self.log_success("Todas as pesagens têm cliente e carga")
        
        # 3. Validar que movimentações têm câmara
        movimentacoes = self.db.query(MovimentacaoCamara).all()
        mov_invalidas = [m for m in movimentacoes if not m.camara_id]
        if mov_invalidas:
            self.log_error(f"{len(mov_invalidas)} movimentações inválidas encontradas")
        else:
            self.log_success("Todas as movimentações têm câmara")
        
        # 4. Validar que entregas têm rota e cliente
        entregas = self.db.query(EntregaCliente).all()
        entregas_invalidas = [e for e in entregas if not e.rota_id or not e.cliente_id]
        if entregas_invalidas:
            self.log_error(f"{len(entregas_invalidas)} entregas inválidas encontradas")
        else:
            self.log_success("Todas as entregas têm rota e cliente")
        
        # 5. Validar que perdas têm carga
        perdas = self.db.query(Perda).all()
        perdas_invalidas = [p for p in perdas if not p.carga_id]
        if perdas_invalidas:
            self.log_error(f"{len(perdas_invalidas)} perdas inválidas encontradas")
        else:
            self.log_success("Todas as perdas têm carga")
        
        # 6. Validar que devoluções têm cliente
        devolucoes = self.db.query(Devolucao).all()
        devolucoes_invalidas = [d for d in devolucoes if not d.cliente_id]
        if devolucoes_invalidas:
            self.log_error(f"{len(devolucoes_invalidas)} devoluções inválidas encontradas")
        else:
            self.log_success("Todas as devoluções têm cliente")
        
        # 7. Validar consistência de quantidades
        cargas = self.db.query(Carga).all()
        for carga in cargas:
            total_pesagens = sum(p.quantidade_caixas for p in carga.pesagens)
            total_perdas = sum(p.quantidade_caixas for p in carga.perdas)
            total_movimentacoes = sum(m.quantidade_caixas for m in carga.movimentacoes if m.tipo_movimento == TipoMovimento.ENTRADA)
            
            if total_pesagens + total_perdas > carga.quantidade_caixas:
                self.log_warning(
                    f"Carga {carga.id}: Pesagens ({total_pesagens}) + Perdas ({total_perdas}) "
                    f"> Quantidade total ({carga.quantidade_caixas})"
                )
            else:
                self.log_success(
                    f"Carga {carga.id}: Quantidades consistentes "
                    f"(Total: {carga.quantidade_caixas}, Pesagens: {total_pesagens}, Perdas: {total_perdas})"
                )
    
    def print_summary(self):
        """Imprime resumo final"""
        print("\n" + "="*80)
        print("  RESUMO DA VALIDAÇÃO")
        print("="*80)
        print(f"\n✅ Sucessos: {len(self.success)}")
        print(f"⚠️  Avisos: {len(self.warnings)}")
        print(f"❌ Erros: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ ERROS ENCONTRADOS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  AVISOS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n" + "="*80)
        if self.errors:
            print("❌ VALIDAÇÃO FALHOU - Corrija os erros acima")
            return False
        else:
            print("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO")
            return True

if __name__ == "__main__":
    validator = OperationalValidator()
    validator.validate_and_create()
    success = validator.print_summary()
    sys.exit(0 if success else 1)

