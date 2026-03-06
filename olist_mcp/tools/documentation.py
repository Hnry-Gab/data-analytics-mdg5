"""MCP-06: Data Dictionary & Documentation Tools (11 tools).

Exposes project documentation: data dictionary, specs, plans,
task details, algorithm explanations, and stack info.
"""

import re
from pathlib import Path

from fastmcp import FastMCP

from olist_mcp.config import DOCS_DIR, ROOT, SPEC_DIR

_TASKS_DIR = DOCS_DIR / "linear_tasks"
_ALGORITHMS_DIR = DOCS_DIR / "algorithms"

# Section mapping for the data dictionary (maps section name → header substring)
_DICT_SECTIONS = {
    "customers": "1. Clientes",
    "orders": "2. Pedidos",
    "items": "3. Itens do Pedido",
    "products": "4. Produtos",
    "reviews": "5. Avaliações",
    "sellers": "6. Vendedores",
    "payments": "7. Pagamentos",
    "geolocation": "8. Geolocalização",
    "translation": "9. Tradução",
}

# Engineered column definitions (not in dicionario_dados.md)
_ENGINEERED_DEFS: dict[str, dict[str, str]] = {
    "dias_diferenca": {
        "tipo": "int64",
        "origem": "Engineered (Task 2)",
        "descricao": "Diferença em dias entre data estimada e data real de entrega. Negativo = atrasou.",
        "formula": "order_estimated_delivery_date - order_delivered_customer_date (em dias)",
    },
    "foi_atraso": {
        "tipo": "int64 (binary)",
        "origem": "Engineered (Task 2)",
        "descricao": "Variável alvo: 1 se pedido atrasou, 0 se chegou no prazo.",
        "formula": "1 if dias_diferenca < 0 else 0",
    },
    "volume_cm3": {
        "tipo": "float64",
        "origem": "Engineered (Task 10)",
        "descricao": "Volume do produto em centímetros cúbicos.",
        "formula": "product_length_cm × product_height_cm × product_width_cm",
    },
    "frete_ratio": {
        "tipo": "float64",
        "origem": "Engineered (Task 10)",
        "descricao": "Razão frete/preço. Indica peso relativo do custo de envio.",
        "formula": "freight_value / price",
    },
    "velocidade_lojista_dias": {
        "tipo": "float64",
        "origem": "Engineered (Task 10)",
        "descricao": "Dias entre compra e despacho à transportadora. Feature mais correlacionada (+0.2143).",
        "formula": "(order_delivered_carrier_date - order_purchase_timestamp).days",
    },
    "dia_semana_compra": {
        "tipo": "int64",
        "origem": "Engineered (Task 7)",
        "descricao": "Dia da semana da compra (0=Segunda, 6=Domingo).",
        "formula": "order_purchase_timestamp.dt.dayofweek",
    },
    "rota_interestadual": {
        "tipo": "int64 (binary)",
        "origem": "Engineered (Task 8)",
        "descricao": "1 se seller_state ≠ customer_state (rota interestadual).",
        "formula": "1 if seller_state != customer_state else 0",
    },
    "customer_lat": {
        "tipo": "float64",
        "origem": "Engineered (Task 9)",
        "descricao": "Latitude do cliente (geocodificada via CEP).",
        "formula": "Mediana de geolocation_lat para o customer_zip_code_prefix",
    },
    "customer_lng": {
        "tipo": "float64",
        "origem": "Engineered (Task 9)",
        "descricao": "Longitude do cliente (geocodificada via CEP).",
        "formula": "Mediana de geolocation_lng para o customer_zip_code_prefix",
    },
    "seller_lat": {
        "tipo": "float64",
        "origem": "Engineered (Task 9)",
        "descricao": "Latitude do vendedor (geocodificada via CEP).",
        "formula": "Mediana de geolocation_lat para o seller_zip_code_prefix",
    },
    "seller_lng": {
        "tipo": "float64",
        "origem": "Engineered (Task 9)",
        "descricao": "Longitude do vendedor (geocodificada via CEP).",
        "formula": "Mediana de geolocation_lng para o seller_zip_code_prefix",
    },
    "distancia_haversine_km": {
        "tipo": "float64",
        "origem": "Engineered (Task 9)",
        "descricao": "Distância great-circle entre vendedor e cliente em km.",
        "formula": "haversine(seller_lat, seller_lng, customer_lat, customer_lng)",
    },
}

# Algorithm explanations (plain language, no jargon)
_ALGORITHM_EXPLANATIONS: dict[str, str] = {
    "pearson": (
        "## Correlação de Pearson\n\n"
        "Mede a força da relação **linear** entre duas variáveis numéricas.\n\n"
        "- **Escala:** -1 a +1\n"
        "  - +1 = relação positiva perfeita (quando uma sobe, a outra sobe igual)\n"
        "  - 0 = sem relação linear\n"
        "  - -1 = relação negativa perfeita (quando uma sobe, a outra desce)\n\n"
        "**Neste projeto:** Aplicado a features logísticas para medir correlação com `foi_atraso`. "
        "A feature mais forte foi `velocidade_lojista_dias` com Pearson = +0.2143.\n\n"
        "**Limitações:** Só captura relações lineares. Correlação ≠ causalidade."
    ),
    "cramers_v": (
        "## Cramér's V\n\n"
        "Mede a **associação** entre duas variáveis categóricas (não numéricas).\n\n"
        "- **Escala:** 0 a 1\n"
        "  - 0 = independência total\n"
        "  - 1 = associação perfeita\n\n"
        "**Neste projeto:** Usado para medir a relação entre variáveis como `customer_state` e "
        "`foi_atraso`. O estado do cliente mostrou Cramér's V = 0.1336 (associação moderada).\n\n"
        "**Base:** Derivado do teste qui-quadrado (χ²), normalizado pelo tamanho da amostra."
    ),
    "xgboost": (
        "## XGBoost (eXtreme Gradient Boosting)\n\n"
        "Algoritmo de **ensemble** que constrói árvores de decisão sequencialmente, "
        "onde cada nova árvore corrige os erros da anterior.\n\n"
        "**Como funciona:**\n"
        "1. Treina uma árvore simples\n"
        "2. Calcula os erros (resíduos)\n"
        "3. Treina a próxima árvore focando nos erros\n"
        "4. Repete N vezes (200 neste projeto)\n\n"
        "**Neste projeto:**\n"
        "- Classificação binária: atraso sim/não\n"
        "- `scale_pos_weight=14.17` compensa o desbalanceamento de classes\n"
        "- ROC-AUC baseline: 0.7452\n\n"
        "**Vantagem:** Lida bem com dados desbalanceados e extrai padrões não-lineares "
        "mesmo de features individualmente fracas."
    ),
    "haversine": (
        "## Fórmula de Haversine\n\n"
        "Calcula a distância **great-circle** entre dois pontos na superfície terrestre "
        "dados suas coordenadas (latitude e longitude).\n\n"
        "**Fórmula simplificada:**\n"
        "```\n"
        "a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlng/2)\n"
        "d = 2R × arcsin(√a)    onde R = 6371 km\n"
        "```\n\n"
        "**Neste projeto:** Calcula a distância seller → customer em km. "
        "É a 3ª feature mais correlacionada (Pearson = +0.0753).\n\n"
        "**Exemplo:** São Paulo → Rio de Janeiro ≈ 361 km."
    ),
    "target_encoding": (
        "## Target Encoding\n\n"
        "Técnica para converter variáveis categóricas em numéricas usando a **taxa do target** "
        "por categoria.\n\n"
        "**Como funciona:**\n"
        "1. Para cada valor da categoria (ex: cada estado UF)\n"
        "2. Calcula a taxa média do target (% de atrasos naquele estado)\n"
        "3. Substitui o nome do estado pelo número\n\n"
        "**Exemplo:** AL tem 20.84% de atrasos → AL = 0.2084\n\n"
        "**Neste projeto:** Aplicado a `customer_state` e `seller_state` para criar "
        "`customer_state_encoded` e `seller_state_encoded` no dataset de treino.\n\n"
        "**Cuidado:** Risco de data leakage se não feito corretamente (usar apenas dados de treino)."
    ),
    "smote": (
        "## SMOTE (Synthetic Minority Over-sampling Technique)\n\n"
        "Técnica para balancear classes criando **exemplos sintéticos** da classe minoritária.\n\n"
        "**Como funciona:**\n"
        "1. Seleciona um exemplo da classe minoritária\n"
        "2. Encontra seus K vizinhos mais próximos (mesma classe)\n"
        "3. Cria novo ponto entre o original e um vizinho aleatório\n"
        "4. Repete até equalizar as classes\n\n"
        "**Neste projeto:** Não utilizado. Optou-se por `scale_pos_weight` no XGBoost, "
        "que é mais simples e mostrou resultados equivalentes para este caso."
    ),
    "roc_auc": (
        "## ROC-AUC (Area Under the Receiver Operating Characteristic Curve)\n\n"
        "Métrica que avalia a capacidade do modelo de **distinguir** entre classes.\n\n"
        "- **Escala:** 0 a 1\n"
        "  - 0.5 = chute aleatório (inútil)\n"
        "  - 0.7-0.8 = discriminação aceitável\n"
        "  - 0.8-0.9 = boa discriminação\n"
        "  - >0.9 = excelente\n\n"
        "**Por que usamos ROC-AUC e não accuracy?**\n"
        "Com 93.4% da classe 0, um modelo que sempre diz \"não atrasou\" teria 93.4% de accuracy "
        "mas seria inútil. ROC-AUC ignora esse viés.\n\n"
        "**Neste projeto:** XGBoost baseline ROC-AUC = 0.7452 (acima do target mínimo de 0.70)."
    ),
}


def _read_file(path: Path) -> str:
    """Read a file and return its content, or an error message if missing."""
    if not path.exists():
        return f"**Error:** File not found: `{path.relative_to(ROOT)}`"
    return path.read_text(encoding="utf-8")


def _parse_dict_section(content: str, header_substr: str) -> str:
    """Extract a section from the data dictionary by its header substring."""
    lines = content.split("\n")
    capturing = False
    section_lines: list[str] = []

    for line in lines:
        if line.startswith("## ") and header_substr in line:
            capturing = True
            section_lines.append(line)
            continue
        if capturing:
            if line.startswith("## "):  # next section
                break
            section_lines.append(line)

    return "\n".join(section_lines).strip() if section_lines else f"Section not found: {header_substr}"


def _parse_task_title(content: str) -> str:
    """Extract the title from a task file's first line (# [TASK-ID] Title)."""
    first_line = content.split("\n", 1)[0]
    match = re.match(r"^#\s*\[[\w-]+\]\s*(.+)", first_line)
    return match.group(1).strip() if match else first_line.lstrip("# ").strip()


def register(mcp: FastMCP) -> None:
    """Register all 11 documentation tools on the MCP server."""

    @mcp.tool()
    def get_column_definition(column_name: str) -> str:
        """Get the detailed definition of a single dataset column: type, origin, description, formula, and caveats."""
        # Check engineered columns first
        if column_name in _ENGINEERED_DEFS:
            info = _ENGINEERED_DEFS[column_name]
            return (
                f"## Coluna: `{column_name}`\n\n"
                f"- **Tipo:** {info['tipo']}\n"
                f"- **Origem:** {info['origem']}\n"
                f"- **Descrição:** {info['descricao']}\n"
                f"- **Fórmula:** `{info['formula']}`\n"
            )

        # Search in dicionario_dados.md
        dict_path = DOCS_DIR / "data" / "dicionario_dados.md"
        content = _read_file(dict_path)
        if content.startswith("**Error:**"):
            return content

        # Search for the column name in the dictionary
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if f"**`{column_name}`**" in line:
                # Find the section header (walk backwards)
                section = "Unknown"
                for j in range(i, -1, -1):
                    if lines[j].startswith("## "):
                        section = lines[j].lstrip("# ").strip()
                        break
                # Extract description after "**`col`**: "
                desc = line.split(":**", 1)[-1].strip() if ":**" in line else line
                desc = desc.lstrip("* ")
                return (
                    f"## Coluna: `{column_name}`\n\n"
                    f"- **Origem:** {section}\n"
                    f"- **Descrição:** {desc}\n"
                )

        return (
            f"**Error:** Column `{column_name}` not found in data dictionary.\n\n"
            f"Available engineered columns: {', '.join(sorted(_ENGINEERED_DEFS.keys()))}"
        )

    @mcp.tool()
    def get_data_dictionary(section: str = "all") -> str:
        """Get the dataset data dictionary. Sections: customers, orders, items, products, reviews, sellers, payments, geolocation, translation, engineered, all."""
        dict_path = DOCS_DIR / "data" / "dicionario_dados.md"
        content = _read_file(dict_path)
        if content.startswith("**Error:**"):
            return content

        if section == "all" or section is None:
            # Append engineered columns
            eng_section = "\n---\n\n## 10. Variáveis Engineered (Feature Engineering Pipeline)\n\n"
            for col, info in _ENGINEERED_DEFS.items():
                eng_section += f"*   **`{col}`** ({info['tipo']}): {info['descricao']}\n"
            return content + eng_section

        if section == "engineered":
            lines = ["## Variáveis Engineered (Feature Engineering Pipeline)\n"]
            for col, info in _ENGINEERED_DEFS.items():
                lines.append(
                    f"*   **`{col}`** ({info['tipo']}): {info['descricao']}  \n"
                    f"    Fórmula: `{info['formula']}`"
                )
            return "\n".join(lines)

        if section not in _DICT_SECTIONS:
            valid = ", ".join(sorted(list(_DICT_SECTIONS.keys()) + ["engineered", "all"]))
            return f"**Error:** Invalid section `{section}`. Valid options: {valid}"

        return _parse_dict_section(content, _DICT_SECTIONS[section])

    @mcp.tool()
    def get_project_spec() -> str:
        """Get the full project specification: scope, squads, deliverables, timeline, and out-of-scope items."""
        return _read_file(SPEC_DIR / "project_spec.md")

    @mcp.tool()
    def get_model_spec() -> str:
        """Get the ML model specification: XGBoost hyperparameters, metrics targets, split strategy, contingency plan, and export format."""
        return _read_file(SPEC_DIR / "model_spec.md")

    @mcp.tool()
    def get_feature_engineering_plan() -> str:
        """Get the feature engineering plan: Tasks 5-11, formulas, owners, and deliverables for each new feature created."""
        return _read_file(DOCS_DIR / "data" / "plano_feature_engineering_eda.md")

    @mcp.tool()
    def get_viability_report() -> str:
        """Get the model viability report: feature ranking, strengths, risks, projected metrics, and final verdict on whether ML training is worthwhile."""
        return _read_file(DOCS_DIR / "data" / "relatorio_viabilidade_modelo.md")

    @mcp.tool()
    def get_eda_report() -> str:
        """Get the consolidated EDA report: notebook summaries, data criteria, feature ranking, multicollinearity check, and key business findings."""
        path = ROOT / "notebooks" / "final_analysis" / "relatorio_final_eda.md"
        return _read_file(path)

    @mcp.tool()
    def get_task_details(task_id: str) -> str:
        """Get the full specification of a Linear task by ID (e.g., 'ALPHA-01', 'DELTA-03', 'OMEGA-02'). Returns title, description, acceptance criteria, dependencies, and deliverables."""
        task_id = task_id.upper().strip()

        # Parse squad from task_id
        match = re.match(r"^(ALPHA|DELTA|OMEGA)-\d+$", task_id)
        if not match:
            return (
                f"**Error:** Invalid task ID format: `{task_id}`.\n\n"
                "Expected format: `SQUAD-NN` where SQUAD is ALPHA, DELTA, or OMEGA.\n"
                "Examples: ALPHA-01, DELTA-03, OMEGA-02"
            )

        squad = match.group(1).lower()
        task_file = _TASKS_DIR / squad / f"{task_id}.md"
        return _read_file(task_file)

    @mcp.tool()
    def list_all_tasks(squad: str = "all") -> str:
        """List all Linear tasks, optionally filtered by squad (alpha, delta, omega, or all). Returns task IDs, titles, and squad assignments."""
        squads = ["alpha", "delta", "omega"]

        if squad != "all" and squad is not None:
            squad = squad.lower().strip()
            if squad not in squads:
                return f"**Error:** Invalid squad `{squad}`. Valid options: alpha, delta, omega, all"
            squads = [squad]

        lines = ["## Linear Tasks\n", "| Task ID | Squad | Title |", "|---------|-------|-------|"]

        for s in squads:
            squad_dir = _TASKS_DIR / s
            if not squad_dir.exists():
                continue
            for task_file in sorted(squad_dir.glob(f"{s.upper()}-*.md")):
                task_id = task_file.stem
                content = task_file.read_text(encoding="utf-8")
                title = _parse_task_title(content)
                lines.append(f"| {task_id} | {s.capitalize()} | {title} |")

        return "\n".join(lines)

    @mcp.tool()
    def get_algorithm_explanation(algorithm: str) -> str:
        """Get a plain-language explanation of an algorithm used in this project. Options: pearson, cramers_v, xgboost, haversine, target_encoding, smote, roc_auc."""
        algorithm = algorithm.lower().strip()

        if algorithm in _ALGORITHM_EXPLANATIONS:
            return _ALGORITHM_EXPLANATIONS[algorithm]

        # Try reading from docs/algorithms/
        for alg_file in _ALGORITHMS_DIR.glob("*.md"):
            if algorithm in alg_file.stem.lower():
                return _read_file(alg_file)

        valid = ", ".join(sorted(_ALGORITHM_EXPLANATIONS.keys()))
        return f"**Error:** Algorithm `{algorithm}` not found.\n\nAvailable: {valid}"

    @mcp.tool()
    def get_stack_info() -> str:
        """Get the official tech stack: languages, libraries with versions, and explicit list of technologies NOT used with rationale."""
        stack_content = _read_file(SPEC_DIR / "stack.md")

        # Also append requirements.txt content
        req_path = ROOT / "requirements.txt"
        if req_path.exists():
            reqs = req_path.read_text(encoding="utf-8").strip()
            stack_content += (
                "\n\n---\n\n## requirements.txt (Dependências instaladas)\n\n"
                f"```\n{reqs}\n```\n"
            )

        return stack_content
