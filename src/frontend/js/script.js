/**
 * Olist — Logistics Intelligence
 * Keita Yamada tech-noir aesthetic — Vanilla JS + Plotly.js
 */

/* ── Constants ───────────────────────────────────────────────────────── */

const LIME  = "#0000FF";
const PURP  = "#0000FF";
const CYAN  = "#00F0FF";
const ALERT = "#FF0000";
const WHITE = "#FFFFFF";
const GHOST = "rgba(255,255,255,0.06)";
const FAINT = "rgba(255,255,255,0.12)";
const DIM   = "rgba(255,255,255,0.60)";
const MUTED = "rgba(255,255,255,0.75)";
const DAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const DAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

/* ── i18n ─────────────────────────────────────────────────────────────── */

const CURRENT_LANG = navigator.language.startsWith("pt") ? "pt" : "en";
const DAYS = CURRENT_LANG === "pt" ? DAYS_PT : DAYS_EN;

const I18N = {
    en: {
        // Page title
        "title":              "Olist — Logistics Intelligence",
        // Nav
        "nav.subtitle":       "Logistics Intelligence",
        "nav.dashboard":      "Dashboard",
        "nav.insights":       "Insights",
        "nav.predictor":      "Predictor",
        // Dashboard hero
        "dash.heroLabel":     "DASHBOARD",
        "dash.heroLine1":     "Delivery performance",
        "dash.heroLine2":     "under the lens.",
        "dash.heroSub":       "Comprehensive analytics across 96k+ orders — delay rates, freight costs, geographic patterns and timelines.",
        // Dashboard filters
        "dash.filterState":   "State",
        "dash.allStates":     "All States",
        "dash.filterPeriod":  "Period",
        "dash.fullDataset":   "Full dataset",
        // KPIs
        "dash.kpiOrders":     "TOTAL ORDERS",
        "dash.kpiDelayed":    "DELAYED",
        "dash.kpiFreight":    "AVG FREIGHT",
        "dash.kpiDelta":      "DELTA DAYS",
        // Charts
        "dash.chartDelay":    "DELAY DISTRIBUTION",
        "dash.chartFreight":  "FREIGHT COST",
        "dash.chartGeo":      "GEOGRAPHIC DELAY",
        "dash.tagChoropleth": "Choropleth",
        "dash.chartTopStates":"TOP STATES BY DELAY",
        "dash.tagRanking":    "Ranking",
        "dash.chartTimeline": "DELAY TIMELINE",
        "dash.tagTimeline":   "Timeline",
        "dash.chartScatter":  "PRICE × FREIGHT",
        "dash.tagOutcome":    "Outcome",
        // Gauge titles
        "gauge.delayRate":    "Delay Rate",
        "gauge.avgFreight":   "Avg Freight",
        // Map colorbar
        "map.delayPct":       "Delay %",
        // Scatter legend
        "scatter.onTime":     "On time",
        "scatter.delayed":    "Delayed",
        // KPI dynamic
        "kpi.ofTotal":        "% of total",
        // Insights hero
        "ins.heroLabel":      "INSIGHTS",
        "ins.heroLine1":      "Patterns that explain",
        "ins.heroLine2":      "the delays.",
        "ins.heroSub":        "Deep-dive into interstate routes, product categories, seller speed and freight dynamics.",
        // Insights sections
        "ins.labelInterstate":"INTERSTATE",
        "ins.titleInterstate":"Interstate vs Intrastate",
        "ins.captionInterstate":"delay rate for cross-state routes",
        "ins.labelCategories":"CATEGORIES",
        "ins.titleCategories":"Categories at Risk",
        "ins.labelSellers":   "SELLERS",
        "ins.titleSellers":   "Seller Shipping Speed",
        "ins.sellerText":     "Distribution of seller shipping speed, split by delivery outcome.",
        "ins.labelFreight":   "FREIGHT",
        "ins.titleFreight":   "Freight Dynamics",
        "ins.freightText":    "Freight ratio vs price — orders above the 0.5 line carry proportionally higher shipping costs.",
        "ins.labelMacro":     "MACRO-REGION",
        "ins.titleMacro":     "Macro-Region Routes",
        "ins.macroText":      "Detailed heatmap of delay rates between origin and destination regions. Highlights logistical bottlenecks such as Southeast to North/Northeast routes.",
        "heatmap.origin":     "Origin",
        "heatmap.dest":       "Dest",
        // Donut
        "donut.onTimeInter":  "On time (Inter)",
        "donut.delayedInter": "Delayed (Inter)",
        "donut.onTimeIntra":  "On time (Intra)",
        "donut.delayedIntra": "Delayed (Intra)",
        // Treemap colorbar
        "treemap.delayPct":   "Delay %",
        // Violin
        "violin.daysToShip":  "Days to ship",
        "violin.onTime":      "On time",
        "violin.delayed":     "Delayed",
        // Freight scatter
        "fscatter.priceR":    "Price (R$)",
        "fscatter.freightRatio":"Freight Ratio",
        "fscatter.onTime":    "On time",
        "fscatter.delayed":   "Delayed",
        // Insight dynamic texts
        "ins.interText":      'Orders crossing state borders show a <strong>{interRate}%</strong> delay rate compared to {intraRate}% for intrastate. The distance and complexity of multi-state logistics drives this gap.',
        "ins.catText":        'The top offender — <strong>{cat}</strong> — reaches {pct}% delay rate across {total} orders. The chart sizes categories by volume and colors them by delay severity.',
        // Predictor hero
        "pred.heroLabel":     "PREDICTOR",
        "pred.heroLine1":     "Simulate before",
        "pred.heroLine2":     "you ship.",
        "pred.heroSub":       "Feed order parameters and get an instant risk assessment powered by our logistic model.",
        // Predictor form
        "pred.parameters":    "Parameters",
        "pred.route":         "Route",
        "pred.origin":        "Origin state",
        "pred.destination":   "Destination state",
        "pred.product":       "Product",
        "pred.weight":        "Weight (g)",
        "pred.price":         "Price (R$)",
        "pred.volume":        "Volume (cm³)",
        "pred.freight":       "Freight (R$)",
        "pred.operations":    "Operations",
        "pred.sellerDays":    'Seller shipping days: <span class="field-val" id="seller-days-val">{val}</span>',
        "pred.purchaseDay":   'Purchase day: <span class="field-val" id="purchase-day-val">{val}</span>',
        "pred.submit":        "Run Simulation →",
        "pred.waiting":       "Adjust the parameters above and run the simulation to see the risk assessment.",
        // Predictor results
        "pred.highRisk":      "HIGH RISK",
        "pred.moderate":      "MODERATE",
        "pred.lowRisk":       "LOW RISK",
        "pred.featureProfile":"FEATURE PROFILE",
        "pred.recActions":    "RECOMMENDED ACTIONS",
        "pred.recInterstate": "Interstate route — consider express carrier and +20% delivery buffer.",
        "pred.recSeller":     "Seller shows {days}d avg ship time — flag for support.",
        "pred.recFreight":    "High freight ratio — review pricing or route optimization.",
        "pred.recOk":         "All parameters within optimal range. No actions required.",
        // Radar categories
        "radar.weight":       "Weight",
        "radar.price":        "Price",
        "radar.freight":      "Freight",
        "radar.volume":       "Volume",
        "radar.fRatio":       "F.Ratio",
        "radar.sellerSpd":    "Seller Spd",
        "radar.interstate":   "Interstate",
        // Footer
        "footer.text":        "Olist Logistics Intelligence — Academic project · ALPHA EDTECH 2026",
        // Chat
        "chat.title":         "OLIST AI",
        "chat.status":        "// online",
        "chat.sysConnect":    "Connection established. OLIST AI v1.0 ready.",
        "chat.welcome":       "Welcome to Olist Logistics Intelligence. I can help you analyze delivery patterns, predict delays, and optimize freight routes. What would you like to explore?",
        "chat.placeholder":   "Type a message...",
        "chartHelp.title":    "CHART PREVIEW",
        "chartHelp.ask":      "Ask about this chart",
    },
    pt: {
        "title":              "Olist - Inteligência Logística",
        "nav.subtitle":       "Inteligência Logística",
        "nav.dashboard":      "Dashboard",
        "nav.insights":       "Insights",
        "nav.predictor":      "Preditor",
        "dash.heroLabel":     "DASHBOARD",
        "dash.heroLine1":     "Performance de entrega",
        "dash.heroLine2":     "sob análise.",
        "dash.heroSub":       "Análise completa de mais de 96 mil pedidos — taxas de atraso, custos de frete, padrões geográficos e linhas do tempo.",
        "dash.filterState":   "Estado",
        "dash.allStates":     "Todos os Estados",
        "dash.filterPeriod":  "Período",
        "dash.fullDataset":   "Dataset completo",
        "dash.kpiOrders":     "TOTAL DE PEDIDOS",
        "dash.kpiDelayed":    "ATRASADOS",
        "dash.kpiFreight":    "FRETE MÉDIO",
        "dash.kpiDelta":      "DELTA DIAS",
        "dash.chartDelay":    "DISTRIBUIÇÃO DE ATRASOS",
        "dash.chartFreight":  "CUSTO DE FRETE",
        "dash.chartGeo":      "ATRASO GEOGRÁFICO",
        "dash.tagChoropleth": "Coroplético",
        "dash.chartTopStates":"ESTADOS COM MAIS ATRASO",
        "dash.tagRanking":    "Ranking",
        "dash.chartTimeline": "LINHA DO TEMPO DE ATRASOS",
        "dash.tagTimeline":   "Linha do Tempo",
        "dash.chartScatter":  "PREÇO × FRETE",
        "dash.tagOutcome":    "Resultado",
        "gauge.delayRate":    "Taxa de Atraso",
        "gauge.avgFreight":   "Frete Médio",
        "map.delayPct":       "Atraso %",
        "scatter.onTime":     "No prazo",
        "scatter.delayed":    "Atrasado",
        "kpi.ofTotal":        "% do total",
        "ins.heroLabel":      "INSIGHTS",
        "ins.heroLine1":      "Padrões que explicam",
        "ins.heroLine2":      "os atrasos.",
        "ins.heroSub":        "Análise aprofundada de rotas interestaduais, categorias de produto, velocidade dos vendedores e dinâmicas de frete.",
        "ins.labelInterstate":"INTERESTADUAL",
        "ins.titleInterstate":"Interestadual vs Intraestadual",
        "ins.captionInterstate":"taxa de atraso em rotas interestaduais",
        "ins.labelCategories":"CATEGORIAS",
        "ins.titleCategories":"Categorias em Risco",
        "ins.labelSellers":   "VENDEDORES",
        "ins.titleSellers":   "Velocidade de Envio do Vendedor",
        "ins.sellerText":     "Distribuição da velocidade de envio dos vendedores, dividida por resultado de entrega.",
        "ins.labelFreight":   "FRETE",
        "ins.titleFreight":   "Dinâmicas de Frete",
        "ins.freightText":    "Razão frete vs preço — pedidos acima da linha 0.5 possuem custos de envio proporcionalmente maiores.",
        "ins.labelMacro":     "MACRO-REGIÃO",
        "ins.titleMacro":     "Rotas Macro-Regionais",
        "ins.macroText":      "Heatmap detalhado das taxas de atraso entre regiões de origem e destino. Destaca gargalos logísticos como rotas do Sudeste para o Norte/Nordeste.",
        "heatmap.origin":     "Origem",
        "heatmap.dest":       "Destino",
        "donut.onTimeInter":  "No prazo (Inter)",
        "donut.delayedInter": "Atrasado (Inter)",
        "donut.onTimeIntra":  "No prazo (Intra)",
        "donut.delayedIntra": "Atrasado (Intra)",
        "treemap.delayPct":   "Atraso %",
        "violin.daysToShip":  "Dias para enviar",
        "violin.onTime":      "No prazo",
        "violin.delayed":     "Atrasado",
        "fscatter.priceR":    "Preço (R$)",
        "fscatter.freightRatio":"Razão de Frete",
        "fscatter.onTime":    "No prazo",
        "fscatter.delayed":   "Atrasado",
        "ins.interText":      'Pedidos que cruzam fronteiras estaduais apresentam uma taxa de atraso de <strong>{interRate}%</strong> comparada a {intraRate}% para intraestaduais. A distância e complexidade da logística multiestadual impulsionam essa diferença.',
        "ins.catText":        'O maior infrator — <strong>{cat}</strong> — atinge {pct}% de atraso em {total} pedidos. No gráfico, o tamanho do bloco representa o volume de vendas e a cor a severidade do atraso.',
        "pred.heroLabel":     "PREDITOR",
        "pred.heroLine1":     "Simule antes",
        "pred.heroLine2":     "de enviar.",
        "pred.heroSub":       "Insira os parâmetros do pedido e obtenha uma avaliação de risco instantânea do nosso modelo logístico.",
        "pred.parameters":    "Parâmetros",
        "pred.route":         "Rota",
        "pred.origin":        "Estado de origem",
        "pred.destination":   "Estado de destino",
        "pred.product":       "Produto",
        "pred.weight":        "Peso (g)",
        "pred.price":         "Preço (R$)",
        "pred.volume":        "Volume (cm³)",
        "pred.freight":       "Frete (R$)",
        "pred.operations":    "Operações",
        "pred.sellerDays":    'Dias de envio do vendedor: <span class="field-val" id="seller-days-val">{val}</span>',
        "pred.purchaseDay":   'Dia da compra: <span class="field-val" id="purchase-day-val">{val}</span>',
        "pred.submit":        "Executar Simulação →",
        "pred.waiting":       "Ajuste os parâmetros acima e execute a simulação para ver a avaliação de risco.",
        "pred.highRisk":      "ALTO RISCO",
        "pred.moderate":      "MODERADO",
        "pred.lowRisk":       "BAIXO RISCO",
        "pred.featureProfile":"PERFIL DE FEATURES",
        "pred.recActions":    "AÇÕES RECOMENDADAS",
        "pred.recInterstate": "Rota interestadual — considere transportadora expressa e +20% de margem no prazo.",
        "pred.recSeller":     "Vendedor com {days}d de tempo médio de envio — sinalizar para suporte.",
        "pred.recFreight":    "Alta razão de frete — revisar precificação ou otimização de rota.",
        "pred.recOk":         "Todos os parâmetros dentro da faixa ideal. Nenhuma ação necessária.",
        "radar.weight":       "Peso",
        "radar.price":        "Preço",
        "radar.freight":      "Frete",
        "radar.volume":       "Volume",
        "radar.fRatio":       "Razão F.",
        "radar.sellerSpd":    "Vel. Vendedor",
        "radar.interstate":   "Interestadual",
        "footer.text":        "Olist Inteligência Logística — Projeto acadêmico · ALPHA EDTECH 2026",
        // Chat
        "chat.title":         "OLIST IA",
        "chat.status":        "// online",
        "chat.sysConnect":    "Conexão estabelecida. OLIST IA v1.0 pronta.",
        "chat.welcome":       "Bem-vindo à Olist Inteligência Logística. Posso ajudar a analisar padrões de entrega, prever atrasos e otimizar rotas de frete. O que deseja explorar?",
        "chat.placeholder":   "Digite uma mensagem...",
        "chartHelp.title":    "VISUALIZAÇÃO DO GRÁFICO",
        "chartHelp.ask":      "Pergunte sobre este gráfico",
    },
};

function t(key, params) {
    let str = (I18N[CURRENT_LANG] && I18N[CURRENT_LANG][key]) || I18N.en[key] || key;
    if (params) {
        Object.keys(params).forEach(k => {
            str = str.replaceAll("{" + k + "}", params[k]);
        });
    }
    return str;
}

function applyLanguage() {
    document.title = t("title");
    document.querySelectorAll("[data-i18n]").forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-html]").forEach(el => {
        const key = el.dataset.i18nHtml;
        if (key === "pred.sellerDays") {
            const val = document.getElementById("pred-seller-days")?.value || "3";
            el.innerHTML = t(key, { val });
        } else if (key === "pred.purchaseDay") {
            const idx = parseInt(document.getElementById("pred-day")?.value || "0");
            el.innerHTML = t(key, { val: DAYS[idx] });
        } else {
            el.innerHTML = t(key);
        }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        el.placeholder = t(el.dataset.i18nPlaceholder);
    });
}

const IS_TOUCH = matchMedia("(pointer: coarse)").matches;
const VW = window.innerWidth;
const SCALE = VW >= 3840 ? 2.4 : VW >= 2560 ? 1.8 : VW >= 1537 ? 1.4 : 1;

/** Scale Plotly height for large screens */
function pH(h) { return Math.round(h * SCALE); }

const PLOTLY_BASE = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "IBM Plex Mono, monospace", color: MUTED, size: Math.round(11 * SCALE) },
    hoverlabel: {
        bgcolor: "#111111",
        bordercolor: LIME,
        font: { family: "IBM Plex Mono, monospace", color: "#ECEBE9", size: Math.round(12 * SCALE) },
    },
    ...(IS_TOUCH && { dragmode: false }),
};

/** Merge fixedrange into axis config on touch devices */
function ax(cfg) { return IS_TOUCH ? { ...cfg, fixedrange: true } : cfg; }

const PLOTLY_CFG = { displayModeBar: false, responsive: true, scrollZoom: false };

/* ── Tab Navigation ──────────────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {
    const navTabs = document.querySelectorAll(".nav-tab");
    const pages   = document.querySelectorAll(".page");

    navTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.tab;
            navTabs.forEach(t => t.classList.remove("active"));
            pages.forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById("tab-" + target).classList.add("active");
            window.scrollTo({ top: 0, behavior: "instant" });

            // Lazy-render insights charts & resize all Plotly charts after tab becomes visible
            requestAnimationFrame(() => {
                if (target === "insights") renderInsightsIfNeeded();
                document.querySelectorAll("#tab-" + target + " .js-plotly-plot").forEach(el => {
                    Plotly.Plots.resize(el);
                });
            });
        });
    });

    // Apply language
    applyLanguage();

    // Slider live values
    const sellerSlider = document.getElementById("pred-seller-days");
    const daySlider    = document.getElementById("pred-day");

    if (sellerSlider) {
        sellerSlider.addEventListener("input", () => {
            const label = sellerSlider.closest(".form-field").querySelector("[data-i18n-html='pred.sellerDays']");
            if (label) label.innerHTML = t("pred.sellerDays", { val: sellerSlider.value });
            else document.getElementById("seller-days-val").textContent = sellerSlider.value;
        });
    }
    if (daySlider) {
        daySlider.addEventListener("input", () => {
            const label = daySlider.closest(".form-field").querySelector("[data-i18n-html='pred.purchaseDay']");
            if (label) label.innerHTML = t("pred.purchaseDay", { val: DAYS[daySlider.value] });
            else document.getElementById("purchase-day-val").textContent = DAYS[daySlider.value];
        });
    }

    // Scroll-triggered reveal
    initScrollReveal();

    // Bootstrap all tabs
    initDashboard();
    initInsights();
    initPredictor();

    // Resize Plotly charts on viewport change
    let resizeTimer;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            document.querySelectorAll(".js-plotly-plot").forEach(el => {
                Plotly.Plots.resize(el);
            });
        }, 200);
    });

    // Filtros do Dashboard
    const stateFilter = document.getElementById("dash-state-filter");
    const periodFilter = document.getElementById("dash-period-filter");
    if (stateFilter) stateFilter.addEventListener("change", handleDashboardFilterChange);
    if (periodFilter) periodFilter.addEventListener("change", handleDashboardFilterChange);

    // ── Chart Help: inject ? buttons & wire overlay ────────────────────
    initChartHelp();
});

/* ── Chart Help System ───────────────────────────────────────────────── */

function initChartHelp() {
    const helpOverlay  = document.getElementById("chart-help-overlay");
    const helpBody     = document.getElementById("chart-help-body");
    const helpTitle    = document.getElementById("chart-help-title");
    const helpClose    = document.getElementById("chart-help-close");
    const chatOverlay  = document.getElementById("chat-overlay");
    const chatFab      = document.getElementById("chat-fab");

    function injectBtn(card) {
        if (card.querySelector(".chart-help-btn")) return;

        // For Insights: place button next to the section-title (one per section)
        const section = card.closest(".insight-section");
        if (section) {
            if (section.querySelector(".chart-help-btn")) return;
            const title = section.querySelector(".section-title");
            if (title) {
                const btn = createBtn(card);
                title.appendChild(btn);
                return;
            }
        }

        // For Dashboard / Predictor: place inside .chart-label
        const btn = createBtn(card);
        const label = card.querySelector(".chart-label");
        if (label) {
            label.appendChild(btn);
        } else {
            card.prepend(btn);
        }
    }

    function createBtn(card) {
        const btn = document.createElement("button");
        btn.className = "chart-help-btn";
        btn.setAttribute("aria-label", t("chartHelp.ask"));
        btn.textContent = "?";
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            openChartHelp(card);
        });
        return btn;
    }

    // Inject ? button into every chart-card and insight-chart
    document.querySelectorAll(".chart-card, .insight-chart").forEach(injectBtn);

    // Expose for dynamically created cards (e.g. predictor)
    window.reinjectChartHelp = () => {
        document.querySelectorAll(".chart-card, .insight-chart").forEach(injectBtn);
    };

    function getChartLabel(card) {
        const label = card.querySelector(".chart-label");
        if (label) return label.textContent;
        const section = card.closest(".insight-section");
        if (section) {
            const title = section.querySelector(".section-title");
            if (title) return title.textContent;
        }
        return t("chartHelp.title");
    }

    function openChartHelp(card) {
        helpTitle.textContent = getChartLabel(card);

        // On small screens the left overlay is hidden via CSS; only open chat
        const showPreview = window.innerWidth > 768;

        // Don't open chart-help if chat is expanded (would overlap)
        const isExpanded = chatOverlay.classList.contains("chat-expanded");

        // Open chat overlay (right)
        chatOverlay.classList.remove("chat-hidden");
        chatFab.classList.add("chat-fab--hidden");

        if (!showPreview || isExpanded) return;

        helpBody.innerHTML = "";
        helpOverlay.classList.remove("chart-help-hidden");

        // Find the Plotly graph div. Plotly stores .data/.layout on the element
        // passed to Plotly.newPlot() — the one with the id like #dash-scatter.
        let plotDiv = null;
        const candidates = card.querySelectorAll("[id]");
        for (const el of candidates) {
            if (el.data && el.layout) { plotDiv = el; break; }
        }
        if (!plotDiv) {
            const jp = card.querySelector(".js-plotly-plot");
            if (jp) plotDiv = jp.data ? jp : (jp.parentElement?.data ? jp.parentElement : null);
        }

        if (plotDiv && plotDiv.data && plotDiv.layout) {
            // Plotly needs a container with concrete pixel dimensions.
            // Use requestAnimationFrame so the overlay is fully laid out first.
            requestAnimationFrame(() => {
                const bodyRect = helpBody.getBoundingClientRect();
                const w = Math.round(bodyRect.width - 32);  // minus padding
                const h = Math.round(bodyRect.height - 32);

                if (w < 50 || h < 50) return;

                const container = document.createElement("div");
                container.style.width = w + "px";
                container.style.height = h + "px";
                helpBody.innerHTML = "";
                helpBody.appendChild(container);

                const clonedData = JSON.parse(JSON.stringify(plotDiv.data));
                const clonedLayout = JSON.parse(JSON.stringify(plotDiv.layout));

                clonedLayout.autosize = false;
                clonedLayout.width = w;
                clonedLayout.height = h;

                const config = {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ["lasso2d", "select2d"]
                };

                Plotly.newPlot(container, clonedData, clonedLayout, config);
            });
        } else {
            // Fallback: static image from any Plotly element found
            const jp = card.querySelector(".js-plotly-plot") ||
                       card.querySelector("[id]");
            const srcEl = jp && jp._fullLayout ? jp : (jp?.parentElement?._fullLayout ? jp.parentElement : null);
            if (srcEl) {
                Plotly.toImage(srcEl, {
                    format: "png",
                    width: srcEl.offsetWidth || 800,
                    height: srcEl.offsetHeight || 500,
                    scale: 2,
                }).then(url => {
                    helpBody.innerHTML = "";
                    const img = document.createElement("img");
                    img.src = url;
                    img.alt = helpTitle.textContent;
                    helpBody.appendChild(img);
                });
            } else {
                helpBody.innerHTML = '<p style="color:var(--muted);font-family:var(--font-mono);font-size:0.7rem;text-align:center;">No chart preview available</p>';
            }
        }
    }

    function closeChartHelp() {
        helpOverlay.classList.add("chart-help-hidden");
        helpBody.innerHTML = "";
    }

    helpClose.addEventListener("click", closeChartHelp);

    // Also close chart help when chat is closed
    const chatClose = document.getElementById("chat-close");
    chatClose.addEventListener("click", closeChartHelp);

    // Close both on Escape
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !helpOverlay.classList.contains("chart-help-hidden")) {
            closeChartHelp();
        }
    });
}

/* ── Scroll Reveal ───────────────────────────────────────────────────── */

function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("revealed");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

    document.querySelectorAll(".reveal").forEach(el => {
        el.style.opacity = "0";
        el.style.transform = "translateY(40px)";
        observer.observe(el);
    });

    // Re-observe when tab changes
    document.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            setTimeout(() => {
                document.querySelectorAll(".reveal:not(.revealed)").forEach(el => {
                    observer.observe(el);
                });
                // Trigger immediate reveal for already-visible elements
                document.querySelectorAll(".page.active .reveal:not(.revealed)").forEach(el => {
                    el.classList.add("revealed");
                });
            }, 50);
        });
    });
}

// CSS injection for .revealed state
const revealStyle = document.createElement("style");
revealStyle.textContent = `.revealed { opacity: 1 !important; transform: translateY(0) !important; transition: opacity 0.7s cubic-bezier(.16,1,.3,1), transform 0.7s cubic-bezier(.16,1,.3,1); }`;
document.head.appendChild(revealStyle);

/* ═══════════════════════════════════════════════════════════════════════ */
/* TAB 1: DASHBOARD                                                      */
/* ═══════════════════════════════════════════════════════════════════════ */

async function initDashboard(state = "", year = "") {
    try {
        let url = `/api/stats`;
        const params = [];
        if (state) params.push(`state=${state}`);
        if (year && year !== "all") params.push(`year=${year}`);
        if (params.length > 0) url += "?" + params.join("&");

        const res = await fetch(url);
        if (res.ok) {
            const data = await res.json();
            
            // Controle de Layout Dinâmico (Mapa + Ranking)
            const geoGrid = document.getElementById("dash-geo-grid");
            const rankCard = document.getElementById("dash-rank-card");
            const stateBadge = document.getElementById("dash-state-badge");
            
            if (state) {
                // Estado Selecionado: Ocultar Ranking e expandir Mapa
                geoGrid.classList.add("is-filtered");
                rankCard.style.display = "none";
                
                // Mostrar Badge no Header do Mapa
                const statePct = data.map_data[state] || 0;
                stateBadge.textContent = `${state}: ${statePct.toFixed(1)}%`;
                stateBadge.style.display = "inline-flex";

                // Comparação com a média global (do ano selecionado)
                if (statePct > data.global_delay_rate) {
                    stateBadge.classList.add("state-badge--alert");
                } else {
                    stateBadge.classList.remove("state-badge--alert");
                }
            } else {
                // Global: Mostrar Ranking e resetar Mapa
                geoGrid.classList.remove("is-filtered");
                rankCard.style.display = "block";
                stateBadge.style.display = "none";
                renderRanking(data.ranking_data);
            }

            updateKPIs({
                orders: data.total_orders,
                delayed: data.delayed_orders,
                rate: data.delay_rate,
                avgFreight: data.avg_freight,
                deltaDays: data.delta_days, 
            });

            renderGaugeDelay(data.delay_rate);
            renderGaugeFreight(data.avg_freight);
            
            // O mapa deve ser sempre renderizado (com os dados filtrados ou globais)
            renderMap(data.map_data);
            renderTimeline(data.timeline_data);
            renderScatter(); 
        }
    } catch (e) {
        console.error("Falha ao carregar dashboard", e);
    }
}

// Handler para mudança nos filtros do Dashboard
function handleDashboardFilterChange() {
    const state = document.getElementById("dash-state-filter").value;
    const year = document.getElementById("dash-period-filter").value;
    initDashboard(state, year);
}

function updateKPIs(d) {
    document.getElementById("kpi-orders").textContent      = d.orders.toLocaleString();
    document.getElementById("kpi-delayed").textContent     = d.delayed.toLocaleString();
    document.getElementById("kpi-delayed-pct").textContent = d.rate.toFixed(1) + t("kpi.ofTotal");
    document.getElementById("kpi-freight").textContent     = "R$ " + d.avgFreight.toFixed(0);
    document.getElementById("kpi-delta").textContent       = (d.deltaDays >= 0 ? "+" : "") + d.deltaDays.toFixed(1) + "d";
}

/* ── Gauges ───────────────────────────────────────────────────────────── */

function renderGaugeDelay(rate) {
    Plotly.newPlot("dash-gauge-delay", [{
        type: "indicator", mode: "gauge+number", value: rate,
        number: { suffix: "%", font: { family: "Space Grotesk", size: pH(48), color: WHITE } },
        title: { text: t("gauge.delayRate"), font: { family: "IBM Plex Mono", size: pH(11), color: DIM } },
        gauge: {
            axis: { range: [0, 50], tickfont: { color: DIM, size: pH(10) }, tickcolor: FAINT, dtick: 10 },
            bar: { color: ALERT, thickness: 0.7 },
            bgcolor: "#111111", borderwidth: 0,
            steps: [
                { range: [0, 15], color: "#0d0d0d" },
                { range: [15, 30], color: "#161616" },
                { range: [30, 50], color: "#1a1118" },
            ],
            threshold: { line: { color: WHITE, width: 2 }, thickness: 0.8, value: rate },
        },
    }], { ...PLOTLY_BASE, height: pH(240), margin: { l: 30, r: 30, t: 50, b: 10 } }, PLOTLY_CFG);
}

function renderGaugeFreight(avg) {
    Plotly.newPlot("dash-gauge-freight", [{
        type: "indicator", mode: "gauge+number", value: avg,
        number: { prefix: "R$", font: { family: "Space Grotesk", size: pH(48), color: WHITE } },
        title: { text: t("gauge.avgFreight"), font: { family: "IBM Plex Mono", size: pH(11), color: DIM } },
        gauge: {
            axis: { range: [0, 150], tickfont: { color: DIM, size: pH(10) }, tickcolor: FAINT, dtick: 30 },
            bar: { color: LIME, thickness: 0.7 },
            bgcolor: "#111111", borderwidth: 0,
            steps: [
                { range: [0, 50],  color: "#0d0d0d" },
                { range: [50, 100], color: "#110d17" },
                { range: [100, 150], color: "#16121e" },
            ],
        },
    }], { ...PLOTLY_BASE, height: pH(240), margin: { l: 30, r: 30, t: 50, b: 10 } }, PLOTLY_CFG);
}

/* ── Map ──────────────────────────────────────────────────────────────── */

function renderMap(mapData = {}) {
    const states = Object.keys(mapData);
    const rates  = Object.values(mapData);

    if (states.length === 0) {
        // Fallback global se vazio por erro
        return;
    }

    Plotly.newPlot("dash-map", [{
        type: "choropleth",
        geojson: "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations: states, featureidkey: "properties.sigla", z: rates,
        zmin: 0, zmax: 40, // Escala fixa nacional (máximo esperado ~35-40%)
        autocolorscale: false,
        colorscale: [
            [0, "#0a0a0a"],   // 0% - Preto
            [0.1, "#0a0a2e"], // 4% - Azul bem escuro
            [0.25, "#000066"], // 10% - Azul profundo
            [0.4, "#440044"],  // 16% - Roxo (transição)
            [0.6, ALERT],      // 24% - Vermelho (AL está aqui)
            [1.0, "#FF4D4D"]   // 40% - Vermelho mais claro
        ],
        colorbar: {
            bgcolor: "rgba(0,0,0,0)", borderwidth: 0,
            tickfont: { color: DIM }, title: { text: t("map.delayPct"), font: { color: DIM } },
            len: 0.8, thickness: 15
        },
        hovertemplate: "%{location}: %{z:.1f}%<extra></extra>",
    }], {
        ...PLOTLY_BASE, height: pH(520), margin: { l: 0, r: 0, t: 0, b: 0 },
        geo: { 
            scope: "south america", 
            fitbounds: "locations", 
            visible: false, 
            bgcolor: "rgba(0,0,0,0)",
            projection: { type: "mercator" }
        },
    }, PLOTLY_CFG);
}

/* ── Ranking ──────────────────────────────────────────────────────────── */

function renderRanking(rankingData = []) {
    const traces = [];

    rankingData.forEach((item, i) => {
        const s = item.state;
        const r = item.rate;
        traces.push({
            x: [0, r], y: [s, s], mode: "lines",
            line: { color: i === 0 ? ALERT : FAINT, width: 2 },
            showlegend: false, hoverinfo: "skip",
        });
        traces.push({
            x: [r], y: [s], mode: "markers",
            marker: { size: 10, color: i === 0 ? ALERT : LIME, symbol: "circle" },
            showlegend: false,
            hovertemplate: `${s}: %{x:.1f}%<extra></extra>`,
        });
    });

    Plotly.newPlot("dash-rank", traces, {
        ...PLOTLY_BASE, height: pH(520), margin: { l: 40, r: 20, t: 0, b: 30 },
        xaxis: ax({ gridcolor: FAINT, title: null, ticksuffix: "%" }),
        yaxis: ax({ gridcolor: "rgba(0,0,0,0)", title: null, autorange: true }),
    }, PLOTLY_CFG);
}

/* ── Timeline ─────────────────────────────────────────────────────────── */

function renderTimeline(timelineData = {x: [], y: []}) {
    Plotly.newPlot("dash-timeline", [{
        x: timelineData.x, y: timelineData.y, type: "scatter", mode: "lines",
        fill: "tozeroy",
        fillcolor: "rgba(0, 0, 255, 0.04)",
        line: { color: LIME, width: 2, shape: "spline" },
        hovertemplate: "%{x}: %{y:.1f}%<extra></extra>",
    }], {
        ...PLOTLY_BASE, height: pH(340), margin: { l: 50, r: 20, t: 10, b: 40 },
        xaxis: ax({ gridcolor: FAINT, title: null }),
        yaxis: ax({ gridcolor: FAINT, title: null, ticksuffix: "%" }),
    }, PLOTLY_CFG);
}

/* ── Price vs Freight Scatter ────────────────────────────────────────── */

function renderScatter() {
    const n = 900;
    const okX = [], okY = [], dX = [], dY = [];
    for (let i = 0; i < n; i++) {
        const p = Math.random() * 500 + 10;
        const f = Math.random() * 80 + 5;
        if (Math.random() > 0.93) { dX.push(p); dY.push(f); }
        else { okX.push(p); okY.push(f); }
    }

    Plotly.newPlot("dash-scatter", [
        { x: okX, y: okY, mode: "markers", name: t("scatter.onTime"),
          marker: { size: 3, color: FAINT, opacity: 0.5 },
          hovertemplate: "R$%{x:.0f} | R$%{y:.0f}<extra>" + t("scatter.onTime") + "</extra>" },
        { x: dX, y: dY, mode: "markers", name: t("scatter.delayed"),
          marker: { size: 5, color: ALERT, opacity: 0.7 },
          hovertemplate: "R$%{x:.0f} | R$%{y:.0f}<extra>" + t("scatter.delayed") + "</extra>" },
    ], {
        ...PLOTLY_BASE, height: pH(380), margin: { l: 50, r: 20, t: 10, b: 40 },
        xaxis: ax({ gridcolor: FAINT, title: null }),
        yaxis: ax({ gridcolor: FAINT, title: null }),
        legend: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, font: { color: DIM } },
    }, PLOTLY_CFG);
    addLegendHint("dash-scatter");
}

/* ═══════════════════════════════════════════════════════════════════════ */
/* TAB 2: INSIGHTS                                                       */
/* ═══════════════════════════════════════════════════════════════════════ */

let insightsRendered = false;
let insightsData = null;

function initInsights() {
    // Defer rendering — charts need visible container for correct sizing
}

async function renderInsightsIfNeeded() {
    if (insightsRendered) return;
    
    document.getElementById("ins-inter-rate").textContent = "...";
    
    try {
        const res = await fetch("/api/insights");
        if (res.ok) {
            insightsData = await res.json();
        } else {
            console.error("Failed to fetch insights data");
        }
    } catch (e) {
        console.error("API error", e);
    }
    
    insightsRendered = true;
    renderDonut(insightsData?.donut);
    renderTreemap(insightsData?.treemap);
    renderViolin(insightsData?.violin);
    renderFreightScatter(insightsData?.scatter);
    renderHeatmap(insightsData?.heatmap);
}

function renderDonut(data) {
    if (!data) return;
    const interRate = data.inter_rate, intraRate = data.intra_rate;
    document.getElementById("ins-inter-rate").textContent = interRate.toFixed(1) + "%";
    document.getElementById("ins-inter-text").innerHTML =
        t("ins.interText", { interRate: interRate.toFixed(1), intraRate: intraRate.toFixed(1) });

    Plotly.newPlot("ins-donut-chart", [{
        labels: [t("donut.onTimeInter"), t("donut.delayedInter"), t("donut.onTimeIntra"), t("donut.delayedIntra")],
        values: [data.inter_ontime, data.inter_delayed, data.intra_ontime, data.intra_delayed],
        marker: { colors: [FAINT, ALERT, GHOST, "#440000"] },
        hole: 0.7, type: "pie",
        textfont: { family: "IBM Plex Mono", color: MUTED, size: pH(11) },
        textinfo: "percent",
        hovertemplate: "%{label}<br>%{value:,} orders<br>%{percent}<extra></extra>",
    }], {
        ...PLOTLY_BASE, height: pH(340), showlegend: true,
        margin: { l: 0, r: 0, t: 0, b: 0 },
        legend: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, font: { color: DIM, size: pH(10) } },
    }, PLOTLY_CFG);
    addLegendHint("ins-donut-chart");
}

function renderTreemap(data) {
    if (!data || !data.categories || data.categories.length === 0) return;
    const cats = data.categories.map(c => c.split("_").join(" "));
    const tots = data.totals;
    const pcts = data.delay_rates;

    Plotly.newPlot("ins-treemap-chart", [{
        type: "treemap", labels: cats, parents: cats.map(() => ""), values: pcts,
        marker: {
            colors: pcts,
            cmin: 5,
            cmax: Math.max(...pcts) + 1,
            colorscale: [[0, "#0d0d0d"], [0.3, "#0a0a2e"], [0.6, "#00003a"], [1, ALERT]],
            colorbar: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, tickfont: { color: DIM }, title: { text: t("treemap.delayPct"), font: { color: DIM } } },
            cornerradius: 6,
        },
        text: pcts.map(p => p.toFixed(1) + "%"),
        textfont: { family: "IBM Plex Mono", color: "#ECEBE9", size: pH(11) },
        textinfo: "label+text",
        hovertemplate: "%{label}<br>Orders: %{customdata:,}<br>Delay: %{color:.1f}%<extra></extra>",
        customdata: tots
    }], { ...PLOTLY_BASE, height: pH(440), margin: { l: 0, r: 0, t: 0, b: 0 } }, PLOTLY_CFG);

    document.getElementById("ins-cat-text").innerHTML =
        t("ins.catText", { cat: cats[0], pct: pcts[0].toFixed(1), total: tots[0].toLocaleString() });
}

function renderViolin(data) {
    if (!data || !data.on_time) return;
    
    Plotly.newPlot("ins-violin-chart", [
        { y: data.on_time, name: t("violin.onTime"), type: "violin", box: { visible: true }, meanline: { visible: true },
          fillcolor: FAINT, opacity: 0.8, line: { color: DIM }, marker: { color: DIM } },
        { y: data.delayed, name: t("violin.delayed"), type: "violin", box: { visible: true }, meanline: { visible: true },
          fillcolor: ALERT, opacity: 0.7, line: { color: ALERT }, marker: { color: ALERT } },
    ], {
        ...PLOTLY_BASE, height: pH(380), showlegend: true,
        margin: { l: 40, r: 0, t: 0, b: 40 },
        yaxis: ax({ title: t("violin.daysToShip"), gridcolor: FAINT }),
        xaxis: ax({ gridcolor: "rgba(0,0,0,0)" }),
        legend: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, font: { color: DIM } },
        violingap: 0.3, violinmode: "group",
    }, PLOTLY_CFG);
    addLegendHint("ins-violin-chart");
}

function renderFreightScatter(data) {
    if (!data || !data.on_time_x) return;

    Plotly.newPlot("ins-freight-scatter", [
        { x: data.on_time_x, y: data.on_time_y, mode: "markers", name: t("fscatter.onTime"),
          marker: { size: 3, color: FAINT, opacity: 0.4 },
          hovertemplate: "R$%{x:.0f} | Ratio: %{y:.2f}<extra>" + t("fscatter.onTime") + "</extra>" },
        { x: data.delayed_x, y: data.delayed_y, mode: "markers", name: t("fscatter.delayed"),
          marker: { size: 5, color: ALERT, opacity: 0.6 },
          hovertemplate: "R$%{x:.0f} | Ratio: %{y:.2f}<extra>" + t("fscatter.delayed") + "</extra>" },
    ], {
        ...PLOTLY_BASE, height: pH(380), margin: { l: 50, r: 20, t: 10, b: 40 },
        xaxis: ax({ gridcolor: FAINT, title: { text: t("fscatter.priceR"), font: { color: DIM } } }),
        yaxis: ax({ gridcolor: FAINT, title: { text: t("fscatter.freightRatio"), font: { color: DIM } } }),
        legend: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, font: { color: DIM } },
        shapes: [{ type: "line", x0: 0, x1: 2900, y0: 0.5, y1: 0.5, line: { color: DIM, width: 1, dash: "dot" } }],
    }, PLOTLY_CFG);
    addLegendHint("ins-freight-scatter");
}

function renderHeatmap(data) {
    if (!data || !data.z) return;
    
    const rColorscale = [
        [0, "rgba(0,0,0,0)"],
        [0.2, "#2a0000"],
        [0.5, "#800000"],
        [0.8, "#cc0000"],
        [1.0, ALERT]
    ];
    
    // Reverse array structure for Plotly heatmap orientation matching standard reading
    const zRev = [...data.z].reverse();
    const yRev = [...data.y].reverse();
    
    Plotly.newPlot("ins-heatmap-chart", [{
        z: zRev,
        x: data.x,
        y: yRev,
        type: "heatmap",
        colorscale: rColorscale,
        text: zRev.map(row => row.map(val => val !== null ? val.toFixed(1) + "%" : "-")),
        texttemplate: "%{text}",
        hoverinfo: "x+y+text"
    }], {
        ...PLOTLY_BASE, height: pH(380), margin: { l: 80, r: 20, t: 10, b: 60 },
        xaxis: ax({ gridcolor: "rgba(0,0,0,0)", title: { text: t("heatmap.dest"), font: { color: DIM } } }),
        yaxis: ax({ gridcolor: "rgba(0,0,0,0)", title: { text: t("heatmap.origin"), font: { color: DIM } } }),
    }, PLOTLY_CFG);
    addLegendHint("ins-heatmap-chart");
}

/* ═══════════════════════════════════════════════════════════════════════ */
/* TAB 3: PREDICTOR                                                      */
/* ═══════════════════════════════════════════════════════════════════════ */

function initPredictor() {
    document.getElementById("pred-submit").addEventListener("click", runPrediction);
}

async function runPrediction() {
    const btn = document.getElementById("pred-submit");
    const originalText = btn.textContent;
    btn.textContent = "Processing...";
    btn.disabled = true;

    try {
        const originCep  = document.getElementById("pred-origin-cep").value || "01001000";
        const destCep    = document.getElementById("pred-dest-cep").value || "20000000";
        const category   = document.getElementById("pred-category").value || "beleza_saude";
        const weight     = parseFloat(document.getElementById("pred-weight").value) || 1000;
        const price      = parseFloat(document.getElementById("pred-price").value) || 50.0;
        const volume     = parseFloat(document.getElementById("pred-volume").value) || 2000;
        const freight    = parseFloat(document.getElementById("pred-freight").value) || 15.0;
        const items      = parseInt(document.getElementById("pred-items").value) || 1;
        const estDays    = parseFloat(document.getElementById("pred-estimated-days").value) || 10;
        const sellerDays = parseFloat(document.getElementById("pred-seller-days").value) || 2.0;
        const sellerHist = parseFloat(document.getElementById("pred-seller-history").value) || 0.05;
        const sellerOrd  = parseInt(document.getElementById("pred-seller-orders").value) || 50;

        const payload = {
            cep_cliente: destCep,
            cep_vendedor: originCep,
            categoria_produto: category,
            peso_produto_g: weight,
            preco_produto: price,
            preco_frete: freight,
            volume_cm3: volume,
            total_itens_pedido: items,
            prazo_estimado_dias: estDays,
            velocidade_lojista_dias: sellerDays,
            historico_atraso_vendedor: sellerHist,
            qtd_pedidos_anteriores_vendedor: sellerOrd,
            data_aprovacao: new Date().toISOString()
        };

        const res = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "API Error");
        }

        const data = await res.json();
        
        // Dados Retornados da API V5
        const prob = data.probabilidade_atraso / 100.0;
        const limiar = (data.limiar_corte || 54.0) / 100.0;
        const ratio = freight / (price || 1);
        const interstate = data.features_utilizadas.seller_state !== data.features_utilizadas.customer_state ? 1 : 0;

        let color, label;
        if (prob >= limiar) { 
            color = ALERT; 
            label = t("pred.highRisk"); 
        } else if (prob >= (limiar * 0.5)) { 
            color = MUTED; 
            label = t("pred.moderate"); 
        } else { 
            color = LIME;  
            label = t("pred.lowRisk"); 
        }

        const resultDiv = document.getElementById("pred-result");

        resultDiv.innerHTML = `
            <div class="risk-result">
                <div class="glass-card chart-card">
                    <div id="pred-gauge"></div>
                </div>
                <div class="glass-card chart-card">
                    <div class="chart-label">${t("pred.featureProfile")}</div>
                    <div id="pred-radar"></div>
                </div>
            </div>
        `;

        requestAnimationFrame(() => {
            const gaugeCard = document.getElementById("pred-gauge").parentElement;
            const radarCard = document.getElementById("pred-radar").parentElement;

            const pad = 48;
            const gaugeH = Math.max(140, Math.round(gaugeCard.getBoundingClientRect().height - pad));
            const radarLabelH = radarCard.querySelector(".chart-label")?.offsetHeight || 0;
            const radarH = Math.max(140, Math.round(radarCard.getBoundingClientRect().height - pad - radarLabelH));

            // Gauge (Usando o Limiar do CatBoost)
            Plotly.newPlot("pred-gauge", [{
                type: "indicator", mode: "gauge+number", value: data.probabilidade_atraso,
                number: { suffix: "%", font: { family: "Space Grotesk", size: pH(56), color: color } },
                title: { text: label, font: { family: "IBM Plex Mono", size: pH(12), color: color } },
                gauge: {
                    axis: { range: [0, 100], tickfont: { color: DIM, size: pH(10) }, tickcolor: FAINT, dtick: 20 },
                    bar: { color: color, thickness: 0.75 },
                    bgcolor: "#111111", borderwidth: 0,
                    steps: [
                        { range: [0, data.limiar_corte], color: "#0d0d0d" },
                        { range: [data.limiar_corte, 100], color: "#1a1118" },
                    ],
                    threshold: { line: { color: WHITE, width: 2 }, thickness: 0.85, value: data.probabilidade_atraso },
                },
            }], { ...PLOTLY_BASE, height: gaugeH, margin: { l: 30, r: 30, t: 50, b: 10 } }, PLOTLY_CFG);

            // Radar com base nos dados do Form
            const cats = [t("radar.weight"), t("radar.price"), t("radar.freight"), t("radar.volume"), t("radar.fRatio"), t("radar.sellerSpd"), t("radar.interstate")];
            const maxV = [30000, 2000, 200, 100000, 2, 15, 1];
            const raw  = [weight, price, freight, volume, ratio, sellerDays, interstate];
            const norm = raw.map((v, i) => Math.min(v / maxV[i], 1.0));
            norm.push(norm[0]);
            const catsC = [...cats, cats[0]];

            Plotly.newPlot("pred-radar", [{
                type: "scatterpolar", r: norm, theta: catsC, fill: "toself",
                fillcolor: "rgba(0, 0, 255, 0.08)",
                line: { color: LIME, width: 2 },
                marker: { size: 5, color: CYAN },
                hovertemplate: "%{theta}: %{r:.2f}<extra></extra>",
            }], {
                ...PLOTLY_BASE, height: radarH, margin: { l: 60, r: 60, t: 20, b: 20 },
                polar: {
                    bgcolor: "rgba(0,0,0,0)",
                    angularaxis: { gridcolor: FAINT, linecolor: FAINT },
                    radialaxis: { gridcolor: FAINT, linecolor: FAINT, range: [0, 1], showticklabels: false },
                },
                showlegend: false,
            }, PLOTLY_CFG);

            if (window.reinjectChartHelp) window.reinjectChartHelp();

            // Recommendations 
            const recs = [];
            if (interstate)     recs.push(t("pred.recInterstate"));
            if (sellerDays > 5) recs.push(t("pred.recSeller", { days: sellerDays }));
            if (ratio > 0.5)    recs.push(t("pred.recFreight"));

            const recsDiv = document.getElementById("pred-recommendations");
            if (recs.length === 0) {
                recsDiv.style.display = "none";
            } else {
                recsDiv.style.display = "";
                recsDiv.innerHTML = `
                    <div class="glass-card" style="padding:24px">
                        <div class="chart-label">${t("pred.recActions")}</div>
                        <div style="margin-top:12px">
                            ${recs.map((r, i) => `<div class="rec-card${i === 0 ? ' primary' : ''}"><p>${r}</p></div>`).join("")}
                        </div>
                    </div>
                `;
            }
        });
    } catch (err) {
        console.error(err);
        alert("Ops! Falha na predição: " + err.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

/* ── Utilities ───────────────────────────────────────────────────────── */

function gauss(mean, std) {
    const u = 1 - Math.random(), v = Math.random();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v) * std + mean;
}

/** Add a "click legend to filter" hint below a Plotly chart */
function addLegendHint(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const parent = el.closest(".chart-card") || el.parentElement;
    if (parent && !parent.querySelector(".legend-filter-hint")) {
        const hint = document.createElement("div");
        hint.className = "legend-filter-hint";
        hint.textContent = CURRENT_LANG === "pt" ? "Clique na legenda para filtrar" : "Click legend to filter";
        parent.appendChild(hint);
    }
}

/* ── FUI Real-Time Clock ──────────────────────────────────────────────── */
setInterval(() => {
    const el = document.getElementById("fui-clock");
    if (el) el.textContent = new Date().toISOString().slice(11, 19) + " UTC";
}, 1000);

/* ── Custom Dropdown (CDD) ────────────────────────────────────────────── */
/* Wraps every <select> into a styled dropdown panel while keeping the
   native element in sync so `.value` and `change` events still work.   */

function initCustomDropdowns() {
    document.querySelectorAll("select:not(.cdd-hidden)").forEach(sel => {
        /* 1. Build wrapper */
        const wrap = document.createElement("div");
        wrap.className = "cdd";

        /* 2. Trigger button */
        const trigger = document.createElement("button");
        trigger.type = "button";
        trigger.className = "cdd-trigger";
        trigger.setAttribute("aria-haspopup", "listbox");
        trigger.setAttribute("aria-expanded", "false");
        trigger.innerHTML = `
            <span class="cdd-label"></span>
            <svg class="cdd-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none">
                <path d="M0 0l5 6 5-6z" fill="currentColor"/>
            </svg>`;
        const label = trigger.querySelector(".cdd-label");

        /* 3. Option panel */
        const panel = document.createElement("div");
        panel.className = "cdd-panel";
        panel.setAttribute("role", "listbox");

        function buildOptions() {
            panel.innerHTML = "";
            Array.from(sel.options).forEach((opt, i) => {
                const item = document.createElement("div");
                item.className = "cdd-option" + (i === sel.selectedIndex ? " active" : "");
                item.setAttribute("role", "option");
                item.dataset.value = opt.value;
                item.textContent = opt.textContent;
                panel.appendChild(item);
            });
            label.textContent = sel.options[sel.selectedIndex]?.textContent || "";
        }
        buildOptions();

        /* 4. Insert into DOM */
        sel.parentNode.insertBefore(wrap, sel);
        wrap.appendChild(trigger);
        wrap.appendChild(panel);
        sel.classList.add("cdd-hidden");
        wrap.appendChild(sel);

        /* 5. Toggle */
        trigger.addEventListener("click", (e) => {
            e.stopPropagation();
            const wasOpen = wrap.classList.contains("open");
            closeAllDropdowns();
            if (!wasOpen) {
                wrap.classList.add("open");
                trigger.setAttribute("aria-expanded", "true");
                /* Scroll active option into view */
                const active = panel.querySelector(".active");
                if (active) active.scrollIntoView({ block: "nearest" });
            }
        });

        /* 6. Select option */
        panel.addEventListener("click", (e) => {
            const item = e.target.closest(".cdd-option");
            if (!item) return;
            sel.value = item.dataset.value;
            sel.dispatchEvent(new Event("change", { bubbles: true }));
            panel.querySelectorAll(".cdd-option").forEach(o => o.classList.remove("active"));
            item.classList.add("active");
            label.textContent = item.textContent;
            wrap.classList.remove("open");
            trigger.setAttribute("aria-expanded", "false");
        });

        /* 7. Keyboard navigation */
        trigger.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                trigger.click();
            } else if (e.key === "Escape") {
                wrap.classList.remove("open");
                trigger.setAttribute("aria-expanded", "false");
            }
        });

        /* 8. Keep in sync if native select changes programmatically */
        const observer = new MutationObserver(buildOptions);
        observer.observe(sel, { childList: true, subtree: true, attributes: true });
    });
}

function closeAllDropdowns() {
    document.querySelectorAll(".cdd.open").forEach(d => {
        d.classList.remove("open");
        const btn = d.querySelector(".cdd-trigger");
        if (btn) btn.setAttribute("aria-expanded", "false");
    });
}

/* Close on outside click */
document.addEventListener("click", closeAllDropdowns);

/* Init after DOM */
document.addEventListener("DOMContentLoaded", initCustomDropdowns);

console.log("◉ Olist Logistics Intelligence — Keita Yamada aesthetic loaded");
