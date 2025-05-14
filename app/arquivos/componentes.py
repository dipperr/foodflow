import flet as ft
from typing import Optional, Callable, List
import locale
import pandas as pd
from datetime import datetime

from controles import ControleMovimentacao

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class SeletorTemporal(ft.SegmentedButton):
    def __init__(self, on_change: Optional[Callable]=None) -> None:
        super().__init__(
            selected={"30"},
            segments=[
                ft.Segment(
                    value="365",
                    label=ft.Text("1 a"),
                ),
                ft.Segment(
                    value="90",
                    label=ft.Text("90 d"),
                ),
                ft.Segment(
                    value="30",
                    label=ft.Text("30 d"),
                ),
                ft.Segment(
                    value="7",
                    label=ft.Text("7 d")
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
            show_selected_icon=False,
            on_change=on_change
        )

    @property
    def valor(self):
        return self.selected


class CabecalhoCartao(ft.ListTile):
    def __init__(self, titulo: str, subtitulo: str, icone_path: str):
        super().__init__(
            title=ft.Text(titulo),
            subtitle=ft.Text(subtitulo),
            trailing=ft.Image(icone_path),
            title_text_style=ft.TextStyle(color=ft.Colors.BLACK87, weight=ft.FontWeight.BOLD, size=17),
            content_padding=ft.padding.all(0),
            bgcolor=ft.Colors.WHITE
        )


class MarcacoesCores(ft.Row):
    def __init__(self, rotulos: List, cores: List) -> None:
        super().__init__(
            controls=[
                ft.Row([
                    ft.CircleAvatar(bgcolor=cor, radius=5), ft.Text(rotulo)
                ])
                for rotulo, cor in zip(rotulos, cores)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )


class Evento:
    def __init__(self, data: str) -> None:
        self.data = data


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


class GradeNotificacao(ft.ResponsiveRow):
    def __init__(self, itens: list, num_colunas: int=2):
        super().__init__()
        self.num_colunas = num_colunas
        self.itens = itens
        self._criar_conteudo()

    def _criar_conteudo(self):
        itens_por_coluna = len(self.itens) // self.num_colunas
        restante = len(self.itens) % self.num_colunas

        colunas = []
        for i in range(self.num_colunas):
            inicio = i * itens_por_coluna + min(i, restante)
            fim = (i + 1) * itens_por_coluna + min(i + 1, restante)
            
            coluna = ft.Column([item for item in self.itens[inicio:fim]], col=12 // self.num_colunas)
            colunas.append(coluna)
        
        self.controls = colunas

    def reiniciar_grade(self):
        self._criar_conteudo()
        self.update()


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
    def __init__(self, categoria, cor):
        super().__init__()
        self.content = ft.Text(categoria, weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        self.bgcolor=eval(f"ft.{cor}")
        self.border_radius=30
        self.col=int(len(categoria) / 2) + 1
        self.padding=ft.padding.only(left=10, top=5, right=10, bottom=5)
        self.alignment=ft.alignment.center


class TextField(ft.Column):
    def __init__(
        self,
        label: str,
        col: int,
        subtitulo: Optional[str]=None,
        value: Optional[str]=None,
        placeholder: Optional[str]=None,
        on_change: Optional[Callable]=None,
        input_filter: Optional[Callable]=None,
        visible: Optional[bool]=True,
        prefix: Optional[str]=None
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
            prefix_text=prefix
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
    def value(self) -> str:
        return self.entrada.value if self.entrada.value else None
    
    def atualizar_rotulo(self, rotulo: str) -> None:
        self.controls[0].value = rotulo
        self.controls[0].update()


class Filtro(ft.Container):
    def __init__(
            self,
            rotulo: str,
            itens: List[str],
            checked: int=None,
            mostrar_botao: Callable[[None], None]=None,
            acao: Callable[[str], None]=None
        ) -> None:
        super().__init__(
            col=3,
            border=ft.border.all(1, ft.Colors.BLACK54),
            border_radius=5,
            padding=ft.padding.all(7),
            alignment=ft.alignment.center
        )

        self.mostrar_botao = mostrar_botao
        self.acao = acao
        self.checked = checked
        self.itens = itens
        self.menu = ft.PopupMenuButton(
            content=ft.ResponsiveRow([
                ft.Image("./icons_clone/bars-filter.png", col=2, width=16, height=16),
                ft.Text(rotulo, col=8, weight=ft.FontWeight.W_500),
                ft.Image("./icons_clone/angles-up-down.png", width=16, height=16, col=2)
            ], vertical_alignment=ft.MainAxisAlignment.CENTER),
            items=self._criar_itens(),
            bgcolor=ft.Colors.WHITE,
            tooltip=""
        )
        self.content = self.menu

    def _criar_itens(self) -> List[ft.PopupMenuItem]:
        return [
            ft.PopupMenuItem(
                text=label,
                checked=(self.checked == i),
                on_click=self._ao_clicar_item
            )
            for i, label in enumerate(self.itens)
        ]

    def _ao_clicar_item(self, e: ft.ControlEvent) -> None:
        if self.checked is None and self.mostrar_botao:
            self.mostrar_botao()

        for item in self.menu.items:
            item.checked = (item.text == e.control.text)

        self.menu.update()
        if self.acao is not None:
            self.acao(e.control.text)

    def limpar(self) -> None:
        for item in self.menu.items:
            item.checked = False
        self.menu.update()


class CapsulaDropdown(ft.Container):
    def __init__(self, rotulo: str, id: int, on_click: Callable[[int], None]) -> None:
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
            col=len(rotulo) / 2 + 4
        )
        self.rotulo = rotulo
        self.id = id

    @property
    def value(self) -> dict:
        return {"id": self.id, "nome": self.rotulo}


class DropdownV2(ft.PopupMenuButton):
    def __init__(self, rotulos: dict, ids: List[int] = []) -> None:
        super().__init__(
            tooltip="",
            size_constraints=ft.BoxConstraints(max_height=250, min_width=200),
            bgcolor=ft.Colors.WHITE
        )
        self.rotulos = rotulos
        self.area_botao = ft.ResponsiveRow([], spacing=5)
        self._criar_interface()
        self._carregar_itens_menu()
        if len(ids) > 0:
            self._carregar_valores_iniciais(ids)

    @property
    def value(self) -> Optional[list]:
        return [capsula.value for capsula in self.area_botao.controls] or None

    def _criar_interface(self) -> None:
        self.content = ft.Container(
            content=ft.ResponsiveRow(
                [
                    ft.Container(
                        self.area_botao,
                        padding=ft.padding.only(left=5, bottom=5, right=5),
                        border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.BLACK54)),
                        expand=True,
                        col=10
                    ),
                    ft.Column(
                        [ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.BLACK54)],
                        col=2
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=0
            ),
            padding=ft.padding.only(top=10, bottom=10),
            alignment=ft.alignment.center,
            width=230,
            border_radius=15,
            border=ft.border.all(1, ft.Colors.BLACK54)
        )

    def _carregar_itens_menu(self) -> None:
        self.items = [
            ft.PopupMenuItem(
                text=label,
                on_click=lambda e, id=key: self._adicionar_item(id)
            )
            for key, label in self.rotulos.items()
        ]

    def _carregar_valores_iniciais(self, ids: list) -> None:
        for id in ids:
            self._adicionar_item(id, atualizar=False)

    def _adicionar_item(self, id: int, atualizar: bool=True) -> None:
        if any(capsula.value == id for capsula in self.area_botao.controls):
            return  # evita itens duplicados
        self.area_botao.controls.append(
            CapsulaDropdown(self.rotulos[id], id, self.excluir)
        )
        if atualizar:
            self.area_botao.update()

    def atualizar_itens(self, id: int, nome: str) -> None:
        self.rotulos[id] = nome
        self._carregar_itens_menu()
        self.update()

    def excluir(self, id: int) -> None:
        self.area_botao.controls = [
            capsula for capsula in self.area_botao.controls if int(capsula.id) != int(id)
        ]
        self.area_botao.update()


class FiltroEntrada(ft.InputFilter):
    def __init__(self):
        super().__init__(
            regex_string=r"^(\d+(,\d*)?)?$",
            replacement_string="",
            allow=True
        )


class JanelaEditarMovimentacao(ft.AlertDialog):
    def __init__(self, movimentacao, controle_movimentacoes) -> None:
        super().__init__(modal=True, bgcolor=ft.Colors.WHITE,)
        self.movimentacao = movimentacao
        self.controle_movimentacoes = controle_movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
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
                                self.entrada_acao
                            ], col=6),
                            ft.Column([
                                ft.Text("CLASSIFICAR AÇÃO",weight=ft.FontWeight.W_500),
                                self.entrada_classificar_acao
                            ], col=6),
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE",weight=ft.FontWeight.W_500),
                                self.entrada_unidade
                            ], col=6),
                            self.entrada_qtd
                        ]),
                        ft.ResponsiveRow([
                            self.entrada_preco,
                            self.entrada_dt_movimentacao
                        ]),
                        ft.Column([
                            ft.Divider(),
                            ft.ResponsiveRow([
                                self.botao_cancelar,
                                self.botao_confirmar
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=410, width=500
        )    

    def _criar_entradas(self) -> None:
        preco = self.movimentacao.valor_unit if not pd.isnull(self.movimentacao.valor_unit) else 0
        self.entrada_acao = self._criar_dropdown(
            [self.movimentacao.operacao],
            self.movimentacao.operacao
        )
        self.entrada_classificar_acao = self._criar_dropdown(
            [],
            None,
            False,
            self._liberar_botao_confirmar
        )
        self.entrada_unidade = self._criar_dropdown(
            [self.movimentacao.unidade],
            self.movimentacao.unidade
        )
        self.entrada_qtd = TextField(
            "QUANTIDADE",
            6,
            value=locale.currency(self.movimentacao.qtd, grouping=True, symbol=False),
            input_filter=FiltroEntrada(),
            on_change=self._liberar_botao_confirmar
        )
        self.entrada_preco = TextField(
            f"PRECO POR {self.movimentacao.unidade.upper()}",
            6,
            "Preço de custo por unidade do produto.",
            value=locale.currency(preco, grouping=True, symbol=False),
            visible=False,
            input_filter=FiltroEntrada(),
            prefix="R$ "
        )
        self.entrada_dt_movimentacao = TextField(
            "DATA MOVIMENTAÇÃO",
            6,
            value=datetime.now().strftime("%d/%m/%Y"),
            on_change=self._liberar_botao_confirmar
        )

    def _criar_dropdown(
        self,
        options: List,
        value: str,
        disabled: bool=True,
        on_change: Callable=None
    ) -> None:
        return ft.Dropdown(
            options=[
                ft.dropdown.Option(acao)
                for acao in options
            ],
            value=value,
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            disabled=disabled,
            on_change=on_change
        )

    def _criar_botoes(self) -> None:
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.botao_confirmar = ft.OutlinedButton(
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

    def _liberar_botao_confirmar(self, e: ft.ControlEvent) -> None:
        values = [
            self.entrada_classificar_acao.value,
            self.entrada_qtd.value,
            self.entrada_dt_movimentacao.value
        ]
        self.botao_confirmar.disabled = not all(values)
        self.botao_confirmar.update()

    def _acao(self, acao: str) -> None:
        self._estado_padrao()
        self._estado_padrao()

        acoes = {
            "entrada": self._acao_entrada,
            "saída": self._acao_saida,
            "inventário": self._acao_inventario
        }

        if acao in acoes:
            acoes[acao]()
        
    def _estado_padrao(self) -> None:
        self.entrada_classificar_acao.options.clear()
        self.entrada_classificar_acao.update()

    def _acao_entrada(self) -> None:
        self._setar_opcoes_classificacao(["Compras", "Produção", "Transferência"])
        self.entrada_preco.visible = True
        self.entrada_preco.update()

    def _acao_saida(self) -> None:
        self._setar_opcoes_classificacao(["Vendas", "Consumo interno", "Transferência", "Desperdício"])

    def _acao_inventario(self) -> None:
        self.entrada_preco.visible = False
        self.entrada_preco.update()

    def _setar_opcoes_classificacao(self, opcoes: list[str]) -> None:
        self.entrada_classificar_acao.options = [
            ft.dropdown.Option(valor) for valor in opcoes
        ]
        self.entrada_classificar_acao.update()

    def salvar_movimentacao(self, e: ft.ControlEvent) -> None:
        self.controle_movimentacoes.atualizar(
            self.movimentacao.id,
            self.entrada_classificar_acao.value,
            self.entrada_qtd.value,
            self.movimentacao.qtd,
            self.movimentacao.qtd_estoque,
            self.entrada_preco.value,
            self.movimentacao.produto_id
        )
        self.page.close(self)

    def did_mount(self) -> None:
        self._acao(self.movimentacao.operacao.lower())


class JanelaCancelarMovimentacao(ft.AlertDialog):
    def __init__(self, movimentacao_id, controle_acao) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Cancelar movimentação"),
            actions_padding=ft.padding.all(0)
        )
        self.movimentacao_id = movimentacao_id
        self.controle_acao = controle_acao
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Confirma o cancelamento da movimentação?"),
                ft.ResponsiveRow([
                    self.botao_sim,
                    self.botao_nao,
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=20),
            width=400,
            height=70
        )

    def _criar_botoes(self) -> None:
        self.botao_sim = ft.OutlinedButton(
            text="SIM",
            col=4,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_100,
                side=ft.BorderSide(color=ft.Colors.WHITE, width=1),
                text_style=ft.TextStyle(foreground=ft.Paint(ft.Colors.BLACK), weight=ft.FontWeight.W_500)
            ),
            on_click=self.sim
        )
        self.botao_nao = ft.OutlinedButton(
            text="NÃO",
            col=4,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.WHITE,
                side=ft.BorderSide(color=ft.Colors.WHITE, width=1),
                text_style=ft.TextStyle(foreground=ft.Paint(ft.Colors.RED), weight=ft.FontWeight.W_500)
            ),
            on_click=self.nao
        )

    def nao(self, e: ft.ControlEvent) -> None:
        self.page.close(self)

    def sim(self, e: ft.ControlEvent) -> None:
        ...


class LinhaHistorico(ft.ExpansionTile):
    def __init__(self, movimentacao, controle_painel=None):
        super().__init__(
            title=ft.Row(),
            shape=ft.RoundedRectangleBorder(0)
        )
        self.movimentacao = movimentacao
        self.controle_painel = controle_painel
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        icones = {
            "saída": {
                "path": "./icons_clone/arrow-left16.png",
                "cor": ft.Colors.RED
            },
            "entrada": {
                "path": "./icons_clone/arrow-right16.png",
                "cor": ft.Colors.GREEN
            },
            "inventário": {
                "path": "./icons_clone/list16.png",
                "cor": ft.Colors.GREY
            }
        }
        self._criar_textos()
        self.title = ft.ResponsiveRow([
            ft.Text(self.movimentacao.data.strftime("%b %d").upper(), col=1, weight=ft.FontWeight.W_600),
            ft.Image(
                icones[self.movimentacao.operacao.lower()]["path"],
                color=icones[self.movimentacao.operacao.lower()]["cor"],
                col=0.5
            ),
            ft.Column([
                ft.Text(self.movimentacao.nome, weight=ft.FontWeight.W_600, size=15),
                self.texto_classificacao
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
                            self.texto_quantidade
                        ], run_spacing=0, spacing=0), col=4,
                    ),
                    ft.Container(
                        ft.ResponsiveRow([
                            ft.Text("Valor unit.", col=12, size=12, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            self.texto_valor_unit
                        ], run_spacing=0, spacing=0), col=4
                    ),
                    ft.Container(
                        ft.ResponsiveRow([
                            ft.Text("Valor total", col=12, size=12, color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            self.texto_valor_total
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

    def _criar_textos(self) -> None:
        self.texto_classificacao = ft.Text(
            self.movimentacao.classificacao if self.movimentacao.classificacao is not None else "Sem class.",
            size=12,
            weight=ft.FontWeight.W_600
        )
        self.texto_quantidade = ft.Text(
            self._criar_texto_quantidade(self.movimentacao.qtd, self.movimentacao.unidade, self.movimentacao.operacao),
            col=12,
            size=15,
            weight=ft.FontWeight.BOLD
        )
        self.texto_valor_unit = ft.Text(
            locale.currency(self._formatar_preco(self.movimentacao.valor_unit), grouping=True),
            col=12,
            size=15,
            weight=ft.FontWeight.BOLD
        )
        self.texto_valor_total = ft.Text(
            locale.currency(self._valor_total(self.movimentacao.valor_unit, self.movimentacao.qtd), grouping=True),
            col=12,
            size=15,
            weight=ft.FontWeight.BOLD
        )

    def _criar_texto_quantidade(self, qtd: float, unidade: str, operacao: str) -> str:
        qtd = self._formatar_quantidade(qtd)
        unidade = unidade.split(" ")[1].strip("()")
        op = "+" if operacao.lower() == "entrada" else "-"
        return f"{op}{qtd} {unidade}" 

    def _formatar_quantidade(self, quantidade: float) -> str:
        return locale.currency(quantidade, grouping=True, symbol=False)

    def _formatar_preco(self, preco: Optional[float]) -> float:
        return preco if pd.notna(preco) else 0.0
    
    def _valor_total(self, preco: float, quantidade: float) -> float:
        return self._formatar_preco(preco) * quantidade

    def atualizar_infos(self, classificacao: str, qtd: float, valor_unit: float) -> None:
        self._atualizar_campo(self.texto_classificacao, classificacao)
        self._atualizar_campo(
            self.texto_quantidade,
            self._criar_texto_quantidade(qtd, self.movimentacao.unidade, self.movimentacao.operacao)
        )
        self._atualizar_campo(self.texto_valor_unit, locale.currency(valor_unit, grouping=True))
        self._atualizar_campo(self.texto_valor_total, locale.currency(self._valor_total(valor_unit, qtd), grouping=True))

    def _atualizar_campo(self, campo, valor) -> None:
        campo.value = valor
        campo.update()

    def abrir_janela_edicao(self, e: ft.ControlEvent) -> None:
        controle = ControleMovimentacao(self.controle_painel)
        janela = JanelaEditarMovimentacao(self.movimentacao, controle)
        self.page.open(janela)

    def _abrir_janela_cancelar(self, e: ft.ControlEvent) -> None:
        ...
