import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/processed/cleaned_data.csv")

print("Informations du dataset :")
print(df.info())

print("\nValeurs manquantes :")
print(df.isnull().sum())

print("\nDistribution des classes :")
print(df["label"].value_counts())

sns.countplot(data=df, x="label")

plt.title("Distribution des sentiments")
plt.xlabel("Sentiment")
plt.ylabel("Nombre de commentaires")
plt.show()

df["text_length"] = df["text"].astype(str).apply(len)

print("\nLongueur moyenne des commentaires :")
print(df["text_length"].mean())

plt.hist(df["text_length"], bins=30)
plt.title("Longueur des commentaires")
plt.xlabel("Nombre de caractères")
plt.ylabel("Fréquence")
plt.show()