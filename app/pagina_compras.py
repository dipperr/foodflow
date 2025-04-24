import flet as ft
import pandas as pd

from banco_de_dados import SupabaseSingleton
from controles import (
    BotaoTonal,
    RotuloColuna,
    CartaoIndicadores,
    InfosGlobal
)


class ControleBarraNavegacao:
    def __init__(self, barra, csb):
        self.barra = barra
        self.csb = csb

    def ocultar_barra(self):
        self.barra.visible = False
        self.barra.update()
        self.csb.visibilidade(False)
    
    def mostrar_barra(self):
        self.barra.visible = True
        self.barra.update()
        self.csb.visibilidade(True)


class CartaoListasFinalizadas(ft.Card):
    def __init__(self, nome, controle_bn):
        super().__init__(elevation=5)
        self.controle_bn = controle_bn
        self.painel = ft.Container(
            ft.Column([
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
                                                ft.Text("flv", col=5),
                                                ft.Column([
                                                    ft.Text("Qtd. de produtos", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("2", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Valor estimado", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("R$ 90,00", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Recebimento", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5),
                                                ft.Column([
                                                    ft.Text("Responsável", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.all(5)
                                        )
                                    )
                                ],
                                on_select_changed=lambda e: self.controle_bn.mostrar_barra()
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(
                                        ft.Container(
                                            ft.ResponsiveRow([
                                                ft.Text("flv", col=5),
                                                ft.Column([
                                                    ft.Text("Qtd. de produtos", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("2", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Valor estimado", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("R$ 90,00", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Recebimento", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5),
                                                ft.Column([
                                                    ft.Text("Responsável", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.all(5)
                                        )
                                    )
                                ],
                                on_select_changed=lambda e: self.controle_bn.mostrar_barra()
                            )
                        ],
                        heading_row_height=0,
                        column_spacing=10,
                        data_row_max_height=float("inf"),
                        horizontal_margin=0
                    )
                ])
            ], spacing=5), visible=False
        )
        self.botao_expandir = ft.IconButton(
            ft.Icons.ARROW_DROP_DOWN_ROUNDED,
            selected_icon=ft.Icons.ARROW_DROP_UP_ROUNDED,
            col=1.5,
            on_click=self.visibilidade_painel,
            icon_color=ft.Colors.BLACK87,
            selected_icon_color=ft.Colors.BLACK87,
            selected=False
        )
        self.content = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Text(nome, col=10.5, weight=ft.FontWeight.BOLD, size=15),
                    self.botao_expandir
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self.painel
            ]),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15),
            padding=ft.padding.symmetric(vertical=10, horizontal=10)
        )

    def visibilidade_painel(self, e):
        self.painel.visible = not self.painel.visible
        self.botao_expandir.selected = not self.botao_expandir.selected
        self.painel.update()
        self.botao_expandir.update()


class CartaoListasAndamento(ft.Card):
    def __init__(self, controle_bn):
        super().__init__(elevation=5)
        self.controle_bn = controle_bn
        self.content = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Text("Listas em andamentos", weight=ft.FontWeight.BOLD, col=4, size=15)
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
                                                ft.Text("flv", col=5),
                                                ft.Column([
                                                    ft.Text("Qtd. de produtos", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("2", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Valor estimado", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("R$ 90,00", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Recebimento", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5),
                                                ft.Column([
                                                    ft.Text("Responsável", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.all(5)
                                        )
                                    )
                                ],
                                on_select_changed=lambda e: self.controle_bn.mostrar_barra()
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(
                                        ft.Container(
                                            ft.ResponsiveRow([
                                                ft.Text("flv", col=5),
                                                ft.Column([
                                                    ft.Text("Qtd. de produtos", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("2", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Valor estimado", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("R$ 90,00", weight=ft.FontWeight.BOLD)
                                                ], col=2),
                                                ft.Column([
                                                    ft.Text("Recebimento", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5),
                                                ft.Column([
                                                    ft.Text("Responsável", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                    ft.Text("-", weight=ft.FontWeight.BOLD)
                                                ], col=1.5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.all(5)
                                        )
                                    )
                                ],
                                on_select_changed=lambda e: self.controle_bn.mostrar_barra()
                            )
                        ],
                        heading_row_height=0,
                        column_spacing=10,
                        data_row_max_height=float("inf"),
                        horizontal_margin=0
                    )
                ])
            ]), padding=ft.padding.all(10), bgcolor=ft.Colors.WHITE, border_radius=ft.border_radius.all(15)
        )





class PaginaCompras(ft.Stack):
    def __init__(self, controle_sombra):
        super().__init__()
        self.controle_sombra = controle_sombra

        self.barra_navegacao_lf = ft.Container(
            ft.ResponsiveRow([
                ft.Container(
                    ft.Column([
                        ft.Container(
                            ft.Column([
                                ft.Container(
                                    ft.Column([
                                        ft.ResponsiveRow([
                                            ft.Text("flv", weight=ft.FontWeight.BOLD, size=18, col=11),
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
                                                on_click=self.visualizacao_barra_lf
                                            )
                                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                        ft.Divider(),
                                        ft.Column([
                                            ft.Text("2 produto(s)", weight=ft.FontWeight.BOLD),
                                            ft.Text("Valor: R$ 90,00 *", weight=ft.FontWeight.BOLD),
                                            ft.Text("Essa lista contém um ou mais produtos sem preço.", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK54)
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
                                        ft.Text("Movimentações registradas", size=17, weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54),
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
                                                                                        ft.Text("Arroz japonês", weight=ft.FontWeight.BOLD)
                                                                                    ])
                                                                                ], col=4),
                                                                                ft.IconButton(
                                                                                    col=1.5,
                                                                                    content=ft.Image("./icons_clone/pencil.png", width=13, height=13),
                                                                                    style=ft.ButtonStyle(
                                                                                        shape=ft.RoundedRectangleBorder(5),
                                                                                        bgcolor=ft.Colors.BLUE_100,
                                                                                        elevation=5
                                                                                    ),
                                                                                    height=35
                                                                                ),
                                                                                ft.IconButton(
                                                                                    col=1.5,
                                                                                    content=ft.Image("./icons_clone/trash.png", width=13, height=13, color=ft.Colors.RED),
                                                                                    style=ft.ButtonStyle(
                                                                                        shape=ft.RoundedRectangleBorder(5),
                                                                                        bgcolor=ft.Colors.WHITE
                                                                                    ),
                                                                                    height=35
                                                                                ),
                                                                                ft.Column([
                                                                                    ft.Text("Quantidade", size=13,  weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54),
                                                                                    ft.Text("10", size=13, weight=ft.FontWeight.BOLD)
                                                                                ], col=2.5, spacing=5),
                                                                                ft.Column([
                                                                                    ft.Text("Preço unit.", size=13,  weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54),
                                                                                    ft.Text("R$ 9,00/und", size=13, weight=ft.FontWeight.BOLD)
                                                                                ], col=2.5, spacing=5)
                                                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                                                                            padding=ft.padding.only(left=5, top=10, right=5, bottom=10)
                                                                        )
                                                                    )
                                                                ]
                                                            )
                                                        ]*6,
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
            ], alignment=ft.MainAxisAlignment.END),
            expand=True,
            bgcolor=ft.Colors.BLACK26,
            visible=False
        )

        self.barra_navegacao_la = ft.Container(
            ft.ResponsiveRow([
                ft.Container(
                    ft.Column([
                        ft.Container(
                            ft.Column([
                                ft.Container(
                                    ft.Column([
                                        ft.ResponsiveRow([
                                            ft.Text("flv", weight=ft.FontWeight.BOLD, size=18, col=11),
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
                                                on_click=self.visualizacao_barra_la
                                            )
                                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                        ft.Divider(),
                                        ft.Column([
                                            ft.Text("2 produto(s)", weight=ft.FontWeight.BOLD),
                                            ft.Text("Valor: R$ 90,00 *", weight=ft.FontWeight.BOLD),
                                            ft.Text("Essa lista contém um ou mais produtos sem preço.", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK54)
                                        ]),
                                        ft.ResponsiveRow([
                                            ft.Card(
                                                ft.Container(
                                                    ft.Column([
                                                        ft.ResponsiveRow([
                                                            ft.Column([
                                                                ft.Text("Status:", weight=ft.FontWeight.BOLD),
                                                                ft.Text("Aguardando Recebimento", weight=ft.FontWeight.W_600)
                                                            ], spacing=5, col=6),
                                                            ft.Column([
                                                                ft.Text("Previsão de recebimento:", weight=ft.FontWeight.BOLD),
                                                                ft.Text("-", weight=ft.FontWeight.W_600)
                                                            ], spacing=5, col=6)
                                                        ]),
                                                        ft.Divider(),
                                                        ft.ResponsiveRow([
                                                            BotaoTonal(
                                                                "Confirmar Recebimento",
                                                                "./icons_clone/box-circle-check.png",
                                                                6,
                                                                ft.Colors.GREEN
                                                            )
                                                        ])
                                                    ]),
                                                    padding=ft.padding.all(20)
                                                ), elevation=5, col=12
                                            ),
                                            BotaoTonal(
                                                "Salvar Lista",
                                                "./icons_clone/disk.png",
                                                6
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
                                                ft.Card(
                                                    ft.Container(
                                                        ft.ResponsiveRow([
                                                            ft.Column([
                                                                ft.Text("Manga tommy", size=18, weight=ft.FontWeight.BOLD),
                                                                ft.Row([
                                                                    ft.Container(
                                                                        ft.Text("fruta", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                        border_radius=30,
                                                                        padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                                        alignment=ft.alignment.center
                                                                    )
                                                                ]),
                                                                ft.ResponsiveRow([
                                                                    ft.Column([
                                                                        ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, size=13, weight=ft.FontWeight.W_400),
                                                                        ft.Text("0 Kg", weight=ft.FontWeight.BOLD)
                                                                    ], col=6, spacing=5),
                                                                    ft.Column([
                                                                        ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, size=13, weight=ft.FontWeight.W_400),
                                                                        ft.Text("4 Kg", weight=ft.FontWeight.BOLD)
                                                                    ], col=6, spacing=5)
                                                                ])
                                                            ], col=8),
                                                            ft.Column([
                                                                ft.Container(
                                                                    ft.Column([
                                                                        ft.Text("Comprar"),
                                                                        ft.ResponsiveRow([
                                                                            ft.TextField(
                                                                                height=30,
                                                                                col=6, 
                                                                                cursor_height=13,
                                                                                content_padding=ft.padding.only(top=0, left=10),
                                                                                border_color=ft.Colors.BLACK54,
                                                                                cursor_color=ft.Colors.BLACK54
                                                                            ),
                                                                            ft.Text("und", size=13, weight=ft.FontWeight.BOLD, col=4)
                                                                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                                                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                                                    expand=True,
                                                                    bgcolor=ft.Colors.BLUE_100,
                                                                    border_radius=5,
                                                                    padding=ft.padding.all(7),
                                                                    border=ft.border.all(1, ft.Colors.BLUE),
                                                                ),
                                                                ft.ResponsiveRow([
                                                                    BotaoTonal(
                                                                        "Remover",
                                                                        "./icons_clone/trash.png",
                                                                        12,
                                                                        ft.Colors.WHITE,
                                                                        text_color=ft.Colors.RED,
                                                                        icon_color=ft.Colors.RED
                                                                    )
                                                                ])
                                                            ], col=4)
                                                        ]),
                                                        bgcolor=ft.Colors.WHITE,
                                                        padding=ft.padding.all(20),
                                                        border_radius=15
                                                    ), col=12, elevation=5
                                                )
                                            ])
                                        ], run_spacing=20),
                                        ft.Container(
                                        ft.Text("Adicionar outros produtos", weight=ft.FontWeight.BOLD),
                                            padding=ft.padding.only(top=30)
                                        ),
                                        ft.Divider(),
                                        ft.ResponsiveRow([
                                            ft.TextField(cursor_color=ft.Colors.BLACK54,
                                                border_radius=10,
                                                border_color=ft.Colors.BLACK54,
                                                col=12,
                                                height=35,
                                                label="Buscar produto...",
                                                cursor_height=15,
                                                content_padding=ft.padding.only(top=0, left=10),
                                                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
                                                label_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
                                            )
                                        ]),
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
                                                                                    ft.Text("Alho poró", weight=ft.FontWeight.BOLD),
                                                                                    ft.Text(
                                                                                        "HORTIFRUTI SANTA RITA | HORTIFRUTI BOM SUCESSO | GAUCHÃO",
                                                                                        max_lines=2,
                                                                                        overflow=ft.TextOverflow.ELLIPSIS,
                                                                                        size=12
                                                                                    ),
                                                                                    ft.Row([
                                                                                        ft.Container(
                                                                                            ft.Text("fruta", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                                            border_radius=30,
                                                                                            padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                                                            alignment=ft.alignment.center,
                                                                                        )
                                                                                    ])
                                                                                ], col=8, spacing=5),
                                                                                ft.Column([
                                                                                    ft.ResponsiveRow([
                                                                                        BotaoTonal(
                                                                                        "Adicionar à lista",
                                                                                        "./icons_clone/shopping-basket.png",
                                                                                        12
                                                                                    )
                                                                                    ])
                                                                                ], col=4)
                                                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                                                                            padding=ft.padding.only(left=0, top=10, right=0, bottom=10)
                                                                        )
                                                                    )
                                                                ]
                                                            ),
                                                            ft.DataRow(
                                                                cells=[
                                                                    ft.DataCell(
                                                                        ft.Container(
                                                                            ft.ResponsiveRow([
                                                                                ft.Column([
                                                                                    ft.Text("Arroz japonês", weight=ft.FontWeight.BOLD),
                                                                                    ft.Text(
                                                                                        "ATACADÃO | ASSAI | GAUCHÃO",
                                                                                        max_lines=2,
                                                                                        overflow=ft.TextOverflow.ELLIPSIS,
                                                                                        size=12
                                                                                    ),
                                                                                    ft.Row([
                                                                                        ft.Container(
                                                                                            ft.Text("condimentos", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                                            border_radius=30,
                                                                                            padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                                                            alignment=ft.alignment.center,
                                                                                        )
                                                                                    ])
                                                                                ], col=8, spacing=5),
                                                                                ft.Column([
                                                                                    ft.ResponsiveRow([
                                                                                        BotaoTonal(
                                                                                        "Adicionar à lista",
                                                                                        "./icons_clone/shopping-basket.png",
                                                                                        12
                                                                                    )
                                                                                    ])
                                                                                ], col=4)
                                                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                                                                            padding=ft.padding.only(left=0, top=10, right=0, bottom=10)
                                                                        )
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                        heading_row_height=0,
                                                        column_spacing=0,
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
                            expand=True)
                    ]),
                    col=7,
                    expand=True,
                    bgcolor=ft.Colors.GREY_100,
                )
            ], alignment=ft.MainAxisAlignment.END),
            expand=True,
            bgcolor=ft.Colors.BLACK26,
            visible=False
        )

        self.barra_lista_compras = ft.Container(
            ft.ResponsiveRow([
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
                                                on_click=self.ocultar_barra_lista_compra
                                            )
                                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                        ft.Divider(),
                                        ft.Column([
                                            ft.Text("2 produto(s)", weight=ft.FontWeight.BOLD),
                                            ft.Text("Valor: R$ 90,00", weight=ft.FontWeight.BOLD)
                                        ]),
                                        ft.ResponsiveRow([
                                            BotaoTonal(
                                                "Salvar Lista",
                                                "./icons_clone/disk.png",
                                                6
                                            ),
                                            BotaoTonal(
                                                "Exportar",
                                                "./icons_clone/file-export.png",
                                                6
                                            ),
                                            ft.ResponsiveRow([
                                                ft.Card(
                                                    ft.Container(
                                                        ft.ResponsiveRow([
                                                            ft.Column([
                                                                ft.Text("Manga tommy", size=18, weight=ft.FontWeight.BOLD),
                                                                ft.Row([
                                                                    ft.Container(
                                                                        ft.Text("fruta", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                        border_radius=30,
                                                                        padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                                        alignment=ft.alignment.center
                                                                    )
                                                                ]),
                                                                ft.ResponsiveRow([
                                                                    ft.Column([
                                                                        ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, size=13, weight=ft.FontWeight.W_400),
                                                                        ft.Text("0 Kg", weight=ft.FontWeight.BOLD)
                                                                    ], col=6, spacing=5),
                                                                    ft.Column([
                                                                        ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, size=13, weight=ft.FontWeight.W_400),
                                                                        ft.Text("4 Kg", weight=ft.FontWeight.BOLD)
                                                                    ], col=6, spacing=5)
                                                                ])
                                                            ], col=8),
                                                            ft.Column([
                                                                ft.Container(
                                                                    ft.Column([
                                                                        ft.Text("Comprar"),
                                                                        ft.ResponsiveRow([
                                                                            ft.TextField(
                                                                                height=30,
                                                                                col=6, 
                                                                                cursor_height=13,
                                                                                content_padding=ft.padding.only(top=0, left=10),
                                                                                border_color=ft.Colors.BLACK54,
                                                                                cursor_color=ft.Colors.BLACK54
                                                                            ),
                                                                            ft.Text("und", size=13, weight=ft.FontWeight.BOLD, col=4)
                                                                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                                                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                                                    expand=True,
                                                                    bgcolor=ft.Colors.BLUE_100,
                                                                    border_radius=5,
                                                                    padding=ft.padding.all(7),
                                                                    border=ft.border.all(1, ft.Colors.BLUE),
                                                                ),
                                                                ft.ResponsiveRow([
                                                                    BotaoTonal(
                                                                        "Remover",
                                                                        "./icons_clone/trash.png",
                                                                        12,
                                                                        ft.Colors.WHITE,
                                                                        text_color=ft.Colors.RED,
                                                                        icon_color=ft.Colors.RED
                                                                    )
                                                                ])
                                                            ], col=4)
                                                        ]),
                                                        bgcolor=ft.Colors.WHITE,
                                                        padding=ft.padding.all(20),
                                                        border_radius=15
                                                    ), col=12, elevation=5
                                                )
                                            ]*3)
                                        ], run_spacing=20)
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
            ], alignment=ft.MainAxisAlignment.END),
            expand=True,
            bgcolor=ft.Colors.BLACK26,
            visible=False
        )

        self.controle_bn_lf = ControleBarraNavegacao(self.barra_navegacao_lf, controle_sombra)
        self.controle_bn_la = ControleBarraNavegacao(self.barra_navegacao_la, controle_sombra)
        self.controle_bn_listacp = ControleBarraNavegacao(self.barra_lista_compras, controle_sombra)

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
                            on_click=self.ir_pagina_lista
                            ),
                            BotaoTonal("Gerenciar Fornecedores", "./icons_clone/shop.png", 3)
                        ]),
                        CartaoListasAndamento(self.controle_bn_la),
                        CartaoListasFinalizadas(
                            "Listas Finalizadas",
                            self.controle_bn_lf
                        )
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

        self.pagina_lista = [
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
                                                    ft.Text("LISTA DE COMPRAS"),
                                                    ft.Text("Vazia")
                                                ], col=9, spacing=5)
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            padding=ft.padding.only(top=10, bottom=10, left=0, right=0)
                                        ),
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(5)),
                                        bgcolor=ft.Colors.GREEN,
                                        on_click=self.visualizar_barra_lista_compra
                                    )
                                ], col=3, alignment=ft.MainAxisAlignment.END)
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Divider(),
                            ft.ResponsiveRow([
                                ft.Card(
                                    ft.Container(
                                        ft.ResponsiveRow([
                                            BotaoTonal(
                                                "Salvar Lista",
                                                "./icons_clone/disk.png",
                                                2.5
                                            ),
                                            BotaoTonal(
                                                "Exportar",
                                                "./icons_clone/file-export.png",
                                                2.5
                                            )
                                        ]),
                                        padding=ft.padding.all(20),
                                        border_radius=15,
                                        bgcolor=ft.Colors.WHITE
                                    ), col=12, elevation=5
                                )
                            ]),
                            ft.Container(
                                ft.Column([
                                    ft.Text("Selecionar produtos", size=17, weight=ft.FontWeight.BOLD),
                                    ft.Text("Selecione os produtos que deseja adicionar à lista de compras.", size=14, color=ft.Colors.BLACK54)
                                ], spacing=5), padding=ft.padding.only(top=20), 
                            ),
                            ft.Divider(),
                            ft.ResponsiveRow([
                                ft.Dropdown(
                                    label="Filtrar categorias(s)",
                                    col=4,
                                    border_width=1,
                                    elevation=5
                                ),
                                ft.Dropdown(
                                    label="Filtrar fornecedores(s)",
                                    col=4,
                                    border_width=1,
                                    elevation=5
                                ),
                                ft.Dropdown(
                                    label="Filtrar produtos(s)",
                                    col=4,
                                    border_width=1,
                                    elevation=5
                                )
                            ]),
                            ft.ResponsiveRow([
                                ft.Card(
                                    ft.Container(
                                        ft.Column([
                                            ft.ResponsiveRow([
                                                ft.Row([
                                                    ft.Switch(
                                                        label="Visualizar apenas produtos abaixo do estoque mínimo",
                                                        height=30
                                                    )
                                                ], col=6),
                                                ft.Text("1 produto(s) encontrado(s)", col=3, weight=ft.FontWeight.BOLD),
                                                BotaoTonal(
                                                    "Adicionar todos à lista",
                                                    "./icons_clone/shopping-basket.png",
                                                    3
                                                )
                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                            ft.Container(
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
                                                                                ft.Column([
                                                                                    ft.Text("Arroz japonês", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                                    ft.Row([
                                                                                        ft.Container(
                                                                                            ft.Text("condimentos", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                                            border_radius=30,
                                                                                            padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                                                            alignment=ft.alignment.center
                                                                                        )
                                                                                    ])
                                                                                ], col=4.1),
                                                                                ft.Container(
                                                                                    ft.Column([
                                                                                        ft.Text("Comprar", color=ft.Colors.BLACK54, size=13, max_lines=1, overflow=ft.TextOverflow),
                                                                                        ft.ResponsiveRow([
                                                                                            ft.TextField(
                                                                                                height=30,
                                                                                                col=6, 
                                                                                                cursor_height=13,
                                                                                                content_padding=ft.padding.only(top=0, left=10),
                                                                                                border_color=ft.Colors.BLACK54,
                                                                                                cursor_color=ft.Colors.BLACK54
                                                                                            ),
                                                                                            ft.Text("und", size=13, weight=ft.FontWeight.BOLD, col=4)
                                                                                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                                                                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                                                                    col=2,
                                                                                    bgcolor=ft.Colors.BLUE_100,
                                                                                    border_radius=5,
                                                                                    padding=ft.padding.all(5),
                                                                                    border=ft.border.all(1, ft.Colors.BLUE)
                                                                                ),
                                                                                ft.Column([
                                                                                    ft.ResponsiveRow([
                                                                                        BotaoTonal(
                                                                                            "Adicionar à lista",
                                                                                            "./icons_clone/shopping-basket.png",
                                                                                            12
                                                                                        )
                                                                                    ])
                                                                                ], col=2.3),
                                                                                ft.Column([
                                                                                    ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                                                    ft.Text("25 und", weight=ft.FontWeight.BOLD)
                                                                                ], col=1.8),
                                                                                ft.Column([
                                                                                    ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                                                    ft.Text("20 und", weight=ft.FontWeight.BOLD)
                                                                                ], col=1.8)
                                                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                                                                            padding=ft.padding.all(10)
                                                                        )
                                                                    )
                                                                ]
                                                            ),
                                                            ft.DataRow(
                                                                cells=[
                                                                    ft.DataCell(
                                                                        ft.Container(
                                                                            ft.ResponsiveRow([
                                                                                ft.Column([
                                                                                    ft.Text("Limão", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                                    ft.Row([
                                                                                        ft.Container(
                                                                                            ft.Text("fruta", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                                                            border_radius=30,
                                                                                            padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                                                            alignment=ft.alignment.center
                                                                                        )
                                                                                    ])
                                                                                ], col=4.1),
                                                                                ft.Container(
                                                                                    ft.Column([
                                                                                        ft.Text("Comprar", color=ft.Colors.BLACK54, size=13, max_lines=1, overflow=ft.TextOverflow),
                                                                                        ft.ResponsiveRow([
                                                                                            ft.TextField(
                                                                                                height=30,
                                                                                                col=6, 
                                                                                                cursor_height=13,
                                                                                                content_padding=ft.padding.only(top=0, left=10),
                                                                                                border_color=ft.Colors.BLACK54,
                                                                                                cursor_color=ft.Colors.BLACK54
                                                                                            ),
                                                                                            ft.Text("und", size=13, weight=ft.FontWeight.BOLD, col=4)
                                                                                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                                                                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                                                                                    col=2,
                                                                                    bgcolor=ft.Colors.BLUE_100,
                                                                                    border_radius=5,
                                                                                    padding=ft.padding.all(5),
                                                                                    border=ft.border.all(1, ft.Colors.BLUE)
                                                                                ),
                                                                                ft.Column([
                                                                                    ft.ResponsiveRow([
                                                                                        BotaoTonal(
                                                                                            "Adicionar à lista",
                                                                                            "./icons_clone/shopping-basket.png",
                                                                                            12
                                                                                        )
                                                                                    ])
                                                                                ], col=2.3),
                                                                                ft.Column([
                                                                                    ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                                                    ft.Text("25 und", weight=ft.FontWeight.BOLD)
                                                                                ], col=1.8),
                                                                                ft.Column([
                                                                                    ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                                                    ft.Text("20 und", weight=ft.FontWeight.BOLD)
                                                                                ], col=1.8)
                                                                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                                                                            padding=ft.padding.all(10)
                                                                        )
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                        heading_row_height=0,
                                                        column_spacing=10,
                                                        data_row_max_height=float("inf"),
                                                        horizontal_margin=0
                                                    )
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
        
        self.controls = self.pagina_inicial

    def placeholder(self):
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _criar_cartoes_indicadores(self):
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

    def visualizar_barra_lista_compra(self, e):
        self.controle_bn_listacp.mostrar_barra()

    def ocultar_barra_lista_compra(self, e):
        self.controle_bn_listacp.ocultar_barra()

    def ir_pagina_lista(self, e):
        self.controls = self.pagina_lista
        self.update()

    def ir_pagina_inicial(self, e):
        self.controls = self.pagina_inicial
        self.update()

    def visualizacao_barra_lf(self, e):
        self.controle_bn_lf.ocultar_barra()

    def visualizacao_barra_la(self, e):
        self.controle_bn_la.ocultar_barra()

    def ler_dados_produtos(self):
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
