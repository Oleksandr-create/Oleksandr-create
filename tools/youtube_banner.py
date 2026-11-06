"""YouTube channel banner for INCON (2560x1440, text inside the 1546x423 safe area).

Usage: python3 youtube_banner.py logo.jpg out.png [debug_preview.png]
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import sys

W, H = 2560, 1440
SAFE = (507, 508, 2053, 931)  # area visible on every device (1546x423)
RED, DARK, WHITE = (238, 32, 45), (196, 18, 32), (255, 255, 255)
F = "/usr/share/fonts/opentype/inter/"
font = lambda name, s: ImageFont.truetype(F + name, s)

# logo -> white-on-transparent mask (alpha from how far a pixel is from white)
logo = Image.open(sys.argv[1]).convert("RGB")
logo = logo.resize((logo.width * 3, logo.height * 3), Image.LANCZOS)
g = logo.split()[1]
alpha = g.point(lambda v: max(0, min(255, int((255 - v) * 255 / (255 - 32)))))
def tinted(color, a):
    im = Image.new("RGBA", a.size, color + (255,)); im.putalpha(a); return im

# background: brand red with a darker radial vignette
bg = Image.new("RGB", (W, H), RED)
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse((-600, -500, W + 600, H + 500), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(260))
bg = Image.composite(bg, Image.new("RGB", (W, H), DARK), vig).convert("RGBA")

# large faded elephants on the sides (decor, visible on TV/desktop only)
elephants = alpha.crop((0, 0, alpha.width, int(alpha.height * 0.60)))
big_h = 1250
big = elephants.resize((int(elephants.width * big_h / elephants.height), big_h), Image.LANCZOS)
faint = big.point(lambda v: int(v * 0.07))
layer = Image.new("RGBA", big.size, WHITE + (255,)); layer.putalpha(faint)
bg.alpha_composite(layer, (W - big.width + 380, H - big_h + 260))
small = big.resize((big.width // 2, big_h // 2), Image.LANCZOS)
l2 = Image.new("RGBA", small.size, WHITE + (255,)); l2.putalpha(small.point(lambda v: int(v * 0.07)))
bg.alpha_composite(l2, (-160, -90))

d = ImageDraw.Draw(bg)
sx0, sy0, sx1, sy1 = SAFE

# logo, white, left of safe area
lh = sy1 - sy0 - 20
lw = int(logo.width * lh / logo.height)
la = alpha.resize((lw, lh), Image.LANCZOS)
bg.alpha_composite(tinted(WHITE, la), (sx0, sy0 + 10))

# divider
dx = sx0 + lw + 56
d.rectangle((dx, sy0 + 40, dx + 5, sy1 - 40), fill=(255, 255, 255, 140))

# text block
tx = dx + 60
tw = sx1 - tx - 30

def fit(text, name, size, width):
    while size > 20:
        f = font(name, size)
        if d.textlength(text, font=f) <= width: return f
        size -= 2
    return font(name, size)

f1 = fit("Семінари та вебінари", "InterDisplay-Black.otf", 92, tw)
f2 = fit("для бухгалтерів, юристів,", "InterDisplay-Bold.otf", 54, tw)
f3 = fit("з 2005 року  ·  лектори-практики  ·  нові відео щотижня", "InterDisplay-SemiBold.otf", 36, tw)
f4 = font("InterDisplay-Black.otf", 40)

y = sy0 + 16
d.text((tx, y), "Семінари та вебінари", font=f1, fill=WHITE); y += 112
d.text((tx, y), "для бухгалтерів, юристів,", font=f2, fill=WHITE); y += 64
d.text((tx, y), "кадровиків і керівників", font=f2, fill=WHITE); y += 86
d.text((tx, y), "з 2005 року  ·  лектори-практики  ·  нові відео щотижня", font=f3, fill=(255, 225, 225)); y += 60
url = "incon.com.ua"
pw = d.textlength(url, font=f4) + 56
d.rounded_rectangle((tx, y, tx + pw, y + 62), radius=31, fill=WHITE)
d.text((tx + 28, y + 9), url, font=f4, fill=RED)
assert y + 62 <= sy1, y + 62

out = bg.convert("RGB")
out.save(sys.argv[2], optimize=True)
if len(sys.argv) > 3:  # debug copy with the safe area outlined
    dbg = out.copy(); ImageDraw.Draw(dbg).rectangle(SAFE, outline=(0, 255, 0), width=4)
    dbg.resize((W // 2, H // 2)).save(sys.argv[3])
