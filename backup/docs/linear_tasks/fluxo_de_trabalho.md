# Fluxo de Trabalho (Linear + GitHub)

Para garantir que o time avance de forma sincronizada, adotaremos o uso do **Linear** integrado ao repositório GitHub. O Linear otimiza nosso fluxo, criando nomenclaturas adequadas e linkando nativamente código, tarefas e Pull Requests.

---

## 🚀 Ciclo Profissional de Desenvolvimento

Cada membro atua da seguinte forma para iniciar e finalizar a sua Issue:

1. **Atribuir Issue no Linear:**
   Assuma a issue no painel do Linear (ex: *ALPHA-11 Exportação de pkl*). Ao passar o status para "In Progress", o Linear já disponibiliza o prefixo exato para copiar.

2. **Atualizar Bse Local:**
   Mantenha a `main` local atualizada antes de iniciar qualquer código.
   ```bash
   git checkout main
   git pull origin main
   ```

3. **Criar a Branch Padronizada:**
   **Dê `checkout -b` usando preferencialmente o comando sugerido pelo próprio Linear** (ou seguindo nosso padrão explícito na documentação). O ID da issue *tem obrigatoriamente que estar na branch* (ex: `feat/alpha-11-exportar-modelo`).
   ```bash
   git checkout -b feat/alpha-11-exportar-modelo
   ```

4. **Codar e Fazer Commits Semânticos:**
   Desenvolva a solução. Use Conventional Commits referenciando o ID no escopo. 
   ```bash
   git commit -m "feat(alpha-11): serializacao xgb em .pkl e geracao_artifacts"
   ```

5. **Aprovação Online via Pull Request (⚠️ REGRA DE OURO):**
   **Em NENHUMA hipótese você fará `git merge` local com a `main`.** Todo código validado sobe para validação da equipe via GitHub Actions e Pull Request. 
   ```bash
   git push origin feat/alpha-11-exportar-modelo
   ```

6. **Abrir Pull Request:**
   No GitHub, crie um PR apontando a sua branch contra a `main`. O fato da branch conter `alpha-11` fará o GitHub fechar e rastrear a tarefa do Linear automaticamente quando for feito o merge.

7. **Review & Merge:**
   Pelo menos um par de equipe analisa seu Pull Request online. Uma vez aprovado de forma síncrona/assíncrona, faz-se o "Squash and Merge" ou "Merge Commit" clicando no botão verde do GitHub. A branch deve ser deletada pós-merge para reter organização.
