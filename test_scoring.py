import pandas as pd
from utils.scoring import score_dataframe

df = pd.read_csv("data/batch_template.csv")
result = score_dataframe(df)

print(result)
