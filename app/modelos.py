from datetime import datetime
from typing import Optional
from banco_de_dados import SupabaseSingleton


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

    def atualizar_qtd(self):
        try:
            cliente = SupabaseSingleton().get_client()
            resposta = (
                cliente.table("produtos")
                .select("quantidade")
                .eq("id", self.id)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self.qtd_estoque = resposta[0]["quantidade"]


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
        mensagem: str,
        produto_id: Optional[int]=None,
        qtd_estoque: Optional[float]=None
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
        self.produto_id = produto_id
        self.qtd_estoque = qtd_estoque
