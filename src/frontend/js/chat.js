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

    /** Minimal Markdown → HTML (safe — escapes first, then applies formatting) */
    function renderMarkdown(raw) {
        let html = escapeHtml(raw);

        // Bold: **text**
        html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

        // Inline code: `code`
        html = html.replace(/`([^`]+)`/g, '<code class="chat-inline-code">$1</code>');

        // Line breaks
        html = html.replace(/\n/g, "<br>");

        // Bullet lists: lines starting with "- " (after <br>)
        html = html.replace(/(?:^|<br>)- (.+?)(?=<br>|$)/g, (_, item) => {
            return `<br><span class="chat-bullet">•</span> ${item}`;
        });

        return html;
    }

    /** UUID fallback for non-secure contexts (e.g. 0.0.0.0) */
    function fallbackUUID() {
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
            const r = (Math.random() * 16) | 0;
            return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
        });
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
        div.innerHTML =
            `<span class="chat-msg-meta">[AI ${now}]</span>` +
            `<p class="chat-bot-text"><span class="chat-typing"><span>.</span><span>.</span><span>.</span></span></p>`;
        messages.appendChild(div);
        scrollToBottom();
        return div;
    }

    /** Remove typing indicator on first real content */
    function removeTypingIndicator(botDiv) {
        const typing = botDiv.querySelector(".chat-typing");
        if (typing) typing.remove();
    }

    /** Raw text accumulator (per bot message) */
    let _rawText = "";

    function appendTextDelta(botDiv, text) {
        removeTypingIndicator(botDiv);
        _rawText += text;
        const p = botDiv.querySelector(".chat-bot-text");
        if (p) p.innerHTML = renderMarkdown(_rawText);
        scrollToBottom();
    }

    function showToolIndicator(botDiv, toolName) {
        removeTypingIndicator(botDiv);
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
        removeTypingIndicator(botDiv);
        const err = document.createElement("p");
        err.className = "chat-error";
        err.textContent = `⚠ ${message}`;
        botDiv.appendChild(err);
        scrollToBottom();
    }

    function finalizeBotMessage(botDiv) {
        removeTypingIndicator(botDiv);
        botDiv.classList.add("chat-msg--complete");
    }

    function setInputEnabled(enabled) {
        input.disabled = !enabled;
        sendBtn.disabled = !enabled;
        if (enabled) input.focus();
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

    /* ── Error message helper ────────────────────────────── */

    async function getErrorMessage(response) {
        const status = response.status;
        if (status === 429) return "Limite de requisições atingido. Aguarde um momento e tente novamente.";
        if (status === 503) {
            try {
                const body = await response.json();
                return body.detail || "Chatbot indisponível no momento.";
            } catch (_) {
                return "Chatbot indisponível no momento.";
            }
        }
        return `Erro do servidor (HTTP ${status}). Tente novamente.`;
    }

    /* ── Send message ────────────────────────────────────── */

    let sending = false;

    async function sendMessage() {
        const text = input.value.trim();
        if (!text || sending) return;
        sending = true;
        setInputEnabled(false);

        if (!window._chatSessionId) {
            window._chatSessionId = (crypto.randomUUID?.bind(crypto) || fallbackUUID)();
        }

        appendUserMessage(text);
        input.value = "";

        const botDiv = createBotBubble();
        _rawText = "";

        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 120_000);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    session_id: window._chatSessionId,
                }),
                signal: controller.signal,
            });

            if (!response.ok) {
                const errorMsg = await getErrorMessage(response);
                throw new Error(errorMsg);
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
            const msg = err.name === "AbortError"
                ? "Tempo limite atingido. Tente novamente."
                : (err.message || "Erro de conexão. Tente novamente.");
            appendError(botDiv, msg);
        } finally {
            clearTimeout(timeout);
            sending = false;
            setInputEnabled(true);
            finalizeBotMessage(botDiv);
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendMessage();
    });
})();
