# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"الدافوري" (Al-Dafouri) — A static Arabic (RTL) web app for organizing Sudanese football training sessions in a community group. No build tools, frameworks, or package manager — just HTML, CSS, and vanilla JS served directly.

## Architecture

- **`index.html`** — Main page: current training session with team rosters (Yellow vs Red), interactive football pitch lineup (1-2-3 formation), bench/subs, gallery lightbox, and modals (announcements, group rules, jersey wash schedule). All JS is inline in a `<script>` tag at the bottom.
- **`previous-matches.html`** — Historical match archive with match cards showing date, venue, scores, and player rosters per team. Uses the same `styles.css`.
- **`reports.html`** — Match reports written in Arabic newspaper style by "د. هاني قوي". Has its own body class `reports-page` for distinct styling.
- **`styles.css`** — Single shared stylesheet (~70KB). Dark glassmorphism theme with CSS custom properties in `:root`. Contains all component styles for all three pages.
- **`styles_transparent_board.css`** — Alternate standalone stylesheet for a transparent lineup board layout (uses `indoor-pitch.webp` as background).
- **`player_match_stats.ipynb`** — Jupyter notebook that parses `previous-matches.html` with BeautifulSoup to compute player win/loss stats. Designed to run in Google Colab.
- **`Gallery/`** — Training session photos (1.jpg–18.jpeg, no 13).
- **`sudan-ball.png`, `iran.webp`** — Logos used for special/international matches (e.g. Sudan vs Iran). Regular matches show `الفريق الأصفر` / `الفريق الأحمر`; international matches replace the team headers with country names + flag logos.
- **`routine.txt`** — Plain-text spec of the recurring match-day update task. The full procedure (with HTML templates and pitch coordinates) lives in `.claude/skills/routine/SKILL.md` and is invoked via the `/routine` skill.

## Key Patterns

- **All content is hardcoded in HTML** — no database, no API, no templating. Updating a training session means editing `index.html` directly.
- **RTL layout**: `<html lang="ar" dir="rtl">`. All text is Arabic. Player names, team names, dates, and announcements are in Arabic.
- **Pitch lineup sync**: `syncLineup()` in `index.html` copies player names/numbers from the roster cards (`.tv-player-card`) to the pitch dots (`.pp`), so you only need to edit the roster cards.
- **Formation**: Teams play 6v6 indoor (1-2-3) or 9v9 (1-2-3-3). Pitch positions are set via inline `style` attributes (percentage-based `left`/`top`). The formation badge uses Arabic-Indic digits: **١-٢-٣** or **١-٢-٣-٣**. Yellow occupies the top half; red mirrors at `top% = 100% - yellow_top%`. Canonical coordinates:
  - **6 (1-2-3):** GK 50%/5.5% · DEF 30% & 70% / 22% · FWD 20% & 50% & 80% / 39–41%
  - **9 (1-2-3-3):** GK 50%/5.5% · DEF 30% & 70% / 17% · MID 20% & 50% & 80% / 30–32% · FWD 20% & 50% & 80% / 42–44%
- **GK-split convention**: The first roster row of each team is written as `رزقه | [other player]` until the routine resolves it. The instruction `1 yellow` means رزقه stays on yellow GK and the `|` partner becomes red GK (vice versa for `1 red`). The split is fixed as Step 1 of the routine, not when the next match is set up.
- **Two team colors**: Yellow (`.yellow-team`, `.yp`) and Red (`.red-team`, `.rp`) with corresponding CSS variables `--amber*` and `--red*`.
- **Modals**: Gallery, announcements, rules, and jerseys all use simple show/hide with `display` toggling. Body scroll is locked via `.body-locked` class.
- **Gallery lightbox**: Supports keyboard nav, touch swipe, zoom, filmstrip thumbnails. Image list is maintained in both the HTML masonry grid and the `galleryImages` JS array.
- **Match cards** in `previous-matches.html` use classes `.match-card`, `.red-team-column`, `.yellow-team-column`, `.player-name` — these are parsed by the notebook.

## Development

No build step. Open `index.html` in a browser or use any static file server. All external dependencies are loaded via CDN (Google Fonts, Font Awesome).

## Updating for a New Training Session

The standard weekly update is automated by the `/routine` skill (see `.claude/skills/routine/SKILL.md`). Invoke it with `/routine 1 yellow | yellow won 9 null` (GK assignment + last match result), then provide the screenshot for the next match. The skill handles:

1. **GK split** in `index.html` based on the `1 yellow|red` argument.
2. **Archive**: prepend a new `.match-card` to `previous-matches.html` with the result. Match cards must keep the classes `.match-card`, `.red-team-column`, `.yellow-team-column`, `.player-name` — the notebook depends on them.
3. **Jersey table**: mark the previous holder as `done` (✓), the next holder as `due` (!), and reorder the new due row to sit just below the last ✓.
4. **Next match** in `index.html`: title, date/time, both rosters, formation badge, pitch dot positions, bench, jersey holder.

For things outside the routine: match reports go into `reports.html` as `<article class="report-card">`; new gallery photos must be added to **both** the masonry grid HTML and the `galleryImages` JS array in `index.html`.
