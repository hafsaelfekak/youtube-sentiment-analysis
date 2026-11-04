import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import RandomOverSampler
import os

df = pd.read_csv("data/processed/cleaned_data.csv")

X = df["text"]
y = df["label"]

print("Distribution initiale :")
print(y.value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
print("\nDistribution avant équilibrage :")
print(y_train.value_counts())

sampler = RandomOverSampler(random_state=42)

X_train, y_train = sampler.fit_resample(
    X_train.to_frame(),
    y_train
)

print("\nDistribution après équilibrage :")
print(y_train.value_counts())

train_data = pd.DataFrame({
    "text": X_train["text"],
    "label": y_train
})

test_data = pd.DataFrame({
    "text": X_test,
    "label": y_test
})

os.makedirs("data/processed", exist_ok=True)

train_data.to_csv("data/processed/train.csv", index=False)
test_data.to_csv("data/processed/test.csv", index=False)

print("\nDivision et équilibrage terminés !")

print("Nombre de données train :", len(train_data))
print("Nombre de données test :", len(test_data))