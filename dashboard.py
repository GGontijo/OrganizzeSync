import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from investments import Investments

class Dashboard:
    def __init__(self, investments: Investments):
        self.app = dash.Dash(__name__)
        self.investments = investments

    def evolucao_patrimonio_graph(self):

        teste = self.investments.evolucao_posicoes()
        movimentacoes = self.investments.historico_movimentacoes().resample('M', on='data_movimentacao')

        proventos = self.investments.ler_proventos().resample('M', on='data_pagamento')


        table = html.Table(
            # Header
            [html.Tr([html.Th(col) for col in movimentacoes.columns])] +

            # Rows
            [html.Tr([
            html.Td(movimentacoes.iloc[i][col]) for col in movimentacoes.columns
            ]) for i in range(len(movimentacoes))]
        )
        
        self.app.layout = html.Div(children=[table])

        self.app.run_server(debug=True)
    