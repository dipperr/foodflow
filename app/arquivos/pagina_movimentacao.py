from dateutil import parser
import flet as ft
import locale
import pandas as pd
from typing import Optional

from banco_de_dados import SupabaseSingleton
from modelos import Movimentacao
from controles import InfosGlobal
from componentes import (
    RotuloColuna,
    CartaoIndicadores,
    TextoMonetario,
    BotaoTonal,
    Filtro,
    LinhaHistorico
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class FiltrosMovimentacoes(ft.ResponsiveRow):
    def __init__(self) -> None:
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

    def limpar_filtros(self, e: ft.ControlEvent) -> None:
        for filtro in self.controls[:-2]:
            filtro.limpar()
        self.controls[-1].visible = False
        self.controls[-1].update()

    def mostrar_botao(self) -> None:
        self.controls[-1].visible = True
        self.controls[-1].update()


class PaginaMovimentacao(ft.Column):
    def __init__(self) -> None:
        super().__init__()

    def _criar_conteudo(self) -> None:
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
                                    locale.currency(total_entradas, grouping=True, symbol=False),
                                    30,
                                    ft.FontWeight.BOLD,
                                    11
                                ),
                                4
                            ),
                            CartaoIndicadores(
                                "R$ total de saídas *",
                                TextoMonetario(
                                    locale.currency(total_saidas, grouping=True, symbol=False),
                                    30,
                                    ft.FontWeight.BOLD,
                                    11
                                ),
                                4
                            )
                        ]),
                        ft.ResponsiveRow([
                            ft.Text(
                                "* os números acima consideram os filtros aplicados abaixo",
                                col=10,
                                color=ft.Colors.BLACK54,
                                weight=ft.FontWeight.W_500
                            )
                        ]),
                        ft.Divider(),
                        FiltrosMovimentacoes(),
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

    def placeholder(self) -> None:
        self.expand = True
        self.controls = [
            ft.Container(ft.ProgressRing(), expand=True, alignment=ft.alignment.center)
        ]
        self.update()

    def _movimentacoes(self) -> None:
        if len(self.df) > 0:
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
                for _, row in self.df.iterrows()
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
        return ft.ResponsiveRow([])
        
    def _estatisticas(self) -> None:
        if len(self.df):
            total_movimentacoes = len(self.df)
            total_entradas = self.df[self.df["operacao"] == "entrada"]["total_movimentado"].sum()
            total_saidas = self.df[self.df["operacao"] == "saída"]["total_movimentado"].sum()
        else:
            total_movimentacoes = total_entradas = total_saidas = 0
        return total_movimentacoes, total_entradas, total_saidas

    def obter_preco(self, preco_mov: Optional[float], preco_uni: float) -> float:
        return preco_mov if pd.notna(preco_mov) else preco_uni
    
    def ler_dados(self) -> None:
        try:
            client = SupabaseSingleton().get_client()
            respostas = (
                client.table("movimentacao")
                .select("id, operacao, data_movimentacao, quantidade, classificacao, preco_movimentacao, informacoes, produtos(nome, unidade, preco_unidade)")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .order("data_movimentacao", desc=True)
                .execute()
            ).data
        except Exception as e:
            print(e)
        else:
            self._criar_df(respostas)
            self._criar_conteudo()

    def _criar_df(self, dados: list) -> None:
        df_base = pd.DataFrame(dados)
        produtos_df = pd.json_normalize(df_base['produtos'])
        df = pd.concat([df_base.drop(columns=['produtos']), produtos_df], axis=1)
        df["classificacao"].fillna("Sem class.", inplace=True)
        df["preco_movimentacao"].fillna(df["preco_unidade"], inplace=True)
        df["total_movimentado"] = df["quantidade"] * df["preco_movimentacao"]
        df["operacao"] = df["operacao"].str.lower()

        self.df = df

    def did_mount(self) -> None:
        self.placeholder()
        self.ler_dados()
