---
name: routine
description: Match day routine — move current match to previous, record result, set up next match from screenshot, then propose 3 jersey-holder candidates for the user to choose. Use when user says "routine" or "do the routine".
argument-hint: "[1 yellow/red] | [result e.g. yellow won 9 null]"
---

# Match Day Routine

Execute these steps **in order** using `$ARGUMENTS` for the team assignment and result.

The screenshot does **not** contain the jersey holder — Step 4 works that out and asks the
user to choose. Everything else comes from the screenshot as before.

## Step 1 — Fix the GK Split

The first row of each team in `index.html` has two players: `رزقه | [other player]`.
- Parse the `$ARGUMENTS` for "1 yellow" or "1 red" — this tells which team رزقه plays on.
- "1 yellow" → رزقه stays in yellow, the other player (after `|`) becomes red team GK.
- "1 red" → رزقه stays in red, the other player becomes yellow team GK.

## Step 2 — Move Current Match to Previous Matches

Take the current match from `index.html` (title, date, venue, teams, players after the GK fix) and insert a new `.match-card` block at the **top** of `previous-matches.html` (before existing match cards).

Record the result from `$ARGUMENTS`:
- "yellow won 9 null" → yellow score 9, red score 0
- "red won 5 3" → red score 5, yellow score 3

Match card format:
```html
<div class="match-card">
  <div class="match-details">
    <span class="match-date">[day] [dd/mm/yyyy]</span>
    <span class="match-venue">[venue and time]</span>
  </div>
  <div class="teams-row">
    <div class="team-name red-team">الفريق الأحمر</div>
    <div class="team-name yellow-team">الفريق الأصفر</div>
  </div>
  <div class="score-row">
    <div class="score red-score">[red score]</div>
    <div class="score-separator">-</div>
    <div class="score yellow-score">[yellow score]</div>
    <div class="score-label">النتيجه</div>
  </div>
  <div class="players-section">
    <div class="players-column red-team-column">
      <div class="player-row red-player"><span class="player-name">[name]</span></div>
      ...
    </div>
    <div class="players-column yellow-team-column">
      <div class="player-row yellow-player"><span class="player-name">[name]</span></div>
      ...
    </div>
  </div>
  <div class="jerseys-row">
    <span class="jerseys-info">الفنايل <i class="fas fa-tshirt"></i> [jersey holder name from the current match's bench jerseys card]</span>
  </div>
</div>
```

## Step 3 — Set Up Next Match from Screenshot

The user provides a screenshot with next match data. Extract:
- Match title (day + date)
- Venue and time
- Yellow team players (in order)
- Red team players (in order)
- Bench/substitute players
- **Guest flags** — any name carrying a standalone `g` (e.g. `امجد g`) is a guest. Strip the
  `g` from the name you write into the HTML, but remember the list for Step 4.

Update `index.html`:
- Match title (`h1.match-title`) and details
- Lineup header date and time
- Both team roster cards (`.yellow-team .tv-lineup` and `.red-team .tv-lineup`)
- Formation badge — use **١-٢-٣** for 6 players, **١-٢-٣-٣** for 9 players
- Football pitch dots (`.pp.yp` and `.pp.rp`) with correct formation positions:
  - **6 players (1-2-3):** GK at 50%/5.5%, DEF at 30%+70%/22%, FWD at 20%+50%+80%/39-41%
  - **9 players (1-2-3-3):** GK at 50%/5.5%, DEF at 30%+70%/17%, MID at 20%+50%+80%/30-32%, FWD at 20%+50%+80%/42-44%
  - Red team mirrors at bottom half (top% = 100% - yellow top%)
- Bench section players
- The first row of each team keeps the `رزقه | [other player]` format (the split happens next routine)

**Do not touch the jerseys card or the jerseys table yet** — Step 4 needs the outgoing holder
still marked `due`.

⚠️ When editing rosters, watch for **name collisions between the two teams**. Replacing
`--ti:N ... [name]` one at a time can hit the yellow card when you meant the red one if both
teams have the same player at the same row index. Split the HTML at `<!-- Red Team -->` and
edit each half separately, then verify both rosters against the screenshot before moving on.

### New names
If a player in the lineup is not yet a row in the jerseys table:
- **Guest** (flagged `g`) → leave them out of the table entirely. Guests never wash jerseys.
- **Regular** → add a row at the bottom of the table with `<span class="status unmarked">-</span>`,
  so they enter the rotation.

If it is not obvious which, ask the user.

## Step 4 — Pick the Jersey (فنايل) Holder

Run the ranking script from the repo root, passing any guests you saw in the screenshot:

```bash
python .claude/skills/routine/jersey_candidates.py --guests "امجد,محمد نايل"
```

It reads the freshly-updated `index.html` (lineup + jerseys table) and `previous-matches.html`
(attendance + past holders) and prints a ranked shortlist.

**Selection rules it applies** — hard filters first, then score:

*Hard filters (excluded outright):*
1. Must be playing in the next match — starters or bench.
2. Not a **guest** (flagged `g` in the screenshot, or passed via `--guests`).
3. Not the **outgoing holder** (the row currently marked `due`) — they have just done it.
4. Must exist in the jerseys table, otherwise there is no row to mark.

*Tiers, best first:*
- **Tier 0** — not yet `done` **and** played ≥3 of the last 6 matches.
- **Tier 1** — not yet `done` but thinner recent form (used when Tier 0 is short).
- **Tier 2** — already `done`. Only surfaces when everyone eligible has had a turn, i.e. the
  rotation restarts from the top of the list.

*Score within a tier:*
- `10 ×` appearances in the last 6 archived matches — the more he played, the stronger.
- `+6` played the last 3 matches in a row (a regular).
- `+4` never held the jersey before (no `✓` and no past `jerseys-info` mention).
- `+3` starter rather than bench.
- `+ (rows − table position)/100` — a name higher up the table is more overdue; also a stable tie-break.

Then **present the top 3 to the user and ask them to choose** with `AskUserQuestion` — one
option per candidate, numbered 1–3, most suitable first, each labelled with the reason the
script gave (recent appearances, streak, never-held, starter/bench). Do not pick for them.
Include the script's "next in line" names in the question description so they have context if
they want someone else.

Flags worth mentioning to the user when they appear: a Tier 2 candidate (rotation restarting),
or a lineup player skipped for a reason they may want to override.

## Step 5 — Apply the Jersey Update

Once the user has chosen:
1. The **outgoing** holder (currently `due`) → `<span class="status done">✓</span>`.
2. The **chosen** player → `<span class="status due">!</span>`.
3. **Move the chosen player's row** to sit just below the last `✓` in the table (remove from
   old position, insert after the last done entry).
4. Put the chosen player's name in the bench jerseys card in `index.html`
   (`.bench-card.jerseys-card .bench-name`).

## Verify

Before committing, check:
- Both rosters and the pitch dots match the screenshot, name for name.
- The archived card has the right score, date and outgoing jersey holder.
- The jerseys table has exactly one `due` row, sitting directly under the last `✓`.
- No name appears twice in the jerseys table.
