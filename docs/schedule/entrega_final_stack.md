# O Nosso Produto Final: O que o Grupo Vai Entregar?

Nossa entrega não será apenas um conjunto de planilhas e scripts soltos, mas sim um **Produto de Dados Unificado**, hospedado em uma única interface web. 

O objetivo é que, ao abrirmos o link durante a apresentação, os Professores da Turma enxerguem o ciclo completo: de onde viemos (histórico/insights) para onde vamos (predição ao vivo).

---

## 🖥️ A Interface Unificada (As Abas do App)

O produto final será uma Aplicação Web (Dashboard) dividida em 3 Telas Livres / Abas principais de navegação:

### Aba 1: Painel Gerencial Interativo (O Passado)
*   **O que terá na tela:** Gráficos interativos (filtros por data, categoria de produto e estado) demonstrando a saúde geral da Olist com base no dataset histórico original.
*   **A grande estrela:** Um Mapa do Brasil de calor, mostrando CEPs de vendedores ou clientes em vermelho (rotas críticas de atraso). Tudo clicável e dinâmico.

### Aba 2: Insights Valiosos (A Inteligência de Negócio)
*   **O que terá na tela:** O lado "humano" do projeto corporativo. Em formato de *Key Results* e indicadores arrojados, a tela mostrará as maiores descobertas em texto e pequenos gráficos de apoio.
*   **A grande estrela:** Respostas diretas como: *"Descobrimos que a correlação de X com Y causa 45% dos atrasos da região Norte gerando Z mil reais em perdas monetárias. O problema da Olist nunca foi o tamanho do produto, mas sim a transportadora."*

### Aba 3: O Motor de Predição e API (O Futuro)
*   **O que terá na tela:** Um formulário de Sistema Real (Ex: "Simulador de Nova Venda"). 
*   **A grande estrela (O Clímax da Apresentação):** 
    1. Você digita o CEP de Origem e de Destino e seleciona um Produto Fictício.
    2. Ao apertar o botão "Prever Risco e Transportadora" na Interface...
    3. ...A interface dispara as informações para o Backend de Machine Learning (construído nas frentes 3 e 4). 
    4. A Tela "pensa" por 2 segundos e retorna o Veredito do *XGBoost*: **"Com base nessas variáveis, a chance deste pedido atrasar é de 89%. Para não queimar a margem de Growth e manter a retenção, acione o Lojista para enviar 2 dias mais cedo do que o normal."**

---

## 🛠️ A Melhor Stack Tecnológica (Para 4 Dias Corridos)

Dado o nosso prazo hiper-curto e a necessidade de unir **Painel de Dados + Textos + Inteligências Artificiais em Python**, a stack vencedora incontestável é **Python + Streamlit**.

Vantagens da Stack escolhida:
1.  Esqueça desenvolvimento web demorado (HTML, CSS ou React). Você programa os botões e os gráficos das 3 telas **usando puramente código Python** em um único arquivo.
2.  Como o Machine Learning (Pandas, Scikit-learn, XGBoost) é feito nativamente em Python, o Streamlit "roda por cima" da Inteligência Artificial sem precisar construir pontes complexas (APIs REST cheias de rotas) entre Frontend e Backend num curto espaço de tempo.

### Nossa Stack Definitiva:
*   **Tratamento e ML:** Jupyter Notebook ou Google Colab (Módulos: `pandas`, `scikit-learn` ou `xgboost`).
*   **Visualização Gráfica:** `plotly` (Gera gráficos lindos, responsivos e interativos perfeitamente compatíveis com a web).
*   **Aplicação Final (App.py):** `Streamlit` (A "cola" mágica que junta tudo numa interface de navegador).
*   **Deploy Cloud (Onde o Link vai ficar):** `Streamlit Community Cloud` ou `Render`. (O deploy do Streamlit é tão simples quanto dar permissão na sua conta do Github, ele compila e gera a URL em minutos totalmente de graça).
