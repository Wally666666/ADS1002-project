"""One-factor Forest sensitivity check on the six existing forecast windows.

The four specifications below are fixed before inspecting this script's results.
They are diagnostics of the existing Forest comparison, not replacement candidates
in the original seven-procedure ranking. Each origin repeats the report's past-only
store selection, complete-date filter and ten-input construction.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
EVIDENCE = ROOT / "results"
INPUT = ROOT / "data/raw/Rossmann_train.csv.gz"

ORIGINAL = dict(n_estimators=100, max_depth=4, min_samples_leaf=5,
                max_features=1.0, bootstrap=True, max_samples=0.5,
                random_state=0, n_jobs=1)
SPECIFICATIONS = {
    "Original Forest": ORIGINAL,
    "Full-size bootstrap": {**ORIGINAL, "max_samples": None},
    "Depth 3": {**ORIGINAL, "max_depth": 3},
    "Leaf minimum 15": {**ORIGINAL, "min_samples_leaf": 15},
}
STARTS = pd.to_datetime(["2015-02-14", "2015-03-14", "2015-04-11",
                         "2015-05-09", "2015-06-06", "2015-07-04"])
DEVELOPMENT = set(pd.to_datetime(["2015-04-11", "2015-05-09", "2015-06-06"]))
FEATURES = ["DayOfWeek", "OpenStores", "PromoStores",
            "StateHolidayStores", "SchoolHolidayStores"]


def outer_data(train, start, store_count):
    """Return past-only features and the matched next 28 complete portfolio dates."""
    end = start + pd.Timedelta(days=27)
    prior = train[train.Date.between(pd.Timestamp("2015-01-01"),
                                     start - pd.Timedelta(days=1))]
    ranks = prior.groupby("Store").Sales.sum().sort_index().sort_values(
        ascending=False, kind="stable")
    selected = ranks.head(store_count).index
    rows = train[train.Store.isin(selected) & train.Date.le(end)].copy()
    rows["Holiday"] = rows.StateHoliday.ne("0").astype(int)
    daily = rows.groupby("Date").agg(
        Stores=("Store", "nunique"), Sales=("Sales", "sum"),
        OpenStores=("Open", "sum"), PromoStores=("Promo", "sum"),
        StateHolidayStores=("Holiday", "sum"),
        SchoolHolidayStores=("SchoolHoliday", "sum"))
    daily["DayOfWeek"] = daily.index.dayofweek + 1
    daily = daily[daily.Stores.eq(store_count)]
    past, future = daily[daily.index < start], daily.loc[start:end]
    assert future.index.equals(pd.date_range(start, end))
    assert past.index.max() < start and len(selected) == store_count
    x = pd.get_dummies(past[FEATURES], columns=["DayOfWeek"],
                       drop_first=True, dtype=int)
    xf = pd.get_dummies(future[FEATURES], columns=["DayOfWeek"],
                        drop_first=True, dtype=int).reindex(columns=x.columns,
                                                             fill_value=0)
    assert x.shape[1] == 10 and x.notna().all().all() and xf.notna().all().all()
    return past, future, x, xf


def main():
    train = pd.read_csv(INPUT, low_memory=False).drop_duplicates().copy()
    train.columns = train.columns.str.strip()
    train["Date"] = pd.to_datetime(train.Date, errors="raise")
    train["StateHoliday"] = train.StateHoliday.astype("string").str.strip()
    integer_columns = ["Store", "DayOfWeek", "Sales", "Customers",
                       "Open", "Promo", "SchoolHoliday"]
    train[integer_columns] = train[integer_columns].astype(int)
    train = train.sort_values(["Store", "Date"]).reset_index(drop=True)
    assert len(train) == 1017209 and not train.duplicated(["Store", "Date"]).any()
    assert train.notna().all().all()
    store_count = int(np.ceil(0.20 * train.Store.nunique()))
    assert store_count == 223

    rows = []
    for start in STARTS:
        past, future, x, xf = outer_data(train, start, store_count)
        holiday = future.StateHolidayStores.gt(0)
        label = start.strftime("%d %b") + "-" + (
            start + pd.Timedelta(days=27)).strftime("%d %b")
        for name, specification in SPECIFICATIONS.items():
            model = RandomForestRegressor(**specification).fit(x, past.Sales)
            prediction = pd.Series(model.predict(xf), index=future.index)
            error = prediction - future.Sales
            rows.append({
                "Window": label, "Origin": start.date().isoformat(),
                "Role": "Development" if start in DEVELOPMENT else
                        ("July reference" if start == STARTS[-1] else "Supplemental"),
                "Variant": name, "Train days": len(past),
                "MAE": error.abs().mean(),
                "RMSE": np.sqrt(error.pow(2).mean()),
                "Total %": 100 * error.sum() / future.Sales.sum(),
                "H-days": int(holiday.sum()),
                "H-MAE": error[holiday].abs().mean(),
                "Neg": int(prediction.lt(0).sum()),
            })
    scores = pd.DataFrame(rows)
    assert len(scores) == 24

    # Independently reconstruct the published original Forest results before
    # interpreting any alternative specification.
    published = pd.read_csv(EVIDENCE / "forest_scores.csv")
    original = scores[scores.Variant.eq("Original Forest")]
    for _, current in original.iterrows():
        prior = published[published.Window.eq(current.Window)].iloc[0]
        assert current["Train days"] == prior["Train days"]
        for metric in ["MAE", "RMSE", "Total %"]:
            assert np.isclose(current[metric], prior[metric], rtol=0, atol=1e-6)

    development = scores[scores.Role.eq("Development")]
    summary = development.groupby("Variant", sort=False).agg(
        Mean_MAE=("MAE", "mean"), Mean_RMSE=("RMSE", "mean"),
        Mean_abs_total_pct=("Total %", lambda s: s.abs().mean()),
        Worst_abs_total_pct=("Total %", lambda s: s.abs().max()),
        Neg=("Neg", "sum")).reset_index()
    trend = pd.read_csv(EVIDENCE / "seven_selection.csv")
    trend_mae = float(trend.loc[trend.Model.eq("Trend"), "Mean_MAE"].iloc[0])
    summary["Delta_vs_Trend_pct"] = 100 * (summary.Mean_MAE / trend_mae - 1)
    assert np.isclose(summary.iloc[0].Mean_MAE,
                      float(trend.loc[trend.Model.eq("Forest"), "Mean_MAE"].iloc[0]),
                      rtol=0, atol=1e-6)
    scores.to_csv(EVIDENCE / "forest_sensitivity_scores.csv", index=False)
    summary.to_csv(EVIDENCE / "forest_sensitivity_summary.csv", index=False)
    print(summary.to_string(index=False))
    print(scores.pivot(index="Window", columns="Variant", values="MAE")
          .to_string(float_format=lambda value: f"{value:,.0f}"))


if __name__ == "__main__":
    main()
