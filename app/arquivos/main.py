import flet as ft
import logging
import bcrypt
import configparser

from pagina_painel import Painel
from pagina_estoque import Estoque
from pagina_movimentacao import PaginaMovimentacao
from banco_de_dados import SupabaseSingleton
from pagina_ficha import PaginaFT
from pagina_compras import PaginaCompras
from modelos import (
    Usuario,
    Empresa,
)
from controles import InfosGlobal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
  

class ControleConteudo:
    def __init__(self, app) -> None:
        self._app = app

    def atualizar_conteudo(self, pagina) -> None:
        self._app.alterar_pagina(pagina)

    def pagina_inicial(self, usuario) -> None:
        self._app.iniciar_app(usuario)

    def logoff(self, e: ft.ControlEvent) -> None:
        self._app.logoff()


class ControleSombra:
    def __init__(self, sombra, sombra_area) -> None:
        self.sombra = sombra
        self.sombra_area = sombra_area

    def visibilidade(self, visibilidade) -> None:
        self.sombra.visible = visibilidade
        self.sombra_area.visible = visibilidade
        self.sombra.update()
        self.sombra_area.update()


class MenuLateral(ft.Container):
    def __init__(self, empresas: list, controle_conteudo) -> None:
        super().__init__(expand=True, col=2.5)
        self.ROTULOS_BOTOES = [
            "Painel", "Estoque", "Movimentações", "Fichas Técnicas", "Compras"
        ]
        self.ICONES_PATH = [
            "./icons_clone/browser.png",
            "./icons_clone/boxes.png",
            "./icons_clone/exchange.png",
            "./icons_clone/utensils.png",
            "./icons_clone/shopping-basket.png"
        ]
        self.controle_conteudo = controle_conteudo
        self.empresas = empresas
        self._criar_conteudo()
    
    def _criar_conteudo(self) -> None:
        self.sombra = ft.Column([
            ft.Container(expand=True, bgcolor=ft.Colors.BLACK26)
        ], visible=False)

        self.content = ft.Stack([
            ft.Column([
                self._criar_cabecalho(),
                ft.Container(
                    ft.Column([
                        ft.ResponsiveRow([
                            ft.FilledTonalButton(
                                content=ft.ResponsiveRow([
                                    ft.Image(src=src, width=18, height=18, col=3),
                                    ft.Text(label, color=ft.Colors.BLACK87, col=9, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                                ]),
                                col=11,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=5),
                                    alignment=ft.alignment.center_left,
                                ),
                                bgcolor=ft.Colors.GREY_100,
                                on_click=lambda e, l=label: self.controle_conteudo.atualizar_conteudo(l),
                            )
                            for label, src in zip(
                                self.ROTULOS_BOTOES, self.ICONES_PATH
                                )
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], expand=True, horizontal_alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=ft.Colors.GREY_100,
                    alignment=ft.alignment.center,
                    border=ft.border.only(right=ft.border.Border(1, ft.Colors.GREY_500)),
                    padding=ft.padding.only(top=20),
                    expand=True
                )
            ], spacing=0),
            self.sombra
        ])

    def _criar_cabecalho(self) -> ft.Container:
        return ft.Container(
            ft.ResponsiveRow([
                ft.Image("./icons_clone/home.png", width=19, height=19, col=2),
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option(key=empresa.id, text=empresa.nome)
                        for empresa in self.empresas
                    ],
                    text_size=15,
                    value=self.empresas[0].id,
                    border_radius=ft.border_radius.all(5),
                    col=10,
                    border_width=1
                )
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_100,
            height=60,
            padding=ft.padding.only(left=20, top=10, right=20, bottom=10),
            alignment=ft.alignment.center,
            border=ft.border.only(right=ft.border.Border(1, ft.Colors.GREY_500))
        )


class Area(ft.Container):
    def __init__(self, controle_conteudo) -> None:
        super().__init__(expand=True, col=9.5)
        self.conteudo = ft.Container(
            bgcolor=ft.Colors.GREY_100,
            expand=True
        )
        self.sombra_area = ft.Container(expand=True, height=60, bgcolor=ft.Colors.BLACK26, visible=False)
        
        self.content = ft.Column([
            ft.Stack([
                ft.Container(
                    ft.Row([
                        ft.PopupMenuButton(
                            content=ft.Container(
                                ft.Row([
                                    ft.Image("./icons_clone/user.png", width=16, height=16),
                                    ft.Text(InfosGlobal().usuario_nome)
                                ]), bgcolor=ft.Colors.BLUE_200, border_radius=10,
                                padding=ft.padding.only(left=10, top=5, right=10, bottom=5)
                            ),
                            items=[
                                ft.PopupMenuItem(text="Sair", on_click=controle_conteudo.logoff)
                            ],
                            menu_position=ft.PopupMenuPosition.UNDER
                        )
                    ], alignment=ft.MainAxisAlignment.END),
                    bgcolor=ft.Colors.BLUE_100,
                    padding=ft.padding.only(right=20),
                    height=60,
                ),
                self.sombra_area
            ]),
            self.conteudo
        ], spacing=0)

    def atualizar_conteudo(self, conteudo) -> None:
        self.conteudo.content = conteudo
        self.conteudo.update()


class Login(ft.Container):
    def __init__(self, controle_conteudo) -> None:
        super().__init__(expand=True, bgcolor=ft.Colors.GREY_100, padding=ft.padding.all(0))
        self.bd = SupabaseSingleton()
        self.controle_conteudo = controle_conteudo
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self._criar_entradas()
        self._criar_botoes()
        self.mensagens = ft.Text(color=ft.Colors.RED)
        self.content = ft.Column([
            ft.Container(
                ft.Text("FoodFlow", size=25, weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(left=20, top=20)
            ),
            ft.Divider(),
            ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Row([
                            ft.Text("Bem Vindo(a)", size=30, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        self.entrada_telefone,
                        self.entrada_senha,
                        ft.Row([
                            self.mensagens
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            self.botao_entrar
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ], col=4, alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ], alignment=ft.MainAxisAlignment.CENTER), expand=True
            )
        ])

    def _criar_entradas(self) -> None:
        self.entrada_telefone = self._criar_field(
            "Telefone",
            "(67) ",
            ft.NumbersOnlyInputFilter()
        )
        self.entrada_senha = self._criar_field("Senha")

    def _criar_botoes(self) -> None:
        self.botao_entrar = ft.TextButton(
            "ENTRAR",
            on_click=self._autenticar,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.BLUE_100,
                    ft.ControlState.DISABLED: ft.Colors.GREY
                },
                padding=ft.padding.all(20),
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK87))
            ),
            disabled=True
        )

    def _criar_field(self, label: str, prefix: str=None, filter=None) -> ft.TextField:
        return ft.TextField(
            label=label,
            prefix_text=prefix,
            border_radius=10,
            border_color=ft.Colors.BLACK54,
            cursor_height=15,
            content_padding=ft.padding.only(top=0, left=10),
            text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
            label_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)),
            input_filter=filter,
            on_change=self._liberar_botao_entrar
        )

    def _liberar_botao_entrar(self, e: ft.ControlEvent) -> None:
        campos_preenchidos = all([self.entrada_telefone.value, self.entrada_senha.value])
        if self.botao_entrar.disabled == campos_preenchidos:
            self.botao_entrar.disabled = not campos_preenchidos
            self.botao_entrar.update()

    def _autenticar(self, e: ft.ControlEvent) -> None:
        telefone = self.entrada_telefone.value
        senha = self.entrada_senha.value
        if not telefone or not senha:
            self.mostrar_mensagem("Preencha todos os campos")
            return

        credenciais = self._obter_credenciais(telefone)
        if not credenciais:
            self.mostrar_mensagem("Credenciais não encontradas")
            return

        if not self._autenticar_senha(senha, credenciais.get("senha")):
            self.mostrar_mensagem("Senha incorreta")
            return

        usuario = self._relacionar_empresa_usuario(credenciais)
        self.logar(usuario)

    def _autenticar_senha(self, senha: str, hash_armazenado: str) -> bool:
        try:
            return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
        except Exception as e:
            return False

    def _obter_credenciais(self, telefone: str) -> dict:
        try:
            client = self.bd.get_client()
            resposta = (
                client.table("usuarios")
                .select("id, nome, telefone, senha")
                .eq("telefone", f"67{telefone}")
                .execute()
            ).data
        except Exception as e:
            return {}
        else:
            return resposta[0] if resposta else {}

    def _relacionar_empresa_usuario(self, credenciais: dict) -> Usuario:
        usuario = Usuario(credenciais["id"], credenciais["nome"], credenciais["telefone"])
        infos_empresas = self._obter_empresas(usuario.id)
        if infos_empresas:
            usuario.empresas = [
                Empresa(info["empresas"]["id"], info["empresas"]["nome"])
                for info in infos_empresas
            ]
        return usuario
        
    def _obter_empresas(self, usuario_id: int) -> dict:
        try:
            client = self.bd.get_client()
            resposta= (
                client.table("relacao_empresa_usuario")
                .select("empresas(id, nome)")
                .eq("usuario_id", usuario_id)
                .execute()
            ).data
        except Exception as e:
            return {}
        else:
            return resposta if resposta else {}
        
    def logar(self, usuario: Usuario) -> None:
        self.controle_conteudo.pagina_inicial(usuario)

    def mostrar_mensagem(self, msg: str) -> None:
        self.mensagens.value = msg
        self.mensagens.update()


class App(ft.Container):
    def __init__(self) -> None:
        super().__init__(
            expand=True,
            padding=ft.padding.all(0),
            margin=ft.margin.all(0),
            alignment=ft.alignment.top_left
        )
        self.content = Login(ControleConteudo(self))
        # usuario = Usuario(1, "Luiz Henique", "556792300729")
        # usuario.empresas = [Empresa(1, "Ebi sushi")]
        # self.iniciar_app(usuario)

    def alterar_pagina(self, label):
        paginas = {
            "Painel": lambda: Painel(),
            "Estoque": lambda: Estoque(self.controle_sombra),
            "Movimentações": lambda: PaginaMovimentacao(),
            "Fichas Técnicas": lambda: PaginaFT(),
            "Compras": lambda: PaginaCompras(self.controle_sombra),
        }

        criar_pagina = paginas.get(label)
        if criar_pagina:
            self.area.atualizar_conteudo(criar_pagina())

    def iniciar_app(self, usuario):
        empresa = usuario.empresas[0]
        InfosGlobal().atualizar(usuario.id, usuario.nome, empresa.id, empresa.nome)

        self.menu_lateral = MenuLateral(usuario.empresas, ControleConteudo(self))
        self.area = Area(ControleConteudo(self))
        self.controle_sombra = ControleSombra(self.menu_lateral.sombra, self.area.sombra_area)

        self.content = ft.ResponsiveRow([self.menu_lateral, self.area], expand=True, spacing=0)
        self.update()
        self.area.atualizar_conteudo(Painel())
    
    def logoff(self):
        self.content = Login(ControleConteudo(self))
        self.update()

    # def did_mount(self):
    #     self.area.atualizar_conteudo(Painel())


def main(page):
    config = configparser.ConfigParser()
    config.read("./app/credenciais.ini")
    _ = SupabaseSingleton(config["supabase"]["Url"], config["supabase"]["Key"])

    page.padding = ft.padding.all(0)
    app = App()
    page.add(app)

ft.app(target=main, assets_dir="assets")
