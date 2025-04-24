from datetime import datetime
from typing import Optional


UNIDADES = [
    "bisnagas (bg)",
    "caixas (cx)",
    "fardos (fardo)",
    "frascos (fr)",
    "galões (gl)",
    "garrafas (gr)",
    "gramas (g)",
    "latas (lt)",
    "litros (l)",
    "mililitros (ml)",
    "pacote (pct)",
    "potes (pt)",
    "quilograma (kg)",
    "rolos (rl)",
    "sacos (sc)",
    "unidades (und)"
]


class InfosGlobal:
    _instance = None

    def __new__(cls,
        usuario_id=None,
        usuario_nome=None,
        empresa_id=None,
        empresa_nome=None
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.u_id = usuario_id
            cls._instance.u_nome = usuario_nome
            cls._instance.e_id = empresa_id
            cls._instance.e_nome = empresa_nome
        return cls._instance

    def atualizar(self, usuario_id, usuario_nome, empresa_id, empresa_nome):
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.empresa_id = empresa_id
        self.empresa_nome = empresa_nome


class CoresGlobal:
    _instance = None

    def __new__(cls,
        cores=None
    ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cores = cores
        return cls._instance

    def atualizar(self, cores):
        self.cores = cores


class Produto:
    def __init__(
        self,
        id=None,
        nome=None,
        unidade=None,
        qtd_estoque=None,
        estoque_min=None,
        preco=None,
        categorias=None,
        fornecedores=None,
        cmv=None
    ):
        self.id = id
        self.nome = nome
        self.unidade = unidade
        self.qtd_estoque = qtd_estoque
        self.estoque_min = estoque_min
        self.preco = preco
        self.categorias = categorias
        self.fornecedores = fornecedores
        self.cmv = cmv


class Empresa:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome


class Usuario:
    def __init__(self, id, nome, telefone):
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.empresas = []


class Categoria:
    def __init__(self, nome: str, cor: str):
        self.nome = nome
        self.cor = cor


class Fornecedor:
    def __init__(self, nome, vendedor, telefone):
        self.nome = nome
        self.vendedor = vendedor
        self.telefone = telefone


class Movimentacao:
    def __init__(
        self,
        id: int,
        operacao: str,
        classificacao: Optional[str],
        data: datetime,
        nome: str,
        qtd: float,
        unidade: str,
        valor_unit: float,
        mensagem: str
    ):
        self.id = id
        self.operacao  = operacao
        self.classificacao = classificacao
        self.data = data
        self.nome = nome
        self.qtd = qtd
        self.unidade = unidade
        self.valor_unit = valor_unit
        self.mensagem = mensagem
