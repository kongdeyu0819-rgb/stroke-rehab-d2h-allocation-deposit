# -*- coding: utf-8 -*-
"""
Step 11d — Extract the 15-country stroke burden rate table from the GBD download.

Run this only if you want to regenerate `data/stroke_burden_rates_15countries_gbd2023.csv`
from the original download; the archived rate table is otherwise sufficient for
`scripts/11c_build_gap_daly.py`.

Source: GBD 2023 Results Tool, cause = stroke, metric = Rate, age = All ages,
sex = Both, location = the 15 study economies, year = 2010-2023. The download is
not redistributed here because of its size; it is public and free to obtain.

Usage
-----
    python 11d_extract_gbd_rates.py <path-to-IHME-GBD_2023_DATA.csv>

The tool exports localised labels (Chinese) for measure, age, sex and location;
the lookup tables below map them onto the ISO codes used throughout this deposit.
"""
import sys
import os
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "stroke_burden_rates_15countries_gbd2023.csv")

LOC2ISO = {
    "美利坚合众国": "US", "英国": "GB", "日本": "JP", "大韩民国": "KR", "中国": "CN",
    "文莱达鲁萨兰国": "BN", "柬埔寨": "KH", "印度尼西亚": "ID",
    "老挝人民民主共和国": "LA", "马来西亚": "MY", "缅甸": "MM",
    "菲律宾": "PH", "新加坡": "SG", "泰国": "TH", "越南": "VN",
}
MEASURES = {"incidence": "发病率", "daly": "伤残调整生命年",
            "yld": "伤残损失生命年", "prevalence": "患病率"}


def main(path):
    g = pd.read_csv(path)
    g = g[(g.metric_name == "率") & (g.age_name == "全部") & (g.sex_name == "合计")].copy()
    g["country"] = g.location_name.map(LOC2ISO)
    missing = g[g.country.isna()].location_name.unique()
    assert len(missing) == 0, f"unmapped locations: {missing}"

    wide = g.pivot_table(index=["country", "year"], columns="measure_name",
                         values="val").reset_index()
    wide = wide.rename(columns={v: k for k, v in MEASURES.items()})
    wide = wide[wide.year.between(2010, 2023)]
    wide = wide[["country", "year", "incidence", "daly", "yld", "prevalence"]]
    wide.columns = ["country", "year", "stroke_incidence_per100k",
                    "stroke_daly_per100k", "stroke_yld_per100k", "stroke_prevalence_per100k"]
    wide = wide.sort_values(["country", "year"]).reset_index(drop=True)
    assert len(wide) == 210, f"expected 210 country-years, got {len(wide)}"
    wide.to_csv(OUT, index=False, encoding="utf-8", float_format="%.6f")
    print(f"[11d] wrote {len(wide)} rows -> {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
