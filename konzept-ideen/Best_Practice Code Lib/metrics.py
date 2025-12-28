import pandas as pd
def save_model_comparison(data, outfile):
    pd.DataFrame(data).to_csv(outfile, index=False)
