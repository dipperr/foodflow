import flet as ft


class CapsulaDropdown(ft.Container):
    def __init__(self, rotulo: str, id: int, on_click):
        super().__init__(
            content=ft.ResponsiveRow([
                ft.Text(rotulo, size=13, col=9.5, weight=ft.FontWeight.W_500),
                ft.TextButton(
                    "X",
                    col=2.5,
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
                        padding=ft.padding.all(3)
                    ),
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

    @property
    def value(self):
        return self.rotulo


class DropDownEntry(ft.PopupMenuButton):
    def __init__(self, labels: list):
        super().__init__(
            surface_tint_color=ft.Colors.WHITE,
            tooltip="",
            size_constraints=ft.BoxConstraints(max_height=100)
        )
        self.labels = labels
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
            ft.PopupMenuItem(text=label, on_click=lambda e, id=i: self.adicionar_item(id))
            for i, label in enumerate(self.labels)
        ]

    @property
    def value(self):
        if self.area_botao.controls:
            return [capsula.value for capsula in self.area_botao.controls]
        else:
            return None

    def adicionar_item(self, id):
        self.area_botao.controls.append(
            CapsulaDropdown(self.labels[id], id, self.excluir)
        )
        self.area_botao.update()

    def excluir(self, id):
        for i in self.area_botao.controls:
            if int(i.data) == int(id):
                self.area_botao.controls.remove(i)
                self.area_botao.update()

def main(page: ft.Page):
    def check_item_clicked(e):
        e.control.checked = not e.control.checked
        print(e)
        page.update()

    pb = DropDownEntry(["fruta", "verdura", "legume", "condimento"])
    page.add(
        ft.ResponsiveRow([
            ft.Container(
                pb,
                col=3
            )
        ])
    )

ft.app(main)