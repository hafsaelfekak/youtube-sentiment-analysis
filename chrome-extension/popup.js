
const API_URL = "http://127.0.0.1:8000/predict_batch";

let predictions = [];

const analyzeBtn = document.getElementById("analyzeBtn");
const statusText = document.getElementById("status");
const resultsSection = document.getElementById("results");
const commentsList = document.getElementById("commentsList");
const filter = document.getElementById("filter");


analyzeBtn.addEventListener("click", async () => {

    try {

        statusText.textContent = "Extraction des commentaires...";
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyse en cours...";

        const tabs = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        const tab = tabs[0];

        if (!tab || !tab.url ||
            !tab.url.startsWith("https://www.youtube.com/")) {

            throw new Error("Ouvre une vidéo YouTube avant de commencer.");
        }

        const response = await chrome.tabs.sendMessage(
            tab.id,
            { action: "extract_comments" }
        );

        if (!response || !response.comments ||
            response.comments.length === 0) {

            throw new Error(
                "Aucun commentaire trouvé. Fais défiler la section des commentaires puis réessaie."
            );
        }

        const comments = response.comments;

        statusText.textContent =
            comments.length + " commentaires extraits. Analyse en cours...";

        const apiResponse = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                comments: comments.slice(0, 100)
            })
        });

        if (!apiResponse.ok) {
            const errorData = await apiResponse.json();
            throw new Error(
                errorData.detail || "Erreur lors de l'analyse."
            );
        }

        const data = await apiResponse.json();

        predictions = data.predictions;

        displayStatistics(data.statistics);

        displayComments(predictions);

        resultsSection.hidden = false;

        statusText.textContent =
            predictions.length + " commentaires analysés avec succès.";

    } catch (error) {

        statusText.textContent = error.message;

        resultsSection.hidden = true;

    } finally {

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyser les commentaires";

    }

});
function displayStatistics(stats) {

    document.getElementById("total").textContent =
        stats.total_comments;

    document.getElementById("positiveCount").textContent =
        stats.positive.count;

    document.getElementById("neutralCount").textContent =
        stats.neutral.count;

    document.getElementById("negativeCount").textContent =
        stats.negative.count;

    document.getElementById("positivePercent").textContent =
        stats.positive.percentage + "%";

    document.getElementById("neutralPercent").textContent =
        stats.neutral.percentage + "%";

    document.getElementById("negativePercent").textContent =
        stats.negative.percentage + "%";

    document.getElementById("positiveBar").style.width =
        stats.positive.percentage + "%";

    document.getElementById("neutralBar").style.width =
        stats.neutral.percentage + "%";

    document.getElementById("negativeBar").style.width =
        stats.negative.percentage + "%";
}

function displayComments(data) {

    commentsList.innerHTML = "";

    const selectedFilter = filter.value;

    const filteredComments = data.filter(item => {

        return selectedFilter === "all" ||
            item.sentiment === selectedFilter;

    });

    if (filteredComments.length === 0) {

        commentsList.textContent = "Aucun commentaire dans cette catégorie.";
        return;
    }

    filteredComments.forEach(item => {

        const card = document.createElement("div");
        card.className = "comment-card " + item.sentiment;

        const text = document.createElement("div");
        text.className = "comment-text";
        text.textContent = item.comment;

        const info = document.createElement("div");
        info.className = "comment-info";

        const sentiment = document.createElement("strong");
        sentiment.textContent = item.sentiment.toUpperCase();

        const confidence = document.createElement("span");
        confidence.textContent =
            "Score indicatif : " + item.confidence + "%";

        info.appendChild(sentiment);
        info.appendChild(confidence);

        card.appendChild(text);
        card.appendChild(info);

        commentsList.appendChild(card);

    });

}



filter.addEventListener("change", () => {
    displayComments(predictions);
});


const themeBtn = document.getElementById("themeBtn");

themeBtn.addEventListener("click", () => {

    document.body.classList.toggle("dark");

    const darkMode = document.body.classList.contains("dark");

    themeBtn.textContent = darkMode ? "☀️" : "🌙";

});


document.getElementById("copyBtn").addEventListener(
    "click",
    async () => {

        if (predictions.length === 0) return;

        const text = predictions.map(item => {

            return `${item.sentiment.toUpperCase()} | ${item.confidence}% | ${item.comment}`;

        }).join("\n");

        try {
            await navigator.clipboard.writeText(text);
            statusText.textContent = "Résultats copiés !";
        } catch (error) {
            statusText.textContent = "Impossible de copier les résultats.";
        }

    }
);


document.getElementById("exportBtn").addEventListener(
    "click",
    () => {

        if (predictions.length === 0) return;

        const rows = [
            ["Commentaire", "Sentiment", "Label", "Score indicatif"]
        ];

        predictions.forEach(item => {
            rows.push([
                item.comment,
                item.sentiment,
                item.label,
                item.confidence
            ]);
        });

        const csv = rows.map(row =>
            row.map(value =>
                `"${String(value).replace(/"/g, '""')}"`
            ).join(",")
        ).join("\n");

        const blob = new Blob(
            ["\uFEFF" + csv],
            { type: "text/csv;charset=utf-8;" }
        );

        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = url;
        link.download = "youtube_sentiment_results.csv";

        link.click();

        URL.revokeObjectURL(url);

    }
);
