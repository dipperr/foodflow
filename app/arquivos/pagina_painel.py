from datetime import datetime, timedelta
from flet.plotly_chart import PlotlyChart
import flet as ft
import locale
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import List, Union

from banco_de_dados import SupabaseSingleton
from controles import InfosGlobal
from componentes import (
    SeletorTemporal,
    CabecalhoCartao,
    MarcacoesCores,
    RotuloColuna,
    TextoMonetario,
    CartaoNotificacao,
    GradeNotificacao
)

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


class Graficos:
    def __init__(self) -> None:
        self.bg_config = dict(
            margin=dict(t=5, l=10, b=10, r=10),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
        )

    def _definir_cor(self, classificacao: str, tipo: str = "cmv") -> str:
        paleta = {
            "cmv": {
                "sem class.": "#ffeb3b",
                "vendas": "#4caf50",
                "desperdício": "#e57373",
            },
            "entradas": {
                "sem class.": "#ffeb3b",
                "compras": "#4caf50",
                "desperdício": "#e57373",
            },
        }
        return paleta.get(tipo, {}).get(classificacao, "blue")

    def grafico_estoque(self, df: pd.DataFrame) -> go.Figure:
        dados = OperadorDados.dados_grafico_estoque(df)
        dados["categorias"] = dados["categorias"].str.title()

        fig = go.Figure(
            data=[
                go.Bar(
                    x=dados["categorias"],
                    y=dados["valor_estoque"],
                    text=dados["valor_estoque"],
                    texttemplate="R$ %{y:.2f}",
                )
            ]
        )

        fig.update_traces(textposition="outside", textfont_size=18)
        fig.update_layout(
            **self.bg_config,
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2", showticklabels=False),
            xaxis=dict(tickfont=dict(size=20), gridcolor="#ffffff"),
            barcornerradius=30,
            showlegend=False,
            separators=",.",
        )

        return fig
    
    def grafico_cmv(self, df: pd.DataFrame) -> go.Figure:
        dados = OperadorDados.dados_grafico_cmv(df)
        dados["categorias"] = dados["categorias"].str.title()
        categorias_top5 = dados.groupby("categorias")["total_movimentado"].sum().nlargest(5).index
        dados = dados[dados["categorias"].isin(categorias_top5)]

        dados["cores"] = dados["classificacao"].apply(lambda c: self._definir_cor(c, "cmv"))

        fig = go.Figure()

        for classi in dados["classificacao"].unique():
            df_fil = dados[dados["classificacao"] == classi]
            fig.add_trace(
                go.Bar(
                    x=df_fil["categorias"],
                    y=df_fil["total_movimentado"],
                    marker_color=df_fil["cores"]
                )
            )

        fig.add_trace(
            go.Bar(
                x=categorias_top5,
                y=np.zeros(len(categorias_top5)),
                text=dados.groupby("categorias")["total_movimentado"].sum(),
                texttemplate="R$ %{text:.2f}"
            )
        )

        fig.update_traces(textposition="outside", textfont_size=18)
        fig.update_layout(
            **self.bg_config,
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2", showticklabels=False),
            xaxis=dict(tickfont=dict(size=20), gridcolor="#ffffff"),
            barcornerradius=30,
            showlegend=False,
            barmode="stack",
            separators=",.",
        )

        return fig

    def grafico_entradas(self, df: pd.DataFrame) -> go.Figure:
        dados = OperadorDados.dados_grafico_entradas(df)
        dados["cores"] = dados["classificacao"].apply(lambda c: self._definir_cor(c, "entradas"))

        fig = go.Figure()

        for classi in dados["classificacao"].unique():
            df_fil = dados[dados["classificacao"] == classi]
            fig.add_trace(
                go.Bar(
                    x=df_fil["total_movimentado"],
                    y=["entradas"],
                    marker_color=df_fil["cores"],
                    orientation="h"
                )
            )

        fig.update_layout(
            **self.bg_config,
            height=150,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            barmode="stack"
        )

        dados["total_movimentado"] = dados["total_movimentado"].apply(locale.currency, grouping=True)
        tooltip = "\n".join([" ".join(row) for row in dados[["classificacao", "total_movimentado"]].astype(str).values])

        return fig, tooltip

    def grafico_giro_estoque(self, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure(
            data=go.Scatter(
                x=df["data_movimentacao"],
                y=df["em_estoque"],
                line=dict(width=4),
                marker=dict(size=10)
            )
        )
        fig.update_layout(
            **self.bg_config,
            height=400,
            xaxis=dict(tickformat="%b %d", tickfont=dict(size=20), gridcolor="#b2b2b2"),
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2"),
        )
        return fig

    def grafico_volatilidade(self, df: pd.DataFrame, produto: str) -> go.Figure:
        dados = OperadorDados.dados_grafico_volatilidade(df, produto)
        fig = go.Figure(
            data=go.Scatter(
                x=dados["data_movimentacao"],
                y=dados["preco_movimentacao"],
                line=dict(width=4),
                marker=dict(size=10)
            )
        )
        fig.update_layout(
            **self.bg_config,
            height=400,
            xaxis=dict(tickformat="%b %d", tickfont=dict(size=20), gridcolor="#b2b2b2"),
            yaxis=dict(tickfont=dict(size=20), gridcolor="#b2b2b2"),
        )
        return fig


class OperadorDados:
    @staticmethod
    def dados_grafico_estoque(df: pd.DataFrame) -> pd.DataFrame:
        df['valor_estoque'] = df['quantidade'] * df['preco_unidade']
        valor_categoria = df.groupby('categorias')['valor_estoque'].sum()
        valor_categoria = valor_categoria[valor_categoria > 0]
        
        return valor_categoria.nlargest(n=5).reset_index()
    
    @staticmethod
    def calcular_cmv_real(df: pd.DataFrame) -> float:
        return df[df["operacao"] == "saída"]["total_movimentado"].sum()
    
    @staticmethod
    def dados_grafico_cmv(df: pd.DataFrame) -> pd.DataFrame:
        saidas = df[df["operacao"] == "saída"]
        agrupado = (
            saidas
            .groupby(["categorias", "classificacao"])["total_movimentado"]
            .sum()
            .reset_index()
            .sort_values("total_movimentado", ascending=False)
        )
        return agrupado

    @staticmethod
    def valor_total_entradas(df: pd.DataFrame) -> pd.DataFrame:
        return df[df["operacao"] == "entrada"]["total_movimentado"].sum()
    
    @staticmethod
    def dados_grafico_entradas(df: pd.DataFrame) -> pd.DataFrame:
        entradas = df[df["operacao"] == "entrada"]
        return (
            entradas
            .groupby("classificacao")["total_movimentado"]
            .sum()
            .reset_index()
            .sort_values("total_movimentado", ascending=False)
        )

    @staticmethod
    def transformar_dados_movimentacoes(df: pd.DataFrame) -> pd.DataFrame:
        produtos_expandidos = pd.json_normalize(df['produtos'], max_level=0)
        df = pd.concat([df.drop(columns=['produtos']), produtos_expandidos], axis=1)

        categorias = df["categorias"].explode()
        df = df.loc[categorias.index]
        df["categorias"] = categorias

        df["operacao"] = df["operacao"].str.lower()
        df["classificacao"] = df["classificacao"].str.lower()
        df["data_movimentacao"] = pd.to_datetime(df["data_movimentacao"], format='ISO8601')
        df = df.fillna({"classificacao": "sem class.", "preco_movimentacao": df["preco_unidade"]})
        df["total_movimentado"] = df["quantidade"] * df["preco_movimentacao"]
        
        return df
    
    @staticmethod
    def transformar_dados_produtos(df: pd.DataFrame) -> pd.DataFrame:
        categorias = df["categorias"].explode()
        df = df.loc[categorias.index]
        df["categorias"] = categorias
        return df

    @staticmethod
    def dados_grafico_giro_estoque(df: pd.DataFrame, produto: str) -> pd.DataFrame:
        df_fil = df[df["nome"] == produto].sort_values("data_movimentacao")
        df_fil["em_estoque"] = df_fil["quantidade"].where(df_fil["operacao"].str.lower() == "entrada", -df_fil["quantidade"]).cumsum()
        return df_fil

    @staticmethod
    def volatilidade_preco(df: pd.DataFrame) -> pd.DataFrame:
        data_limite = datetime.now() - timedelta(days=30)
        df_recente = df[df["data_movimentacao"] > data_limite.strftime("%Y-%m-%d %H:%M:%S")]

        variacao = (
            df_recente
            .groupby("nome")["preco_movimentacao"]
            .agg(["min", "max"])
            .reset_index()
        )
        variacao["variacao"] = variacao["max"] - variacao["min"]

        return variacao[variacao["variacao"] > 0].sort_values("variacao", ascending=False).head(5)
    
    @staticmethod
    def dados_grafico_volatilidade(df: pd.DataFrame, produto: str) -> pd.DataFrame:
        df_filtrado = df[(df["operacao"] == "entrada") & (df["nome"] == produto)]
        return df_filtrado.sort_values("data_movimentacao")


class CartaoEstoque(ft.Card):
    def __init__(self, produtos: pd.DataFrame) -> None:
        super().__init__(col=12, elevation=10)
        self.produtos = produtos
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        valor_estoque, qtd_produtos = self._calcular_estatisticas()
        grafico = self._criar_grafico()

        self.content = ft.Container(
            content=ft.Column([
                self._montar_cabecalho(),
                ft.Divider(),
                self._montar_corpo(valor_estoque, qtd_produtos, grafico)
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _montar_cabecalho(self) -> None:
        return CabecalhoCartao("Produtos em estoque", "Visão Geral", "./icons_clone/boxes.png")

    def _montar_corpo(self, valor_estoque: float, qtd_produtos: int, grafico: PlotlyChart) -> ft.Column:
        return ft.Column([
            self._montar_metricas(valor_estoque, qtd_produtos),
            self._montar_legenda(),
            ft.Row([grafico])
        ], spacing=10)

    def _montar_metricas(self, valor_estoque: float, qtd_produtos: int) -> ft.ResponsiveRow:
        return ft.ResponsiveRow([
            ft.Column([
                ft.Text("Valor em estoque", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                TextoMonetario(
                    locale.currency(valor_estoque, grouping=True, symbol=False),
                    40,
                    ft.FontWeight.BOLD,
                    10.5
                )
            ], spacing=0, col=6),
            ft.Column([
                ft.Text("Produtos cadastrados", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
                ft.Text(str(qtd_produtos), size=20, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.START, spacing=10, col=6)
        ], vertical_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.START, spacing=50)

    def _montar_legenda(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow([
            ft.Image("./icons_clone/chart-histogram.png", color=ft.Colors.BLACK54, col=1),
            ft.Text(
                "Valor em estoque por categoria (Top 5)",
                color=ft.Colors.BLACK54,
                weight=ft.FontWeight.W_500,
                col=11
            )
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _calcular_estatisticas(self) -> tuple:
        if self.produtos.empty:
            return 0, 0

        self.produtos["valor_total"] = self.produtos["quantidade"] * self.produtos["preco_unidade"]
        valor_estoque = self.produtos["valor_total"].dropna().sum()
        qtd_produtos = len(self.produtos)
        return valor_estoque, qtd_produtos

    def _criar_grafico(self) -> Union[ft.Container, PlotlyChart]:
        if self.produtos.empty:
            return ft.Container()

        fig = Graficos().grafico_estoque(self.produtos.copy())
        return PlotlyChart(fig, expand=True)


class CartaoGiro(ft.Card):
    def __init__(self, movimentacoes: pd.DataFrame) -> None:
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        if self.movimentacoes.empty:
            conteudo = self._sem_conteudo()
        else:
            self.opcoes_produtos = self._obter_top_produtos()
            conteudo = self._conteudo_completo()

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

    def _conteudo_completo(self) -> ft.Column:
        produto_inicial = self.opcoes_produtos[0]
        self.grafico = ft.Container(ft.Row([self._criar_grafico(produto_inicial, 30)]))

        self.seletor_produto = ft.Dropdown(
            options=[ft.dropdown.Option(produto) for produto in self.opcoes_produtos],
            value=produto_inicial,
            col=6,
            text_size=15,
            border_radius=ft.border_radius.all(5),
            border_width=1,
            on_change=self._ao_mudar_produto
        )

        self.seletor_temporal = SeletorTemporal(self._ao_alterar_tempo)

        return ft.Column([
            self.seletor_temporal,
            ft.ResponsiveRow([self.seletor_produto]),
            self.grafico
        ], spacing=10)
    
    def _ao_mudar_produto(self, e: ft.ControlEvent) -> None:
        tempo = list(self.seletor_temporal.valor)
        self.grafico.content = ft.Row([self._criar_grafico(e.data, int(tempo[0]))])
        self.grafico.update()

    def _sem_conteudo(self) -> ft.Column:
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
        ])

    def _obter_top_produtos(self) -> List:
        top_produtos = (
            self.movimentacoes.groupby("nome")["total_movimentado"]
            .sum()
            .nlargest(5)
            .index.tolist()
        )
        return top_produtos if top_produtos else []

    def _criar_grafico(self, produto: str, tempo: int) -> Union[ft.Container, PlotlyChart]:
        dados = OperadorDados.dados_grafico_giro_estoque(self.movimentacoes, produto)
        dados_filtrados = self._filtrar_por_tempo(tempo, dados)

        if dados_filtrados.empty:
            return ft.Container()

        fig = Graficos().grafico_giro_estoque(dados_filtrados)
        return PlotlyChart(fig, expand=True)

    def _ao_alterar_tempo(self, e: ft.ControlEvent) -> None:
        try:
            tempo = int(e.data.strip("[]\""))
        except ValueError:
            tempo = 0
        self._atualizar_infos(tempo)

    def _atualizar_infos(self, tempo: int) -> None:
        self.opcoes_produtos = self._obter_top_produtos()

        self.seletor_produto.options = [
            ft.dropdown.Option(produto) for produto in self.opcoes_produtos
        ]
        self.seletor_produto.value = self.opcoes_produtos[0] if self.opcoes_produtos else None

        novo_grafico = self._criar_grafico(self.seletor_produto.value, tempo)
        self.grafico.content = ft.Row([novo_grafico])

        self.seletor_produto.update()
        self.grafico.update()

    def _filtrar_por_tempo(self, tempo: int, df: pd.DataFrame) -> pd.DataFrame:
        if tempo <= 0:
            return df
        data_limite = datetime.now() - timedelta(days=tempo)
        return df[df["data_movimentacao"] > data_limite.strftime("%Y-%m-%d %H:%M:%S")]


class CartaoFichaTecnica(ft.Card):
    def __init__(self) -> None:
        super().__init__(col=12, elevation=10)
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
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


class CartaoCMV(ft.Card):
    def __init__(self, movimentacoes: pd.DataFrame) -> None:
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        df_filtrado = self._filtrar_por_tempo(30) if len(self.movimentacoes) > 0 else pd.DataFrame([])
        self._montar_conteudo(df_filtrado)

    def _montar_conteudo(self, movimentacoes: pd.DataFrame) -> None:
        cmv_valor = self._calcular_cmv(movimentacoes)
        self.cmv_real = TextoMonetario(
            locale.currency(cmv_valor, grouping=True, symbol=False),
            40,
            ft.FontWeight.BOLD,
            10.5
        )

        self.grafico = ft.Container(
            ft.Row([self._criar_grafico(movimentacoes)]) if len(movimentacoes) else None
        )

        self.content = ft.Container(
            ft.Column([
                CabecalhoCartao(
                    "CMV",
                    "Por período, categoria e classificação de saída",
                    "./icons_clone/usd-circle.png"
                ),
                ft.Divider(),
                SeletorTemporal(self._ao_alterar_tempo),
                self._montar_valores_cmv(),
                self._montar_titulo_grafico(),
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

    def _montar_valores_cmv(self) -> None:
        return ft.ResponsiveRow([
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
            ], spacing=0, col=6)
        ], vertical_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.START, spacing=50)

    def _montar_titulo_grafico(self) -> None:
        return ft.ResponsiveRow([
            ft.Image("./icons_clone/chart-histogram.png", color=ft.Colors.BLACK54, col=1),
            ft.Text(
                "CMV real por categoria e classificação de saída (top 5 categorias)",
                color=ft.Colors.BLACK54,
                weight=ft.FontWeight.W_500,
                col=11
            )
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _ao_alterar_tempo(self, e: ft.ControlEvent) -> None:
        try:
            tempo = int(e.data.strip("[]\""))
        except ValueError:
            tempo = 0

        df_filtrado = self._filtrar_por_tempo(tempo) if tempo > 0 else self.movimentacoes
        self._atualizar_infos(df_filtrado)

    def _atualizar_infos(self, movimentacoes: pd.DataFrame)-> None:
        novo_valor = locale.currency(self._calcular_cmv(movimentacoes), grouping=True, symbol=False)
        self.cmv_real.atualizar_valor(novo_valor)
        self.grafico.content = ft.Row([self._criar_grafico(movimentacoes)])
        self.grafico.update()

    def _filtrar_por_tempo(self, dias: int) -> pd.DataFrame:
        if dias <= 0:
            return self.movimentacoes
        data_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
        return self.movimentacoes[self.movimentacoes["data_movimentacao"] > data_limite]

    def _calcular_cmv(self, movimentacoes: pd.DataFrame) -> float:
        return OperadorDados.calcular_cmv_real(movimentacoes) if len(movimentacoes) else 0

    def _criar_grafico(self, movimentacoes: pd.DataFrame) -> ft.Control:
        if len(movimentacoes) and "saída" in movimentacoes["operacao"].values:
            fig = Graficos().grafico_cmv(movimentacoes)
            return PlotlyChart(fig, expand=True)
        return ft.Container()


class CartaoEntradas(ft.Card):
    def __init__(self, movimentacoes: pd.DataFrame) -> None:
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        df_filtrado = self._filtrar_por_tempo(30) if len(self.movimentacoes) > 0 else pd.DataFrame([])
        self._montar_conteudo(df_filtrado)

    def _montar_conteudo(self, movimentacoes: pd.DataFrame) -> None:
        valor_entradas = self._calcular_total_entradas(movimentacoes)
        self.total_entradas = TextoMonetario(
            locale.currency(valor_entradas, grouping=True, symbol=False),
            40,
            ft.FontWeight.BOLD,
            10.5
        )

        self.grafico = ft.Container(
            ft.Row([self._criar_grafico(movimentacoes)]) if len(movimentacoes) else None
        )

        self.content = ft.Container(
            content=ft.Column([
                self._montar_cabecalho(),
                ft.Divider(),
                self._montar_corpo()
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _montar_cabecalho(self) -> ft.ListTile:
        return ft.ListTile(
            title=ft.Text("Entradas"),
            subtitle=ft.Text("Por período e classificação", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500),
            bgcolor=ft.Colors.WHITE,
            trailing=ft.Image("./icons_clone/dolly-flatbed.png"),
            title_text_style=ft.TextStyle(color=ft.Colors.BLACK87, weight=ft.FontWeight.BOLD, size=17),
            content_padding=ft.padding.all(0)
        )

    def _montar_corpo(self) -> ft.Column:
        return ft.Column([
            SeletorTemporal(self._ao_alterar_tempo),
            self._montar_valores(),
            self.grafico,
            self._montar_legenda()
        ], spacing=10)

    def _montar_valores(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow([
            ft.Column([
                ft.Row([
                    ft.Text("Valor Total", color=ft.Colors.BLACK54, weight=ft.FontWeight.W_500)
                ]),
                self.total_entradas
            ], spacing=0, col=6)
        ])

    def _montar_legenda(self) -> ft.Row:
        return ft.Row([
            ft.Row([ft.CircleAvatar(bgcolor=ft.Colors.YELLOW, radius=5), ft.Text("Sem classificação")]),
            ft.Row([ft.CircleAvatar(bgcolor=ft.Colors.GREEN, radius=5), ft.Text("Compras")]),
            ft.Row([ft.CircleAvatar(bgcolor=ft.Colors.RED_300, radius=5), ft.Text("Transferência")])
        ], alignment=ft.MainAxisAlignment.CENTER)

    def _ao_alterar_tempo(self, e: ft.ControlEvent) -> None:
        try:
            tempo = int(e.data.strip("[]\""))
        except ValueError:
            tempo = 0

        df_filtrado = self._filtrar_por_tempo(tempo) if tempo > 0 else self.movimentacoes
        self._atualizar_infos(df_filtrado)

    def _atualizar_infos(self, movimentacoes: pd.DataFrame) -> None:
        novo_valor = locale.currency(self._calcular_total_entradas(movimentacoes), grouping=True, symbol=False)
        self.total_entradas.atualizar_valor(novo_valor)
        self.grafico.content = ft.Row([self._criar_grafico(movimentacoes)])
        self.grafico.update()

    def _filtrar_por_tempo(self, dias: int) -> pd.DataFrame:
        if dias <= 0:
            return self.movimentacoes
        data_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")
        return self.movimentacoes[self.movimentacoes["data_movimentacao"] > data_limite]

    def _calcular_total_entradas(self, movimentacoes: pd.DataFrame) -> pd.DataFrame:
        return OperadorDados.valor_total_entradas(movimentacoes) if len(movimentacoes) else 0

    def _criar_grafico(self, movimentacoes: pd.DataFrame) -> Union[ft.Container, PlotlyChart]:
        if len(movimentacoes) > 0:
            fig, tooltip = Graficos().grafico_entradas(movimentacoes)
            return PlotlyChart(fig, expand=True, tooltip=tooltip)
        return ft.Container()


class CartaoVolatilidade(ft.Card):
    def __init__(self, movimentacoes: pd.DataFrame) -> None:
        super().__init__(col=12, elevation=10)
        self.movimentacoes = movimentacoes
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        self.opcoes_produtos = self._obter_produtos_com_volatilidade()

        if self.opcoes_produtos:
            conteudo = self._conteudo_completo()
        else:
            conteudo = self._sem_conteudo()

        self.content = ft.Container(
            content=ft.Column([
                ft.ListTile(
                    title=ft.Text("Volatilidade de preço"),
                    subtitle=ft.Text(
                        "Os 5 produtos com maior volatilidade de preço no último mês",
                        color=ft.Colors.BLACK54,
                        weight=ft.FontWeight.W_500
                    ),
                    trailing=ft.Image("./icons_clone/chart-line-up.png"),
                    bgcolor=ft.Colors.WHITE,
                    title_text_style=ft.TextStyle(
                        color=ft.Colors.BLACK87,
                        weight=ft.FontWeight.BOLD,
                        size=17
                    ),
                    content_padding=ft.padding.all(0)
                ),
                ft.Divider(),
                conteudo
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(15)
        )

    def _conteudo_completo(self) -> ft.Column:
        produto_inicial = self.opcoes_produtos[0]
        self.grafico = ft.Container(ft.Row([self._criar_grafico(produto_inicial)]))

        self.seletor_produto = ft.Dropdown(
            options=[ft.dropdown.Option(produto) for produto in self.opcoes_produtos],
            value=produto_inicial,
            col=6,
            text_size=15,
            border_radius=ft.border_radius.all(5),
            border_width=1,
            on_change=self._ao_mudar_produto
        )

        return ft.Column([
            ft.ResponsiveRow([self.seletor_produto]),
            self.grafico
        ], spacing=10)

    def _sem_conteudo(self) -> ft.Column:
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
        ])

    def _obter_produtos_com_volatilidade(self) -> List:
        if self.movimentacoes.empty:
            return []

        df_variacao = OperadorDados.volatilidade_preco(self.movimentacoes)
        return df_variacao["nome"].tolist() if not df_variacao.empty else []

    def _criar_grafico(self, produto: str) -> Union[ft.Container, PlotlyChart]:
        if self.movimentacoes.empty:
            return ft.Container()

        fig = Graficos().grafico_volatilidade(self.movimentacoes, produto)
        return PlotlyChart(fig, expand=True)

    def _ao_mudar_produto(self, e: ft.ControlState) -> None:
        novo_produto = e.control.value
        self.grafico.content = ft.Row([self._criar_grafico(novo_produto)])
        self.grafico.update()


class AreaCompras(ft.Column):
    def __init__(self, movimentacoes: pd.DataFrame, produtos: pd.DataFrame) -> None:
        super().__init__()
        self._criar_conteudo(movimentacoes, produtos)

    def _criar_conteudo(self, movimentacoes: pd.DataFrame, produtos: pd.DataFrame):
        self.controls = [
            RotuloColuna("Compras", "./icons_clone/shopping-basket.png"),
            GradeNotificacao(self._cartoes_notificacoes(produtos)),
            ft.ResponsiveRow([
                CartaoEntradas(movimentacoes),
                CartaoVolatilidade(movimentacoes)
            ])
        ]

    def _cartoes_notificacoes(self, produtos: pd.DataFrame) -> List[CartaoNotificacao]:
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
                    "Configurar os preços dos seus produtos possibilita o cálculo correto do seu estoque total,\
                    do seu CMV, do custo de suas fichas técnicas, entre outros.",
                    sem_preco
                )
            )

        return cards


class AreaEstoque(ft.Column):
    def __init__(self, produtos: pd.DataFrame) -> None:
        super().__init__()
        self._criar_conteudos(produtos)

    def _criar_conteudos(self, produtos: pd.DataFrame) -> None:
        self.controls = [
            CartaoEstoque(produtos),
            GradeNotificacao(self._cartoes_notificacoes(produtos))
        ]

    def _cartoes_notificacoes(self, produtos) -> List:
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
    def __init__(self) -> None:
        super().__init__()
        self._criar_conteudo()

    def _criar_conteudo(self) -> None:
        dados = self.ler_dados()     
        self.controls = [
            GradeNotificacao(self._cartoes_notificacoes(dados)),
            CartaoFichaTecnica()
        ]

    def _cartoes_notificacoes(self, dados: list) -> List:
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
    
    def ler_dados(self) -> List:
        cliente = SupabaseSingleton().get_client()
        resposta = (
            cliente.table("fichas_tecnicas")
            .select("*")
            .eq("empresa_id", InfosGlobal().empresa_id)
            .execute()
        ).data
        return resposta


class Painel(ft.Column):
    def __init__(self) -> None:
        super().__init__()

    def did_mount(self) -> None:
        self._mostrar_placeholder()
        self._carregar_dados()

    def _mostrar_placeholder(self) -> None:
        self.expand = True
        self.controls = [
            ft.Container(
                content=ft.ProgressRing(),
                expand=True,
                alignment=ft.alignment.center
            )
        ]
        self.update()

    def _carregar_dados(self) -> None:
        client = SupabaseSingleton().get_client()
        try:
            produtos_raw = (
                client.table("produtos")
                .select("quantidade, preco_unidade, categorias, estoque_minimo")
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data

            movimentacoes_raw = (
                client.table("movimentacao")
                .select(
                    "operacao, data_movimentacao, data_validade, quantidade, classificacao,"
                    "preco_movimentacao, produtos(nome, preco_unidade, categorias)"
                )
                .eq("empresa_id", InfosGlobal().empresa_id)
                .execute()
            ).data

        except Exception as e:
            print("Erro ao carregar dados do Supabase:", e)
            produtos_df, movimentacoes_df = pd.DataFrame(), pd.DataFrame()
        else:
            produtos_df, movimentacoes_df = self._preparar_dataframes(produtos_raw, movimentacoes_raw)

        self._criar_conteudo(produtos_df, movimentacoes_df)

    def _preparar_dataframes(self, produtos: List, movimentacoes: List) -> tuple:
        df_produtos = pd.DataFrame(produtos)
        df_movimentacoes = pd.DataFrame(movimentacoes)

        if not df_produtos.empty:
            df_produtos = OperadorDados.transformar_dados_produtos(df_produtos)

        if not df_movimentacoes.empty:
            df_movimentacoes = OperadorDados.transformar_dados_movimentacoes(df_movimentacoes)

        return df_produtos, df_movimentacoes

    def _criar_conteudo(self, df_produtos: pd.DataFrame, df_movimentacoes: pd.DataFrame) -> None:
        self.expand = False
        self.scroll = ft.ScrollMode.ALWAYS
        self.controls = [
            ft.Container(
                padding=ft.padding.all(20),
                content=ft.ResponsiveRow([
                    ft.Column([
                        RotuloColuna("Estoque", "./icons_clone/boxes.png"),
                        ft.ResponsiveRow([AreaEstoque(df_produtos)]),

                        RotuloColuna("Giro de estoque", "./icons_clone/exchange.png"),
                        ft.ResponsiveRow([CartaoGiro(df_movimentacoes)]),

                        RotuloColuna("Fichas técnicas", "./icons_clone/utensils.png"),
                        ft.ResponsiveRow([AreaFichasTecnicas()])
                    ], col=6),

                    ft.Column([
                        RotuloColuna("CMV", "./icons_clone/usd-circle.png"),
                        ft.ResponsiveRow([CartaoCMV(df_movimentacoes)]),

                        AreaCompras(df_movimentacoes, df_produtos)
                    ], col=6)
                ])
            )
        ]
        self.update()
