#!/usr/bin/env python3
"""將 data-src/*.csv 合併做 data.json（網頁讀呢個檔）。

用法：python3 tools/build-data.py

CSV 格式（| 分隔）：plan_zh|plan_en|cat|cur|type|v1..v10|v10p
- cat：save 儲蓄及退休、life 人壽、ci 危疾（我哋自己按產品性質分）
- type：週年紅利、歸原紅利、終期紅利、特別紅利（照公司寫法）
- v1 = 第 1 個保單年度（報告年度前一年生效）… v10，v10p = 10 年以上
- 數值：數字（百分比，唔使 %）；NA 不適用；NL 未推出；CS 已停售；留空 = 公司冇列
"""
import csv, hashlib, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data-src")
TYPE_GROUP = {"週年紅利": "annual", "歸原紅利": "rev", "終期紅利": "term", "特別紅利": "term", "非保證利益": "term", "非保證年金": "annual"}

def cell(x):
    x = (x or "").strip()
    if x == "":
        return None
    if re.fullmatch(r"\d+(\.\d+)?", x):
        return float(x) if "." in x else int(x)
    if x in ("NA", "NL", "CS"):
        return x
    raise ValueError("unknown cell: " + x)

def main():
    cos = json.load(open(os.path.join(SRC, "companies.json"), encoding="utf-8"))
    series = []
    for c in cos:
        rows = list(csv.DictReader(open(os.path.join(SRC, c["file"]), encoding="utf-8"), delimiter="|"))
        for i, r in enumerate(rows):
            t = r["type"].strip()
            if t not in TYPE_GROUP:
                raise ValueError(f"{c['file']} row {i}: type {t}")
            if r["cat"] not in ("save", "life", "ci"):
                raise ValueError(f"{c['file']} row {i}: cat {r['cat']}")
            v = [cell(r[k]) for k in ["v%d" % n for n in range(1, 11)] + ["v10p"]]
            series.append({
                # 穩定 id（分享連結用）：公司 + 計劃英文名 + 貨幣 + 紅利類型
                "id": c["id"] + "-" + hashlib.md5(f"{r['plan_en'].strip()}|{r['cur'].strip()}|{t}".encode()).hexdigest()[:6],
                "co": c["id"],
                "plan": (r["plan_zh"] or "").strip() or r["plan_en"].strip(),
                "zh": (r["plan_zh"] or "").strip(),
                "en": r["plan_en"].strip(),
                "cat": r["cat"], "cur": r["cur"].strip(), "type": t, "tg": TYPE_GROUP[t],
                "v": v,
            })
    ids = [x["id"] for x in series]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate series id")
    out = {
        "rep": max(c["rep"] for c in cos),
        "updated": "2026-11-26",
        "companies": [{k: c.get(k, "") for k in ("id", "name", "full", "rep", "source", "note", "color", "ink")} for c in cos],
        # 未收錄嘅公司（名 + 原因），總覽會列出，免得客人以為冇列出 = 唔好
        "missing": json.load(open(os.path.join(SRC, "missing.json"), encoding="utf-8")) if os.path.exists(os.path.join(SRC, "missing.json")) else [],
        "series": series,
    }
    json.dump(out, open(os.path.join(ROOT, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    pts = sum(1 for s in series for x in s["v"] if isinstance(x, (int, float)))
    print(f"{len(cos)} companies, {len(series)} series, {pts} data points")

if __name__ == "__main__":
    main()
