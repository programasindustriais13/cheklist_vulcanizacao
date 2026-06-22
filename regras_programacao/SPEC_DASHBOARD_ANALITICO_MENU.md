# 🧠 SPEC — Painel Gráfico (Dashboard Analítico) e Refatoração do Menu

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** 
  - `/dashboard/` (Nova rota para o Dashboard Analítico)
  - `/` (Rota principal/home - renomeada visualmente para "Início")
- **Contexto(s):** Dashboard Analítico, Menu de Navegação e Filtros de Período.
- **Perfil(s) afetados:**
  - Eletricista, Mecânico, Eletromecânico, Lider: Oculto no menu e acesso bloqueado (redireciona para home).
  - Analista, Diretor, Superusuário: Acesso total permitido e link visível no menu.

---

## ❗ 2. PROBLEMA ATUAL

- O menu chama a rota home (`/`) de "Dashboard", mas sua função real é listar checklists e fornecer o controle do fluxo operacional (aprovações/inspeções).
- Falta um painel analítico/gráfico para a gerência e engenharia de manutenção acompanharem o desempenho da fábrica, reincidências de problemas, distribuição de falhas e cumprimento da rotina de inspeção.

---

## 🎯 3. OBJETIVO

- Renomear o link "Dashboard" atual para **"Início"**.
- Criar a rota `/dashboard/` apontando para um novo **Dashboard Analítico** com 4 gráficos interativos utilizando **Chart.js via CDN**:
  1. **Evolução dos Checklists Realizados** (Linha/Tendência).
  2. **Quantidade de Problemas Encontrados por Máquina** (Barras).
  3. **Distribuição dos Tipos de Falha** (Pizza/Donut).
  4. **Reincidência de Problemas** (Barras Empilhadas).
- Integrar todos os gráficos ao filtro de período por data (Data Inicial e Data Final).
- Restringir o acesso apenas a Diretores, Analistas e Superusers.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Possíveis arquivos:
- `core/urls.py` (Adicionar rota `/dashboard/`)
- `core/views.py` (Implementar a view `analytical_dashboard` com agregação de dados)
- `core/templates/core/base.html` (Refatorar menu para renomear home e adicionar link do Dashboard Analítico)
- `core/templates/core/analytical_dashboard.html` [NEW] (Criar o template dos gráficos)
- `core/tests.py` (Adicionar testes para o novo dashboard e permissões)

---

## 🚫 5. FORA DE ESCOPO

- Não criar novos apps ou alterar a estrutura do banco de dados (sem alterações no `models.py`, portanto sem migrations).
- Não instalar pacotes adicionais no `requirements.txt` para gráficos (utilizar Chart.js no frontend).
- Não modificar as regras de aprovação ou fluxo do checklist atual.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

- Utilizar apenas o ambiente virtual existente (`venv/`).
- Validar permissões no backend (decorador `@machine_management_required` ou verificação direta de specialty/superuser).
- Usar ORM do Django para todas as queries.
- Manter a interface em Português Brasileiro (pt-br).

---

## ⚙️ 7. REGRAS DE NEGÓCIO

1. **Restrição de Acesso:** Apenas perfis `Diretor`, `Analista` ou `is_superuser=True` podem acessar `/dashboard/`. Outros perfis recebem mensagem de erro e são redirecionados para a tela inicial.
2. **Checklists Realizados/Finalizados:** Para fins estatísticos, checklists finalizados são aqueles que possuem o campo `completed_at` preenchido (ou seja, status `AGUARDANDO_LIDER`, `APROVADO`, `REPROVADO_LIDER`, `REPROVAR_FINAL_REFAZER`).
3. **Agrupamento de Evolução (Gráfico 001):**
   - Período <= 30 dias: Agrupar por Dia.
   - Período > 30 e <= 120 dias: Agrupar por Semana.
   - Período > 120 dias: Agrupar por Mês.
4. **Problemas por Máquina (Gráfico 002):** Contar ocorrências do status `'NC'` na tabela `ChecklistItemValue` agrupadas por máquina das sessões do período.
5. **Tipos de Falha (Gráfico 003):** Contar ocorrências do status `'NC'` por seção (`HIDRAULICA`, `PNEUMATICA`, `ELETRICA`, `ESTRUTURA`, `SISTEMA_VULCANIZACAO`, `SISTEMA_VAPOR`) mapeando para nomes limpos/amigáveis.
6. **Reincidência de Problemas (Gráfico 004):** Mapear o volume de falhas por seção para cada mês presente no período selecionado.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Menu do sistema atualizado: link da Home alterado para "Início" e link do "Dashboard Analítico" visível apenas para os perfis permitidos.
- [ ] Acesso à rota `/dashboard/` retorna `200 OK` para Analista, Diretor e Superuser.
- [ ] Acesso à rota `/dashboard/` retorna redirect + erro `403` ou mensagem de erro para Mecânicos, Eletricistas e Líderes.
- [ ] Os 4 gráficos são renderizados usando dados do backend.
- [ ] O filtro de data atualiza dinamicamente os 4 gráficos.
- [ ] Sem regressão nas telas e fluxos existentes.
- [ ] Todos os testes automatizados passam.

---

## ⚠️ 9. RISCOS

- **Carregamento assíncrono do Chart.js:** Utilizar tags script corretas na CDN para garantir que o script carregue antes de inicializar os gráficos.
- **Divisão de tempo com datas limites:** Garantir que o fuso horário local seja respeitado ao converter datas do filtro para o banco de dados.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

1. **Definição de Rotas:** Adicionar a rota `/dashboard/` em `core/urls.py`.
2. **Menu Base:** Atualizar `base.html` para renomear e condicionar a exibição do novo link.
3. **Lógica de Views:** Criar `analytical_dashboard` em `core/views.py`, herdando os filtros de período e agregando os dados no formato adequado para os gráficos.
4. **Interface Visual (Template):** Criar `analytical_dashboard.html` herdando de `base.html`, incluindo CDN do Chart.js e construindo os gráficos.
5. **Testes:** Escrever testes no `core/tests.py`.
6. **Protocolo:** Registrar em `Instrucoes.txt`.

---

## 🧪 11. TESTES MANUAIS

1. Login como Mecânico: verificar que "Dashboard Analítico" não aparece no menu e se tentar acessar `/dashboard/` direto é redirecionado com aviso.
2. Login como Analista/Diretor: verificar presença do link e renderização dos gráficos com filtro padrão (mês corrente).
3. Alterar filtro de datas para um intervalo maior: verificar se os gráficos e escalas de tempo mudam de forma correspondente.
4. Validar se os totais e distribuições batem com os dados salvos na listagem operacional.
