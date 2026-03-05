/**
 * Custom cursor — Keita Yamada tech-noir
 * Smooth-following cyan dot with scale reactions
 * Skipped on touch devices
 */
(function () {
    if (matchMedia("(pointer: coarse)").matches) return;

    const dot = document.createElement("div");
    Object.assign(dot.style, {
        position: "fixed",
        top: "-50px",
        left: "-50px",
        width: "14px",
        height: "14px",
        borderRadius: "50%",
        background: "#00F0FF",
        pointerEvents: "none",
        zIndex: "9999",
        mixBlendMode: "difference",
        transition: "transform 0.15s cubic-bezier(.16,1,.3,1), opacity 0.2s ease",
        transform: "translate(-50%,-50%) scale(1)",
        opacity: "0",
    });
    document.body.appendChild(dot);

    let mx = -50, my = -50, cx = -50, cy = -50;

    document.addEventListener("mousemove", (e) => {
        mx = e.clientX;
        my = e.clientY;
        dot.style.opacity = "1";
    });

    document.addEventListener("mouseleave", () => {
        dot.style.opacity = "0";
    });

    (function loop() {
        cx += (mx - cx) * 0.18;
        cy += (my - cy) * 0.18;
        dot.style.left = cx + "px";
        dot.style.top  = cy + "px";
        requestAnimationFrame(loop);
    })();

    /* Hover reactions */
    const BTNS  = "button, a, .nav-tab, .btn-lime";
    const CARDS = ".glass-card, .kpi-card, .rec-card, .chart-card";

    document.addEventListener("mouseover", (e) => {
        if (e.target.closest(BTNS))  dot.style.transform = "translate(-50%,-50%) scale(2.8)";
        else if (e.target.closest(CARDS)) dot.style.transform = "translate(-50%,-50%) scale(1.8)";
    });

    document.addEventListener("mouseout", (e) => {
        if (e.target.closest(BTNS) || e.target.closest(CARDS)) {
            dot.style.transform = "translate(-50%,-50%) scale(1)";
        }
    });
})();
