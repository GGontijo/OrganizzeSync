from pydantic import BaseModel

class OFXTransaction(BaseModel):
    date_posted: str
    amount: int
    payee: str
    memo: str
