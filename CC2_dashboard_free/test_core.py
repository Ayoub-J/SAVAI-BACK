import pandas as pd
from analyse_core import run_analysis

df_raw = pd.read_csv("LLM-classified-data/free tweet export.csv")  # adapte le chemin si besoin
df_final, df_problematic = run_analysis(df_raw)

print("Final :", len(df_final))
print("Problematic :", len(df_problematic))
print(df_final.head())
print(df_problematic.head())
