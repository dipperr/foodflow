import flet as ft
from typing import Optional, Callable, List


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
        
        itens_por_coluna = len(itens) // num_colunas
        restante = len(itens) % num_colunas

        colunas = []
        for i in range(num_colunas):
            inicio = i * itens_por_coluna + min(i, restante)
            fim = (i + 1) * itens_por_coluna + min(i + 1, restante)
            
            coluna = ft.Column([item for item in itens[inicio:fim]], col=12 // num_colunas)
            colunas.append(coluna)
        
        self.controls = colunas


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
        subtitulo: str=None,
        value: str=None,
        placeholder: str=None,
        on_change: Callable=None,
        input_filter: Callable=None,
        visible: bool=True
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
            mostrar_botao: Callable[[None], None]=None
        ) -> None:
        super().__init__(
            col=3,
            border=ft.border.all(1, ft.Colors.BLACK54),
            border_radius=5,
            padding=ft.padding.all(7),
            alignment=ft.alignment.center
        )

        self.mostrar_botao = mostrar_botao
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

    def limpar(self) -> None:
        for item in self.menu.items:
            item.checked = False
        self.menu.update()
