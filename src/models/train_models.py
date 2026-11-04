
import pandas as pd
import joblib
import os
import time
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

from sklearn.model_selection import GridSearchCV

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score
)


train_data = pd.read_csv("data/processed/train.csv")
test_data = pd.read_csv("data/processed/test.csv")

X_train = train_data["text"].fillna("")
y_train = train_data["label"]

X_test = test_data["text"].fillna("")
y_test = test_data["label"]

print("Nombre de données d'entraînement :", len(X_train))
print("Nombre de données de test :", len(X_test))

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english"
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ),
    "SVM": LinearSVC()
}

print("\nComparaison des modèles :")

for name, model in models.items():

    model.fit(X_train_tfidf, y_train)

    predictions = model.predict(X_test_tfidf)

    accuracy = accuracy_score(y_test, predictions)

    print(name, ":", round(accuracy, 3))

parameters = {
    "C": [0.01, 0.1, 1, 10, 100]
}

grid_search = GridSearchCV(
    LinearSVC(),
    parameters,
    cv=3,
    scoring="f1_macro",
    n_jobs=-1
)

grid_search.fit(X_train_tfidf, y_train)

best_model = grid_search.best_estimator_

print("\nMeilleurs paramètres :", grid_search.best_params_)

y_pred = best_model.predict(X_test_tfidf)

accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy :", round(accuracy, 4))

print("\nRapport de classification :")

print(
    classification_report(
        y_test,
        y_pred,
        labels=[-1, 0, 1],
        target_names=["Negative", "Neutral", "Positive"],
        digits=4
    )
)

print("F1-score macro :", round(
    f1_score(y_test, y_pred, average="macro"), 4
))


matrix = confusion_matrix(
    y_test,
    y_pred,
    labels=[-1, 0, 1]
)

display = ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=["Negative", "Neutral", "Positive"]
)

display.plot(cmap="Blues")

plt.title("Matrice de confusion - SVM")
plt.tight_layout()
plt.savefig("models/confusion_matrix.png")
plt.show()

comments = X_test.head(50).tolist()

start_time = time.perf_counter()

comments_tfidf = vectorizer.transform(comments)

predictions = best_model.predict(comments_tfidf)

end_time = time.perf_counter()

inference_time = (end_time - start_time) * 1000

print("\nTemps d'inférence pour 50 commentaires :",
      round(inference_time, 2), "ms")

os.makedirs("models", exist_ok=True)

joblib.dump(
    best_model,
    "models/sentiment_model.joblib"
)

joblib.dump(
    vectorizer,
    "models/tfidf_vectorizer.joblib"
)

print("\nModèle SVM sauvegardé")
print("Vectorizer sauvegardé")

