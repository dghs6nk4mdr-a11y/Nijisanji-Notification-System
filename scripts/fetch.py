import requests
import json
import os
from datetime import datetime, timezone, timedelta

# ── 設定 ──────────────────────────────────────────────────
API_BASE = "https://www.nijisanji.jp/api/streams"
DATA_PATH = "docs/data/streams.json"
KEYWORDS_PATH = "config/keywords.json"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

JST = timezone(timedelta(hours=9))

# ── キーワード読み込み ────────────────────────────────────
def load_keywords():
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [kw.strip() for kw in data.get("keywords", []) if kw.strip()]

# ── API取得 ───────────────────────────────────────────────
def fetch_streams(day_offset: int) -> list:
    try:
        res = requests.get(
            API_BASE,
            params={"day_offset": day_offset},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        res.raise_for_status()
        data = res.json()
        # レスポンス構造に応じて調整（配列 or {"streams": [...]} など）
        if isinstance(data, list):
            return data
        return data.get("streams", data.get("data", []))
    except Exception as e:
        print(f"[ERROR] day_offset={day_offset} の取得に失敗: {e}")
        return []

# ── フィルタリング ────────────────────────────────────────
def filter_streams(streams: list, keywords: list) -> list:
    results = []
    for s in streams:
        title = s.get("title", "")
        if any(kw in title for kw in keywords):
            results.append({
                "id": s.get("id", ""),
                "title": title,
                "liver_name": s.get("liver", {}).get("name", s.get("liver_name", "")),
                "liver_icon": s.get("liver", {}).get("icon_image_url", s.get("liver_icon", "")),
                "thumbnail": s.get("thumbnail_image_url", s.get("thumbnail", "")),
                "status": s.get("status", ""),          # "onair" / "scheduled" など
                "start_time": s.get("start_time", s.get("scheduled_start_time", "")),
                "url": s.get("url", s.get("stream_url", "")),
                "matched_keywords": [kw for kw in keywords if kw in title],
            })
    return results

# ── 既存データ読み込み ────────────────────────────────────
def load_existing() -> list:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("streams", [])

# ── Discord通知 ───────────────────────────────────────────
def notify_discord(new_streams: list):
    if not DISCORD_WEBHOOK_URL or not new_streams:
        return
    lines = [f"**新しく{len(new_streams)}件の配信が見つかりました！**"]
    for s in new_streams:
        lines.append(f"🎙️ {s['liver_name']}  {s['title']}")
        if s.get("url"):
            lines.append(f"　<{s['url']}>")
    payload = {"content": "\n".join(lines)}
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        print(f"[INFO] Discord通知送信: {len(new_streams)}件")
    except Exception as e:
        print(f"[ERROR] Discord通知失敗: {e}")

# ── メイン ────────────────────────────────────────────────
def main():
    keywords = load_keywords()
    print(f"[INFO] キーワード: {keywords}")

    # 今日・明日のデータを取得して統合
    raw = []
    for offset in [0, 1]:
        fetched = fetch_streams(offset)
        print(f"[INFO] day_offset={offset}: {len(fetched)}件取得")
        raw.extend(fetched)

    filtered = filter_streams(raw, keywords)
    print(f"[INFO] フィルタ後: {len(filtered)}件")

    # 既存データとIDで差分チェック（通知用）
    existing_ids = {s["id"] for s in load_existing()}
    new_streams = [s for s in filtered if s["id"] not in existing_ids]
    print(f"[INFO] 新着: {len(new_streams)}件")

    # Discord通知（新着のみ）
    notify_discord(new_streams)

    # 保存
    os.makedirs("data", exist_ok=True)
    output = {
        "updated_at": datetime.now(JST).isoformat(),
        "keywords": keywords,
        "streams": filtered,
    }
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[INFO] {DATA_PATH} を更新しました")

if __name__ == "__main__":
    main()
