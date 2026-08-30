# -*- coding: utf-8 -*-
"""Rank candidates for the next الفنايل (jersey-wash) holder.

Reads the CURRENT state of index.html (next-match lineup + jerseys table) and
previous-matches.html (attendance history), then prints a ranked shortlist.

Run AFTER the next match rosters/bench are in index.html and AFTER the finished
match has been archived, but BEFORE the jerseys table is updated.

Usage:
    python .claude/skills/routine/jersey_candidates.py --guests "name1,name2"
"""
import argparse
import io
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WINDOW_DEFAULT = 6      # how many recent archived matches count as "recent form"
REGULAR_MIN = 3         # rule 3: played 3+ of the recent games

# ---------------------------------------------------------------- name helpers
_TASHKEEL = re.compile(u"[ؐ-ًؚ-ٰٟۖ-ۭ]")


def norm(name):
    """Fold Arabic spelling variants so قياده/قيادة and أحمد/احمد match."""
    s = unicodedata.normalize("NFKC", name or "").strip()
    s = _TASHKEEL.sub("", s)
    s = s.replace(u"ـ", "")                                # tatweel
    s = re.sub(u"[آأإٱ]", u"ا", s)     # آ أ إ ٱ -> ا
    s = s.replace(u"ة", u"ه")                         # ة -> ه
    s = s.replace(u"ى", u"ي")                         # ى -> ي
    s = re.sub(r"\s+", " ", s)
    return s


GUEST_RE = re.compile(r"(?:^|\s)\(?[gG]\)?(?:\s|$)")


def strip_guest_flag(name):
    """Return (clean_name, is_guest) for a screenshot name that may carry a g."""
    if GUEST_RE.search(name):
        return GUEST_RE.sub(" ", name).strip(), True
    return name.strip(), False


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


# ---------------------------------------------------------------- index.html
def parse_index(html):
    tbl = html[html.index("jerseys-table"):html.index("</table>")]
    rows = re.findall(
        r"<tr>\s*<td>([^<]*)</td>\s*<td>\s*<span class=\"status (\w+)\"", tbl)
    table = [(n.strip(), st) for n, st in rows]

    ysec = html[html.index("Yellow Team"):html.index("Red Team")]
    rsec = html[html.index("Red Team"):html.index("lineup-section")]

    def roster(sec):
        out = []
        for raw in re.findall(r'class="tv-name player-name">([^<]*)<', sec):
            for part in raw.split("|"):      # unresolved GK split "رزقه | انور"
                part = part.strip()
                if part:
                    out.append(part)
        return out

    starters = roster(ysec) + roster(rsec)

    bsec = html[html.index("bench-section"):]
    cards = bsec.split('class="bench-card')
    bench = re.findall(r'class="bench-name">([^<]*)<', cards[1]) if len(cards) > 1 else []
    holder = re.findall(r'class="bench-name">([^<]*)<', cards[2]) if len(cards) > 2 else []
    return table, starters, [b.strip() for b in bench], (holder[0].strip() if holder else None)


# ---------------------------------------------------------- previous-matches
def parse_archive(html):
    matches = []
    for card in html.split('class="match-card"')[1:]:
        if "jerseys-row" in card:
            card = card[:card.index("jerseys-row")]
        date = re.search(r'class="match-date">([^<]*)<', card)
        names = [n.strip() for n in re.findall(r'class="player-name">([^<]*)<', card)]
        matches.append((date.group(1).strip() if date else "?", names))
    return matches


def parse_past_holders(html):
    return [n.strip() for n in
            re.findall(r'class="jerseys-info">.*?</i>\s*([^<]*)<', html, re.S)]


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guests", default="",
                    help="comma-separated names flagged g in the screenshot")
    ap.add_argument("--window", type=int, default=WINDOW_DEFAULT)
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--index", default="index.html")
    ap.add_argument("--archive", default="previous-matches.html")
    a = ap.parse_args()

    table, starters, bench, card_holder = parse_index(read(a.index))
    archive = parse_archive(read(a.archive))
    past_holders = set(norm(h) for h in parse_past_holders(read(a.archive)))

    guests = set()
    for g in a.guests.split(","):
        g = strip_guest_flag(g)[0]
        if g:
            guests.add(norm(g))

    # also honour a g written straight into the lineup itself
    clean_starters, clean_bench = [], []
    for src, dst in ((starters, clean_starters), (bench, clean_bench)):
        for n in src:
            c, is_guest = strip_guest_flag(n)
            if is_guest:
                guests.add(norm(c))
            dst.append(c)
    starters, bench = clean_starters, clean_bench

    status = dict((norm(n), st) for n, st in table)
    order = dict((norm(n), i) for i, (n, _) in enumerate(table))
    display = dict((norm(n), n) for n, _ in table)
    outgoing = next((n for n, st in table if st == "due"), card_holder)

    recent = archive[:a.window]
    played = {}
    for i, (_, names) in enumerate(recent):
        for n in names:
            played.setdefault(norm(n), set()).add(i)
    last3 = set(k for k, v in played.items() if set([0, 1, 2]) <= v)

    lineup = [(n, True) for n in starters] + [(n, False) for n in bench]
    seen, ranked, skipped = set(), [], []
    for name, is_starter in lineup:
        k = norm(name)
        if k in seen:
            continue
        seen.add(k)
        att = len(played.get(k, ()))
        why = []
        if k in guests:
            why.append(u"ضيف / guest")
        if outgoing and k == norm(outgoing):
            why.append("just held it")
        if k not in status:
            why.append("not in jerseys table")
        if why:
            skipped.append((display.get(k, name), u"، ".join(why), att))
            continue
        score = 10 * att
        if k in last3:
            score += 6
        if k not in past_holders and status[k] == "unmarked":
            score += 4
        if is_starter:
            score += 3
        score += (len(table) - order[k]) / 100.0
        ranked.append(dict(name=display.get(k, name), att=att, score=score,
                           status=status[k], starter=is_starter,
                           regular=att >= REGULAR_MIN,
                           first_time=k not in past_holders,
                           streak=k in last3, order=order[k]))

    def bucket(c):
        # 0 = ideal: not done + meets the attendance rule
        # 1 = not done but thin recent form
        # 2 = already done (rotation restart / nothing else left)
        if c["status"] != "done" and c["regular"]:
            return 0
        if c["status"] != "done":
            return 1
        return 2

    ranked.sort(key=lambda c: (bucket(c), -c["score"], c["order"]))

    print("recent window: %d matches - %s"
          % (len(recent), " | ".join(d for d, _ in recent)))
    print("outgoing holder: %s" % (outgoing or "?"))
    if guests:
        print("guests excluded: %s"
              % u"، ".join(sorted(display.get(g, g) for g in guests)))
    print("")
    print("CANDIDATES (pick one):")
    for i, c in enumerate(ranked[:a.top], 1):
        tags = ["%d/%d recent" % (c["att"], len(recent))]
        if c["streak"]:
            tags.append("last 3 in a row")
        if c["first_time"]:
            tags.append("never held it")
        tags.append("starter" if c["starter"] else "bench")
        if c["status"] == "done":
            tags.append("ALREADY DONE - rotation restart")
        if not c["regular"]:
            tags.append("under %d recent games" % REGULAR_MIN)
        print("  %d. %-16s score %6.2f  (%s)"
              % (i, c["name"], c["score"], u"، ".join(tags)))
    if not ranked:
        print("  (none - every player in the lineup was filtered out)")
    if len(ranked) > a.top:
        print("")
        print("next in line: "
              + u"، ".join(c["name"] for c in ranked[a.top:a.top + 4]))
    if skipped:
        print("")
        print("skipped:")
        for n, why, att in skipped:
            print("  - %-16s %s (%d recent)" % (n, why, att))


if __name__ == "__main__":
    main()
