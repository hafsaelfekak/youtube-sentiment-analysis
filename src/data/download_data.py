import pandas as pd
import os

url = "https://raw.githubusercontent.com/Himanshu-1703/reddit-sentiment-analysis/refs/heads/main/data/reddit.csv"

os.makedirs("data/raw", exist_ok=True)

df = pd.read_csv(url)
df.to_csv("data/raw/reddit.csv", index=False)
print("Dataset téléchargé")
print("\nPremières lignes :")
print(df.head())
print("\nNombre de commentaires :", len(df))
print("\nDistribution des sentiments :")
print(df["category"].value_counts())