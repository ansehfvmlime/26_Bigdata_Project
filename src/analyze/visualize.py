"""
분석 결과 시각화 스크립트
- Q1: 요일별 시세 라인 차트
- Q2: 제작 이득 히트맵
- Q3: 재료 상관관계 히트맵
- Q4: 이상치 분포 박스플롯
Usage:
    python src/analyze/visualize.py
"""

import json
import glob
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# 한글 폰트 설정 (HDP Sandbox 환경)
plt.rcParams["axes.unicode_minus"] = False
try:
    plt.rcParams["font.family"] = "NanumGothic"
except:
    plt.rcParams["font.family"] = "DejaVu Sans"

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 데이터 로딩 (raw JSON → pandas) ──────────────────────────────────────────
def load_raw_data() -> pd.DataFrame:
    files = glob.glob("data/raw/**/*.json", recursive=True)
    if not files:
        raise FileNotFoundError("data/raw/ 에 수집 데이터가 없습니다. collect.py 먼저 실행하세요.")
    records = []
    for f in files:
        with open(f, encoding="utf-8") as fp:
            records.extend(json.load(fp))
    df = pd.DataFrame(records)
    df["collected_at"] = pd.to_datetime(df["collected_at"])
    df["day_of_week"]  = df["collected_at"].dt.dayofweek  # 0=월 ~ 6=일
    df["hour_of_day"]  = df["collected_at"].dt.hour
    df["day_label"]    = df["collected_at"].dt.day_name()
    return df


# ── Q1: 요일별 시세 라인 차트 ────────────────────────────────────────────────
def plot_q1(df: pd.DataFrame):
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_kr    = ["월","화","수(초기화)","목","금","토","일"]

    df_mat = df[df["category"] == "생활재료"]
    pivot  = df_mat.groupby(["item_name", "day_label"])["price"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    for item in pivot["item_name"].unique():
        sub = pivot[pivot["item_name"] == item].set_index("day_label")
        sub = sub.reindex(day_order)
        ax.plot(day_kr, sub["price"].values, marker="o", label=item)

    ax.axvline(x=2, color="red", linestyle="--", alpha=0.5, label="레이드 초기화(수)")
    ax.set_title("Q1. 요일별 생활재료 평균 시세")
    ax.set_xlabel("요일")
    ax.set_ylabel("평균가 (골드)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "q1_daily_trend.png", dpi=150)
    plt.close()
    print("  ✓ Q1 저장: results/q1_daily_trend.png")


# ── Q2: 제작 이득 히트맵 ─────────────────────────────────────────────────────
def plot_q2(df: pd.DataFrame):
    recipe = pd.read_csv("data/recipe/oreha_recipe.csv")
    df_mat = df[df["category"] == "생활재료"][["collected_at","item_name","price","day_of_week"]] \
               .rename(columns={"item_name":"material_name","price":"material_price"})
    df_ore = df[df["category"] == "오레하"][["collected_at","item_name","price"]] \
               .rename(columns={"item_name":"result_item","price":"market_price"})

    merged = recipe.merge(df_mat, on="material_name", how="inner")
    merged["material_cost"] = merged["material_price"] * merged["quantity"]
    craft_cost = merged.groupby(["result_item","collected_at","day_of_week"]) \
                       .agg(craft_cost=("material_cost","sum"),
                            craft_fee=("craft_fee","first")).reset_index()
    craft_cost["total_cost"] = craft_cost["craft_cost"] + craft_cost["craft_fee"]

    final = craft_cost.merge(df_ore, on=["result_item","collected_at"], how="inner")
    final["profit"] = final["market_price"] - final["total_cost"]

    pivot = final.groupby(["result_item","day_of_week"])["profit"].mean().unstack()
    pivot.columns = ["월","화","수","목","금","토","일"]

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn",
                center=0, linewidths=0.5, ax=ax)
    ax.set_title("Q2. 요일별 제작 이득 (골드) — 초록=이득, 빨강=손해")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "q2_craft_profit.png", dpi=150)
    plt.close()
    print("  ✓ Q2 저장: results/q2_craft_profit.png")


# ── Q3: 상관관계 히트맵 ──────────────────────────────────────────────────────
def plot_q3(df: pd.DataFrame):
    items = ["빙하의 숨결","수렵물","채집물","벌목물","광물"]
    df_mat = df[df["item_name"].isin(items)]
    pivot  = df_mat.groupby(["collected_at","item_name"])["price"].mean().unstack()
    corr   = pivot.corr()

    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                vmin=-1, vmax=1, linewidths=0.5, ax=ax)
    ax.set_title("Q3. 생활재료 간 가격 상관관계")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "q3_correlation.png", dpi=150)
    plt.close()
    print("  ✓ Q3 저장: results/q3_correlation.png")


# ── Q4: 이상치 박스플롯 ──────────────────────────────────────────────────────
def plot_q4(df: pd.DataFrame):
    items = ["빙하의 숨결","수렵물","채집물","오레하 융화 재료","상급 오레하 융화 재료"]
    df_sub = df[df["item_name"].isin(items)]

    fig, ax = plt.subplots(figsize=(12, 6))
    df_sub.boxplot(column="price", by="item_name", ax=ax,
                   flierprops=dict(marker="o", color="red", markersize=4))
    ax.set_title("Q4. 아이템별 가격 분포 및 이상치")
    ax.set_xlabel("아이템")
    ax.set_ylabel("가격 (골드)")
    plt.suptitle("")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "q4_anomaly.png", dpi=150)
    plt.close()
    print("  ✓ Q4 저장: results/q4_anomaly.png")


# ── 메인 ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[시각화 시작]")
    try:
        df = load_raw_data()
        print(f"  데이터 로딩 완료: {len(df)}건\n")
        plot_q1(df)
        plot_q2(df)
        plot_q3(df)
        plot_q4(df)
        print("\n[완료] 모든 시각화 저장 → results/ 폴더 확인")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
