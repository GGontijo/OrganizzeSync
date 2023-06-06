from typing import Optional, List
from pydantic import BaseModel


class GoalModel(BaseModel): # Meta do Organizze
    amoount_in_cents: int
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


class CategoryModel(BaseModel):
    id: int
    name: str
    color: str
    parent_id: int = None
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
