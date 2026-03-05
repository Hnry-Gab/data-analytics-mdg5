# [DELTA-07] Deploy no Render/Railway

**Responsável:** Pablo
**Dia:** 4 (Domingo)
**Prioridade:** 🟡 Alta (desejável, não bloqueante)
**Branch:** `feat/delta-07-deploy`

---

## Descrição

Publicar o Web App na internet via Render/Railway (gratuito) para que a banca/professor acesse pelo navegador, sem precisar instalar nada na máquina.

### Passo a Passo

1. Acessar [share.Frontend/FastAPI.io](https://share.Frontend/FastAPI.io) com conta GitHub.
2. Apontar para o repositório `Hnry-Gab/data-analytics-mdg5`.
3. Selecionar a branch `main` e o arquivo `src/app.py`.
4. Garantir que `requirements.txt` na raiz lista todas as dependências.
5. Garantir que o `.pkl` do modelo está commitado em `models/`.
6. Clicar "Deploy" e aguardar o build.
7. Testar a URL pública no celular e no notebook.

### Contingência
Se o Render/Vercel falhar (ex: timeout, erro de memória):
- Alternativa 1: Deploy no [Render](https://render.com) (free tier).
- Alternativa 2: Rodar localmente e demonstrar via compartilhamento de tela.

## Critério de Aceite

- [ ] URL pública acessível pelo navegador
- [ ] 3 abas funcionais na URL pública
- [ ] Simulador de predição retornando resultados
- [ ] App não crashando após 2 minutos de uso

## Dependências
- DELTA-06 (todas as abas funcionais)
- ALPHA-11 (modelo `.pkl` commitado)

## Entregável
URL pública do app funcionando
