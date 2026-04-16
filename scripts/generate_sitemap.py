#!/usr/bin/env python3
"""Generate sitemap.xml for Terroir HUB CRAFT."""
import json, glob, os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://craft.terroirhub.com"
TODAY = date.today().isoformat()

urls = []

def add(loc, priority, changefreq="weekly"):
    urls.append({"loc": loc, "priority": priority, "changefreq": changefreq, "lastmod": TODAY})

# Top-level pages
add(f"{BASE_URL}/", "1.0", "daily")
add(f"{BASE_URL}/craft/search/", "0.9", "daily")
add(f"{BASE_URL}/craft/category/", "0.8", "weekly")
add(f"{BASE_URL}/craft/region/", "0.8", "weekly")
add(f"{BASE_URL}/en/", "0.7", "weekly")

# Category pages
categories = ["ceramics", "lacquerware", "textiles", "dyeing", "metalwork", "paper", "woodwork", "dolls", "buddhist", "other"]
for cat in categories:
    add(f"{BASE_URL}/craft/category/{cat}/", "0.8", "weekly")

# All individual craft pages from JSON data
data_files = sorted(glob.glob(os.path.join(BASE, "data", "data_*.json")))
craft_count = 0
for filepath in data_files:
    with open(filepath, encoding="utf-8") as f:
        crafts = json.load(f)
    for craft in crafts:
        pref = craft.get("prefecture", "")
        cid = craft.get("id", "")
        if pref and cid:
            add(f"{BASE_URL}/craft/{pref}/{cid}.html", "0.7", "monthly")
            craft_count += 1

# Prefecture/region pages
prefectures = set()
for filepath in data_files:
    with open(filepath, encoding="utf-8") as f:
        crafts = json.load(f)
    for craft in crafts:
        if craft.get("prefecture"):
            prefectures.add(craft["prefecture"])
for pref in sorted(prefectures):
    add(f"{BASE_URL}/craft/region/{pref}/", "0.75", "weekly")

# Build XML
lines = ['<?xml version="1.0" encoding="UTF-8"?>']
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')
for u in urls:
    lines.append("  <url>")
    lines.append(f"    <loc>{u['loc']}</loc>")
    lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
    lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
    lines.append(f"    <priority>{u['priority']}</priority>")
    lines.append("  </url>")
lines.append("</urlset>")

out_path = os.path.join(BASE, "sitemap.xml")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"✓ sitemap.xml generated")
print(f"  Total URLs: {len(urls)}")
print(f"  Craft pages: {craft_count}")
print(f"  Prefecture pages: {len(prefectures)}")
print(f"  Output: {out_path}")
