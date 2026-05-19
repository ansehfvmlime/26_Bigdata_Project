"""
로스트아크 경매장 OpenAPI 수집 스크립트
Usage:
    python collect.py              # 1회 수집
    python collect.py --schedule   # 2시간 간격 자동 수집
"""

import os
import json
import time
import argparse
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── 설정 ──────────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("LOSTARK_API_KEY", "")
BASE_URL = "https://developer-lostark.game.smilegate.net"
OUTPUT_DIR = Path("data/raw")
COLLECT_INTERVAL_SEC = 7200  # 2시간

CATEGORIES = {
    "생활재료": 90200,
    "오레하":   50010,
}

TARGET_ITEMS = {
    "생활재료": ["빙하의 숨결", "수렵물", "채집물", "벌목물", "광물"],
    "오레하":   ["오레하 융화 재료", "상급 오레하 융화 재료"],
}

HEADERS = {
    "accept": "application/json",
    "authorization": f"bearer {API_KEY}",
}

# ── 수집 함수 ──────────────────────────────────────────────────────────────────
def fetch_auction(category_code: int, item_name: str) -> dict:
    url = f"{BASE_URL}/markets/items"
    payload = {
        "Sort": "CURRENT_MIN_PRICE",
        "CategoryCode": category_code,
        "ItemName": item_name,
        "PageNo": 1,
        "SortCondition": "ASC",
    }
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def collect_all() -> list:
    collected_at = datetime.now().isoformat(timespec="seconds")
    results = []

    for category, items in TARGET_ITEMS.items():
        cat_code = CATEGORIES[category]
        for item_name in items:
            try:
                data = fetch_auction(cat_code, item_name)
                for record in (data.get("Items") or []):
                    results.append({
                        "collected_at": collected_at,
                        "category": category,
                        "item_name": item_name,
                        "grade": record.get("Grade", ""),
                        "price": record.get("CurrentMinPrice", 0),
                        "quantity": record.get("Quantity", 0),
                        "end_date": record.get("EndDate", ""),
                    })
                print(f"  ✓ [{category}] {item_name}: {len(data.get('Items') or [])}건")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ✗ [{category}] {item_name}: 오류 — {e}")

    return results


def save(records: list) -> Path:
    now = datetime.now()
    out_dir = OUTPUT_DIR / now.strftime("%Y-%m-%d") / now.strftime("%H")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"auction_{now.strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return out_file


# ── 메인 ──────────────────────────────────────────────────────────────────────
def run_once():
    if not API_KEY:
        print("[ERROR] LOSTARK_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  1. cp .env.example .env")
        print("  2. .env 파일에 실제 API 키 입력")
        return

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 수집 시작")
    records = collect_all()
    if records:
        path = save(records)
        print(f"[완료] {len(records)}건 저장 → {path}")
    else:
        print("[경고] 수집된 데이터가 없습니다.")


def run_scheduled():
    print(f"스케줄 수집 시작 (간격: {COLLECT_INTERVAL_SEC // 3600}시간)")
    while True:
        run_once()
        print(f"다음 수집까지 {COLLECT_INTERVAL_SEC // 3600}시간 대기...\n")
        time.sleep(COLLECT_INTERVAL_SEC)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", action="store_true", help="주기적 자동 수집 모드")
    args = parser.parse_args()

    if args.schedule:
        run_scheduled()
    else:
        run_once()
