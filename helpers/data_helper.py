from ofxparse import OfxParser
import difflib
import json
from models.generic_models import *

def convert_ofx_to_json(file_path: str) -> json:
    with open(file_path, 'rb') as ofx_file:
        ofx = OfxParser.parse(ofx_file)
        transactions = []
        bank_name = ofx.signon.fi_org
        for transaction in ofx.account.statement.transactions:
            transaction_data = OFXTransaction(date_posted=str(transaction.date),
                                              amount_cents=convert_amount_to_cents(transaction.amount),
                                              payee=transaction.payee,
                                              description=' '.join(transaction.memo.split()).lower())
            transactions.append(transaction_data)
        
        
        return {"start_date": ofx.account.statement.start_date, 
                "end_date": ofx.account.statement.end_date, 
                "transactions": transactions,
                "bank_name": bank_name}
    
def convert_amount_to_cents(amount: int) -> int:
    if isinstance(amount, int):
        cents = amount * 100
    else:
        cents = int(amount * 100)
    return cents

def get_matching_words(string1: str, string2: str) -> bool:

    ignored_words = [ "compra", "venda", "pagamento", "recebimento", "transferencia", "transferência", "deposito", "depósito",
    "saque", "debito", "débito", "credito", "crédito", "saldo", "conta", "cartao", "cartão", "boleto", "fatura",
    "juros", "encargos", "estabelecimento", "loja", "mercado", "supermercado", "farmacia", "farmácia", "posto",
    "combustivel", "combustível", "restaurante", "alimentacao", "alimentação", "educacao", "educação", "saude",
    "saúde", "servicos", "serviços", "tarifa", "seguro", "mensalidade", "internet", "telefone", "energia", "agua",
    "água", "gas", "gás", "aluguel", "moradia", "transporte", "taxa", "imposto", "tributo", "despesa", "receita",
    "valor", "parcela", "cheque", "cheque especial", "emprestimo", "empréstimo", "financiamento", "investimento",
    "rendimento", "saldos", "extrato", "comprovante", "anuidade", "tarifa bancaria", "tarifa bancária", "fatura cartao"]

    ignored_set = set(ignored_words)

    # Separa as palavras das strings
    words1 = string1.lower().split()
    words2 = string2.lower().split()
    
    matching_words = []
    
    for word1 in words1:
        # Ignora as palavras vazias e as palavras da lista de ignoradas
        if word1 not in ignored_set:
            # Itera sobre as palavras da segunda string
            for word2 in words2:
                # Ignora as palavras vazias e as palavras da lista de ignoradas
                if word2 and word2 not in ignored_set:
                    # Calcula a similaridade entre as palavras usando a razão de similaridade
                    similarity_ratio = difflib.SequenceMatcher(None, word1, word2).ratio()
                    
                    # Define um limite de similaridade mínimo para considerar as palavras como similares
                    similarity_threshold = 0.7
                    
                    # Se a similaridade entre as palavras for maior que o limite, adiciona a palavra à lista
                    if similarity_ratio > similarity_threshold:
                        matching_words.append(word1)
    
    # Retorna a lista das palavras similares
    return matching_words
