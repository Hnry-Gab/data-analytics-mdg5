# Fase Atual: Análise Exploratória Nichada (EDA)

Toda a nossa modelagem preditiva a partir de agora dependerá de encontrar os padrões corretos que influenciam atrasos e notas baixas. Esta documentação define o foco da nossa Análise Exploratória de Dados (EDA), cujo objetivo principal é **encontrar insights empíricos sobre os atributos que se relacionam com os nossos contextos**.

Serão realizadas duas frentes de investigação, uma para cada contexto:

---

## Contexto 1: Atraso na Entrega (Logística)
*Foco principal: Analisar tabelas relativas à localização (`geolocation`), produtos (`products`) e registro de datas temporais (`orders`).*

**Métricas a descobrir na EDA:**
*   **Tempo vs Localização:** Rotas específicas (Ex: de SP para o Nordeste ou interior de MG) possuem taxas de atraso sistematicamente maiores?
*   **A Matriz do Produto:** Produtos classificados nas categorias de alta cubagem/peso (`furniture_decor`, `bed_bath_table`) sofrem mais atraso devido ao manuseio logístico dificultado em relação a categorias de pacotes menores?
*   **Ofensores (Pareto):** Uma minoria de vendedores é responsável pela grande maioria (80%) dos atrasos no despache do produto? Quais as características desses vendedores?
*   **Temporalidade:** Existem épocas do mês ou dias específicos da compra que geram um ciclo vicioso de atrasos (ex: final de semana retardando a postagem)?
*   **A Relação do Frete (Growth):** O valor cobrado pelo frete (`freight_value`) vs o valor bruto do produto (`price`) afeta a tolerância do cliente? Clientes que pagaram proporcionalmente muito caro no frete cancelam mais ou abrem mais reclamações quando existe atraso?

### Próximos Passos
Após isolar os "outliers" (como pedidos registrados com centenas de dias para entrega por erro no sistema) e mapear visualmente essas correlações por meio de gráficos, teremos clareza exata de quais colunas transformaremos nas *Features* que alimentarão nossos algoritmos de Machine Learning (Random Forest / XGBoost). O foco final será entregar um modelo logístico capaz de prever retenção e maximizar a margem financeira de Growth.
