---
name: routine
description: Match day routine — move current match to previous, record result, set up next match from screenshot. Use when user says "routine" or "do the routine".
argument-hint: "[1 yellow/red] | [result e.g. yellow won 9 null]"
---

# Match Day Routine

Execute these steps in order using `$ARGUMENTS` for the team assignment and result.

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
</div>
```

## Step 3 — Update Jersey (فنايل) Table

1. Find the current jersey holder in the bench jerseys card — mark them as **done** (`<span class="status done">✓</span>`) in the jerseys table.
2. The new jersey holder (from the next match screenshot) gets marked as **due** (`<span class="status due">!</span>`).
3. **Move the new due person's row** to sit just below the last "done" entry in the table (remove from old position, insert after last ✓).

## Step 4 — Set Up Next Match from Screenshot

The user provides a screenshot with next match data. Extract:
- Match title (day + date)
- Venue and time
- Yellow team players (in order)
- Red team players (in order)
- Bench/substitute players
- Jersey holder name

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
- Jersey holder in bench jerseys card
- The first row of each team keeps the `رزقه | [other player]` format (the split happens next routine)
