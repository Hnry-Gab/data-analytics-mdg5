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
        top: "0",
        left: "0",
        width: "14px",
        height: "14px",
        borderRadius: "50%",
        background: "#00F0FF",
        pointerEvents: "none",
        zIndex: "9999",
        mixBlendMode: "difference",
        transition: "opacity 0.2s ease",
        transform: "translate3d(-100px, -100px, 0) scale(1)",
        opacity: "0",
    });
    document.body.appendChild(dot);

    let targetScale = 1;
    let currentScale = 1;
    let mx = -100, my = -100;

    document.addEventListener("mousemove", (e) => {
        mx = e.clientX;
        my = e.clientY;
        dot.style.opacity = "1";
        // Aplicação imediata da posição para eliminar latência
        updateTransform();
    });

    document.addEventListener("mouseleave", () => {
        dot.style.opacity = "0";
    });

    function updateTransform() {
        dot.style.transform = `translate3d(${mx}px, ${my}px, 0) translate(-50%, -50%) scale(${currentScale})`;
    }

    // Loop apenas para suavizar a transição de escala (Hover)
    (function scaleLoop() {
        if (Math.abs(targetScale - currentScale) > 0.001) {
            currentScale += (targetScale - currentScale) * 0.2;
            updateTransform();
        }
        requestAnimationFrame(scaleLoop);
    })();

    /* Reações de Hover via Event Delegation */
    const BTNS  = "button, a, .nav-tab, .btn-lime";
    const CARDS = ".glass-card, .kpi-card, .rec-card, .chart-card";

    document.addEventListener("mouseover", (e) => {
        const target = e.target;
        if (target.closest(BTNS)) targetScale = 2.8;
        else if (target.closest(CARDS)) targetScale = 1.8;
    });

    document.addEventListener("mouseout", (e) => {
        const target = e.target;
        if (target.closest(BTNS) || target.closest(CARDS)) {
            targetScale = 1;
        }
    });
})();
