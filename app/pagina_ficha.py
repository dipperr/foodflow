import flet as ft
from typing import Callable
import locale

from modelos import UNIDADES
from controles import (
    BotaoTonal,
    GradeNotificacao,
    RotuloColuna,
    InfosGlobal,
    SupabaseSingleton,
    ControleFichaTecnica
)


class ControlePaginaFicha:
    def __init__(self, pagina):
        self.pagina = pagina

    def atualizar_pagina(self):
        self.pagina.atualizar_dados()


class JanelaExcluir(ft.AlertDialog):
    def __init__(self, ficha, controle):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("Excluir ficha técnica"),
            actions_padding=ft.padding.all(0)
        )
        self.ficha = ficha
        self.controle = controle
        self._criar_conteudo()

    def _criar_conteudo(self):
        self.content = ft.Container(
            ft.Column([
                ft.Text(f"Deseja excluir a ficha técnica {self.ficha["nome"]}?"),
                ft.ResponsiveRow([
                    ft.OutlinedButton(
                        content=ft.ResponsiveRow([
                            ft.Image("./icons_clone/pencil.png", width=14, height=14, col=3),
                            ft.Text("SIM", col=7, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.BLACK87, size=14)
                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        col=4,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_100,
                            side=ft.BorderSide(color=ft.Colors.WHITE, width=1)
                        ),
                        on_click=self.sim
                    ),
                    ft.OutlinedButton(
                        content=ft.ResponsiveRow([
                            ft.Image("./icons_clone/trash.png", width=14, height=14, col=3, color=ft.Colors.RED),
                            ft.Text("NÃO", col=8, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.RED, size=14, weight=ft.FontWeight.NORMAL)
                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        col=4,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.WHITE,
                            side=ft.BorderSide(color=ft.Colors.WHITE, width=1)
                        ),
                        on_click=self.nao
                        
                    ),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=20),
            width=400,
            height=70
        )

    def nao(self, e):
        self.page.close(self)

    def sim(self, e):
        self.controle.apagar_ficha(self.ficha["id"])
        self.page.close(self)


class LinhaFicha(ft.Column):
    def __init__(self, produto):
        super().__init__(spacing=0)
        self.controls = [
            ft.ResponsiveRow([
                ft.Text(
                    spans=[
                        ft.TextSpan(f"{produto[0]} {produto[1]}", ft.TextStyle(weight=ft.FontWeight.BOLD, size=15)),
                        ft.TextSpan(" de "),
                        ft.TextSpan(
                            f"{produto[2]}", ft.TextStyle(weight=ft.FontWeight.BOLD, size=15)
                        )
                    ],
                    col=8.5,
                    size=15,
                    weight=ft.FontWeight.W_400,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Text(
                    f"custo: {locale.currency(produto[4], grouping=True)}",
                    col=3.5,
                    size=15,
                    color=ft.Colors.BLACK54,
                    weight=ft.FontWeight.W_400
                )
            ]),
            ft.Divider(height=5)
        ]


class CartaoFT(ft.Card):
    def __init__(self, ficha, controle_pagina):
        super().__init__(elevation=5)
        self.ficha = ficha
        self.controle_pagina = controle_pagina
        self._criar_conteudo()

    def _criar_conteudo(self):
        self._criar_botoes()
        self._criar_painel()

        self.content = ft.Container(
            ft.Column([
                ft.ResponsiveRow([
                    ft.Text(self.ficha["nome"], col=10.5, size=20, weight=ft.FontWeight.W_600),
                    self.botao_expandir
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(),
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Text("Porção", weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54, size=17),
                        ft.Text(
                            f"{self.ficha["qtd_porcao"]} {self.ficha["unidade"].split(" ")[1].strip("()")}",
                            weight=ft.FontWeight.W_500,
                            size=16
                        )
                    ], col=6),
                    ft.Column([
                        ft.Text("Custo", weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54, size=17),
                        ft.Text(
                            f"{locale.currency(self._calcular_custo(), grouping=True)}",
                            weight=ft.FontWeight.W_500,
                            size=16
                        )
                    ], col=6)
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self.painel
            ]),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.symmetric(vertical=10, horizontal=10)
        )

    def _criar_botoes(self):
        self.botao_expandir = ft.IconButton(
            ft.Icons.ARROW_DROP_DOWN_ROUNDED,
            selected_icon=ft.Icons.ARROW_DROP_UP_ROUNDED,
            col=1.5,
            on_click=self.visibilidade_painel,
            icon_color=ft.Colors.BLACK87,
            selected_icon_color=ft.Colors.BLACK87,
            selected=False
        )

    def _criar_painel(self):
        self.painel = ft.Container(
            ft.Column([
                ft.Text("Produtos", weight=ft.FontWeight.W_400, color=ft.Colors.BLACK54, size=17),
                ft.Column([
                    LinhaFicha(produto)
                    for produto in self.ficha["ingredientes"]["itens"]
                ]),
                ft.ResponsiveRow([
                    ft.OutlinedButton(
                        content=ft.ResponsiveRow([
                            ft.Image("./icons_clone/pencil.png", width=14, height=14, col=3),
                            ft.Text("EDITAR", col=7, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.BLACK87, size=14)
                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        col=4,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_200,
                            side=ft.BorderSide(color=ft.Colors.BLUE_100, width=1)
                        )
                    ),
                    ft.OutlinedButton(
                        content=ft.ResponsiveRow([
                            ft.Image("./icons_clone/trash.png", width=14, height=14, col=3, color=ft.Colors.RED),
                            ft.Text("EXCLUIR", col=8, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.RED, size=14, weight=ft.FontWeight.NORMAL)
                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        col=4,
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(color=ft.Colors.BLUE_100, width=1)
                        ),
                        on_click=self.abrir_janela_excluir
                        
                    ),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10), visible=False
        )
    
    def abrir_janela_excluir(self, e):
        janela = JanelaExcluir(
            self.ficha,
            ControleFichaTecnica(self.controle_pagina)
        )
        self.page.open(janela)

    def _calcular_custo(self):
        return sum([item[4] for item in self.ficha["ingredientes"]["itens"]])

    def visibilidade_painel(self, e):
        self.painel.visible = not self.painel.visible
        self.botao_expandir.selected = not self.botao_expandir.selected
        self.alterar_cor()
        self.painel.update()
        self.botao_expandir.update()

    def alterar_cor(self):
        self.content.bgcolor = ft.Colors.BLUE_100 if self.painel.visible else ft.Colors.WHITE
        self.content.update()


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
            col=int(len(rotulo) / 2) if len(rotulo) < 10 else 5
        )
        self.rotulo = rotulo
        self.id = id

    @property
    def value(self):
        return {"id": self.id, "nome": self.rotulo}


class LinhaProduto(ft.ResponsiveRow):
    def __init__(self, id: int, produto: str):
        super().__init__(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            run_spacing=0
        )
        self.id = id
        self.produto = produto
        self._criar_conteudo()

    def _criar_conteudo(self):
        self.controls = [
            ft.TextField(
                label="Qtd.",
                label_style=ft.TextStyle(size=15),
                col=2,
                height=35,
                cursor_height=15,
                content_padding=ft.padding.only(top=0, left=10),
                border_radius=10,
                input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True)
            ),
            ft.Dropdown(
                options=[ft.dropdown.Option(self.produto.split("(")[1].strip(")"))],
                col=4,
                height=35,
                icon_size=15,
                border_radius=10,
                text_style=ft.TextStyle(
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    foreground=ft.Paint(ft.Colors.BLACK)
                )
            ),
            ft.Text(
                "de ",
                spans=[
                    ft.TextSpan(self.produto, ft.TextStyle(weight=ft.FontWeight.BOLD))
                ],
                col=6
            ),
            ft.Container(ft.Divider(), col=12)
        ]

    def obter_valores(self):
        return (
            self.controls[0].value.replace(",", "."),
            self.controls[1].value,
            self.produto.split("(")[0].strip(),
            self.id
        )


class DropdownV2(ft.PopupMenuButton):
    def __init__(self, rotulos: dict, lista_produtos: ft.Column, values: list=None):
        super().__init__(
            tooltip="",
            size_constraints=ft.BoxConstraints(
                max_height=250,
                min_width=200
            ),
            bgcolor=ft.Colors.WHITE
        )
        self.rotulos = rotulos
        self.lista_produtos = lista_produtos
        self._criar_conteudo(values)

    @property
    def value(self):
        if self.area_botao.controls:
            return [capsula.value for capsula in self.area_botao.controls]
        else:
            return None

    def _criar_conteudo(self, values):
        self.area_botao = ft.ResponsiveRow([], spacing=5)
        self.content = ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    self.area_botao,
                    padding=ft.padding.only(left=5, bottom=5, right=5),
                    border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.BLACK54)),
                    expand=True,
                    col=11
                ),
                ft.Column([
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN,color=ft.Colors.BLACK54)
                ], col=1)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=0),
            padding=ft.padding.only(top=10, bottom=10),
            alignment=ft.alignment.center,
            width=500,
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

    def _adicionar_item(self, id):
        self._adicionar_item_lista(id)
        self.area_botao.controls.append(
            CapsulaDropdown(self.rotulos[id], id, self.excluir)
        )
        self.area_botao.update()

    def _adicionar_item_lista(self, id):
        self.lista_produtos.controls.append(LinhaProduto(id, self.rotulos[id]))
        self.lista_produtos.update()

    def _excluir_produto_lista(self, id):
        for item in self.lista_produtos.controls:
            if item.id == id:
                self.lista_produtos.controls.remove(item)
                self.lista_produtos.update()
                break

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
                break
        self._excluir_produto_lista(id)


class JanelaCadFicha(ft.AlertDialog):
    def __init__(self, controle: ControleFichaTecnica):
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.controle = controle
        self.unidades = UNIDADES
        self.ler_produtos()

    def _criar_conteudo(self, produtos):
        self.lista_produtos = ft.Column([])
        self.criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Criar novo produto", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Column([
                    ft.ResponsiveRow([
                        self.f_nome
                    ]),
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.Text("UNIDADE",weight=ft.FontWeight.W_500),
                            self.d_unidade
                        ], col=6),
                        self.f_quantidade
                    ]),
                    ft.ResponsiveRow([
                        ft.Text("ESTE PRODUTO SERÁ ARMAZENADO EM ESTOQUE OU É INGREDIENTE DE OUTRA FICHA TÉCNICA?", col=12)
                    ]),
                    ft.Column([
                        self.check_sim,
                        self.check_nao
                    ], spacing=5),
                    ft.Column([
                        ft.Text("PRODUTOS", weight=ft.FontWeight.W_500),
                        self.lista_produtos,
                        DropdownV2(
                            {produto["id"]: produto["nome"] + self.rotulo_quantidade(produto["unidade"]) for produto in produtos},
                            self.lista_produtos
                        )
                    ]),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        self.b_cancelar,
                        self.b_criar_produto
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10)
            ], spacing=10, scroll=ft.ScrollMode.ALWAYS), width=500, height=530
        )
    
    def rotulo_quantidade(self, quantidade: str):
        return f" {quantidade.split(" ")[1]}"
    
    def criar_entradas(self):
        self.check_sim = ft.Checkbox(label="SIM", value=True, on_change=self.estado_check)
        self.check_nao = ft.Checkbox(label="NÃO", on_change=self.estado_check)
        self.f_nome = TextField("NOME DA FICHA TÉCNICA", 12, on_change=self._liberar_botao_criar_prod)
        self.d_unidade = self.f_unidade = ft.Dropdown(
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
        self.f_quantidade = TextField(
            "QUANTIDADE DA PORÇÃO",
            6,
            input_filter=ft.InputFilter(regex_string=r"^(\d+(,\d*)?)?$", replacement_string="", allow=True),
            on_change=self._liberar_botao_criar_prod
        )

    def estado_check(self, e):
        if self.check_sim.value:
            self.check_nao.value = False
        elif self.check_nao.value:
            self.check_sim.value = False
        self.check_nao.update()
        self.check_sim.update()

    def _liberar_botao_criar_prod(self, e):
        entradas = [self.f_nome.value, self.d_unidade.value, self.f_quantidade.value]
        self.b_criar_produto.disabled = not all(entradas)
        self.b_criar_produto.update()

    def _criar_botoes(self):
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
            on_click=self.criar_ficha,
            disabled=True
        )

    def criar_ficha(self, e):
        produtos = [produto.obter_valores() for produto in self.lista_produtos.controls]
        self.controle.criar_ficha(
            self.f_nome.value,
            self.f_unidade.value,
            self.f_quantidade.value,
            True,
            produtos
        )
        self.page.close(self)

    def ler_produtos(self):
        try:
            ig = InfosGlobal()
            bd = SupabaseSingleton()
            client = bd.get_client()
            resposta = (
                client.table("produtos")
                .select("id, nome, unidade, preco_unidade")
                .eq("empresa_id", ig.empresa_id)
                .order("nome")
                .execute()
            )
        except Exception as e:
            print(e)
        else:
            self._criar_conteudo(resposta.data)


class PaginaFT(ft.Column):
    def __init__(self):
        super().__init__()

    def _criar_conteudo(self):
        self.expand = False
        self.scroll = ft.ScrollMode.ALWAYS
        self.controls = [
            ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        RotuloColuna("Fichas técnicas", "./icons_clone/utensils.png"),
                        ft.Divider(),
                        ft.ResponsiveRow([
                            BotaoTonal(
                                "Cadastrar Ficha Técnica",
                                "./icons_clone/checklist-task-budget.png",
                                3,
                                on_click=self.janela_cad_ficha
                            )
                        ]),
                        ft.ResponsiveRow([
                            ft.TextField(cursor_color=ft.Colors.BLACK54,
                                border_radius=10,
                                border_color=ft.Colors.BLACK54,
                                col=4,
                                height=35,
                                label="Pesquisar por nome...",
                                cursor_height=15,
                                content_padding=ft.padding.only(top=0, left=10),
                                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
                                label_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
                            )
                        ]),
                        self._criar_grade_fichas()
                    ], col=12, spacing=20)
                ]),
                padding=ft.padding.all(20)
            )
        ]
        self.update()

    def placeholder(self):
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _criar_grade_fichas(self):
        if len(self.fichas) > 0:
            grade = GradeNotificacao([
                CartaoFT(f, ControlePaginaFicha(self))
                for f in self.fichas
            ], 2)
            return grade
        return ft.Container()

    def janela_cad_ficha(self, e):
        janela = JanelaCadFicha(ControleFichaTecnica(self))
        self.page.open(janela)

    def calcular_valores_fichas(self):
        produtos_dict = {produto["id"]: produto for produto in self.produtos}
        
        for ficha in self.fichas:
            for produto_ficha in ficha["ingredientes"]["itens"]:
                produto_id = produto_ficha[3]
                
                if produto_id in produtos_dict:
                    produto = produtos_dict[produto_id]
                    valor = round(produto["preco_unidade"] * float(produto_ficha[0]), 2)
                    produto_ficha.append(valor)

    def atualizar_dados(self):
        self.ler_dados()
        self.update()

    def ler_dados(self):
        try:
            client = SupabaseSingleton().get_client()
            self.fichas = (
                client.table("fichas_tecnicas")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
            self.produtos = (
                client.table("produtos")
                .select("id, preco_unidade")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self.calcular_valores_fichas()
            self._criar_conteudo()

    def did_mount(self):
        self.placeholder()
        self.ler_dados()
