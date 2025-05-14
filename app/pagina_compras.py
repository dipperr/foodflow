import flet as ft
import pandas as pd
from typing import Callable, List
import locale
from datetime import datetime

from banco_de_dados import SupabaseSingleton
from controles import InfosGlobal, ControleCompras
from componentes import (
    BotaoTonal,
    RotuloColuna,
    CartaoIndicadores,
    Filtro
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class ItemLista:
    def __init__(
        self,
        id: int,
        nome: str,
        unidade: str,
        quantidade: float,
        estoque_minimo: float,
        preco: float,
        categorias: dict,
        qtd_comprar: float = 0
    ) -> None:
        self.id = id
        self.nome = nome
        self._unidade = unidade
        self._quantidade = quantidade
        self.estoque_minimo = estoque_minimo
        self.preco = preco
        self._categorias = categorias
        self._qtd_comprar = qtd_comprar

    @property
    def categorias(self) -> str:
        if isinstance(self._categorias, dict):
            return " | ".join(self._categorias.keys())
        return self._categorias
    
    @property
    def unidade(self) -> str:
        partes = self._unidade.split(" ", 1)
        return partes[1].strip("()") if len(partes) > 1 else self._unidade
    
    @property
    def quantidade(self) -> str:
        if isinstance(self._quantidade, float):
            return str(int(self._quantidade)) if self._quantidade.is_integer() else f"{self._quantidade:.2f}".replace(".", ",")
        return str(self._quantidade)

    @property
    def quantidade_num(self) -> float:
        return self._quantidade
    
    @property
    def qtd_comprar(self) -> float:
        return self._qtd_comprar
    
    @property
    def qtd_comprar_num(self) -> float:
        return float(str(self._qtd_comprar).replace(",", "."))
    
    @qtd_comprar.setter
    def qtd_comprar(self, valor: str) -> None:
        self._qtd_comprar = valor
    
    def __eq__(self, id: int) -> bool:
        if isinstance(id, int):
            return self.id == id
        return False


class ControlePagina:
    def __init__(self, pagina) -> None:
        self.pagina = pagina

    def pagina_inicial(self) -> None:
        self.pagina.exibir_pagina_inicial()

    def pagina_inicial_e_atualizar(self) -> None:
        self.pagina.exibir_pagina_inicial_e_atualizar()


class ControleBarraNavegacao:
    def __init__(self, barra, csb) -> None:
        self.barra = barra
        self.csb = csb

    def ocultar_barra(self) -> None:
        self.barra.visible = False
        self.barra.update()
        self.csb.visibilidade(False)
    
    def mostrar_barra(self, lista) -> None:
        self.barra.mostrar_barra(lista)


class ControleBarraLista:
    def __init__(self, barra) -> None:
        self.barra = barra

    def atualizar_barra(self, lista_compras) -> None:
        self.barra.criar_conteudo(lista_compras)


class ControleListaCompras:
    def __init__(self, lista_compras: list) -> None:
        self.lista_compras = lista_compras

    def adicionar_item_lista(self, item: ItemLista, qtd: float) -> None:
        item.qtd_comprar = qtd if qtd else 0.0
        self.lista_compras.append(item)

    def remover_item(self, id: int) -> None:
        self.lista_compras.remove(id)


class ControleAlterarLista:
    def __init__(self, lista, texto) -> None:
        self.lista = lista
        self.texto = texto

    def alterar_qtd(self, item_id: int, qtd: float) -> None:
        if qtd:
            item = next((i for i in self.lista if i.id == item_id), None)
            if item:
                item.qtd_comprar = qtd
                self.alterar_valor()

    def alterar_valor(self) -> None:
        total = sum([item.preco * item.qtd_comprar_num for item in self.lista])
        self.texto.value = locale.currency(total, grouping=True)
        self.texto.update()


class CartaoListas(ft.Card):
    def __init__(self, rotulo, controle_bn, listas) -> None:
        super().__init__(elevation=5)
        self.controle_bn = controle_bn
        self.content = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Text(rotulo, weight=ft.FontWeight.BOLD, col=4, size=15)
                ]),
                ft.ResponsiveRow([
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text()),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(
                                        ft.Container(
                                            ft.ResponsiveRow([
                                                ft.Text(lista["nome"], col=6.5),
                                                ft.Column([
                                                    ft.Text("Qtd. de produtos", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text(len(lista["produtos"]), weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Valor estimado", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text(locale.currency(lista["valor_total"], grouping=True), weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Recebimento", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text(
                                                        self._obter_data_recebimento(lista["recebimento"]),
                                                        weight=ft.FontWeight.BOLD
                                                    )
                                                ], col=1.5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.all(5)
                                        )
                                    )
                                ],
                                on_select_changed=lambda e, l=lista: self.controle_bn.mostrar_barra(l)
                            )
                            for lista in listas if lista["finalizada"]
                        ],
                        heading_row_height=0,
                        column_spacing=10,
                        data_row_max_height=float("inf"),
                        horizontal_margin=0
                    )
                ])
            ]), padding=ft.padding.all(10), bgcolor=ft.Colors.WHITE, border_radius=ft.border_radius.all(15)
        )

    def _obter_data_recebimento(self, recebimento: str) -> str:
        if recebimento is not None:
            return datetime.fromisoformat(recebimento).strftime("%d-%m-%Y")
        return "-"


class LinhaTabelaProdutos(ft.DataRow):
    def __init__(self, produto: ItemLista, controle_lista: ControleListaCompras) -> None:
        super().__init__(cells=[])
        self.controle_lista = controle_lista
        self.produto = produto
        self._criar_conteudo()

    @property
    def quantidade(self) -> float:
        return self.produto.quantidade_num

    @property
    def estoque_minimo(self) -> float:
        return self.produto.estoque_minimo

    def _criar_conteudo(self) -> None:
        self._criar_entradas()
        self._criar_botoes()
        self.cells = [
            ft.DataCell(
                ft.Container(
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.Text(self.produto.nome, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Container(
                                    ft.Text(
                                        self.produto.categorias,
                                        weight=ft.FontWeight.W_600,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS
                                    ),
                                    border_radius=30,
                                    padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                    alignment=ft.alignment.center
                                )
                            ])
                        ], col=4.1),
                        self.cartao_quantidade,
                        ft.Column([
                            ft.ResponsiveRow([
                                self.botao_add,
                                self.botao_remove
                            ]),

                        ], col=2.3),
                        ft.Column([
                            ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                            ft.Text(
                                self.produto.quantidade,
                                weight=ft.FontWeight.BOLD
                            )
                        ], col=1.8),
                        ft.Column([
                            ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                            ft.Text(self.produto.estoque_minimo, weight=ft.FontWeight.BOLD)
                        ], col=1.8)
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                    padding=ft.padding.all(10)
                )
            )
        ]

    def _criar_entradas(self) -> None:
        self.qtd_comprar = ft.TextField(
            height=30,
            col=6, 
            cursor_height=13,
            content_padding=ft.padding.only(top=0, left=10),
            border_color=ft.Colors.BLACK54,
            cursor_color=ft.Colors.BLACK54
        )
        self.cartao_quantidade = ft.Container(
            ft.Column([
                ft.Text("Comprar", color=ft.Colors.BLACK54, size=13, max_lines=1, overflow=ft.TextOverflow),
                ft.ResponsiveRow([
                    self.qtd_comprar,
                    ft.Text(
                        self.produto.unidade,
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        col=4
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            col=2,
            bgcolor=ft.Colors.BLUE_100,
            border_radius=5,
            padding=ft.padding.all(5),
            border=ft.border.all(1, ft.Colors.BLUE)
        )

    def _criar_botoes(self) -> None:
        self.botao_add = BotaoTonal(
            "Adicionar à lista",
            "./icons_clone/shopping-basket.png",
            12,
            on_click=self.adicionar_item_lista
        )
        self.botao_remove = BotaoTonal(
            "Excluir",
            "./icons_clone/trash.png",
            12,
            bgcolor=ft.Colors.WHITE,
            text_color=ft.Colors.RED,
            icon_color=ft.Colors.RED,
            on_click=self.remover_item_lista,
            visible=False
        )

    def adicionar_item_lista(self, e: ft.ControlEvent) -> None:
        self.controle_lista.adicionar_item_lista(self.produto, self.qtd_comprar.value)
        self.visibilidade_elementos(False)

    def remover_item_lista(self, e: ft.ControlEvent) -> None:
        self.controle_lista.remover_item(self.produto.id)
        self.visibilidade_elementos(True)

    def visibilidade_elementos(self, visibilidade: bool) -> None:
        elementos = [
            (self.cartao_quantidade, visibilidade),
            (self.botao_add, visibilidade),
            (self.botao_remove, not visibilidade),
        ]

        for elemento, visivel in elementos:
            elemento.visible = visivel
            elemento.update()
        

class FiltrosEstoque(ft.ResponsiveRow):
    def __init__(self) -> None:
        super().__init__(
            controls=[
                Filtro(
                    "Filtrar categoria(s)",
                    []
                ),
                Filtro(
                    "Filtrar fornecedor(es)",
                    []
                ),
                Filtro(
                    "Filtrar por produtos(s)",
                    []
                ),
            ]
        )


class CartaoListaCompras(ft.Card):
    def __init__(self, item, controle_alterar_lista) -> None:
        super().__init__(col=12, elevation=5)
        self.controle_alterar_lista = controle_alterar_lista
        self.item = item
        self._criar_entrada(item)
        self.content = ft.Container(
            ft.ResponsiveRow([
                ft.Column([
                    ft.Text(item.nome, size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Container(
                            ft.Text(item.categorias, weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            border_radius=30,
                            padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                            alignment=ft.alignment.center
                        )
                    ]),
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, size=13, weight=ft.FontWeight.W_400),
                            ft.Text(item.quantidade, weight=ft.FontWeight.BOLD)
                        ], col=6, spacing=5),
                        ft.Column([
                            ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, size=13, weight=ft.FontWeight.W_400),
                            ft.Text(item.estoque_minimo, weight=ft.FontWeight.BOLD)
                        ], col=6, spacing=5)
                    ])
                ], col=8),
                ft.Column([
                    ft.Container(
                        ft.Column([
                            ft.Text("Comprar"),
                            ft.ResponsiveRow([
                                self.qtd,
                                ft.Text(item.unidade, size=13, weight=ft.FontWeight.BOLD, col=4)
                            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        expand=True,
                        bgcolor=ft.Colors.BLUE_100,
                        border_radius=5,
                        padding=ft.padding.all(7),
                        border=ft.border.all(1, ft.Colors.BLUE),
                    )
                ], col=4)
            ]),
            bgcolor=ft.Colors.WHITE,
            padding=ft.padding.all(20),
            border_radius=15
        )
    def alterar_qtd(self, e: ft.ControlEvent) -> None:
        self.controle_alterar_lista.alterar_qtd(self.item.id, self.qtd.value)

    def _criar_entrada(self, item) -> None:
        self.qtd = ft.TextField(
            value=item.qtd_comprar,
            height=30,
            col=6, 
            cursor_height=13,
            content_padding=ft.padding.only(top=0, left=10),
            border_color=ft.Colors.BLACK54,
            cursor_color=ft.Colors.BLACK54,
            on_change=self.alterar_qtd
        )


class JanelaSalvarLista(ft.AlertDialog):
    def __init__(self, lista_compras, controle_compras) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.lista_compras = lista_compras
        self.controle_compras = controle_compras
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self.criar_botoes()
        self._criar_entradas()
        
        self.content = ft.Container(
            ft.Column([
                ft.Column([
                    ft.Text("NOME DA LISTA", weight=ft.FontWeight.W_500),
                    self.entrada_nome
                ]),
                ft.Column([
                    ft.ResponsiveRow([
                        self.botao_cancelar,
                        self.botao_salvar
                    ], alignment=ft.MainAxisAlignment.END)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=500,
            height=150
        )

    def _criar_entradas(self) -> None:
        self.entrada_nome = ft.TextField(
            cursor_color=ft.Colors.BLACK54,
            border_radius=10,
            border_color=ft.Colors.BLACK54,
            width=490,
            content_padding=ft.padding.only(top=0, left=10),
            text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
            label_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
            on_change=self.alterar_status_botao
        )

    def criar_botoes(self) -> None:
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=3,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.botao_salvar = ft.OutlinedButton(
            "SALVAR LISTA",
            col=4,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            ),
            disabled=True,
            on_click=self.salvar
        )

    def alterar_status_botao(self, e: ft.ControlEvent) -> None:
        self.botao_salvar.disabled = not bool(self.entrada_nome.value)
        self.botao_salvar.update()

    def salvar(self, e: ft.ControlEvent) -> None:
        self.page.close(self)
        self.controle_compras.salvar_lista(self.entrada_nome.value, self.lista_compras)
        

class BarraListaCompras(ft.Container):
    def __init__(self, controle_sombra, controle_pagina) -> None:
        super().__init__(
            expand=True,
            bgcolor=ft.Colors.BLACK26,
            visible=False
        )
        self.controle_sombra = controle_sombra
        self.controle_pagina = controle_pagina

    def criar_conteudo(self, lista_compras) -> None:
        self.lista_compras = lista_compras
        self.content = ft.ResponsiveRow([
            ft.Container(
                ft.Column([
                    ft.Container(
                        ft.Column([
                            ft.Container(
                                ft.Column([
                                    ft.ResponsiveRow([
                                        ft.Text("Sua lista de compras", weight=ft.FontWeight.BOLD, size=18, col=11),
                                        ft.TextButton(
                                            "X",
                                            col=1,
                                            style=ft.ButtonStyle(
                                                text_style=ft.TextStyle(
                                                    foreground=ft.Paint(color=ft.Colors.BLACK87),
                                                    weight=ft.FontWeight.BOLD,
                                                    size=18
                                                )
                                            ),
                                            on_click=self.ocultar_barra
                                        )
                                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    ft.Divider(),
                                    self.criar_lista()
                                ], spacing=20),
                                bgcolor=ft.Colors.GREY_100,
                                padding=ft.padding.all(20),
                            )
                        ], scroll=ft.ScrollMode.ALWAYS),
                        expand=True)
                ]),
                col=6,
                expand=True,
                bgcolor=ft.Colors.GREY_100,
            )
        ], alignment=ft.MainAxisAlignment.END)
        self.update()

    def criar_lista(self) -> List:
        if len(self.lista_compras) > 0:
            self.texto_valor = ft.Text(
                locale.currency(self.calcular_valor_total(), grouping=True),
                weight=ft.FontWeight.BOLD
            )
            return ft.Column([
                ft.Column([
                    ft.Text(f"{len(self.lista_compras)} produto(s)", weight=ft.FontWeight.BOLD),
                    self.texto_valor
                ]),
                ft.ResponsiveRow([
                    BotaoTonal(
                        "Salvar Lista",
                        "./icons_clone/disk.png",
                        6,
                        on_click=self.salvar_lista
                    ),
                    BotaoTonal(
                        "Exportar",
                        "./icons_clone/file-export.png",
                        6
                    ),
                    ft.ResponsiveRow([
                        CartaoListaCompras(
                            item,
                            ControleAlterarLista(self.lista_compras, self.texto_valor)
                        )
                        for item in self.lista_compras
                    ])
                ], run_spacing=20)
            ])
        return ft.Column([
            ft.Text("Sua lista está vazia")
        ])
    
    def calcular_valor_total(self) -> float:
        return sum([item.preco * item.qtd_comprar_num for item in self.lista_compras])

    def mostrar_barra(self, lista_compras) -> None:
        self.criar_conteudo(lista_compras)
        self.visible = True
        self.update()
        self.controle_sombra.visibilidade(True)

    def ocultar_barra(self, e: ft.ControlEvent) -> None:
        self.controle_sombra.visibilidade(False)
        self.visible = False
        self.update()

    def salvar_lista(self, e: ft.ControlEvent) -> None:
        janela = JanelaSalvarLista(self.lista_compras, ControleCompras(self.controle_pagina))
        self.ocultar_barra(None)
        self.page.open(janela)


class PainelListaCompras(ft.Stack):
    def __init__(self, controle_pagina, controle_sombra) -> None:
        super().__init__()
        self.controle_pagina = controle_pagina
        self.controle_sombra = controle_sombra
        self.lista_compras = []

    def _criar_conteudo(self) -> None:
        self.expand = False
        self._criar_barra_lista_compras()
        self._criar_tabela_produtos()
        self.controls = [
            ft.Column([
                ft.Container(
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.ResponsiveRow([
                                ft.Column([
                                    ft.IconButton(
                                        content=ft.Image("./icons_clone/arrow-left.png"),
                                        on_click=self.ir_pagina_inicial
                                    ),
                                    ft.Text("Nova lista de compras", size=24, weight=ft.FontWeight.BOLD)
                                ], col=9),
                                ft.Column([
                                    ft.FilledTonalButton(
                                        content=ft.Container(
                                            ft.ResponsiveRow([
                                                ft.Image("./icons_clone/shopping-basket.png", height=16, width=16, col=3),
                                                ft.Column([
                                                    ft.Text("LISTA DE COMPRAS")
                                                ], col=9, spacing=5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.only(top=10, bottom=10, left=0, right=0)
                                        ),
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(5)),
                                        bgcolor=ft.Colors.GREEN,
                                        on_click=self.visualizar_barra_lista_compra
                                    )
                                ], col=3, alignment=ft.MainAxisAlignment.END)
                            ], vertical_alignment=ft.CrossAxisAlignment.END),
                            ft.Divider(),
                            ft.Container(
                                ft.Column([
                                    ft.Text("Selecionar produtos", size=17, weight=ft.FontWeight.BOLD),
                                    ft.Text("Selecione os produtos que deseja adicionar à lista de compras.", size=14, color=ft.Colors.BLACK54)
                                ], spacing=5) 
                            ),
                            ft.Divider(),
                            FiltrosEstoque(),
                            ft.ResponsiveRow([
                                ft.Card(
                                    ft.Container(
                                        ft.Column([
                                            ft.ResponsiveRow([
                                                ft.Row([
                                                    ft.Switch(
                                                        label="Visualizar apenas produtos abaixo do estoque mínimo",
                                                        height=30,
                                                        on_change=self.produtos_abaixo_estoque
                                                    )
                                                ], col=9)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            ft.Container(
                                                ft.ResponsiveRow([
                                                    self.tabela_produtos
                                                ])
                                            )
                                        ]), padding=ft.padding.all(20), bgcolor=ft.Colors.WHITE, border_radius=15
                                    ), col=12
                                )
                            ])
                        ], col=12)
                    ]), padding=ft.padding.all(20)
                )
            ], scroll=ft.ScrollMode.ALWAYS),
            self.barra_lista_compras
        ]
        self.update()

    def placeholder(self) -> None:
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _criar_tabela_produtos(self) -> None:
        produtos = self.ler_produtos()
        self.tabela_produtos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text()),
            ],
            rows=[
                LinhaTabelaProdutos(
                    ItemLista(
                        produto["id"],
                        produto["nome"],
                        produto["unidade"],
                        produto["quantidade"],
                        produto["estoque_minimo"],
                        produto["preco_unidade"],
                        produto["categorias"]
                    ),
                    ControleListaCompras(self.lista_compras)
                )
                for produto in produtos
            ],
            heading_row_height=0,
            column_spacing=10,
            data_row_max_height=float("inf"),
            horizontal_margin=0
        )

    def produtos_abaixo_estoque(self, e: ft.ControlEvent) -> None:
        filtrar = e.data == "true"
        for row in self.tabela_produtos.rows:
            row.visible = (row.quantidade < row.estoque_minimo) if filtrar else True
            row.update()

    def _criar_barra_lista_compras(self) -> None:
        self.barra_lista_compras = BarraListaCompras(self.controle_sombra, self.controle_pagina)

    def visualizar_barra_lista_compra(self, e: ft.ControlEvent) -> None:
        self.barra_lista_compras.mostrar_barra(self.lista_compras)

    def ir_pagina_inicial(self, e: ft.ControlEvent) -> None:
        self.controle_pagina.pagina_inicial()

    def ler_produtos(self) -> None:
        try:
            cliente = SupabaseSingleton().get_client()
            produtos = (
                cliente.table("produtos")
                .select("id, nome, unidade, quantidade, estoque_minimo, categorias, preco_unidade")
                .execute()
            ).data
        except Exception as e:
            return []
        else:
            return produtos

    def did_mount(self) -> None:
        self.placeholder()
        self._criar_conteudo()


class JanelaConfimarRecebimento(ft.AlertDialog):
    def __init__(self, lista_id, produtos, controle_compras) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.lista_id = lista_id
        self.produtos = produtos
        self.controle_compras = controle_compras
        self.opcao_selecionada = None
        self._criar_conteudo()
        
    def _criar_conteudo(self) -> None:
        self.criar_botoes()
        self._criar_opcoes()
        self.content = ft.Container(
            ft.Column([
                ft.Column([
                    ft.Text("Confirmar recebimento", weight=ft.FontWeight.BOLD, size=20),
                    ft.Divider(),
                    ft.Text("Selecione a opção desejada:", weight=ft.FontWeight.W_500),
                    ft.ResponsiveRow(self.opcoes)
                ]),
                ft.ResponsiveRow([
                    self.botao_cancelar,
                    self.botao_continuar
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=20),
            width=500,
            height=300
        )

    def criar_botoes(self) -> None:
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=3,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.botao_continuar = ft.OutlinedButton(
            "CONTINUAR",
            col=4,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            ),
            disabled=True,
            on_click=self.salvar
        )

    def _criar_opcoes(self) -> None:
        def criar_container(titulo: str, descricao: str, opcao: int) -> ft.Container:
            return ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Text(titulo, weight=ft.FontWeight.BOLD),
                        ft.Text(descricao, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK54)
                    ])
                ]),
                padding=ft.padding.all(10),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(10),
                col=12,
                border=ft.border.all(1, ft.Colors.BLACK12),
                ink=True,
                on_click=lambda e: self.selecionar_opcao(opcao)
            )
        
        self.opcoes = [
            criar_container(
                "Confirmar recebimento com entrada no estoque",
                "Revise a lista de compras e dê entrada dos produtos em estoque",
                0
            ),
            criar_container(
                "Confirmar recebimento sem entrada no estoque",
                "Finalize a lista de compras sem dar entrada dos produtos em estoque",
                1
            )
        ]

    def selecionar_opcao(self, opcao: int) -> None:
        if self.botao_continuar.disabled:
            self.botao_continuar.disabled = False
            self.botao_continuar.update()

        for i, op in enumerate(self.opcoes):
            op.bgcolor = ft.Colors.BLUE_100 if i == opcao else ft.Colors.WHITE
            op.update()
        self.opcao_selecionada = opcao

    def salvar(self, e: ft.ControlEvent) -> None:
        self.page.close(self)
        self.controle_compras.atualizar_status(
            self.lista_id,
            self.produtos,
            self.opcao_selecionada
        )


class BarraNavegacaoLA(ft.Container):
    def __init__(self, controle_sombra, controle_pagina) -> None:
        super().__init__(
            expand=True,
            bgcolor=ft.Colors.BLACK26,
            visible=False
        )
        self.controle_sombra = controle_sombra
        self.controle_pagina = controle_pagina
        self.lista_id = None
        self.lista_produtos = None

    def criar_conteudo(self, lista: dict) -> None:
        self.lista_id = lista["id"]
        self.lista_produtos = [
            ItemLista(
                infos["id"],
                nome,
                infos["unidade"],
                infos["quantidade"],
                infos["estoque_minimo"],
                infos["preco"],
                infos["categorias"],
                infos["qtd_comprar"]
            )
            for nome, infos in lista["produtos"].items()
        ]
        self.texto_valor = ft.Text(locale.currency(lista["valor_total"], grouping=True), weight=ft.FontWeight.BOLD)
        self.content = ft.ResponsiveRow([
            ft.Container(
                ft.Column([
                    ft.Container(
                        ft.Column([
                            ft.Container(
                                ft.Column([
                                    ft.ResponsiveRow([
                                        ft.Text(lista["nome"], weight=ft.FontWeight.BOLD, size=18, col=11),
                                        ft.TextButton(
                                            "X",
                                            col=1,
                                            style=ft.ButtonStyle(
                                                text_style=ft.TextStyle(
                                                    foreground=ft.Paint(color=ft.Colors.BLACK87),
                                                    weight=ft.FontWeight.BOLD,
                                                    size=18
                                                )
                                            ),
                                            on_click=self.ocultar_barra
                                        )
                                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    ft.Divider(),
                                    ft.Column([
                                        ft.Text(f"{len(lista["produtos"])} produto(s)", weight=ft.FontWeight.BOLD),
                                        self.texto_valor
                                    ]),
                                    ft.ResponsiveRow([
                                        ft.Card(
                                            ft.Container(
                                                ft.Column([
                                                    ft.ResponsiveRow([
                                                        ft.Column([
                                                            ft.Text("Status:", weight=ft.FontWeight.BOLD),
                                                            ft.Text("Aguardando Recebimento", weight=ft.FontWeight.W_600)
                                                        ], spacing=5, col=6)
                                                    ]),
                                                    ft.Divider(),
                                                    ft.ResponsiveRow([
                                                        BotaoTonal(
                                                            "Confirmar Recebimento",
                                                            "./icons_clone/box-circle-check.png",
                                                            6,
                                                            ft.Colors.GREEN,
                                                            on_click=self.confirmar_recebimento
                                                        )
                                                    ])
                                                ]),
                                                padding=ft.padding.all(20)
                                            ), elevation=5, col=12
                                        ),
                                        BotaoTonal(
                                            "Exportar",
                                            "./icons_clone/file-export.png",
                                            6
                                        ),
                                        BotaoTonal(
                                            "Excluir Lista",
                                            "./icons_clone/trash.png",
                                            6,
                                            ft.Colors.WHITE,
                                            icon_color=ft.Colors.RED,
                                            text_color=ft.Colors.RED
                                        ),
                                        ft.ResponsiveRow([
                                            CartaoListaCompras(
                                                item,
                                                ControleAlterarLista(self.lista_produtos, self.texto_valor)
                                            )
                                            for item in self.lista_produtos
                                        ])
                                    ], run_spacing=20)
                                ]),
                                bgcolor=ft.Colors.GREY_100,
                                padding=ft.padding.all(20),
                            )
                        ], scroll=ft.ScrollMode.ALWAYS),
                        expand=True
                    )
                ]),
                col=7,
                expand=True,
                bgcolor=ft.Colors.GREY_100,
            )
        ], alignment=ft.MainAxisAlignment.END)

    def ocultar_barra(self, e: ft.ControlEvent) -> None:
        self.controle_sombra.visibilidade(False)
        self.visible = False
        self.update()

    def mostrar_barra(self, lista: dict) -> None:
        self.controle_sombra.visibilidade(True)
        self.criar_conteudo(lista)
        self.visible = True
        self.update()

    def confirmar_recebimento(self, e: ft.ControlEvent) -> None:
        self.ocultar_barra(None)
        janela = JanelaConfimarRecebimento(
            self.lista_id,
            self.lista_produtos,
            ControleCompras(self.controle_pagina)
        )
        self.page.open(janela)
        

class BarraNavegacaoLF(ft.Container):
    def __init__(self, controle_sombra, controle_pagina) -> None:
        super().__init__(
            expand=True,
            bgcolor=ft.Colors.BLACK26,
            visible=False
        )
        self.controle_sombra = controle_sombra
        self.controle_pagina = controle_pagina
        self.lista_produtos = None

    def criar_conteudo(self, lista: dict) -> None:
        self.lista_produtos = [
            ItemLista(
                infos["id"],
                nome,
                infos["unidade"],
                infos["quantidade"],
                infos["estoque_minimo"],
                infos["preco"],
                infos["categorias"],
                infos["qtd_comprar"]
            )
            for nome, infos in lista["produtos"].items()
        ]
        self.content = ft.ResponsiveRow([
            ft.Container(
                ft.Column([
                    ft.Container(
                        ft.Column([
                            ft.Container(
                                ft.Column([
                                    ft.ResponsiveRow([
                                        ft.Text(lista["nome"], weight=ft.FontWeight.BOLD, size=18, col=11),
                                        ft.TextButton(
                                            "X",
                                            col=1,
                                            style=ft.ButtonStyle(
                                                text_style=ft.TextStyle(
                                                    foreground=ft.Paint(color=ft.Colors.BLACK87),
                                                    weight=ft.FontWeight.BOLD,
                                                    size=18
                                                )
                                            ),
                                            on_click=self.ocultar_barra
                                        )
                                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                    ft.Divider(),
                                    ft.Column([
                                        ft.Text(f"{len(lista["produtos"])} produto(s)", weight=ft.FontWeight.BOLD),
                                        ft.Text(locale.currency(lista["valor_total"], grouping=True), weight=ft.FontWeight.BOLD)
                                    ]),
                                    ft.ResponsiveRow([
                                        ft.Card(
                                            ft.Container(
                                                ft.Column([
                                                    ft.Text("Status:", weight=ft.FontWeight.BOLD),
                                                    ft.Text("Recebido", weight=ft.FontWeight.W_600)
                                                ], spacing=5), padding=ft.padding.all(20)
                                            ), elevation=5, col=12
                                        )
                                    ]),
                                    ft.Text("Produtos:", size=17, weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54),
                                    ft.ResponsiveRow([
                                        ft.Card(
                                            ft.Container(
                                                ft.DataTable(
                                                    columns=[
                                                        ft.DataColumn(ft.Text()),
                                                    ],
                                                    rows=[
                                                        ft.DataRow(
                                                            cells=[
                                                                ft.DataCell(
                                                                    ft.Container(
                                                                        ft.ResponsiveRow([
                                                                            ft.Column([
                                                                                ft.Row([
                                                                                    ft.Text(item.nome, weight=ft.FontWeight.BOLD)
                                                                                ])
                                                                            ], col=7),
                                                                            ft.Column([
                                                                                ft.Text("Quantidade", size=13,  weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54),
                                                                                ft.Text(item.quantidade, size=13, weight=ft.FontWeight.BOLD)
                                                                            ], col=2.5, spacing=5),
                                                                            ft.Column([
                                                                                ft.Text("Preço unit.", size=13,  weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54),
                                                                                ft.Text(locale.currency(item.preco, grouping=True), size=13, weight=ft.FontWeight.BOLD)
                                                                            ], col=2.5, spacing=5)
                                                                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                                                                        padding=ft.padding.only(left=5, top=10, right=5, bottom=5)
                                                                    )
                                                                )
                                                            ]
                                                        )
                                                        for item in self.lista_produtos
                                                    ],
                                                    heading_row_height=0,
                                                    column_spacing=10,
                                                    data_row_max_height=float("inf"),
                                                    horizontal_margin=0
                                                ), padding=ft.padding.all(20), bgcolor=ft.Colors.WHITE, border_radius=15
                                            )
                                        )
                                    ])
                                ]),
                                bgcolor=ft.Colors.GREY_100,
                                padding=ft.padding.all(20),
                            )
                        ], scroll=ft.ScrollMode.ALWAYS),
                        expand=True
                    )
                ]),
                col=7,
                expand=True,
                bgcolor=ft.Colors.GREY_100,
            )
        ], alignment=ft.MainAxisAlignment.END)

    def ocultar_barra(self, e: ft.ControlEvent) -> None:
        self.controle_sombra.visibilidade(False)
        self.visible = False
        self.update()

    def mostrar_barra(self, lista: dict) -> None:
        self.controle_sombra.visibilidade(True)
        self.criar_conteudo(lista)
        self.visible = True
        self.update()


class PaginaCompras(ft.Stack):
    def __init__(self, controle_sombra) -> None:
        super().__init__()
        self.controle_sombra = controle_sombra

    def _criar_conteudo(self) -> None:
        self.expand = False
        self._criar_barra_navegacao_lf()
        self._criar_barra_navegacao_la()

        cartoes_indicadores = self._criar_cartoes_indicadores()

        self.area = ft.Column([
            ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        RotuloColuna("Compras", "./icons_clone/shopping-basket.png"),
                        ft.ResponsiveRow(cartoes_indicadores),
                        ft.ResponsiveRow([
                            BotaoTonal(
                                "Criar Lista de Compras",
                                "./icons_clone/add-document.png",
                                3,
                            on_click=self.exibir_pagina_lista
                            ),
                            BotaoTonal("Gerenciar Fornecedores", "./icons_clone/shop.png", 3)
                        ]),
                        CartaoListas("Listas em andamento", self.controle_bn_la, self.listas_compras),
                        CartaoListas("Listas finalizadas", self.controle_bn_lf, self.listas_compras)
                    ], col=12, spacing=20)
                ]),
                padding=ft.padding.all(20)
            )
        ], scroll=ft.ScrollMode.ALWAYS)

        self.pagina_inicial = [
            self.area,
            self.barra_navegacao_lf,
            self.barra_navegacao_la
        ]
        
        self.controls = self.pagina_inicial
        self.update()

    def _criar_barra_navegacao_lf(self) -> None:
        self.barra_navegacao_lf = BarraNavegacaoLF(self.controle_sombra, ControlePagina(self))
        self.controle_bn_lf = ControleBarraNavegacao(self.barra_navegacao_lf, self.controle_sombra)

    def _criar_barra_navegacao_la(self) -> None:
        self.barra_navegacao_la = BarraNavegacaoLA(self.controle_sombra, ControlePagina(self))
        self.controle_bn_la = ControleBarraNavegacao(self.barra_navegacao_la, self.controle_sombra)

    def placeholder(self) -> None:
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _criar_cartoes_indicadores(self) -> List[CartaoIndicadores]:
        dados = self.ler_dados_produtos()
        if len(dados) > 0:
            estoque_baixo = len(dados[dados['quantidade'] < dados['estoque_minimo']])
            estoque_critico = len(dados[dados['quantidade'] < (dados["estoque_minimo"] * 0.2)])
            estoque_zero = len(dados[dados["quantidade"] == 0])
        else:
            estoque_baixo = estoque_critico = estoque_zero = 0
        
        return [
            CartaoIndicadores(
                "Produtos abaixo do estoque mínimo",
                ft.Row([ft.Text(estoque_baixo, size=20, weight=ft.FontWeight.BOLD)]),
                4
            ),
            CartaoIndicadores(
                "Produtos com estoque crítico",
                ft.Row([ft.Text(estoque_critico, size=20, weight=ft.FontWeight.BOLD)]),
                4
            ),
            CartaoIndicadores(
                "Produtos sem estoque",
                ft.Row([ft.Text(estoque_zero, size=20, weight=ft.FontWeight.BOLD)]),
                4
            )
        ]

    def exibir_pagina_lista(self, e: ft.ControlEvent) -> None:
        self.controls = [PainelListaCompras(ControlePagina(self), self.controle_sombra)]
        self.update()

    def exibir_pagina_inicial(self) -> None:
        self.controls = self.pagina_inicial
        self.update()

    def exibir_pagina_inicial_e_atualizar(self) -> None:
        self.controls = self.pagina_inicial
        self.ler_dados_listas()

    def visualizacao_barra_lf(self, e: ft.ControlEvent) -> None:
        self.controle_bn_lf.ocultar_barra()

    def ler_dados_produtos(self) -> pd.DataFrame:
        try:
            cliente = SupabaseSingleton().get_client()
            resposta = (
                cliente.table("produtos")
                .select("quantidade, estoque_minimo")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
        except Exception as e:
            return pd.DataFrame([])
        else:
            return pd.DataFrame(resposta)
        
    def ler_dados_listas(self) -> None:
        try:
            cliente = SupabaseSingleton().get_client()
            listas = (
                cliente.table("lista_compras")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self.listas_compras = listas
            self._criar_conteudo()

    def did_mount(self) -> None:
        self.placeholder()
        self.ler_dados_listas()
