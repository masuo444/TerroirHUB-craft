#!/usr/bin/env python3
"""
Manual corrections for craft source URLs.
Maps our craft names to official kougeihin.jp names and URLs.
"""
import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the official URL map built by fetch_official_data.py
with open(os.path.join(BASE, 'scripts', 'official_url_map.json')) as f:
    official_map = json.load(f)

# Build name → url lookup from official map
name_to_url = {v['name']: v['url'] for v in official_map.values()}

# Manual mappings: our name → official kougeihin.jp name
# (only for crafts that ARE on kougeihin.jp but under a different name)
MANUAL_MAP = {
    # Dyeing - 染色
    '江戸小紋':        '東京染小紋',
    '伊勢型紙':        '伊勢形紙',
    '加賀繡':          '加賀繍',
    '京繡':            '京繍',
    # Metalwork - 金工
    '肥後象嵌':        '肥後象がん',
    '播州刃物':        '播州三木打刃物',
    '三条打刃物':      '越後三条打刃物',
    # Lacquerware - 漆器
    # Other - その他
    '江戸ガラス':      '江戸硝子',
    '鼈甲細工':        '江戸べっ甲',   # Or '長崎べっ甲' — our item is Tokyo-based
    '伊賀組紐':        '伊賀くみひも',
    # Paper/Wood - 和紙・木工
    '石州半紙':        '石州和紙',
    '内山和紙':        '内山紙',
    '加茂桐箪笥':      '加茂桐簞笥',
    '春日部桐箪笥':    '春日部桐簞笥',
    # Textiles - 織物
    '阿波しじら織':    '阿波正藍しじら織',
    '米沢織':          '置賜紬',
    # Buddhist - 仏壇
    '新潟仏壇':        '新潟・白根仏壇',
    # Dolls - 人形
    '江戸衣裳着人形':  '江戸節句人形',
    '名古屋節句飾':    '名古屋節句飾',
}

# Items confirmed NOT on kougeihin.jp (prefectural designations or unconfirmed)
# These get source="" and a note that they may be prefectural designation
NOT_METI_CONFIRMED = {
    # Dolls - these appear to be prefectural/city level
    '三春人形', '鴻巣雛人形', '奈良一刀彫', '伏見人形', '加茂人形',
    '金沢人形', '仙台張子', '下川原土人形', '相良人形', '大津張子',
    # Textiles - may be prefectural or recently added/removed from METI list
    '丹後ちりめん', '伊勢木綿', '真岡木綿', '上田紬', '能登上布',
    '播州織', '越前羽二重', '佐賀錦', '甲州織', '長浜ちりめん',
    '会津木綿', '遠州綿紬', '高島ちぢみ', '足利織物', '知多木綿',
    '津軽織', '武蔵野織物', '但馬ちりめん', '川越唐桟', '南部裂織',
    '三河木綿', '人吉球磨紬', '郡上紬', '丹波布',
    # Ceramics - prefectural or unconfirmed
    '小鹿田焼', '大樋焼', '肥前吉田焼', '今戸焼', '高取焼',
    # Other
    '薩摩切子', '江戸扇子', '讃岐かがり手まり', '和蝋燭',
    '阿波人形浄瑠璃人形', '越後上布', '津軽こぎん刺し', '那智黒石工芸品',
    # Dyeing
    '長板中形', '江戸刺繍', '京繡', '南部紫根染',
    # Paper
    '西ノ内和紙', '飛騨和紙', '細川紙', '名塩和紙', '吉野和紙',
    # Metalwork
    '東京打刃物', '京金工', '庄内刃物', '岐阜刃物', '備前長船刃物', '豊後高田やすり',
    # Buddhist
    '長崎仏壇', '長野仏壇',
    # Lacquerware
    '輪島沈金', '根来塗', '日光彫',
}

def main():
    data_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*.json')))

    manual_fixed = 0
    already_matched = 0
    not_meti = 0
    still_missing = []

    for filepath in data_files:
        fname = os.path.basename(filepath)
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        changed = 0
        for item in data:
            name = item['name']
            current_src = item.get('source', '')

            # Already has correct source
            if current_src and 'kougeihin.jp/craft/' in current_src:
                already_matched += 1
                continue

            # Apply manual mapping
            if name in MANUAL_MAP:
                official_name = MANUAL_MAP[name]
                if official_name in name_to_url:
                    item['source'] = name_to_url[official_name]
                    manual_fixed += 1
                    changed += 1
                    print(f"  ✓ {name} → {official_name}: {item['source']}")
                continue

            # Known not METI
            if name in NOT_METI_CONFIRMED:
                item['source'] = ''
                not_meti += 1
                continue

            # Direct name match
            if name in name_to_url:
                item['source'] = name_to_url[name]
                manual_fixed += 1
                changed += 1
                continue

            still_missing.append(f"{fname}: {name}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if changed:
            print(f"  [{fname}] {changed}件更新")

    print(f"\n=== 結果 ===")
    print(f"既存マッチ: {already_matched}件")
    print(f"手動修正: {manual_fixed}件")
    print(f"非METI指定: {not_meti}件（source空欄に設定）")
    print(f"未解決: {len(still_missing)}件")
    if still_missing:
        print("未解決リスト:")
        for s in still_missing:
            print(f"  {s}")

if __name__ == '__main__':
    main()
