from ofxparse import OfxParser
import difflib
import json
from models.organizze_models import TransactionCreateModel
from models.organizze_models import EnumOrganizzeAccounts
from decimal import Decimal

def determine_account_id(title: str) -> EnumOrganizzeAccounts:
    title_parsed = title.split()
    

    for i in title_parsed:
        enum_name = next((enum for enum in EnumOrganizzeAccounts if enum.name == i.upper()), None)
        if enum_name:
            return enum_name
        
    raise KeyError('Não foi possível determinar a conta bancária!')

def convert_ofx_to_json(file_path: str) -> json:
    with open(file_path, 'rb') as ofx_file:
        ofx = OfxParser.parse(ofx_file)
        transactions = []
        bank_name = ofx.signon.fi_org
        for transaction in ofx.account.statement.transactions:
            transaction_data = TransactionCreateModel(description=' '.join(transaction.memo.split()).lower(),
                                                      date=str(transaction.date),
                                                      amount_cents=convert_amount_to_cents(transaction.amount)
                                                    )
            transactions.append(transaction_data)
        
        
        return {"start_date": ofx.account.statement.start_date, 
                "end_date": ofx.account.statement.end_date, 
                "transactions": transactions,
                "bank_name": bank_name}
    
def convert_amount_to_cents(amount: int) -> int:
    try:
        if isinstance(amount, int):
            cents = amount * 100
        else:
            cents = int(amount * 100)
        return cents
    except TypeError:
        raise ValueError("O valor fornecido não é um número inteiro.")


def convert_brl_to_decimal(amount_brl: str):
    amount_brl = amount_brl.upper()

    if 'R$' in amount_brl:
        return Decimal(amount_brl.replace("R$", "").strip().replace(",", ".")) 
    return None

def convert_amount_to_decimal(amount: int) -> float:
    return float(amount) / 100


def match_strings(string1: str, string2: str, simillar: bool = False, threshold: int = 1) -> bool:
    ''' Essa função tem como objetivo analisar duas strings e determinar se elas são referente ao mesmo "assunto".
        No contexto atual, é analisado se duas transações são referente ao mesmo estabelecimento comercial'''

    ignored_words = [ "compra", "venda", "pagamento", "recebimento", "transferencia", "transferência", "deposito", "depósito",
    "saque", "debito", "débito", "credito", "crédito", "saldo", "conta", "cartao", "cartão", "boleto", "fatura",
    "juros", "encargos", "estabelecimento", "loja", "mercado", "supermercado", "farmacia", "farmácia", "posto",
    "combustivel", "combustível", "restaurante", "alimentacao", "alimentação", "educacao", "educação", "saude",
    "saúde", "servicos", "serviços", "tarifa", "seguro", "mensalidade", "internet", "telefone", "energia", "agua",
    "água", "gas", "gás", "aluguel", "moradia", "transporte", "taxa", "imposto", "tributo", "despesa", "receita",
    "valor", "parcela", "cheque", "cheque especial", "emprestimo", "empréstimo", "financiamento", "investimento",
    "rendimento", "saldos", "extrato", "comprovante", "anuidade", "tarifa bancaria", "tarifa bancária", "fatura cartao", 
    "banco", "s/a", "pix", "enviado", "cp", "-", "18236120", ":", "recebido", "inserido", "interno", "via", "api", "[api]", 
    "cuiaba", "bra", "brasil", "coxipo", "mei", "me", "eireli", "das", "osasco", "pagseguro", "cielo", "mercadopago", 
    "getnet", "izettle", "stone", "sumup", "rede", "dos", "das", "de", "shopping", "goiabeiras", "estacao", "pantanal", "sumuup", 
    "stonedev", "payleven", "smartpos", "point", "superget", "varzea", "grande", "deb", "mc"]

    ignored_set = set(ignored_words)

    # Separa as palavras das strings
    words1 = string1.lower().split()
    words2 = string2.lower().split()
    
    matching_words = []
    
    for word1 in words1:
        # Ignora as palavras vazias, palavras da lista de ignoradas, palavras que sejam apenas números e palavras menores que 2 chars
        if word1 not in ignored_set and len(word1) > 2:
            # Itera sobre as palavras da segunda string
            for word2 in words2:
                # Ignora as palavras vazias, palavras da lista de ignoradas, palavras que sejam apenas números e palavras menores que 2 chars
                if word2 and word2 not in ignored_set and len(word2) > 2:
                    # Se for pedido uma analise por similaridade
                    if simillar:
                        # Calcula a similaridade entre as palavras usando a razão de similaridade
                        similarity_ratio = difflib.SequenceMatcher(None, word1, word2).ratio()
                    
                        # Define um limite de similaridade mínimo para considerar as palavras como similares
                        similarity_threshold = 0.73
                    
                        # Se a similaridade entre as palavras for maior que o limite, adiciona a palavra à lista
                        if similarity_ratio > similarity_threshold:
                            matching_words.append(word1)
                    
                    if word1 == word2:
                        matching_words.append(word1)
                    
    if len(matching_words) >= threshold:
        return True
    
    return False
