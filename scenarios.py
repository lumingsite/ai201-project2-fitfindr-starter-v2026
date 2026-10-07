"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Any normal completed run — criterion 3 checks that the id of
        # selected_item matches what actually reached suggest_outfit.
        "name": "state: selected item matches what's passed on",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 needs 5 fit cards for 5 DIFFERENT items, not the same
        # item 5 times — these are 5 separate scenarios, each matching a
        # distinct top listing (verified with tools.search_listings first).
        "name": "fit card: item 1 (tee)",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card: item 2 (track jacket)",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card: item 3 (slip dress)",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card: item 4 (sneakers)",
        "query": "platform sneakers size 8",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card: item 5 (denim jacket)",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5: an explicit max_price, checked against selected_item's
        # price. Deterministic — doesn't touch the model — so 5/5 is fair.
        "name": "price ceiling respected",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
