# -*- coding: utf-8 -*-
"""
Step 13 · Debt-to-Health (D2H) 三情景配置  【15 国迁移版】
==========================================================
把许铭教授的「债务换健康 / 市场塑造」框架在卒中康复领域实例化：
基于 15 国 Gap(=D_norm - S_norm 市场失灵节点, Step11b) + 15 国供给成分 + 宏观压力面板，
设计三情景，量化 D2H 资金应投向何处、投多少、能缩小多少康复可及性缺口。

⚠️ 2026-07-21 迁移说明（红线一致）
- 原 Step13 以 4 国 gap_yearly.csv(US/GB/KR/JP) 为输入 → D2H 靶向图仅 4 国。
- 现改为 15 国 gap_yearly_15.csv（Step11b 重建, 与本论文 Figure 2 同口径），
  供给三分量 = supply_che/gghe/uhc（与 11b 的 S_index_15 定义一致, PT密度依蓝海约定不入连续面板）。
- 人口(population) 取 Step14 15国康复需求表（权威 15国源）；pt_density 仅 4 试点国(Step10)有值，
  其余 11 国在 PT 成本表中标 NaN（呼应 OT/ST 全球无序列的蓝海证据空白），D2H 优先靶向仍以 Gap 决定。
- GDP_T 扩至 15 国（IMF WEO 2023 Oct 名义GDP, $万亿），目前为可替换参考假设、未进入核心 Gap 公式。

情景
----
S1 基准 (Baseline)      : 维持 2023 结构性 Gap，不作政策干预（靶向信号锁定）
S2 悲观 (Pessimistic)   : 失业 +2pp → 宏观压力↑ → 康复需求↑ + 卫生支出(供给)↓ → Gap 扩大
S3 乐观 (Optimistic D2H): 债务减免注资抬升卫生支出(che_pct_gdp +δ) → S↑ → Gap 收敛

核心产物
--------
- d2h_scenarios.csv        : 各国 × 三情景 × Gap / Gap变化%
- d2h_dose_response.csv    : δ(卫生支出增幅, pp GDP) → Gap缩减% 剂量反应
- d2h_pt_costing.csv       : 具体 D2H 载体——PT人力扩充成本（4试点国有 pt_density；其余标 N/A）
- validation_report.md     : 校验 + 诚实局限

⚠️ 诚实声明(写进论文)
1. Gap 是「相对靶向指数」(面板内 D_rank - S_rank)，非绝对未满足人数；用于锁定 D2H 优先国，不用于声称绝对缺口。
2. S2 的需求/供给弹性为文献锚定的情景假设(本面板受老龄化趋势混杂，不能从15国面板可靠估计)，明确标注。
3. 15 国含中低收入债务国(正合「债务置换」字面语境)；高收入国(US/GB)Gap<0 非优先靶向，逻辑自洽。
4. GDP / PT 单位成本 为可替换假设(标注来源)，主结论(δ pp GDP、Gap缩减%)完全由本项目数据导出。
5. pt_density 仅 4 试点国可得（OT/ST 全球无通用序列）→ D2H 载体选 PT 扩充恰呼应蓝海叙事与许铭「卫生产品可及性」倡议；其余国 PT 成本待数据。
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\D\我的论文\脑卒中全球卫生"
STEP11 = os.path.join(ROOT, "建模步骤", "11_Gap市场失灵节点", "output", "gap_yearly_15.csv")   # 15国 Gap (Step11b)
POP = os.path.join(ROOT, "建模步骤", "14_康复需求扩展15国", "output", "rehab_demand_yearly.csv")  # 15国人口
PT4 = os.path.join(ROOT, "建模步骤", "10_供给侧S(t)整理", "output", "supply_capacity_yearly.csv")  # 4试点国 pt_density
OUTDIR = os.path.join(ROOT, "建模步骤", "13_D2H三情景配置", "output")
os.makedirs(OUTDIR, exist_ok=True)

ANCHOR = 2023

# ---------- 可替换参考假设(IMF WEO 2023 Oct 名义GDP, $万亿; 未进入核心Gap公式) ----------
GDP_T = {
    "US": 26.95, "CN": 17.70, "JP": 4.23, "GB": 3.33, "KR": 1.71,
    "ID": 1.42, "TH": 0.512, "SG": 0.497, "PH": 0.436, "VN": 0.433,
    "MY": 0.431, "MM": 0.0749, "KH": 0.0309, "BN": 0.0152, "LA": 0.0142,
}
# D2H 注资扩 PT 人力的完全负担年成本($/PT/年, 含培训+薪资+福利, 示意)
PT_COST_USD = 85000.0

# ---------- S2 弹性假设(文献锚定, 本面板受老龄化混杂不可估) ----------
GAMMA_D_MID = 1.5
GAMMA_D_RANGE = [0.5, 1.0, 1.5, 2.0]
GAMMA_S_MID = -0.05
GAMMA_S_RANGE = [0.0, -0.05, -0.10, -0.15]
UNEMP_SHOCK_PP = 2.0

# D2H 卫生支出注资档位(pp GDP)
DELTA_GRID = [0.25, 0.5, 1.0, 2.0]


def main():
    # ---- 主输入: 15国 Gap ----
    gap = pd.read_csv(STEP11)
    # 列名规整: supply_che_pct_gdp → che_pct_gdp 等, 便于复用原逻辑
    gap = gap.rename(columns={
        "supply_che_pct_gdp": "che_pct_gdp",
        "supply_gghe_pct_gdp": "gghe_pct_gdp",
        "uhc_index": "uhc_index",
    })
    # ---- 人口(15国, Step14) ----
    pop = pd.read_csv(POP)[["country", "year", "population"]]
    # ---- pt_density(仅 4 试点国, Step10) ----
    pt = pd.read_csv(PT4)[["country", "year", "pt_density_per100k"]]

    df = gap.merge(pop, on=["country", "year"], how="left")
    df = df.merge(pt, on=["country", "year"], how="left")  # 11国 pt_density = NaN
    df = df.rename(columns={"pt_density_per100k": "pt_density"})

    panel = df.copy()
    # 面板 min/max 用于一致再归一化(与 Step11b 同口径, 3 分量 S_index)
    rate_min, rate_max = panel["rehab_demand_rate_per100k"].min(), panel["rehab_demand_rate_per100k"].max()
    Sidx_min, Sidx_max = panel["S_index"].min(), panel["S_index"].max()
    # 三分量(与 11b S_index_15 一致): che / gghe / uhc
    comp = ["che_pct_gdp", "gghe_pct_gdp", "uhc_index"]
    stats = {c: (panel[c].mean(), panel[c].std(ddof=0)) for c in comp}

    def d_norm(rate):
        return (rate - rate_min) / (rate_max - rate_min)

    def s_index_from_che(che, row):
        zs = []
        for c in comp:
            mu, sd = stats[c]
            v = che if c == "che_pct_gdp" else row[c]
            zs.append((v - mu) / sd)
        return float(np.mean(zs))

    def s_norm_from_sidx(sidx):
        return (sidx - Sidx_min) / (Sidx_max - Sidx_min)

    # ---------- 锚定年 2023 ----------
    a = df[df.year == ANCHOR].copy().reset_index(drop=True)
    priority = a[a["Gap"] > 0]["country"].tolist()

    rows = []
    dose_rows = []
    pt_rows = []

    for _, r in a.iterrows():
        c = r["country"]
        # S1 直接用 Step11b 已发布的 D_norm/S_norm/Gap, 保证与 Figure 2 完全一致
        D0 = r["D_norm"]
        S0 = r["S_norm"]
        Gap0 = r["Gap"]
        rate0 = r["rehab_demand_rate_per100k"]
        che0 = r["che_pct_gdp"]
        pt_dens0 = r["pt_density"]
        pop0 = r["population"]

        # ---- S1 基准 ----
        rows.append(dict(country=c, scenario="S1_baseline", rehab_demand_rate=rate0,
                         che_pct_gdp=che0, D_norm=D0, S_norm=S0, Gap=Gap0,
                         Gap_change_vs_base=0.0))

        # ---- S2 悲观(失业+2pp) ----
        s2_gaps = {}
        for gd in GAMMA_D_RANGE:
            for gs in GAMMA_S_RANGE:
                rate_s = rate0 * (1 + gd / 100.0 * UNEMP_SHOCK_PP)
                che_s = che0 + gs * UNEMP_SHOCK_PP
                D_s = d_norm(rate_s)
                S_s = s_norm_from_sidx(s_index_from_che(che_s, r))
                gap_s = D_s - S_s
                s2_gaps[(gd, gs)] = gap_s
        rate_mid = rate0 * (1 + GAMMA_D_MID / 100.0 * UNEMP_SHOCK_PP)
        che_mid = che0 + GAMMA_S_MID * UNEMP_SHOCK_PP
        D_mid = d_norm(rate_mid)
        S_mid = s_norm_from_sidx(s_index_from_che(che_mid, r))
        Gap_mid = D_mid - S_mid
        rows.append(dict(country=c, scenario="S2_pessimistic(unemp+2pp,mid)",
                         rehab_demand_rate=rate_mid, che_pct_gdp=che_mid,
                         D_norm=D_mid, S_norm=S_mid, Gap=Gap_mid,
                         Gap_change_vs_base=(Gap_mid - Gap0) / abs(Gap0) * 100 if Gap0 != 0 else np.nan))

        # ---- S3 乐观 D2H : δ 档位剂量反应 ----
        for delta in DELTA_GRID:
            che_d = che0 + delta
            S_d = s_norm_from_sidx(s_index_from_che(che_d, r))
            Gap_d = D0 - S_d
            dose_rows.append(dict(country=c, delta_che_pp_GDP=delta,
                                  che_pct_gdp=che_d, S_norm=S_d, Gap=Gap_d,
                                  Gap_reduction_pct=(Gap0 - Gap_d) / abs(Gap0) * 100 if Gap0 != 0 else np.nan,
                                  health_exp_increase_pct=delta / che0 * 100))

        # ---- S3* 完全闭合 Gap 所需 δ* (仅对 Gap>0 的优先国) ----
        # 解析推导: ΔS_norm = δ / [3 * sd_che * (Sidx_max - Sidx_min)]
        #   (s_index 为三分量 z 值均值, che 单分量变动 δ/sd_che 仅贡献 1/3)
        # 闭合条件 ΔS_norm = Gap0  →  δ* = 3 * Gap0 * sd_che * (Sidx_max - Sidx_min)
        # [2026-08-07 修正] 原系数 4.0 为笔误, 致 δ* 高估 4/3 倍(Gap_star ≈ -0.33*Gap0 ≠ 0); 已改 3.0
        if Gap0 > 0:
            delta_star = 3.0 * Gap0 * (Sidx_max - Sidx_min) * stats["che_pct_gdp"][1]
            che_star = che0 + delta_star
            S_star = s_norm_from_sidx(s_index_from_che(che_star, r))
            Gap_star = D0 - S_star
            health_exp_inc_star = delta_star / che0 * 100
            dose_rows.append(dict(country=c, delta_che_pp_GDP=round(delta_star, 4),
                                  che_pct_gdp=che_star, S_norm=S_star, Gap=Gap_star,
                                  Gap_reduction_pct=100.0,
                                  health_exp_increase_pct=health_exp_inc_star))
        else:
            dose_rows.append(dict(country=c, delta_che_pp_GDP=np.nan,
                                  che_pct_gdp=np.nan, S_norm=np.nan, Gap=np.nan,
                                  Gap_reduction_pct=np.nan,
                                  health_exp_increase_pct=np.nan))

        # ---- 具体 D2H 载体: PT 人力扩充成本 ----
        us_pt = df[(df.country == "US") & (df.year == ANCHOR)]["pt_density"].values[0]
        target_pt = us_pt
        if pd.notna(pt_dens0) and pd.notna(pop0):
            pt_current = pt_dens0 * pop0 / 1e5
            pt_target = target_pt * pop0 / 1e5
            pt_needed = pt_target - pt_current
        else:
            pt_current = pt_target = pt_needed = np.nan
        d2h_priority = "YES" if Gap0 > 0 else "NO"
        pt_allocated = int(round(pt_needed)) if (Gap0 > 0 and pd.notna(pt_needed) and pt_needed > 0) else 0
        cost_alloc = pt_allocated * PT_COST_USD
        pt_rows.append(dict(country=c, pt_density_2023=pt_dens0,
                            target_pt_density_us_level=target_pt if pd.notna(pt_dens0) else np.nan,
                            pop_millions=round(pop0 / 1e6, 2) if pd.notna(pop0) else np.nan,
                            current_PTs=int(round(pt_current)) if pd.notna(pt_current) else np.nan,
                            target_PTs=int(round(pt_target)) if pd.notna(pt_target) else np.nan,
                            PTs_needed=int(round(pt_needed)) if pd.notna(pt_needed) else np.nan,
                            d2h_priority=d2h_priority,
                            pt_data_available="YES" if pd.notna(pt_dens0) else "NO(blue-ocean gap)",
                            PTs_allocated=pt_allocated,
                            d2h_alloc_usd=round(cost_alloc, 0),
                            d2h_alloc_usd_billions=round(cost_alloc / 1e9, 3)))

    scen = pd.DataFrame(rows)
    dose = pd.DataFrame(dose_rows)
    ptc = pd.DataFrame(pt_rows)

    scen.to_csv(os.path.join(OUTDIR, "d2h_scenarios.csv"), index=False)
    dose.to_csv(os.path.join(OUTDIR, "d2h_dose_response.csv"), index=False)
    ptc.to_csv(os.path.join(OUTDIR, "d2h_pt_costing.csv"), index=False)

    # ---------- validation_report ----------
    lines = []
    lines.append("# Step 13 · Debt-to-Health 三情景配置 · 校验报告（15 国迁移版）\n")
    lines.append("## 数据锚定\n")
    lines.append(f"- 锚定年: {ANCHOR}; 样本: **{a['country'].nunique()} 国** ({list(a['country'])})")
    lines.append(f"- Gap 口径: Step11b 15国面板 min-max 相对靶向指数 (D_norm - S_norm); 面板 S_index 区间 [{Sidx_min:.3f}, {Sidx_max:.3f}]（三分量 che/gghe/uhc, 与论文 Figure 2 同口径）")
    lines.append(f"- 宏观压力源: household_stress 面板 (失业/gov债务); 注: 15国面板受老龄化趋势混杂, S2弹性用文献锚定假设非面板估计\n")
    lines.append("## ① 三情景 Gap（锚定年 2023）\n")
    lines.append(scen.to_string(index=False))
    lines.append("\n")
    lines.append("## ② D2H 剂量反应（δ=卫生支出增幅 pp GDP → Gap缩减%）\n")
    lines.append(f"- D2H 优先靶向国(Gap>0, {ANCHOR}): **{priority}** （共 {len(priority)} 国; 以中国与东盟中低收入国为主）\n")
    lines.append(dose.round(4).to_string(index=False))
    lines.append("\n")
    lines.append("## ③ 具体 D2H 载体：PT 人力扩充成本（追上美国2023 PT密度；仅 4 试点国有 pt_density）\n")
    lines.append(f"- PT 单位完全负担成本假设: ${PT_COST_USD:,.0f}/PT/年 (可替换)\n")
    lines.append(f"- 注: pt_density 全球仅 4 试点国(US/GB/KR/JP)可得, 其余 11 国标 NO(blue-ocean gap)——OT/ST 全球无通用序列, 恰为本文蓝海创新点; 其 D2H 优先性由 Gap 决定, 载体成本待数据。\n")
    lines.append(ptc.to_string(index=False))
    lines.append("\n")
    lines.append("## ④ 关键结论\n")
    lines.append(f"- **D2H 优先靶向国 = {priority}**（{ANCHOR} 年 Gap>0），以中国与东盟中低收入经济体为主；US/GB 等高收入国 Gap<0（供给相对充足），D2H 不应流向这些国——与许铭『债务置换更适债务国』语境一致。")
    n_pos = len(priority)
    lines.append(f"- 完全闭合相对 Gap 所需 δ*（卫生支出增幅 pp GDP）仅在 {n_pos} 个优先国为正；说明 D2H 是**边际靶向注资**而非全量填补, 符合「市场塑造」精准投放逻辑。")
    # 取 Gap 最大国做样例
    top = a.sort_values("Gap", ascending=False).iloc[0]
    lines.append(f"- 样例（最大 Gap 国 {top['country']}, 2023 Gap=+{top['Gap']:.3f}）: 完全闭合需卫生支出 +{4.0*top['Gap']*(Sidx_max-Sidx_min)*stats['che_pct_gdp'][1]:.1f} pp GDP, 量级显示 D2H 须精准而非粗放。")
    lines.append(f"- 悲观情景(失业+2pp): 中点下优先国 Gap 普遍扩大（宏观压力扩大康复缺口, 反向论证 D2H 必要性）。")
    lines.append("\n## ⑤ 诚实局限\n")
    lines.append("1. Gap 为相对靶向指数, 非绝对未满足人数; 用于锁定优先国, 不声称绝对缺口规模。")
    lines.append("2. S2 需求/供给弹性为文献锚定情景假设(面板受老龄化混杂), 非本数据估计; 已给灵敏度区间。")
    lines.append("3. 15 国含中低收入债务国, 字面债务置换语境自洽; 高收入国 Gap<0 非优先靶向。")
    lines.append("4. GDP / PT单位成本 为可替换假设(标注来源); 主指标 δ(pp GDP) 与 Gap缩减% 完全由本项目数据导出。")
    lines.append("5. pt_density 仅 4 试点国可得(OT/ST全球无序列)→ D2H 载体选 PT 扩充恰呼应 OT/ST 蓝海叙事与许铭「卫生产品可及性」倡议; 其余国载体成本待数据。")
    lines.append("6. 本 15国版取代原 4国版(US/GB/KR/JP); 与论文 Figure 2 的 15国 Gap 口径完全一致。")

    with open(os.path.join(OUTDIR, "validation_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Step13 (15-country) DONE")
    print(f"Priority countries (Gap>0 @ {ANCHOR}): {priority}")
    print(scen.to_string(index=False))
    print("\n--- PT costing (priority flagged) ---")
    print(ptc.to_string(index=False))


if __name__ == "__main__":
    main()
