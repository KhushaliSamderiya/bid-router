from pydantic import BaseModel, Field

class Item(BaseModel):
    value: float = Field(gt=0)          # declared value in USD
    weight_oz: float = Field(gt=0)

class Bid(BaseModel):
    maker_id: str
    price: float = Field(gt=0)          # headline bid in USD
    maker_zip: str = Field(pattern=r"^\d{5}$")
    transit_days: int = Field(ge=1)

class RankedBid(BaseModel):
    maker_id: str
    price: float
    shipping: float
    insurance: float
    boxes: int
    net: float                          # what the seller actually keeps
    reason: str                         # one-line explanation of the rank