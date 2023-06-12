from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class BudgetModel(BaseModel): # Meta do Organizze
    amount_in_cents: int
    category_id: int
    category_name: Optional[str]
    date: str
    activity_type: int
    total: int
    predicted_total: int
    percentage: str

class AccountModel(BaseModel):
    id: int
    name: str
    institution_id: str
    institution_name: Optional[str]
    description: Optional[str]
    archived: bool
    created_at: str
    updated_at: str
    default: bool
    type: str

class BalanceDateModel(BaseModel): # Saldo por data
    date: str
    date_range: str
    outcomes: int
    predicted_outcomes: int
    incomes: int
    predicted_incomes: int
    expenses: int
    predicted_expenses: int
    earnings: int
    predicted_earnings: int
    initial_amounts: int
    predicted_initial_amounts: int
    transferences: int
    predicted_transferences: int
    credit_card_invoices_to_pay: int
    balance: int
    predicted_balance: int
    previous_balance: int
    previous_predicted_balance: int
    accumulated_outcomes: int
    accumulated_predicted_outcomes: int
    accumulated_incomes: int
    accumulated_predicted_incomes: int
    accumulated_expenses: int
    accumulated_predicted_expenses: int
    accumulated_earnings: int
    accumulated_predicted_earnings: int
    accumulated_initial_amounts: int
    accumulated_predicted_initial_amounts: int

class BalanceModel(BaseModel):
    previous_balance: int
    previous_predicted_balance: int
    balance: int
    predicted_balance: int
    outcomes: int
    predicted_outcomes: int
    incomes: int
    predicted_incomes: int
    expenses: int
    predicted_expenses: int
    earnings: int
    predicted_earnings: int
    initial_amounts: int
    predicted_initial_amounts: int
    result: int
    predicted_result: int
    balances: List[BalanceDateModel]

class CategoryModel(BaseModel):
    id: int
    name: str
    color: str
    parent_id: Optional[int]
    group_id: str
    fixed: bool
    essential: bool
    default: bool
    uuid: str
    kind: str
    archived: bool

class TransactionModel(BaseModel):
    id: int
    description: str
    date: str
    paid: bool
    amount_cents: int
    total_installments: int
    installment: int
    recurring: bool
    account_id: int
    category_id: int
    notes: Optional[str]
    attachments_count: int
    credit_card_id: Optional[int]
    credit_card_invoice_id: Optional[int]
    paid_credit_card_id: Optional[int]
    paid_credit_card_invoice_id: Optional[int]
    oposite_transaction_id: Optional[int]
    oposite_account_id: Optional[int]
    created_at: str
    updated_at: str
    tags: List[dict] = []
    attachments: List[dict] = []
    recurrence_id: Optional[int]

class TransactionCreateModel(BaseModel):
    description: str
    date: str
    amount_cents: int
    category_name: Optional[str]
    account_id: int
    category_id: int
    notes: Optional[str]
    tags: List[dict] = []

    def to_dict(self, **kwargs): #Tem que passar serializada em json/dict pra api do organizze...
        return super().dict(**kwargs)
    
class EnumOrganizzeAccounts(Enum):
    INTER = 4375871
    INTER_EDELIN = 6585539
    SANTANDER = 4375850
    SANTANDER_EDELIN = 6066704
    NUBANK_EDELIN = 5156963
    
