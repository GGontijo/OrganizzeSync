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
        movimentacoes = self.investments.historico_movimentacoes().resample('M', on='data_movimentacao')

        proventos = self.investments.ler_proventos().resample('M', on='data_pagamento')


        chart_ptfvalue = go.Figure()  # generating a figure that will be updated in the following lines
        chart_ptfvalue.add_trace(go.Scatter(x=movimentacoes['data_movimentacao'], y=movimentacoes['saldo_carteira'],
                            mode='lines+markers',  # you can also use "lines+markers", or just "markers"
                            name='Global Value'))
        chart_ptfvalue.add_trace(go.Scatter(x=proventos['data_pagamento'], y=proventos['valor_total'],
                            mode='lines+markers',  # you can also use "lines+markers", or just "markers"
                            name='Global Value'))
        chart_ptfvalue.layout.template = 'plotly_white'
        chart_ptfvalue.layout.height=500
        chart_ptfvalue.update_layout(margin = dict(t=50, b=50, l=25, r=25))  # this will help you optimize the chart space
        chart_ptfvalue.update_layout(
        #     title='Global Portfolio Value (USD $)',
            xaxis_tickfont_size=12,
            yaxis=dict(
                title='Valor: R$',
                titlefont_size=14,
                tickfont_size=12,
                ))
        
        self.app.layout = html.Div([
        dcc.Graph(
            id='evolucao-patrimonio',
            figure=chart_ptfvalue  # Use the created figure here
            )
        ])

        self.app.run_server(debug=True)
    