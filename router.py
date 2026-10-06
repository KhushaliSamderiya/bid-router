# net = bid price - shipping - insurance - delay_penalty
# Assumptions (all mock):
#   - shipping: flat rate by zone, per box
#   - insurance: 1.5% of declared value
#   - multi-box: split when value exceeds $2,500 per label
#   - delay penalty: $3 per transit day beyond 2

import math
from models import Item, Bid, RankedBid
from data import (BASE_SHIPPING, PER_ZONE_SHIPPING, INSURANCE_RATE,
                  BOX_VALUE_CAP, DELAY_FREE_DAYS, DELAY_PENALTY_PER_DAY)


def zone(seller_zip: str, maker_zip: str) -> int:
    """Mock distance zone: difference in the first zip digit (0-9)."""
    return abs(int(seller_zip[0]) - int(maker_zip[0]))


def cost_breakdown(item: Item, seller_zip: str, bid: Bid) -> dict:
    boxes = max(1, math.ceil(item.value / BOX_VALUE_CAP))
    per_box = BASE_SHIPPING + PER_ZONE_SHIPPING * zone(seller_zip, bid.maker_zip)
    shipping = per_box * boxes
    insurance = item.value * INSURANCE_RATE
    delay = max(0, bid.transit_days - DELAY_FREE_DAYS) * DELAY_PENALTY_PER_DAY
    return {"boxes": boxes, "shipping": shipping, "insurance": insurance, "delay": delay}


def rank_bids(item: Item, seller_zip: str, bids: list[Bid]) -> list[RankedBid]:
    if not bids:
        return []

    scored = []
    for bid in bids:
        c = cost_breakdown(item, seller_zip, bid)
        net = bid.price - c["shipping"] - c["insurance"] - c["delay"]
        scored.append((bid, c, net))

    # Deterministic: best net first, then faster transit, then maker_id.
    scored.sort(key=lambda t: (-t[2], t[0].transit_days, t[0].maker_id))

    top_headline = max(bids, key=lambda b: b.price).maker_id
    results = []
    for rank, (bid, c, net) in enumerate(scored):
        total_costs = bid.price - net
        if net <= 0:
            reason = "Negative net proceeds: do not route."
        elif rank == 0 and bid.maker_id != top_headline:
            reason = f"Lower headline bid than {top_headline}, but nets more after ${total_costs:.2f} in costs."
        elif rank > 0 and bid.maker_id == top_headline:
            reason = f"Highest headline bid, but ${total_costs:.2f} in costs drops it to #{rank + 1}."
        else:
            reason = f"Nets ${net:.2f} after ${total_costs:.2f} in costs."
        results.append(RankedBid(
            maker_id=bid.maker_id, price=bid.price,
            shipping=round(c["shipping"], 2), insurance=round(c["insurance"], 2),
            boxes=c["boxes"], net=round(net, 2), reason=reason,
        ))
    return results