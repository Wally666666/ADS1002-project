# ADS1002 Rossmann 短期销售预测 / Short-Term Portfolio Sales Forecasting

**课程 / Course:** ADS1002, Monash University（莫纳什大学）  
**作者 / Author:** 王俊尧 (Junyao Wang)

## 项目简介

本项目使用 Rossmann Store Sales 训练数据（2013 年 1 月至 2015 年 7 月），研究如何预测销售额最高的 20% 门店（223 家）未来 28 天的合计日销售额，用于短期收入规划。项目内容包括数据清洗、探索性分析（星期、促销、客流、节假日等因素）、以及 Baseline、Regression、Trend、Ridge、Tuned Ridge、Tree、Random Forest 七种方法的滚动回测比较和 Forest 敏感性分析。

主要结论：2015 年 7 月参考窗口中，回归模型日 MAE 为 109,611（Baseline 为 264,217，降低 58.5%），四周合计仅高估 1.40%；三窗口开发期内 Forest 按日 MAE 略优于 Trend（领先 0.95%），但 Trend 在 RMSE 和四周总量误差上更稳健。节假日仍是主要误差来源，模型的实际业务适用性需在新数据上进一步验证。

## English summary

A Monash ADS1002 data-science project forecasting combined daily sales of the top-20% Rossmann stores over a 28-day horizon, comparing seven calendar-based procedures with rolling backtests and a Random Forest sensitivity check.

*Statement: This project was completed independently by Junyao Wang (王俊尧); per course requirements it was submitted to the group repository by the group leader.*

---


**Question:** How accurately can calendar-based models forecast the combined daily sales of the highest-sales 20% of stores over the next 28 days?

This repository contains the analysis notebook, numerical evidence and final sensitivity check. The historical analysis is complete; operational suitability remains unproven.

## Start here

- [Notebook](project_notebook.ipynb): code, figures, diagnostics and final interpretation.
- [Result evidence](results/README.md): CSV snapshots and metric definitions.
- [Forest sensitivity](scripts/forest_sensitivity.py): portable reproduction of the report's bounded check.

## Findings and final decision

The July reference forecast covers **4–31 July 2015**, for 223 stores selected using **1 January–3 July 2015** sales. These stores account for 30.5% of recorded sales across the supplied stores during that ranking period.

| Evidence | Result | Interpretation |
|---|---|---|
| July daily MAE | Regression 109,611 versus Baseline 264,217 | Regression reduces MAE by 58.5%. |
| July four-week sales | Regression 57.33 million versus actual 56.54 million | Total overforecast is 1.40%. |
| Three-window development MAE | Forest 160,118 versus Trend 161,659 | Forest leads by only 0.95% under the daily-MAE rule. |
| Development mean RMSE | Trend 223,369 versus Forest 255,617 | The MAE ranking does not carry over to every metric. |
| Development mean absolute total error | Trend 2.10% versus Forest 4.87% | Retain Trend as a reference for four-week totals. |
| July Forest MAE | 138,087 | Regression performs better in this window. |
| Four diagnosed holidays | Forest MAE 48,195, no negative forecasts | Small-sample evidence, insufficient to establish future reliability. |

Errors use the dataset's original sales units, with no currency assumption. Regression improves daily MAE and RMSE over Baseline in all six inspected windows, but improves absolute four-week total percentage error in only four.

**Conclusion:** retain the original Forest as a candidate for fresh validation, with Trend and Regression as references. No universally best model is established. Portfolio forecasts cannot justify automatic targets, single-store staffing, stock decisions or quantified profit claims.

## Data and evaluation design

- Input: 1,017,209 observed store-date records for 1,115 stores, January 2013 through July 2015. Only the supplied training dataset is analysed.
- Cleaning: validate missing cells, duplicates, keys, domains and dates; standardise types without imputing or clipping sales. Recorded closed days remain included.
- Coverage: 27 selected stores lack July–December 2014. Missing rows remain unknown. Portfolio models use complete dates only, giving 730 training days for July and 28 evaluation days.
- Inputs: weekday indicators and counts of open, promotional, public-holiday and school-holiday stores. Future customer counts are excluded. Opening and promotion schedules are assumed available in advance.
- At each forecast origin, store selection and training use only earlier observations. Inner chronological tuning also repeats past-only selection. Models within a window share targets and coverage.
- Development ranking: 28-day windows beginning 11 April, 9 May and 6 June 2015. Supplemental origins: 14 February and 14 March. July reference origin: 4 July. Training histories expand and selected stores can change between origins.
- All six periods influenced development. None is an untouched final test. Small differences are descriptive, with no statistical-significance claim.

## Model progression

| Procedure | Purpose |
|---|---|
| Baseline | Training weekday-mean forecast. |
| Regression | Interpretable calendar and schedule regression. |
| Trend | Regression extended with elapsed time. |
| Ridge | Standardised shrinkage reference, fixed alpha 1. |
| Tree | Regression tree with bounded chronological inner tuning. |
| Tuned Ridge | Chronological inner selection over a bounded alpha grid. |
| Forest | 100 bootstrap trees, depth 4, leaf minimum 5, half-size bootstrap, all inputs eligible at each split, seed 0. |

The four- and six-procedure notebook stages document development; the seven-procedure table is the final ranking. Forest followed the Tree comparison. Independence of its parameter choices from earlier findings is undocumented. With all inputs eligible at each split, this configuration has no feature-subsampling randomisation.

### Forest sensitivity

| Setting | Mean development MAE |
|---|---:|
| Original Forest | 160,118 |
| Full-size bootstrap | 168,637 |
| Depth 3 | 169,752 |
| Leaf minimum 15 | 150,460 |

Each alternative changes one setting. Full-size bootstrap and depth 3 lose the narrow lead over Trend. Larger leaves improve the three development windows and July but worsen both supplemental windows. These post-ranking diagnostics demonstrate configuration sensitivity; they do not retrospectively replace the original candidate.

## Run the project notebook

Tested with Python 3.13.9. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab project_notebook.ipynb
```

Run every cell in order. For non-interactive execution:

```bash
python -m jupyter nbconvert --execute --to notebook --inplace project_notebook.ipynb --ExecutePreprocessor.timeout=600
```

The notebook includes the sensitivity check. To run it separately:

```bash
python scripts/forest_sensitivity.py
```

The numerical dependencies are pinned to the tested versions. Reconciliation checks compare recomputed rankings against report snapshots. The sensitivity step rewrites its two derived CSVs under `results/`; original comparison snapshots remain unchanged.

Clone or download this repository, open `project_notebook.ipynb` from its root,
and run all cells in order using Python with pandas, matplotlib and scikit-learn.
All required input data are in this repository; no separate desktop folder or
GitHub login is needed to run a local checkout.

- `data/raw/Rossmann_train.csv.gz`: original supplied training CSV, losslessly
  compressed. The notebook loads this file and rebuilds the cleaned analytical
  data in memory before EDA and modelling.
- `data/cleaned/Rossmann_train_clean.csv.gz`: retained cleaned output reference.
- `data/cleaned/Rossmann_store_clean.csv`: retained reference only; not used by
  the notebook. The competition test dataset is not needed for this project.

Raw and cleaned training files are two stages of the same dataset. Notebook
execution does not overwrite either file. Pandas reads `.csv.gz` directly.

Original file supplied on 6 September 2026: `Rossmann_train.csv`.
SHA-256 of the **decompressed original CSV**:
`f6e4597c142d7d909a13d53b68a8e85c00b9a4c7b5ff40adbb37d6829cc1f4cc`.

## Project close-out

The completed analysis provides a transparent historical comparison, identifies holiday failures and defines a bounded use case. Before adoption, freeze candidate specifications, confirm advance schedule availability, agree daily and total-error tolerances, and evaluate genuinely unseen seasons and holidays. Investigate holiday-specific features and prediction-interval coverage with appropriately separated validation.

References are listed at the end of the notebook. The local `logitplots.py` supports the existing diagnostic plots. No additional models are introduced in this close-out.
