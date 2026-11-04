
chrome.runtime.onMessage.addListener(
    (request, sender, sendResponse) => {

        if (request.action === "extract_comments") {

            // Récupérer les commentaires affichés sur YouTube
            const elements = document.querySelectorAll(
                "ytd-comment-thread-renderer #content-text"
            );

            const comments = [];
            const seen = new Set();

            elements.forEach(element => {

                const text = element.innerText.trim();

                if (text && !seen.has(text)) {
                    comments.push(text);
                    seen.add(text);
                }

            });

            sendResponse({
                success: true,
                comments: comments
            });
        }

        return true;
    }
);
