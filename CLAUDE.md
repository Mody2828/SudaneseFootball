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

## Key Patterns

- **All content is hardcoded in HTML** — no database, no API, no templating. Updating a training session means editing `index.html` directly.
- **RTL layout**: `<html lang="ar" dir="rtl">`. All text is Arabic. Player names, team names, dates, and announcements are in Arabic.
- **Pitch lineup sync**: `syncLineup()` in `index.html` copies player names/numbers from the roster cards (`.tv-player-card`) to the pitch dots (`.pp`), so you only need to edit the roster cards.
- **Formation**: Teams play 6v6 indoor with 1-2-3 formation (1 GK, 2 DEF, 3 FWD). Pitch positions are set via inline `style` attributes (percentage-based `left`/`top`).
- **Two team colors**: Yellow (`.yellow-team`, `.yp`) and Red (`.red-team`, `.rp`) with corresponding CSS variables `--amber*` and `--red*`.
- **Modals**: Gallery, announcements, rules, and jerseys all use simple show/hide with `display` toggling. Body scroll is locked via `.body-locked` class.
- **Gallery lightbox**: Supports keyboard nav, touch swipe, zoom, filmstrip thumbnails. Image list is maintained in both the HTML masonry grid and the `galleryImages` JS array.
- **Match cards** in `previous-matches.html` use classes `.match-card`, `.red-team-column`, `.yellow-team-column`, `.player-name` — these are parsed by the notebook.

## Development

No build step. Open `index.html` in a browser or use any static file server. All external dependencies are loaded via CDN (Google Fonts, Font Awesome).

## Updating for a New Training Session

1. Edit `index.html`: update match title, date, time, team rosters, pitch lineup positions, bench players, and jersey holder.
2. Move the previous session's data into `previous-matches.html` as a new `.match-card` block.
3. If a match report is written, add a new `<article class="report-card">` to `reports.html`.
4. New gallery photos go in `Gallery/` and need entries in both the masonry grid HTML and the `galleryImages` JS array.
