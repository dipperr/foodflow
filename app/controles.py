import flet as ft
import pytz
from datetime import datetime
from typing import Callable, List, Optional

from modelos import Produto, InfosGlobal, CoresGlobal
from banco_de_dados import SupabaseSingleton


class GradeNotificacao(ft.ResponsiveRow):
    def __init__(self, itens: list, num_colunas: int=2):
        super().__init__()
        
        itens_por_coluna = len(itens) // num_colunas
        restante = len(itens) % num_colunas

        colunas = []
        for i in range(num_colunas):
            inicio = i * itens_por_coluna + min(i, restante)
            fim = (i + 1) * itens_por_coluna + min(i + 1, restante)
            
            coluna = ft.Column([item for item in itens[inicio:fim]], col=12 // num_colunas)
            colunas.append(coluna)
        
        self.controls = colunas


class RotuloColuna(ft.Container):
    def __init__(self, rotulo: str, icone_path: str):
        super().__init__(
            content=ft.Row([
                ft.Image(icone_path),
                ft.Text(rotulo, size=24, weight=ft.FontWeight.BOLD)
            ]),
            col=6,
            padding=ft.padding.only(left=10)
        )
        

class TextoMonetario(ft.ResponsiveRow):
    def __init__(self, valor: str, tamanho: int, weight: str, col_text: int):
        super().__init__(
            controls=[
                ft.Text("R$", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500, col=12 - col_text),
                ft.Text(
                    valor,
                    size=tamanho,
                    weight=weight,
                    col=col_text,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS
                )
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    
    def atualizar_valor(self, valor):
        self.controls[1].value = valor
        self.controls[1].update()


class CartaoNotificacao(ft.Card):
    def __init__(self,
        titulo: str,
        subtitulo: ft.Control,
        valor: ft.Control,
        icone_path: str,
        cor_borda: str,
        botao: ft.Control=ft.Container(),
        col: int=6
    ):
        super().__init__(col=col, elevation=10)
        self.content = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Text(titulo, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500, col=10),
                    ft.Image(icone_path, width=20, height=20, color=cor_borda, col=2)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                valor,
                ft.ResponsiveRow([
                    ft.Text(subtitulo, col=12, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_300, size=13)
                ], spacing=0, alignment=ft.MainAxisAlignment.START),
                ft.ResponsiveRow([botao])
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(10),
            border=ft.Border(left=ft.BorderSide(5, cor_borda))
        )


class BotaoTonal(ft.FilledTonalButton):
    def __init__(
        self,
        label: str,
        icone_path: str,
        col: int,
        bgcolor: str=ft.Colors.BLUE_100,
        on_click: Callable=None,
        icon_color: str = ft.Colors.BLACK87,
        text_color: str = ft.Colors.BLACK87,
        visible: bool = True
    ):
        super().__init__(
            content=ft.ResponsiveRow([
                ft.Image(icone_path, col=2, width=16, height=16, color=icon_color),
                ft.Text(
                    label,
                    size=13,
                    col=9,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    color=text_color,
                    weight=ft.FontWeight.BOLD
                )
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            col=col,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            bgcolor=bgcolor,
            on_click=on_click,
            elevation=5,
            visible=visible
        )


class CartaoIndicadores(ft.Card):
    def __init__(self, rotulo: str, valor: ft.Control, col):
        super().__init__(col=col, elevation=5)
        self.content = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Text(
                        rotulo,
                        color=ft.Colors.BLACK54,
                        weight=ft.FontWeight.W_500,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ]),
                valor
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15),
        )


class CapsulaCategoria(ft.Container):
    def __init__(self, categoria):
        super().__init__()
        cores = CoresGlobal()
        self.content = ft.Text(categoria, weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        self.bgcolor=eval(f"ft.{cores.cores[categoria.lower()]}")
        self.border_radius=30
        self.col=int(len(categoria) / 2) + 1
        self.padding=ft.padding.only(left=10, top=5, right=10, bottom=5)
        self.alignment=ft.alignment.center


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
                        "categorias": {
                            "nomes": categorias
                        },
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
