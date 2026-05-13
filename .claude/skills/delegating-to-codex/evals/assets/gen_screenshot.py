"""Generate a synthetic iPhone 15 Pro settings-page screenshot with a deliberate
6px overlap between the 'Push notifications' toggle row and the divider above it.

This is a fixture for eval #2 of the delegating-to-codex skill.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 393, 852  # iPhone 15 Pro logical resolution
BG = (242, 242, 247)            # iOS group background
CARD = (255, 255, 255)
TEXT = (0, 0, 0)
SUB = (60, 60, 67, 153)
DIVIDER = (198, 198, 200)
ACCENT_ON = (52, 199, 89)       # iOS green for "on" toggle
ACCENT_OFF = (228, 228, 230)
NAV = (0, 122, 255)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

f_title  = font(28, bold=True)
f_h2     = font(20, bold=True)
f_row    = font(16)
f_caption= font(12)

# Status bar mock
d.text((20, 14), "9:41", fill=TEXT, font=f_row)
d.text((W-60, 14), "100%", fill=TEXT, font=f_row)

# Nav bar
d.text((20, 50), "< General", fill=NAV, font=f_row)
d.text((W/2 - 36, 50), "Settings", fill=TEXT, font=f_row)

# Big title
d.text((20, 90), "Notifications", fill=TEXT, font=f_title)

# First card: Allow Notifications row
card1_top = 150
card1_h = 56
d.rectangle((16, card1_top, W-16, card1_top + card1_h), fill=CARD)
d.text((28, card1_top + 18), "Allow Notifications", fill=TEXT, font=f_row)
# toggle on (drawn correctly)
tx, ty = W-72, card1_top + 16
d.rounded_rectangle((tx, ty, tx+48, ty+24), radius=12, fill=ACCENT_ON)
d.ellipse((tx+24, ty+1, tx+47, ty+23), fill="white")

# Divider line below card1 (this is the divider that gets overlapped)
divider_y = card1_top + card1_h + 22
d.line((16, divider_y, W-16, divider_y), fill=DIVIDER, width=1)

# Section header
d.text((28, divider_y + 8), "ALERTS", fill=SUB[:3], font=f_caption)

# Second card top — DELIBERATE BUG: it overlaps the divider by 6px
# Correct position would be divider_y + 32. We start at divider_y - 6.
card2_top = divider_y - 6
card2_h = 56
d.rectangle((16, card2_top, W-16, card2_top + card2_h), fill=CARD)

# Row text inside card2 — "Push notifications" — visually overlapping divider
d.text((28, card2_top + 18), "Push notifications", fill=TEXT, font=f_row)
# toggle on
tx2, ty2 = W-72, card2_top + 16
d.rounded_rectangle((tx2, ty2, tx2+48, ty2+24), radius=12, fill=ACCENT_ON)
d.ellipse((tx2+24, ty2+1, tx2+47, ty2+23), fill="white")

# Row 2 inside card2
row2_y = card2_top + card2_h
d.line((28, row2_y, W-16, row2_y), fill=DIVIDER, width=1)
d.rectangle((16, row2_y, W-16, row2_y + card2_h), fill=CARD)
d.text((28, row2_y + 18), "Sounds", fill=TEXT, font=f_row)
tx3, ty3 = W-72, row2_y + 16
d.rounded_rectangle((tx3, ty3, tx3+48, ty3+24), radius=12, fill=ACCENT_OFF)
d.ellipse((tx3+1, ty3+1, tx3+24, ty3+23), fill="white")

# Subtle red annotation arrow to make the bug findable for any vision model
# (this is not part of the "in-app" UI; it's a debug hint baked into the fixture
#  so eval results don't depend on the model spotting subpixel issues)
d.line((W-30, divider_y-12, W-30, divider_y+12), fill=(255, 59, 48), width=2)
d.polygon([(W-34, divider_y-10), (W-26, divider_y-10), (W-30, divider_y-16)],
          fill=(255, 59, 48))
d.text((W-100, divider_y+18), "6px overlap", fill=(255, 59, 48), font=f_caption)

out = Path(__file__).resolve().parent / "screenshot-settings.png"
img.save(out, "PNG", optimize=True)
print(f"wrote {out} ({out.stat().st_size} bytes)")
