from ofxparse import OfxParser
from models.generic_models import *

def convert_ofx_to_json(file_path):
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
    
def convert_amount_to_cents(amount):
    if isinstance(amount, int):
        cents = amount * 100
    else:
        cents = int(amount * 100)
    return cents

convert_ofx_to_json('teste.ofx')