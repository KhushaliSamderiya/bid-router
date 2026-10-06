import pytest
from pydantic import ValidationError

from models import Item, Bid
from router import rank_bids, cost_breakdown
from data import HERO_ITEM, HERO_SELLER_ZIP, HERO_BIDS

SELLER = HERO_SELLER_ZIP  # "60601"


def hero_bids():
    return [Bid(**b) for b in HERO_BIDS]


# --- Hero example ---------------------------------------------------------

def test_hero_ranking_order():
    ranked = rank_bids(Item(**HERO_ITEM), SELLER, hero_bids())
    assert [r.maker_id for r in ranked] == ["B_chicago", "C_dallas", "A_los_angeles"]


def test_hero_net_numbers():
    ranked = rank_bids(Item(**HERO_ITEM), SELLER, hero_bids())
    nets = {r.maker_id: r.net for r in ranked}
    assert nets["B_chicago"] == pytest.approx(957.0)
    assert nets["C_dallas"] == pytest.approx(952.0)
    assert nets["A_los_angeles"] == pytest.approx(932.0)


def test_top_headline_bid_loses_on_net():
    bids = hero_bids()
    top_headline = max(bids, key=lambda b: b.price).maker_id
    ranked = rank_bids(Item(**HERO_ITEM), SELLER, bids)
    assert ranked[0].maker_id != top_headline
    assert "drops it to #3" in ranked[-1].reason


# --- Multi-box rule -------------------------------------------------------

@pytest.mark.parametrize("value, expected_boxes", [
    (1000, 1),
    (2500, 1),       # exactly at the cap: still one box
    (2500.01, 2),    # just over: splits
    (6000, 3),
])
def test_multi_box_threshold(value, expected_boxes):
    bid = Bid(maker_id="x", price=100, maker_zip="60614", transit_days=1)
    item = Item(value=value, weight_oz=4)
    assert cost_breakdown(item, SELLER, bid)["boxes"] == expected_boxes


def test_multi_box_scales_shipping_and_insurance():
    bid = Bid(maker_id="x", price=7000, maker_zip="60614", transit_days=1)
    c = cost_breakdown(Item(value=6000, weight_oz=4), SELLER, bid)
    assert c["boxes"] == 3
    assert c["shipping"] == pytest.approx(24.0)    # 3 boxes x $8, zone 0
    assert c["insurance"] == pytest.approx(90.0)   # 1.5% of $6,000


# --- Tie-breaking and determinism ----------------------------------------

def test_tie_breaks_on_transit_days():
    # Same price, same zone, both within free delay days -> identical net.
    slow = Bid(maker_id="a", price=500, maker_zip="60614", transit_days=2)
    fast = Bid(maker_id="b", price=500, maker_zip="60614", transit_days=1)
    ranked = rank_bids(Item(**HERO_ITEM), SELLER, [slow, fast])
    assert ranked[0].net == ranked[1].net
    assert ranked[0].maker_id == "b"   # faster wins even though id sorts later


def test_tie_breaks_on_maker_id_last():
    b1 = Bid(maker_id="zeta", price=500, maker_zip="60614", transit_days=1)
    b2 = Bid(maker_id="alpha", price=500, maker_zip="60614", transit_days=1)
    ranked = rank_bids(Item(**HERO_ITEM), SELLER, [b1, b2])
    assert [r.maker_id for r in ranked] == ["alpha", "zeta"]


def test_same_result_regardless_of_input_order():
    forward = rank_bids(Item(**HERO_ITEM), SELLER, hero_bids())
    backward = rank_bids(Item(**HERO_ITEM), SELLER, list(reversed(hero_bids())))
    assert forward == backward


# --- Edge cases -----------------------------------------------------------

def test_empty_bid_list_returns_empty():
    assert rank_bids(Item(**HERO_ITEM), SELLER, []) == []


def test_negative_net_is_flagged_and_ranked_last():
    bad = Bid(maker_id="bad", price=10, maker_zip="60614", transit_days=1)
    good = Bid(maker_id="good", price=900, maker_zip="60614", transit_days=1)
    ranked = rank_bids(Item(**HERO_ITEM), SELLER, [bad, good])
    assert ranked[0].maker_id == "good"
    assert ranked[-1].net < 0
    assert ranked[-1].reason.startswith("Negative net proceeds")


def test_invalid_zip_rejected():
    with pytest.raises(ValidationError):
        Bid(maker_id="x", price=100, maker_zip="1234", transit_days=1)