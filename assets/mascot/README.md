# Mascot art

No art ships with this repo. The dashboard shows a labelled placeholder until you
add your own, so a fresh clone works without these files.

To supply a mascot, drop five images here, named for the mood the dashboard derives
from streak state:

| File | Shown when |
|---|---|
| `thriving.png` | today is logged |
| `neutral.png` | streak active, today not logged yet |
| `worried.png` | one day missed (`grace`) |
| `battered.png` | streak broken |
| `celebrating.png` | first dashboard open after a `log-day` write |

A matching `.webp` beside each `.png` is optional and preferred when present.

Square images work best — they are bottom-aligned in a 250px frame, so keep the
character's feet near the bottom edge with transparent space above. `celebrating`
and `battered` are treated as full-bleed scenes and fill the frame instead.

Use art you have the right to distribute. This folder is public.
