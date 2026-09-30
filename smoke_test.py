"""
Ad-hoc smoke tests for the Milestone 5 loop, run ahead of unit 4's formal
evaluation (that lives in scenarios.py / run_eval.py and is a later unit's
job). This script just sanity-checks, with real runs, that the loop and the
five acceptance criteria in criteria.md behave the way they're supposed to
before moving on.

Run with caching off so repeated model calls are real, not replayed:

    AI201_CACHE=0 python smoke_test.py
"""

import os

os.environ.setdefault("AI201_CACHE", "0")

import agent
from agent import run_agent
from tools import create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_listings

PASS = "PASS"
FAIL = "FAIL"

results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


# ── Criterion 1 + 3 + 5: a matching query, in one pass per try ───────────────
# Spy on suggest_outfit so we can compare what the session says was selected
# against what the tool actually received (criterion 3).

_real_suggest_outfit = agent.suggest_outfit
_captured_id = {}


def _spy_suggest_outfit(new_item, wardrobe):
    _captured_id["id"] = new_item["id"]
    return _real_suggest_outfit(new_item, wardrobe)


agent.suggest_outfit = _spy_suggest_outfit

MATCHING_TRIES = [
    ("vintage graphic tee under $30", 30.0),
    ("90s track jacket in size M", None),
    ("graphic tee under $25", 25.0),
    ("vintage flannel under $30", 30.0),
    ("graphic hoodie under $30", 30.0),
]

completed = 0
state_ok = 0
price_ok = 0

for query, max_price in MATCHING_TRIES:
    _captured_id.clear()
    session = run_agent(query, get_example_wardrobe())

    if session["error"] is None and session["fit_card"]:
        completed += 1

    if session["selected_item"] and _captured_id.get("id") == session["selected_item"]["id"]:
        state_ok += 1

    if max_price is None or (
        session["selected_item"] and session["selected_item"]["price"] <= max_price
    ):
        price_ok += 1

agent.suggest_outfit = _real_suggest_outfit

check(
    "criterion 1 — matching query completes (>= 4/5)",
    completed >= 4,
    f"{completed}/5 completed all three tools",
)
check(
    "criterion 3 — state: selected_item id matches what suggest_outfit received (5/5)",
    state_ok == 5,
    f"{state_ok}/5 matched",
)
check(
    "criterion 5 — selected_item price <= max_price (5/5)",
    price_ok == 5,
    f"{price_ok}/5 within ceiling",
)


# ── Criterion 2: an impossible query stops before suggest_outfit ─────────────

stopped_early = 0
for _ in range(5):
    session = run_agent("designer ballgown size XXS under $5", get_example_wardrobe())
    error = session["error"] or ""
    names_something_to_change = error.strip() != "" and error.strip().lower() != "no results"
    if names_something_to_change and session["fit_card"] is None:
        stopped_early += 1

check(
    "criterion 2 — impossible query stops before suggest_outfit (5/5)",
    stopped_early == 5,
    f"{stopped_early}/5 stopped with fit_card still None",
)


# ── Criterion 4: fit card mentions price/platform, opens differ ─────────────

item = load_listings()[0]
outfit = "Pair with a white tank top and chunky sneakers for an effortless look."
cards = [create_fit_card(outfit, item) for _ in range(5)]


def _mentions_price_and_platform(caption: str) -> bool:
    price_mentioned = (
        f"{item['price']:.2f}" in caption or str(int(item["price"])) in caption
    )
    platform_mentioned = item["platform"].lower() in caption.lower()
    return price_mentioned and platform_mentioned


mentions_ok = sum(1 for c in cards if _mentions_price_and_platform(c))
opens = [c.split(".")[0].strip() for c in cards]
identical_pairs = sum(
    1
    for i in range(len(opens))
    for j in range(i + 1, len(opens))
    if opens[i] == opens[j]
)

check(
    "criterion 4a — price and platform mentioned (5/5)",
    mentions_ok == 5,
    f"{mentions_ok}/5 mentioned both",
)
check(
    "criterion 4b — at most 1 of 10 opening-sentence pairs identical",
    identical_pairs <= 1,
    f"{identical_pairs}/10 pairs identical",
)


# ── Diagnostic: empty wardrobe still returns real advice ─────────────────────

session = run_agent("vintage graphic tee under $30", get_empty_wardrobe())
check(
    "diagnostic — empty wardrobe still returns non-empty outfit advice",
    bool(session["outfit_suggestion"] and session["outfit_suggestion"].strip()),
)


# ── Summary ───────────────────────────────────────────────────────────────────

print()
passed = sum(1 for _, status, _ in results if status == PASS)
print(f"{passed}/{len(results)} checks passed")
