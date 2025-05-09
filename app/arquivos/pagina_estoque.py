from datetime import datetime
from dateutil import parser
import flet as ft
import locale
import pandas as pd
from typing import Callable, List, Optional, Union

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
    InfosGlobal,
    ControleDropdownV2
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
    Filtro,
    DropdownV2,
    FiltroEntrada,
    LinhaHistorico
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


class JanelaRegistrarMovimentacao(ft.AlertDialog):
    def __init__(self, produto: Produto, controle: ControleMovimentacao) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.produto = produto
        self.controle = controle
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
                        ft.ResponsiveRow([
                            self.entrada_dt_validade
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

    def _criar_entradas(self):
        self.entrada_acao = self._criar_dropdown(
            ["Entrada", "Saída", "Inventário"],
            self._acao
        )
        self.entrada_classificar_acao = self._criar_dropdown([])
        self.entrada_unidade = self._criar_dropdown([self.produto.unidade])
        self.entrada_qtd = TextField(
            "QUANTIDADE",
            6,
            input_filter=ft.InputFilter(
                regex_string=r"^(\d+(,\d*)?)?$",
                replacement_string="",
                allow=True
            ),
            on_change=self._liberar_botao_confirmar
        )
        self.entrada_preco = TextField(
            f"PRECO POR {self.produto.unidade.upper()}",
            6,
            "Preço de custo por unidade do produto.",
            value=locale.currency(
                self.produto.preco if not pd.isnull(self.produto.preco) else 0,
                grouping=True
            ).replace(".", ""),
            visible=False
        )
        self.entrada_dt_movimentacao = TextField(
            "DATA MOVIMENTAÇÃO",
            6,
            value=datetime.now().strftime("%d/%m/%Y"),
            on_change=self._liberar_botao_confirmar
        )
        self.entrada_dt_validade = TextField(
            "DATA DE VALIDADE",
            6,
            "a data de validade irá criar um lote deste produto",
            placeholder=f"ex: {datetime.now().strftime("%d/%m/%Y")}",
            visible=False
        )

    def _criar_dropdown(self, options: List, on_change: Optional[Callable]=None) -> ft.Dropdown:
        return ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in options
            ],
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
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
            on_click=self.registrar_movimentacao
        )

    def _liberar_botao_confirmar(self, e: ft.ControlEvent) -> None:
        values = [
            self.entrada_acao.value,
            self.entrada_unidade.value,
            self.entrada_qtd.value,
            self.entrada_dt_movimentacao.value
        ]
        self.botao_confirmar.disabled = not all(values)
        self.botao_confirmar.update()

    def _acao(self, e: ft.ControlEvent) -> None:
        self._estado_padrao()
        acao = e.data.lower()
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
        self._atualizar_visibilidade(self.entrada_preco, False)
        self._atualizar_visibilidade(self.entrada_dt_validade, False)

    def _acao_entrada(self) -> None:
        self._definir_opcoes(self.entrada_classificar_acao, ["Compras", "Produção", "Tranferência"])
        self._atualizar_visibilidade(self.entrada_preco, True)
        self._atualizar_visibilidade(self.entrada_dt_validade, True)

    def _acao_saida(self) -> None:
        self._definir_opcoes(self.entrada_classificar_acao, ["Vendas", "Consumo interno", "Tranferência", "Desperdício"])

    def _acao_inventario(self) -> None:
        self._atualizar_visibilidade(self.entrada_preco, True)

    def _definir_opcoes(self, dropdown, opcoes) -> None:
        dropdown.options.extend([ft.dropdown.Option(op) for op in opcoes])
        dropdown.update()

    def _atualizar_visibilidade(self, campo, visivel) -> None:
        campo.visible = visivel
        campo.update()

    def registrar_movimentacao(self, e: ft.ControlEvent) -> None:
        self.controle.registrar(
            self.produto.id,
            self.produto.qtd_estoque,
            self.entrada_acao.value,
            self.entrada_classificar_acao.value,
            self.entrada_unidade.value,
            self.entrada_qtd.value,
            self.entrada_dt_movimentacao.value,
            self.entrada_preco.value,
            self.entrada_dt_validade.value
        )


class JanelaEditarProduto(ft.AlertDialog):
    def __init__(self, produto, controle) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.produto = produto
        self.controle_produto = controle
        self.categorias = None
        self.fornecedores = None
        self.ler_dados()

    def _criar_conteudo(self, categorias: List, fornecedores: List) -> None:
        self.mensagem = ft.Text(color=ft.Colors.RED, visible=False)
        self._criar_entradas(categorias, fornecedores)
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Editar produto", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    ft.Column([
                        ft.ResponsiveRow([
                            self.entrada_nome_produto
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE",weight=ft.FontWeight.W_500),
                                self.entrada_unidade
                            ], col=6),
                            self.entrada_qtd_estoque
                        ]),
                        ft.ResponsiveRow([
                            self.entrada_estoque_min,
                            self.entrada_preco_unidade
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("CATEGORIA", weight=ft.FontWeight.W_500),
                                self.entrada_categoria,
                                ft.Row([
                                    self.botao_criar_categoria
                                ], alignment=ft.MainAxisAlignment.END)
                            ], col=6),
                            ft.Column([
                                ft.Text("FORNECEDOR(ES)", weight=ft.FontWeight.W_500),
                                self.entrada_fornecedores,
                                ft.Row([
                                    self.botao_criar_fornecedor
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
                                self.botao_cancelar,
                                self.botao_criar_produto
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=500, width=500
        )

    def _criar_entradas(self, categorias: List, fornecedores: List) -> None:
        preco = 0 if pd.isnull(self.produto.preco) else self.produto.preco
        self.check_sim = ft.Checkbox(label="SIM", value=True, on_change=self.estado_check)
        self.check_nao = ft.Checkbox(label="NÃO", on_change=self.estado_check)
        self.entrada_nome_produto = TextField(
            "NOME DO PRODUTO",
            12,
            value=self.produto.nome,
            on_change=self._liberar_botao_criar_prod
        )
        self.entrada_qtd_estoque = TextField(
            "QUANTIDADE EM ESTOQUE",
            6,
            value=locale.currency(self.produto.qtd_estoque, grouping=True, symbol=False),
            on_change=self._liberar_botao_criar_prod,
            input_filter=FiltroEntrada()
        )
        self.entrada_estoque_min = TextField(
            "ESTOQUE MÍNIMO",
            6,
            "Quantidade de refência para compras desse produto",
            value=locale.currency(self.produto.estoque_min, grouping=True, symbol=False),
            on_change=self._liberar_botao_criar_prod,
            input_filter=FiltroEntrada()
        )
        self.entrada_preco_unidade = TextField(
            "PREÇO POR UNIDADE",
            6,
            "Preço de custo por unidade do produto (campo opcional)",
            value=locale.currency(preco, grouping=True, symbol=False),
            input_filter=FiltroEntrada()
        )
        self.entrada_unidade = ft.Dropdown(
            options=[
                ft.dropdown.Option(unidade)
                for unidade in UNIDADES
            ],
            value=self.produto.unidade,
            border_radius=15,
            col=6,
            border_color=ft.Colors.BLACK54,
            bgcolor=ft.Colors.WHITE,
            max_menu_height=300,
            on_change=self._liberar_botao_criar_prod
        )

        ids_categorias, ids_fornecedores = self._obter_ids(categorias, fornecedores)

        self.entrada_categoria = DropdownV2(
            {cat["id"]: cat["nome"] for cat in categorias}, ids_categorias
        )
        self.entrada_fornecedores = DropdownV2(
            {forn["id"]: forn["nome"] for forn in fornecedores}, ids_fornecedores
        )

    def _obter_ids(self, categorias: List, fornecedores: List) -> List:
        ids_categorias = []
        ids_fornecedores = []
        if self.produto.categorias is not None:
            ids_categorias = [cat["id"] for cat in categorias if cat["nome"] in self.produto.categorias.keys()]
        
        if self.produto.fornecedores["nomes"] is not None:
            ids_fornecedores = [forn["id"] for forn in fornecedores if forn["nome"] in self.produto.fornecedores["nomes"]]

        return ids_categorias, ids_fornecedores

    def _criar_botoes(self) -> None:
        self.botao_criar_categoria = ft.TextButton(
            "CRIAR NOVA CATEGORIA",
            on_click=self.janela_add_categoria,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.botao_criar_fornecedor = ft.TextButton(
            "CRIAR NOVO FORNECEDOR",
            on_click=self.janela_add_fornecedor,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.botao_criar_produto = ft.OutlinedButton(
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
    
    def estado_check(self, e: ft.ControlEvent) -> None:
        if self.check_sim.value:
            self.check_nao.value = False
        elif self.check_nao.value:
            self.check_sim.value = False
        self.check_nao.update()
        self.check_sim.update()

    def _liberar_botao_criar_prod(self, e: ft.ControlEvent) -> None:
        entradas = [
            self.entrada_nome_produto.value,
            self.entrada_unidade.value,
            self.entrada_qtd_estoque.value,
            self.entrada_estoque_min.value
        ]
        self.botao_criar_produto.disabled = not all(entradas)

        self.botao_criar_produto.update()

    def janela_add_categoria(self, e: ft.ControlEvent) -> None:
        janela = JanelaCadCategoria(ControleDropdownV2(self.f_categoria))
        controle = ControleCategoria(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def janela_add_fornecedor(self, e: ft.ControlEvent) -> None:
        janela = JanelaCadFornecedor(ControleDropdownV2(self.f_fornecedores))
        controle = ControleFornecedores(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def salvar_produto(self, e: ft.ControlEvent) -> None:
        if self.controle_produto is not None:
            self.controle_produto.atualizar_produto(
                self.produto.id,
                self.entrada_nome_produto.value,
                self.entrada_unidade.value,
                self.entrada_qtd_estoque.value,
                self.entrada_estoque_min.value,
                self.entrada_preco_unidade.value,
                self.entrada_categoria.value,
                self.entrada_fornecedores.value,
                self.check_sim.value
            )

    def ler_dados(self) -> None:
        try:
            bd = SupabaseSingleton()
            client = bd.get_client()
            categorias = (
                client.table("categoria")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
            fornecedores = (
                client.table("fornecedores")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self._criar_conteudo(categorias, fornecedores)


class JanelaCadCategoria(ft.AlertDialog):
    def __init__(self, controle_dropdown: ControleDropdownV2) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.controle_dropdown = controle_dropdown
        self.controle_categoria = None
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self._criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Criar nova categoria", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ResponsiveRow([self.entrada_categoria]),
                ft.Row([
                    ft.Text("CORES: ", weight=ft.FontWeight.W_500),
                    self.cores
                ]),
                ft.Divider(),
                ft.ResponsiveRow([
                    self.botao_cancelar,
                    self.botao_criar_categoria
                ], alignment=ft.MainAxisAlignment.END)
            ]), height=250, width=500
        )

    def _criar_entradas(self) -> None:
        self.entrada_categoria = TextField(
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

    def _criar_botoes(self) -> None:
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
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=self.fechar,
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )

    def fechar(self, e: ft.ControlEvent) -> None:
        self.page.close(self)
        for ov in reversed(self.page.overlay):
            if isinstance(ov, (JanelaCadProduto, JanelaEditarProduto)):
                self.page.open(ov)
                break

    def criar_categoria(self, e: ft.ControlEvent) -> None:
        if self.controle_categoria is not None:
            self.controle_categoria.criar_categoria(
                self.entrada_categoria.value,
                self.cores.value
            )

    def atualizar_item(self, categoria: dict) -> None:
        self.controle_drop.atualizar_itens(categoria)

    def _liberar_botao_criar(self, e: ft.ControlEvent) -> None:
        self.botao_criar_categoria.disabled = not all([self.entrada_categoria.value, self.cores.value])
        self.botao_criar_categoria.update()

    def definir_controle(self, controle) -> None:
        self.controle_categoria = controle


class JanelaCadFornecedor(ft.AlertDialog):
    def __init__(self, controle_dropdown) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.controle_dropdown = controle_dropdown
        self.controle_fornecedor = None
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self._criar_entradas()
        self._criar_botoes()
        self.content = ft.Container(
            ft.Column([
                ft.Text("Criar novo fornecedor", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.ResponsiveRow([self.entrada_nome_fornecedor]),
                ft.ResponsiveRow([ft.Text("VENDEDOR", col=12, weight=ft.FontWeight.BOLD)]),
                ft.Divider(),
                ft.ResponsiveRow([self.entrada_nome_vendedor]),
                ft.ResponsiveRow([self.entrada_telefone_vendedor]),
                ft.ResponsiveRow([
                    self.botao_cancelar,
                    self.botao_criar
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15, scroll=ft.ScrollMode.ALWAYS), height=460, width=500
        )

    def _criar_entradas(self) -> None:
        self.entrada_nome_fornecedor = TextField("NOME DO FORNECEDOR", col=12, on_change=self._liberar_botao_criar)
        self.entrada_nome_vendedor = TextField("Nome", col=12)
        self.entrada_telefone_vendedor = TextField("Telefone", col=12)

    def _criar_botoes(self) -> None:
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
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=self.fechar,
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )

    def fechar(self, e: ft.ControlEvent) -> None:
        self.page.close(self)
        for ov in reversed(self.page.overlay):
            if isinstance(ov, (JanelaCadProduto, JanelaEditarProduto)):
                self.page.open(ov)
                break

    def criar_fornecedor(self, e: ft.ControlEvent) -> None:
        if self.controle_fornecedor is not None:
            self.controle_fornecedor.criar_fornecedor(
                self.entrada_nome_fornecedor.value,
                self.entrada_nome_vendedor.value,
                self.entrada_telefone_vendedor.value
            )

    def atualizar_item(self, categoria: dict) -> None:
        self.controle_drop.atualizar_itens(categoria)

    def _liberar_botao_criar(self, e: ft.ControlEvent) -> None:
        self.botao_criar.disabled = not bool(self.entrada_nome_fornecedor.value)
        self.botao_criar.update()

    def definir_controle(self, controle) -> None:
        self.controle_fornecedor = controle


class JanelaCadProduto(ft.AlertDialog):
    def __init__(self, nome_unidade: str) -> None:
        super().__init__(
            modal=True,
            bgcolor=ft.Colors.WHITE,
            actions_padding=ft.padding.all(0)
        )
        self.nome_unidade = nome_unidade
        self.controle_produto = None
        self.unidades = UNIDADES
        self.ler_dados()

    def _criar_conteudo(self, categorias: List, fornecedores: List) -> None:
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
                            self.entrada_nome_produto
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("UNIDADE", weight=ft.FontWeight.W_500),
                                self.entrada_unidade
                            ], col=6),
                            self.entrada_qtd_estoque
                        ]),
                        ft.ResponsiveRow([
                            self.entrada_estoque_min,
                            self.entrada_preco_unidade
                        ]),
                        ft.ResponsiveRow([
                            ft.Column([
                                ft.Text("CATEGORIA", weight=ft.FontWeight.W_500),
                                self.entrada_categoria,
                                ft.Row([
                                    self.botao_criar_categoria
                                ], alignment=ft.MainAxisAlignment.END)
                            ], col=6),
                            ft.Column([
                                ft.Text("FORNECEDOR(ES)", weight=ft.FontWeight.W_500),
                                self.entrada_fornecedores,
                                ft.Row([
                                    self.botao_criar_fornecedor
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
                                self.botao_cancelar,
                                self.botao_criar_produto
                            ], alignment=ft.MainAxisAlignment.END)
                        ], spacing=10)
                    ], spacing=20, scroll=ft.ScrollMode.ALWAYS), expand=True
                )
            ], spacing=5), height=500, width=500
        )

    def _criar_entradas(self, categorias: List, fornecedores: List) -> None:
        self.check_sim = ft.Checkbox(label="SIM", value=True, on_change=self.estado_check)
        self.check_nao = ft.Checkbox(label="NÃO", on_change=self.estado_check)
        self.entrada_nome_produto = TextField("NOME DO PRODUTO", 12, on_change=self._liberar_botao_criar_prod)
        self.entrada_qtd_estoque = TextField(
            "QUANTIDADE EM ESTOQUE",
            6, 
            on_change=self._liberar_botao_criar_prod,
            input_filter=FiltroEntrada()
        )
        self.entrada_estoque_min = TextField(
            "ESTOQUE MÍNIMO",
            6,
            "Quantidade de refência para compras desse produto",
            on_change=self._liberar_botao_criar_prod,
            input_filter=FiltroEntrada()
        )
        self.entrada_preco_unidade = TextField(
            "PREÇO POR UNIDADE",
            6,
            "Preço de custo por unidade do produto (campo opcional)",
            input_filter=FiltroEntrada()
        )
        self.entrada_unidade = ft.Dropdown(
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
        self.entrada_categoria = DropdownV2(
            {cat["id"]: cat["nome"] for cat in categorias}
        )
        self.entrada_fornecedores = DropdownV2(
            {forn["id"]: forn["nome"] for forn in fornecedores}
        )

    def _criar_botoes(self) -> None:
        self.botao_criar_categoria = ft.TextButton(
            "CRIAR NOVA CATEGORIA",
            on_click=self.janela_add_categoria,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.botao_criar_fornecedor = ft.TextButton(
            "CRIAR NOVO FORNECEDOR",
            on_click=self.janela_add_fornecedor,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54))
            )
        )
        self.botao_cancelar = ft.OutlinedButton(
            "CANCELAR",
            on_click=lambda e: self.page.close(self),
            col=4,
            style=ft.ButtonStyle(text_style=ft.TextStyle(foreground=ft.Paint(color=ft.Colors.BLACK54)))
        )
        self.botao_criar_produto = ft.OutlinedButton(
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
    
    def estado_check(self, e: ft.ControlEvent) -> None:
        if self.check_sim.value:
            self.check_nao.value = False
        elif self.check_nao.value:
            self.check_sim.value = False
        self.check_nao.update()
        self.check_sim.update()

    def _liberar_botao_criar_prod(self, e: ft.ControlEvent) -> None:
        entradas = [
            self.entrada_nome_produto.value,
            self.entrada_unidade.value,
            self.entrada_qtd_estoque.value,
            self.entrada_estoque_min.value
        ]
        produto_existe = self.verificar_produtos_iguais(entradas[0], entradas[1])

        if all(entradas) and not produto_existe:
            self._atualizar_estado_botao(True)
            self._mostrar_mensagem("")
        else:
            self._atualizar_estado_botao(False)
            msg = "Já existe um produto com esse nome e unidade" if produto_existe else ""
            self._mostrar_mensagem(msg)


            self.mensagem.update()
            self.botao_criar_produto.update()

    def _atualizar_estado_botao(self, habilitar: bool) -> None:
        self.botao_criar_produto.disabled = not habilitar
        self.botao_criar_produto.update()

    def _mostrar_mensagem(self, texto: str) -> None:
        self.mensagem.value = texto
        self.mensagem.visible = bool(texto)
        self.mensagem.update()

    def verificar_produtos_iguais(self, nome: str, und: str) -> bool:
        if nome is None or und is None:
            return False
        produto_str = nome.lower() + und.lower()
        return any(produto_str == "".join(nu) for nu in self.nome_unidade)

    def janela_add_categoria(self, e: ft.ControlEvent) -> None:
        janela = JanelaCadCategoria(ControleDropdownV2(self.f_categoria))
        controle = ControleCategoria(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def janela_add_fornecedor(self, e: ft.ControlEvent) -> None:
        janela = JanelaCadFornecedor(ControleDropdownV2(self.f_fornecedores))
        controle = ControleFornecedores(visualizacao=janela)
        janela.definir_controle(controle)
        self.page.open(janela)

    def criar_produto(self, e: ft.ControlEvent) -> None:
        if self.controle_produto is not None:
            categorias = self._obter_categorias()
            self.controle_produto.criar_produto(
                self.entrada_nome_produto.value,
                self.entrada_unidade.value,
                self.entrada_qtd_estoque.value,
                self.entrada_estoque_min.value,
                self.entrada_preco_unidade.value,
                categorias,
                self.entrada_fornecedores.value,
                self.check_sim.value
            )
            self.page.close(self)

    def _obter_categorias(self) -> Optional[dict]:
        if not self.entrada_categoria.value:
            return None
        return {
            cat["nome"]: self.infos_categorias[cat["id"]]
            for cat in self.entrada_categoria.value
        }

    def definir_controle(self, controle) -> None:
        self.controle_produto = controle

    def ler_dados(self) -> None:
        try:
            bd = SupabaseSingleton()
            client = bd.get_client()
            categorias = (
                client.table("categoria")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
            fornecedores = (
                client.table("fornecedores")
                .select("*")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self.infos_categorias = {cat["id"]: cat["cor"] for cat in categorias}
            self._criar_conteudo(categorias, fornecedores)


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
                            LinhaHistorico(Movimentacao(*dado))
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
    def __init__(self, produto: Produto, controle_painel_infos: ControlePainelInfos) -> None:
        super().__init__(col=4, elevation=10)
        self.produto = produto
        self.controle_painel_infos = controle_painel_infos
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self.content = ft.Container(
            ft.Column([
                self._criar_cabecalho(),
                ft.Divider(height=8),
                self._criar_corpo()
            ], spacing=5),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15),
        )
    
    def _criar_cabecalho(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow([
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
        ], alignment=ft.MainAxisAlignment.CENTER)

    def _criar_corpo(self) -> ft.Column:
        op = OperadorProduto(self.produto)
        preco, valor_estoque, qtd_estoque, estoque_min = op.formatar_valores()
        return ft.Column([
            op.obter_fornecedores(),
            op.obter_categorias(),
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
        ])

    def abrir_configuracoes(self, e: ft.ControlEvent) -> None:
        self.controle_painel_infos.abrir_janela(self.produto)


class Estoque(ft.Stack):
    def __init__(self, controle_sombra) -> None:
        super().__init__()
        self.controle_sombra = controle_sombra
        self.painel_infos = PainelInfos(controle_sombra)
        self.area_produtos = ft.Container(expand=True)
        self.produtos = None

    def _criar_conteudo(self) -> None:
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

    def placeholder(self) -> None:
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _criar_grade_itens(self) -> None:
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

    def _cartoes_notificacoes(self) -> List[CartaoNotificacao]:
        estoque_baixo, estoque_critico, sem_preco = self._calcular_alertas()

        alertas = [
            {
                "condicao": estoque_baixo,
                "titulo": "Produtos abaixo do estoque mínimo",
                "descricao": "",
                "quantidade": estoque_baixo
            },
            {
                "condicao": estoque_critico,
                "titulo": "Produtos com estoque crítico",
                "descricao": "O estoque é considerado crítico quando atinge 20% do seu estoque mínimo.",
                "quantidade": estoque_critico
            },
            {
                "condicao": sem_preco,
                "titulo": "Produtos sem preço",
                "descricao": (
                    "Configurar os preços dos seus produtos possibilita o cálculo correto do seu estoque total, "
                    "do seu CMV, do custo de suas fichas técnicas, entre outros."
                ),
                "quantidade": sem_preco
            }
        ]

        return [
            self._criar_cartao_notificacao(alerta["titulo"], alerta["descricao"], alerta["quantidade"])
            for alerta in alertas if alerta["condicao"]
        ]

    def _calcular_alertas(self) -> List[float]:
        if len(self.df) == 0:
            return 0, 0, 0

        estoque_baixo = len(self.df[self.df['quantidade'] < self.df['estoque_minimo']])
        estoque_critico = len(self.df[self.df['quantidade'] < (self.df["estoque_minimo"] * 0.2)])
        sem_preco = len(self.df[self.df["preco_unidade"].isnull()])
        return estoque_baixo, estoque_critico, sem_preco

    def _criar_cartao_notificacao(
        self,
        titulo: str,
        descricao: str,
        quantidade: float
    ) -> CartaoNotificacao:
        return CartaoNotificacao(
            titulo,
            descricao,
            ft.Row([
                ft.Text(quantidade, color=ft.Colors.BLACK87, weight=ft.FontWeight.W_500, size=20)
            ]),
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

    def _obter_estatisticas(self) -> List[float]:
        if len(self.df) > 0:
            valor_total = (self.df['quantidade'] * self.df['preco_unidade']).dropna().sum()
            total_produtos = len(self.df)
        else:
            valor_total = total_produtos = 0
        return valor_total, total_produtos
    
    def rolar(self, e: ft.ControlEvent) -> None:
        self.coluna_area.scroll_to(delta=400, duration=1000)

    def janela_cad_produtos(self, e: ft.ControlEvent) -> None:
        nome_unidade = [(row["nome"], row["unidade"]) for i, row in self.df.iterrows()]
        janela = JanelaCadProduto(nome_unidade)
        controle = ControleProduto(visualizacao=self)
        janela.definir_controle(controle)
        self.page.open(janela)

    def atualizar_dados(self) -> None:
        self.ler_dados()
        self.update()

    def ler_dados(self) -> None:
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

    def _criar_df(self, dados: List) -> None:
        self.df = pd.DataFrame(dados)

    def did_mount(self) -> None:
        self.placeholder()
        self.ler_dados()
