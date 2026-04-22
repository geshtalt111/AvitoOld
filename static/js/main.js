document.addEventListener("DOMContentLoaded", () => {
    const filterForm = document.getElementById("filter-form");
    const resultsBox = document.getElementById("listing-results");
    const loadingIndicator = document.getElementById("loading-indicator");

    if (!filterForm || !resultsBox || !loadingIndicator) {
        return;
    }

    let timerId = null;

    const loadListings = () => {
        const url = new URL(filterForm.dataset.url || filterForm.action, window.location.origin);
        const params = new URLSearchParams(new FormData(filterForm));

        url.search = params.toString();
        loadingIndicator.classList.remove("hidden");

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Request failed");
                }
                return response.text();
            })
            .then((html) => {
                resultsBox.innerHTML = html;
                window.history.replaceState({}, "", url);
            })
            .catch(() => {
                resultsBox.innerHTML = "<p>Не удалось загрузить объявления.</p>";
            })
            .finally(() => {
                loadingIndicator.classList.add("hidden");
            });
    };

    filterForm.addEventListener("submit", (event) => {
        event.preventDefault();
        loadListings();
    });

    filterForm.querySelectorAll("input, select").forEach((field) => {
        const eventName = field.tagName === "SELECT" ? "change" : "input";

        field.addEventListener(eventName, () => {
            clearTimeout(timerId);
            timerId = setTimeout(loadListings, 250);
        });
    });
});
