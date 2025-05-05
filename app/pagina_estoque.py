import flet as ft
from typing import Callable, List, Optional, Union
import locale
import pandas as pd
from datetime import datetime
from dateutil import parser

from banco_de_dados import SupabaseSingleton
from modelos import (
    Produto,
    Movimentacao,
    UNIDADES
)
from controles import (
    ControleProduto,
    ControleCategoria,
    ControleFornecedores,
    ControleMovimentacao,
    InfosGlobal
)
from componentes import (
    RotuloColuna,
    TextoMonetario,
    GradeNotificacao,
    CartaoNotificacao,
    BotaoTonal,
    CartaoIndicadores,
    CapsulaCategoria,
    TextField,
    Filtro
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


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
                    "Filtrar por alerta(s)",
                    []
                ),
                Filtro(
                    "Compõe CMV?",
                    ["Sim", "Não"],
                    mostrar_botao=self.mostrar_botao
                ),
                Filtro(
                    "Ordenar por:",
                    [
                        "Alfabética (crescente)",
                        "Alfabética (decrescente)",
                        "Preço unit. (crescente)",
                        "Preço unit. (decrescente)",
                        "Valor do estoque (crescente)",
                        "Valor do estoque (decrescente)"
                    ],
                    checked=0
                ),
                ft.FilledTonalButton(
                    content=ft.ResponsiveRow([
                        ft.Image("./icons_clone/clear-alt.png", width=16, height=16, col=3),
                        ft.Text("Limpar filtros", col=9)
                    ]),
                    col=3,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(5), padding=ft.padding.all(15)),
                    visible=False,
                    on_click=self.limpar_filtros
                )
            ]
        )

    def limpar_filtros(self, e: ft.ControlEvent) -> None:
        for filtro in self.controls[:-2]:
            filtro.limpar()
        self.controls[-1].visible = False
        self.controls[-1].update()

    def mostrar_botao(self) -> None:
        self.controls[-1].visible = True
        self.controls[-1].update()


class OperadorProduto:
    def __init__(self, produto: Produto) -> None:
        self.produto = produto
    
    def formatar_valores(self) -> None:
        preco = 0.0 if pd.isnull(self.produto.preco) else self.produto.preco
        valor_estoque = preco * self.produto.qtd_estoque
        qtd_estoque = self._formatar_quantidade(self.produto.qtd_estoque)
        estoque_min = self._formatar_quantidade(self.produto.estoque_min)
        return preco, valor_estoque, qtd_estoque, estoque_min
    
    def _formatar_quantidade(self, qtd: Union[int, float]) -> str:
        if isinstance(qtd, float) and qtd.is_integer():
            qtd = int(qtd)
        qtd_str = str(qtd).replace(".", ",")

        try:
            unidade = self.produto.unidade.split(" ")[1].strip("()")
        except (IndexError, AttributeError):
            unidade = ""
        return f"{qtd_str} {unidade}"

    def obter_categorias(self) -> None:
        categorias = getattr(self.produto, "categorias", None)
        if isinstance(categorias, dict) and categorias:
            return ft.Row([CapsulaCategoria(cat, cor) for cat, cor in categorias.items()])
        return ft.Row([])
        
    def obter_fornecedores(self) -> None:
        fornecedores = getattr(self.produto, "fornecedores", None)
        nomes = fornecedores.get("nomes") if isinstance(fornecedores, dict) else None
        if isinstance(nomes, list) and nomes:
            texto = " | ".join(f.upper() for f in nomes)
            return ft.ResponsiveRow([ft.Text(texto, col=12, size=13)])
        return ft.ResponsiveRow([])


class PainelInfos(ft.Container):
    def __init__(self, controle_sombra) -> None:
        super().__init__(
            expand=True,
            visible=False,
            bgcolor=ft.Colors.GREY_100
        )
        self.controle_sombra = controle_sombra
        self.produto = None
        self.janela = None

    def criar_conteudo(self) -> None:
        op = OperadorProduto(self.produto)
        preco, valor_estoque, qtd_estoque, estoque_min = op.formatar_valores()
        self.content = ft.Column([
            ft.Container(
                ft.Column([
                    ft.Container(
                        ft.ResponsiveRow([
                            ft.IconButton(
                                content=ft.Image("./icons_clone/arrow-left.png"),
                                on_click=self.fechar_janela,
                                col=0.7
                            ),
                            ft.Text(self.produto.nome.title(), col=12, size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            op.obter_fornecedores(),
                            op.obter_categorias(),
                            self._cartoes(qtd_estoque, estoque_min, preco, valor_estoque),
                            ft.Divider(),
                            self._criar_botoes(),
                            ft.ResponsiveRow([ft.Text("Movimentações e Históricos", col=12, color=ft.Colors.BLACK54)]),
                            self._movimentacoes()
                        ]), bgcolor=ft.Colors.GREY_100, expand=True, padding=ft.padding.all(20),
                    )
                ], scroll=ft.ScrollMode.ALWAYS),
            expand=True)
        ])
        self.update()

    def _criar_botoes(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow([
            BotaoTonal(
                "Registrar Movimentação",
                "./icons_clone/exchange.png",
                3,
                on_click=self._registrar_movimentacao
            ),
            BotaoTonal(
                "Editar Produto",
                "./icons_clone/pencil.png",
                3,
                on_click=self._editar_produto
            ),
            BotaoTonal(
                "Excluir",
                "./icons_clone/trash.png",
                2,
                ft.Colors.WHITE,
                icon_color=ft.Colors.RED,
                text_color=ft.Colors.RED
            )
        ])

    def _registrar_movimentacao(self, e: ft.ControlEvent) -> None:
        controle = ControleMovimentacao(self)
        self.janela = JanelaRegistrarMovimentacao(self.produto, controle)
        self.page.open(self.janela)

    def _editar_produto(self, e: ft.ControlEvent) -> None:
        controle = ControleProduto(visualizacao=self)
        self.janela = JanelaEditarProduto(self.produto, controle)
        self.page.open(self.janela)

    def _cartoes(
        self,
        qtd_estoque: float,
        estoque_min: float,
        preco: float,
        valor_estoque: float
    ) -> ft.ResponsiveRow:
        return ft.ResponsiveRow([
            CartaoIndicadores(
                "Quantidade",
                ft.Row([
                    ft.Text(qtd_estoque, size=20, weight=ft.FontWeight.BOLD)
                ]),
                3
            ),
            CartaoIndicadores(
                "Estoque mínimo",
                ft.Row([
                    ft.Text(estoque_min, size=20, weight=ft.FontWeight.BOLD)
                ]),
                3
            ),
            CartaoIndicadores(
                "Preço unitário",
                ft.Row([
                    ft.Text(
                        locale.currency(preco, grouping=True),
                        size=20,
                        weight=ft.FontWeight.BOLD
                    )
                ]),
                3
            ),
            CartaoIndicadores(
                "Valor do estoque",
                ft.Row([
                    ft.Text(
                        locale.currency(valor_estoque, grouping=True),
                        size=20,
                        weight=ft.FontWeight.BOLD
                    )
                ]),
                3
            ),
            CartaoIndicadores(
                "Unidade(s)",
                ft.ResponsiveRow([
                    ft.Text(
                        "Este produto pode ser movimentado em ",
                        spans=[
                            ft.TextSpan(
                                self.produto.unidade,
                                style=ft.TextStyle(
                                    weight=ft.FontWeight.BOLD
                                )
                            )
                        ],
                        weight=ft.FontWeight.W_600,
                        col=12
                    )
                ]),
                6
            ),
            CartaoIndicadores(
                "Lotes com validade",
                ft.Column([
                    ft.ResponsiveRow([ft.Text("Nenhum lote cadastrados", weight=ft.FontWeight.W_600, col=12)]),
                    ft.ResponsiveRow([
                        BotaoTonal("Cadastrar Lote", "./icons_clone/calendar-plus16.png", 4)
                    ])
                ]),
                6
            )
        ])

    def _movimentacoes(self) -> None:
        try:
            client = SupabaseSingleton().get_client()
            respostas = (
                client.table("movimentacao")
                .select("*")
                .eq("id_produto", self.produto.id)
                .order("data_movimentacao", desc=True)
                .execute()
            ).data
        except Exception as e:
            print(e)
            return ft.ResponsiveRow([])
        else:
            respostas_form = [
                [
                    mov["id"],
                    mov["operacao"],
                    mov["classificacao"],
                    parser.isoparse(mov["data_movimentacao"]),
                    self.produto.nome,
                    mov["quantidade"],
                    self.produto.unidade,
                    self.obter_preco(mov["preco_movimentacao"]),
                    mov["informacoes"]
                ]
                for mov in respostas
            ]

            return ft.ResponsiveRow([
                ft.Card(
                    ft.Container(
                        ft.Column([
                            LinhaHistorico(*dado)
                            for dado in respostas_form
                        ]),
                        padding=ft.padding.symmetric(vertical=10, horizontal=0),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=ft.border_radius.all(15),
                    ), col=12
                )
            ])
    
    def obter_preco(self, preco_mov: Optional[float]) -> float:
        return preco_mov if pd.notna(preco_mov) else self.produto.preco

    def atualizar_conteudo(self, **kwars) -> None:
        if self.janela is not None:
            self.page.close(self.janela)
            self.janela = None

        for k, v in kwars.items():
            setattr(self.produto, k, v)

        self.placeholder()
        self.criar_conteudo()
        self.update()

    def abrir_janela(self, produto: Produto) -> None:
        self.produto = produto
        self.placeholder()
        self.criar_conteudo()
        self.update()

    def fechar_janela(self, e: ft.ControlEvent) -> None:
        self.produto = None
        self.controle_sombra.visibilidade(False)
        self.visible = False
        self.update()

    def placeholder(self) -> None:
        self.content = ft.Container(
            ft.ProgressRing(), expand=True, alignment=ft.alignment.center
        )
        self.visible = True
        self.update()


class ControlePainelInfos:
    def __init__(self, painel_infos, controle_sombra) -> None:
        self.painel_infos = painel_infos
        self.controle_sombra = controle_sombra

    def abrir_janela(self, produto: Produto) -> None:
        self.controle_sombra.visibilidade(True)
        self.painel_infos.abrir_janela(produto)


class CartaoItem(ft.Card):
    def __init__(self, produto: Produto, controle_painel_infos: ControlePainelInfos):
        super().__init__(col=4, elevation=10)
        self.produto = produto
        self.controle_painel_infos = controle_painel_infos
        self._criar_conteudo()

    def _criar_conteudo(self):
        op = OperadorProduto(self.produto)
        preco, valor_estoque, qtd_estoque, estoque_min = op.formatar_valores()
        categorias = op.obter_categorias()
        fornecedores = op.obter_fornecedores()
        self.content = ft.Container(
            ft.Column([
            ft.ResponsiveRow([
                ft.Text(
                    self.produto.nome.title(),
                    color=ft.Colors.BLACK87,
                    weight=ft.FontWeight.W_600,
                    col=9.5,
                    size=20
                ),
                ft.IconButton(
                    ft.Icons.MENU_ROUNDED,
                    col=2.5,
                    icon_color=ft.Colors.BLACK54,
                    on_click=self.abrir_configuracoes
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=8),
            fornecedores,
            categorias,
            ft.ResponsiveRow([
                ft.Column([
                    ft.Text(
                        "Quantidade",
                        size=15,
                        color=ft.Colors.BLACK54,
                        weight=ft.FontWeight.W_600
                    ),
                    ft.Text(
                        qtd_estoque,
                        size=17,
                        color=ft.Colors.BLACK87,
                        weight=ft.FontWeight.W_600
                    )
                ], col=6, spacing=0),
                ft.Column([
                    ft.Text(
                        "Estoque mínimo",
                        size=15,
                        color=ft.Colors.BLACK54,
                        weight=ft.FontWeight.W_600,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        estoque_min,
                        size=17,
                        color=ft.Colors.BLACK87,
                        weight=ft.FontWeight.W_600
                    )
                ], col=6, spacing=0),
                ft.Column([
                    ft.Text(
                        "Preço unitário",
                        size=15,
                        color=ft.Colors.BLACK54,
                        weight=ft.FontWeight.W_600,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        locale.currency(preco, grouping=True),
                        size=17,
                        color=ft.Colors.BLACK87,
                        weight=ft.FontWeight.W_600
                    )
                ], col=6, spacing=0),
                ft.Column([
                    ft.Text(
                        "Valor do estoque",
                        size=15,
                        color=ft.Colors.BLACK54,
                        weight=ft.FontWeight.W_600,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        locale.currency(valor_estoque, grouping=True),
                        size=17,
                        color=ft.Colors.BLACK87,
                        weight=ft.FontWeight.W_600
                    )
                ], col=6, spacing=0)
            ], spacing=0)
            ], spacing=5),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15),
        )

    def abrir_configuracoes(self, e):
        self.controle_painel_infos.abrir_janela(self.produto)


class SeletorShowItens(ft.Container):
    def __init__(self):
        super().__init__(col=2)
        self.content = ft.SegmentedButton(
            selected="1",
            segments=[
                ft.Segment(
                    value="1",
                    icon=ft.Image("./icons_clone/apps.png", height=15, width=15)
                ),
                ft.Segment(
                    value="2",
                    icon=ft.Image("./icons_clone/list.png", height=15, width=15)
                )
            ],
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(5),
                side=ft.BorderSide(0, ft.Colors.GREY_100),
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.GREY_100,
                    ft.ControlState.SELECTED: ft.Colors.GREY_300,
                    ft.ControlState.PRESSED: ft.Colors.GREY_300,
                    ft.ControlState.HOVERED: ft.Colors.GREY_100,
                },
                overlay_color={
                    ft.ControlState.DEFAULT: ft.Colors.GREY_100,
                    ft.ControlState.SELECTED: ft.Colors.GREY_300,
                    ft.ControlState.PRESSED: ft.Colors.GREY_300,
                },
            ),
            show_selected_icon=False
        )


class JanelaEditarMovimentacao(ft.AlertDialog):
    def __init__(
        self,
        movimentacao,
        controle
    ):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.movimentacao = movimentacao
        self.controle = controle
        self._criar_conteudo()

    def _criar_conteudo(self):
        self._criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Registrar movimentação", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    ft.Column([
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("AÇÃO",weight=ft.FontWeight.W_500),
                                self.f_acao
                            ], col=6),
                            ft.Column([
                                ft.Text("CLASSIFICAR AÇÃO",weight=ft.FontWeight.W_500),
                                self.f_classificar_acao
                            ], col=6),
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE",weight=ft.FontWeight.W_500),
                                self.f_unidade
                            ], col=6),
                            self.f_qtd
                        ]),
                        ft.ResponsiveRow([
                            self.f_preco,
                            self.f_dt_movimentacao
                        ]),
                        ft.Column([
                            ft.Divider(),
                            ft.ResponsiveRow([
                                self.b_cancelar,
                                self.b_confirmar
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=410, width=500
        )

    def _criar_entradas(self):
        self.f_acao = ft.Dropdown(
            options=[
                ft.dropdown.Option(acao)
                for acao in [self.movimentacao.operacao]
            ],
            value=self.movimentacao.operacao,
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            disabled=True
        )
        self.f_classificar_acao = ft.Dropdown(
            options=[],
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            on_change=self._liberar_botao_confirmar
        )
        self.f_unidade = ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in [self.movimentacao.unidade]
            ],
            value=self.movimentacao.unidade,
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            disabled=True
        )
        self.f_qtd = TextField(
            "QUANTIDADE",
            6,
            value=locale.currency(self.movimentacao.qtd, grouping=True, symbol=False),
            input_filter=ft.InputFilter(
                regex_string=r"^(\d+(,\d*)?)?$",
                replacement_string="",
                allow=True
            ),
            on_change=self._liberar_botao_confirmar
        )
        self.f_preco = TextField(
            f"PRECO POR {self.movimentacao.unidade.upper()}",
            6,
            "Preço de custo por unidade do produto.",
            value=locale.currency(
                self.movimentacao.valor_unit if not pd.isnull(self.movimentacao.valor_unit) else 0,
                grouping=True
            ).replace(".", ""),
            visible=False
        )
        self.f_dt_movimentacao = TextField(
            "DATA MOVIMENTAÇÃO",
            6,
            value=datetime.now().strftime("%d/%m/%Y"),
            on_change=self._liberar_botao_confirmar
        )

    def _criar_botoes(self):
        self.b_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.b_confirmar = ft.OutlinedButton(
            "CONFIRMAR",
            col=5,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            ),
            disabled=True,
            on_click=self.salvar_movimentacao
        )

    def _liberar_botao_confirmar(self, e):
        values = [
            self.f_classificar_acao.value,
            self.f_qtd.value,
            self.f_dt_movimentacao.value
        ]
        self.b_confirmar.disabled = not all(values)
        self.b_confirmar.update()

    def _acao(self, acao):
        self._estado_padrao()
        match acao:
            case "Entrada":
                self._acao_entrada()
            case "Saída":
                self._acao_saida()
            case "Inventário":
                self._acao_inventario()
        
    def _estado_padrao(self):
        self.f_classificar_acao.options.clear()
        self.f_classificar_acao.update()

    def _acao_entrada(self):
        self.f_classificar_acao.options.extend(
            [
                ft.dropdown.Option(value)
                for value in ["Compras", "Produção", "Tranferência"]
            ]
        )
        self.f_preco.visible = True
        self.f_preco.update()
        self.f_classificar_acao.update()

    def _acao_saida(self):
        self.f_classificar_acao.options.extend(
            [
                ft.dropdown.Option(value)
                for value in ["Vendas", "Consumo interno", "Tranferência", "Desperdício"]
            ]
        )
        self.f_classificar_acao.update()

    def _acao_inventario(self):
        self.f_preco.visible = False
        self.f_preco.update()

    def salvar_movimentacao(self, e):
        self.controle.atualizar(
            self.movimentacao.id,
            self.f_classificar_acao.value,
            self.f_qtd.value,
            self.f_preco.value
        )
        self.page.close(self)

    def did_mount(self):
        self._acao(self.movimentacao.operacao.title())


class LinhaHistorico(ft.ExpansionTile):
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
        super().__init__(
            title=ft.Row(),
            shape=ft.RoundedRectangleBorder(0)
        )
        self.icones = {
            "saída": "./icons_clone/arrow-left16.png",
            "entrada": "./icons_clone/arrow-right16.png",
            "inventario": "./icons_clone/list16.png"
        }
        self.cor_icones = {
            "saída": ft.Colors.RED,
            "entrada": ft.Colors.GREEN,
            "inventario": ft.Colors.GREY
        }
        self.movimentacao = Movimentacao(id, operacao, classificacao, data, nome, qtd, unidade, valor_unit, mensagem)
        self._criar_conteudo()

    def _criar_conteudo(self):
        self._criar_textos()
        self.title = ft.ResponsiveRow([
            ft.Text(self.movimentacao.data.strftime("%b %d").upper(), col=1, weight=ft.FontWeight.W_600),
            ft.Image(
                self.icones[self.movimentacao.operacao.lower()],
                color=self.cor_icones[self.movimentacao.operacao.lower()],
                col=0.5
            ),
            ft.Column([
                ft.Text(self.movimentacao.nome, weight=ft.FontWeight.W_600, size=15),
                self.t_classificacao
            ], col=4, spacing=0),
            ft.Container(
                ft.ResponsiveRow([
                    ft.FilledTonalButton(
                        content=ft.ResponsiveRow([
                            ft.Image("./icons_clone/pencil.png", height=15, width=15, col=3.5),
                            ft.Text("Editar", size=12, col=8.5)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        col=6,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
                        bgcolor=ft.Colors.BLUE_100,
                        on_click=self.abrir_janela_edicao
                    ),
                    ft.FilledTonalButton(
                        content=ft.ResponsiveRow([
                            ft.Image(
                                "./icons_clone/trash.png",
                                height=15,
                                width=15,
                                col=3.5,
                                color=ft.Colors.RED
                            ),
                            ft.Text("Cancelar", size=12, col=8.5, color=ft.Colors.RED)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        col=6,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
                        bgcolor=ft.Colors.WHITE
                    )
                ]), col=2.5
            ),
            ft.Container(
                ft.ResponsiveRow([
                    ft.Container(
                        ft.ResponsiveRow([
                            ft.Text("Quantidade", col=12, size=12, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            self.t_quantidade
                        ], run_spacing=0, spacing=0), col=4,
                    ),
                    ft.Container(
                        ft.ResponsiveRow([
                            ft.Text("Valor unit.", col=12, size=12, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            self.t_valor_unit
                        ], run_spacing=0, spacing=0), col=4
                    ),
                    ft.Container(
                        ft.ResponsiveRow([
                            ft.Text("Valor total", col=12, size=12, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            self.t_valor_total
                        ], run_spacing=0, spacing=0), col=4
                    )
                ], spacing=3), col=4, padding=ft.padding.only(left=20)
            )
        ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self.controls=[
            ft.ListTile(
                title=ft.Text(f"{self.movimentacao.operacao.title()} realizada por: {self.movimentacao.mensagem}"),
                subtitle=ft.Text(self.movimentacao.data.strftime("%d-%m-%Y %H:%M"))
            )
        ]

    def _criar_textos(self):
        self.t_classificacao = ft.Text(
            self.movimentacao.classificacao if self.movimentacao.classificacao is not None else "Sem class.",
            size=12,
            weight=ft.FontWeight.W_600
        )
        self.t_quantidade = ft.Text(
            self._criar_texto_quantidade(self.movimentacao.qtd, self.movimentacao.unidade, self.movimentacao.operacao),
            col=12,
            size=15,
            weight=ft.FontWeight.BOLD
        )
        self.t_valor_unit = ft.Text(
            locale.currency(self._formatar_preco(self.movimentacao.valor_unit), grouping=True),
            col=12,
            size=15,
            weight=ft.FontWeight.BOLD
        )
        self.t_valor_total = ft.Text(
            locale.currency(self._valor_total(self.movimentacao.valor_unit, self.movimentacao.qtd), grouping=True),
            col=12,
            size=15,
            weight=ft.FontWeight.BOLD
        )

    def abrir_janela_edicao(self, e):
        controle = ControleMovimentacao(self)
        janela = JanelaEditarMovimentacao(self.movimentacao, controle)
        self.page.open(janela)

    def _criar_texto_quantidade(self, qtd, unidade, operacao):
        qtd = self._formatar_quantidade(qtd)
        unidade = unidade.split(" ")[1].strip("()")
        op = "+" if operacao.lower() == "entrada" else "-"
        return f"{op}{qtd} {unidade}" 

    def _formatar_quantidade(self, quantidade):
        return locale.currency(quantidade, grouping=True, symbol=False)

    def _formatar_preco(self, preco):
        return preco if pd.notna(preco) else 0.0
    
    def _valor_total(self, preco: float, quantidade: float):
        return self._formatar_preco(preco) * quantidade

    def atualizar_infos(self, classificacao, qtd, valor_unit):
        self.t_classificacao.value = classificacao
        self.t_quantidade.value = self._criar_texto_quantidade(qtd, self.movimentacao.unidade, self.movimentacao.operacao)
        self.t_valor_unit.value = locale.currency(valor_unit, grouping=True)
        self.t_valor_total.value = locale.currency(self._valor_total(valor_unit, qtd), grouping=True)
        
        self.t_classificacao.update()
        self.t_quantidade.update()
        self.t_valor_unit.update()
        self.t_valor_total.update()


class JanelaRegistrarMovimentacao(ft.AlertDialog):
    def __init__(self, produto, controle):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.produto = produto
        self.controle: ControleMovimentacao = controle
        self._criar_conteudo()

    def _criar_conteudo(self):
        self._criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Registrar movimentação", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    ft.Column([
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("AÇÃO",weight=ft.FontWeight.W_500),
                                self.f_acao
                            ], col=6),
                            ft.Column([
                                ft.Text("CLASSIFICAR AÇÃO",weight=ft.FontWeight.W_500),
                                self.f_classificar_acao
                            ], col=6),
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE",weight=ft.FontWeight.W_500),
                                self.f_unidade
                            ], col=6),
                            self.f_qtd
                        ]),
                        ft.ResponsiveRow([
                            self.f_preco,
                            self.f_dt_movimentacao
                        ]),
                        ft.ResponsiveRow([
                            self.f_dt_validade
                        ]),
                        ft.Column([
                            ft.Divider(),
                            ft.ResponsiveRow([
                                self.b_cancelar,
                                self.b_confirmar
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=410, width=500
        )

    def _criar_entradas(self):
        self.f_acao = ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in ["Entrada", "Saída", "Inventário"]
            ],
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            on_change=self._acao
        )
        self.f_classificar_acao = ft.Dropdown(
            options=[],
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300
        )
        self.f_unidade = ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in [self.produto.unidade]
            ],
            value=self.produto.unidade,
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300
        )
        self.f_qtd = TextField(
            "QUANTIDADE",
            6,
            input_filter=ft.InputFilter(
                regex_string=r"^(\d+(,\d*)?)?$",
                replacement_string="",
                allow=True
            ),
            on_change=self._liberar_botao_confirmar
        )
        self.f_preco = TextField(
            f"PRECO POR {self.produto.unidade.upper()}",
            6,
            "Preço de custo por unidade do produto.",
            value=locale.currency(
                self.produto.preco if not pd.isnull(self.produto.preco) else 0,
                grouping=True
            ).replace(".", ""),
            visible=False
        )
        self.f_dt_movimentacao = TextField(
            "DATA MOVIMENTAÇÃO",
            6,
            value=datetime.now().strftime("%d/%m/%Y"),
            on_change=self._liberar_botao_confirmar
        )
        self.f_dt_validade = TextField(
            "DATA DE VALIDADE",
            6,
            "a data de validade irá criar um lote deste produto",
            placeholder=f"ex: {datetime.now().strftime("%d/%m/%Y")}",
            visible=False
        )

    def _criar_botoes(self):
        self.b_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.b_confirmar = ft.OutlinedButton(
            "CONFIRMAR",
            col=5,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            ),
            disabled=True,
            on_click=self.registrar_movimentacao
        )

    def _liberar_botao_confirmar(self, e):
        values = [
            self.f_acao.value,
            self.f_unidade.value,
            self.f_qtd.value,
            self.f_dt_movimentacao.value
        ]
        self.b_confirmar.disabled = not all(values)
        self.b_confirmar.update()

    def _acao(self, e):
        self._estado_padrao()
        match e.data:
            case "Entrada":
                self._acao_entrada()
            case "Saída":
                self._acao_saida()
            case "Inventário":
                self._acao_inventario()
        
    def _estado_padrao(self):
        self.f_classificar_acao.options.clear()
        self.f_preco.visible = False
        self.f_dt_validade.visible = False
        self.f_preco.update()
        self.f_dt_validade.update()
        self.f_classificar_acao.update()

    def _acao_entrada(self):
        self.f_classificar_acao.options.extend(
            [
                ft.dropdown.Option(value)
                for value in ["Compras", "Produção", "Tranferência"]
            ]
        )
        self.f_preco.visible = True
        self.f_dt_validade.visible = True
        self.f_preco.update()
        self.f_dt_validade.update()
        self.f_classificar_acao.update()

    def _acao_saida(self):
        self.f_classificar_acao.options.extend(
            [
                ft.dropdown.Option(value)
                for value in ["Vendas", "Consumo interno", "Tranferência", "Desperdício"]
            ]
        )
        self.f_classificar_acao.update()

    def _acao_inventario(self):
        self.f_preco.visible = True
        self.f_preco.update()

    def registrar_movimentacao(self, e):
        self.controle.registrar(
            self.produto.id,
            self.produto.qtd_estoque,
            self.f_acao.value,
            self.f_classificar_acao.value,
            self.f_unidade.value,
            self.f_qtd.value,
            self.f_dt_movimentacao.value,
            self.f_preco.value,
            self.f_dt_validade.value
        )


class JanelaEditarProduto(ft.AlertDialog):
    def __init__(self, produto, controle):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.produto = produto
        self.controle_produto = controle
        self.categorias = None
        self.fornecedores = None
        self.unidades = [
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
        self.ler_dados()

    def _criar_conteudo(self, categorias, fornecedores):
        self.mensagem = ft.Text(color=ft.Colors.RED, visible=False)
        self.check_sim = ft.Checkbox(label="SIM", value=True, on_change=self.estado_check)
        self.check_nao = ft.Checkbox(label="NÃO", on_change=self.estado_check)

        self._criar_entradas(categorias, fornecedores)
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Editar produto", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    ft.Column([
                        ft.ResponsiveRow([
                            self.f_nome_produto
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE",weight=ft.FontWeight.W_500),
                                self.f_unidade
                            ], col=6),
                            self.f_qtd_estoque
                        ]),
                        ft.ResponsiveRow([
                            self.f_estoque_min,
                            self.f_preco_unidade
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("CATEGORIA", weight=ft.FontWeight.W_500),
                                self.f_categoria,
                                ft.Row([
                                    self.b_criar_categoria
                                ], alignment=ft.MainAxisAlignment.END)
                            ], col=6),
                            ft.Column([
                                ft.Text("FORNECEDOR(ES)", weight=ft.FontWeight.W_500),
                                self.f_fornecedores,
                                ft.Row([
                                    self.b_criar_fornecedor
                                ], alignment=ft.MainAxisAlignment.END)
                            ], col=6)
                        ]),
                        ft.Column([
                            ft.Text("COMPÕE CMV?", weight=ft.FontWeight.W_500),
                            ft.Text(
                                "Determina se esse produto deve ser incluído no calculo do seu CMV.",
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Row([
                                self.check_sim,
                                self.check_nao
                            ])
                        ]),
                        self.mensagem,
                        ft.Column([
                            ft.Divider(),
                            ft.ResponsiveRow([
                                self.b_cancelar,
                                self.b_criar_produto
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=500, width=500
        )

    def _criar_entradas(self, categorias, fornecedores):

        self.f_nome_produto = TextField(
            "NOME DO PRODUTO",
            12,
            value=self.produto.nome,
            on_change=self._liberar_botao_criar_prod
        )
        self.f_qtd_estoque = TextField(
            "QUANTIDADE EM ESTOQUE",
            6,
            value=locale.currency(self.produto.qtd_estoque, grouping=True, symbol=False),
            on_change=self._liberar_botao_criar_prod,
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
        )
        self.f_estoque_min = TextField(
            "ESTOQUE MÍNIMO",
            6,
            "Quantidade de refência para compras desse produto",
            value=locale.currency(self.produto.estoque_min, grouping=True, symbol=False),
            on_change=self._liberar_botao_criar_prod,
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
        )
        self.f_preco_unidade = TextField(
            "PREÇO POR UNIDADE",
            6,
            "Preço de custo por unidade do produto (campo opcional)",
            value=locale.currency(
                0 if pd.isnull(self.produto.preco) else self.produto.preco,
                grouping=True,
                symbol=False
            ).replace(".", ""),
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
        )
        self.f_unidade = ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in self.unidades
            ],
            value=self.produto.unidade,
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            on_change=self._liberar_botao_criar_prod
        )

        ids_categorias = None
        ids_fornecedores = None
        if self.produto.categorias["nomes"] is not None:
            ids_categorias = [cat["id"] for cat in categorias if cat["nome"] in self.produto.categorias["nomes"]]
        
        if self.produto.fornecedores["nomes"] is not None:
            ids_fornecedores = [forn["id"] for forn in fornecedores if forn["nome"] in self.produto.fornecedores["nomes"]]

        self.f_categoria = DropdownV2(
            {cat["id"]: cat["nome"] for cat in categorias},
            ids_categorias
        )
        self.f_fornecedores = DropdownV2(
            {forn["id"]: forn["nome"] for forn in fornecedores},
            ids_fornecedores
        )

    def _criar_botoes(self):
        self.b_criar_categoria = ft.TextButton(
            "CRIAR NOVA CATEGORIA",
            on_click=self.janela_add_categoria,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.b_criar_fornecedor = ft.TextButton(
            "CRIAR NOVO FORNECEDOR",
            on_click=self.janela_add_fornecedor,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.b_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.b_criar_produto = ft.OutlinedButton(
            "SALVAR PRODUTO",
            col=5,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            ),
            on_click=self.salvar_produto
        )
    
    def estado_check(self, e):
        if self.check_sim.value:
            self.check_nao.value = False
        elif self.check_nao.value:
            self.check_sim.value = False
        self.check_nao.update()
        self.check_sim.update()

    def _liberar_botao_criar_prod(self, e):
        entradas = [self.f_nome_produto.value, self.f_unidade.value, self.f_qtd_estoque.value, self.f_estoque_min.value]
        self.b_criar_produto.disabled = not all(entradas)

        self.b_criar_produto.update()

    def verificar_produtos_iguais(self, nome, und):
        if nome is None or und is None:
            return False
        produto_str = nome.lower() + und.lower()
        return any(produto_str == "".join(nu) for nu in self.nome_unidade)

    def janela_add_categoria(self, e):
        janela = JanelaCadCategoria(ControleDropdownV2(self.f_categoria))
        controle = ControleCategoria(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def janela_add_fornecedor(self, e):
        janela = JanelaCadFornecedor(ControleDropdownV2(self.f_fornecedores))
        controle = ControleFornecedores(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def salvar_produto(self, e):
        if self.controle_produto is not None:
            self.controle_produto.atualizar_produto(
                self.produto.id,
                self.f_nome_produto.value,
                self.f_unidade.value,
                self.f_qtd_estoque.value,
                self.f_estoque_min.value,
                self.f_preco_unidade.value,
                self.f_categoria.value,
                self.f_fornecedores.value,
                self.check_sim.value
            )

    def ler_dados(self):
        try:
            ig = InfosGlobal()
            bd = SupabaseSingleton()
            client = bd.get_client()
            categorias = (
                client.table("categoria")
                .select("*")
                .eq("empresa_id", ig.empresa_id)
                .execute()
            )
            fornecedores = (
                client.table("fornecedores")
                .select("*")
                .eq("empresa_id", ig.empresa_id)
                .execute()
            )
        except Exception as e:
            print(e)
        finally:
            self._criar_conteudo(categorias.data, fornecedores.data)


class CapsulaDropdown(ft.Container):
    def __init__(self, rotulo: str, id: int, on_click: Callable[[int], None]):
        super().__init__(
            content=ft.ResponsiveRow([
                ft.Text(rotulo, size=13, col=9.5, weight=ft.FontWeight.W_500),
                ft.TextButton(
                    "X",
                    col=2.5,
                    on_click=lambda e, id_f=id: on_click(id_f),
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
                        padding=ft.padding.all(3)
                    )
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=0),
            height=25,
            border_radius=20,
            border=ft.border.all(1, ft.Colors.BLACK87),
            padding=ft.padding.only(left=10, right=10),
            bgcolor=ft.Colors.BLACK12,
            data=id,
            col=int(len(rotulo) / 2 + 4)
        )
        self.rotulo = rotulo
        self.id = id

    @property
    def value(self):
        return {"id": self.id, "nome": self.rotulo}


class DropdownV2(ft.PopupMenuButton):
    def __init__(self, rotulos: dict, values: list=None):
        super().__init__(
            tooltip="",
            size_constraints=ft.BoxConstraints(
                max_height=250,
                min_width=200
            ),
            bgcolor=ft.Colors.WHITE
        )
        self.rotulos = rotulos
        self._criar_conteudo(values)

    def _criar_conteudo(self, values):
        self.area_botao = ft.ResponsiveRow([], spacing=5)
        self.content = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    self.area_botao,
                    padding=ft.padding.only(left=5, bottom=5, right=5),
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.BLACK54)),
                    expand=True,
                    col=10
                ),
                ft.Column([
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN,color=ft.Colors.BLACK54)
                ], col=2)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=0),
            padding=ft.padding.only(top=10, bottom=10),
            alignment=ft.alignment.center,
            width=230,
            border_radius=15,
            border=ft.border.all(1, ft.Colors.BLACK54)
        )
        self.items=[
            ft.PopupMenuItem(text=label, on_click=lambda e, id=i: self._adicionar_item(id))
            for i, label in self.rotulos.items()
        ]
        if values is not None:
            for value in values:
                self.area_botao.controls.append(
                    CapsulaDropdown(self.rotulos[value], value, self.excluir)
                )

    @property
    def value(self):
        if self.area_botao.controls:
            return [capsula.value for capsula in self.area_botao.controls]
        else:
            return None

    def _adicionar_item(self, id):
        self.area_botao.controls.append(
            CapsulaDropdown(self.rotulos[id], id, self.excluir)
        )
        self.area_botao.update()

    def atualizar_itens(self, id, nome):
        self.rotulos.update({id: nome})
        self.items.clear()
        self.items=[
            ft.PopupMenuItem(text=label, on_click=lambda e, id=i: self._adicionar_item(id))
            for i, label in self.rotulos.items()
        ]
        self.update()

    def excluir(self, id):
        for capsula in self.area_botao.controls:
            if int(capsula.id) == int(id):
                self.area_botao.controls.remove(capsula)
                self.area_botao.update()


class ControleDropdownV2:
    def __init__(self, dropdown):
        self.dropdown = dropdown

    def atualizar_itens(self, dados):
        self.dropdown.atualizar_itens(dados["id"], dados["nome"])


class JanelaCadCategoria(ft.AlertDialog):
    def __init__(self, controle_drop):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.controle_drop = controle_drop
        self.controle_categoria = None
        self._criar_conteudo()

    def _criar_conteudo(self):
        self._criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Criar nova categoria", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ResponsiveRow([self.f_categoria]),
                ft.Row([
                    ft.Text("CORES: ", weight=ft.FontWeight.W_500),
                    self.cores
                ]),
                ft.Divider(),
                ft.ResponsiveRow([
                    ft.OutlinedButton(
                        "CANCELAR",
                        on_click=self.fechar,
                        col=4,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
                    ),
                    self.botao_criar_categoria
                ], alignment=ft.MainAxisAlignment.END)
            ]), height=250, width=500
        )

    def _criar_entradas(self):
        self.f_categoria = TextField(
            "NOME DA CATEGORIA",
            col=12,
            on_change=self._liberar_botao_criar
        )
        self.cores = ft.RadioGroup(
            ft.Row([
                ft.Radio(value=cor, fill_color=cor)
                for cor in [
                    ft.Colors.RED_300,
                    ft.Colors.GREEN_300,
                    ft.Colors.BLUE_300,
                    ft.Colors.ORANGE_300,
                    ft.Colors.GREY_300,
                    ft.Colors.PURPLE_300
                ]
            ], spacing=0),
            on_change=self._liberar_botao_criar
        )

    def _criar_botoes(self):
        self.botao_criar_categoria = ft.OutlinedButton(
            "CRIAR NOVA CATEGORIA",
            col=5,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(
                    foreground=ft.Paint(color=ft.Colors.BLACK54)
                ),
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                }
            ),
            disabled=True,
            on_click=self.criar_categoria
        )

    def fechar(self, e):
        self.page.close(self)
        for o in reversed(self.page.overlay):
            if isinstance(o, (JanelaCadProduto, JanelaEditarProduto)):
                self.page.open(o)
                break

    def criar_categoria(self, e):
        if self.controle_categoria is not None:
            self.controle_categoria.criar_categoria(
                self.f_categoria.value,
                self.cores.value
            )

    def atualizar_item(self, categoria):
        self.controle_drop.atualizar_itens(categoria)

    def _liberar_botao_criar(self, e):
        if all([self.f_categoria.value, self.cores.value]):
            self.botao_criar_categoria.disabled = False
        else:
            self.botao_criar_categoria.disabled = True
        self.botao_criar_categoria.update()

    def definir_controle(self, controle):
        self.controle_categoria = controle


class JanelaCadFornecedor(ft.AlertDialog):
    def __init__(self, controle_drop):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.controle_drop = controle_drop
        self.controle_fornecedor = None
        self._criar_conteudo()

    def _criar_conteudo(self):
        self._criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Criar novo fornecedor", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ResponsiveRow([self.f_nome_fornecedor]),
                ft.ResponsiveRow([ft.Text("VENDEDOR", col=12, weight=ft.FontWeight.BOLD)]),
                ft.Divider(),
                ft.ResponsiveRow([self.f_nome_vendedor]),
                ft.ResponsiveRow([self.f_telefone_vendedor]),
                ft.ResponsiveRow([
                    ft.OutlinedButton(
                        "CANCELAR",
                        on_click=self.fechar,
                        col=4,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
                    ),
                    self.botao_criar
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15, scroll=ft.ScrollMode.ALWAYS), height=460, width=500
        )

    def _criar_entradas(self):
        self.f_nome_fornecedor = TextField("NOME DO FORNECEDOR", col=12, on_change=self._liberar_botao_criar)
        self.f_nome_vendedor = TextField("Nome", col=12)
        self.f_telefone_vendedor = TextField("Telefone", col=12)

    def _criar_botoes(self):
        self.botao_criar = ft.OutlinedButton(
            "CRIAR NOVO FORNECEDOR",
            col=5,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(
                    foreground=ft.Paint(color=ft.Colors.BLACK54)
                ),
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                }
            ),
            disabled=True,
            on_click=self.criar_fornecedor
        )

    def fechar(self, e):
        self.page.close(self)
        for o in reversed(self.page.overlay):
            if isinstance(o, (JanelaCadProduto, JanelaEditarProduto)):
                self.page.open(o)
                break

    def criar_fornecedor(self, e):
        if self.controle_fornecedor is not None:
            self.controle_fornecedor.criar_fornecedor(
                self.f_nome_fornecedor.value,
                self.f_nome_vendedor.value,
                self.f_telefone_vendedor.value
            )

    def atualizar_item(self, categoria):
        self.controle_drop.atualizar_itens(categoria)

    def _liberar_botao_criar(self, e):
        if self.f_nome_fornecedor.value:
            self.botao_criar.disabled = False
        else:
            self.botao_criar.disabled = True
        self.botao_criar.update()

    def definir_controle(self, controle):
        self.controle_fornecedor = controle


class JanelaCadProduto(ft.AlertDialog):
    def __init__(self, nome_unidade):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.nome_unidade = nome_unidade
        self.controle_produto = None
        self.categorias = None
        self.fornecedores = None
        self.unidades = UNIDADES
        self.ler_dados()

    def _criar_conteudo(self, categorias, fornecedores):
        self.mensagem = ft.Text(color=ft.Colors.RED, visible=False)

        self._criar_entradas(categorias, fornecedores)
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Criar novo produto", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    ft.Column([
                        ft.ResponsiveRow([
                            self.f_nome_produto
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE", weight=ft.FontWeight.W_500),
                                self.f_unidade
                            ], col=6),
                            self.f_qtd_estoque
                        ]),
                        ft.ResponsiveRow([
                            self.f_estoque_min,
                            self.f_preco_unidade
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("CATEGORIA", weight=ft.FontWeight.W_500),
                                self.f_categoria,
                                ft.Row([
                                    self.b_criar_categoria
                                ], alignment=ft.MainAxisAlignment.END)
                            ], col=6),
                            ft.Column([
                                ft.Text("FORNECEDOR(ES)", weight=ft.FontWeight.W_500),
                                self.f_fornecedores,
                                ft.Row([
                                    self.b_criar_fornecedor
                                ], alignment=ft.MainAxisAlignment.END)
                            ], col=6)
                        ]),
                        ft.Column([
                            ft.Text("COMPÕE CMV?", weight=ft.FontWeight.W_500),
                            ft.Text(
                                "Determina se esse produto deve ser incluído no calculo do seu CMV.",
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Row([
                                self.check_sim,
                                self.check_nao
                            ])
                        ]),
                        self.mensagem,
                        ft.Column([
                            ft.Divider(),
                            ft.ResponsiveRow([
                                self.b_cancelar,
                                self.b_criar_produto
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=500, width=500
        )

    def _criar_entradas(self, categorias, fornecedores):
        self.check_sim = ft.Checkbox(label="SIM", value=True, on_change=self.estado_check)
        self.check_nao = ft.Checkbox(label="NÃO", on_change=self.estado_check)
        self.f_nome_produto = TextField("NOME DO PRODUTO", 12, on_change=self._liberar_botao_criar_prod)
        self.f_qtd_estoque = TextField(
            "QUANTIDADE EM ESTOQUE",
            6, 
            on_change=self._liberar_botao_criar_prod,
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
        )
        self.f_estoque_min = TextField(
            "ESTOQUE MÍNIMO",
            6,
            "Quantidade de refência para compras desse produto",
            on_change=self._liberar_botao_criar_prod,
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
        )
        self.f_preco_unidade = TextField(
            "PREÇO POR UNIDADE",
            6,
            "Preço de custo por unidade do produto (campo opcional)",
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
        )
        self.f_unidade = ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in self.unidades
            ],
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            on_change=self._liberar_botao_criar_prod
        )
        self.f_categoria = DropdownV2(
            {cat["id"]: cat["nome"] for cat in categorias}
        )
        self.f_fornecedores = DropdownV2(
            {forn["id"]: forn["nome"] for forn in fornecedores}
        )

    def _criar_botoes(self):
        self.b_criar_categoria = ft.TextButton(
            "CRIAR NOVA CATEGORIA",
            on_click=self.janela_add_categoria,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.b_criar_fornecedor = ft.TextButton(
            "CRIAR NOVO FORNECEDOR",
            on_click=self.janela_add_fornecedor,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.b_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.b_criar_produto = ft.OutlinedButton(
            "CRIAR NOVO PRODUTO",
            col=5,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            ),
            disabled=True,
            on_click=self.criar_produto
        )
    
    def estado_check(self, e):
        if self.check_sim.value:
            self.check_nao.value = False
        elif self.check_nao.value:
            self.check_sim.value = False
        self.check_nao.update()
        self.check_sim.update()

    def _liberar_botao_criar_prod(self, e):
        entradas = [self.f_nome_produto.value, self.f_unidade.value, self.f_qtd_estoque.value, self.f_estoque_min.value]
        iguais = self.verificar_produtos_iguais(entradas[0], entradas[1])
        self.b_criar_produto.disabled = not (all(entradas) and not iguais)
        if iguais:
            self.mensagem.visible =  True
            self.mensagem.value = "Já existe um produto com esse nome e unidade"
        else:
            self.mensagem.visible = False
            self.mensagem.value = ""

        self.mensagem.update()
        self.b_criar_produto.update()

    def verificar_produtos_iguais(self, nome, und):
        if nome is None or und is None:
            return False
        produto_str = nome.lower() + und.lower()
        return any(produto_str == "".join(nu) for nu in self.nome_unidade)

    def janela_add_categoria(self, e):
        janela = JanelaCadCategoria(ControleDropdownV2(self.f_categoria))
        controle = ControleCategoria(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def janela_add_fornecedor(self, e):
        janela = JanelaCadFornecedor(ControleDropdownV2(self.f_fornecedores))
        controle = ControleFornecedores(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def criar_produto(self, e):
        if self.controle_produto is not None:
            categorias = {cat["nome"]: self.infos_categorias[cat["id"]] for cat in self.f_categoria.value}
            self.controle_produto.criar_produto(
                self.f_nome_produto.value,
                self.f_unidade.value,
                self.f_qtd_estoque.value,
                self.f_estoque_min.value,
                self.f_preco_unidade.value,
                categorias,
                self.f_fornecedores.value,
                self.check_sim.value
            )
            self.page.close(self)

    def definir_controle(self, controle):
        self.controle_produto = controle

    def ler_dados(self):
        try:
            ig = InfosGlobal()
            bd = SupabaseSingleton()
            client = bd.get_client()
            categorias = (
                client.table("categoria")
                .select("*")
                .eq("empresa_id", ig.empresa_id)
                .execute()
            ).data
            fornecedores = (
                client.table("fornecedores")
                .select("*")
                .eq("empresa_id", ig.empresa_id)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self.infos_categorias = {cat["id"]: cat["cor"] for cat in categorias}
            self._criar_conteudo(categorias, fornecedores)
            

class Estoque(ft.Stack):
    def __init__(self, controle_sombra):
        super().__init__()
        self.controle_sombra = controle_sombra
        self.painel_infos = PainelInfos(controle_sombra)
        self.area_produtos = ft.Container(expand=True)
        self.produtos = None

    def _criar_conteudo(self):
        self.expand = False
        valor_total, total_produtos = self._obter_estatisticas()
        self._criar_grade_itens()

        self.coluna_area = ft.Column([
            ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        RotuloColuna("Estoque", "./icons_clone/boxes.png"),
                        ft.ResponsiveRow([
                            CartaoIndicadores(
                                "Valor total em estoque",
                                TextoMonetario(
                                    locale.currency(
                                        valor_total,
                                        grouping=True,
                                        symbol=False
                                    ), 30, ft.FontWeight.BOLD, 11
                                ),
                                4
                            ),
                            CartaoIndicadores(
                                "produtos cadastrados",
                                ft.ResponsiveRow([
                                    ft.Text(total_produtos,  size=30, weight=ft.FontWeight.BOLD, col=12)
                                ]),
                                4
                            ),
                            CartaoIndicadores(
                                "categorias",
                                ft.ResponsiveRow([
                                    ft.Text("0",  size=30, weight=ft.FontWeight.BOLD, col=12)
                                ]),
                                4
                            )
                        ]),
                        GradeNotificacao(self._cartoes_notificacoes(), 3),
                        ft.Divider(),
                        FiltrosEstoque(),
                        ft.Divider(),
                        ft.ResponsiveRow([
                            ft.Container(
                                ft.ResponsiveRow([
                                    BotaoTonal(
                                        "Cadastrar Produto",
                                        "./icons_clone/add.png",
                                        3,
                                        on_click=self.janela_cad_produtos
                                    ),
                                    BotaoTonal("Gerenciar Categorias", "./icons_clone/clipboard-list.png", 3)
                                ]), col=10
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        self.grade_itens
                    ], col=12)
                ]),
                padding=ft.padding.all(20)
            )
        ], scroll=ft.ScrollMode.ALWAYS)
        self.controls = [
            self.coluna_area,
            self.painel_infos
        ]
        self.update()

    def placeholder(self):
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _criar_grade_itens(self):
        self.grade_itens = ft.Container(
            GradeNotificacao([
                CartaoItem(
                    Produto(
                        row["id"],
                        row["nome"],
                        row["unidade"],
                        row["quantidade"],
                        row["estoque_minimo"],
                        row["preco_unidade"],
                        row["categorias"],
                        row["fornecedores"],
                        row["cmv"]
                    ),
                    ControlePainelInfos(self.painel_infos, self.controle_sombra)
                )
                for _, row in self.df.iterrows()
            ], 3), expand=True
        )

    def _cartoes_notificacoes(self):
        if len(self.df) > 0:
            estoque_baixo = len(self.df[self.df['quantidade'] < self.df['estoque_minimo']])
            estoque_critico = len(self.df[self.df['quantidade'] < (self.df["estoque_minimo"] * 0.2)])
            sem_preco = len(self.df[self.df["preco_unidade"].isnull()])
        else:
            estoque_baixo = estoque_critico = sem_preco = 0

        def criar_cartao(titulo, descricao, quantidade):
            return CartaoNotificacao(
                titulo,
                descricao,
                ft.Row([ft.Text(quantidade, color=ft.Colors.BLACK87, weight=ft.FontWeight.W_500, size=20)]),
                "./icons_clone/triangle-warning.png",
                ft.Colors.RED,
                BotaoTonal(
                    "Ver Produtos",
                    "./icons_clone/up-right-from-square.png",
                    7,
                    on_click=self.rolar
                ),
                4
            )

        cards = []
        
        if estoque_baixo:
            cards.append(
                criar_cartao(
                    "Produtos abaixo do estoque mínimo",
                    "",
                    estoque_baixo
                )
            )
        if estoque_critico:
            cards.append(
                criar_cartao(
                    "Produtos com estoque crítico",
                    "O estoque é considerado crítico quando atinge 20% do seu estoque mínimo.",
                    estoque_critico
                )
            )
        if sem_preco:
            cards.append(
                criar_cartao(
                    "Produtos sem preço",
                    "Configurar os preços dos seus produtos possibilita o cálculo correto do seu estoque total, do seu CMV, do custo de suas fichas técnicas, entre outros.",
                    sem_preco
                )
            )

        return cards

    def _obter_estatisticas(self):
        if len(self.df) > 0:
            valor_total = (self.df['quantidade'] * self.df['preco_unidade']).dropna().sum()
            total_produtos = len(self.df)
        else:
            valor_total = total_produtos = 0
        return valor_total, total_produtos
    
    def rolar(self, e):
        self.coluna_area.scroll_to(delta=400, duration=1000)

    def janela_cad_produtos(self, e):
        nome_unidade = [(row["nome"], row["unidade"]) for i, row in self.df.iterrows()]
        janela = JanelaCadProduto(nome_unidade)
        controle = ControleProduto(visualizacao=self)
        janela.definir_controle(controle)
        self.page.open(janela)

    def atualizar_dados(self):
        self.ler_dados()
        self.update()

    def ler_dados(self):
        try:
            client = SupabaseSingleton().get_client()
            resposta = (
                client.table("produtos")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .order("nome")
                .execute()
            )
        except Exception as e:
            print(e)
        else:   
            self._criar_df(resposta.data)
            self._criar_conteudo()

    def _criar_df(self, dados):
        self.df = pd.DataFrame(dados)

    def did_mount(self):
        self.placeholder()
        self.ler_dados()
