#!/usr/bin/env python3
"""將 data-src/raw/<公司>.txt（由公司網站原始數據抽出）轉做 data-src/<公司>.csv。

raw 格式（| 分隔）：中文名|英文名|公司產品類別|貨幣|紅利類型|v1..v10|v10p
用法：python3 tools/import-raw.py aia   （再跑 tools/build-data.py）

產品類型（cat）由下面嘅關鍵字自動分；分錯就喺 OVERRIDE 加。
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CI = r"危疾|Critical [Ii]llness|[Cc]risis|安心保|易重保|倍安保|智倍保|愛伴航|On Your Side|CI\b"
SAVE = (r"儲蓄|Sav|入息|Income|年金|Annuity|教育|Education|升學|長享|Coupon|充裕未來|Bonus Power|盈御|Global Power|"
        r"財富|創富|萬利|Wealth|智昇|Proactive|諾享|Fortune Promise|盈尚|儲速|活享|環宇|Flexi|傳承|Legacy|Endowment|養老|收益")
SAVE_TYPES = r"儲蓄|入息|年金|Endowment|Annuity|Income"
OVERRIDE = {
    # (公司, 英文名): cat
    ("pru", "Double Treasure Plan"): "save",
    ("pru", "Prudential Entrust Multi-Currency Insurance Plan"): "save",
}
CUR = {"所有": "全部", "All": "全部"}

def classify(co, zh, en, ptype):
    if (co, en) in OVERRIDE:
        return OVERRIDE[(co, en)]
    txt = f"{zh} {en}"
    if re.search(CI, txt + " " + ptype):
        return "ci"
    if re.search(SAVE_TYPES, ptype) or re.search(SAVE, txt):
        return "save"
    return "life"

def main(co):
    src = os.path.join(ROOT, "data-src", "raw", co + ".txt")
    out = ["plan_zh|plan_en|cat|cur|type|v1|v2|v3|v4|v5|v6|v7|v8|v9|v10|v10p"]
    for line in open(src, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        f = line.split("|")
        zh, en, ptype, cur, typ, vals = f[0].strip(), f[1].strip(), f[2], f[3].strip(), f[4], f[5:]
        assert len(vals) == 11, line
        out.append("|".join([zh, en, classify(co, zh, en, ptype), CUR.get(cur, cur), typ] + vals))
    open(os.path.join(ROOT, "data-src", co + ".csv"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(co, len(out) - 1, "rows")

if __name__ == "__main__":
    for c in sys.argv[1:]:
        main(c)
