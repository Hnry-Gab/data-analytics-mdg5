/**
 * Chatbot UI — Mock interactions
 * Open / Close / Expand / Minimize
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
    }

    function minimize() {
        overlay.classList.remove("chat-expanded");
    }

    fab.addEventListener("click", open);
    btnClose.addEventListener("click", close);
    btnExpand.addEventListener("click", expand);
    btnMin.addEventListener("click", minimize);

    /* Close on Escape */
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !overlay.classList.contains("chat-hidden")) {
            close();
        }
    });

    /* Mock send */
    function getMockResponses() {
        return [
            t("chat.mock.r1"),
            t("chat.mock.r2"),
            t("chat.mock.r3"),
            t("chat.mock.r4"),
            t("chat.mock.r5"),
            t("chat.mock.r6"),
            t("chat.mock.r7"),
        ];
    }

    let mockIdx = 0;

    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        const now = new Date().toISOString().slice(11, 19);

        // User message
        const userDiv = document.createElement("div");
        userDiv.className = "chat-msg chat-msg--user";
        userDiv.innerHTML = `<span class="chat-msg-meta">[USR ${now}]</span><p>${escapeHtml(text)}</p>`;
        messages.appendChild(userDiv);
        input.value = "";
        scrollToBottom();

        // Bot response (mock, with delay)
        setTimeout(() => {
            const responses = getMockResponses();
            const resp = responses[mockIdx % responses.length];
            mockIdx++;
            const botNow = new Date().toISOString().slice(11, 19);
            const botDiv = document.createElement("div");
            botDiv.className = "chat-msg chat-msg--bot";
            botDiv.innerHTML = `<span class="chat-msg-meta">[AI ${botNow}]</span><p>${resp}</p>`;
            messages.appendChild(botDiv);
            scrollToBottom();
        }, 600 + Math.random() * 800);
    }

    function scrollToBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function escapeHtml(str) {
        const d = document.createElement("div");
        d.textContent = str;
        return d.innerHTML;
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendMessage();
    });
})();
