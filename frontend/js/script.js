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
        "ins.catText":        'The top offender — <strong>{cat}</strong> — reaches {pct}% delay rate across {total} orders. Categories sized by volume, colored by delay severity. Heavier and bulkier products dominate the high-risk zone.',
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
        "footer.text":        "Olist Logistics Intelligence — Academic project · FIAP 2025",
        // Chat
        "chat.title":         "OLIST AI",
        "chat.status":        "// online",
        "chat.sysConnect":    "Connection established. OLIST AI v1.0 ready.",
        "chat.welcome":       "Welcome to Olist Logistics Intelligence. I can help you analyze delivery patterns, predict delays, and optimize freight routes. What would you like to explore?",
        "chat.mockQ1":        "Which states have the highest delay rates?",
        "chat.mockA1":        'Based on the current dataset, the top 3 states by delay rate are:<br><strong>RR</strong> — 14.0%<br><strong>AC</strong> — 13.5%<br><strong>AP</strong> — 12.8%<br><br>Northern region states consistently show higher delay rates due to longer distances and limited logistics infrastructure.',
        "chat.mockQ2":        "What about interstate vs intrastate deliveries?",
        "chat.mockA2":        'Interstate deliveries show a significantly higher delay rate of <strong>9.4%</strong> compared to <strong>5.1%</strong> for intrastate. The freight-to-price ratio is the strongest predictive feature for interstate delays.',
        "chat.placeholder":   "Type a message...",
        "chat.mock.r1":       "The average delivery time in São Paulo is 8.2 days, while northern states average 15.4 days.",
        "chat.mock.r2":       "Based on current data, interstate orders have an 84% higher delay probability than intrastate ones.",
        "chat.mock.r3":       "The freight-to-price ratio above 0.5 is the strongest single predictor of delivery delays.",
        "chat.mock.r4":       "Seller processing speed (days to ship) has a Pearson correlation of 0.42 with final delay status.",
        "chat.mock.r5":       "Recommended action: consolidate northern routes through regional distribution hubs to reduce delay rates by ~18%.",
        "chat.mock.r6":       "The category 'bed_bath_table' accounts for 12.1% of all delayed shipments — the highest in the dataset.",
        "chat.mock.r7":       "Weekend purchases (Saturday/Sunday) show a 23% higher delay rate compared to weekday orders.",
        "chartHelp.title":    "CHART PREVIEW",
        "chartHelp.ask":      "Ask about this chart",
    },
    pt: {
        "title":              "Olist — Inteligência Logística",
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
        "ins.interText":      'Pedidos que cruzam fronteiras estaduais apresentam uma taxa de atraso de <strong>{interRate}%</strong> comparada a {intraRate}% para interestaduais. A distância e complexidade da logística multiestadual impulsionam essa diferença.',
        "ins.catText":        'O maior infrator — <strong>{cat}</strong> — atinge {pct}% de atraso em {total} pedidos. Categorias dimensionadas por volume, coloridas por severidade de atraso. Produtos mais pesados e volumosos dominam a zona de alto risco.',
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
        "footer.text":        "Olist Inteligência Logística — Projeto acadêmico · FIAP 2025",
        // Chat
        "chat.title":         "OLIST IA",
        "chat.status":        "// online",
        "chat.sysConnect":    "Conexão estabelecida. OLIST IA v1.0 pronta.",
        "chat.welcome":       "Bem-vindo à Olist Inteligência Logística. Posso ajudar a analisar padrões de entrega, prever atrasos e otimizar rotas de frete. O que deseja explorar?",
        "chat.mockQ1":        "Quais estados têm as maiores taxas de atraso?",
        "chat.mockA1":        'Com base no dataset atual, os 3 estados com maior taxa de atraso são:<br><strong>RR</strong> — 14,0%<br><strong>AC</strong> — 13,5%<br><strong>AP</strong> — 12,8%<br><br>Estados da região Norte apresentam consistentemente maiores taxas de atraso devido a maiores distâncias e infraestrutura logística limitada.',
        "chat.mockQ2":        "E as entregas interestaduais vs intraestaduais?",
        "chat.mockA2":        'Entregas interestaduais apresentam uma taxa de atraso significativamente maior de <strong>9,4%</strong> comparada a <strong>5,1%</strong> para intraestaduais. A razão frete/preço é a feature preditiva mais forte para atrasos interestaduais.',
        "chat.placeholder":   "Digite uma mensagem...",
        "chat.mock.r1":       "O tempo médio de entrega em São Paulo é 8,2 dias, enquanto estados do Norte levam em média 15,4 dias.",
        "chat.mock.r2":       "Com base nos dados atuais, pedidos interestaduais têm 84% mais probabilidade de atraso que intraestaduais.",
        "chat.mock.r3":       "A razão frete/preço acima de 0,5 é o preditor individual mais forte de atrasos na entrega.",
        "chat.mock.r4":       "A velocidade de processamento do vendedor (dias para envio) tem correlação de Pearson de 0,42 com o status final de atraso.",
        "chat.mock.r5":       "Ação recomendada: consolidar rotas do Norte através de hubs regionais de distribuição para reduzir atrasos em ~18%.",
        "chat.mock.r6":       "A categoria 'cama_mesa_banho' representa 12,1% de todos os envios atrasados — a maior do dataset.",
        "chat.mock.r7":       "Compras no fim de semana (sábado/domingo) apresentam 23% mais atrasos comparadas a pedidos em dias úteis.",
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

function initDashboard() {
    updateKPIs({
        orders: 96461,
        delayed: 6535,
        rate: 6.77,
        avgFreight: 19.99,
        deltaDays: -8.7,
    });

    renderGaugeDelay(6.77);
    renderGaugeFreight(19.99);
    renderMap();
    renderRanking();
    renderTimeline();
    renderScatter();
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

function renderMap() {
    const states = ["SP","RJ","MG","RS","PR","BA","SC","GO","PE","CE","PA","MA","MT","MS","ES","PB","RN","AL","PI","SE","RO","TO","AM","AC","AP","RR","DF"];
    const rates  = [5.2,7.8,6.1,4.9,5.0,9.3,4.2,7.1,8.5,8.9,10.2,11.4,8.0,7.2,6.5,9.0,8.7,9.8,10.5,8.2,11.0,9.5,12.1,13.5,12.8,14.0,5.8];

    Plotly.newPlot("dash-map", [{
        type: "choropleth",
        geojson: "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
        locations: states, featureidkey: "properties.sigla", z: rates,
        colorscale: [[0, "#0a0a0a"], [0.35, "#0a0a2e"], [0.65, "#00003a"], [1, ALERT]],
        colorbar: {
            bgcolor: "rgba(0,0,0,0)", borderwidth: 0,
            tickfont: { color: DIM }, title: { text: t("map.delayPct"), font: { color: DIM } },
        },
        hovertemplate: "%{location}: %{z:.1f}%<extra></extra>",
    }], {
        ...PLOTLY_BASE, height: pH(520), margin: { l: 0, r: 0, t: 0, b: 0 },
        geo: { scope: "south america", fitbounds: "locations", visible: false, bgcolor: "rgba(0,0,0,0)" },
    }, PLOTLY_CFG);
}

/* ── Ranking ──────────────────────────────────────────────────────────── */

function renderRanking() {
    const states = ["RR","AC","AP","AM","MA","RO","PA","PI","AL","TO"];
    const rates  = [14.0,13.5,12.8,12.1,11.4,11.0,10.2,10.5,9.8,9.5];
    const traces = [];

    states.forEach((s, i) => {
        traces.push({
            x: [0, rates[i]], y: [s, s], mode: "lines",
            line: { color: i === 0 ? ALERT : FAINT, width: 2 },
            showlegend: false, hoverinfo: "skip",
        });
        traces.push({
            x: [rates[i]], y: [s], mode: "markers",
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

function renderTimeline() {
    const months = [
        "2016-09","2016-10","2016-11","2016-12",
        "2017-01","2017-02","2017-03","2017-04","2017-05","2017-06",
        "2017-07","2017-08","2017-09","2017-10","2017-11","2017-12",
        "2018-01","2018-02","2018-03","2018-04","2018-05","2018-06",
        "2018-07","2018-08","2018-09","2018-10",
    ];
    const rates = [8.2,7.5,6.9,8.1,7.3,6.8,7.0,6.5,6.2,5.8,5.5,5.9,6.3,7.1,7.8,8.5,7.2,6.4,5.9,5.7,5.4,5.1,5.6,6.0,6.8,7.5];

    Plotly.newPlot("dash-timeline", [{
        x: months, y: rates, type: "scatter", mode: "lines",
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
function initInsights() {
    // Defer rendering — charts need visible container for correct sizing
}

function renderInsightsIfNeeded() {
    if (insightsRendered) return;
    insightsRendered = true;
    renderDonut();
    renderTreemap();
    renderViolin();
    renderFreightScatter();
}

function renderDonut() {
    const interRate = 9.4, intraRate = 5.1;
    document.getElementById("ins-inter-rate").textContent = interRate.toFixed(1) + "%";
    document.getElementById("ins-inter-text").innerHTML =
        t("ins.interText", { interRate: interRate.toFixed(1), intraRate: intraRate.toFixed(1) });

    Plotly.newPlot("ins-donut-chart", [{
        labels: [t("donut.onTimeInter"), t("donut.delayedInter"), t("donut.onTimeIntra"), t("donut.delayedIntra")],
        values: [38200, 3960, 51900, 2780],
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

function renderTreemap() {
    const cats = ["bed_bath_table","health_beauty","sports_leisure","furniture_decor","computers","housewares","watches_gifts","garden_tools","auto","cool_stuff","perfumery","toys"];
    const tots = [3200,2800,2400,2100,1900,1800,1600,1400,1200,1100,950,900];
    const pcts = [12.1,10.8,9.5,8.9,8.4,7.8,7.2,6.9,6.5,6.2,5.8,5.1];

    Plotly.newPlot("ins-treemap-chart", [{
        type: "treemap", labels: cats, parents: cats.map(() => ""), values: tots,
        marker: {
            colors: pcts,
            colorscale: [[0, "#0d0d0d"], [0.3, "#0a0a2e"], [0.6, "#00003a"], [1, ALERT]],
            colorbar: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, tickfont: { color: DIM }, title: { text: t("treemap.delayPct"), font: { color: DIM } } },
            cornerradius: 6,
        },
        textfont: { family: "IBM Plex Mono", color: "#ECEBE9" },
        textinfo: "label+percent parent",
        hovertemplate: "%{label}<br>Orders: %{value:,}<br>Delay: %{color:.1f}%<extra></extra>",
    }], { ...PLOTLY_BASE, height: pH(440), margin: { l: 0, r: 0, t: 0, b: 0 } }, PLOTLY_CFG);

    document.getElementById("ins-cat-text").innerHTML =
        t("ins.catText", { cat: cats[0], pct: pcts[0].toFixed(1), total: tots[0].toLocaleString() });
}

function renderViolin() {
    const onT = [], del = [];
    for (let i = 0; i < 500; i++) {
        onT.push(Math.max(0, Math.min(15, gauss(2.5, 1.5))));
        del.push(Math.max(0, Math.min(15, gauss(5.2, 2.8))));
    }

    Plotly.newPlot("ins-violin-chart", [
        { y: onT, name: t("violin.onTime"), type: "violin", box: { visible: true }, meanline: { visible: true },
          fillcolor: FAINT, opacity: 0.8, line: { color: DIM }, marker: { color: DIM } },
        { y: del, name: t("violin.delayed"), type: "violin", box: { visible: true }, meanline: { visible: true },
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

function renderFreightScatter() {
    const n = 600;
    const okX = [], okY = [], dX = [], dY = [];
    for (let i = 0; i < n; i++) {
        const p = Math.random() * 800 + 10;
        const r = Math.random() * 2;
        if (Math.random() > 0.93) { dX.push(p); dY.push(r); }
        else { okX.push(p); okY.push(r); }
    }

    Plotly.newPlot("ins-freight-scatter", [
        { x: okX, y: okY, mode: "markers", name: t("fscatter.onTime"),
          marker: { size: 3, color: FAINT, opacity: 0.4 },
          hovertemplate: "R$%{x:.0f} | Ratio: %{y:.2f}<extra>" + t("fscatter.onTime") + "</extra>" },
        { x: dX, y: dY, mode: "markers", name: t("fscatter.delayed"),
          marker: { size: 5, color: ALERT, opacity: 0.6 },
          hovertemplate: "R$%{x:.0f} | Ratio: %{y:.2f}<extra>" + t("fscatter.delayed") + "</extra>" },
    ], {
        ...PLOTLY_BASE, height: pH(380), margin: { l: 50, r: 20, t: 10, b: 40 },
        xaxis: ax({ gridcolor: FAINT, title: { text: t("fscatter.priceR"), font: { color: DIM } } }),
        yaxis: ax({ gridcolor: FAINT, title: { text: t("fscatter.freightRatio"), font: { color: DIM } } }),
        legend: { bgcolor: "rgba(0,0,0,0)", borderwidth: 0, font: { color: DIM } },
        shapes: [{ type: "line", x0: 0, x1: 810, y0: 0.5, y1: 0.5, line: { color: DIM, width: 1, dash: "dot" } }],
    }, PLOTLY_CFG);
    addLegendHint("ins-freight-scatter");
}

/* ═══════════════════════════════════════════════════════════════════════ */
/* TAB 3: PREDICTOR                                                      */
/* ═══════════════════════════════════════════════════════════════════════ */

function initPredictor() {
    document.getElementById("pred-submit").addEventListener("click", runPrediction);
}

function runPrediction() {
    const origin     = document.getElementById("pred-origin").value;
    const dest       = document.getElementById("pred-dest").value;
    const weight     = parseFloat(document.getElementById("pred-weight").value) || 0;
    const price      = parseFloat(document.getElementById("pred-price").value) || 0;
    const volume     = parseFloat(document.getElementById("pred-volume").value) || 0;
    const freight    = parseFloat(document.getElementById("pred-freight").value) || 0;
    const sellerDays = parseInt(document.getElementById("pred-seller-days").value) || 0;
    const dayIdx     = parseInt(document.getElementById("pred-day").value) || 0;

    const interstate = origin !== dest ? 1 : 0;
    const ratio      = price > 0 ? freight / price : 0;

    const features = {
        product_weight_g: weight,
        price: price,
        freight_value: freight,
        volume_cm3: volume,
        frete_ratio: Math.round(ratio * 10000) / 10000,
        velocidade_lojista_dias: sellerDays,
        dia_semana_compra: dayIdx,
        rota_interestadual: interstate,
    };

    // Mock scoring
    const prob = Math.min((interstate * 0.3) + (sellerDays * 0.05) + (ratio * 0.1), 0.95);

    let color, label;
    if (prob >= 0.5)      { color = ALERT; label = t("pred.highRisk"); }
    else if (prob >= 0.2) { color = MUTED; label = t("pred.moderate"); }
    else                  { color = LIME;  label = t("pred.lowRisk"); }

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

    // Defer Plotly rendering to next frame so CSS grid stretch is applied
    // and we can measure the real available height in each card.
    requestAnimationFrame(() => {
        const gaugeCard = document.getElementById("pred-gauge").parentElement;
        const radarCard = document.getElementById("pred-radar").parentElement;

        const pad = 48; // 24px top + 24px bottom
        const gaugeH = Math.max(140, Math.round(gaugeCard.getBoundingClientRect().height - pad));
        const radarLabelH = radarCard.querySelector(".chart-label")?.offsetHeight || 0;
        const radarH = Math.max(140, Math.round(radarCard.getBoundingClientRect().height - pad - radarLabelH));

        // Gauge
        Plotly.newPlot("pred-gauge", [{
            type: "indicator", mode: "gauge+number", value: prob * 100,
            number: { suffix: "%", font: { family: "Space Grotesk", size: pH(56), color: color } },
            title: { text: label, font: { family: "IBM Plex Mono", size: pH(12), color: color } },
            gauge: {
                axis: { range: [0, 100], tickfont: { color: DIM, size: pH(10) }, tickcolor: FAINT, dtick: 20 },
                bar: { color: color, thickness: 0.75 },
                bgcolor: "#111111", borderwidth: 0,
                steps: [
                    { range: [0, 20], color: "#0d0d0d" },
                    { range: [20, 50], color: "#161616" },
                    { range: [50, 100], color: "#1a1118" },
                ],
                threshold: { line: { color: WHITE, width: 2 }, thickness: 0.85, value: prob * 100 },
            },
        }], { ...PLOTLY_BASE, height: gaugeH, margin: { l: 30, r: 30, t: 50, b: 10 } }, PLOTLY_CFG);

        // Radar
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

        // Inject ? buttons into dynamically created predictor chart cards
        if (window.reinjectChartHelp) window.reinjectChartHelp();

        // Recommendations (full-width below both columns)
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
