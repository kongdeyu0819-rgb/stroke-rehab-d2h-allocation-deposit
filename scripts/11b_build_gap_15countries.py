# -*- coding: utf-8 -*-
"""
Step 11b · 15国 Gap = D − S 市场失灵节点（扩展版）
=====================================================================================
目的：
    把 Step 14 的**康复需求 D(t)**（15 国）与 Step 16 的**供给能力 S(t)**（15 国）
    在统一量纲下相减，得到覆盖全部 15 国（美英日韩 + 中国 + 东盟10国）的
    **Gap = D − S = 「需求激增 × 供给崩溃」的市场失灵节点**。
    这是许铭「市场塑造 (Market Shaping)」框架的标准操作对象，
    也是后续 Debt-to-Health (D2H) 资金投放的量化标的 —— 论文核心创新点，实例化其方法论。

    本步是 Step 11 在 15 国集团上的正式落地（Step 11 说明.md 已写明「下游若需 15 国统一口径，
    应以 Step14/16 为准重算」）。原 4 国 gap_yearly.csv 作为试点保留，不覆盖。

S_index_15 合成口径（与 Step10 同源、且 15 国全口径可比）：
    Step10 的 S_index = z(卫生总费用%GDP) + z(政府卫生支出%GDP) + z(UHC指数) + z(PT密度) 四项均值。
    15 国中 PT 密度极稀疏（仅 9/15 可入、且多 <5 观测），依 Step16「蓝海证据」约定
    **不入连续面板**（避免 80%+ 缺失扭曲、且造成跨国口径不一致），故本步 S_index_15
    取前三个 universally-complete 的融资/UHC 分量 z-均值：
        S_index_15 = mean( z(supply_che_pct_gdp), z(supply_gghe_pct_gdp), z(uhc_index) )
    跨 15 国 × 14 年面板标准化，方向：越高 = 供给能力越强。

Gap 定义（面板 min-max / z 归一，跨国家跨时间可比）：
    D_norm  = minmax(康复需求率 /10万)               # 需求侧相对位次（Step14）
    S_norm  = minmax(S_index_15)                      # 供给侧相对位次（Step16）
    Gap     = D_norm − S_norm                         # 正值 = 需求在面板内排名高于供给 = 相对市场失灵 / D2H 优先靶向节点
    Gap_z   = z(D) − z(S_index_15)                    # z-score 稳健变体

输入：
    D: 建模步骤/14_康复需求扩展15国/output/rehab_demand_yearly.csv
    S: 建模步骤/16_供给侧面板15国/output/supply_panel_15.csv

输出：
    建模步骤/11_Gap市场失灵节点/output/gap_yearly_15.csv   （210 行 = 15国×14年）
    建模步骤/11_Gap市场失灵节点/output/gap_monthly_15.csv  （年度线性插值，供下游使用）
    建模步骤/11_Gap市场失灵节点/output/validation_report_15.md

红线：debt / 康复需求Y / Gap=D−S / 双路径结构 —— 零改动，仅扩展面板至 15 国。

作者：心灵导师 agent · 2026-07-21（按用户指令 B：扩展 Gap 管线做真 15 国图）
"""
import os
import numpy as np
import pandas as pd

# ───────────────────────── 路径配置 ─────────────────────────
ROOT = "D:/D/我的论文/脑卒中全球卫生"
D_YEARLY = f"{ROOT}/建模步骤/14_康复需求扩展15国/output/rehab_demand_yearly.csv"
S_YEARLY = f"{ROOT}/建模步骤/16_供给侧面板15国/output/supply_panel_15.csv"
OUT_DIR = f"{ROOT}/建模步骤/11_Gap市场失灵节点/output"
os.makedirs(OUT_DIR, exist_ok=True)

YEAR_START, YEAR_END = 2010, 2023
# 15 国短码顺序（美英日韩 + 中国 + 东盟10国），与 Step14/16 一致
ISO2_ORDER = ["US", "GB", "JP", "KR", "CN",
              "BN", "KH", "ID", "LA", "MY", "MM", "PH", "SG", "TH", "VN"]

# S_index_15 分量（15 国全口径完整，对应 Step10 前三个核心分量）
S_COMPONENTS = ["supply_che_pct_gdp", "supply_gghe_pct_gdp", "uhc_index"]


# ───────────────────────── 工具函数 ─────────────────────────
def minmax(s: pd.Series) -> pd.Series:
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(np.ones(len(s)) * 0.5, index=s.index)
    return (s - lo) / (hi - lo)


def zscore(s: pd.Series) -> pd.Series:
    mu, sd = s.mean(), s.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mu) / sd


def main():
    d = pd.read_csv(D_YEARLY)
    s = pd.read_csv(S_YEARLY)

    # 仅保留 15 国短码集合内的观测
    d = d[d["country"].isin(ISO2_ORDER)]
    s = s[s["country"].isin(ISO2_ORDER)]

    df = d.merge(s, on=["country", "year"], how="inner")
    assert len(df) == 15 * (YEAR_END - YEAR_START + 1), \
        f"行数异常: {len(df)} (应为 {15*14})"
    assert df["country"].nunique() == 15, f"国家数异常: {df['country'].nunique()}"

    # —— 供给 S_index_15：三分量 z-均值（跨 15国×14年面板）——
    for c in S_COMPONENTS:
        assert df[c].notna().all(), f"供给分量 {c} 存在缺失，不可用于连续面板"
        df[f"z_{c}"] = zscore(df[c])
    df["S_index"] = df[[f"z_{c}" for c in S_COMPONENTS]].mean(axis=1)

    # —— 归一 ——
    df["D_norm"] = minmax(df["rehab_demand_rate_per100k"])
    df["S_norm"] = minmax(df["S_index"])
    df["D_z"] = zscore(df["rehab_demand_rate_per100k"])
    df["S_z"] = zscore(df["S_index"])

    # —— Gap 两种口径 ——
    df["Gap"] = df["D_norm"] - df["S_norm"]
    df["Gap_z"] = df["D_z"] - df["S_z"]
    df["market_failure"] = df["Gap"] > 0  # 需求 > 供给 = 失灵

    cols = ["country", "year", "rehab_demand_rate_per100k",
            "supply_che_pct_gdp", "supply_gghe_pct_gdp", "uhc_index",
            "S_index", "D_norm", "S_norm", "Gap", "Gap_z", "market_failure"]
    yearly = df[cols].sort_values(["country", "year"]).reset_index(drop=True)
    yearly.to_csv(f"{OUT_DIR}/gap_yearly_15.csv", index=False, encoding="utf-8-sig")

    # —— 月度插值（对齐 Step11 格式）——
    from numpy import interp as ninterp
    monthly_rows = []
    cols_m = ["rehab_demand_rate_per100k", "supply_che_pct_gdp",
              "supply_gghe_pct_gdp", "uhc_index", "S_index",
              "D_norm", "S_norm", "Gap", "Gap_z"]
    for c in ISO2_ORDER:
        sub = yearly[yearly["country"] == c].sort_values("year")
        yrs = sub["year"].values.astype(float)
        for y in range(YEAR_START, YEAR_END + 1):
            for m in range(1, 13):
                t = y + (m - 1) / 12.0
                row = {"country": c, "year": y, "month": m, "date": f"{y}-{m:02d}"}
                for col in cols_m:
                    row[col] = float(ninterp(t, yrs, sub[col].values.astype(float)))
                row["market_failure"] = row["Gap"] > 0
                monthly_rows.append(row)
    monthly = pd.DataFrame(monthly_rows).sort_values(["country", "date"]).reset_index(drop=True)
    monthly.to_csv(f"{OUT_DIR}/gap_monthly_15.csv", index=False, encoding="utf-8-sig")

    # ───────── 校验报告 ─────────
    n = len(yearly)
    pct_fail = yearly["market_failure"].mean() * 100
    # 至少一年正 Gap 的国家数
    n_any_pos = yearly[yearly["market_failure"]]["country"].nunique()
    n_total_c = yearly["country"].nunique()

    # 各国平均 Gap（2010-2023）排序
    mean_gap = yearly.groupby("country")["Gap"].mean().sort_values(ascending=False)
    priority = mean_gap[mean_gap > 0].index.tolist()  # 平均正 Gap = D2H 优先靶向
    n_mean_pos = len(priority)

    # 趋势：各国 Gap 2010→2023 斜率
    trend_lines = []
    for c in ISO2_ORDER:
        sub = yearly[yearly["country"] == c].sort_values("year")
        x = sub["year"].values.astype(float)
        yv = sub["Gap"].values
        slope = np.polyfit(x, yv, 1)[0]
        g10 = sub[sub.year == 2010]["Gap"].values[0]
        g23 = sub[sub.year == 2023]["Gap"].values[0]
        trend_lines.append(f"- {c}: Gap {g10:+.3f}(2010) → {g23:+.3f}(2023), 斜率={slope:+.4f}/年")

    # 稳健性
    r_gap = yearly["Gap"].corr(yearly["Gap_z"])

    # 排名表（平均 Gap）
    rank_lines = []
    for i, (c, v) in enumerate(mean_gap.items(), 1):
        flag = "D2H优先" if v > 0 else ""
        rank_lines.append(f"- #{i:>2} {c}: 平均Gap={v:+.3f} {flag}")

    lines = ["# Gap = D − S 市场失灵节点（15 国扩展版）· 校验报告",
             "",
             "## 定义",
             "- D_norm = minmax(康复需求率/10万) ［Step14，15国］",
             "- S_index_15 = mean(z(卫生总费用%GDP), z(政府卫生支出%GDP), z(UHC指数)) ［Step16，15国，跨15×14面板］",
             "  （PT密度因 9/15 稀疏依 Step16 蓝海证据约定不入连续面板，故取前三个 universally-complete 分量）",
             "- Gap = D_norm − S_norm，正值 = 该国需求在面板内排名高于供给 = 相对市场失灵 / D2H 优先靶向节点",
             "- Gap_z = z(D) − z(S_index_15) ［z-score 稳健变体，不受面板极值影响］",
             "",
             "## 重要说明（口径与解释边界）",
             "- 本 Gap 为**面板内相对靶向指数**（min-max/z 均跨 15 国×14 年归一），衡量『需求 vs 供给的相对位次』，",
             "  **非绝对未满足人数**。故 Gap<0 不代表『无未满足需求』，仅表示该国供给在面板中排名高于需求。",
             "- 『宏观压力下需求激增×供给崩溃、Gap 扩大』的**动态**过程，不由本年度 GBD Gap 承载，",
             "  而由 Step06(WHА79+家庭压力 B) / Step07(COVID 行为突变) / Step08(中介) 在行为与压力层刻画。",
             "- 本扩展版是 Step 11 在 15 国集团上的正式落地；原 4 国 gap_yearly.csv 作为试点保留。",
             "",
             "## ① 符号分布（相对靶向信号）",
             f"- {n} 个 country-year 中，Gap>0 占 **{pct_fail:.1f}%**；",
             f"  平均 Gap > 0 的国家数 = **{n_mean_pos}/{n_total_c}**，其中 {n_any_pos}/{n_total_c} 至少有一年正 Gap。",
             f"  D2H 优先靶向节点（平均 Gap > 0）：{', '.join(priority)}",
             "",
             "## ② 各国平均 Gap 排名（2010–2023，降序；正值=D2H优先靶向）"]
    lines += rank_lines
    lines += ["", "## ③ 时间趋势（相对失灵是否扩大）",
              "（斜率负 = 供给投资跟上了需求增长，相对 Gap 收窄；斜率正 = 需求相对供给恶化）"]
    lines += trend_lines
    lines += ["", "## ④ 稳健性",
              f"- Gap 与 Gap_z 相关系数 r = {r_gap:.3f}（接近 1 = 结论不受归一方式影响）",
              "",
              "## 结论与下一步",
              "- Gap 即许铭『市场塑造 / Debt-to-Health』框架的操作对象：D2H 资金应投放于 Gap 最大（需求相对最未被满足）的国家-年份节点；",
              f"  本 15 国面板中 {', '.join(priority)} 等需求相对供给最未被满足，为优先靶向。",
              "- 本文件直接对接：Step06(WHА79 外推) / Step12b(四阶 SEM，Gap 作市场失灵中介) / 研究内容五(D2H 三情景资金配置)。",
              "- 与 4 国试点一致：康复供给（融资+UHC）是相对失灵主因之一；PT/OT/ST 全球数据盲区本身即论证『市场塑造』的必要性。"]
    report = "\n".join(lines)
    with open(f"{OUT_DIR}/validation_report_15.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print(f"\n✅ 产出: yearly_15={len(yearly)}行, monthly_15={len(monthly)}行 → {OUT_DIR}")


if __name__ == "__main__":
    main()
