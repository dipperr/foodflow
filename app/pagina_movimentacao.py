import flet as ft
import locale
from typing import Callable, List, Optional
from dateutil import parser
from datetime import datetime
import pandas as pd

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

from banco_de_dados import SupabaseSingleton
from modelos import Movimentacao
from controles import (
    RotuloColuna,
    CartaoIndicadores,
    TextoMonetario,
    BotaoTonal,
    ControleMovimentacao,
    InfosGlobal
)


class Filtro(ft.Container):
    def __init__(
            self,
            rotulo: str,
            itens: List[str],
            checked=None,
            botao: Callable[[None], None]=None
        ):
        super().__init__(
            col=3,
            border=ft.border.all(1, ft.Colors.BLACK54),
            border_radius=5,
            padding=ft.padding.all(7),
            alignment=ft.alignment.center
        ),
        self.botao = botao
        self.checked = checked
        self.menu = ft.PopupMenuButton(
            content=ft.ResponsiveRow([
                ft.Image("./icons_clone//bars-filter.png", col=2, width=16, height=16),
                ft.Text(rotulo, col=8, weight=ft.FontWeight.W_500),
                ft.Image("./icons_clone/angles-up-down.png", width=16, height=16, col=2)
            ], vertical_alignment=ft.MainAxisAlignment.CENTER),
            items=[
                ft.PopupMenuItem(text=label, checked=(checked == i), on_click=self.check_clique)
                for i, label in enumerate(itens)
            ],
            bgcolor=ft.Colors.WHITE,
            tooltip=""
        )
        self.content = self.menu

    def check_clique(self, e):
        if self.checked is None:
            self.botao()

        for item in self.menu.items:
            item.checked = (item.text == e.control.text)
        self.menu.update()

    def limpar(self):
        for item in self.menu.items:
            item.checked = False
        self.menu.update()


class FiltrosEstoque(ft.ResponsiveRow):
    def __init__(self):
        super().__init__(
            controls=[
                Filtro(
                    "Filtrar categoria(s)",
                    []
                ),
                Filtro(
                    "Filtrar produto(s)",
                    []
                ),
                Filtro(
                    "Filtrar fornecedor(es)",
                    []
                ),
                Filtro(
                    "Filtrar por ação",
                    []
                ),
                Filtro(
                    "Filtrar por classificação",
                    []
                ),
                Filtro(
                    "Filtrar por data",
                    []
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

    def limpar_filtros(self, e):
        for filtro in self.controls[:-2]:
            filtro.limpar()
        self.controls[-1].visible = False
        self.controls[-1].update()

    def mostrar_botao(self):
        self.controls[-1].visible = True
        self.controls[-1].update()


class TextField(ft.Column):
    def __init__(
        self,
        label,
        col,
        subtitulo=None,
        value=None,
        placeholder=None,
        on_change=None,
        input_filter=None,
        visible=True
    ):
        super().__init__(
            col=col,
            spacing=5,
            visible=visible
        )
        self.entrada = ft.TextField(
            value=value,
            hint_text=placeholder,
            border_radius=15,
            border_color=ft.Colors.BLACK54,
            cursor_color=ft.Colors.BLACK54,
            on_change=on_change,
            input_filter=input_filter,
        )
        self.controls = [
            ft.Text(label, weight=ft.FontWeight.W_500),
            ft.Text(
                subtitulo,
                size=13,
                color=ft.Colors.BLACK54,
                weight=ft.FontWeight.W_400,
            ) if subtitulo else ft.Row(),
            self.entrada
        ]
    
    @property
    def value(self):
        return self.entrada.value if self.entrada.value else None
    
    def atualizar_rotulo(self, rotulo):
        self.controls[0].value = rotulo
        self.controls[0].update()


class JanelaEditarMovimentacao(ft.AlertDialog):
    def __init__(
        self,
        movimentacao,
        controle
    ):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
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


class PaginaMovimentacao(ft.Column):
    def __init__(self):
        super().__init__()

    def _criar_conteudo(self):
        self.expand = False
        self.scroll = ft.ScrollMode.ALWAYS
        
        total_movimentacoes, total_entradas, total_saidas = self._estatisticas()
        self.controls = [
            ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        RotuloColuna("Movimentações", "./icons_clone/exchange.png"),
                        ft.ResponsiveRow([
                            CartaoIndicadores(
                                "Total de movimentações *",
                                ft.Text(total_movimentacoes, size=30, weight=ft.FontWeight.BOLD),
                                4
                            ),
                            CartaoIndicadores(
                                "R$ total de entradas *",
                                TextoMonetario(
                                    locale.currency(
                                        total_entradas,
                                        grouping=True,
                                        symbol=False
                                    ), 30, ft.FontWeight.BOLD, 11
                                ),
                                4
                            ),
                            CartaoIndicadores(
                                "R$ total de saídas *",
                                TextoMonetario(
                                    locale.currency(
                                        total_saidas,
                                        grouping=True,
                                        symbol=False
                                    ), 30, ft.FontWeight.BOLD, 11
                                ),
                                4
                            )
                        ]),
                        ft.ResponsiveRow([ft.Text("* os números acima consideram os filtros aplicados abaixo", col=10, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500)]),
                        ft.Divider(),
                        FiltrosEstoque(),
                        ft.Divider(),
                        ft.ResponsiveRow([
                            BotaoTonal("Registrar Movimentações", "./icons_clone/exchange.png", 3, ft.Colors.BLUE_100),
                            BotaoTonal("Exportar", "./icons_clone/file.png", 3, ft.Colors.BLUE_100)
                        ]),
                        self._movimentacoes()
                    ])
                ]), padding=ft.padding.all(20)
            )
        ]
        self.update()

    def placeholder(self):
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _movimentacoes(self):
        try:
            ig = InfosGlobal()
            client = SupabaseSingleton().get_client()
            respostas = (
                client.table("movimentacao")
                .select("id, operacao, data_movimentacao, quantidade, classificacao, preco_movimentacao, informacoes, produtos(nome, unidade, preco_unidade)")
                .eq("empresa_id", ig.empresa_id)
                .order("data_movimentacao", desc=True)
                .execute()
            )
        except Exception as e:
            print(e)
            return ft.ResponsiveRow([])
        else:
            respostas_form = [
                [
                    row["id"],
                    row["operacao"],
                    row["classificacao"],
                    parser.isoparse(row["data_movimentacao"]),
                    row["nome"],
                    row["quantidade"],
                    row["unidade"],
                    self.obter_preco(row["preco_movimentacao"], row["preco_unidade"]),
                    row["informacoes"]
                ]
                for i, row in self.df.iterrows()
            ]
            movimentacoes = ft.ResponsiveRow([
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
            return movimentacoes
        
    def _estatisticas(self):
        if len(self.df):
            total_movimentacoes = len(self.df)
            total_entradas = self.df[self.df["operacao"] == "entrada"]["total_movimentado"].sum()
            total_saidas = self.df[self.df["operacao"] == "saída"]["total_movimentado"].sum()
        else:
            total_movimentacoes = 0
            total_entradas = 0
            total_saidas
        return total_movimentacoes, total_entradas, total_saidas

    def obter_preco(self, preco_mov, preco_uni):
        return preco_mov if pd.notna(preco_mov) else preco_uni
    
    def ler_dados(self):
        try:
            ig = InfosGlobal()
            client = SupabaseSingleton().get_client()
            respostas = (
                client.table("movimentacao")
                .select("id, operacao, data_movimentacao, quantidade, classificacao, preco_movimentacao, informacoes, produtos(nome, unidade, preco_unidade)")
                .eq("empresa_id", ig.empresa_id)
                .order("data_movimentacao", desc=True)
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self._criar_df(respostas.data)
            self._criar_conteudo()

    def _criar_df(self, dados):
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(dados)
        _ = pd.json_normalize(df['produtos'])
        df = pd.concat([df.drop(columns=['produtos']), _], axis=1)
        df = df.fillna({"classificacao": "Sem class.", "preco_movimentacao": df["preco_unidade"]})
        df["total_movimentado"] = df["quantidade"] * df["preco_movimentacao"]
        df["operacao"] = df["operacao"].str.lower()
        self.df = df

    def did_mount(self):
        self.placeholder()
        self.ler_dados()