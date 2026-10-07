# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is a command-line agent for a thrift/resale shopping assistant. A
user types a plain-language request (e.g. `"vintage graphic tee under $30"`)
and the agent searches a mock listings dataset, picks the best match, and
asks the model for outfit ideas that combine the find with the user's saved
wardrobe. It then turns that into a short, shareable caption for the item.
If nothing in the data matches the request, the agent stops and tells the
user what to change instead of pretending to find something.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters the 40 listings in `data/listings.json` by size and price ceiling, then ranks the survivors by keyword overlap with the description.
- **Inputs:**
  - `description` (str) — free-text keywords, e.g. `"vintage graphic tee"`
  - `size` (str | None) — a size token to filter by, case-insensitive, whole-token match against the listing's `size` field (split on whitespace) rather than substring — so `"M"` matches `"S/M"` but `"S"` does not match `"US 9"`, and `"L"` does not match `"XL"`
  - `max_price` (float | None) — inclusive price ceiling
- **Returns:** A list of listing dicts, best match first, each with `id, title, description, category, style_tags, size, condition, price, colors, brand, platform` — capped at `config.SEARCH_RESULT_LIMIT` (10) results.
- **When it has nothing:** Returns `[]` (empty list) — never `None`, never raises. This is the value the loop's branch checks.

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfits pairing a candidate listing with the user's existing wardrobe.
- **Inputs:**
  - `new_item` (dict) — a listing dict, as returned by `search_listings`
  - `wardrobe` (dict) — `{"items": [...]}`; `items` may be `[]`
- **Returns:** A non-empty string of outfit suggestions. If `wardrobe["items"]` is empty, returns general styling advice for the item instead of naming pieces the user doesn't have.
- **When it has nothing:** There is no "nothing" return here — an empty wardrobe still produces a non-empty string (general advice, not `""` and not an exception).

### `create_fit_card`

- **What it does:** Calls the model to write a 2–4 sentence social-post-style caption for the item, using the outfit suggestion as context.
- **Inputs:**
  - `outfit` (str) — the string returned by `suggest_outfit`
  - `new_item` (dict) — the listing dict for the item
- **Returns:** A 2–4 sentence caption string that mentions the item, its price, and its platform once each.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a descriptive message string (not `""`, not an exception) instead of calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` telling the user what to change (e.g. loosen the price or size) and stop — do not call `suggest_outfit`. Otherwise, take the first result as `session["selected_item"]` and continue to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex over the raw query string (`agent.py::_parse_query`) — `\bsize\s+([A-Za-z0-9/.]+)` pulls the token after the word "size" (e.g. "size M", "size 8"), `under\s*\$\s*(\d+(?:\.\d{1,2})?)` or `\$\s*(\d+(?:\.\d{1,2})?)\s*or less` pulls the price ceiling, and whatever text remains (with those matched spans blanked out, plus a few filler words like "in"/"the" dropped) becomes `description`.

**What moves through the session:** `query` → `parsed` (description/size/max_price) → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`, with `error` set and the run stopped short the moment any step can't produce a usable next input.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair the Y2K baby tee with your baggy straight-leg jeans and chunky
  white sneakers for an effortless throwback streetwear look, finishing it off
  with the black crossbody bag. To lean into a slightly edgy vintage aesthetic,
  layer the cropped zip hoodie over the baby tee, and pair them with your baggy
  straight-leg jeans and black combat boots.

  Fit card: Found my new entire personality for $18 on depop! 🦋 This Y2K
  butterfly baby tee gives the absolute best nostalgic streetwear energy.
  Can't wait to live in this cropped little top all summer long.

2 model calls this session, 498 prompt + 113 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', ... 'price': 18.0, ...},
 {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', ... 'price': 24.0, ...},
 {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', ... 'price': 15.0, ...},
 {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', ... 'price': 19.0, ...},
 ... 8 results total, all ≤ $30]

$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

```
$ python -c "
from tools import suggest_outfit
from utils.data_loader import get_example_wardrobe, load_listings
print(suggest_outfit(load_listings()[0], get_example_wardrobe()))
"
**Outfit 1:** Pair the vintage Levi's 501 jeans with the white ribbed tank top and chunky white sneakers for a classic, effortless 90s streetwear look. Add the black crossbody bag to complete the everyday casual vibe.

**Outfit 2:** Layer the oversized grey crewneck sweatshirt over the jeans, and ground the fit with the black combat boots. Accessorize with the brown leather belt for a subtle touch of contrast and structure.
```

```
$ python -c "
from tools import create_fit_card
from utils.data_loader import load_listings
item = load_listings()[0]
print(create_fit_card('Pair with a white tank top and chunky sneakers for an effortless look.', item))
"
Finally scored the holy grail of denim on Depop and I am never taking these off. These vintage Levi's 501s have the absolute best lived-in fade at the knees for only $38.00. Styling them with a basic white tank and chunky sneakers gives off the ultimate effortless 90s off-duty vibe.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Tested `create_fit_card` by running it three times on
  the same item and reading the output myself, as the milestone asks.
- *What came back:* All three runs came back word-for-word identical.
- *What I changed:* Instead of assuming the tool was broken, I checked
  `config.py` — `TEMPERATURE` is 0.9, not 0, so the repeat wasn't that. It was
  `CACHE_ENABLED` handing back an already-cached answer for the identical
  prompt. I reran the same test with `AI201_CACHE=0` and got three genuinely
  different captions, which is what confirmed the tool itself works and the
  first result was a caching artifact, not a bug.

**Moment 2**

- *What I asked for:* Asked Claude to attack my draft acceptance criteria —
  "tell me exactly how you'd test this using only what the sentence says,
  don't suggest improvements."
- *What came back:* For criterion 3 (state), my draft reason was "must be 5
  of 5, otherwise the wrong item would reach the next tool." Claude pointed
  out that was circular — it restated the criterion instead of explaining why
  5 of 5 is a reasonable target rather than a stricter or looser one.
- *What I changed:* I rewrote the reasoning to point at *why* the target is
  achievable: passing the selected item through `session["selected_item"]` is
  a deterministic assignment, not a model call, so there's no legitimate
  source of variance — any mismatch could only be a bug, which is why it's
  held to 5 of 5 rather than something looser like criterion 1.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools, returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id matches the id passed to `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price + platform (Try N = item N, not a repeat) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. `selected_item` price ≤ query's `max_price` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Scenarios run via `scenarios.py` / `run_eval.py`, 5 tries each, cache off.
Full output: `results/run_2026-10-07_1931_before.md` (84 model calls, 17983
prompt + 5632 output tokens).

**Real output from one try each**, naming the file and function that produced
it — all from `agent.py::run_agent`, which calls `tools.py::search_listings`
(via MCP), `tools.py::suggest_outfit`, and `tools.py::create_fit_card`:

**Criterion 1** — "matching query completes", try 1, query `vintage graphic tee under $30`:
```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Fit card:
Found the ultimate early 2000s throwback on depop for just $18.00! This
butterfly print baby tee has the absolute best nostalgic streetwear vibe.
Already planning to wear it with baggy denim and chunky sneakers for that
effortless 90s-meets-00s fit. 🦋✨
```

**Criterion 2** — "impossible query stops early", try 1, query `designer ballgown size XXS under $5`:
```
- stopped early: yes — No listings matched your search. Try raising the
  price ceiling or trying a different size.
- selected_item: (none)
- search_results: 0
```

**Criterion 3** — verified directly, not just read off the log, because the
report only prints a title and the criterion is about an `id`. I patched
`agent.suggest_outfit` with a spy that records the `id` of the dict it's
called with, ran `run_agent("90s track jacket in size M", ...)`, and compared:

```
selected_item id: lst_004
id passed to suggest_outfit: lst_004
match: True
```

This also explains why this criterion can be 5 of 5 rather than something
looser: `agent.py` (`run_agent`, around the `suggest_outfit` call) passes
`session["selected_item"]` straight through — the exact same dict that came
out of `search_results[0]` — with no intermediate copy or re-lookup by id.
There's no code path by which the two ids could diverge; a mismatch would be
a bug, not acceptable variance, which is what a mismatch would mean.

**Criterion 4** — one fit card per item (5 different items, not the same item
5 times):

| Item | Price | Platform | Fit card mentions both? |
|---|---|---|---|
| Y2K Baby Tee | $18.00 | depop | yes |
| 90s Track Jacket | $45 | Poshmark | yes |
| 90s Silk Slip Dress | "thirty bucks" | Depop | yes (price in words, not digits) |
| Platform Sneakers | $48 | Poshmark | yes |
| Denim Jacket | $42 | Poshmark | yes |

Opening sentences (first sentence of each card), checked across all 10 pairs
for exact duplicates — none matched word-for-word, so 10/10 distinct against
a 9/10 target:
```
"Found the ultimate early 2000s throwback on depop for just $18.00!"
"Finally scored this vintage navy and white track jacket on Poshmark for
 just $45, and I am obsessed with the sporty 90s athletic vibe."
"Finally scored this dreamy 90s floral silk slip dress on Depop for just
 thirty bucks and I am obsessed."
"Found my ultimate Y2K streetwear grail on Poshmark for $48 and I am never
 taking them off."
"Scored this cropped light-wash jacket on Poshmark for just $42 and the
 structured shoulders are literally everything."
```

**Criterion 5** — "price ceiling respected", query `silk slip dress in midi
length under $40` (parsed `max_price=40.0`), all 5 tries selected the same
$30.00 item — $30 ≤ $40 holds regardless of what happens afterward. Try 1 is
worth calling out: the model itself returned a transient `503 UNAVAILABLE`
("high demand") on that attempt, caught by the new `ModelUnavailable` handler
in `agent.py::run_agent` and surfaced as `session["error"]` rather than a
crash — but `selected_item` was already chosen by `search_listings` before
that call, so the criterion (which is about the price filter, not about the
model) still passes on that try:
```
- stopped early: yes — The model could not be reached, so no outfit or fit
  card could be generated: Couldn't reach the model: 503 UNAVAILABLE. ...
- selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
- search_results: 7
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools, returns a fit card | 4 of 5 | MET (5/5) | All 5 tries of `python app.py ask 'vintage graphic tee under $30'` reached `create_fit_card` and returned a non-empty string (245–304 chars). Counted passes straight off `results/run_2026-10-07_1931_before.md`. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET (5/5) | All 5 tries of `designer ballgown size XXS under $5` had `search_results: 0`, a non-empty `session["error"]` naming what to change, and no `outfit_suggestion`. |
| 3 | `selected_item` id matches the id passed to `suggest_outfit` | 5 of 5 | MET (5/5) | The printed log only shows a title, which isn't the id the criterion names, so I didn't call this from the log. I patched `agent.suggest_outfit` with a spy, ran `run_agent`, and compared `session["selected_item"]["id"]` to the id the spy actually received: `lst_004` both times. |
| 4 | Fit card mentions price + platform (5 of 5); ≤1 of 10 opening-sentence pairs identical | 5 of 5, 9 of 10 | MET (5/5, 10/10) | Read all 5 cards (5 different items) by hand — every one names a dollar amount and a platform. Compared all 10 pairs of opening sentences for exact string matches; none matched, so 10/10 distinct, which clears the 9/10 bar with room to spare. |
| 5 | `selected_item` price ≤ query's `max_price` | 5 of 5 | MET (5/5) | Query `silk slip dress in midi length under $40` parses to `max_price=40.0`; all 5 tries selected the $30.00 item, so $30 ≤ $40 held even on the try where the model itself returned a 503 afterward. |

**Diagnoses**

No misses this run — all five criteria held at or above target across all 5 tries. Two things worth flagging honestly rather than just taking the clean sheet at face value:

- **Criterion 1's test doesn't exercise what its "why" paragraph worries about.** `criteria.md` justifies the 4-of-5 target by saying "some phrasings will miss" — but `scenarios.py` runs the *exact same query string* five times, so `search_listings` (a pure function of its inputs) gets identical input on every try and can only ever be all-pass or all-fail, never a mix. The 5/5 I got says the model calls behaved, not that the search tool tolerates varied phrasing. If I ran this again I'd use five *different* phrasings for the same target item (e.g. "80s/90s style t-shirt", "vintage printed tee", "retro graphic shirt") rather than repeating one string — that's a test-design fix, not a target change, since nothing here was unmeasurable, it was just measuring the wrong kind of variation.
- **One transient model failure showed up (criterion 5, try 1 — a `503 UNAVAILABLE` from the service, not a bad key or a bug).** It didn't cost a point only because `selected_item` is chosen by `search_listings` *before* the model is ever called in `run_agent` — the failure landed downstream of what criterion 5 actually checks. That's the one place in this run where the "four places to fail" (tool / branch / session / model output) mattered: this was a model-output failure, caught cleanly by the Milestone 2 handler, and it happened to be irrelevant to the specific criterion it landed on. A criterion about the *outfit* or *fit card* text on that same try, if I'd had one keyed to this exact scenario, would have had a real FAIL to log instead.

If I had to tighten one target given what I actually saw: criterion 3, at 5 of 5, is already as strict as it can be and is correctly justified (a deterministic assignment with no legitimate source of variance). Criterion 1's 4-of-5 is the one I'd leave *as a number* but fix in test design per above, rather than tighten or loosen it on the strength of a single clean run against an unrepresentative test.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Pair the Y2K baby tee with your baggy straight-leg jeans and chunky white sneakers for an effortless throwback…
[4] create_fit_card
      in:  dict with keys: outfit
      out: Found my new entire personality for $18 on depop! 🦋 This Y2K butterfly baby tee gives the absolute best nostal…
```

**Empty search**

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch: empty_search
      →    stopping before suggest_outfit
```

**On the MCP move:** `search_listings` is now registered on `mcp_server.py` and
`run_agent()` calls it through `mcp_client.call_tool("search_listings", {...})`
instead of importing the function directly. The returned value is unchanged —
same list of listing dicts, same ranking — which is why the happy-path output
above matches what the direct call produced before. The only visible change is
in the trace step name, labeled `search_listings (via MCP)` so the MCP hop is
identifiable in the log.



### Failure Modes Triggered

**Empty search** — `python app.py ask 'designer ballgown size XXS under $5'`
```
No listings matched your search. Try raising the price ceiling or trying a different size.
```
Already handled before this unit — the branch in `run_agent()` stops before `suggest_outfit` and names what to change.

**Empty wardrobe** — `python app.py ask 'retro windbreaker size L' --empty-wardrobe`
```
Outfit:   Pair this bold 90s windbreaker with relaxed-fit, light-wash denim or black
joggers to keep the focus on the vibrant color blocking. Layer it over a simple
white or grey graphic tee, and finish the look with classic retro sneakers like
white chunky trainers or Nike Dunks.
```
Already handled — `suggest_outfit` checks `wardrobe['items']` and switches to a general-advice prompt when it's empty. General styling advice, not a crash, not `""`.

**Model unavailable** — one character of `GEMINI_API_KEY` in `.env` changed, then `python app.py ask 'oversized denim shirt size M' --trace`
```
The model could not be reached, so no outfit or fit card could be generated: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```
Not handled before this unit — `generate()` already raised `ModelUnavailable` with a readable message, but `run_agent()` didn't catch it, so it reached `app.py`'s top-level handler as `ModelUnavailable: <message>` and exited. Added a `try/except ModelUnavailable` around the two model-calling steps in `run_agent()` that sets `session["error"]` instead, so the failure comes back through the same session shape as the other two branches rather than killing the process. Key restored afterward; confirmed with `python test.py`.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
