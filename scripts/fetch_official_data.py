#!/usr/bin/env python3
"""
Fetch official data from kougeihin.jp (伝統工芸 青山スクエア) and:
1. Build a correct name → URL mapping
2. Update source URLs in our JSON data files
3. Extract official descriptions and key facts for reference

Legal note: We only extract factual data (craft name, production area, category).
We do NOT copy description text verbatim. Descriptions in our data are original.
Source attribution is added as the 'source' field pointing to the official page.
"""
import urllib.request
import re
import json
import glob
import os
import time
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'ja,en;q=0.9',
}


def fetch_page(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
            else:
                return None


def extract_craft_info(html, url):
    """Extract craft name and key factual info from kougeihin.jp page."""
    if not html:
        return None

    info = {'url': url}

    # Craft name from h1.detail_title
    m = re.search(r'<h1 class="detail_title">([^<]+)</h1>', html)
    if m:
        info['name'] = m.group(1).strip()
    else:
        # fallback: title tag
        m = re.search(r'<title>([^|<]+)', html)
        if m:
            info['name'] = m.group(1).strip()

    # Category from craft_industry link
    m = re.search(r'class="icon_industry"[^>]*>([^<]+)</a>', html)
    if m:
        info['category_official'] = m.group(1).strip()

    # Official description (first paragraph of description - factual reference only)
    m = re.search(r'<p class="description">(.+?)</p>', html, re.DOTALL)
    if m:
        desc_raw = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        desc_raw = re.sub(r'\s+', ' ', desc_raw)
        info['official_desc_ref'] = desc_raw[:200]  # Store first 200 chars for reference

    # Production area from table (工芸品の産地)
    area_match = re.search(
        r'工芸品の産地.*?<td[^>]*>([^<]+)</td>',
        html, re.DOTALL
    )
    if area_match:
        info['official_area'] = area_match.group(1).strip()

    return info


def normalize_name(name):
    """Normalize craft name for matching."""
    return (name
            .replace('・', '')
            .replace('　', '')
            .replace(' ', '')
            .replace('ㇱ', 'シ')  # Ainu character normalization
            .replace('ッ', 'ツ')
            .strip())


def main():
    # Step 1: Get all craft URLs from sitemap
    print("=== Step 1: Fetching sitemap ===")
    sitemap_html = fetch_page('https://kougeihin.jp/sitemap.xml')
    if not sitemap_html:
        print("ERROR: Could not fetch sitemap")
        sys.exit(1)

    craft_urls = sorted(set(re.findall(r'https://kougeihin\.jp/craft/\d+/', sitemap_html)))
    print(f"Found {len(craft_urls)} craft URLs in sitemap")

    # Step 2: Fetch each page and extract craft name
    print(f"\n=== Step 2: Fetching {len(craft_urls)} craft pages ===")
    official_map = {}  # normalized_name → {url, name, ...}
    failed = []

    for i, url in enumerate(craft_urls):
        html = fetch_page(url)
        info = extract_craft_info(html, url)
        if info and info.get('name'):
            norm = normalize_name(info['name'])
            official_map[norm] = info
            if (i + 1) % 20 == 0:
                print(f"  {i+1}/{len(craft_urls)} done...")
        else:
            failed.append(url)
        time.sleep(0.3)  # respectful rate limiting

    print(f"Successfully fetched: {len(official_map)} crafts")
    if failed:
        print(f"Failed: {len(failed)} URLs: {failed[:5]}")

    # Save the official mapping for reference
    mapping_path = os.path.join(BASE, 'scripts', 'official_url_map.json')
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(official_map, f, ensure_ascii=False, indent=2)
    print(f"Saved URL map to: {mapping_path}")

    # Step 3: Match our data to official URLs and update source fields
    print("\n=== Step 3: Matching our data to official URLs ===")
    data_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*.json')))

    total_matched = 0
    total_unmatched = 0
    unmatched_items = []

    for filepath in data_files:
        fname = os.path.basename(filepath)
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        changed = 0
        for item in data:
            norm = normalize_name(item['name'])
            if norm in official_map:
                official = official_map[norm]
                old_src = item.get('source', '')
                new_src = official['url']
                if old_src != new_src:
                    item['source'] = new_src
                    changed += 1
                total_matched += 1
            else:
                # Try partial match
                matched = False
                for key, val in official_map.items():
                    if norm in key or key in norm:
                        item['source'] = val['url']
                        changed += 1
                        matched = True
                        total_matched += 1
                        break
                if not matched:
                    total_unmatched += 1
                    unmatched_items.append(f"{fname}: {item['name']}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        if changed:
            print(f"  {fname}: {changed}件のsource URLを更新")

    print(f"\n=== 結果 ===")
    print(f"マッチ成功: {total_matched}件")
    print(f"マッチ失敗: {total_unmatched}件")
    if unmatched_items:
        print("マッチできなかった品目:")
        for item in unmatched_items:
            print(f"  {item}")

    # Step 4: Verify - check that official names match our names
    print("\n=== Step 4: 名称不一致チェック ===")
    mismatches = []
    for filepath in data_files:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            src = item.get('source', '')
            if src:
                # Extract URL code
                m = re.search(r'/craft/(\d+)/', src)
                if m:
                    url_code = m.group(1)
                    norm_key = normalize_name(item['name'])
                    official = official_map.get(norm_key)
                    if official:
                        if official['url'] != src:
                            mismatches.append(f"{item['name']}: ours={src} official={official['url']}")

    if mismatches:
        print(f"不一致: {len(mismatches)}件")
        for m in mismatches[:10]:
            print(f"  {m}")
    else:
        print("名称ベースのマッチングは正常")

    print("\n完了。")


if __name__ == '__main__':
    main()
