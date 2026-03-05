# Correlação de Pearson: Medindo a Força das Relações

## O que é a Correlação de Pearson?
A **Correlação de Pearson** (ou Coeficiente de Correlação de Pearson) é uma métrica estatística usada para medir a força e a direção da relação linear entre duas variáveis **quantitativas** (numéricas).

Em termos simples: ela responde se "quando o valor de uma variável sobe, o valor da outra também sobe (ou desce) numa proporção constante?".

O resultado do cálculo de Pearson é sempre um número (chamado de *r*) que varia de **-1 a 1**.

## Como interpretar o valor de *r*?

### 1. A Direção (Sinal Positivo ou Negativo)
*   **Positiva (+):** Quando uma variável aumenta, a outra também aumenta. (Ex: Quanto maior a distância da entrega, maior o custo do frete).
*   **Negativa (-):** Quando uma variável aumenta, a outra diminui. (Ex: Quanto mais dias de atraso na entrega, menor será o Review Score dado pelo cliente).

### 2. A Força (O número em si)
*   **+1 ou -1:** Correlação perfeita. Os pontos formam uma linha reta exata no gráfico.
*   **Entre ±0.7 e ±0.99:** Correlação Forte. Existe uma relação muito clara.
*   **Entre ±0.4 e ±0.69:** Correlação Moderada. Existe uma tendência, mas com muitos ruídos/exceções.
*   **Entre ±0.1 e ±0.39:** Correlação Fraca. A relação é quase imperceptível.
*   **0:** Correlação Nenhuma. Uma variável não tem relação linear nenhuma com a outra.

## Aplicação na Nossa EDA (Análise Exploratória)

Na nossa fase de Análise Exploratória Nichada para a Olist, o Coeficiente de Pearson será uma das nossas principais armas para descobrir **quais colunas devem entrar no nosso modelo de IA**.

Se vamos criar um modelo para prever **Atraso** ou **Satisfação (Review Score)**, precisamos encontrar quais outras colunas do banco de dados têm uma *Forte Correlação* com essas duas.

### Casos de Uso Práticos no nosso Projeto:

1.  **Foco Satisfação:** Faremos um Teste de Pearson cruzando `Dias_de_Atraso` com `Review_Score`. Esperamos ver uma correlação **Negativa Forte** (ex: -0.80), indicando claramente para a Inteligência Artificial que "se os dias aumentarem, diminua drasticamente a nota prevista".
2.  **Foco Logística:** Faremos um Teste de Pearson cruzando `Distancia_KM` (entre vendedor e comprador) com `Tempo_de_Entrega`. Provavelmente haverá uma correlação **Positiva Forte**.
3.  **Para Descartar Lixo:** Se cruzarmos `Tamanho_do_Nome_do_Produto` com `Review_Score` e o Pearson der `0.02` (Nenhuma), nós saberemos imediatamente que o nome do produto não afeta a nota, e podemos **deletar essa coluna** para não confundir nosso modelo de Machine Learning.

## Cuidados Importantes (Limitações)
1.  **Correlação não é Causalidade:** Só porque duas coisas sobem juntas, não significa que uma causa a outra.
2.  **Apenas Relações Lineares:** O Pearson traça uma reta. Se a relação entre as variáveis fizer uma curva (ex: em formato de "U", onde a satisfação é alta no começo, cai no meio e sobe no fim), o Pearson vai dar Nota `0`, mesmo existindo um padrão claro. Nesses casos, usa-se a *Correlação de Spearman*.
3.  **Matemática Pura:** Só aceita números. Para calcular a relação do Review Score com variáveis de texto ou categorias (ex: "Estado SP" ou "Categoria Móveis"), precisaremos transformar essas categorias em números antes.
