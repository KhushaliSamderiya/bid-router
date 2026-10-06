# Tradepost: 3 Ideas for What We Could Build Next

## 0. Quick Prototype

**Net-Proceeds Bid Router** (link to repo / demo): given an item, a seller location, and a set of partner bids, it ranks bids by what the seller actually nets, not by headline price.

Net proceeds = bid price − shipping cost − insurance − expected cost of delay or risk

Why this: your FAQ says Instant Cash Offers come from partner bids, and the role mentions more cost-effective order routing across thousands of parcels a month. A higher bid from a far-away market maker can lose to a slightly lower local one once shipping and insurance are counted. The prototype uses mock data and mock rate tables. It is a thinking tool, not a claim about your real system.

---

## Idea 1: Take the router further: routing as a real optimizer

**Problem.** The best bid and the best outcome aren't always the same. Shipping cost, transit time, per-label insurance limits, and the chance a deal gets disputed all change what a bid is really worth.

**What I'd build next.**
- Plug in real carrier rate quotes instead of mock tables
- Handle the multi-box case for high-value shipments (the FAQ notes insurance caps force splitting)
- Add a score for each market maker: dispute rate, time to confirm, how often they bid at all
- Backtest against historical orders to show the dollar difference vs. picking the top bid

**Success looks like:** a measurable lift in seller net proceeds per order, plus lower shipping cost per parcel.

---

## Idea 2: Settlement you can trust: a ledger and state machine with tests

**Problem.** The FAQ shows how many separate states an order can be in: order, transfer, payout, and shipment each have their own status, plus disputes, holds, and failed withdrawals. Users also get confused about pending vs. available balance. At $100M/month, a small bug in how money moves is expensive.

**What I'd build next.**
- A double-entry ledger where every balance is derived from entries, never edited directly
- An explicit order/payout state machine, with illegal transitions made impossible
- Idempotent webhook handling for payment-provider callbacks (retries and out-of-order events must not double-pay)
- Property-based tests that replay random event sequences and assert that money is conserved

**Success looks like:** pending and available balances that are always explainable, and a safe path to add new payment rails (including crypto) without touching the core logic.

---

## Idea 3: Make the Exchange API easy to build against

**Problem.** The Terminal serves professional market makers. They value speed, clarity, and being able to automate. The easier it is to integrate, the more liquidity shows up.

**What I'd build next.**
- A sandbox environment with fake assets and a simulated order flow
- A clean OpenAPI spec plus a streaming bid/ask feed
- A small reference market-maker bot (open-sourced) that shows how to quote, fill, and handle rejections
- Rate-limit and error-code docs written for people who trade for a living

**Success looks like:** a new market maker going from "interested" to quoting in a day instead of a week.

---

## Which one first?

If I could only pick one for the first 90 days: **Idea 2**. Getting settlement airtight is what lets everything else scale safely. Idea 1 is the fastest visible win, and Idea 3 compounds once liquidity is the bottleneck.

Happy to walk through any of these live, or hear where I'm wrong about how things work today.
