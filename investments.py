from database.sqlite import SQLite
from helpers.config_helper import Config
from organizzesync import OrganizzeSync
from helpers.logger_helper import Logger
from models.organizze_models import *
from helpers.data_helper import convert_amount_to_cents, convert_amount_to_decimal
import pandas as pd
from models.b3_models import *
from models.organizze_models import TransactionCreateModel
from datetime import datetime, timedelta
from helpers.date_helper import *
from services.organizze_service import Organizze_Service
from services.b3_service import B3_Service
import yfinance as yf

class Investments:
    '''Esta classe oferece métodos para sincronização e manipulação de dados de investimentos.'''
    
    def __init__(self, logger: Logger, organizze: OrganizzeSync, organizze_service: Organizze_Service, b3_service: B3_Service) -> None:
        self.organizze_service = organizze_service
        #self.organizze.update_old_transactions(resync=True) # Atualiza a base inteira de dados
        _config = Config()
        _database_data = _config.get_config("database")
        _database_path = _database_data["investments_path"]
        self.db = SQLite(_database_path)
        self.logger = logger
        self.organizze = organizze
        self.b3 = b3_service

    def sync_renda_fixa(self, valor_liquido: float):
        saldo_conta = sum(x.amount_cents for x in list(filter(lambda x: x.account_id == EnumOrganizzeAccounts.RENDA_FIXA.value, self.organizze.old_transactions)))

        valor_faltante = round(valor_liquido - convert_amount_to_decimal(saldo_conta), 2)
        movimentacoes_rendimentos = list(filter(lambda x: x.account_id == EnumOrganizzeAccounts.RENDA_FIXA.value and x.category_id == 71967471, self.organizze.old_transactions))
        transactions_list = []

        # Obter a data do transaction mais recente
        transaction_mais_recente = max(movimentacoes_rendimentos, key=lambda x: datetime.strptime(x.date, '%Y-%m-%d').date())
        transaction_date_mais_recente = datetime.strptime(transaction_mais_recente.date, '%Y-%m-%d').date()

        diff_meses = count_months_between_dates(transaction_date_mais_recente, datetime.today().date())

        current_date = datetime.today()

        total_meses = diff_meses.months
        total_dias = diff_meses.days

        valor_proporcional_mes = valor_faltante / (total_meses + (total_dias / 30.0))

        for _ in range(total_meses):
            current_date = current_date.replace(day=1) - timedelta(days=1)
            transactions_list.append(TransactionCreateModel(
                description= f'Rendimento CDB Liquido aferido em {datetime.today().date()}',
                date= current_date.strftime("%Y-%m-%d"),
                category_id= 71967471,
                amount_cents= convert_amount_to_cents(valor_proporcional_mes),
                category_name= self.organizze.get_category_name_by_id(71967471),
                account_id= EnumOrganizzeAccounts.RENDA_FIXA.value
            ))

        # Distribuir o valor proporcional para os dias restantes
        if total_dias:
            valor_dias_restantes = valor_proporcional_mes * (total_dias / 30.0)
            transactions_list.append(TransactionCreateModel(
                description= f'Rendimento CDB Liquido aferido em {datetime.today().date()} - Parcial ref a {total_dias} dias',
                date= datetime.today().strftime("%Y-%m-%d"),
                category_id= 71967471,
                amount_cents= convert_amount_to_cents(valor_dias_restantes),
                category_name= self.organizze.get_category_name_by_id(71967471),
                account_id= EnumOrganizzeAccounts.RENDA_FIXA.value
            ))
        
        for i in transactions_list:
            self.organizze_service.create_transaction(i)

    def sync_proventos(self):
        data_prov = self.db.select('SELECT MAX(data_pagamento) AS data_pagamento_recente FROM proventos')[0][0]
        data_inicio = datetime.strptime(data_prov, "%Y-%m-%dT%H:%M:%S") + timedelta(days= 1)
        ultimo_dia = get_ultimo_dia_util() # Precisa ser um dia útil anterior
        provento: Provento
        lista_mes_provento = self.b3.get_proventos(data_inicio.strftime("%Y-%m-%d"), ultimo_dia.strftime("%Y-%m-%d"))
        for mes_provento in lista_mes_provento:
            for provento in mes_provento.proventos:
                ticker = provento.descricaoProduto.split('-')[0].strip()
                preco_unitario = f"'{provento.precoUnitario}'" if provento.precoUnitario is not None else 'NULL'
                quantidade = f"'{provento.quantidadeTotal}'" if provento.quantidadeTotal is not None else 'NULL'
                tipo_evento = f"'{provento.tipoEvento}'" if provento.tipoEvento is not None else 'NULL'
                valor_total = f"'{provento.totalNegociado}'" if provento.totalNegociado is not None else 'NULL'

                transaction = TransactionCreateModel(description= f'{ticker} - {provento.tipoEvento} ref {provento.quantidadeTotal} cotas',
                                                 account_id=EnumOrganizzeAccounts.RENDA_VARIAVEL.value,
                                                 date=provento.dataPagamento,
                                                 category_id= 71967471,
                                                 amount_cents=convert_amount_to_cents(provento.totalNegociado),
                                                 category_name=self.organizze.get_category_name_by_id(71967471))
                transaction_log = self.organizze_service.create_transaction(transaction) # Sincroniza proventos no organizze
                _query = f'''INSERT INTO PROVENTOS VALUES ('{provento.dataPagamento}', '{ticker}', '{provento.descricaoProduto}', {preco_unitario}, 
                        {quantidade}, {tipo_evento}, {valor_total})'''
                self.db.insert(_query)

    def sync_movimentacoes(self):
        data_mov = self.db.select('SELECT MAX(data_movimentacao) AS data_movimentacao_recente FROM movimentacoes')[0][0]
        data_inicio = datetime.strptime(data_mov, "%Y-%m-%dT%H:%M:%S") + timedelta(days= 1)
        ultimo_dia = get_ultimo_dia_util() # Precisa ser um dia útil anterior
        movimento: Movimento
        lista_mes_movimento = self.b3.get_movimentacoes(data_inicio.strftime("%Y-%m-%d"), ultimo_dia.strftime("%Y-%m-%d"))
        for mes_movimento in lista_mes_movimento:
            for movimento in mes_movimento.movimentacoes:
                ticker = movimento.nomeProduto.split('-')[0].strip()
                preco_unitario = f"'{movimento.precoUnitario}'" if movimento.precoUnitario is not None else 'NULL'
                quantidade = f"'{movimento.quantidade}'" if movimento.quantidade is not None else 'NULL'
                tipo_movimentacao = f"'{movimento.tipoMovimentacao}'" if movimento.tipoMovimentacao is not None else 'NULL'
                tipo_operacao = f"'{movimento.tipoOperacao}'" if movimento.tipoOperacao is not None else 'NULL'
                valor_operacao = f"'{movimento.valorOperacao}'" if movimento.valorOperacao is not None else 'NULL'
                tipo = self.tipo_ativo(ticker)
                tipo_ativo = f"'{tipo}'" if tipo is not None else 'NULL'


                if movimento.tipoMovimentacao not in ['Juros Sobre Capital Próprio', 'Rendimento', 'Dividendo']: # Ignora proventos
                    _query = f'''INSERT INTO MOVIMENTACOES VALUES ('{movimento.dataMovimentacao}', '{ticker}', '{movimento.nomeProduto}', {preco_unitario}, 
                            {quantidade}, {tipo_movimentacao}, {tipo_operacao}, {valor_operacao}, {tipo_ativo})'''
                    
                    self.db.insert(_query)
        
    def tipo_ativo(self, ticker: str) -> str:
        ativo_info = yf.Ticker(f'{ticker}.SA').info
        try:
            if ('longName' in ativo_info and 'fundo De investimento' in ativo_info['longName'].lower()) or ('shortName' in ativo_info and 'fii' in ativo_info['shortName'].lower()):
                return 'FII'
            else:
                return 'Ação'
            
        except Exception as err:
            self.logger.log('ERROR', f'Houve um problema ao buscar informações via Yahoo do ativo {ticker}: {err}')
            return None
        

    def historico_renda_fixa(self):
        conn = self.db.connection()
        rf_raw = ''


        
    def historico_movimentacoes(self):
        conn = self.db.connection()
        mov_raw = pd.read_sql_query("SELECT * FROM movimentacoes", conn)

        # Filtra as movimentações não desejadas (subscrição, cessão de direitos etc..)
        mov = mov_raw.query("preco_unitario.notna()")

        datas_mov = [datetime.strptime(data, '%Y-%m-%dT%H:%M:%S') for data in mov['data_movimentacao'].unique()]

        # Define a data mínima e máxima do rastreamento
        data_inicio = datetime.strptime(mov['data_movimentacao'].min(), '%Y-%m-%dT%H:%M:%S') - timedelta(days=10)
        data_fim = datetime.strptime(mov['data_movimentacao'].max(), '%Y-%m-%dT%H:%M:%S')

        # Obtém datas úteis para preencher os intervalos vazios
        datas_uteis = get_dias_uteis(data_inicio, data_fim, exclude_list=datas_mov)

        mov['data_movimentacao'] = pd.to_datetime(mov['data_movimentacao'], format='%Y-%m-%dT%H:%M:%S')

        # Preenche os valores NaN com 0 e converte as colunas para float
        mov['valor_operacao'] = mov['valor_operacao'].astype(float).fillna(0)
        mov['preco_unitario'] = mov['preco_unitario'].astype(float).fillna(0)

        mov.sort_values(by='data_movimentacao', inplace=True)

        # Calcula a evolução de saldo total da carteira
        mov['credito'] = mov.loc[mov['tipo_operacao'] == 'Credito', 'valor_operacao']
        mov['debito'] = mov.loc[mov['tipo_operacao'] == 'Debito', 'valor_operacao']

        
        # Calcula a evolução de saldo total por ativo
        mov['credito'].fillna(0, inplace=True)
        mov['debito'].fillna(0, inplace=True)
        mov['quantidade'].fillna(0, inplace=True)

        mov['saldo_credito_ativo'] = mov.groupby(['ticker', 'data_movimentacao'])['credito'].cumsum()
        mov['saldo_debito_ativo'] = mov.groupby(['ticker', 'data_movimentacao'])['debito'].cumsum()
        mov['saldo_ticker'] = mov['saldo_credito_ativo'] - mov['saldo_debito_ativo']

        # Passo 2: Calcular o saldo do dia anterior para cada grupo 'ticker'
        mov['saldo_ticker'] = mov.groupby('ticker')['saldo_ticker'].shift(1)

        # Passo 3: Preencher o saldo do primeiro dia de cada ticker com 0 (ou outro valor adequado)
        mov['saldo_ticker'] = mov['saldo_ticker'].fillna(0)

        # Passo 4: Somar saldo do dia anterior com saldo_credito_ativo e saldo_debito_ativo para obter o novo saldo_ticker
        mov['saldo_ticker'] = mov['saldo_ticker'] + mov['saldo_credito_ativo'] - mov['saldo_debito_ativo']


        mov['saldo_ticker'].fillna(method='ffill', inplace=True)


        


        print(mov)

        
        tickers = mov['ticker'].unique()
        data_mov = mov['data_movimentacao'].unique()
        multi_index = pd.MultiIndex.from_product([data_mov, tickers], names=['data_movimentacao', 'ticker'])

        mov.set_index(['data_movimentacao', 'ticker'], inplace=True)

        # Reindexa o DataFrame para incluir todos os níveis do MultiIndex
        mov = mov.reindex(multi_index)

        mov.sort_values(by='data_movimentacao', inplace=True)

        mov['saldo_debito_ativo'].fillna(method='ffill', inplace=True)

        

        print(mov)

        mov['valor_operacao'] = mov['valor_operacao'].astype(float).fillna(0)
        mov['preco_unitario'] = mov['preco_unitario'].astype(float).fillna(0)


        multi_index = pd.MultiIndex.from_product([pd.to_datetime(datas_uteis, format='%Y-%m-%dT%H:%M:%S'), tickers], names=['data_movimentacao', 'ticker'])


        df_concat = pd.DataFrame(index=multi_index)
        

        print(df_concat)


        mov = pd.concat([mov, df_concat], axis=1)

        mov.sort_index(ascending=True, inplace=True)

        


        start_quantidades = mov.groupby('ticker').head(1)
        mov['saldo_quantidade'] = start_quantidades['quantidade']



        



        mov['quantidade_cumsum'] = mov.groupby('ticker')['quantidade'].cumsum()

        mov['saldo_quantidade'] = mov['saldo_quantidade'].fillna(mov['quantidade_cumsum'])
        mov.drop(columns=['quantidade_cumsum'], inplace=True)
        

        print(mov)

        #mov['saldo_quantidade'] = mov['saldo_quantidade'] + mov['quantidade'].where(mov['tipo_operacao'] == 'Credito', 0)
        #mov['saldo_quantidade'] = mov['saldo_quantidade'] - mov['quantidade'].where(mov['tipo_operacao'] == 'Debito', 0)
        mov['saldo_quantidade'] = mov.groupby('ticker')['saldo_quantidade'].ffill()
        print(mov)


        # Eu preciso que o saldo quantidade mantenha um histórico contínuo
        #mov['saldo_quantidade'] = mov.groupby('ticker')['saldo_quantidade'].fillna(method='ffill')
        #mov['saldo_quantidade'] = mov['saldo_quantidade'] + mov['quantidade'].where(mov['tipo_operacao'] == 'Credito', 0)
        #mov['saldo_quantidade'] = mov['saldo_quantidade'] - mov['quantidade'].where(mov['tipo_operacao'] == 'Debito', 0)



        

        print(mov)
        mov['saldo_ticker'] = mov.groupby('ticker')['saldo_ticker'].ffill()

        # Calcula a soma dos saldos diários para cada dia (saldo_carteira)
        saldo_carteira = mov.groupby('data_movimentacao')['saldo_ticker'].sum()

        # Adiciona a coluna 'saldo_carteira' ao DataFrame principal
        mov = mov.join(saldo_carteira.rename('saldo_carteira'), on='data_movimentacao')
        mov['saldo_carteira'].fillna(method='ffill', inplace=True)
        print(mov)
    


        mov['saldo_carteira'].fillna(method='ffill', inplace=True)
        mov['credito'].fillna(0, inplace=True)
        mov['debito'].fillna(0, inplace=True)
        mov['quantidade'].fillna(0, inplace=True)
        mov['saldo_quantidade'].fillna(0, inplace=True)
        mov['saldo_ticker'].fillna(0, inplace=True)

 
        cotacoes = yf.download([ticker + '.SA' for ticker in tickers], start=data_inicio, end=data_fim)['Adj Close']

        # Add the 'ticker' index back to the 'cotacoes' DataFrame
        mov.reset_index('ticker', inplace=True)

        # Calculate the value for each stock (ticker) in each row
        for ticker in tickers:
            # Select rows where the ticker matches and calculate the value
            mask = mov['ticker'] == ticker
            mov.loc[mask, 'valor_acao'] = mov.loc[mask, 'saldo_quantidade'] * cotacoes[ticker + '.SA']

        mov.set_index('ticker')

        valor_carteira = mov[mov['valor_acao'].notnull()].groupby('data_movimentacao')['valor_acao'].sum()
        mov = mov.join(valor_carteira.rename('valor_carteira'), on='data_movimentacao')
        mov['valor_carteira'].fillna(method='ffill', inplace=True)

        mov['valor_carteira'].fillna(0, inplace=True)

        
        print(mov)


        return mov

    def evolucao_posicoes(self):
        '''Calcula a evolução das posições ajustado à mercado'''

        conn = self.db.connection()
        #mov_raw = pd.read_sql_query("SELECT * FROM movimentacoes", conn)
        mov_raw = self.historico_movimentacoes()


        # Criar dataframe vazio para armazenar os dados rastreados
        historico_rastreado = pd.DataFrame()

        for ticker in mov['ticker'].unique():
            # Filtra as movimentações apenas para o ticker atual
            mov_ativo = mov[mov['ticker'] == ticker].copy()

            mov_ativo_reindex['preco_unitario'].fillna(0, inplace=True)
            mov_ativo_reindex['quantidade'].fillna(0, inplace=True)
            mov_ativo_reindex['valor_mercado'].fillna(0, inplace=True)

            mov_ativo.set_index('data_movimentacao', inplace=True)
            mov_ativo_reindex = mov_ativo.reindex(datas_uteis)
            mov_ativo_reindex['ticker'] = ticker
            mov_ativo_reindex['tipo_ativo'] = mov_ativo['tipo_ativo'].iloc[0]
            mov_ativo_reindex['valor_mercado'] = mov_ativo_reindex['preco_unitario'] * mov_ativo_reindex['quantidade']
            historico_rastreado = pd.concat([historico_rastreado, mov_ativo_reindex])

        historico_rastreado.index.rename('data', inplace=True)

        print(historico_rastreado)




        mov['data_movimentacao'] = pd.to_datetime(mov['data_movimentacao'])
        mov['valor_operacao'] = mov['valor_operacao'].astype(float).fillna(0)
        mov.sort_values(by='data_movimentacao', inplace=True)

        # Calcula a evolução de saldo total da carteira
        mov['credito'] = mov.loc[mov['tipo_operacao'] == 'Credito', 'valor_operacao']
        mov['debito'] = mov.loc[mov['tipo_operacao'] == 'Debito', 'valor_operacao']

        mov['credito'].fillna(0, inplace=True)
        mov['debito'].fillna(0, inplace=True)

        mov['saldo_credito'] = mov['credito'].cumsum()
        mov['saldo_debito'] = mov['debito'].cumsum()

        mov['saldo_carteira'] = mov['saldo_credito'] - mov['saldo_debito']
        
        # Calcula a evolução de saldo total por ativo
        mov['credito'].fillna(0, inplace=True)
        mov['debito'].fillna(0, inplace=True)

        mov['saldo_credito_ativo'] = mov.groupby(['ticker', 'data_movimentacao'])['credito'].cumsum()
        mov['saldo_debito_ativo'] = mov.groupby(['ticker', 'data_movimentacao'])['debito'].cumsum()

        mov['saldo_ticker'] = mov['saldo_credito_ativo'] - mov['saldo_debito_ativo']

        mov['saldo_ticker'].fillna(method='ffill', inplace=True)
        
        saldo_acumulado_ticker = mov.groupby(['ticker'])['saldo_ticker'].cumsum()

        # Adicionar o saldo acumulado ao DataFrame
        mov['saldo_acumulado_ticker'] = saldo_acumulado_ticker

        # Remover as colunas saldo_credito e saldo_debito
        mov.drop(columns=['saldo_credito_ativo', 'saldo_debito_ativo', 'saldo_ticker'], inplace=True)


        print(mov)
        print(mov.tail())
        return mov
    
    def ler_proporcoes(self):
        proporcao_df = pd.DataFrame()
        mov_df = self.historico_movimentacoes()

        ultima_posicao_ticker_df = mov_df.groupby('ticker').last().reset_index()

        print(ultima_posicao_ticker_df)

        return proporcao_df




    def historico_valor_mercado(self): #Será agrupado com evolucao_posicoes!!!
        '''Gera uma tabela com o historico de evolução dos valores dos ativos ajustado a mercado'''
        movimentacoes = self.historico_movimentacoes()

        # Isola os ticker para consulta na API do Yahoo
        movimentacoes_grouped = movimentacoes.groupby('ticker')
        tickers = movimentacoes_grouped.groups.keys()

        data_inicio = movimentacoes['data_movimentacao'].min()
        data_fim = movimentacoes['data_movimentacao'].max()

        # Get the latest quotation for each ticker
        cotacoes = yf.download([ticker + '.SA' for ticker in tickers], start=data_inicio, end=data_fim)['Adj Close']

        # Create a new DataFrame to hold the final result
        historico = pd.DataFrame(columns=['data', 'ticker', 'tipo_ativo', 'total_carteira', 'total_ativo', 'valor_carteira', 'valor_ativo'])

        for ticker in tickers:
            # Filtrar as movimentações para o ticker atual
            movimentacoes_ticker = movimentacoes[movimentacoes['ticker'] == ticker]
            # Filtrar as cotações para o ticker atual
            cotacoes_ticker = cotacoes[ticker + '.SA']

        # Calcular os valores ajustados a mercado
        movimentacoes_ticker['preco_unitario'] = cotacoes_ticker.reindex(movimentacoes_ticker['data_movimentacao']).values
        movimentacoes_ticker['valor_ativo'] = movimentacoes_ticker['saldo_carteira'] * movimentacoes_ticker['preco_unitario']
        movimentacoes_ticker['valor_carteira'] = movimentacoes_ticker['saldo_carteira'] * movimentacoes_ticker['preco_unitario'].sum()

        # Adicionar os dados do ticker ao DataFrame do histórico
        historico = pd.concat([historico, movimentacoes_ticker], axis=0)

        # Realizar o agrupamento por mês
        historico.set_index('data_movimentacao', inplace=True)
        historico = historico.resample('M').sum()

        print(historico)

        return historico


    
    def consolidado_valor_mercado(self):
        '''Gera uma tablea com o consolidado por ticker e os valores atualizados'''
        movimentacoes = self.historico_movimentacoes()

        # Group 'movimentacoes' DataFrame by 'ticker'
        movimentacoes_grouped = movimentacoes.groupby('ticker')

        # Get the tickers and date range for data retrieval
        tickers = movimentacoes_grouped.groups.keys()

        data_inicio = movimentacoes['data_movimentacao'].min()
        data_fim = movimentacoes['data_movimentacao'].max()

        # Get the latest quotation for each ticker
        latest_quotations = yf.download([ticker + '.SA' for ticker in tickers], start=data_inicio, end=data_fim)['Adj Close']

        # Create a new DataFrame to hold the final result
        result_df = pd.DataFrame(columns=['data', 'ticker', 'tipo_ativo', 'total_carteira', 'total_ativo', 'valor_carteira', 'valor_ativo'])

        # Calculate the updated value for each ticker based on the latest quotation
        for ticker in tickers:
            ticker_sa = ticker + '.SA'
            latest_quotation = latest_quotations[ticker_sa].iloc[0] if ticker_sa in latest_quotations else None

            if latest_quotation is not None:
                ticker_rows = movimentacoes.loc[movimentacoes['ticker'] == ticker]
                latest_row = ticker_rows.loc[ticker_rows['data_movimentacao'].idxmax()]  # Get the row with the latest date for the ticker
                valor_atualizado_ativo = latest_quotation * latest_row['quantidade']
                result_df = result_df.append({
                    'ticker': ticker,
                    'tipo_ativo': latest_row['tipo_ativo'],
                    'total_carteira': latest_row['saldo_carteira'],
                    'total_ativo': latest_row['saldo_acumulado_ticker'],
                    'valor_ativo': valor_atualizado_ativo
                }, ignore_index=True)

        print(result_df)

        return result_df

    def ler_proventos(self):
        conn = self.db.connection()
        prov_raw = pd.read_sql_query("SELECT * FROM proventos", conn)
        prov = prov_raw.query("preco_unitario.notna()")

        prov['data_pagamento'] = pd.to_datetime(prov['data_pagamento'])
        prov['valor_total'] = prov['valor_total'].astype(float).fillna(0)
        prov.sort_values(by='data_pagamento', inplace=True)

        return prov