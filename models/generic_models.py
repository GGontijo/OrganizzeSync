from pydantic import BaseModel

class OFXTransaction(BaseModel):
    date_posted: str
    amount_cents: int
    payee: str
    description: str
