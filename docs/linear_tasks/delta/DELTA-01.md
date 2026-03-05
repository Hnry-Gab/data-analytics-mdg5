# [DELTA-01] Setup do Frontend/FastAPI e Esqueleto de 3 Abas

**Responsável:** Pablo
**Dia:** 1 (Quinta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/delta-01-Frontend/FastAPI-setup`

---

## Descrição

Criar o projeto Full-Stack do zero, configurar o servidor local e montar o esqueleto visual completo das 3 abas que compõem o produto final.

### Passo a Passo

1. Criar o arquivo `src/app.py` como ponto de entrada.
2. Configurar `st.set_page_config(page_title="Olist Logistics Growth", layout="wide")`.
3. Criar sidebar com navegação entre as 3 abas usando `st.tabs()` ou `st.sidebar.radio()`.
4. Criar os arquivos de cada aba:
   - `src/pages/painel_gerencial.py` → Aba 1 (Dashboard Histórico)
   - `src/pages/insights.py` → Aba 2 (Insights de Negócio)
   - `src/pages/simulador.py` → Aba 3 (Motor de Predição)
5. Cada aba deve ter um título, um subtítulo explicativo e placeholders (`st.empty()`) para os gráficos futuros.
6. Testar `uvicorn src.main:app --reload` localmente no navegador.

### Referências
- `spec/project_spec.md` → Descrição das 3 abas
- `docs/schedule/entrega_final_stack.md` → Produto final esperado

## Critério de Aceite

- [ ] `uvicorn src.main:app --reload` roda sem erros
- [ ] 3 abas navegáveis no browser
- [ ] Sidebar com filtros placeholder (data, estado)
- [ ] Título e logo da aplicação visíveis

## Dependências
Nenhuma — pode começar em paralelo ao Alpha.

## Entregável
Web App rodando localmente com o esqueleto visual completo
