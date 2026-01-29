from pydantic import BaseModel

class Transaction(BaseModel):
    amount: float
    nameOrig: str
    nameDest: str
