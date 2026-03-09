1. Transformar o ZIP em Latitude e Longitude. Isso permite que o modelo entenda distância física real.

Prompt Otimizado
Contexto: Atue como um Engenheiro de Machine Learning Sênior. Preciso de um pipeline de previsão de tempo de entrega (Logística) usando dados do Brasil.
Input de Exemplo: seller_zip_code_prefix (ex: 9350), seller_city, seller_state, customer_zip_code_prefix (ex: 3149).

Instruções Técnicas Específicas:

Normalization de Prefixos: Note que os prefixos podem ter 4 ou 5 dígitos. Padronize-os para 5 dígitos (adicionando zero à esquerda, ex: 9350 -> 09350) para garantir a integridade da localização geográfica.

Feature Engineering Geográfica:

Region Cross: Crie uma feature categórica combinando seller_state + customer_state (ex: "SP_MG"). Isso ajuda o modelo a capturar impostos, barreiras fiscais e rotas interestaduais.

Macro-Região: Extraia o primeiro dígito do prefixo (Região Postal) para ambos (origem/destino).

Geocoding & Haversine: * Utilize uma base de coordenadas (Latitude/Longitude) para os prefixos de CEP.

Calcule a Distância de Haversine entre o vendedor e o cliente.

Tratamento de Categóricos (Alta Cardinalidade):

O zip_code_prefix tem milhares de variações. Não use One-Hot Encoding.

Implemente Target Encoding no customer_zip_code_prefix e no seller_zip_code_prefix, usando a média de dias de entrega como alvo. Utilize um min_samples_leaf para evitar overfitting em CEPs com poucas vendas.

Variáveis de Calendário: Extraia "dia da semana" e "mês" da data de postagem, pois o tráfego logístico no Brasil varia drasticamente em feriados e finais de semana.