# -*- coding: utf-8 -*-
"""
evaluate_job_ads.py
Simple evaluation hooks for precision/recall vs. a gold file.
Expected gold format (CSV):
filename,has_figma,has_figma_gt,has_design_thinking,has_design_thinking_gt,...
OR: filename + a semicolon list columns like tools_gt/methods_gt with canonical names.

Usage:
  python evaluate_job_ads.py --pred /path/to/out.csv --gold /path/to/gold.csv --outdir /path/to/eval
"""

from pathlib import Path
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

def series_contains_token(series: pd.Series, token: str) -> pd.Series:
    token = token.lower()
    return series.fillna("").str.lower().str.contains(rf"\b{token}\b", regex=True)

def eval_binary_metric(y_true, y_pred, label):
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    return {"label": label, "precision": p, "recall": r, "f1": f1}

def run(pred_csv: Path, gold_csv: Path, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    pred = pd.read_csv(pred_csv)
    gold = pd.read_csv(gold_csv)

    # Example metrics for two fields
    # Ensure alignment by filename
    df = pd.merge(gold, pred, on="filename", suffixes=("_gt",""))
    results = []

    # If gold provides boolean columns like has_figma_gt, has_design_thinking_gt
    for col in df.columns:
        if col.endswith("_gt") and df[col].dropna().isin([0,1,True,False]).any():
            base = col[:-3]
            if base in ["has_figma","has_design_thinking"]:
                # build predictions from tools/methods columns
                if base == "has_figma":
                    y_pred = series_contains_token(df["tools_norm"], "figma")
                elif base == "has_design_thinking":
                    y_pred = series_contains_token(df["methods_norm"], "design thinking")
                y_true = df[col].astype(int)
                results.append(eval_binary_metric(y_true, y_pred.astype(int), base))

    res_df = pd.DataFrame(results)
    res_df.to_csv(outdir / "metrics.csv", index=False)
    print("Saved metrics to", outdir)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True, help="CSV from pipeline_job_mining_v2.py")
    ap.add_argument("--gold", required=True, help="CSV with gold labels")
    ap.add_argument("--outdir", required=True, help="Output folder")
    args = ap.parse_args()
    run(Path(args.pred), Path(args.gold), Path(args.outdir))
