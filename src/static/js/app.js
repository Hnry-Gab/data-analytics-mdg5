/**
 * Frontend JavaScript para Olist Logistics API
 */

// Elementos do DOM
const form = document.getElementById('predictionForm');
const resultCard = document.getElementById('resultCard');
const resultDiv = document.getElementById('result');
const errorCard = document.getElementById('errorCard');
const errorDiv = document.getElementById('error');
const submitButton = form.querySelector('button[type="submit"]');

// Event listener do formulário
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Esconder resultados anteriores
    hideResults();

    // Desabilitar botão durante a requisição
    submitButton.disabled = true;
    submitButton.textContent = 'Processando...';

    try {
        // Coletar dados do formulário
        const formData = new FormData(form);
        const data = {
            cep_cliente: formData.get('cep_cliente'),
            cep_vendedor: formData.get('cep_vendedor'),
            categoria_produto: formData.get('categoria_produto'),
            peso_produto_kg: parseFloat(formData.get('peso_produto_kg')),
            preco_frete: parseFloat(formData.get('preco_frete')),
            peso_produto_volume_cm3: parseFloat(formData.get('peso_produto_volume_cm3'))
        };

        // Fazer requisição para a API
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Erro ao realizar predição');
        }

        // Exibir resultado
        displayResult(result);

    } catch (error) {
        console.error('Erro:', error);
        displayError(error.message);
    } finally {
        // Reabilitar botão
        submitButton.disabled = false;
        submitButton.textContent = 'Prever Atraso';
    }
});

/**
 * Exibe o resultado da predição
 */
function displayResult(result) {
    const probabilidade = result.probabilidade_atraso;
    const classe = result.classe_predicao;
    const confianca = result.confianca;
    const features = result.features_utilizadas;

    const classeClass = classe === 'No Prazo' ? 'no-prazo' : 'atrasado';

    resultDiv.innerHTML = `
        <div class="result-metric">
            <strong>Probabilidade de Atraso:</strong>
            <span class="${classeClass}">${probabilidade.toFixed(2)}%</span>
        </div>

        <div class="result-metric">
            <strong>Classificação:</strong>
            <span class="${classeClass}">${classe}</span>
        </div>

        <div class="result-metric">
            <strong>Confiança da Predição:</strong>
            <span>${confianca.toFixed(2)}%</span>
        </div>

        <div class="features-list">
            <strong>Features Processadas:</strong>
            <ul>
                <li>Distância: ${features.distancia_km} km</li>
                <li>Categoria: ${features.categoria_original} (${features.categoria_encoded})</li>
                <li>Peso: ${features.peso_kg} kg</li>
                <li>Frete: R$ ${features.preco_frete.toFixed(2)}</li>
                <li>Volume: ${features.volume_cm3} cm³</li>
                <li>Preço/Peso: R$ ${features.preco_por_peso.toFixed(2)}/kg</li>
                <li>Densidade: ${features.densidade_kg_m3.toFixed(2)} kg/m³</li>
            </ul>
        </div>
    `;

    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Exibe mensagem de erro
 */
function displayError(message) {
    errorDiv.innerHTML = `
        <p style="color: var(--danger-color); font-weight: 600;">
            ⚠️ ${message}
        </p>
        <p style="margin-top: 1rem; color: var(--text-secondary);">
            Verifique os dados e tente novamente.
        </p>
    `;

    errorCard.style.display = 'block';
    errorCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Esconde cards de resultado e erro
 */
function hideResults() {
    resultCard.style.display = 'none';
    errorCard.style.display = 'none';
}

/**
 * Formata CEP enquanto digita (adiciona hífen automaticamente)
 */
const cepInputs = document.querySelectorAll('input[name^="cep_"]');
cepInputs.forEach(input => {
    input.addEventListener('input', (e) => {
        // Permitir apenas números
        e.target.value = e.target.value.replace(/\D/g, '');
    });
});

/**
 * Health check ao carregar a página
 */
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();

        console.log('Health Check:', health);

        if (health.status !== 'healthy') {
            console.warn('API não está totalmente saudável:', health);
        }

        if (!health.model_loaded) {
            alert(
                'Aviso: Modelo de ML não está carregado. ' +
                'Predições não estarão disponíveis até que o modelo seja carregado.'
            );
        }
    } catch (error) {
        console.error('Erro no health check:', error);
    }
});
