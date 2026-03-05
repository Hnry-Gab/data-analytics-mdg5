# Dicionário de Dados: Olist Dataset

Este documento cataloga todos os atributos (colunas) separados por arquivo CSV para facilitar nossa Análise Exploratória (EDA) e ajudar a saber o que cruzar (`merge`) com o quê.

---

## 1. Clientes (`olist_customers_dataset.csv`)
Traz as informações cadastrais e de localização dos clientes (compradores).
*   **`customer_id`**: Chave de identificação única do cliente *específica do pedido* (muda a cada nova compra, é usada como chave de cruzamento com `Orders`).
*   **`customer_unique_id`**: Chave de identificação do cliente na *plataforma* (fixa e inalterável. Serve para contar quem comprou 2x ou mais vezes).
*   **`customer_zip_code_prefix`**: Os cinco primeiros dígitos do CEP de envio do cliente.
*   **`customer_city`**: Cidade do comprador.
*   **`customer_state`**: Estado (UF) do comprador.

---

## 2. Pedidos (`olist_orders_dataset.csv`)
A tabela principal ("Coração do negócio") que liga clientes, prazos e produtos. Usada para cálculos de tempo e atrasos logísticos.
*   **`order_id`**: Identificador único do pedido.
*   **`customer_id`**: Chave que liga este pedido ao cliente (tabela anterior).
*   **`order_status`**: Em qual etapa da esteira o pedido está ou estava (entregue, cancelado, enviado...).
*   **`order_purchase_timestamp`**: Momento (carimbo de data/hora) da **solicitação** da compra.
*   **`order_approved_at`**: Momento da **aprovação do pagamento**.
*   **`order_delivered_carrier_date`**: Momento logístico em que o pacote **entrou na rede da transportadora** (foi postado).
*   **`order_delivered_customer_date`**: Momento real em que o pacote **chegou na mão do cliente**! (Importante).
*   **`order_estimated_delivery_date`**: Prazo de entrega **informado ao cliente** no site. (Gera o "Atraso" se comparada com a data real acima).

---

## 3. Itens do Pedido (`olist_order_items_dataset.csv`)
Lista individual de cada produto físico dentro de um "order_id" (se você comprou 3 coisas juntas, haverão 3 linhas diferentes aqui amarradas à mesma compra).
*   **`order_id`**: Identificador do carrinho.
*   **`order_item_id`**: Número sequencial organizador dentro do carrinho (1 = produto A, 2 = produto B).
*   **`product_id`**: Identifica qual o produto físico escolhido.
*   **`seller_id`**: Identifica qual o vendedor (lojista Olist) comercializou esse item.
*   **`shipping_limit_date`**: Prazo que a Olist deu ao lojista para providenciar as embalagens e transferir para a transportadora.
*   **`price`**: Valor do produto isolado.
*   **`freight_value`**: Preço rateado que o cliente pagou de **frete** só por causa deste item específico.

---

## 4. Produtos (`olist_products_dataset.csv`)
Traz os metadados e medidas físicas do que foi comprado.
*   **`product_id`**: Chave do produto.
*   **`product_category_name`**: Nome/tipo de categoria principal na qual o produto foi listado.
*   **`product_name_lenght`**: Quantidade de caracteres usados no nome/título.
*   **`product_description_lenght`**: Quantidade de caracteres na sua descrição do e-commerce.
*   **`product_photos_qty`**: Número de fotos na galeria do anúncio.
*   **`product_weight_g`**: Peso estático do produto (em Gramas).
*   **`product_length_cm`**: Comprimento do pacote (Centímetros).
*   **`product_height_cm`**: Altura do pacote (Centímetros).
*   **`product_width_cm`**: Largura do pacote (Centímetros).

---

## 5. Avaliações/Reviews (`olist_order_reviews_dataset.csv`)
Dados sobre a opinião do cliente pós-venda. Apesar de conter o *Review Score*, usaremos esta tabela apenas como apoio secundário para cruzar atrasos com reclamações escritas, sem focar em prever a nota final.
*   **`review_id`**: Identificador exclusivo do formulário de resenha.
*   **`order_id`**: Identificador de qual compra a resenha está descrevendo.
*   **`review_score`**: A **nota do cliente de 1 a 5** (1=Terrível, 5=Excelente).
*   **`review_comment_title`**: (Texto) Se o cliente deu um título na reclamação.
*   **`review_comment_message`**: (Texto) A resenha, a reclamação ou o elogio feito à mão.
*   **`review_creation_date`**: Data em que o e-mail de "Qual a sua opinião?" chegou ao cliente.
*   **`review_answer_timestamp`**: Data e hora exatas que o cliente clicou lá e enviou a pesquisa com a nota.

---

## 6. Vendedores (`olist_sellers_dataset.csv`)
Dados de onde vem a encomenda (A Origem).
*   **`seller_id`**: Chave de identificação do vendedor (lojista parceiro).
*   **`seller_zip_code_prefix`**: Os cinco primeiros dígitos do CEP da lojinha dele.
*   **`seller_city`**: A cidade de despacho logístico dele.
*   **`seller_state`**: A UF de onde o frete vai partir.

---

## 7. Pagamentos (`olist_order_payments_dataset.csv`)
Dados financeiros sobre faturas consolidadas.
*   **`order_id`**: O carrinho / nota sendo paga.
*   **`payment_sequential`**: Diz se a pessoa precisou dividir (usar 2 cartões de crédito diferentes ou um voucher promocional + um boleto = sequência 1, 2, etc, pra fechar o valor da compra).
*   **`payment_type`**: A modalidade do crédito (voucher, pix, boleto, credit_card).
*   **`payment_installments`**: Número de parcelas (1x até 24x).
*   **`payment_value`**: Montante faturado / pago naquela modalidade específica.

---

## 8. Geolocalização (`olist_geolocation_dataset.csv`)
Tabela auxiliar essencial para gerar insights de mapeamento logístico numérico na EDA.
*   **`geolocation_zip_code_prefix`**: CEP base de análise (chave de cruzamento para clientes e lojistas).
*   **`geolocation_lat`**: A coordenada geográfica exata de **Latitude (Eixo Y)**.
*   **`geolocation_lng`**: A coordenada geográfica exata de **Longitude (Eixo X)**.
*   **`geolocation_city`**: O nome nativo da cidade referida na coordenada.
*   **`geolocation_state`**: Sigla regional referida pelas coordenadas acima.

---

## 9. Tradução de Categorias (`product_category_name_translation.csv`)
Tabela auxiliar "Tabela de/Para".
*   **`product_category_name`**: Nome raiz listado no Brasil (em Pt-Br).
*   **`product_category_name_english`**: A conversão do nome acima para o Inglês, ótimo se for rodar algoritmos que preferem labels anglo-saxões (Ex: _beleza_saude_ -> _health_beauty_).
