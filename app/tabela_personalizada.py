import flet as ft

from controles import CapsulaCategoria, BotaoTonal

BC_CAPSULA = {
    "fruta": ft.Colors.GREEN_100,
    "vegetal": ft.Colors.GREEN_100,
    "legume": ft.Colors.ORANGE_100,
    "condimentos": ft.Colors.YELLOW_100
}


BG_CAPSULA = {
    "fruta": ft.Colors.GREEN,
    "vegetal": ft.Colors.GREEN,
    "legume": ft.Colors.ORANGE,
    "condimentos": ft.Colors.YELLOW
}


def main(page: ft.Page):

    page.add(
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
                                                ft.Row([
                                                    ft.Text("Arroz japonês"),
                                                    ft.Container(
                                                        ft.Text("condimentos", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                        bgcolor=BC_CAPSULA["condimentos".lower()],
                                                        border_radius=30,
                                                        padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                        alignment=ft.alignment.center,
                                                        border=ft.border.all(1, BG_CAPSULA["condimentos".lower()]),
                                                    )
                                                    ])
                                            ], col=5),
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
                                            ], col=2),
                                            ft.Column([
                                                ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                ft.Text("25 und", weight=ft.FontWeight.BOLD)
                                            ], col=1.5),
                                            ft.Column([
                                                ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                ft.Text("20 und", weight=ft.FontWeight.BOLD)
                                            ], col=1.5)
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
                                                ft.Row([
                                                    ft.Text("Limão"),
                                                    ft.Container(
                                                        ft.Text("fruta", weight=ft.FontWeight.W_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                                        bgcolor=BC_CAPSULA["fruta".lower()],
                                                        border_radius=30,
                                                        padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
                                                        alignment=ft.alignment.center,
                                                        border=ft.border.all(1, BG_CAPSULA["fruta".lower()]),
                                                    )
                                                    ]),
                                            ], col=5),
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
                                            ], col=2),
                                            ft.Column([
                                                ft.Text("Qtd. em estoque", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                ft.Text("25 und", weight=ft.FontWeight.BOLD)
                                            ], col=1.5),
                                            ft.Column([
                                                ft.Text("Estoque mínimo", color=ft.Colors.BLACK54, max_lines=1, overflow=ft.TextOverflow),
                                                ft.Text("20 und", weight=ft.FontWeight.BOLD)
                                            ], col=1.5)
                                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                                        padding=ft.padding.all(10)
                                    )
                                )
                            ]
                        )
                    ],
                    heading_row_height=0,
                    column_spacing=10,
                    data_row_max_height=float("inf")
                )
            ])
        )
    )

ft.app(main)
