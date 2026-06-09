#!/usr/bin/env python3
# OGP画像 (1200x630) を生成する一回限りのスクリプト
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
JP = "/System/Library/Fonts/Hiragino Sans GB.ttc"      # 日本語(W3) ※太字はstrokeで補強
EN = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def jp(sz):  return ImageFont.truetype(JP, sz, index=0)
def en(sz):  return ImageFont.truetype(EN, sz)

# ---- 背景: 縦グラデーション ----
top = (10, 17, 38)      # #0a1126
bot = (15, 28, 60)      # #0f1c3c
bg = Image.new("RGB", (W, H))
px = bg.load()
for y in range(H):
    t = y / (H - 1)
    r = int(top[0] + (bot[0]-top[0])*t)
    g = int(top[1] + (bot[1]-top[1])*t)
    b = int(top[2] + (bot[2]-top[2])*t)
    for x in range(W):
        px[x, y] = (r, g, b)

# ---- グロー(放射状ぼかし) ----
def glow(color, cx, cy, rad, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(rad*0.45))
    bg.paste(Image.alpha_composite(bg.convert("RGBA"), layer).convert("RGB"), (0, 0))

glow((37, 99, 235), 1050, 90, 360, 150)    # 青 右上
glow((245, 158, 11), 120, 600, 300, 90)    # 橙 左下
img = bg.convert("RGBA")
draw = ImageDraw.Draw(img)

# ---- 角丸ヘルパ ----
def rrect(d, box, rad, **kw):
    d.rounded_rectangle(box, radius=rad, **kw)

PAD = 84

# ---- ブランドバッジ(角丸＋ストップウォッチ風アイコン) ----
bx, by, bs = PAD, 70, 84
badge = Image.new("RGBA", (bs, bs), (0, 0, 0, 0))
bd = ImageDraw.Draw(badge)
# 青グラデっぽい塗り(単色＋下に濃色を重ね)
bd.rounded_rectangle([0, 0, bs, bs], radius=22, fill=(37, 99, 235, 255))
bd.rounded_rectangle([0, bs*0.5, bs, bs], radius=22, fill=(30, 64, 175, 120))
# ストップウォッチ
cx, cy, rr = bs/2, bs/2+4, 22
bd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=(255, 255, 255, 255), width=5)
bd.line([cx, cy-6, cx, cy], fill=(255, 255, 255, 255), width=5)          # 針(縦)
bd.line([cx, cy, cx+11, cy-9], fill=(245, 158, 11, 255), width=5)        # 針(橙)
bd.rectangle([cx-6, by*0+6, cx+6, 12], fill=(255, 255, 255, 255))        # 上ボタン土台
bd.rounded_rectangle([cx-7, 4, cx+7, 12], radius=3, fill=(255, 255, 255, 255))
img.alpha_composite(badge, (bx, by))

# ---- ブランド名 ----
draw.text((bx + bs + 26, by + 8), "MARATHON PREP", font=en(34), fill=(226, 235, 250, 255))
draw.text((bx + bs + 28, by + 50), "マラソン準備ツール", font=jp(26), fill=(147, 180, 245, 255))

# ---- メインタイトル ----
def text_bold(d, xy, s, font, fill, stroke=1):
    d.text(xy, s, font=font, fill=fill, stroke_width=stroke, stroke_fill=fill)

white = (244, 248, 255, 255)
orange = (245, 158, 11, 255)
y = 232
text_bold(draw, (PAD, y),       "マラソンに向けて、",            jp(64), white, 1)
text_bold(draw, (PAD, y + 92),  "計算も練習もカウントダウンも。", jp(64), white, 1)
text_bold(draw, (PAD, y + 196), "ぜんぶここで。",                jp(78), orange, 2)

# ---- 機能チップ ----
chips = ["換算", "予測", "練習メニュー", "ラップ", "コース", "大会"]
cf = jp(28)
cx0, cy0, ch = PAD, 560, 50
gap = 16
x = cx0
for c in chips:
    tw = draw.textlength(c, font=cf)
    cw = tw + 44
    rrect(draw, [x, cy0, x + cw, cy0 + ch], 25,
          fill=(56, 96, 170, 130), outline=(120, 165, 240, 150), width=2)
    draw.text((x + 22, cy0 + 10), c, font=cf, fill=(238, 244, 252, 255))
    x += cw + gap

img.convert("RGB").save("ogp.png", "PNG")
print("saved ogp.png", img.size)

# ---- ファビコン / apple-touch-icon（同デザインのストップウォッチ）----
def make_icon(s):
    # 角丸＋縦グラデーション背景
    grad = Image.new("RGB", (s, s))
    gp = grad.load()
    c0, c1 = (37, 99, 235), (29, 58, 140)
    for yy in range(s):
        t = yy / (s - 1)
        col = tuple(int(c0[i] + (c1[i]-c0[i])*t) for i in range(3))
        for xx in range(s):
            gp[xx, yy] = col
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s-1, s-1], radius=int(s*0.22), fill=255)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    im.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(im)
    cx, cy, rr = s/2, s*0.56, s*0.25
    w = max(2, int(round(s*0.075)))
    # 上ボタン＋ステム
    bw, bh = int(s*0.18), int(s*0.12)
    d.rounded_rectangle([cx-bw/2, s*0.05, cx+bw/2, s*0.05+bh], radius=max(2, int(s*0.05)), fill=(255, 255, 255, 255))
    d.line([cx, s*0.05+bh, cx, cy-rr], fill=(255, 255, 255, 255), width=w)
    # 文字盤
    d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=(255, 255, 255, 255), width=w)
    d.line([cx, cy-rr*0.5, cx, cy], fill=(255, 255, 255, 255), width=w)
    d.line([cx, cy, cx+rr*0.6, cy-rr*0.5], fill=(245, 158, 11, 255), width=w)
    return im

make_icon(180).save("apple-touch-icon.png", "PNG")
make_icon(48).resize((48, 48), Image.LANCZOS).save("favicon.png", "PNG")
make_icon(512).resize((512, 512)).save("icon-512.png", "PNG")  # PWA等の予備
print("saved favicon.png / apple-touch-icon.png / icon-512.png")
