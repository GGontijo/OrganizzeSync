import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_table
import plotly.graph_objects as go
from investments import Investments

class Dashboard:
    def __init__(self, investments: Investments):
        self.app = dash.Dash(__name__)
        self.investments = investments

    def evolucao_patrimonio_graph(self):

        movimentacoes = self.investments.historico_movimentacoes()

        movimentacoes['indice'] = movimentacoes.index


        table = dash_table.DataTable(
            id='tabela-dados',
            columns=[
                {'name': 'Índice', 'id': 'indice'}
            ] + [{'name': col, 'id': col} for col in movimentacoes.columns],
            data=movimentacoes.to_dict('records'),
        )


        self.app.layout = html.Div(children=[table])

        self.app.run_server(debug=True)
    