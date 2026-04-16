#!/usr/bin/env python3
"""Generate prefecture-level craft listing pages for Terroir HUB CRAFT."""
import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://craft.terroirhub.com"

PREF_JA = {
    'hokkaido':'北海道','aomori':'青森県','iwate':'岩手県','miyagi':'宮城県',
    'akita':'秋田県','yamagata':'山形県','fukushima':'福島県','ibaraki':'茨城県',
    'tochigi':'栃木県','gunma':'群馬県','saitama':'埼玉県','chiba':'千葉県',
    'tokyo':'東京都','kanagawa':'神奈川県','niigata':'新潟県','toyama':'富山県',
    'ishikawa':'石川県','fukui':'福井県','yamanashi':'山梨県','nagano':'長野県',
    'shizuoka':'静岡県','aichi':'愛知県','mie':'三重県','shiga':'滋賀県',
    'kyoto':'京都府','osaka':'大阪府','hyogo':'兵庫県','nara':'奈良県',
    'wakayama':'和歌山県','tottori':'鳥取県','shimane':'島根県','okayama':'岡山県',
    'hiroshima':'広島県','yamaguchi':'山口県','tokushima':'徳島県','kagawa':'香川県',
    'ehime':'愛媛県','kochi':'高知県','fukuoka':'福岡県','saga':'佐賀県',
    'nagasaki':'長崎県','kumamoto':'熊本県','oita':'大分県','miyazaki':'宮崎県',
    'kagoshima':'鹿児島県','okinawa':'沖縄県','gifu':'岐阜県'
}
PREF_EN = {
    'hokkaido':'Hokkaido','aomori':'Aomori','iwate':'Iwate','miyagi':'Miyagi',
    'akita':'Akita','yamagata':'Yamagata','fukushima':'Fukushima','ibaraki':'Ibaraki',
    'tochigi':'Tochigi','gunma':'Gunma','saitama':'Saitama','chiba':'Chiba',
    'tokyo':'Tokyo','kanagawa':'Kanagawa','niigata':'Niigata','toyama':'Toyama',
    'ishikawa':'Ishikawa','fukui':'Fukui','yamanashi':'Yamanashi','nagano':'Nagano',
    'shizuoka':'Shizuoka','aichi':'Aichi','mie':'Mie','shiga':'Shiga',
    'kyoto':'Kyoto','osaka':'Osaka','hyogo':'Hyogo','nara':'Nara',
    'wakayama':'Wakayama','tottori':'Tottori','shimane':'Shimane','okayama':'Okayama',
    'hiroshima':'Hiroshima','yamaguchi':'Yamaguchi','tokushima':'Tokushima','kagawa':'Kagawa',
    'ehime':'Ehime','kochi':'Kochi','fukuoka':'Fukuoka','saga':'Saga',
    'nagasaki':'Nagasaki','kumamoto':'Kumamoto','oita':'Oita','miyazaki':'Miyazaki',
    'kagoshima':'Kagoshima','okinawa':'Okinawa','gifu':'Gifu'
}
REGIONS = {
    '北海道・東北': ['hokkaido','aomori','iwate','miyagi','akita','yamagata','fukushima'],
    '関東': ['ibaraki','tochigi','gunma','saitama','chiba','tokyo','kanagawa'],
    '中部・北陸': ['niigata','toyama','ishikawa','fukui','yamanashi','nagano','gifu','shizuoka','aichi'],
    '近畿': ['mie','shiga','kyoto','osaka','hyogo','nara','wakayama'],
    '中国・四国': ['tottori','shimane','okayama','hiroshima','yamaguchi','tokushima','kagawa','ehime','kochi'],
    '九州・沖縄': ['fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima','okinawa'],
}
CAT_ICON = {
    'ceramics':'🏺','lacquerware':'🪔','textiles':'🧵','dyeing':'🪭',
    'metalwork':'⚒️','paper':'📜','woodwork':'🌿','dolls':'🎎','buddhist':'🕯️','other':'✨'
}
CAT_JA = {
    'ceramics':'陶磁器','lacquerware':'漆器','textiles':'織物','dyeing':'染色品',
    'metalwork':'金工品','paper':'和紙','woodwork':'木竹工芸品','dolls':'人形・こけし',
    'buddhist':'仏壇・仏具','other':'その他工芸品'
}
UNESCO_IDS = {'yuki_tsumugi','echizen_washi','mino_washi','sekishu_banshi','hosokawa_kami'}

NAV = '''<nav>
  <a href="/" class="nav-logo">Terroir HUB<span>CRAFT</span></a>
  <div class="nav-links">
    <a href="/craft/search/">工芸品検索</a>
    <a href="/craft/category/">カテゴリ</a>
    <a href="/craft/region/" class="active">産地から探す</a>
    <a href="/craft/map/">地図で探す</a>
    <a href="/craft/plans/">プラン</a>
  </div>
  <div class="nav-right">
    <button class="auth-btn">ログイン</button>
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
  <a href="https://terroirhub.com">Terroir HUB TOP</a>
</div>'''

FOOTER = '''<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div>
        <div class="footer-brand">Terroir HUB<br>CRAFT</div>
        <div class="footer-brand-en">Traditional Crafts of Japan</div>
        <p class="footer-desc">経産省指定240品目以上の伝統的工芸品を網羅したデータベースメディア。</p>
      </div>
      <div class="footer-links">
        <div class="footer-col">
          <h4>探す</h4>
          <a href="/craft/search/">工芸品検索</a>
          <a href="/craft/category/">カテゴリ一覧</a>
          <a href="/craft/region/">産地から探す</a>
          <a href="/craft/map/">地図で探す</a>
        </div>
        <div class="footer-col">
          <h4>学ぶ</h4>
          <a href="/craft/guide/">工芸の教科書</a>
          <a href="/craft/guide/history/">歴史と文化</a>
          <a href="/craft/guide/techniques/">技法図鑑</a>
        </div>
        <div class="footer-col">
          <h4>Terroir HUB</h4>
          <a href="https://terroirhub.com">トップページ</a>
          <a href="https://sake.terroirhub.com">日本酒</a>
          <a href="https://shochu.terroirhub.com">焼酎・泡盛</a>
          <a href="/craft/plans/">プラン</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 合同会社FOMUS / Terroir HUB CRAFT</span>
      <div style="display:flex;gap:16px">
        <a href="/privacy/" style="color:rgba(255,255,255,.35);text-decoration:none">プライバシーポリシー</a>
        <a href="/terms/" style="color:rgba(255,255,255,.35);text-decoration:none">利用規約</a>
      </div>
    </div>
  </div>
</footer>
<script>
function openMM(){document.getElementById('mobileMenu').classList.add('open');document.getElementById('mmOverlay').classList.add('open')}
function closeMM(){document.getElementById('mobileMenu').classList.remove('open');document.getElementById('mmOverlay').classList.remove('open')}
</script>'''

CSS = '''<style>
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
.nav-right{margin-left:auto;display:flex;align-items:center;gap:12px}
.auth-btn{background:var(--accent);color:#fff;border:none;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;font-family:'Noto Sans JP',sans-serif;transition:all .2s}
.auth-btn:hover{background:#245048}
.hamburger{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:4px}
.hamburger span{width:22px;height:2px;background:var(--text);border-radius:2px;transition:all .3s}
.mobile-menu{position:fixed;top:0;right:-100%;width:280px;height:100dvh;background:var(--bg);border-left:1px solid var(--border);z-index:2000;transition:right .3s ease;padding:80px 24px 32px;display:flex;flex-direction:column;gap:16px}
.mobile-menu.open{right:0}
.mobile-menu a{color:var(--text);text-decoration:none;font-size:16px;font-weight:500;padding:12px 0;border-bottom:1px solid var(--border)}
.menu-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:1999}
.menu-overlay.open{display:block}
.mm-close{position:absolute;top:16px;right:16px;background:none;border:none;font-size:24px;cursor:pointer;color:var(--text2)}
.page-header{padding-top:calc(var(--nav-h) + 48px);padding-bottom:48px;padding-left:24px;padding-right:24px;background:linear-gradient(135deg,#e8f0ec,#f0ebe3)}
.page-header-inner{max-width:1200px;margin:0 auto}
.breadcrumb{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text3);margin-bottom:16px;flex-wrap:wrap}
.breadcrumb a{color:var(--text3);text-decoration:none;transition:color .2s}
.breadcrumb a:hover{color:var(--accent)}
.breadcrumb-sep{color:var(--border)}
.page-header-label{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
.page-header h1{font-family:'Shippori Mincho',serif;font-size:clamp(28px,4vw,44px);font-weight:700;margin-bottom:10px;line-height:1.3}
.page-header-meta{display:flex;align-items:center;gap:16px;margin-top:12px;flex-wrap:wrap}
.page-header-count{background:var(--accent);color:#fff;font-size:13px;font-weight:700;padding:4px 14px;border-radius:20px}
.page-header p{color:var(--text2);font-size:15px;margin-top:8px;max-width:600px}
.content-wrap{max-width:1200px;margin:0 auto;padding:48px 24px 80px}
.craft-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.craft-card{background:#fff;border-radius:var(--radius);overflow:hidden;border:1px solid var(--border);transition:all .25s;text-decoration:none;display:block}
.craft-card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg)}
.craft-card-img{aspect-ratio:4/3;background:linear-gradient(135deg,var(--accent-light),#f0e8d8);display:flex;align-items:center;justify-content:center;font-size:48px;position:relative}
.craft-card-badge{position:absolute;top:12px;left:12px;background:var(--accent);color:#fff;font-size:10px;font-weight:700;letter-spacing:.08em;padding:3px 8px;border-radius:4px;font-family:'Inter',sans-serif;text-transform:uppercase}
.craft-card-badge.unesco{background:#7B4F9E}
.craft-card-body{padding:20px}
.craft-card-cat{font-size:11px;color:var(--accent2);font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-family:'Inter',sans-serif;margin-bottom:6px}
.craft-card-name{font-family:'Shippori Mincho',serif;font-size:20px;font-weight:700;margin-bottom:4px;color:var(--text)}
.craft-card-name-en{font-size:12px;color:var(--text3);font-family:'Inter',sans-serif;margin-bottom:10px}
.craft-card-area{font-size:12px;color:var(--text2)}
.craft-card-area::before{content:'📍';font-size:11px;margin-right:4px}
.craft-card-desc{font-size:13px;color:var(--text2);line-height:1.7;margin-top:10px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
footer{background:#1a1a18;color:rgba(255,255,255,.5);padding:40px 24px 24px;font-size:13px;margin-top:80px}
.footer-inner{max-width:1200px;margin:0 auto}
.footer-top{display:grid;grid-template-columns:1fr 2fr;gap:48px;margin-bottom:40px}
.footer-brand{font-family:'Shippori Mincho',serif;font-size:20px;font-weight:700;color:#fff;margin-bottom:8px}
.footer-brand-en{font-size:11px;letter-spacing:.15em;color:var(--accent-gold);font-family:'Inter',sans-serif;text-transform:uppercase}
.footer-desc{font-size:13px;color:rgba(255,255,255,.45);margin-top:12px;line-height:1.7}
.footer-links{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.footer-col h4{color:#fff;font-size:13px;font-weight:600;margin-bottom:12px}
.footer-col a{display:block;color:rgba(255,255,255,.45);text-decoration:none;font-size:12px;margin-bottom:8px;transition:color .2s}
.footer-col a:hover{color:rgba(255,255,255,.9)}
.footer-bottom{border-top:1px solid rgba(255,255,255,.08);padding-top:20px;display:flex;justify-content:space-between;align-items:center;font-size:12px}
@media(max-width:900px){
  .nav-links{display:none}.hamburger{display:flex}
  .craft-grid{grid-template-columns:repeat(2,1fr)}
  .footer-top{grid-template-columns:1fr}.footer-links{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:600px){
  .craft-grid{grid-template-columns:1fr}
  .content-wrap{padding:32px 16px 60px}
  .footer-links{grid-template-columns:1fr}
  .footer-bottom{flex-direction:column;gap:12px;text-align:center}
}
</style>'''

def build_pref_page(pref, crafts_in_pref):
    pref_ja = PREF_JA.get(pref, pref)
    pref_en = PREF_EN.get(pref, pref.capitalize())
    count = len(crafts_in_pref)
    craft_names = [c['name'] for c in crafts_in_pref[:4]]
    title_crafts = '・'.join(craft_names)

    title = f"{pref_ja}の伝統的工芸品 — {title_crafts} | Terroir HUB CRAFT"
    desc = f"{pref_ja}の経産省指定伝統的工芸品{count}品目を網羅。{title_crafts}など{pref_ja}を代表する工芸品の産地・技法・体験情報。"
    canonical = f"{BASE_URL}/craft/region/{pref}/"

    # JSON-LD
    items_ld = []
    for i, c in enumerate(crafts_in_pref):
        items_ld.append(f'''    {{"@type":"ListItem","position":{i+1},"name":"{c['name']}","url":"{BASE_URL}/craft/{pref}/{c['id']}.html"}}''')

    cards_html = []
    for c in crafts_in_pref:
        icon = CAT_ICON.get(c.get('category',''), '🏺')
        cat_ja = CAT_JA.get(c.get('category',''), c.get('category_ja',''))
        is_unesco = c['id'] in UNESCO_IDS
        badge = '<span class="craft-card-badge unesco">UNESCO</span>' if is_unesco else '<span class="craft-card-badge">国指定</span>'
        desc_short = (c.get('desc','') or '')[:90]
        cards_html.append(f'''<a class="craft-card" href="/craft/{pref}/{c['id']}.html">
      <div class="craft-card-img">{icon}{badge}</div>
      <div class="craft-card-body">
        <div class="craft-card-cat">{cat_ja}</div>
        <div class="craft-card-name">{c['name']}</div>
        <div class="craft-card-name-en">{c.get('name_en','')}</div>
        <div class="craft-card-area">{c.get('area','')}</div>
        <p class="craft-card-desc">{desc_short}</p>
      </div>
    </a>''')

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="ja" href="{canonical}">
<link rel="alternate" hreflang="en" href="{BASE_URL}/en/region/{pref}/">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{pref_ja}の伝統的工芸品 | Terroir HUB CRAFT">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}/img/ogp.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"BreadcrumbList",
  "itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Terroir HUB CRAFT","item":"{BASE_URL}/"}},
    {{"@type":"ListItem","position":2,"name":"産地から探す","item":"{BASE_URL}/craft/region/"}},
    {{"@type":"ListItem","position":3,"name":"{pref_ja}","item":"{canonical}"}}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"ItemList",
  "name":"{pref_ja}の伝統的工芸品",
  "numberOfItems":{count},
  "itemListElement":[
{chr(10).join(items_ld)}
  ]
}}
</script>
{CSS}
</head>
<body>
{NAV}

<div class="page-header">
  <div class="page-header-inner">
    <nav class="breadcrumb" aria-label="パンくずリスト">
      <a href="/">トップ</a><span class="breadcrumb-sep">›</span>
      <a href="/craft/region/">産地から探す</a><span class="breadcrumb-sep">›</span>
      <span>{pref_ja}</span>
    </nav>
    <p class="page-header-label">産地 / {pref_en}</p>
    <h1>{pref_ja}の<br>伝統的工芸品</h1>
    <div class="page-header-meta">
      <span class="page-header-count">{count}品目</span>
    </div>
    <p>経産省が指定する{pref_ja}の伝統的工芸品{count}品目。{title_crafts}など、{pref_ja}が誇る匠の技を探せます。</p>
  </div>
</div>

<div class="content-wrap">
  <div class="craft-grid">
    {''.join(cards_html)}
  </div>
</div>

{FOOTER}
</body>
</html>'''


def build_region_index(pref_craft_map):
    # Build regional sections
    sections = []
    for region_name, prefs in REGIONS.items():
        cards = []
        for pref in prefs:
            crafts = pref_craft_map.get(pref, [])
            if not crafts:
                continue
            pref_ja = PREF_JA.get(pref, pref)
            sample = '・'.join(c['name'] for c in crafts[:3])
            cards.append(f'''<a class="pref-card" href="/craft/region/{pref}/">
        <div class="pref-card-name">{pref_ja}</div>
        <div class="pref-card-count">{len(crafts)}品目</div>
        <div class="pref-card-sample">{sample}</div>
      </a>''')
        if cards:
            sections.append(f'''<section class="region-section">
    <h2 class="region-heading">{region_name}</h2>
    <div class="pref-grid">
      {''.join(cards)}
    </div>
  </section>''')

    total_prefs = sum(1 for p in pref_craft_map if pref_craft_map[p])
    total_crafts = sum(len(v) for v in pref_craft_map.values())

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>産地から探す — 都道府県別伝統工芸品一覧 | Terroir HUB CRAFT</title>
<meta name="description" content="都道府県別に日本の伝統的工芸品を探せます。石川県の九谷焼・輪島塗、京都府の西陣織・京漆器など46都道府県{total_crafts}品目を網羅。">
<link rel="canonical" href="{BASE_URL}/craft/region/">
<link rel="alternate" hreflang="ja" href="{BASE_URL}/craft/region/">
<meta property="og:type" content="website">
<meta property="og:title" content="産地から探す — 都道府県別伝統工芸品 | Terroir HUB CRAFT">
<meta property="og:description" content="46都道府県{total_crafts}品目の伝統的工芸品を産地から探せます。">
<meta property="og:url" content="{BASE_URL}/craft/region/">
<meta property="og:image" content="{BASE_URL}/img/ogp.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"BreadcrumbList",
  "itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Terroir HUB CRAFT","item":"{BASE_URL}/"}},
    {{"@type":"ListItem","position":2,"name":"産地から探す","item":"{BASE_URL}/craft/region/"}}
  ]
}}
</script>
{CSS}
<style>
.region-section{{margin-bottom:56px}}
.region-heading{{font-family:'Shippori Mincho',serif;font-size:22px;font-weight:700;color:var(--accent);padding-bottom:12px;border-bottom:2px solid var(--accent-light);margin-bottom:20px}}
.pref-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.pref-card{{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:20px 16px;text-decoration:none;display:block;transition:all .2s}}
.pref-card:hover{{transform:translateY(-2px);box-shadow:var(--shadow);border-color:var(--accent-light)}}
.pref-card-name{{font-family:'Shippori Mincho',serif;font-size:18px;font-weight:700;color:var(--text);margin-bottom:4px}}
.pref-card-count{{font-size:12px;color:var(--accent);font-weight:600;margin-bottom:8px}}
.pref-card-sample{{font-size:12px;color:var(--text3);line-height:1.5}}
.stats-bar{{background:var(--accent);color:#fff;padding:20px 24px;border-radius:var(--radius);display:flex;gap:40px;margin-bottom:48px;flex-wrap:wrap}}
.stat-item{{text-align:center}}
.stat-num{{font-family:'Shippori Mincho',serif;font-size:32px;font-weight:700;display:block}}
.stat-label{{font-size:12px;opacity:.8;margin-top:2px}}
@media(max-width:900px){{.pref-grid{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:600px){{.pref-grid{{grid-template-columns:repeat(2,1fr)}}.stats-bar{{gap:24px}}}}
</style>
</head>
<body>
{NAV}

<div class="page-header">
  <div class="page-header-inner">
    <nav class="breadcrumb" aria-label="パンくずリスト">
      <a href="/">トップ</a><span class="breadcrumb-sep">›</span>
      <span>産地から探す</span>
    </nav>
    <p class="page-header-label">Region</p>
    <h1>産地から探す</h1>
    <p>都道府県別に日本の伝統的工芸品を探せます。地域の風土が育んだ匠の技を、産地から発見してください。</p>
  </div>
</div>

<div class="content-wrap">
  <div class="stats-bar">
    <div class="stat-item"><span class="stat-num">{total_prefs}</span><div class="stat-label">都道府県</div></div>
    <div class="stat-item"><span class="stat-num">{total_crafts}</span><div class="stat-label">品目</div></div>
    <div class="stat-item"><span class="stat-num">240+</span><div class="stat-label">経産省指定品目</div></div>
  </div>
  {''.join(sections)}
</div>

{FOOTER}
</body>
</html>'''


def main():
    # Load all craft data
    data_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*.json')))
    pref_craft_map = {}
    for filepath in data_files:
        with open(filepath, encoding='utf-8') as f:
            crafts = json.load(f)
        for craft in crafts:
            pref = craft.get('prefecture', '')
            if pref:
                pref_craft_map.setdefault(pref, []).append(craft)

    count = 0
    for pref, crafts in sorted(pref_craft_map.items()):
        out_dir = os.path.join(BASE, 'craft', pref)
        os.makedirs(out_dir, exist_ok=True)
        html = build_pref_page(pref, crafts)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✓ {pref}/index.html — {PREF_JA.get(pref,pref)} ({len(crafts)}品目)')
        count += 1

    # Region index
    index_dir = os.path.join(BASE, 'craft', 'region')
    os.makedirs(index_dir, exist_ok=True)
    index_html = build_region_index(pref_craft_map)
    with open(os.path.join(index_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f'  ✓ region/index.html')

    print(f'\n=== Done ===')
    print(f'Generated: {count} prefecture pages + 1 index')

if __name__ == '__main__':
    main()
