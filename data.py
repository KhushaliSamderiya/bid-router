# All mock numbers. Not real carrier rates.
BASE_SHIPPING = 8.0        # flat cost per box
PER_ZONE_SHIPPING = 12.0   # added per zone of distance
INSURANCE_RATE = 0.015     # 1.5% of declared value
BOX_VALUE_CAP = 2500.0     # max insured value per label
DELAY_FREE_DAYS = 2
DELAY_PENALTY_PER_DAY = 3.0

# Hero example: seller in Chicago selling a $1,000 item.
# Headline order: A > C > B. Net order: B > C > A.
HERO_SELLER_ZIP = "60601"
HERO_ITEM = {"value": 1000, "weight_oz": 4}
HERO_BIDS = [
    {"maker_id": "A_los_angeles", "price": 1000, "maker_zip": "90210", "transit_days": 5},
    {"maker_id": "B_chicago",     "price": 980,  "maker_zip": "60614", "transit_days": 1},
    {"maker_id": "C_dallas",      "price": 990,  "maker_zip": "75201", "transit_days": 3},
]