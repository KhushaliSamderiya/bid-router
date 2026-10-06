from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict

from models import Item, Bid, RankedBid
from router import rank_bids
from data import HERO_ITEM, HERO_SELLER_ZIP, HERO_BIDS

app = FastAPI(
    title="Net-Proceeds Bid Router",
    description="Ranks partner bids by what the seller actually nets after "
                "shipping, insurance, and delay. Mock data and rates.",
)


class RouteRequest(BaseModel):
    item: Item
    seller_zip: str = Field(pattern=r"^\d{5}$")
    bids: list[Bid]

    # Pre-fills the example in /docs with the hero scenario
    model_config = ConfigDict(json_schema_extra={
        "example": {"item": HERO_ITEM, "seller_zip": HERO_SELLER_ZIP, "bids": HERO_BIDS}
    })


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/route", response_model=list[RankedBid])
def route(req: RouteRequest):
    return rank_bids(req.item, req.seller_zip, req.bids)