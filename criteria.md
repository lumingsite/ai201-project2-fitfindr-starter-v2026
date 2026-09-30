# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**

My search is a plain keyword match, so some phrasings will miss — that's why
4 of 5, not 5 of 5.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

This path is a deterministic code branch — it doesn't call the model and
isn't subject to model randomness — so it can be held to 5 of 5, unlike
criterion 1.

---

## 3. Something about state

Given a completed run, the `id` of the listing `search_listings` selected as
its first result matches the `id` of the `new_item` actually passed into
`suggest_outfit` — in 5 of 5 tries.

**Why this target:**

Passing the selected item into `suggest_outfit` is a deterministic assignment
through session state, not a model call — there is no legitimate source of
variance here. A mismatch can only be a bug, not acceptable error, so this
must be 5 of 5.



---

## 4. Something about the fit card

Given 5 generated fit cards for different items: (a) each one mentions the
item's price and its platform at least once — 5 of 5; and (b) comparing all
10 pairs of opening sentences across the 5 outputs, at most 1 pair is
identical — 9 of 10 pairs distinct.

**Why this target:**

`TEMPERATURE` is 0.9 (not 0), so the output is intentionally non-deterministic
— occasionally generating a similar-sounding opening by chance is expected and
shouldn't be over-penalized, but heavy repetition would still be a problem,
hence one pair of tolerance. Mentioning price and platform, however, is a
prompt-following instruction, not stylistic variance, so those must hold 5 of
5.



---

## 5. Your choice

Given a query with an explicit `max_price`, the price of `selected_item`
is less than or equal to `max_price` — in 5 of 5 tries.

**Why this target:**

Ignoring the price ceiling makes the recommendation entirely invalid to the
user — there is no acceptable rate of failure here, so this has to be 5 of 5.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
