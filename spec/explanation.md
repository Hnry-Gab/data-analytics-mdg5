## Parte 1: Data Pipeline Foundation

A base de qualquer projeto de dados. Sem um "ground truth" confiável, os modelos subsequentes falharão.

* **Importância:** Garante a integridade referencial. O dataset da Olist tem uma estrutura de esquema em estrela (8 tabelas); erros nos joins (como duplicar ordens devido a múltiplos itens) podem inflar o faturamento artificialmente.
* **Defeitos/Riscos:**
* **Data Leakage:** Limpar timestamps sem considerar o "tempo de corte" pode vazar informações do futuro para o passado.
* **Custo de Memória:** Unir as 8 tabelas em um único DataFrame pode estourar a RAM. O uso do **Parquet** é excelente aqui para otimizar o I/O.
* **Omissão de Geolocalização:** Ignorar a tabela de geolocalização pode impedir análises de frete que explicam o churn.

---

## Parte 2: Customer Analytics Core

Transforma transações em comportamento humano.

* **Importância:** O RFM (Recência, Frequência, Valor Monetário) é o padrão ouro para e-commerce. Definir o Churn como >180 dias é realista para o varejo brasileiro, onde o ciclo de recompra é mais longo que em apps de SaaS.
* **Defeitos/Riscos:**
* **Janela Estática:** O dataset da Olist é limitado no tempo (2016-2018). 180 dias pode ser muito tempo para alguns usuários, reduzindo sua amostra de "churners" reais.
* **Frequência:** A maioria dos clientes da Olist comprou apenas uma vez. Isso gera uma massa de dados enviesada para $F=1$, dificultando a diferenciação de grupos.

---

## Parte 3: Segmentation Models

A transição da estatística descritiva para o aprendizado não supervisionado.

* **Importância:** O **K-Means** agrupa clientes com comportamentos similares que o olho humano não veria. O **BG/NBD** (Beta Geometric/Negative Binomial Distribution) é essencial para prever a "probabilidade de estar vivo" do cliente.
* **Defeitos/Riscos:**
* **K-Means Sensibility:** O K-Means é sensível a outliers (clientes "baleias"). É obrigatório escalar os dados (StandardScaler ou RobustScaler) antes do treino.
* **Interpretabilidade:** Clusters puramente matemáticos podem não fazer sentido para o marketing. O "Segment Labeling Logic" deve ser muito bem alinhado ao negócio.

---

## Parte 4: Value Prediction

Onde o projeto se torna financeiramente estratégico.

* **Importância:** O modelo **Gamma-Gamma** acoplado ao BG/NBD permite estimar o **Customer Lifetime Value (CLV)** futuro, não apenas o histórico. Isso decide quanto a empresa pode gastar para adquirir um novo cliente (CAC).
* **Defeitos/Riscos:**
* **Premissa do Gamma-Gamma:** Ele assume que não há correlação entre o valor monetário e a frequência. No e-commerce real, quem compra mais vezes às vezes gasta menos por pedido. Você precisará validar essa independência.

---

## Parte 5: Churn Prediction

Ação preventiva para estancar a perda de receita.

* **Importância:** Usar **XGBoost** permite capturar relações não lineares (ex: um cliente com boa recência mas com uma entrega atrasada e nota 1 no review tem alta chance de churn).
* **Defeitos/Riscos:**
* **Desbalanceamento de Classes:** Provavelmente haverá muito mais "Não-Churn" do que "Churn" (ou vice-versa, dependendo da janela). Será necessário usar técnicas como SMOTE ou ajustar o `scale_pos_weight` no XGBoost.
* **Feature Importance vs. Causality:** O modelo dirá o que correlaciona com o churn, mas não necessariamente a causa raiz.

---

## Parte 6: Advanced Analytics

O diferencial competitivo do projeto.

* **Importância:**
* **NLP:** O texto das avaliações é onde mora o "porquê" do churn.
* **Apriori:** Fundamental para recomendação de "Compre Junto" (Cross-sell).
* **Uplift Modeling:** A joia da coroa. Ele identifica quem só comprará *se* receber um cupom, evitando gastar margem com quem já compraria de qualquer forma.


* **Defeitos/Riscos:**
* **Complexidade:** O Apriori pode ser computacionalmente caro. O `causalml` exige um design experimental rigoroso; com dados históricos (observacionais), o viés de seleção é alto.

---

## Parte 7: Dashboard & Testing

A entrega de valor para o usuário final.

* **Importância:** Streamlit transforma código em ferramenta de decisão. Testes E2E com Playwright garantem que o dashboard não quebre quando os dados mudarem.
* **Defeitos/Riscos:**
* **Performance:** Dashboards com grandes volumes de dados no Streamlit podem ficar lentos. O uso de `@st.cache_data` e o carregamento via Parquet da Parte 1 serão vitais.
* **Sobrecarga de Informação:** 5 páginas podem dispersar o usuário. O foco deve ser na página de "Ações Recomendadas".