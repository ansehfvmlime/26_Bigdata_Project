# -*- coding: utf-8 -*-
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
BASE_URL = "https://developer-lostark.game.onstove.com"
OUTPUT_DIR = Path("data/raw")
COLLECT_INTERVAL_SEC = 7200  # 2시간

CATEGORIES = {
    "식물채집": 90200,
    "벌목":    90300,
    "채광":    90400,
    "수렵":    90500,
    "낚시":    90600,
    "고고학":  90700,
    "재련재료": 50010,
    "재련추가": 50020,
    "유물각인서": 40000,
}

TARGET_ITEMS = {
    "식물채집": ["들꽃", "수줍은 들꽃", "아비도스 들꽃", "화사한 들꽃"],
    "벌목":    ["목재", "부드러운 목재", "튼튼한 목재", "아비도스 목재"],
    "채광":    ["철광석", "묵직한 철광석", "단단한 철광석", "아비도스 철광석"],
    "수렵":    ["진귀한 가죽", "두툼한 생고기", "수렵의 결정", "다듬은 생고기", "아비도스 두툼한 생고기", "오레하 두툼한 생고기"],
    "낚시":    ["낚시의 결정", "생선", "붉은 살 생선", "오레하 태양 잉어", "아비도스 태양 잉어"],
    "고고학":  ["진귀한 유물", "고대 유물", "희귀한 유물", "고고학의 결정", "오레하 유물", "아비도스 유물"],
    "재련재료": ["수호석 조각", "수호석 결정", "수호강석", "파괴석 조각", "파괴석 결정","정제된 수호강석", "조화의 돌파석", "위대한 명예의 돌파석", "운명의 수호석","운명의 돌파석", "파괴강석", "위대한 운명의 돌파석", "상급 오레하 융화 재료","파괴석", "명예의 돌파석", "경이로운 명예의 돌파석", "생명의 돌파석","운명의 수호석 결정", "오레하 융화 재료", "수호석", "정제된 파괴강석","최상급 오레하 융화 재료", "아비도스 융화 재료", "상급 아비도스 융화 재료","찬란한 명예의 돌파석", "운명의 파괴석", "운명의 파괴석 결정"],
    "재련추가": ["별의 숨결", "태양의 은총", "태양의 축복", "태양의 가호","달의 숨결", "빙하의 숨결", "용암의 숨결"],
    "유물각인서": [
    "유물 탈출의 명수 각인서", "유물 실드관통 각인서", "유물 굳은 의지 각인서",
    "유물 강화 방패 각인서", "유물 여신의 가호 각인서", "유물 에테르 포식자 각인서",
    "유물 불굴 각인서", "유물 최대 마나 증가 각인서", "유물 번개의 분노 각인서",
    "유물 부러진 뼈 각인서", "유물 약자 무시 각인서", "유물 강령술 각인서",
    "유물 위기 모면 각인서", "유물 시선 집중 각인서", "유물 폭발물 전문가 각인서",
    "유물 달인의 저력 각인서", "유물 분쇄의 주먹 각인서", "유물 추진력 각인서",
    "유물 긴급구조 각인서", "유물 선수필승 각인서", "유물 급소 타격 각인서",
    "유물 승부사 각인서", "유물 정밀 단도 각인서", "유물 정기 흡수 각인서",
    "유물 안정된 상태 각인서", "유물 마나 효율 증가 각인서", "유물 바리케이드 각인서",
    "유물 중갑 착용 각인서", "유물 속전속결 각인서", "유물 구슬동자 각인서",
    "유물 마나의 흐름 각인서", "유물 결투의 대가 각인서", "유물 슈퍼 차지 각인서",
    "유물 전문의 각인서", "유물 타격의 대가 각인서", "유물 각성 각인서",
    "유물 저주받은 인형 각인서", "유물 기습의 대가 각인서", "유물 질량 증가 각인서",
    "유물 아드레날린 각인서", "유물 예리한 둔기 각인서", "유물 원한 각인서",
    "유물 돌격대장 각인서",
],
}

HEADERS = {
    "accept": "application/json",
    "authorization": f"bearer {API_KEY}",
}

# ── 수집 함수 ──────────────────────────────────────────────────────────────────
def fetch_auction(category_code, item_name):
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
