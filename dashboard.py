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

        # Movimentacoes possui um multi index entre data_movimentacao e ticker, gostaria de manter apenas o data_movimentacao como index preservando o ticker
        #movimentacoes.reset_index('ticker', inplace=True)

         # Cria o gráfico Plotly
        chart_ptfvalue = go.Figure()
        chart_ptfvalue.add_trace(go.Scatter(x=movimentacoes.index, y=movimentacoes.valor_carteira,
                            mode='lines',
                            name='Global Value',
                            line=dict(color='white')))
        chart_ptfvalue.layout.template = 'plotly_dark'
        chart_ptfvalue.layout.height=500
        chart_ptfvalue.update_layout(margin = dict(t=50, b=50, l=25, r=25))
        chart_ptfvalue.update_layout(
            title='Valor Toal Portfólio',
            xaxis_tickfont_size=12,
            yaxis=dict(
                title='Valor: R$ BRL',
                titlefont_size=14,
                tickfont_size=12,
                ))

        # Define o layout do dashboard usando componentes HTML do Dash
        self.app.layout = html.Div(children=[
            html.H1('Dashboard de Investimentos'),
            dcc.Graph(figure=chart_ptfvalue)  # Insere o gráfico no dashboard
        ])

        #movimentacoes['indice'] = movimentacoes.index


        #table = html.Table(
        #    # Header
        #    [html.Tr([html.Th(col) for col in movimentacoes.columns])] +
        #    # Rows
        #    [html.Tr([
        #    html.Td(movimentacoes.iloc[i][col]) for col in movimentacoes.columns
        #    ]) for i in range(len(movimentacoes))]
        #)

        #self.app.layout = html.Div(children=[table])

        self.app.run_server(debug=True)
    