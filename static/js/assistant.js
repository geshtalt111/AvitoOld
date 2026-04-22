document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("assistant-form");
    const historyBox = document.getElementById("assistant-history");
    const clearButton = document.getElementById("assistant-clear");
    const feedback = document.getElementById("assistant-feedback");

    if (!form || !historyBox || !clearButton || !feedback) {
        return;
    }

    const textarea = form.querySelector('textarea[name="message"]');
    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    const submitButton = form.querySelector('button[type="submit"]');

    if (!textarea || !csrfToken || !submitButton) {
        return;
    }

    const setFeedback = (text) => {
        feedback.textContent = text;
    };

    const scrollHistoryToBottom = () => {
        historyBox.scrollTop = historyBox.scrollHeight;
    };

    const createBubble = (role, text) => {
        const bubble = document.createElement("article");
        bubble.className = `assistant-bubble assistant-bubble-${role}`;

        const roleLabel = document.createElement("div");
        roleLabel.className = "assistant-bubble-role";
        roleLabel.textContent = role === "user" ? "Вы" : "Помощник";

        const content = document.createElement("div");
        content.className = "assistant-bubble-text";

        const lines = String(text).split("\n");
        lines.forEach((line, index) => {
            if (index > 0) {
                content.appendChild(document.createElement("br"));
            }
            content.appendChild(document.createTextNode(line));
        });

        bubble.append(roleLabel, content);
        return bubble;
    };

    const renderWelcome = () => {
        const welcomeText = historyBox.dataset.welcome || "Помощник готов отвечать.";
        historyBox.innerHTML = "";
        const welcomeBubble = createBubble("assistant", welcomeText);
        welcomeBubble.classList.add("assistant-bubble-welcome");
        historyBox.appendChild(welcomeBubble);
        clearButton.disabled = true;
        scrollHistoryToBottom();
    };

    form.addEventListener("submit", (event) => {
        const message = textarea.value.trim();
        if (!message) {
            event.preventDefault();
            setFeedback("Введите вопрос.");
            textarea.focus();
            return;
        }

        submitButton.textContent = "Отправляем...";
        submitButton.setAttribute("aria-disabled", "true");
        textarea.readOnly = true;
        clearButton.disabled = true;
        setFeedback("Отправляем вопрос помощнику...");
    });

    clearButton.addEventListener("click", async () => {
        setFeedback("Очищаем историю...");
        clearButton.disabled = true;

        try {
            const response = await fetch(form.dataset.clearUrl, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                },
            });

            const data = await response.json();
            if (!response.ok || !data.ok) {
                throw new Error("Не удалось очистить чат.");
            }

            renderWelcome();
            textarea.value = "";
            setFeedback("История очищена.");
        } catch (error) {
            clearButton.disabled = historyBox.children.length <= 1;
            setFeedback(error.message || "Не удалось очистить чат.");
        } finally {
            textarea.focus();
        }
    });

    textarea.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            form.requestSubmit();
        }
    });

    scrollHistoryToBottom();
});
