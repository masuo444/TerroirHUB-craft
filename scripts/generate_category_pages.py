#!/usr/bin/env python3
"""Generate category listing pages for Terroir HUB CRAFT."""
import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://craft.terroirhub.com"

# Category metadata
CATEGORIES = {
    'ceramics': {
        'ja': '陶磁器',
        'en': 'Ceramics & Porcelain',
        'en_sub': 'CERAMICS & PORCELAIN',
        'icon': '🏺',
        'color': '#8B6F5E',
        'bg': '#f5ede8',
        'desc_ja': '土を素材に成形・焼成によって作られる器・壺・置物などの工芸品。九谷焼・有田焼・清水焼・信楽焼・備前焼など日本各地に個性豊かな産地が広がります。',
        'desc_en': 'Japanese ceramics encompass a rich tradition of pottery and porcelain produced across the country. From the colorful overglaze enamels of Kutani ware to the refined whiteness of Arita porcelain, each region has developed its own distinctive style.',
    },
    'lacquerware': {
        'ja': '漆器',
        'en': 'Lacquerware',
        'en_sub': 'LACQUERWARE',
        'icon': '🪔',
        'color': '#7A1F1F',
        'bg': '#f5e8e8',
        'desc_ja': '木地に漆を塗り重ねて仕上げる伝統工芸品。輪島塗・会津塗・越前漆器・琉球漆器など、産地ごとに異なる技法と意匠が発達しました。日本の漆器は世界的に「Japan」と呼ばれるほど高く評価されています。',
        'desc_en': 'Japanese lacquerware, known internationally as "Japan," represents one of the country\'s most refined craft traditions. Built up through layers of urushi lacquer over wooden forms, pieces from Wajima, Aizu, Echizen and other regions each carry a distinct regional identity.',
    },
    'textiles': {
        'ja': '織物',
        'en': 'Weaving & Textiles',
        'en_sub': 'WEAVING & TEXTILES',
        'icon': '🧵',
        'color': '#3D5A80',
        'bg': '#e8ecf5',
        'desc_ja': '糸を織り合わせて布を作る伝統工芸品。西陣織・博多織・結城紬・大島紬・琉球絣など、日本全国に約70品目が経産省に指定されており、工芸品の中で最も品目数の多いカテゴリです。',
        'desc_en': 'Japanese traditional textiles represent the largest category of designated crafts, with over 70 types recognized by the government. From the intricate brocades of Nishijin weaving in Kyoto to the distinctive kasuri patterns of Oshima Tsumugi from Amami Oshima, Japanese woven textiles span an extraordinary range of techniques.',
    },
    'dyeing': {
        'ja': '染色品',
        'en': 'Dyeing & Printing',
        'en_sub': 'DYEING & PRINTING',
        'icon': '🪭',
        'color': '#5C3A8A',
        'bg': '#ede8f5',
        'desc_ja': '布や糸に染料・顔料で文様を施す伝統工芸品。京友禅・江戸小紋・有松鳴海絞り・加賀友禅など、染めの技法は地域の美意識と深く結びついています。',
        'desc_en': 'Traditional Japanese dyeing crafts transform fabric through centuries-old techniques. Kyo-Yuzen from Kyoto, Edo Komon from Tokyo, Arimatsu Shibori tie-dye, and Kaga Yuzen each represent distinct regional approaches to pattern, color and resist-dyeing methods.',
    },
    'metalwork': {
        'ja': '金工品',
        'en': 'Metalwork',
        'en_sub': 'METALWORK',
        'icon': '⚒️',
        'color': '#4A4A4A',
        'bg': '#efefef',
        'desc_ja': '鉄・銅・金・銀などの金属を素材とした伝統工芸品。南部鉄器・高岡銅器・燕鎚起銅器・堺打刃物など、鍛造・鋳造・彫金などの技法で作られた器具・装飾品・刃物類が含まれます。',
        'desc_en': 'Japanese traditional metalwork encompasses casting, forging, and engraving across a range of metals. Nambu ironware from Iwate, Takaoka copperware from Toyama, Tsubame hammered copperware from Niigata, and Sakai cutlery from Osaka each exemplify different metalworking traditions.',
    },
    'paper': {
        'ja': '和紙',
        'en': 'Japanese Paper',
        'en_sub': 'JAPANESE PAPER',
        'icon': '📜',
        'color': '#5C7A4A',
        'bg': '#eef5e8',
        'desc_ja': '楮・三椏・雁皮などの植物繊維から手漉きで作られる日本の伝統的な紙。越前和紙・美濃和紙・石州半紙・土佐和紙など、ユネスコ無形文化遺産に登録されたものも含む、世界に誇る紙の文化です。',
        'desc_en': 'Washi, Japanese handmade paper, is crafted from plant fibers such as kozo, mitsumata and gampi. Echizen Washi, Mino Washi, Sekishu Banshi and Tosa Washi are among the finest examples — several are recognized on UNESCO\'s Intangible Cultural Heritage list.',
    },
    'woodwork': {
        'ja': '木竹工芸品',
        'en': 'Wood & Bamboo Crafts',
        'en_sub': 'WOOD & BAMBOO',
        'icon': '🌿',
        'color': '#5C7A4A',
        'bg': '#eef5e8',
        'desc_ja': '木材・竹・籐などを素材とした伝統工芸品。指物・挽物・曲物・建具・竹細工など多様な技法があり、日常の器具から美術工芸品まで幅広い品目が含まれます。',
        'desc_en': 'Japanese wood and bamboo crafts range from fine cabinet-making and woodturning to traditional basketry and lacquered woodwork. These crafts reflect a deep respect for natural materials and a centuries-old tradition of working with the grain and character of each piece of wood or bamboo.',
    },
    'dolls': {
        'ja': '人形・こけし',
        'en': 'Dolls & Kokeshi',
        'en_sub': 'DOLLS & KOKESHI',
        'icon': '🎎',
        'color': '#8A4A6E',
        'bg': '#f5e8ef',
        'desc_ja': '伝統的な技法で作られた人形・こけしなどの工芸品。江戸木目込人形・博多人形・鴻巣雛人形・東北こけしなど、日本各地の風土と文化を反映した独自の人形文化が花開いています。',
        'desc_en': 'Japanese traditional dolls reflect the country\'s rich festival culture and folk art heritage. From the intricate brocade-dressed Edo Kimekomi dolls to the simple turned-wood Kokeshi from Tohoku, each type carries deep cultural meaning and regional identity.',
    },
    'buddhist': {
        'ja': '仏壇・仏具',
        'en': 'Buddhist Altars & Implements',
        'en_sub': 'BUDDHIST CRAFTS',
        'icon': '🕯️',
        'color': '#7A6020',
        'bg': '#f5f0e0',
        'desc_ja': '仏壇・位牌・仏具などの宗教的工芸品。京仏壇・金沢仏壇・名古屋仏壇・岩槻仏壇など、漆・金箔・金具・木彫りなど多様な技術が集結した総合工芸の粋です。',
        'desc_en': 'Japanese Buddhist altar crafts represent a convergence of multiple traditional crafts — lacquerwork, gold leaf application, metalwork, woodcarving and textile weaving — all combined in a single devotional object. Kyoto, Kanazawa and Nagoya are among the most prominent centers for this tradition.',
    },
    'other': {
        'ja': 'その他工芸品',
        'en': 'Other Traditional Crafts',
        'en_sub': 'OTHER CRAFTS',
        'icon': '✨',
        'color': '#2E5E4E',
        'bg': '#e8f0ec',
        'desc_ja': '扇子・提灯・硝子・組紐・べっ甲細工・石工品など、上記カテゴリに分類されない多様な伝統工芸品。それぞれに独自の技法と長い歴史を持つ、日本の生活文化を彩る品々です。',
        'desc_en': 'Japan\'s traditional craft heritage encompasses many items beyond the major categories — from Edo Kiriko cut glass and intricate kumihimo braided cords to tortoiseshell work, stone crafts, and elaborate folding fans. Each carries its own deep tradition and regional identity.',
    },
}

CAT_JA = {k: v['ja'] for k, v in CATEGORIES.items()}
CAT_ICON = {k: v['icon'] for k, v in CATEGORIES.items()}
UNESCO_IDS = {'yuki_tsumugi', 'echizen_washi', 'mino_washi', 'sekishu_banshi', 'hosokawa_kami'}

NAV = '''<nav>
  <a href="/" class="nav-logo">Terroir HUB<span>CRAFT</span></a>
  <div class="nav-links">
    <a href="/craft/search/">工芸品検索</a>
    <a href="/craft/category/" class="active">カテゴリ</a>
    <a href="/craft/region/">産地から探す</a>
    <a href="/craft/map/">地図で探す</a>
    <a href="/craft/plans/">プラン</a>
  </div>
  <div class="nav-right">
    <button class="hamburger" onclick="openMM()" aria-label="メニュー"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="menu-overlay" id="mmOverlay" onclick="closeMM()"></div>
<div class="mobile-menu" id="mobileMenu">
  <button class="mm-close" onclick="closeMM()">✕</button>
  <a href="/craft/search/" onclick="closeMM()">🔍 工芸品検索</a>
  <a href="/craft/category/" onclick="closeMM()">🏺 カテゴリ一覧</a>
  <a href="/craft/region/" onclick="closeMM()">📍 産地から探す</a>
  <a href="/craft/map/" onclick="closeMM()">🗾 地図で探す</a>
  <a href="/craft/plans/" onclick="closeMM()">⭐ プラン</a>
</div>'''

FOOTER = '''<footer>
  <div class="footer-inner">
    <div class="footer-bottom">
      <span>© 2026 合同会社FOMUS / Terroir HUB CRAFT</span>
      <div class="footer-bottom-links">
        <a href="/privacy/">プライバシーポリシー</a>
        <a href="/terms/">利用規約</a>
        <a href="/craft/plans/">料金プラン</a>
      </div>
    </div>
  </div>
</footer>
<script>
function openMM(){document.getElementById('mobileMenu').classList.add('open');document.getElementById('mmOverlay').classList.add('open')}
function closeMM(){document.getElementById('mobileMenu').classList.remove('open');document.getElementById('mmOverlay').classList.remove('open')}
</script>'''

BASE_CSS = '''<style>
:root{
  --bg:#FAF8F5;--bg2:#F3EDE6;--accent:#2E5E4E;--accent2:#C4A265;
  --accent-light:#EAF2EE;--accent-gold:#E8C97A;--text:#1A1A18;
  --text2:#5C5A56;--text3:#8A8880;--border:#E8E0D6;
  --nav-h:56px;--radius:12px;
  --shadow:0 2px 16px rgba(46,94,78,.10);--shadow-lg:0 8px 40px rgba(46,94,78,.16);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans JP','Inter',sans-serif;font-size:15px;line-height:1.7;-webkit-font-smoothing:antialiased}
nav{position:fixed;top:0;left:0;right:0;height:var(--nav-h);background:rgba(250,248,245,.94);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:1000;display:flex;align-items:center;padding:0 24px;gap:24px}
.nav-logo{font-family:'Shippori Mincho',serif;font-size:17px;font-weight:700;color:var(--accent);letter-spacing:.05em;text-decoration:none;white-space:nowrap}
.nav-logo span{color:var(--accent2);font-size:11px;letter-spacing:.12em;display:block;font-family:'Inter',sans-serif;font-weight:600;text-transform:uppercase}
.nav-links{display:flex;align-items:center;gap:20px;margin-left:8px}
.nav-links a{color:var(--text2);text-decoration:none;font-size:13px;font-weight:500;transition:color .2s;white-space:nowrap}
.nav-links a:hover,.nav-links a.active{color:var(--accent)}
.nav-right{margin-left:auto}
.hamburger{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:4px}
.hamburger span{width:22px;height:2px;background:var(--text);border-radius:2px}
.mobile-menu{position:fixed;top:0;right:-100%;width:280px;height:100dvh;background:var(--bg);border-left:1px solid var(--border);z-index:2000;transition:right .3s ease;padding:80px 24px 32px;display:flex;flex-direction:column;gap:16px}
.mobile-menu.open{right:0}
.mobile-menu a{color:var(--text);text-decoration:none;font-size:16px;font-weight:500;padding:12px 0;border-bottom:1px solid var(--border)}
.menu-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:1999}
.menu-overlay.open{display:block}
.mm-close{position:absolute;top:16px;right:16px;background:none;border:none;font-size:24px;cursor:pointer;color:var(--text2)}
.breadcrumb{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text3);margin-bottom:16px;flex-wrap:wrap}
.breadcrumb a{color:var(--text3);text-decoration:none;transition:color .2s}
.breadcrumb a:hover{color:var(--accent)}
.breadcrumb-sep{color:var(--border)}
.craft-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.craft-card{background:#fff;border-radius:var(--radius);overflow:hidden;border:1px solid var(--border);transition:all .25s;text-decoration:none;display:block}
.craft-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg)}
.craft-card-img{aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;font-size:48px;position:relative}
.craft-card-badge{position:absolute;top:12px;left:12px;background:var(--accent);color:#fff;font-size:10px;font-weight:700;letter-spacing:.08em;padding:3px 8px;border-radius:4px;font-family:'Inter',sans-serif;text-transform:uppercase}
.craft-card-badge.regional{background:#5C7A8A}
.craft-card-badge.unesco{background:#7B4F9E}
.craft-card-body{padding:20px}
.craft-card-pref{font-size:11px;color:var(--accent2);font-weight:600;letter-spacing:.08em;font-family:'Inter',sans-serif;margin-bottom:6px}
.craft-card-name{font-family:'Shippori Mincho',serif;font-size:20px;font-weight:700;margin-bottom:4px;color:var(--text)}
.craft-card-name-en{font-size:12px;color:var(--text3);font-family:'Inter',sans-serif;margin-bottom:10px}
.craft-card-area{font-size:12px;color:var(--text2)}
.craft-card-area::before{content:'📍';font-size:11px;margin-right:4px}
.craft-card-desc{font-size:13px;color:var(--text2);line-height:1.7;margin-top:10px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
footer{background:#1a1a18;color:rgba(255,255,255,.5);padding:40px 24px 24px;font-size:13px}
.footer-inner{max-width:1200px;margin:0 auto}
.footer-bottom{border-top:1px solid rgba(255,255,255,.08);padding-top:20px;display:flex;justify-content:space-between;align-items:center;font-size:12px;flex-wrap:wrap;gap:12px}
.footer-bottom-links{display:flex;gap:16px}
.footer-bottom-links a{color:rgba(255,255,255,.35);text-decoration:none;transition:color .2s}
.footer-bottom-links a:hover{color:rgba(255,255,255,.7)}
@media(max-width:900px){.nav-links{display:none}.hamburger{display:flex}.craft-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.craft-grid{grid-template-columns:1fr}.footer-bottom{flex-direction:column;text-align:center}}
</style>'''


def get_pref_from_area(area):
    """Extract prefecture display name from area string."""
    return area.split('・')[0] if area else ''


def build_category_page(cat_key, crafts, cat_info):
    count = len(crafts)
    sample_names = '・'.join(c['name'] for c in crafts[:5])
    title = f"{cat_info['ja']} — {sample_names} | Terroir HUB CRAFT"
    desc_ja = f"経産省指定の伝統的工芸品・{cat_info['ja']}{count}品目を網羅。{sample_names}など、日本各地の{cat_info['ja']}の産地・歴史・技法・体験情報。"
    canonical = f"{BASE_URL}/craft/category/{cat_key}/"

    # JSON-LD items
    items_ld = []
    for i, c in enumerate(crafts):
        pref = c.get('prefecture', '')
        url = f"{BASE_URL}/craft/{pref}/{c['id']}.html" if pref else f"{BASE_URL}/craft/{c['id']}.html"
        items_ld.append(
            f'    {{"@type":"ListItem","position":{i+1},"name":"{c["name"]}","url":"{url}"}}'
        )

    # Craft cards
    cards_html = []
    for c in crafts:
        pref = c.get('prefecture', '')
        url = f"/craft/{pref}/{c['id']}.html" if pref else f"/craft/{c['id']}.html"
        is_unesco = c['id'] in UNESCO_IDS
        designation = c.get('designation', 'meti')
        if is_unesco:
            badge = '<span class="craft-card-badge unesco">UNESCO</span>'
        elif designation == 'regional':
            badge = '<span class="craft-card-badge regional">地域指定</span>'
        else:
            badge = '<span class="craft-card-badge">国指定</span>'
        desc_short = (c.get('desc', '') or '')[:90]
        area = c.get('area', '')
        cards_html.append(f'''<a class="craft-card" href="{url}">
      <div class="craft-card-img" style="background:{cat_info['bg']}">{cat_info['icon']}{badge}</div>
      <div class="craft-card-body">
        <div class="craft-card-pref">{area}</div>
        <div class="craft-card-name">{c['name']}</div>
        <div class="craft-card-name-en">{c.get('name_en', '')}</div>
        <p class="craft-card-desc">{desc_short}</p>
      </div>
    </a>''')

    # Other category links
    other_cats = []
    for k, v in CATEGORIES.items():
        if k != cat_key:
            other_cats.append(
                f'<a href="/craft/category/{k}/" class="sibling-cat">'
                f'<span class="sibling-icon">{v["icon"]}</span>'
                f'<span class="sibling-name">{v["ja"]}</span>'
                f'</a>'
            )

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc_ja}">
<meta name="description" lang="en" content="{cat_info['desc_en'][:160]}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="ja" href="{canonical}">
<link rel="alternate" hreflang="en" href="{BASE_URL}/en/category/{cat_key}/">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{cat_info['ja']} ({cat_info['en']}) | Terroir HUB CRAFT">
<meta property="og:description" content="{desc_ja}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}/img/ogp.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type":"ListItem","position":1,"name":"Terroir HUB CRAFT","item":"{BASE_URL}/"}},
    {{"@type":"ListItem","position":2,"name":"カテゴリ","item":"{BASE_URL}/craft/category/"}},
    {{"@type":"ListItem","position":3,"name":"{cat_info['ja']}","item":"{canonical}"}}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "{cat_info['ja']} — Japanese {cat_info['en']}",
  "description": "{cat_info['desc_en'][:200]}",
  "url": "{canonical}",
  "numberOfItems": {count},
  "about": {{
    "@type": "Thing",
    "name": "Japanese Traditional Crafts — {cat_info['en']}",
    "sameAs": "https://en.wikipedia.org/wiki/Japanese_crafts"
  }},
  "mainEntity": {{
    "@type": "ItemList",
    "numberOfItems": {count},
    "itemListElement": [
{chr(10).join(items_ld)}
    ]
  }}
}}
</script>
{BASE_CSS}
<style>
.page-header{{padding-top:calc(var(--nav-h) + 48px);padding-bottom:48px;padding-left:24px;padding-right:24px;background:linear-gradient(135deg,{cat_info['bg']},{cat_info['bg']}cc,#f0ebe3)}}
.page-header-inner{{max-width:1200px;margin:0 auto}}
.page-header-label{{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}}
.cat-hero{{display:flex;align-items:flex-start;gap:32px;flex-wrap:wrap}}
.cat-icon-big{{font-size:72px;flex-shrink:0;line-height:1}}
.cat-hero-text h1{{font-family:'Shippori Mincho',serif;font-size:clamp(28px,4vw,44px);font-weight:700;margin-bottom:6px}}
.cat-en-label{{font-family:'Inter',sans-serif;font-size:14px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--accent2);margin-bottom:12px;display:block}}
.cat-count-badge{{display:inline-block;background:var(--accent);color:#fff;font-size:13px;font-weight:700;padding:4px 14px;border-radius:20px;margin-bottom:16px}}
.cat-desc{{color:var(--text2);font-size:14px;max-width:620px;line-height:1.8;margin-bottom:10px}}
.cat-desc-en{{color:var(--text3);font-size:13px;max-width:620px;line-height:1.7;font-style:italic}}
.content-wrap{{max-width:1200px;margin:0 auto;padding:48px 24px 80px}}
.sibling-cats{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:48px}}
.sibling-cats-label{{font-size:12px;color:var(--text3);font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px}}
.sibling-cat{{display:flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--border);border-radius:20px;padding:6px 14px;text-decoration:none;font-size:13px;color:var(--text2);transition:all .2s}}
.sibling-cat:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}}
.sibling-icon{{font-size:16px}}
.sibling-name{{font-weight:500}}
</style>
</head>
<body>
{NAV}

<div class="page-header">
  <div class="page-header-inner">
    <nav class="breadcrumb" aria-label="パンくずリスト">
      <a href="/">トップ</a><span class="breadcrumb-sep">›</span>
      <a href="/craft/category/">カテゴリ</a><span class="breadcrumb-sep">›</span>
      <span>{cat_info['ja']}</span>
    </nav>
    <div class="cat-hero">
      <div class="cat-icon-big">{cat_info['icon']}</div>
      <div class="cat-hero-text">
        <span class="cat-en-label">{cat_info['en_sub']}</span>
        <h1>{cat_info['ja']}</h1>
        <span class="cat-count-badge">{count}品目</span>
        <p class="cat-desc">{cat_info['desc_ja']}</p>
        <p class="cat-desc-en">{cat_info['desc_en']}</p>
      </div>
    </div>
  </div>
</div>

<div class="content-wrap">
  <div class="sibling-cats-label">他のカテゴリ</div>
  <div class="sibling-cats">
    {''.join(other_cats)}
  </div>

  <div class="craft-grid">
    {''.join(cards_html)}
  </div>
</div>

{FOOTER}
</body>
</html>'''


def build_category_index(cat_craft_map):
    total = sum(len(v) for v in cat_craft_map.values())

    cards_html = []
    for cat_key, info in CATEGORIES.items():
        crafts = cat_craft_map.get(cat_key, [])
        count = len(crafts)
        sample = '・'.join(c['name'] for c in crafts[:5])
        cards_html.append(f'''<a class="cat-card" href="/craft/category/{cat_key}/">
      <div class="cat-card-icon">{info['icon']}</div>
      <div class="cat-card-body">
        <div class="cat-card-en">{info['en_sub']}</div>
        <div class="cat-card-name">{info['ja']}</div>
        <div class="cat-card-count">約{count}品目</div>
        <div class="cat-card-sample">{sample}</div>
      </div>
      <span class="cat-card-arrow">→</span>
    </a>''')

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>カテゴリ一覧 — 伝統工芸品を種類から探す | Terroir HUB CRAFT</title>
<meta name="description" content="経産省が定める10分類から日本の伝統工芸品を探せます。陶磁器・漆器・織物・染色品・金工品・和紙・木竹工芸品・人形・仏壇仏具など{total}品目を網羅。">
<link rel="canonical" href="{BASE_URL}/craft/category/">
<link rel="alternate" hreflang="ja" href="{BASE_URL}/craft/category/">
<link rel="alternate" hreflang="en" href="{BASE_URL}/en/category/">
<meta property="og:type" content="website">
<meta property="og:title" content="カテゴリから探す — 日本の伝統工芸品 | Terroir HUB CRAFT">
<meta property="og:description" content="陶磁器・漆器・織物・染色品・金工品など10カテゴリ{total}品目の伝統工芸品データベース。">
<meta property="og:url" content="{BASE_URL}/craft/category/">
<meta property="og:image" content="{BASE_URL}/img/ogp.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Japanese Traditional Crafts by Category",
  "description": "Browse {total} Japanese traditional crafts across 10 categories including ceramics, lacquerware, textiles, metalwork, and more.",
  "url": "{BASE_URL}/craft/category/",
  "about": {{"@type":"Thing","name":"Japanese Traditional Crafts"}}
}}
</script>
{BASE_CSS}
<style>
.page-header{{padding-top:calc(var(--nav-h) + 48px);padding-bottom:48px;padding-left:24px;padding-right:24px;background:linear-gradient(135deg,#e8f0ec,#f0ebe3)}}
.page-header-inner{{max-width:1200px;margin:0 auto}}
.page-header-label{{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}}
.page-header h1{{font-family:'Shippori Mincho',serif;font-size:clamp(28px,4vw,40px);font-weight:700;margin-bottom:10px}}
.page-header p{{color:var(--text2);font-size:15px;max-width:600px}}
.content-wrap{{max-width:1200px;margin:0 auto;padding:48px 24px 80px}}
.cat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.cat-card{{background:#fff;border:1.5px solid var(--border);border-radius:16px;padding:28px 24px;text-decoration:none;display:flex;align-items:flex-start;gap:16px;transition:all .25s;position:relative}}
.cat-card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg);border-color:var(--accent-light)}}
.cat-card-icon{{font-size:40px;flex-shrink:0;line-height:1}}
.cat-card-body{{flex:1;min-width:0}}
.cat-card-en{{font-family:'Inter',sans-serif;font-size:10px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--accent2);margin-bottom:4px}}
.cat-card-name{{font-family:'Shippori Mincho',serif;font-size:22px;font-weight:700;color:var(--text);margin-bottom:4px}}
.cat-card-count{{font-size:12px;color:var(--accent);font-weight:600;margin-bottom:8px}}
.cat-card-sample{{font-size:12px;color:var(--text3);line-height:1.6}}
.cat-card-arrow{{position:absolute;bottom:20px;right:20px;color:var(--accent2);font-size:18px;transition:transform .2s}}
.cat-card:hover .cat-card-arrow{{transform:translateX(4px)}}
.stats-bar{{display:flex;gap:40px;background:var(--accent);border-radius:var(--radius);padding:20px 28px;margin-bottom:40px;flex-wrap:wrap}}
.stat-item{{text-align:center}}
.stat-num{{font-family:'Shippori Mincho',serif;font-size:32px;font-weight:700;color:#fff;display:block}}
.stat-label{{font-size:12px;color:rgba(255,255,255,.7)}}
@media(max-width:900px){{.cat-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:480px){{.cat-grid{{grid-template-columns:1fr}}.stats-bar{{gap:20px}}}}
</style>
</head>
<body>
{NAV}

<div class="page-header">
  <div class="page-header-inner">
    <nav class="breadcrumb" aria-label="パンくずリスト">
      <a href="/">トップ</a><span class="breadcrumb-sep">›</span>
      <span>カテゴリ</span>
    </nav>
    <p class="page-header-label">Categories</p>
    <h1>カテゴリから探す</h1>
    <p>経産省が定める分類から、お気に入りの伝統工芸ジャンルを選んでください。</p>
  </div>
</div>

<div class="content-wrap">
  <div class="stats-bar">
    <div class="stat-item"><span class="stat-num">10</span><div class="stat-label">カテゴリ</div></div>
    <div class="stat-item"><span class="stat-num">{total}</span><div class="stat-label">品目</div></div>
    <div class="stat-item"><span class="stat-num">208</span><div class="stat-label">経産省指定</div></div>
    <div class="stat-item"><span class="stat-num">37</span><div class="stat-label">地域指定</div></div>
  </div>
  <div class="cat-grid">
    {''.join(cards_html)}
  </div>
</div>

{FOOTER}
</body>
</html>'''


def main():
    # Load all craft data grouped by category
    data_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*.json')))
    cat_craft_map = {}
    for filepath in data_files:
        with open(filepath, encoding='utf-8') as f:
            crafts = json.load(f)
        for craft in crafts:
            cat = craft.get('category', '')
            if cat:
                cat_craft_map.setdefault(cat, []).append(craft)

    # Sort each category's crafts alphabetically by name
    for cat in cat_craft_map:
        cat_craft_map[cat].sort(key=lambda c: c.get('name', ''))

    count = 0
    for cat_key, cat_info in CATEGORIES.items():
        crafts = cat_craft_map.get(cat_key, [])
        if not crafts:
            print(f'  SKIP {cat_key} — no crafts found')
            continue

        out_dir = os.path.join(BASE, 'craft', 'category', cat_key)
        os.makedirs(out_dir, exist_ok=True)
        html = build_category_page(cat_key, crafts, cat_info)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✓ category/{cat_key}/index.html — {cat_info["ja"]} ({len(crafts)}品目)')
        count += 1

    # Category index
    index_dir = os.path.join(BASE, 'craft', 'category')
    os.makedirs(index_dir, exist_ok=True)
    index_html = build_category_index(cat_craft_map)
    with open(os.path.join(index_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f'  ✓ category/index.html')

    print(f'\n=== Done ===')
    print(f'Generated: {count} category pages + 1 index')
    total = sum(len(v) for v in cat_craft_map.values())
    print(f'Total crafts indexed: {total}')


if __name__ == '__main__':
    main()
