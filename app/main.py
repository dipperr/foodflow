import flet as ft
import logging
import bcrypt

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
from controles import (
    InfosGlobal
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
  

class MenuLateral(ft.Container):
    def __init__(self, empresas: list, controle_conteudo):
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

        self.sombra = ft.Column([
            ft.Container(expand=True, bgcolor=ft.Colors.BLACK26)
        ], visible=False)

        self.content = ft.Stack([
            ft.Column([
                ft.Container(
                    ft.ResponsiveRow([
                        ft.Image("./icons_clone/home.png", width=19, height=19, col=2),
                        ft.Dropdown(
                            options=[
                                ft.dropdown.Option(key=empresa.id, text=empresa.nome)
                                for empresa in empresas
                            ],
                            text_size=15,
                            value=empresas[0].id,
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
                ),
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


class ControleConteudo:
    def __init__(self, app):
        self._app = app

    def atualizar_conteudo(self, pagina):
        self._app.alterar_pagina(pagina)

    def pagina_inicial(self, usuario):
        self._app.iniciar_app(usuario)

    def logoff(self, e):
        self._app.logoff()


class ControleSombra:
    def __init__(self, sombra, sombra_area):
        self.sombra = sombra
        self.sombra_area = sombra_area

    def visibilidade(self, visibilidade):
        self.sombra.visible = visibilidade
        self.sombra_area.visible = visibilidade
        self.sombra.update()
        self.sombra_area.update()


class Area(ft.Container):
    def __init__(self, cc):
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
                                ft.PopupMenuItem(text="Sair", on_click=cc.logoff)
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

    def atualizar_conteudo(self, conteudo):
        self.conteudo.content = conteudo
        self.conteudo.update()


class Login(ft.Container):
    def __init__(self, controle_conteudo):
        super().__init__(expand=True, bgcolor=ft.Colors.GREY_100, padding=ft.padding.all(0))
        self.bd = SupabaseSingleton()
        self.controle_conteudo = controle_conteudo
        self._criar_conteudo()

    def _criar_conteudo(self):
        self.mensagens = ft.Text(color=ft.Colors.RED)
        self.field_telefone = self._criar_field(
            "Telefone",
            "(67) ",
            ft.NumbersOnlyInputFilter()
        )
        self.field_senha = self._criar_field("Senha")
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
        self.pagina_login = ft.Column([
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
                        self.field_telefone,
                        self.field_senha,
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

        self.content = self.pagina_login

    def _criar_field(self, label, prefix=None, filter=None):
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

    def _liberar_botao_entrar(self, e):
        self.botao_entrar.disabled = False if self.field_telefone.value and self.field_senha.value else True
        self.botao_entrar.update()

    def _autenticar(self, e):
        # telefone = self.field_telefone.value
        # senha = self.field_senha.value
        telefone = "992300729"
        senha = "01091939"
        if telefone and senha:
            credenciais = self._obter_credenciais(telefone)
            if not credenciais:
                self.mostrar_mensagem("Credenciais não encontradas")
                return

            if self._autenticar_senha(senha, credenciais.get("senha")):
                usuario = self._relacionar_empresa_usuario(credenciais)
                self.logar(usuario)
            else:
                self.mostrar_mensagem("Senha incorreta")
        else:
            self.mostrar_mensagem("Preencha todos os campos")

    def _autenticar_senha(self, senha: str, hash_armazenado: str) -> bool:
        try:
            return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
        except Exception as e:
            return False

    def _obter_credenciais(self, telefone: str) -> dict:
        try:
            client = self.bd.get_client()
            response = (
                client.table("usuarios")
                .select("id, nome, telefone, senha")
                .eq("telefone", f"67{telefone}")
                .execute()
            )
            if response:
                return response.data[0]
            else:
                return {}
        except Exception as e:
            return {}
        
    def _relacionar_empresa_usuario(self, credenciais):
        usuario = Usuario(credenciais["id"], credenciais["nome"], credenciais["telefone"])
        infos_empresas = self._obter_empresas(usuario.id)
        if infos_empresas:
            usuario.empresas = [
                Empresa(info["empresas"]["id"], info["empresas"]["nome"])
                for info in infos_empresas
            ]
        return usuario
        
    def _obter_empresas(self, usuario_id: int):
        try:
            client = self.bd.get_client()
            response = (
                client.table("relacao_empresa_usuario")
                .select("empresas(id, nome)")
                .eq("usuario_id", usuario_id)
                .execute()
            )
            if response:
                    return response.data
            else:
                return {}
        except Exception as e:
            return {}
        
    def logar(self, usuario):
        self.controle_conteudo.pagina_inicial(usuario)

    def mostrar_mensagem(self, msg):
        self.mensagens.value = msg
        self.mensagens.update()

    def did_mount(self):
        self._autenticar(None)


class App(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=ft.padding.all(0),
            margin=ft.margin.all(0),
            alignment=ft.alignment.top_left
        )
        # self.content = Login(ControleConteudo(self))
        usuario = Usuario(1, "Luiz Henique", "556792300729")
        usuario.empresas = [Empresa(1, "Ebi sushi")]
        self.iniciar_app(usuario)

    def alterar_pagina(self, label):
        match label:
            case "Painel":
                self.area.atualizar_conteudo(Painel())
            case "Estoque":
                self.area.atualizar_conteudo(Estoque(self.controle_sombra))
            case "Movimentações":
                self.area.atualizar_conteudo(PaginaMovimentacao())
            case "Fichas Técnicas":
                self.area.atualizar_conteudo(PaginaFT())
            case "Compras":
                self.area.atualizar_conteudo(PaginaCompras(self.controle_sombra))

    def iniciar_app(self, usuario):
        empresa = usuario.empresas[0]
        InfosGlobal().atualizar(usuario.id, usuario.nome, empresa.id, empresa.nome)

        self.menu_lateral = MenuLateral(usuario.empresas, ControleConteudo(self))
        self.area = Area(ControleConteudo(self))
        self.controle_sombra = ControleSombra(self.menu_lateral.sombra, self.area.sombra_area)

        self.content = ft.ResponsiveRow([self.menu_lateral, self.area], expand=True, spacing=0)
        # self.update()
        # self.area.atualizar_conteudo(Painel())
    
    def logoff(self):
        self.content = Login(ControleConteudo(self))
        self.update()

    def did_mount(self):
        self.area.atualizar_conteudo(Estoque(self.controle_sombra))


def main(page):
    SUPABASE_URL = "https://cuecskniecdwpdpgoqtp.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN1ZWNza25pZWNkd3BkcGdvcXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMxODU5ODcsImV4cCI6MjA1ODc2MTk4N30.0GnN4YWskXOkV6hS6NLxYOnKSeFT2Hofjc660XYa1Fs"

    _ = SupabaseSingleton(SUPABASE_URL, SUPABASE_KEY)

    page.padding = ft.padding.all(0)
    app = App()
    page.add(app)

ft.app(target=main, assets_dir="assets")
