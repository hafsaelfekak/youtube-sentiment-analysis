import pandas as pd
import re
import os

df = pd.read_csv("data/raw/reddit.csv")

df = df.rename(columns={
    "clean_comment": "text",
    "category": "label"
})
df = df[["text", "label"]]
df = df.dropna()
df = df.drop_duplicates(subset="text")
def clean_text(text):
    text = str(text)
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()
df["text"] = df["text"].apply(clean_text)
df = df[df["text"] != ""]
df = df[df["label"].isin([-1, 0, 1])]
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/cleaned_data.csv", index=False)
print("\nNombre de commentaires après nettoyage :", len(df))
print("\nDistribution des sentiments :")
print(df["label"].value_counts())