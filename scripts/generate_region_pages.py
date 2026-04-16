#!/usr/bin/env python3
"""Generate 6 regional group pages for Terroir HUB CRAFT."""
import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://craft.terroirhub.com"

REGIONS = [
    {
        'slug': 'hokkaido-tohoku',
        'ja': '北海道・東北',
        'en': 'Hokkaido & Tohoku',
        'prefs': ['hokkaido','aomori','iwate','miyagi','akita','yamagata','fukushima'],
        'prefs_ja': ['北海道','青森県','岩手県','宮城県','秋田県','山形県','福島県'],
        'desc': '本州最北端から北の大地まで、寒冷な気候と豊かな森林資源が独自の工芸文化を育みました。南部鉄器・津軽塗・会津塗・米沢織など、厳しい自然に鍛えられた骨太な工芸品が揃います。',
        'desc_en': 'The northern regions of Japan — from Hokkaido to Tohoku — have developed craft traditions shaped by cold climates and abundant forest resources. Nambu ironware, Tsugaru lacquer, Aizu lacquerware, and Yonezawa textiles are among the most celebrated.',
        'color': '#3D6B8A',
        'bg': '#e8eff5',
    },
    {
        'slug': 'kanto',
        'ja': '関東',
        'en': 'Kanto',
        'prefs': ['ibaraki','tochigi','gunma','saitama','chiba','tokyo','kanagawa'],
        'prefs_ja': ['茨城県','栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県'],
        'desc': '江戸文化が花開いた関東地方は、職人の技が集結した工芸の一大産地です。江戸切子・江戸小紋・結城紬・益子焼など、都市の審美眼と職人の高度な技術が融合した工芸品が数多く誕生しました。',
        'desc_en': 'The Kanto region, home to Edo (modern Tokyo), became a major center of craft production where artisan skills were refined for an urban clientele. Edo Kiriko cut glass, Edo Komon dyeing, Yuki Tsumugi weaving, and Mashiko pottery are among the finest examples.',
        'color': '#5C4A8A',
        'bg': '#ede8f5',
    },
    {
        'slug': 'chubu-hokuriku',
        'ja': '中部・北陸',
        'en': 'Chubu & Hokuriku',
        'prefs': ['niigata','toyama','ishikawa','fukui','yamanashi','nagano','gifu','shizuoka','aichi'],
        'prefs_ja': ['新潟県','富山県','石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県'],
        'desc': '石川県の九谷焼・輪島塗をはじめ、越前漆器・美濃和紙・西陣に次ぐ織物産地など、日本を代表する工芸品が集中する地域です。北陸の豊かな自然と中部の技術力が融合した工芸文化が根付いています。',
        'desc_en': 'Chubu and Hokuriku are home to some of Japan\'s most celebrated craft traditions. Ishikawa Prefecture alone boasts Kutani ceramics and Wajima lacquerware. Echizen lacquerware, Mino washi paper, and Owari cloisonné from Aichi add to an extraordinary concentration of craft heritage.',
        'color': '#2E5E4E',
        'bg': '#e8f0ec',
    },
    {
        'slug': 'kinki',
        'ja': '近畿',
        'en': 'Kinki (Kansai)',
        'prefs': ['mie','shiga','kyoto','osaka','hyogo','nara','wakayama'],
        'prefs_ja': ['三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県'],
        'desc': '千年の都・京都を中心に、日本の伝統工芸の中心地として発展してきた近畿地方。西陣織・京友禅・京漆器・京焼など「京」の名を冠する工芸品の多くがここで生まれました。',
        'desc_en': 'With Kyoto at its heart, the Kinki (Kansai) region is arguably Japan\'s most important cradle of traditional crafts. Nishijin weaving, Kyo-Yuzen dyeing, Kyoto lacquerware, and Kyo-yaki ceramics represent centuries of refined artisanship in the ancient capital.',
        'color': '#7A4020',
        'bg': '#f5ede8',
    },
    {
        'slug': 'chugoku-shikoku',
        'ja': '中国・四国',
        'en': 'Chugoku & Shikoku',
        'prefs': ['tottori','shimane','okayama','hiroshima','yamaguchi','tokushima','kagawa','ehime','kochi'],
        'prefs_ja': ['鳥取県','島根県','岡山県','広島県','山口県','徳島県','香川県','愛媛県','高知県'],
        'desc': '山陰・山陽・四国にわたるこの地域には、石州和紙・出雲石燈籠・備前焼・阿波しじら織など個性豊かな工芸品が点在します。山と海の豊かな自然と、各地の固有文化が生んだ多様な工芸の宝庫です。',
        'desc_en': 'Spanning the Chugoku and Shikoku regions, this area offers remarkable craft diversity — from Sekishu washi paper and Bizen pottery in the west to Awa Shijira textiles and Tosa washi in Shikoku. Each craft reflects the distinctive local environment and culture.',
        'color': '#5C7A4A',
        'bg': '#eef5e8',
    },
    {
        'slug': 'kyushu-okinawa',
        'ja': '九州・沖縄',
        'en': 'Kyushu & Okinawa',
        'prefs': ['fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima','okinawa'],
        'prefs_ja': ['福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県'],
        'desc': 'アジアとの交流拠点として独自の工芸文化を育んだ九州・沖縄。有田焼・博多織・薩摩切子・琉球漆器・琉球絣など、大陸文化の影響を受けた華やかで個性的な工芸品が生まれました。',
        'desc_en': 'Kyushu and Okinawa developed distinctive craft traditions shaped by centuries of exchange with Asia. Arita porcelain, Hakata weaving, Satsuma cut glass, Ryukyu lacquerware, and Ryukyu kasuri textiles all reflect the cross-cultural influences that make this region\'s crafts uniquely vibrant.',
        'color': '#7A6020',
        'bg': '#f5f0e0',
    },
]

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
CAT_ICON = {
    'ceramics':'🏺','lacquerware':'🪔','textiles':'🧵','dyeing':'🪭',
    'metalwork':'⚒️','paper':'📜','woodwork':'🌿','dolls':'🎎','buddhist':'🕯️','other':'✨'
}
CAT_JA = {
    'ceramics':'陶磁器','lacquerware':'漆器','textiles':'織物','dyeing':'染色品',
    'metalwork':'金工品','paper':'和紙','woodwork':'木竹工芸品','dolls':'人形・こけし',
    'buddhist':'仏壇・仏具','other':'その他'
}
UNESCO_IDS = {'yuki_tsumugi','echizen_washi','mino_washi','sekishu_banshi','hosokawa_kami'}

NAV_TPL = '''<nav>
  <a href="/" class="nav-logo">Terroir HUB<span>CRAFT</span></a>
  <div class="nav-links">
    <a href="/craft/search/">工芸品検索</a>
    <a href="/craft/category/">カテゴリ</a>
    <a href="/craft/region/" class="active">産地から探す</a>
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

CSS = '''<style>
:root{
  --bg:#FAF8F5;--bg2:#F3EDE6;--accent:#2E5E4E;--accent2:#C4A265;
  --accent-light:#EAF2EE;--accent-gold:#E8C97A;--text:#1A1A18;
  --text2:#5C5A56;--text3:#8A8880;--border:#E8E0D6;
  --nav-h:56px;--radius:12px;
  --shadow:0 2px 16px rgba(46,94,78,.10);--shadow-lg:0 8px 40px rgba(46,94,78,.16);
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans JP','Inter',sans-serif;font-size:15px;line-height:1.7;-webkit-font-smoothing:antialiased}
nav{position:fixed;top:0;left:0;right:0;height:var(--nav-h);background:rgba(250,248,245,.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:1000;display:flex;align-items:center;padding:0 24px;gap:24px}
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
.breadcrumb a{color:var(--text3);text-decoration:none}
.breadcrumb a:hover{color:var(--accent)}
.breadcrumb-sep{color:var(--border)}
footer{background:#1a1a18;color:rgba(255,255,255,.5);padding:40px 24px 24px;font-size:13px}
.footer-inner{max-width:1200px;margin:0 auto}
.footer-bottom{border-top:1px solid rgba(255,255,255,.08);padding-top:20px;display:flex;justify-content:space-between;align-items:center;font-size:12px;flex-wrap:wrap;gap:12px}
.footer-bottom-links{display:flex;gap:16px}
.footer-bottom-links a{color:rgba(255,255,255,.35);text-decoration:none;transition:color .2s}
.footer-bottom-links a:hover{color:rgba(255,255,255,.7)}
@media(max-width:900px){.nav-links{display:none}.hamburger{display:flex}}
@media(max-width:600px){.footer-bottom{flex-direction:column;text-align:center}}
</style>'''


def build_region_page(region, crafts_in_region, pref_craft_map):
    slug = region['slug']
    count = len(crafts_in_region)
    sample_names = '・'.join(c['name'] for c in crafts_in_region[:6])
    canonical = f"{BASE_URL}/craft/region/{slug}/"
    title = f"{region['ja']}の伝統的工芸品 {count}品目 — {sample_names} | Terroir HUB CRAFT"
    desc = f"{region['ja']}の伝統的工芸品{count}品目を網羅。{sample_names}など、{region['ja']}各地の工芸品の産地・技法・歴史を紹介。"

    # Prefecture sub-sections
    pref_sections = []
    for pref in region['prefs']:
        crafts = pref_craft_map.get(pref, [])
        if not crafts:
            continue
        pref_ja = PREF_JA.get(pref, pref)
        cards = []
        for c in crafts:
            icon = CAT_ICON.get(c.get('category', ''), '🏺')
            designation = c.get('designation', 'meti')
            is_unesco = c['id'] in UNESCO_IDS
            if is_unesco:
                badge = '<span class="cc-badge unesco">UNESCO</span>'
            elif designation == 'regional':
                badge = '<span class="cc-badge regional">地域指定</span>'
            else:
                badge = '<span class="cc-badge">国指定</span>'
            name_en = c.get('name_en', '')
            cards.append(f'''<a class="craft-card" href="/craft/{pref}/{c['id']}.html">
          <div class="craft-card-img" style="background:{region['bg']}">{icon}{badge}</div>
          <div class="craft-card-body">
            <div class="craft-card-name">{c['name']}</div>
            <div class="craft-card-name-en">{name_en}</div>
          </div>
        </a>''')

        pref_sections.append(f'''<section class="pref-section" id="{pref}">
      <div class="pref-heading">
        <h2>{pref_ja}</h2>
        <a href="/craft/region/{pref}/" class="pref-all-link">すべて見る ({len(crafts)}品目) →</a>
      </div>
      <div class="craft-grid">
        {''.join(cards)}
      </div>
    </section>''')

    # Other regions nav
    other_regions = []
    for r in REGIONS:
        if r['slug'] != slug:
            other_regions.append(
                f'<a href="/craft/region/{r["slug"]}/" class="sibling-region">{r["ja"]}</a>'
            )

    # JSON-LD items
    items_ld = []
    for i, c in enumerate(crafts_in_region[:20]):
        pref = c.get('prefecture', '')
        url = f"{BASE_URL}/craft/{pref}/{c['id']}.html"
        items_ld.append(f'    {{"@type":"ListItem","position":{i+1},"name":"{c["name"]}","url":"{url}"}}')

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="ja" href="{canonical}">
<link rel="alternate" hreflang="en" href="{BASE_URL}/en/region/{slug}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{region['ja']}の伝統的工芸品 | Terroir HUB CRAFT">
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
  "@type":"CollectionPage",
  "name":"{region['ja']}の伝統的工芸品",
  "description":"{region['desc_en'][:200]}",
  "url":"{canonical}",
  "about":{{"@type":"Place","name":"{region['ja']}","containedInPlace":{{"@type":"Country","name":"Japan"}}}},
  "mainEntity":{{
    "@type":"ItemList","numberOfItems":{count},
    "itemListElement":[
{chr(10).join(items_ld)}
    ]
  }}
}}
</script>
{CSS}
<style>
.page-header{{padding-top:calc(var(--nav-h) + 48px);padding-bottom:48px;padding-left:24px;padding-right:24px;background:linear-gradient(135deg,{region['bg']},{region['bg']}aa,#f0ebe3)}}
.page-header-inner{{max-width:1200px;margin:0 auto}}
.page-header-label{{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}}
.page-header h1{{font-family:'Shippori Mincho',serif;font-size:clamp(28px,4vw,44px);font-weight:700;margin-bottom:8px}}
.page-header-en{{font-size:14px;color:var(--text3);font-family:'Inter',sans-serif;letter-spacing:.08em;margin-bottom:12px}}
.count-badge{{display:inline-block;background:var(--accent);color:#fff;font-size:13px;font-weight:700;padding:4px 14px;border-radius:20px;margin-bottom:16px}}
.page-header-desc{{color:var(--text2);font-size:14px;max-width:640px;line-height:1.8;margin-bottom:6px}}
.page-header-desc-en{{color:var(--text3);font-size:13px;max-width:640px;line-height:1.7;font-style:italic}}
.content-wrap{{max-width:1200px;margin:0 auto;padding:40px 24px 80px}}
.pref-tabs{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:40px;padding-bottom:20px;border-bottom:1px solid var(--border)}}
.pref-tab{{font-size:13px;color:var(--text2);background:#fff;border:1px solid var(--border);border-radius:20px;padding:5px 14px;text-decoration:none;transition:all .2s}}
.pref-tab:hover{{border-color:var(--accent);color:var(--accent)}}
.pref-section{{margin-bottom:56px}}
.pref-heading{{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:8px}}
.pref-heading h2{{font-family:'Shippori Mincho',serif;font-size:22px;font-weight:700;color:var(--accent)}}
.pref-all-link{{font-size:13px;color:var(--accent2);text-decoration:none;font-weight:600;transition:color .2s}}
.pref-all-link:hover{{color:var(--accent)}}
.craft-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}
.craft-card{{background:#fff;border-radius:var(--radius);overflow:hidden;border:1px solid var(--border);transition:all .25s;text-decoration:none;display:block}}
.craft-card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-lg)}}
.craft-card-img{{aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;font-size:40px;position:relative}}
.cc-badge{{position:absolute;top:8px;left:8px;background:var(--accent);color:#fff;font-size:9px;font-weight:700;letter-spacing:.06em;padding:2px 7px;border-radius:4px;font-family:'Inter',sans-serif;text-transform:uppercase}}
.cc-badge.regional{{background:#5C7A8A}}
.cc-badge.unesco{{background:#7B4F9E}}
.craft-card-body{{padding:14px}}
.craft-card-name{{font-family:'Shippori Mincho',serif;font-size:16px;font-weight:700;color:var(--text);margin-bottom:3px}}
.craft-card-name-en{{font-size:11px;color:var(--text3);font-family:'Inter',sans-serif}}
.sibling-regions{{display:flex;flex-wrap:wrap;gap:10px;padding-top:32px;border-top:1px solid var(--border);margin-top:16px}}
.sibling-regions-label{{font-size:12px;color:var(--text3);font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px}}
.sibling-region{{background:#fff;border:1px solid var(--border);border-radius:20px;padding:6px 16px;font-size:13px;color:var(--text2);text-decoration:none;transition:all .2s}}
.sibling-region:hover{{border-color:var(--accent);color:var(--accent)}}
@media(max-width:900px){{.craft-grid{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:600px){{.craft-grid{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head>
<body>
{NAV_TPL}

<div class="page-header">
  <div class="page-header-inner">
    <nav class="breadcrumb" aria-label="パンくずリスト">
      <a href="/">トップ</a><span class="breadcrumb-sep">›</span>
      <a href="/craft/region/">産地から探す</a><span class="breadcrumb-sep">›</span>
      <span>{region['ja']}</span>
    </nav>
    <p class="page-header-label">Region — {region['en']}</p>
    <h1>{region['ja']}の伝統的工芸品</h1>
    <div class="page-header-en">{region['en']} Traditional Crafts</div>
    <span class="count-badge">{count}品目</span>
    <p class="page-header-desc">{region['desc']}</p>
    <p class="page-header-desc-en">{region['desc_en']}</p>
  </div>
</div>

<div class="content-wrap">
  <div class="pref-tabs">
    {''.join(f'<a class="pref-tab" href="#{p}">{PREF_JA.get(p,p)}</a>' for p in region['prefs'] if p in pref_craft_map)}
  </div>

  {''.join(pref_sections)}

  <div class="sibling-regions-label">他の地域を見る</div>
  <div class="sibling-regions">
    {''.join(other_regions)}
  </div>
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

    out_dir_base = os.path.join(BASE, 'craft', 'region')
    os.makedirs(out_dir_base, exist_ok=True)

    for region in REGIONS:
        # Collect all crafts for this region
        crafts_in_region = []
        for pref in region['prefs']:
            crafts_in_region.extend(pref_craft_map.get(pref, []))

        html = build_region_page(region, crafts_in_region, pref_craft_map)
        out_dir = os.path.join(out_dir_base, region['slug'])
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ region/{region['slug']}/index.html — {region['ja']} ({len(crafts_in_region)}品目)")

    print(f'\n=== Done === 6 regional pages generated')


if __name__ == '__main__':
    main()
