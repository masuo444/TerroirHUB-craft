#!/usr/bin/env python3
"""Generate sitemap.xml for Terroir HUB CRAFT.

全公開HTMLファイルをファイルシステムから走査し、各ページの
<link rel="canonical"> が自分自身を指しているページ（= 正規URL）だけを
sitemapに登録する。canonicalが他ページを指す複製ページ（例:
/craft/{pref}/index.html → /craft/region/{pref}/ への重複）は自動的に除外される。

JSONデータの構造に依存しないため、ページが追加/削除されても
このスクリプトを再実行するだけでsitemapが実ファイルと同期する。
"""
import os
import re
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://craft.terroirhub.com"
TODAY = date.today().isoformat()

# トップレベルで除外するディレクトリ
EXCLUDE_DIRS = {".git", "api", "node_modules", "scripts"}

CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
NOINDEX_RE = re.compile(r'<meta[^>]+robots[^>]+noindex', re.I)


def path_to_url(rel_path):
    """相対パス（例: craft/aichi/index.html）を正規URLに変換。"""
    rel_path = rel_path.replace(os.sep, "/")
    if rel_path == "index.html":
        return f"{BASE_URL}/"
    if rel_path.endswith("/index.html"):
        return f"{BASE_URL}/{rel_path[:-len('index.html')]}"
    return f"{BASE_URL}/{rel_path}"


def priority_for(url):
    """URLパターンごとにpriority/changefreqを決定。"""
    path = url[len(BASE_URL):] or "/"

    if path == "/":
        return "1.0", "daily"
    if path == "/craft/search/":
        return "0.9", "daily"
    if path in ("/craft/category/", "/craft/region/"):
        return "0.8", "weekly"
    if re.fullmatch(r"/craft/category/[^/]+/", path):
        return "0.8", "weekly"
    if re.fullmatch(r"/craft/region/[^/]+/", path):
        return "0.75", "weekly"
    if path == "/en/":
        return "0.7", "weekly"
    if re.fullmatch(r"/craft/[^/]+/[^/]+\.html", path):
        return "0.7", "monthly"
    if path in ("/craft/experience/", "/craft/guide/", "/craft/map/",
                "/craft/partner/", "/craft/plans/"):
        return "0.6", "monthly"
    if path in ("/privacy/", "/terms/"):
        return "0.3", "yearly"
    return "0.5", "monthly"


def collect_urls():
    urls = []
    for root, dirs, files in os.walk(BASE):
        rel_root = os.path.relpath(root, BASE)
        parts = [] if rel_root == "." else rel_root.split(os.sep)
        if parts and parts[0] in EXCLUDE_DIRS:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for fname in files:
            if not fname.endswith(".html"):
                continue
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, BASE)
            with open(full, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if NOINDEX_RE.search(content):
                continue

            m = CANONICAL_RE.search(content)
            expected = path_to_url(rel)
            if not m or m.group(1) != expected:
                # canonicalが無い、または他ページを指す複製ページなので除外
                continue

            urls.append(expected)
    return sorted(set(urls))


def build_xml(urls):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    for url in urls:
        priority, changefreq = priority_for(url)
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    urls = collect_urls()
    xml = build_xml(urls)
    out_path = os.path.join(BASE, "sitemap.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)

    print("✓ sitemap.xml generated")
    print(f"  Total URLs: {len(urls)}")
    print(f"  Output: {out_path}")


if __name__ == "__main__":
    main()
