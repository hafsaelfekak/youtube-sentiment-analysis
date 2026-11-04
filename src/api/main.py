
import joblib
import numpy as np

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import PredictionRequest


app = FastAPI(
    title="YouTube Sentiment Analysis API",
    description="API de classification des sentiments des commentaires",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "sentiment_model.joblib"
VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.joblib"

model = None
vectorizer = None

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

    print("Modèle et vectorizer chargés avec succès !")

except Exception as error:
    print("Erreur de chargement :", error)

sentiment_names = {
    -1: "negative",
    0: "neutral",
    1: "positive"
}

@app.get("/health")
def health():

    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle ou le vectorizer n'est pas disponible."
        )

    return {
        "status": "healthy",
        "model_loaded": True,
        "message": "API opérationnelle"
    }



@app.post("/predict_batch")
def predict_batch(request: PredictionRequest):

    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle n'est pas disponible."
        )

    try:

        comments = request.comments
        comments_tfidf = vectorizer.transform(comments)

        predictions = model.predict(comments_tfidf)

        decision_scores = model.decision_function(comments_tfidf)

        decision_scores = decision_scores - np.max(
            decision_scores, axis=1, keepdims=True
        )

        probabilities = np.exp(decision_scores)

        probabilities = probabilities / np.sum(
            probabilities, axis=1, keepdims=True
        )

        results = []

        for i, prediction in enumerate(predictions):

            label = int(prediction)
            class_index = list(model.classes_).index(label)

            confidence = float(
                probabilities[i][class_index] * 100
            )

            results.append({
                "comment": comments[i],
                "sentiment": sentiment_names[label],
                "label": label,
                "confidence": round(confidence, 2)
            })
        total = len(predictions)

        counts = {
            -1: int(np.sum(predictions == -1)),
            0: int(np.sum(predictions == 0)),
            1: int(np.sum(predictions == 1))
        }

        statistics = {
            "total_comments": total,
            "negative": {
                "count": counts[-1],
                "percentage": round(counts[-1] / total * 100, 2)
            },
            "neutral": {
                "count": counts[0],
                "percentage": round(counts[0] / total * 100, 2)
            },
            "positive": {
                "count": counts[1],
                "percentage": round(counts[1] / total * 100, 2)
            }
        }

        return {
            "success": True,
            "predictions": results,
            "statistics": statistics
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur pendant la prédiction : {str(error)}"
        )
