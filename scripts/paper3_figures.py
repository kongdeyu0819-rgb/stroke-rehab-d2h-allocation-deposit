# -*- coding: utf-8 -*-
"""
Paper 3 (Health Policy 投稿版) 三张配图
========================================
Figure 1: 政策设计逻辑图 (WHA79.10 -> Gap 双口径靶向 -> D2H 设施三分支)
Figure 2: 15 国 2023 锚定年 Gap 条图 (S1 vs S2, 9 优先国高亮)
Figure 3: 9 优先国剂量反应曲线 (0-2pp 实线观测区间 + 至 δ* 虚线样本外)

数据源: 建模步骤/13_D2H三情景配置/output/d2h_scenarios.csv, d2h_dose_response.csv (2026-08-07 δ* 修正版)
纪律: TNR 字体, dpi=300, 蓝=需求/橙=供给/红=Gap
生成: 2026-08-07 | 主理人: 心灵导师
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = r"D:\D\我的论文\脑卒中全球卫生"
STEP13 = os.path.join(ROOT, "建模步骤", "13_D2H三情景配置", "output")
OUT = os.path.join(ROOT, "论文写作路线图", "论文3", "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#444444",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "text.color": "#222222",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})

# 项目配色纪律
C_DEMAND = "#2c6fbb"   # 蓝 = 需求
C_SUPPLY = "#e8853d"   # 橙 = 供给
C_GAP    = "#c0392b"   # 红 = Gap
C_NEG    = "#8da9c4"   # 负 Gap 用灰蓝
C_GREY   = "#5a5a5a"

COUNTRY_NAMES = {
    "CN": "China", "ID": "Indonesia", "VN": "Vietnam", "MM": "Myanmar",
    "TH": "Thailand", "LA": "Laos", "KH": "Cambodia", "JP": "Japan",
    "MY": "Malaysia", "PH": "Philippines", "SG": "Singapore", "BN": "Brunei",
    "KR": "Korea", "GB": "United Kingdom", "US": "United States",
}

scen = pd.read_csv(os.path.join(STEP13, "d2h_scenarios.csv"))
dose = pd.read_csv(os.path.join(STEP13, "d2h_dose_response.csv"))

s1 = scen[scen.scenario == "S1_baseline"].set_index("country")
s2 = scen[scen.scenario.str.startswith("S2")].set_index("country")
order = s1.sort_values("Gap", ascending=False).index.tolist()  # CN ... US
priority = [c for c in order if s1.loc[c, "Gap"] > 0]

# ---------------------------------------------------------------- Figure 2
def fig2():
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = np.arange(len(order))
    w = 0.38
    g1 = [s1.loc[c, "Gap"] for c in order]
    g2 = [s2.loc[c, "Gap"] for c in order]
    cols1 = [C_GAP if v > 0 else C_NEG for v in g1]
    cols2 = [C_GAP if v > 0 else C_NEG for v in g2]
    ax.bar(x - w/2, g1, w, color=cols1, edgecolor="white", linewidth=0.4,
           label="S1 baseline (2023 anchor)", zorder=3)
    ax.bar(x + w/2, g2, w, color=cols2, edgecolor="white", linewidth=0.4,
           alpha=0.55, hatch="//", label="S2 pessimistic (unemployment +2pp)", zorder=3)
    ax.axhline(0, color="#333333", linewidth=0.9, zorder=2)
    labels = []
    for c in order:
        name = COUNTRY_NAMES[c]
        labels.append(name + (" *" if c in priority else ""))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=8)
    ax.set_ylabel("Gap = D $-$ S (panel-relative index)")
    ax.set_ylim(min(g1 + g2) - 0.08, max(g1 + g2) + 0.10)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.995, 0.97, "* D2H operational priority (2023 rule)", transform=ax.transAxes,
            ha="right", va="top", fontsize=7.5, color=C_GREY)
    ax.set_title("Gap by country, 2023 anchor year: baseline vs pessimistic macro shock",
                 fontsize=9.5, pad=8)
    fig.savefig(os.path.join(OUT, "paper3_fig2_gap_2023anchor.png"))
    plt.close(fig)

# ---------------------------------------------------------------- Figure 3
def fig3():
    """双面板: (a) 观测区间 0-2pp 剂量反应曲线; (b) δ* 闭合剂量条图(标 illustrative)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.7),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    grid = [0.25, 0.5, 1.0, 2.0]
    cmap = plt.get_cmap("tab10")
    star = dose[dose["Gap_reduction_pct"] == 100.0].set_index("country")["delta_che_pp_GDP"]

    # Panel (a): 观测窗口内曲线; 端点标签只给分离度好的 MY/JP/KH, 其余六国进图例
    DIRECT = {"MY", "JP", "KH"}
    for i, c in enumerate(priority):
        sub = dose[(dose.country == c) & (dose.delta_che_pp_GDP.isin(grid))].sort_values("delta_che_pp_GDP")
        xs = [0.0] + sub.delta_che_pp_GDP.tolist()
        ys = [0.0] + [min(v, 100.0) for v in sub.Gap_reduction_pct.tolist()]
        col = cmap(i % 10)
        lw = 2.0 if c in ("JP", "MY", "CN") else 1.1
        ax1.plot(xs, ys, color=col, lw=lw, zorder=3,
                 label="_nolegend_" if c in DIRECT else f"{COUNTRY_NAMES[c]} ({ys[-1]:.0f}%)")
        dstar = star.get(c, np.nan)
        if pd.notna(dstar) and dstar <= 2.0:  # MY 在观测窗口内闭合
            ax1.plot([dstar], [100.0], marker="o", ms=4.5, color=col, zorder=4)
        if c in DIRECT:
            ax1.annotate(COUNTRY_NAMES[c], (2.0, ys[-1]), textcoords="offset points",
                         xytext=(5, -3), fontsize=7.5, color=col)
    ax1.legend(frameon=False, fontsize=7, loc="upper left", handlelength=1.6,
               borderaxespad=0.1, labelspacing=0.35)
    ax1.set_xlim(0, 2.75)
    ax1.set_ylim(0, 105)
    ax1.set_xlabel("CHE increase (pp of GDP)", fontsize=8.5)
    ax1.set_ylabel("Gap reduction (%)", fontsize=8.5)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_title("(a) Observed dosing window (0-2 pp)", fontsize=9, pad=6)

    # Panel (b): δ* 条图（按闭合剂量升序）
    star_s = star.sort_values()
    names = [COUNTRY_NAMES[c] for c in star_s.index]
    vals = star_s.values
    colors = [C_GAP if v > 2.0 else "#7a9e7e" for v in vals]
    bars = ax2.barh(np.arange(len(vals)), vals, color=colors, edgecolor="white",
                    linewidth=0.4, height=0.62, zorder=3)
    for i, v in enumerate(vals):
        ax2.text(v + 0.3, i, f"+{v:.1f}", va="center", fontsize=7.5, color="#333333")
    ax2.set_yticks(np.arange(len(vals)))
    ax2.set_yticklabels(names, fontsize=8)
    ax2.invert_yaxis()
    ax2.axvline(2.0, color=C_GREY, lw=0.9, ls=(0, (4, 3)), zorder=2)
    ax2.text(3.6, 0.0, "edge of observed window", fontsize=6.8,
             color=C_GREY, va="top", ha="left")
    ax2.set_xlim(0, 26)
    ax2.set_xlabel("Illustrative closure dose δ* (pp of GDP)", fontsize=8.5)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.set_title("(b) Full-closure dose δ* (out-of-sample,\nillustrative only)", fontsize=9, pad=6)

    fig.suptitle("Dose-response of the Gap to health-expenditure injections, 9 priority countries",
                 fontsize=9.5, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "paper3_fig3_dose_response.png"))
    plt.close(fig)

# ---------------------------------------------------------------- Figure 1
def fig1():
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    def box(x, y, w, h, text, fc, ec, fs=8.2, tc="white", lw=1.0):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.08",
                           fc=fc, ec=ec, lw=lw, zorder=2)
        ax.add_patch(p)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
                color=tc, zorder=3, linespacing=1.45)
        return p

    def arrow(p1, p2, color=C_GREY, lw=1.4):
        """p1/p2 = 显式坐标点 (x, y)，直线箭头"""
        a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=13,
                            color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=1)
        ax.add_patch(a)

    # 顶层: 政策窗口
    b0 = box(2.6, 8.6, 4.8, 1.15,
             "WHA79.10 (May 2026)\nfirst stroke resolution in WHA history\n"
             "rehabilitation as one of four pillars", "#3b4a5a", "#26313c", fs=8.4)

    # 中层: 双路径 Gap
    b1 = box(0.4, 5.9, 2.9, 1.35,
             "Demand pathway\nmacro shock -> rehab need D\n(demand-driven signal:\nimportance ranking 96.6%)",
             C_DEMAND, "#1d4e89", fs=7.8)
    b2 = box(6.7, 5.9, 2.9, 1.35,
             "Supply pathway\nbudget compression -> capacity S\n(PT density only comparable\nworkforce series)", C_SUPPLY, "#b25f1e", fs=7.8)
    b3 = box(3.3, 3.9, 3.4, 1.15,
             "Gap = D - S\nmarket-failure node, 15-country panel\n52.9% of country-years positive",
             C_GAP, "#8e2a20", fs=8.0)

    # 靶向规则
    b4 = box(0.4, 1.9, 4.5, 1.15,
             "Targeting rules (stated jointly)\nstructural: mean Gap > 0, 2010-2023 (8 economies)\noperational: Gap > 0, 2023 anchor (9 countries)",
             "#ffffff", C_GAP, fs=7.6, tc="#8e2a20", lw=1.2)
    # 设施设计三分支
    b5 = box(5.4, 1.9, 4.2, 1.15,
             "Debt-for-health facility, by debt profile\n"
             "conversion (high-debt LMICs) | repurposing\n"
             "(middle-income) | reallocation (Japan)", "#ffffff", "#3b4a5a",
             fs=7.4, tc="#26313c", lw=1.2)
    # 底层结果
    b6 = box(2.6, 0.15, 4.8, 1.0,
             "Allocation output: 9 priority countries\n"
             "Japan costed case: +16,951 PTs / US$1.441 B",
             "#eef3f8", "#3b4a5a", fs=7.6, tc="#26313c", lw=1.2)

    arrow((3.6, 8.55), (1.85, 7.30))            # b0 -> b1
    arrow((6.4, 8.55), (8.15, 7.30))            # b0 -> b2
    arrow((1.85, 5.84), (4.3, 5.10), color=C_DEMAND)   # b1 -> b3
    arrow((8.15, 5.84), (5.7, 5.10), color=C_SUPPLY)   # b2 -> b3
    arrow((4.2, 3.84), (2.65, 3.10), color=C_GAP)      # b3 -> b4
    arrow((5.8, 3.84), (7.5, 3.10), color=C_GAP)       # b3 -> b5
    arrow((2.65, 1.84), (3.8, 1.20))            # b4 -> b6
    arrow((7.5, 1.84), (6.2, 1.20))             # b5 -> b6

    ax.set_title("From the WHA79.10 policy window to a targeted debt-for-health allocation",
                 fontsize=9.5, pad=6)
    fig.savefig(os.path.join(OUT, "paper3_fig1_design_logic.png"))
    plt.close(fig)

if __name__ == "__main__":
    fig1(); fig2(); fig3()
    print("priority:", priority)
    print("figures written to", OUT)
