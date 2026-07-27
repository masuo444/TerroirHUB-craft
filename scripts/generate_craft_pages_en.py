#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""英語版の工芸品個別ページを生成する。

データ245件すべてに desc_en（中央値502字の英文）が最初から入っていたのに、
英語ページが1枚も存在しなかった（2026-07-27発見）。訪日客・海外の工芸ファンに
とって最も需要のある情報が、日本語ページの片隅にしか出ていなかった。

設計:
  - 出力: en/craft/{prefecture}/{id}.html + en/craft/index.html
  - 本文は desc_en を主役に。技法・原材料は翻訳不能な固有名詞なので
    日本語表記のまま英語ラベルで示す（誤ローマ字化より誠実）
  - CSSは日本語ページから流用して見た目を揃える
  - hreflang ja/en の完全な対（日本語側は generate_craft_pages.py が張る）
  - 地図は他ジャンルと同じOpenStreetMap埋め込み（lat/lngがある場合のみ）
"""
import json
import os
import glob
import re
import html as _html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://craft.terroirhub.com"

CATEGORY_EN = {
    "ceramics": "Ceramics", "lacquerware": "Lacquerware", "textiles": "Textiles",
    "dyeing": "Dyeing", "metalwork": "Metalwork", "paper": "Washi Paper",
    "woodwork": "Wood & Bamboo", "dolls": "Dolls & Kokeshi",
    "buddhist": "Buddhist Crafts", "other": "Other Crafts",
}
PREF_EN = {
    'hokkaido': 'Hokkaido', 'aomori': 'Aomori', 'iwate': 'Iwate', 'miyagi': 'Miyagi', 'akita': 'Akita',
    'yamagata': 'Yamagata', 'fukushima': 'Fukushima', 'ibaraki': 'Ibaraki', 'tochigi': 'Tochigi',
    'gunma': 'Gunma', 'saitama': 'Saitama', 'chiba': 'Chiba', 'tokyo': 'Tokyo', 'kanagawa': 'Kanagawa',
    'niigata': 'Niigata', 'toyama': 'Toyama', 'ishikawa': 'Ishikawa', 'fukui': 'Fukui',
    'yamanashi': 'Yamanashi', 'nagano': 'Nagano', 'gifu': 'Gifu', 'shizuoka': 'Shizuoka',
    'aichi': 'Aichi', 'mie': 'Mie', 'shiga': 'Shiga', 'kyoto': 'Kyoto', 'osaka': 'Osaka',
    'hyogo': 'Hyogo', 'nara': 'Nara', 'wakayama': 'Wakayama', 'tottori': 'Tottori',
    'shimane': 'Shimane', 'okayama': 'Okayama', 'hiroshima': 'Hiroshima', 'yamaguchi': 'Yamaguchi',
    'tokushima': 'Tokushima', 'kagawa': 'Kagawa', 'ehime': 'Ehime', 'kochi': 'Kochi',
    'fukuoka': 'Fukuoka', 'saga': 'Saga', 'nagasaki': 'Nagasaki', 'kumamoto': 'Kumamoto',
    'oita': 'Oita', 'miyazaki': 'Miyazaki', 'kagoshima': 'Kagoshima', 'okinawa': 'Okinawa',
}


def esc(s):
    return _html.escape(str(s or ''), quote=True)


def load_all():
    crafts = []
    for f in sorted(glob.glob(os.path.join(BASE, 'data', '*.json'))):
        for b in json.load(open(f, encoding='utf-8')):
            if isinstance(b, dict) and b.get('id'):
                crafts.append(b)
    return crafts


def base_css():
    """日本語の個別ページからCSSを流用（見た目を揃える）。"""
    for p in glob.glob(os.path.join(BASE, 'craft', '*', '*.html')):
        if p.endswith('index.html'):
            continue
        m = re.search(r'<style>(.*?)</style>', open(p, encoding='utf-8').read(), re.S)
        if m:
            return m.group(1)
    return ''


EXTRA_CSS = """
.en-nav{position:sticky;top:0;z-index:90;background:rgba(253,251,247,.95);backdrop-filter:blur(10px);border-bottom:1px solid #e8e0d4;padding:12px 24px;display:flex;gap:16px;align-items:center;}
.en-nav a{text-decoration:none;color:#4a4039;font-size:13.5px;}
.en-nav .brand{font-weight:700;font-size:16px;letter-spacing:.04em;color:#2a2018;}
.en-nav .lang{margin-left:auto;font-size:12px;}
.terms-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.term-chip{font-size:13px;padding:6px 12px;background:#f4ede2;border:1px solid #e2d5c2;border-radius:16px;color:#4a4039;}
.jp-name-note{font-size:12.5px;color:#8a7e72;margin-top:2px;}
"""


def craft_page(c, all_crafts):
    cid, pref, cat = c['id'], c.get('prefecture', ''), c.get('category', '')
    name_en = c.get('name_en') or c.get('name')
    name_ja = c.get('name', '')
    pref_en = PREF_EN.get(pref, pref)
    cat_en = CATEGORY_EN.get(cat, cat)
    desc_en = str(c.get('desc_en') or '').strip()
    founded = str(c.get('founded') or '').strip()
    ja_url = f"{SITE}/craft/{pref}/{cid}.html"
    en_url = f"{SITE}/en/craft/{pref}/{cid}.html"
    meti = c.get('designation') == 'meti'

    meta_desc = (desc_en[:157] + '…') if len(desc_en) > 158 else desc_en

    techniques = [t for t in (c.get('techniques') or []) if str(t).strip()]
    materials = [m for m in (c.get('materials') or []) if str(m).strip()]
    workshops = [w for w in (c.get('workshops') or []) if isinstance(w, dict) and w.get('name')]

    # 地図（他ジャンルと同じOSM埋め込み。座標が無ければ出さない）
    map_box = ''
    lat, lng = c.get('lat'), c.get('lng')
    if lat and lng:
        try:
            la, ln = float(lat), float(lng)
            bbox = f"{ln-0.05}%2C{la-0.035}%2C{ln+0.05}%2C{la+0.035}"
            map_box = (f'<section class="info-section"><h2 class="section-title">Where it is made</h2>'
                       f'<div style="border:1px solid #e2d5c2;border-radius:8px;overflow:hidden;">'
                       f'<iframe title="Map of {esc(name_en)}" width="100%" height="280" frameborder="0" scrolling="no" loading="lazy" '
                       f'style="display:block;border:0;" src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&amp;layer=mapnik&amp;marker={la}%2C{ln}"></iframe>'
                       f'<div style="padding:8px 12px;background:#f4ede2;font-size:12px;text-align:right;">'
                       f'<a href="https://www.google.com/maps/search/?api=1&amp;query={la}%2C{ln}" target="_blank" rel="noopener" style="color:#8a5a2a;text-decoration:none;">Open in Google Maps →</a></div></div></section>')
        except (ValueError, TypeError):
            pass

    tech_html = ''
    if techniques or materials:
        chips_t = ''.join(f'<span class="term-chip">{esc(t)}</span>' for t in techniques)
        chips_m = ''.join(f'<span class="term-chip">{esc(m)}</span>' for m in materials)
        tech_html = f'''<section class="info-section">
  <h2 class="section-title">Techniques &amp; Materials</h2>
  <p style="font-size:13px;color:#8a7e72;">Craft terms are shown in the original Japanese — these are proper names with no standard English equivalents.</p>
  {f'<h3 style="font-size:14px;margin:14px 0 4px;">Techniques</h3><div class="terms-grid">{chips_t}</div>' if chips_t else ''}
  {f'<h3 style="font-size:14px;margin:14px 0 4px;">Materials</h3><div class="terms-grid">{chips_m}</div>' if chips_m else ''}
</section>'''

    ws_html = ''
    if workshops:
        rows = ''
        for w in workshops[:6]:
            exp = ' <span style="font-size:11px;background:#e8f0e4;color:#3a6a3a;border-radius:10px;padding:2px 8px;">hands-on experience</span>' if w.get('experience') else ''
            link = f'<a href="{esc(w["url"])}" target="_blank" rel="noopener">{esc(w["name"])}</a>' if w.get('url') else esc(w['name'])
            rows += f'<li style="margin:6px 0;font-size:14.5px;">{link}{exp}</li>'
        ws_html = f'''<section class="info-section">
  <h2 class="section-title">Where to see &amp; buy</h2>
  <p style="font-size:13px;color:#8a7e72;">Workshop names are in Japanese; links go to their official sites.</p>
  <ul style="list-style:none;padding:0;margin:8px 0 0;">{rows}</ul>
</section>'''

    related = [r for r in all_crafts if r.get('category') == cat and r.get('id') != cid][:4]
    rel_html = ''
    if related:
        cards = ''.join(
            f'<a href="/en/craft/{esc(r.get("prefecture"))}/{esc(r["id"])}.html" style="display:block;padding:14px 16px;border:1px solid #e2d5c2;border-radius:8px;text-decoration:none;">'
            f'<span style="display:block;font-size:14.5px;color:#2a2018;">{esc(r.get("name_en") or r.get("name"))}</span>'
            f'<span style="display:block;font-size:12px;color:#8a7e72;margin-top:2px;">{esc(PREF_EN.get(r.get("prefecture"), ""))}</span></a>'
            for r in related)
        rel_html = f'''<section class="info-section">
  <h2 class="section-title">More {esc(cat_en)}</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;">{cards}</div>
</section>'''

    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": f"{name_en} — Traditional craft of {pref_en}, Japan",
        "description": meta_desc, "mainEntityOfPage": en_url,
        "about": {"@type": "Thing", "name": name_en, "alternateName": name_ja},
    }, ensure_ascii=False).replace('</', '<\\/')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(name_en)} — Traditional Craft of {esc(pref_en)}, Japan | Terroir HUB CRAFT</title>
<meta name="description" content="{esc(meta_desc)}">
<link rel="canonical" href="{en_url}">
<link rel="alternate" hreflang="ja" href="{ja_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{ja_url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(name_en)} — Traditional Craft of {esc(pref_en)}, Japan">
<meta property="og:description" content="{esc(meta_desc)}">
<meta property="og:url" content="{en_url}">
<meta property="og:image" content="{SITE}/img/ogp.jpg">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{jsonld}</script>
<style>{CSS}{EXTRA_CSS}</style>
</head>
<body>
<nav class="en-nav">
  <a class="brand" href="/en/">Terroir HUB <span style="color:#8a5a2a;">CRAFT</span></a>
  <a href="/en/craft/">All crafts</a>
  <span class="lang"><a href="{ja_url}">日本語</a> / EN</span>
</nav>
<div class="craft-hero">
  <div class="hero-inner">
    <span class="hero-category">{esc(cat_en)}</span>
    <h1 class="hero-title">{esc(name_en)}</h1>
    <p class="hero-title-en">{esc(name_ja)}</p>
    <div class="hero-meta">
      <div class="hero-meta-item"><span class="meta-label">Region</span><span>{esc(pref_en)}{(' — ' + esc(c.get('area'))) if c.get('area') else ''}</span></div>
      {f'<div class="hero-meta-item"><span class="meta-label">Origins</span><span>c. {esc(founded)}</span></div>' if founded else ''}
      <div class="hero-meta-item"><span class="meta-label">Status</span><span>{'METI-designated Traditional Craft' if meti else 'Regional traditional craft'}</span></div>
    </div>
  </div>
</div>
<main class="craft-content">
  <section class="info-section">
    <h2 class="section-title">About {esc(name_en)}</h2>
    <p class="craft-desc" style="line-height:1.95;">{esc(desc_en)}</p>
  </section>
  {tech_html}
  {ws_html}
  {map_box}
  {rel_html}
</main>
<footer style="margin-top:64px;padding:32px 24px;text-align:center;font-size:12px;color:#8a7e72;border-top:1px solid #e8e0d4;">
  <a href="/en/" style="color:inherit;">Terroir HUB CRAFT</a> — FOMUS LLC
</footer>
</body>
</html>'''


def index_page(crafts):
    by_cat = {}
    for c in crafts:
        by_cat.setdefault(c.get('category', 'other'), []).append(c)
    blocks = ''
    order = ['ceramics', 'lacquerware', 'textiles', 'dyeing', 'metalwork', 'paper',
             'woodwork', 'dolls', 'buddhist', 'other']
    for cat in order:
        items = by_cat.get(cat)
        if not items:
            continue
        cards = ''.join(
            f'<a href="/en/craft/{esc(c.get("prefecture"))}/{esc(c["id"])}.html" style="display:block;padding:13px 15px;border:1px solid #e2d5c2;border-radius:8px;text-decoration:none;">'
            f'<span style="display:block;font-size:14.5px;color:#2a2018;">{esc(c.get("name_en") or c.get("name"))}</span>'
            f'<span style="display:block;font-size:12px;color:#8a7e72;margin-top:2px;">{esc(PREF_EN.get(c.get("prefecture"), ""))}</span></a>'
            for c in sorted(items, key=lambda x: str(x.get('name_en') or '')))
        blocks += (f'<section style="max-width:1080px;margin:0 auto;padding:22px 24px;">'
                   f'<h2 style="font-size:20px;border-bottom:1px solid #e2d5c2;padding-bottom:8px;">{esc(CATEGORY_EN.get(cat, cat))}'
                   f'<span style="font-size:12px;color:#8a7e72;margin-left:10px;">{len(items)}</span></h2>'
                   f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin-top:14px;">{cards}</div></section>')
    title = f"Traditional Crafts of Japan — {len(crafts)} METI-designated and regional crafts | Terroir HUB CRAFT"
    desc = f"Explore {len(crafts)} traditional Japanese crafts — ceramics, lacquerware, textiles, washi paper and more — with history, techniques and where to see them."
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/en/craft/">
<link rel="alternate" hreflang="ja" href="{SITE}/">
<link rel="alternate" hreflang="en" href="{SITE}/en/craft/">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/img/ogp.jpg"><meta name="twitter:card" content="summary">
<style>{EXTRA_CSS}
body{{font-family:'Helvetica Neue',Arial,'Hiragino Kaku Gothic ProN',sans-serif;margin:0;background:#fdfbf7;color:#2a2018;}}
.hd{{max-width:1080px;margin:0 auto;padding:40px 24px 6px;}}
.hd h1{{font-size:clamp(24px,4vw,36px);margin:0 0 8px;}}
.hd p{{color:#8a7e72;font-size:14.5px;margin:0;}}</style>
</head>
<body>
<nav class="en-nav">
  <a class="brand" href="/en/">Terroir HUB <span style="color:#8a5a2a;">CRAFT</span></a>
  <span class="lang"><a href="/">日本語</a> / EN</span>
</nav>
<div class="hd"><h1>Traditional Crafts of Japan</h1>
<p>{len(crafts)} crafts — ceramics, lacquerware, textiles, paper and more, with history, techniques and places to visit.</p></div>
{blocks}
<footer style="margin-top:64px;padding:32px 24px;text-align:center;font-size:12px;color:#8a7e72;border-top:1px solid #e8e0d4;">
  <a href="/en/" style="color:inherit;">Terroir HUB CRAFT</a> — FOMUS LLC
</footer>
</body>
</html>'''


def main():
    global CSS
    CSS = base_css()
    crafts = load_all()
    made = 0
    for c in crafts:
        out_dir = os.path.join(BASE, 'en', 'craft', c.get('prefecture', ''))
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, f"{c['id']}.html"), 'w', encoding='utf-8').write(craft_page(c, crafts))
        made += 1
    os.makedirs(os.path.join(BASE, 'en', 'craft'), exist_ok=True)
    open(os.path.join(BASE, 'en', 'craft', 'index.html'), 'w', encoding='utf-8').write(index_page(crafts))
    print(f'EN craft pages: {made} + index')


if __name__ == '__main__':
    main()
