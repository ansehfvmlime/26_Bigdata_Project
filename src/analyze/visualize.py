# -*- coding: utf-8 -*-
"""
분석 결과 시각화 스크립트
- Q1: 요일별 시세 라인 차트 (재련추가)
- Q2: 요일별 제작 이득률 막대 그래프
- Q3: 요일-가격 상관계수 수평 막대 그래프
- Q4: 유물각인서 이상치 빈도 및 요일별 분포
Usage:
    python3.6 src/analyze/visualize.py
"""
from __future__ import print_function, unicode_literals
import os
import sys

# 한글 출력 설정
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 한글 폰트 설정
def set_korean_font():
    font_candidates = [
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/nanum/NanumGothic.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for font_path in font_candidates:
        if os.path.exists(font_path):
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            break
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

OUTPUT_DIR = "results"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

DAYS = [u'일', u'월', u'화', u'수', u'목', u'금', u'토']
DAYS_NUM = [1, 2, 3, 4, 5, 6, 7]

# ── Q1: 요일별 재련추가 시세 라인 차트 ───────────────────────────────────────
def plot_q1():
    items = {
        u'달의 숨결':   [139, 138, 138, 188, 165, 142, 139],
        u'빙하의 숨결': [297, 287, 281, 271, 278, 304, 312],
        u'용암의 숨결': [369, 354, 348, 368, 376, 391, 384],
    }
    colors = ['#185FA5', '#0F6E56', '#D85A30']

    fig, ax = plt.subplots(figsize=(10, 5))

    for (name, values), color in zip(items.items(), colors):
        ax.plot(DAYS, values, marker='o', label=name, color=color,
                linewidth=2, markersize=6)
        for i, v in enumerate(values):
            ax.annotate(str(v), (DAYS[i], v),
                       textcoords="offset points", xytext=(0, 8),
                       ha='center', fontsize=8, color=color)

    ax.axvline(x=3, color='red', linestyle='--', alpha=0.4, linewidth=1.5)
    ax.text(3.1, ax.get_ylim()[1] * 0.95, u'레이드 초기화(수)',
            color='red', fontsize=9, alpha=0.7)

    ax.set_title(u'Q1. 요일별 재련추가 아이템 평균 시세', fontsize=14, pad=15)
    ax.set_xlabel(u'요일', fontsize=11)
    ax.set_ylabel(u'평균가 (골드)', fontsize=11)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'q1_daily_trend.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print("  [완료] Q1 저장: " + path)


# ── Q2: 요일별 제작 이득률 막대 그래프 ───────────────────────────────────────
def plot_q2():
    items = {
        u'아비도스 융화 재료':    [93.1, 90.6, 88.1, 94.8, 98.1, 94.9, 95.9],
        u'상급 아비도스 융화 재료': [87.4, 84.9, 93.7, 84.0, 78.0, 75.0, 89.9],
        u'오레하 융화 재료':      [71.3, 55.9, 45.5, 66.2, 76.2, 69.0, 78.6],
        u'상급 오레하 융화 재료':  [50.0, 50.0, 55.2, 64.3, 75.3, 62.4, 50.0],
        u'최상급 오레하 융화 재료': [99.7, 69.4, 76.2, 62.0, 42.5, 80.1, 95.8],
    }
    colors = ['#0F6E56', '#1D9E75', '#185FA5', '#378ADD', '#854F0B']

    x = np.arange(len(DAYS))
    width = 0.15
    n = len(items)
    offsets = np.linspace(-(n-1)/2, (n-1)/2, n) * width

    fig, ax = plt.subplots(figsize=(13, 6))

    for (name, values), color, offset in zip(items.items(), colors, offsets):
        bars = ax.bar(x + offset, values, width, label=name,
                      color=color, alpha=0.85, edgecolor='white', linewidth=0.5)

    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(6.6, 51.5, u'50% 기준선', color='gray', fontsize=8)

    ax.set_title(u'Q2. 요일별 제작 이득률 (profitable_pct %)', fontsize=14, pad=15)
    ax.set_xlabel(u'요일', fontsize=11)
    ax.set_ylabel(u'이득 확률 (%)', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(DAYS)
    ax.set_ylim(0, 115)
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'q2_craft_profit.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print("  [완료] Q2 저장: " + path)


# ── Q3: 요일-가격 상관계수 수평 막대 그래프 ──────────────────────────────────
def plot_q3():
    items = [
        u'정제된 파괴강석',
        u'상급 아비도스 융화 재료',
        u'생명의 돌파석',
        u'태양의 가호',
        u'운명의 파괴석 결정',
        u'달의 숨결',
        u'태양의 축복',
        u'빙하의 숨결',
        u'경이로운 명예의 돌파석',
    ]
    corrs = [-0.4119, -0.1351, -0.1329, 0.1213, 0.1044, 0.0970, 0.0954, 0.2103, 0.3527]

    sorted_pairs = sorted(zip(corrs, items))
    corrs_sorted = [p[0] for p in sorted_pairs]
    items_sorted = [p[1] for p in sorted_pairs]
    colors = ['#D85A30' if c < 0 else '#0F6E56' for c in corrs_sorted]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(items_sorted, corrs_sorted, color=colors, alpha=0.85,
                   edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, corrs_sorted):
        x_pos = val + (0.01 if val >= 0 else -0.01)
        ha = 'left' if val >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                '{:.4f}'.format(val), va='center', ha=ha, fontsize=9)

    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.axvline(x=0.3, color='#0F6E56', linestyle='--', alpha=0.4, linewidth=1)
    ax.axvline(x=-0.3, color='#D85A30', linestyle='--', alpha=0.4, linewidth=1)
    ax.text(0.31, -0.5, u'유의미 기준\n(|r|>0.3)', color='gray', fontsize=8, va='top')

    ax.set_title(u'Q3. 요일-가격 상관계수 (재련재료/재련추가)', fontsize=14, pad=15)
    ax.set_xlabel(u'상관계수 (음수: 주말로 갈수록 하락 / 양수: 상승)', fontsize=10)
    ax.set_xlim(-0.55, 0.55)
    ax.grid(True, axis='x', alpha=0.3)
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#D85A30', alpha=0.85, label=u'음의 상관 (주말로 갈수록 하락)'),
        Patch(facecolor='#0F6E56', alpha=0.85, label=u'양의 상관 (주말로 갈수록 상승)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'q3_correlation.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print("  [완료] Q3 저장: " + path)


# ── Q4: 유물각인서 이상치 시각화 ─────────────────────────────────────────────
def plot_q4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 왼쪽: 아이템별 이상치 빈도 Top 10
    items_freq = [
        u'아드레날린', u'마나의 흐름', u'구슬동자',
        u'기습의 대가', u'급소 타격', u'바리케이드',
        u'예리한 둔기', u'안정된 상태', u'전문의', u'중갑 착용'
    ]
    counts = [90, 77, 63, 58, 54, 51, 43, 41, 37, 32]
    discounts = [7.9, 33.0, 30.1, 10.3, 63.1, 38.8, 7.2, 47.9, 17.0, 49.4]

    colors_freq = ['#D85A30' if d > 30 else '#378ADD' for d in discounts]
    bars1 = ax1.barh(items_freq[::-1], counts[::-1],
                     color=colors_freq[::-1], alpha=0.85,
                     edgecolor='white', linewidth=0.5)

    for bar, cnt, disc in zip(bars1, counts[::-1], discounts[::-1]):
        ax1.text(bar.get_width() + 1,
                 bar.get_y() + bar.get_height()/2,
                 u'{}건 ({:.1f}% 할인)'.format(cnt, disc),
                 va='center', fontsize=8)

    ax1.set_title(u'Q4-1. 유물각인서 이상치 빈도 Top 10', fontsize=12, pad=10)
    ax1.set_xlabel(u'이상치 발생 건수', fontsize=10)
    ax1.set_xlim(0, 130)
    ax1.grid(True, axis='x', alpha=0.3)
    ax1.set_facecolor('#FAFAFA')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#D85A30', alpha=0.85, label=u'할인율 30% 초과'),
        Patch(facecolor='#378ADD', alpha=0.85, label=u'할인율 30% 이하'),
    ]
    ax1.legend(handles=legend_elements, loc='lower right', fontsize=8)

    # 오른쪽: 요일별 이상치 발생 빈도
    day_counts = [60, 38, 17, 49, 485, 40, 36]
    bar_colors = ['#D85A30' if v > 200 else '#378ADD' for v in day_counts]

    bars2 = ax2.bar(DAYS, day_counts, color=bar_colors, alpha=0.85,
                    edgecolor='white', linewidth=0.5, width=0.6)

    for bar, val in zip(bars2, day_counts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 str(val), ha='center', va='bottom', fontsize=10,
                 fontweight='bold' if val > 200 else 'normal')

    ax2.set_title(u'Q4-2. 요일별 이상치 발생 빈도', fontsize=12, pad=10)
    ax2.set_xlabel(u'요일', fontsize=10)
    ax2.set_ylabel(u'이상치 건수', fontsize=10)
    ax2.set_ylim(0, 560)
    ax2.grid(True, axis='y', alpha=0.3)
    ax2.set_facecolor('#FAFAFA')

    total = sum(day_counts)
    ax2.text(4, 495,
             u'목요일 {:.1f}%\n({}/{}건)'.format(485/total*100, 485, total),
             ha='center', fontsize=9, color='#D85A30',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       edgecolor='#D85A30', alpha=0.8))

    fig.patch.set_facecolor('white')
    plt.suptitle(u'Q4. 유물각인서 이상치(덤핑) 탐지 결과\n'
                 u'전체 114,243건 중 725건(0.63%) 탐지 | 기준: 평균가 - 2×표준편차',
                 fontsize=13, y=1.02)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'q4_anomaly.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print("  [완료] Q4 저장: " + path)


# ── 메인 ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[시각화 시작]")
    print("")
    plot_q1()
    plot_q2()
    plot_q3()
    plot_q4()
    print("")
    print("[완료] 모든 시각화 저장 완료 → results/ 폴더 확인")