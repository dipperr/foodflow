import pytz
import flet as ft
from datetime import datetime
from typing import List, Optional

from modelos import Produto
from banco_de_dados import SupabaseSingleton


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


class ControleProduto:
    def __init__(self, produto: Optional[Produto]=None, visualizacao=None):
        self.produto = produto
        self.visualizacao = visualizacao
        self.db = SupabaseSingleton()

    def criar_produto(
        self,
        nome: str,
        und: str,
        qtd_estoque: str,
        estoque_min: str,
        preco: Optional[str],
        categorias: Optional[dict],
        fornecedores: Optional[List[dict]],
        cmv: bool
    ):
        qtd_estoque, estoque_min, preco = self._formatar_valores(qtd_estoque, estoque_min, preco)
        try:
            client = self.db.get_client()

            if fornecedores is not None:
                fornecedores = [forns["nome"] for forns in fornecedores]

            resposta_produtos = (
                client.table("produtos")
                .insert(
                    {
                        "empresa_id": InfosGlobal().empresa_id,
                        "nome": nome.lower(),
                        "unidade": und.lower(),
                        "quantidade": qtd_estoque,
                        "estoque_minimo": estoque_min,
                        "preco_unidade": preco,
                        "cmv": cmv,
                        "categorias": categorias,
                        "fornecedores": {
                            "nomes": fornecedores
                        }
                    }
                )
                .execute()
            )
            resposta_movimentacao = (
                client.table("movimentacao")
                .insert({
                    "id_produto": resposta_produtos.data[0]["id"],
                    "empresa_id": InfosGlobal().empresa_id,
                    "unidade": und.lower(),
                    "data_movimentacao": self.gerar_data(),
                    "quantidade": qtd_estoque,
                    "operacao": "entrada",
                    "informacoes": "Web",
                    "preco_movimentacao": preco
                })
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            if self.visualizacao is not None:
                self.visualizacao.atualizar_dados()

    def atualizar_produto(
        self,
        id: int,
        nome: str,
        und: str,
        qtd_estoque: str,
        estoque_min: str,
        preco: Optional[str],
        categorias: Optional[List[dict]],
        fornecedores: Optional[List[dict]],
        cmv: bool
    ):
        qtd_estoque, estoque_min, preco = self._formatar_valores(qtd_estoque, estoque_min, preco)
        try:
            client = self.db.get_client()
            
            if categorias is not None:
                categorias = [cats["nome"] for cats in categorias]

            if fornecedores is not None:
                fornecedores = [forns["nome"] for forns in fornecedores]

            resposta = (
                client.table("produtos")
                .update(
                    {
                        "nome": nome.lower(),
                        "unidade": und.lower(),
                        "quantidade": qtd_estoque,
                        "estoque_minimo": estoque_min,
                        "preco_unidade": preco,
                        "cmv": cmv,
                        "categorias": {
                            "nomes": categorias
                        },
                        "fornecedores": {
                            "nomes": fornecedores
                        }
                    }
                )
                .eq("id", id)
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            if self.visualizacao is not None:
                self.visualizacao.atualizar_conteudo(
                    id=id,
                    nome=nome,
                    unidade=und,
                    qtd_estoque=qtd_estoque,
                    estoque_min=estoque_min,
                    preco=preco,
                    categorias={"nomes": categorias},
                    fornecedores={"nomes": fornecedores},
                    cmv=cmv
                )

    def gerar_data(self):
        br_tz = pytz.timezone("America/Sao_Paulo")
        dt_timezone = br_tz.localize(datetime.now()).strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
        return dt_timezone

    def _formatar_valores(self, *args):
        return [float(arg.replace(",", ".")) if arg is not None else None for arg in args]


class ControleCategoria:
    def __init__(self, categoria=None, visualizacao=None):
        self.categoria = categoria
        self.visualizacao = visualizacao
        self.db = SupabaseSingleton()

    def criar_categoria(self, nome: str, cor: str):
        try:
            client = self.db.get_client()
            resposta = (
                client.table("categoria")
                .insert(
                    {
                        "empresa_id": InfosGlobal().empresa_id,
                        "nome": nome.lower(),
                        "cor": cor,
                    }
                )
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            if self.visualizacao is not None:
                self.visualizacao.atualizar_item(resposta.data[0])
                self.visualizacao.fechar(None)


class ControleFornecedores:
    def __init__(self, fornecedor=None, visualizacao=None):
        self.fornecedor = fornecedor
        self.visualizacao = visualizacao
        self.db = SupabaseSingleton()

    def criar_fornecedor(self, nome_fornecedor: str, nome_vendedor: str, telefone: str):
        try:
            client = self.db.get_client()
            resposta = (
                client.table("fornecedores")
                .insert(
                    {
                        "empresa_id": InfosGlobal().empresa_id,
                        "nome": nome_fornecedor.lower(),
                        "nome_vendedor": nome_vendedor.lower() if nome_vendedor is not None else None,
                        "telefone": telefone
                    }
                )
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            if self.visualizacao is not None:
                self.visualizacao.atualizar_item(resposta.data[0])
                self.visualizacao.fechar(None)


class ControleMovimentacao:
    def __init__(self, visualizacao):
        self.visualizacao = visualizacao
        self.db = SupabaseSingleton()

    def atualizar(self, id, classificacao, qtd, valor_unit):
        qtd, valor_unit = self.formatar_valores(qtd, valor_unit)
        try:
            client = self.db.get_client()
            (
                client.table("movimentacao")
                .update({
                    "classificacao": classificacao,
                    "quantidade": qtd,
                    "preco_movimentacao": valor_unit
                })
                .eq("id", id)
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self.visualizacao.atualizar_infos(
                classificacao,
                float(qtd),
                float(valor_unit)
            )

    def registrar(
        self,
        id_produto: int,
        qtd_produto: float,
        acao: str,
        classificacao: str,
        unidade: str,
        qtd: str,
        data_movimentacao: str,
        preco: str,
        data_validade: str
    ):
        qtd, preco = self.formatar_valores(qtd, preco)
        qtd_produto = self.obter_quantidade(acao, qtd_produto, qtd)
        data_movimentacao = self.formatar_data_movimentacao(data_movimentacao)

        try:
            client = self.db.get_client()
            (
                client.table("produtos")
                .update({"quantidade": qtd_produto})
                .eq("id", id_produto)
                .execute()
            )
            (
                client.table("movimentacao")
                .insert({
                    "empresa_id": InfosGlobal().empresa_id,
                    "id_produto": id_produto,
                    "unidade": unidade,
                    "operacao": acao,
                    "data_movimentacao": data_movimentacao,
                    "preco_movimentacao": preco,
                    "data_validade": data_validade,
                    "informacoes": "Web",
                    "quantidade": qtd,
                    "classificacao": classificacao
                })
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self.visualizacao.atualizar_conteudo(qtd_estoque=qtd_produto)

    def formatar_valores(self, *args: str):
        return [valor.replace(",", ".").removeprefix("R$ ") for valor in args]
    
    def formatar_data_movimentacao(self, dt):
        try:
            br_tz = pytz.timezone("America/Sao_Paulo")
            dt += datetime.now().strftime(" %H:%M:%S")
            dt_timezone = (
                br_tz.localize(datetime.strptime(dt, "%d/%m/%Y %H:%M:%S"))
                .strftime("%Y-%m-%dT%H:%M:%S.000-04:00")
            )
            return dt_timezone
        except Exception:
            return dt
        
    def obter_quantidade(self, operacao, qtd_produto, qtd):
        if operacao.lower() == "saída":
            return float(qtd_produto) - float(qtd)
        elif operacao.lower() == "entrada":
            return float(qtd_produto) + float(qtd)


class ControleFichaTecnica:
    def __init__(self, visualizacao):
        self.db = SupabaseSingleton()
        self.visualizacao = visualizacao

    def criar_ficha(self, nome, unidade, porcao, estoque, produtos):
        porcao = self._formatar_valores(porcao)
        JSON = self._criar_json(produtos)
        try:
            client = self.db.get_client()
            (
                client.table("fichas_tecnicas")
                .insert({
                    "empresa_id": InfosGlobal().empresa_id,
                    "nome": nome.lower(),
                    "unidade": unidade,
                    "qtd_porcao": porcao[0],
                    "estoque": estoque,
                    "ingredientes": JSON
                })
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self.visualizacao.atualizar_dados()

    def apagar_ficha(self, id):
        try:
            cliente = self.db.get_client()
            (
                cliente.table("fichas_tecnicas")
                .delete()
                .eq("id", id)
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self.visualizacao.atualizar_pagina()

    def _formatar_valores(self, *args):
            return [float(arg.replace(",", ".")) if arg is not None else None for arg in args]
    
    def _criar_json(self, produtos):
        return {
            produto.pop("nome"): produto for produto in produtos
        }


class ControleDropdownV2:
    def __init__(self, dropdown):
        self.dropdown = dropdown

    def atualizar_itens(self, dados: dict) -> None:
        self.dropdown.atualizar_itens(dados["id"], dados["nome"])


class ControleCompras:
    def __init__(self, visualizacao) -> None:
        self.visualizacao = visualizacao

    def salvar_lista(self, nome, lista_compras):
        JSON = self._criar_json_produtos(lista_compras)
        valor_total = self._obter_valor_total(JSON)
        try:
            cliente = SupabaseSingleton().get_client()
            (
                cliente.table("lista_compras")
                .insert({
                    "empresa_id": InfosGlobal().empresa_id,
                    "nome": nome,
                    "valor_total": valor_total,
                    "produtos": JSON,
                    "recebimento": None,
                    "finalizada": False
                })
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self.visualizacao.pagina_inicial_e_atualizar()

    def atualizar_status(self, lista_id, produtos, opcao):
        print(opcao)
        JSON = self._criar_json_produtos(produtos)
        valor_total = self._obter_valor_total(JSON)
        try:
            cliente = SupabaseSingleton().get_client()
            (
                cliente.table("lista_compras")
                .update({
                    "valor_total": valor_total,
                    "finalizada": True,
                    "produtos": JSON,
                    "recebimento": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                .eq("id", lista_id)
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self.visualizacao.pagina_inicial_e_atualizar()


    def _criar_json_produtos(self, lista_compras):
        return {
            item.nome: {
                "id": item.id,
                "unidade": item.unidade,
                "quantidade": item.quantidade_num,
                "qtd_comprar": item.qtd_comprar_num,
                "estoque_minimo": item.estoque_minimo,
                "preco": item.preco,
                "categorias": item.categorias
            }
            for item in lista_compras
        }
    
    def _obter_valor_total(self, produtos: dict):
        return sum([
            item["preco"] * item["qtd_comprar"]
            for item in produtos.values()
        ])
