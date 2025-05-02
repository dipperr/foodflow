import flet as ft
import numpy as np
import pandas as pd
import locale
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from datetime import datetime, timedelta
import locale
from typing import Callable, Optional

from banco_de_dados import SupabaseSingleton
from controles import (
    GradeNotificacao,
    RotuloColuna,
    TextoMonetario,
    CartaoNotificacao,
    InfosGlobal
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class Graficos:
    def grafico_estoque(self, df):
        dados = OperadorDados.dados_grafico_estoque(df)
        dados["categoria"] = dados["categoria"].str.title()
        fig_estoque = go.Figure([
            go.Bar(x=dados["categoria"], y=dados["valor_estoque"], text=dados["valor_estoque"], texttemplate="R$ %{y:.2f}")
        ])
        fig_estoque.update_traces(textposition='outside', textfont_size=18, textfont=dict(weight="bold"))
        fig_estoque.update_layout(
            margin=dict(t=5,l=10,b=10,r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=False,
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2", showticklabels=False),
            xaxis=dict(tickfont=dict(size=20), gridcolor="#ffffff"),
            barcornerradius=30,
            separators=",."
        )
        return fig_estoque
    
    def grafico_cmv(self, df):
        def definir_cores(classi):
            cores = {
                "sem class.": "#ffeb3b",
                "vendas": "#4caf50",
                "desperdício": "#e57373"
            }
            return cores.get(classi, "blue")
            
        dados = OperadorDados.dados_grafico_cmv(df)
        dados["categorias"] = dados["categorias"].str.title()
        categorias = dados.groupby("categorias")["total_movimentado"].sum().sort_values(ascending=False)
        dados = dados[dados["categorias"].isin(categorias.index[:5])]
        dados["cores"] = dados["classificacao"].apply(definir_cores)

        fig_cmv = go.Figure()

        def adicionar_trace(dados_classi):
            fig_cmv.add_trace(
                go.Bar(
                    x=dados_classi["categorias"],
                    y=dados_classi["total_movimentado"],
                    marker_color=dados_classi["cores"]
                )
            )

        for classi in dados["classificacao"].unique():
            df_fil = dados[dados["classificacao"] == classi]
            adicionar_trace(df_fil)

        fig_cmv.add_trace(
            go.Bar(
                x=categorias.index,
                y=np.zeros(len(categorias.index[:5])),
                text=categorias.values,
                texttemplate="R$ %{text:.2f}"
            )
        )

        fig_cmv.update_traces(textposition='outside', textfont_size=18, textfont=dict(weight="bold"))
        fig_cmv.update_layout(
            margin=dict(t=5,l=10,b=10,r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=False,
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2", showticklabels=False),
            xaxis=dict(tickfont=dict(size=20), gridcolor="#ffffff"),
            barcornerradius=30,
            barmode='stack',
            separators=",."
        )
        return fig_cmv

    def grafico_entradas(self, df):
        def definir_cores(classi):
            cores = {
                "sem class.": "#ffeb3b",
                "compras": "#4caf50",
                "desperdício": "#e57373"
            }
            return cores.get(classi, "blue")
        
        dados = OperadorDados.dados_grafico_entradas(df)
        dados["cores"] = dados["classificacao"].apply(definir_cores)

        fig_entradas = go.Figure()

        def adicionar_trace(dados_classi):
            fig_entradas.add_trace(
                go.Bar(
                    x=dados_classi["total_movimentado"],
                    y=["entradas"],
                    marker_color=dados_classi["cores"],
                    orientation="h"
                )
            )

        for classi in dados["classificacao"].unique():
            df_fil = dados[dados["classificacao"] == classi]
            adicionar_trace(df_fil)

        fig_entradas.update_layout(
            margin=dict(t=5,l=10,b=10,r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            showlegend=False,
            yaxis=dict(visible=False),
            xaxis=dict(visible=False),
            height=150,
            barmode="stack"
        )

        dados["total_movimentado"] = dados["total_movimentado"].apply(locale.currency, grouping=True)
        tooltip = "\n".join([" ".join(item.astype(str)) for item in dados.iloc[:, 0:2].values])

        return fig_entradas, tooltip

    def grafico_giro_estoque(self, dados):
        fig_giro = go.Figure(
            data=go.Scatter(x=dados["data_movimentacao"], y=dados["em_estoque"], line=dict(width=4), marker=dict(size=10))
        )
        fig_giro.update_xaxes(tickformat="%b %d")
        fig_giro.update_layout(
            margin=dict(t=5,l=10,b=10,r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2"),
            xaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2"),
            height=400
        )
        return fig_giro

    def grafico_volatilidade(self, df, produto):
        dados = OperadorDados.dados_grafico_volatilidade(df, produto)
        fig_volatilidade = go.Figure(
            data=go.Scatter(x=dados["data_movimentacao"], y=dados["preco_movimentacao"], line=dict(width=4), marker=dict(size=10))
        )
        fig_volatilidade.update_xaxes(tickformat="%b %d")
        fig_volatilidade.update_layout(
            margin=dict(t=5,l=10,b=10,r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2"),
            xaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2"),
            height=400
        )
        return fig_volatilidade


class OperadorDados:
    @staticmethod
    def dados_grafico_estoque(df: pd.DataFrame):
        df['valor_estoque'] = df['quantidade'] * df['preco_unidade']

        categorias = df['categorias'].apply(lambda x: x['nomes'] if isinstance(x, dict) else []).explode()

        df_expanded = df.loc[categorias.index].copy()
        df_expanded['categoria'] = categorias

        valor_categoria = df_expanded.groupby('categoria')['valor_estoque'].sum()
        valor_categoria = valor_categoria[valor_categoria > 0]
        
        return valor_categoria.nlargest(n=5).reset_index()
    
    @staticmethod
    def calcular_cmv_real(df):
        saidas = df[df["operacao"] == "saída"]
        return saidas["total_movimentado"].sum()
    
    @staticmethod
    def dados_grafico_cmv(df):
        saidas = df[df["operacao"] == "saída"]
        saidas_group = saidas.groupby(["categorias", "classificacao"]).agg({"total_movimentado": "sum"}).reset_index()
        saidas_group = saidas_group.sort_values("total_movimentado", ascending=False)
        return saidas_group

    @staticmethod
    def valor_total_entradas(df):
        entradas = df[df["operacao"] == "entrada"]
        return entradas["total_movimentado"].sum()
    
    @staticmethod
    def dados_grafico_entradas(df):
        entradas = df[df["operacao"] == "entrada"]
        return (
            entradas
            .groupby("classificacao")["total_movimentado"]
            .sum()
            .reset_index()
            .sort_values("total_movimentado", ascending=False)
        )

    @staticmethod
    def transformar_dados_movimentacoes(df):
        produtos_expandidos = pd.json_normalize(df['produtos'])
        df = pd.concat([df.drop(columns=['produtos']), produtos_expandidos], axis=1)

        df['categorias'] = df["categorias.nomes"].explode()

        df = df.drop(columns=["categorias.nomes"])

        df["operacao"] = df["operacao"].str.lower()
        df["classificacao"] = df["classificacao"].str.lower()
        df["data_movimentacao"] = pd.to_datetime(df["data_movimentacao"], format='ISO8601')
        df = df.fillna({"classificacao": "sem class.", "preco_movimentacao": df["preco_unidade"]})
        df["total_movimentado"] = df["quantidade"] * df["preco_movimentacao"]
        
        return df

    @staticmethod
    def dados_grafico_giro_estoque(df, produto):
        df_fil = df[df["nome"] == produto]
        df_fil = df_fil.sort_values("data_movimentacao")
        df_fil["em_estoque"] = df_fil["quantidade"].where(df_fil["operacao"].str.lower() == "entrada", -df_fil["quantidade"]).cumsum()
        return df_fil

    @staticmethod
    def volatilidade_preco(df):
        df_fil = df[df["data_movimentacao"] > (datetime.now() - timedelta(30)).strftime("%Y-%m-%d %H:%M:%S")]

        variacao_preco = df_fil.groupby('nome')['preco_movimentacao'].agg(['min', 'max']).reset_index()
        variacao_preco['variacao'] = variacao_preco['max'] - variacao_preco['min']
        variacao_preco = variacao_preco.sort_values("variacao", ascending=False)

        return variacao_preco[variacao_preco["variacao"] > 0].iloc[:5]

    @staticmethod
    def dados_grafico_volatilidade(df, produto):
        df_fil = df[(df["operacao"] == "entrada") & (df["nome"] == produto)]
        df_fil = df_fil.sort_values("data_movimentacao")
        return df_fil


class SeletorTemporal(ft.SegmentedButton):
    def __init__(self, on_change: Optional[Callable]=None):
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
                ),
                ft.Segment(
                    value="0",
                    icon=ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED)
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


class CartaoEstoque(ft.Card):
    def __init__(self, produtos: pd.DataFrame):
        super().__init__(col=12, elevation=10)
        self.produtos = produtos
        self._criar_conteudo()

    def _criar_conteudo(self):
        valor_estoque, qtd_produtos = self._estatisticas()
        grafico = self._criar_grafico()
        self.content = ft.Container(
            content=ft.Column([
                CabecalhoCartao("Produtos em estoque", "Visão Geral", "./icons_clone/boxes.png"),
                ft.Divider(),
                ft.Column([
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.Text("Valor em estoque", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            TextoMonetario(locale.currency(valor_estoque, grouping=True, symbol=False), 40, ft.FontWeight.BOLD, 10.5)
                        ], spacing=0, col=6),
                        ft.Column([
                            ft.Text("Produtos cadastrados", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                            ft.Text(qtd_produtos, size=20, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.START, spacing=10, col=6)
                    ], vertical_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.START, spacing=50),
                    ft.ResponsiveRow([
                        ft.Image("./icons_clone/chart-histogram.png", color=ft.Colors.BLACK54, col=1),
                        ft.Text(
                            "Valor em estoque por categoria (Top 5)",
                            color=ft.Colors.BLACK54,
                            weight=ft.FontWeight.W_500,
                            col=11
                        )
                    ]),
                    ft.Row([
                        grafico
                    ])
                ], spacing=10)
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _estatisticas(self):
        if len(self.produtos) > 0:
            valor_estoque = (self.produtos["quantidade"] * self.produtos["preco_unidade"]).dropna().sum()
            qtd_produtos = len(self.produtos)
        else:
            valor_estoque = 0
            qtd_produtos = 0
        return valor_estoque, qtd_produtos
    
    def _criar_grafico(self):
        if len(self.produtos) > 0:
            fig = Graficos().grafico_estoque(self.produtos.copy())
            grafico = PlotlyChart(fig, expand=True)
        else:
            grafico = ft.Container()
        return grafico


class CartaoGiro(ft.Card):
    def __init__(self, movimentacoes: pd.DataFrame):
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self):
        if len(self.movimentacoes):
            opcoes = self._obter_valores_dropdown(self.movimentacoes)
            conteudo = self._conteudo(opcoes)
        else:
            conteudo = self._sem_conteudo()

        self.content = ft.Container(
            content=ft.Column([
                CabecalhoCartao("Top 5 produtos", "em R$ movimentado por período", "./icons_clone/chart-line-up.png"),
                ft.Divider(),
                conteudo
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _conteudo(self, opcoes):
        self.grafico = ft.Container(
            ft.Row([self._criar_grafico(opcoes[0], 30)])
        )
        self.seletor_produto = ft.Dropdown(
            options=[
                ft.dropdown.Option(opcao)
                for opcao in opcoes
            ],
            value=opcoes[0],
            col=6,
            text_size=15,
            border_radius=ft.border_radius.all(5),
            border_width=1
        )
        return ft.Column([
            SeletorTemporal(self.seletor_temporal),
            ft.ResponsiveRow([
                self.seletor_produto
            ]),
            self.grafico
        ], spacing=10)
    
    def _sem_conteudo(self):
        return ft.Column([
            ft.ResponsiveRow([
                ft.Text(
                    "Para ver esse dado é necessário precificar seus produtos nas entradas em estoque",
                    col=12,
                    color=ft.Colors.BLACK54,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER
                )
            ])
        ], spacing=0)

    def _obter_valores_dropdown(self, movimentacoes):
        if len(movimentacoes):
            return (movimentacoes.groupby("nome")["total_movimentado"].sum().nlargest(5)).index
        else:
            return []
        
    def _criar_grafico(self, produto, tempo):
        if len(self.movimentacoes):
            dados = OperadorDados.dados_grafico_giro_estoque(self.movimentacoes, produto)
            dados_fil = self.filtrar_por_tempo(tempo, dados)
            fig = Graficos().grafico_giro_estoque(dados_fil)
            grafico = PlotlyChart(fig, expand=True)
        else:
            grafico = ft.Container()
        return grafico
    
    def seletor_temporal(self, e):
        try:
            tempo = int(e.data.strip("[]\""))
        except ValueError:
            tempo = 0

        self.atualizar_infos(tempo)

    def atualizar_infos(self, tempo):
        opcoes = self._obter_valores_dropdown(self.movimentacoes)
        self.seletor_produto.options = [
            ft.dropdown.Option(opcao)
            for opcao in opcoes
        ]
        self.grafico.content = ft.Row([self._criar_grafico(opcoes[0], tempo)])

        self.seletor_produto.update()
        self.grafico.update()

    def filtrar_por_tempo(self, tempo, movimentacoes):
        if tempo > 0:
            return movimentacoes[movimentacoes["data_movimentacao"] > (datetime.now() - timedelta(tempo)).strftime("%Y-%m-%d %H:%M:%S")]
        else:
            return movimentacoes


class CartaoFichaTecnica(ft.Card):
    def __init__(self):
        super().__init__(col=12, elevation=10)
        self.content = ft.Container(
            content=ft.Column([
                CabecalhoCartao(
                    "Volatilidade de preço",
                    "As 5 fichas técnicas com maior volatilidade de preço no último mês",
                    "./icons_clone/chart-line-up.png"
                ),
                ft.Divider(),
                ft.Column([
                    ft.ResponsiveRow([
                        ft.Text(
                            "Para ver esse dado é necessário cadastrar fichas técnicas",
                            col=12,
                            color=ft.Colors.BLACK54,
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.CENTER
                        )
                    ])
                ], spacing=0)
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )


class MarcacoesCores(ft.Row):
    def __init__(self, rotulos, cores):
        super().__init__(
            controls=[
                ft.Row([
                    ft.CircleAvatar(bgcolor=c, radius=5), ft.Text(r)
                ])
                for r, c in zip(rotulos, cores)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )


class Evento:
    def __init__(self, data):
        self.data = data


class CartaoCMV(ft.Card):
    def __init__(self, movimentacoes):
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self):
        df_fil = self.filtrar_por_tempo(30)
        self._conteudo(df_fil)

    def _conteudo(self, movimentacoes):
        self.cmv_real = TextoMonetario(
            locale.currency(self._estatisticas(movimentacoes), grouping=True, symbol=False),
            40,
            ft.FontWeight.BOLD,
            10.5
        )
        self.grafico = ft.Container(
            ft.Row([self._criar_grafico(movimentacoes)])
        )

        self.content = ft.Container(
            ft.Column([
                CabecalhoCartao(
                    "CMV",
                    "Por período, categoria e classificação de saída",
                    "./icons_clone/usd-circle.png"
                ),
                ft.Divider(),
                SeletorTemporal(self.seletor_temporal),
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Text("CMV Real", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                        self.cmv_real
                    ], spacing=0, col=6),
                    ft.Column([
                        ft.Text("CMV Teórico", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                        TextoMonetario(
                            locale.currency(0, grouping=True, symbol=False),
                            40,
                            ft.FontWeight.BOLD,
                            10.5
                        )
                    ], alignment=ft.MainAxisAlignment.START, spacing=0, col=6)
                ], vertical_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.START, spacing=50),
                ft.ResponsiveRow([
                    ft.Image("./icons_clone/chart-histogram.png", color=ft.Colors.BLACK54, col=1),
                    ft.Text("CMV real por categoria e classificação de saída (top 5 categorias)", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500, col=11)
                ]),
                self.grafico,
                MarcacoesCores(
                    ["Sem classificação", "Vendas", "Desperdício"],
                    [ft.Colors.YELLOW, ft.Colors.GREEN, ft.Colors.RED_300]
                )
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def seletor_temporal(self, e):
        try:
            tempo = int(e.data.strip("[]\""))
        except ValueError:
            tempo = 0
        
        df_fil = self.filtrar_por_tempo(tempo) if tempo > 0 else self.movimentacoes
        
        self.atualizar_infos(df_fil)

    def atualizar_infos(self, movimentacoes):
        self.cmv_real.atualizar_valor(
            locale.currency(self._estatisticas(movimentacoes), grouping=True, symbol=False)
        )

        self.grafico.content = ft.Row([self._criar_grafico(movimentacoes)])
        self.grafico.update()

    def filtrar_por_tempo(self, tempo):
        if tempo > 0:
            return self.movimentacoes[self.movimentacoes["data_movimentacao"] > (datetime.now() - timedelta(tempo)).strftime("%Y-%m-%d %H:%M:%S")]
        else:
            return self.movimentacoes

    def _estatisticas(self, movimentacoes: pd.DataFrame):
        return OperadorDados.calcular_cmv_real(movimentacoes) if len(movimentacoes) else 0
    
    def _criar_grafico(self, movimentacoes: pd.DataFrame):
        if len(movimentacoes) and "saída" in movimentacoes["operacao"].values:
            fig = Graficos().grafico_cmv(movimentacoes)
            return PlotlyChart(fig, expand=True)
        return ft.Container()


class CartaoEntradas(ft.Card):
    def __init__(self, movimentacoes):
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self):
        df_fil = self.filtrar_por_tempo(30)
        self._conteudo(df_fil)

    def _conteudo(self, movimentacoes):
        self.total_entradas = TextoMonetario(
            locale.currency(self._estatisticas(movimentacoes), grouping=True, symbol=False),
            40,
            ft.FontWeight.BOLD,
            10.5
        )
        self.grafico = ft.Container(
            ft.Row([self._criar_grafico(movimentacoes)])
        )

        self.content = ft.Container(
            content=ft.Column([
                ft.ListTile(
                    title=ft.Text("Entradas"),
                    subtitle=ft.Text("Por período e classificação", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.WHITE,
                    trailing=ft.Image("./icons_clone/dolly-flatbed.png"),
                    title_text_style=ft.TextStyle(color=ft.Colors.BLACK87, weight=ft.FontWeight.BOLD, size=17),
                    content_padding=ft.padding.all(0)
                ),
                ft.Divider(),
                ft.Column([
                    SeletorTemporal(self.seletor_temporal),
                    ft.ResponsiveRow([
                        ft.Column([
                            ft.Row([ft.Text("Valor Total", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500)]),
                            self.total_entradas
                        ], spacing=0, col=6)
                    ]),
                    self.grafico,
                    ft.Row([
                        ft.Row([
                            ft.CircleAvatar(bgcolor=ft.Colors.YELLOW, radius=5), ft.Text("Sem classificação")
                        ]),
                        ft.Row([
                            ft.CircleAvatar(bgcolor=ft.Colors.GREEN, radius=5), ft.Text("Compras")
                        ]),
                        ft.Row([
                            ft.CircleAvatar(bgcolor=ft.Colors.RED_300, radius=5), ft.Text("Transferência")
                        ])
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10)
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _estatisticas(self, movimentacoes):
        if len(movimentacoes) > 0:
            total_entradas = OperadorDados.valor_total_entradas(movimentacoes)
        else:
            total_entradas = 0
        return total_entradas
    
    def _criar_grafico(self, movimentacoes):
        if len(movimentacoes) > 0:
            fig, tooltip = Graficos().grafico_entradas(movimentacoes)
            grafico = PlotlyChart(fig, expand=True, tooltip=tooltip)
        else:
            grafico = ft.Container()
        return grafico
    
    def seletor_temporal(self, e):
        try:
            tempo = int(e.data.strip("[]\""))
        except ValueError:
            tempo = 0
        
        df_fil = self.filtrar_por_tempo(tempo) if tempo > 0 else self.movimentacoes
        
        self.atualizar_infos(df_fil)

    def atualizar_infos(self, movimentacoes):
        self.total_entradas.atualizar_valor(
            locale.currency(self._estatisticas(movimentacoes), grouping=True, symbol=False)
        )

        self.grafico.content = ft.Row([self._criar_grafico(movimentacoes)])
        self.grafico.update()

    def filtrar_por_tempo(self, tempo):
        if tempo > 0:
            return self.movimentacoes[self.movimentacoes["data_movimentacao"] > (datetime.now() - timedelta(tempo)).strftime("%Y-%m-%d %H:%M:%S")]
        else:
            return self.movimentacoes


class CartaoVolatilidade(ft.Card):
    def __init__(self, movimentacoes):
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()
    
    def _criar_conteudo(self):
        opcoes = self._obter_valores_dropdown()
        if len(opcoes):
            conteudo = self._conteudo(opcoes)
        else:
            conteudo = self._sem_conteudo()

        self.content = ft.Container(
            content=ft.Column([
                ft.ListTile(
                    title=ft.Text("Volatilidade de preço"),
                    subtitle=ft.Text("Os 5 produtos com maior volatilidade de preço no último mês", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.WHITE,
                    trailing=ft.Image("./icons_clone/chart-line-up.png"),
                    title_text_style=ft.TextStyle(color=ft.Colors.BLACK87, weight=ft.FontWeight.BOLD, size=17),
                    content_padding=ft.padding.all(0)
                ),
                ft.Divider(),
                conteudo
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _conteudo(self, opcoes):
        grafico = self._criar_grafico(opcoes[0])
        return ft.Column([
            ft.ResponsiveRow([
                ft.Dropdown(
                    options=[
                        ft.dropdown.Option(opcao)
                        for opcao in opcoes
                    ],
                    value=opcoes[0],
                    col=6,
                    text_size=15,
                    border_radius=ft.border_radius.all(5),
                    border_width=1
                )
            ]),
            ft.Row([
                grafico
            ])
        ], spacing=10)
    
    def _sem_conteudo(self):
        return ft.Column([
            ft.ResponsiveRow([
                ft.Text(
                    "Para ver esse dado é necessário precificar seus produtos nas entradas em estoque",
                    col=12,
                    color=ft.Colors.BLACK54,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER
                )
            ])
        ], spacing=0)

    def _obter_valores_dropdown(self):
        if len(self.movimentacoes):
            df_variacao = OperadorDados.volatilidade_preco(self.movimentacoes)
            return df_variacao["nome"].values if len(df_variacao) else []
        else:
            return []
        
    def _criar_grafico(self, produto):
        if len(self.movimentacoes):
            fig = Graficos().grafico_volatilidade(self.movimentacoes, produto)
            grafico = PlotlyChart(fig, expand=True)
        else:
            grafico = ft.Container()
        return grafico


class AreaCompras(ft.Column):
    def __init__(self, movimentacoes, produtos):
        super().__init__()
        self.movimentacoes = movimentacoes
        self.controls = [
            RotuloColuna("Compras", "./icons_clone/shopping-basket.png"),
            GradeNotificacao(self._cartoes_notificacoes(produtos)),
            ft.ResponsiveRow([
                CartaoEntradas(self.movimentacoes),
                CartaoVolatilidade(self.movimentacoes)
            ])
        ]

    def _cartoes_notificacoes(self, produtos):
        if len(produtos) > 0:
            estoque_baixo = len(produtos[produtos['quantidade'] < produtos['estoque_minimo']])
            estoque_critico = len(produtos[produtos['quantidade'] < (produtos["estoque_minimo"] * 0.2)])
            sem_preco = len(produtos[produtos["preco_unidade"].isnull()])
        else:
            estoque_baixo = estoque_critico = sem_preco = 0

        def criar_cartao(titulo, descricao, quantidade):
            return CartaoNotificacao(
                titulo,
                descricao,
                ft.Row([ft.Text(quantidade, color=ft.Colors.BLACK87, weight=ft.FontWeight.W_500, size=20)]),
                "./icons_clone/triangle-warning.png",
                ft.Colors.RED
            )

        cards = []
        
        if estoque_baixo:
            cards.append(
                criar_cartao(
                    "Produtos abaixo do estoque mínimo",
                    "",
                    estoque_baixo
                )
            )
        
        if estoque_critico:
            cards.append(
                criar_cartao(
                    "Produtos com estoque crítico",
                    "O estoque é considerado crítico quando atinge 20% do seu estoque mínimo.",
                    estoque_critico
                )
            )
        
        if sem_preco:
            cards.append(
                criar_cartao(
                    "Produtos sem preço",
                    "Configurar os preços dos seus produtos possibilita o cálculo correto do seu estoque total, do seu CMV, do custo de suas fichas técnicas, entre outros.",
                    sem_preco
                )
            )

        return cards


class AreaEstoque(ft.Column):
    def __init__(self, produtos):
        super().__init__()
        self.controls = [
            CartaoEstoque(produtos),
            GradeNotificacao(self._cartoes_notificacoes(produtos))
        ]

    def _cartoes_notificacoes(self, produtos):
        cartoes = [
            CartaoNotificacao(
                "Nenhum Lote vencendo",
                "",
                TextoMonetario("0,00", 20, ft.FontWeight.BOLD, 10.5),
                "./icons_clone/check-circle.png",
                ft.Colors.GREEN
            ),
            CartaoNotificacao(
                "Nenhum lote vencido",
                "",
                TextoMonetario("0,00", 20, ft.FontWeight.BOLD, 10.5),
                "./icons_clone/check-circle.png",
                ft.Colors.GREEN
            )
        ]
        # return cartoes
        return []


class AreaFichasTecnicas(ft.Column):
    def __init__(self):
        super().__init__()
        self._criar_conteudo()

    def _criar_conteudo(self):
        dados = self.ler_dados()     
        self.controls = [
            GradeNotificacao(self._cartoes_notificacoes(dados)),
            CartaoFichaTecnica()
        ]

    def _cartoes_notificacoes(self, dados):
        if len(dados) > 0:
            cartoes = [
                CartaoNotificacao(
                        "Fichas técnicas cadastradas",
                        "",
                        ft.Row([
                            ft.Text(len(dados), color=ft.Colors.BLACK87,
                            weight=ft.FontWeight.W_500, size=20)
                        ]),
                        "./icons_clone/check-circle.png",
                        ft.Colors.GREEN
                    ),
                    CartaoNotificacao(
                        "Todas as fichas técnicas estão completas",
                        "",
                        ft.Row([]),
                        "./icons_clone/check-circle.png",
                        ft.Colors.GREEN
                    )
            ]
            return cartoes
        return []
    
    def ler_dados(self):
        cliente = SupabaseSingleton().get_client()
        resposta = (
            cliente.table("fichas_tecnicas")
            .select("*")
            .eq("empresa_id", InfosGlobal().empresa_id)
            .execute()
        ).data
        return resposta


class Painel(ft.Column):
    def __init__(self):
        super().__init__()

    def criar_conteudo(self):
        self.expand = False
        self.scroll = ft.ScrollMode.ALWAYS
        self.controls = [
            ft.Container(
                ft.ResponsiveRow([
                    ft.Column([
                        RotuloColuna("Estoque", "./icons_clone/boxes.png"),
                        ft.ResponsiveRow([
                            AreaEstoque(self.produtos)
                        ]),
                        RotuloColuna("Giro de estoque", "./icons_clone/exchange.png"),
                        ft.ResponsiveRow([
                            CartaoGiro(self.movimentacoes)
                        ]),
                        RotuloColuna("Fichas técnicas", "./icons_clone/utensils.png"),
                        ft.ResponsiveRow([
                            AreaFichasTecnicas()
                        ])
                    ], col=6),
                    ft.Column([
                        RotuloColuna("CMV", "./icons_clone/usd-circle.png"),
                        ft.ResponsiveRow([
                            CartaoCMV(self.movimentacoes)
                        ]),
                        AreaCompras(self.movimentacoes, self.produtos)
                    ], col=6)
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

    def _ler_dados(self):
        client = SupabaseSingleton().get_client()
        produtos = (
            client.table("produtos")
            .select("quantidade, preco_unidade, categorias, estoque_minimo")
            .eq("empresa_id", InfosGlobal().empresa_id)
            .execute()
        )
        movimentacao = (
            client.table("movimentacao")
            .select("operacao, data_movimentacao, data_validade, quantidade, classificacao, preco_movimentacao, produtos(nome, preco_unidade, categorias)")
            .eq("empresa_id", InfosGlobal().empresa_id)
            .execute()
        )
        self.criar_dfs(produtos.data, movimentacao.data)
        self.criar_conteudo()

    def criar_dfs(self, produtos, movimentacoes):
        self.produtos = pd.DataFrame(produtos)
        self.movimentacoes = pd.DataFrame(movimentacoes)

        if len(self.movimentacoes):
            self.transformar_df()

    def transformar_df(self):
        self.movimentacoes = OperadorDados.transformar_dados_movimentacoes(self.movimentacoes)

    def did_mount(self):
        self.placeholder()
        self._ler_dados()
