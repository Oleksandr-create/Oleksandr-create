"""Animated "subscribe to our YouTube channel" bar for incon.com.ua.

Usage: python3 subscribe_gif.py logo.jpg frames_dir  (then build GIF/MP4 with ffmpeg, see README.md)
"""
from PIL import Image, ImageDraw, ImageFont
import math, sys

S = 4                      # drawing scale (2x output, 2x supersampling)
OUT = 2                    # output is 2x the display size, for sharp phones/Retina
W, H = 960, 150            # output size
RED, GREY, DARK, LIGHT = (238, 32, 45), (102, 102, 102), (40, 40, 40), (205, 205, 205)
F = "/usr/share/fonts/opentype/inter/"
fnt = lambda name, size: ImageFont.truetype(F + name, size * S)

# avatar: red circle with the white elephants + INCON from the logo
logo = Image.open(sys.argv[1]).convert("RGB")
alpha = logo.split()[1].point(lambda v: max(0, min(255, int((255 - v) * 255 / 223))))
alpha = alpha.crop((0, 0, logo.width, 400))          # drop "ІНФОРМ-КОНСАЛТИНГ"
alpha = alpha.crop(alpha.getbbox())
AV = 116 * S
avatar = Image.new("RGBA", (AV, AV), (0, 0, 0, 0))
ImageDraw.Draw(avatar).ellipse((0, 0, AV - 1, AV - 1), fill=RED + (255,))
mw = int(AV * 0.68); mh = int(alpha.height * mw / alpha.width)
mark = Image.new("RGBA", (mw, mh), (255, 255, 255, 255)); mark.putalpha(alpha.resize((mw, mh), Image.LANCZOS))
avatar.alpha_composite(mark, ((AV - mw) // 2, (AV - mh) // 2))

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t

BTN = (580, 44, 860, 106)          # button box (output px)
BELL = (906, 78)                  # bell centre

def bell(d, cx, cy, color, angle=0.0, waves=False):
    cx, cy = cx * S, cy * S
    B = S * 0.8
    pts = []
    # bell outline built from a half-profile, mirrored, then rotated around the top
    prof = [(0, -30), (6, -29), (12, -24), (15, -14), (16, 2), (19, 12), (25, 18), (25, 22)]
    half = [(x * B, y * B) for x, y in prof]
    shape = half + [(-x, y) for x, y in reversed(half)]
    a = math.radians(angle)
    rot = lambda p: (cx + p[0] * math.cos(a) - (p[1] + 30 * B) * math.sin(a),
                     cy - 30 * B + p[0] * math.sin(a) + (p[1] + 30 * B) * math.cos(a))
    d.polygon([rot(p) for p in shape], fill=color)
    kx, ky = rot((0, 29 * B))
    d.ellipse((kx - 6 * B, ky - 6 * B, kx + 6 * B, ky + 6 * B), fill=color)
    tx, ty = rot((0, -31 * B))
    d.ellipse((tx - 4 * B, ty - 4 * B, tx + 4 * B, ty + 4 * B), fill=color)
    if waves:
        for side in (-1, 1):
            for r in (36, 46):
                box = (cx - r * B, cy - 8 * B - r * B, cx + r * B, cy - 8 * B + r * B)
                start = -40 if side == 1 else 180 - 20
                d.arc(box, start, start + 60 - 20 * (r == 46), fill=color, width=round(4 * B))

def cursor(img, x, y, scale=1.0):
    # hand-free classic arrow pointer, white with dark outline
    pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    pts = [(x * S + px * S * scale * 0.85, y * S + py * S * scale * 0.85) for px, py in pts]
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=(255, 255, 255), outline=(20, 20, 20), width=3 * S)

FPS, DUR = 25, 4.4
frames = []
for i in range(int(FPS * DUR)):
    t = i / FPS
    img = Image.new("RGB", (W * S, H * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W * S - 1, H * S - 1), outline=(225, 225, 225), width=2 * S)

    # avatar pops in at the start
    sc = 0.85 + 0.15 * ease(t / 0.35)
    av = avatar.resize((int(AV * sc), int(AV * sc)), Image.LANCZOS)
    img.paste(av, (int(34 * S + (AV - av.width) / 2), int((H * S - av.height) / 2)), av)

    d.text((176 * S, 24 * S), "INCON", font=fnt("InterDisplay-Black.otf", 44), fill=DARK)
    d.text((178 * S, 78 * S), "Інформ-Консалтинг", font=fnt("Inter-Bold.otf", 20), fill=GREY)
    d.text((178 * S, 106 * S), "YouTube · @incon.seminar", font=fnt("Inter-Medium.otf", 17), fill=GREY)

    # timeline: cursor travels to the button (0.4-1.3), clicks (1.4), goes to the bell (2.0-2.5), clicks (2.6)
    clicked = t >= 1.4
    bx0, by0, bx1, by1 = BTN
    press = 1.0
    if 1.3 <= t < 1.4: press = 0.95
    elif 1.4 <= t < 1.55: press = lerp(0.95, 1.0, (t - 1.4) / 0.15)
    pulse = 1.0 + (0.035 * math.sin((t - 0.8) * 12) if 0.8 <= t < 1.3 else 0)
    k = press * pulse
    cxm, cym = (bx0 + bx1) / 2, (by0 + by1) / 2
    hw, hh = (bx1 - bx0) / 2 * k, (by1 - by0) / 2 * k
    box = [(cxm - hw) * S, (cym - hh) * S, (cxm + hw) * S, (cym + hh) * S]
    label = "ВИ ПІДПИСАНІ" if clicked else "ПІДПИСАТИСЯ"
    fill = (229, 229, 229) if clicked else RED
    d.rectangle(box, fill=fill)
    lf = fnt("InterDisplay-Black.otf", int(30 * k) if not clicked else int(26 * k))
    tw = d.textlength(label, font=lf)
    d.text((cxm * S - tw / 2, cym * S), label, font=lf, fill=GREY if clicked else (255, 255, 255), anchor="lm")

    # ripple on click
    if 1.4 <= t < 1.8:
        r = lerp(10, 120, (t - 1.4) / 0.4) * S
        a = int(lerp(120, 0, (t - 1.4) / 0.4))
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).ellipse((cxm * S - r, cym * S - r, cxm * S + r, cym * S + r), fill=(255, 255, 255, a))
        img.paste(ov, (0, 0), ov)

    rung = t >= 2.6
    ang = 18 * math.sin((t - 2.6) * 30) * max(0, 1 - (t - 2.6) / 0.8) if rung else 0
    bell(d, BELL[0], BELL[1], DARK if rung else LIGHT, ang, waves=rung and t < 3.6)

    # cursor path
    if t < 0.4: cx, cy = W + 40, H + 40
    elif t < 1.3: e = ease((t - 0.4) / 0.9); cx, cy = lerp(W - 30, cxm + 20, e), lerp(H + 20, cym + 6, e)
    elif t < 2.0: cx, cy = cxm + 20, cym + 6
    elif t < 2.5: e = ease((t - 2.0) / 0.5); cx, cy = lerp(cxm + 20, BELL[0] + 4, e), lerp(cym + 6, BELL[1] + 6, e)
    elif t < 3.6: cx, cy = BELL[0] + 4, BELL[1] + 6
    else: e = ease((t - 3.6) / 0.6); cx, cy = lerp(BELL[0] + 4, W + 40, e), lerp(BELL[1] + 6, H + 60, e)
    clickdip = 0.85 if (1.3 <= t < 1.45 or 2.5 <= t < 2.65) else 1.0
    cursor(img, cx, cy, clickdip)

    frames.append(img.resize((W * OUT, H * OUT), Image.LANCZOS))

import os
os.makedirs(sys.argv[2], exist_ok=True)
for n, f in enumerate(frames): f.save(os.path.join(sys.argv[2], "f%03d.png" % n))
