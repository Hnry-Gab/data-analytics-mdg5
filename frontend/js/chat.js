/**
 * Chatbot UI — SSE streaming integration with backend
 * Open / Close / Expand / Minimize + real LLM chat via /api/chat
 */
(function () {
    const fab      = document.getElementById("chat-fab");
    const overlay  = document.getElementById("chat-overlay");
    const btnClose = document.getElementById("chat-close");
    const btnExpand = document.getElementById("chat-expand");
    const btnMin   = document.getElementById("chat-minimize");
    const input    = document.getElementById("chat-input");
    const sendBtn  = document.getElementById("chat-send");
    const messages = document.getElementById("chat-messages");

    /* ── Window controls ─────────────────────────────────── */

    function open() {
        overlay.classList.remove("chat-hidden");
        fab.classList.add("chat-fab--hidden");
        input.focus();
    }

    function close() {
        overlay.classList.add("chat-hidden");
        overlay.classList.remove("chat-expanded");
        fab.classList.remove("chat-fab--hidden");
    }

    function expand() {
        overlay.classList.add("chat-expanded");
        const chartHelp = document.getElementById("chart-help-overlay");
        if (chartHelp) chartHelp.classList.add("chart-help-hidden");
    }

    function minimize() {
        overlay.classList.remove("chat-expanded");
    }

    fab.addEventListener("click", open);
    btnClose.addEventListener("click", close);
    btnExpand.addEventListener("click", expand);
    btnMin.addEventListener("click", minimize);

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !overlay.classList.contains("chat-hidden")) {
            close();
        }
    });

    /* ── Helpers ──────────────────────────────────────────── */

    function escapeHtml(str) {
        const d = document.createElement("div");
        d.textContent = str;
        return d.innerHTML;
    }

    function scrollToBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function appendUserMessage(text) {
        const now = new Date().toISOString().slice(11, 19);
        const div = document.createElement("div");
        div.className = "chat-msg chat-msg--user";
        div.innerHTML = `<span class="chat-msg-meta">[USR ${now}]</span><p>${escapeHtml(text)}</p>`;
        messages.appendChild(div);
        scrollToBottom();
    }

    function createBotBubble() {
        const now = new Date().toISOString().slice(11, 19);
        const div = document.createElement("div");
        div.className = "chat-msg chat-msg--bot";
        div.innerHTML = `<span class="chat-msg-meta">[AI ${now}]</span><p class="chat-bot-text"></p>`;
        messages.appendChild(div);
        scrollToBottom();
        return div;
    }

    function appendTextDelta(botDiv, text) {
        const p = botDiv.querySelector(".chat-bot-text");
        if (p) p.textContent += text;
        scrollToBottom();
    }

    function showToolIndicator(botDiv, toolName) {
        let ind = botDiv.querySelector(".chat-tool-indicator");
        if (!ind) {
            ind = document.createElement("span");
            ind.className = "chat-tool-indicator";
            botDiv.appendChild(ind);
        }
        ind.textContent = `🔍 Consultando dados (${toolName})...`;
        scrollToBottom();
    }

    function hideToolIndicator(botDiv) {
        const ind = botDiv.querySelector(".chat-tool-indicator");
        if (ind) ind.remove();
    }

    function appendError(botDiv, message) {
        const err = document.createElement("p");
        err.className = "chat-error";
        err.textContent = `⚠ ${message}`;
        botDiv.appendChild(err);
        scrollToBottom();
    }

    function finalizeBotMessage(botDiv) {
        botDiv.classList.add("chat-msg--complete");
    }

    /* ── SSE event handler ───────────────────────────────── */

    function handleSSEEvent(type, data, botDiv) {
        switch (type) {
            case "text_delta":
                appendTextDelta(botDiv, data.content);
                break;
            case "tool_call":
                showToolIndicator(botDiv, data.name);
                break;
            case "tool_result":
                hideToolIndicator(botDiv);
                break;
            case "error":
                appendError(botDiv, data.message);
                break;
            case "done":
                finalizeBotMessage(botDiv);
                break;
        }
        scrollToBottom();
    }

    /* ── Send message ────────────────────────────────────── */

    let sending = false;

    async function sendMessage() {
        const text = input.value.trim();
        if (!text || sending) return;
        sending = true;

        if (!window._chatSessionId) {
            window._chatSessionId = crypto.randomUUID();
        }

        appendUserMessage(text);
        input.value = "";

        const botDiv = createBotBubble();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    session_id: window._chatSessionId,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop();

                let eventType = "";
                for (const line of lines) {
                    if (line.startsWith("event: ")) {
                        eventType = line.slice(7);
                    } else if (line.startsWith("data: ") && eventType) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            handleSSEEvent(eventType, data, botDiv);
                        } catch (_) { /* skip malformed JSON */ }
                        eventType = "";
                    }
                }
            }
        } catch (err) {
            appendError(botDiv, "Erro de conexão. Tente novamente.");
        } finally {
            sending = false;
            finalizeBotMessage(botDiv);
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendMessage();
    });
})();
