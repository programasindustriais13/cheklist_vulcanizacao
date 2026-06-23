# 🧠 SPEC — FILTROS AVANÇADOS NA TABELA, OBSERVAÇÃO GERAL E RESPONSIVIDADE MOBILE DA OBSERVAÇÃO

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** 
  - `/` (Dashboard / Histórico)
  - `/checklist/start/` (Início de checklist)
  - `/checklist/<session_id>/` (Execução/Visualização de Checklist)
  - `/export/dashboard/excel/` (Exportação do histórico consolidado)
  - `/export/checklist/excel/<session_id>/` (Exportação do checklist individual)
- **Contexto(s):** Dashboard, Execução de Checklist, Exportação Excel
- **Perfil(s) afetados:** Eletricista, Mecânico, Eletromecânico (Técnicos/Inspetores), Líder (Aprovadores), Analista/Diretor (Revisores) e Superusuários.

---

## ❗ 2. PROBLEMA ATUAL

1. **Falta de Filtros no Histórico:** O painel principal (dashboard) do checklist exibe o histórico de sessões com filtro apenas por período (data inicial e final). No entanto, não é possível filtrar facilmente por máquina, inspetor específico, líder de turno, status ou realizar uma busca textual por NCs específicas, o que dificulta a rastreabilidade à medida que o volume de checklists cresce.
2. **Ausência de Campo de Observação Geral:** O formulário de preenchimento atual permite apenas observações individuais por item de checklist (especialmente quando há não conformidades). Não existe um campo livre para observações gerais sobre o estado geral da máquina no final da inspeção.
3. **Responsividade Mobile dos Itens de Observação:** A visualização e edição das observações individuais em dispositivos móveis (smartphones) na tabela é compacta e desconfortável para digitação e leitura.

---

## 🎯 3. OBJETIVO

1. **Filtros Avançados:** Adicionar um painel de filtros robusto e responsivo no dashboard (acima da tabela principal) abrangendo Data (intervalo ou dia específico), Máquina (dropdown), Inspetor (dropdown), Líder (dropdown), Status (dropdown) e Resumo de NC (busca textual). Estes mesmos filtros devem ser aplicados à exportação de Excel consolidada.
2. **Campo de Observação Geral:** Adicionar o campo `general_observations` ao modelo `ChecklistSession` (nulo e em branco por padrão), permitindo ao inspetor adicionar observações sobre o estado geral da máquina no final do preenchimento e exibir esse campo na visualização do histórico e nos relatórios exportados (individual e consolidado).
3. **Modal de Observações Responsivo:** Implementar/Reestilizar uma janela modal/popup amigável para smartphones para visualização/edição das observações dos itens individuais, utilizando classes Bootstrap `modal-fullscreen-sm-down` e Media Queries customizadas com `width: 95%` para melhorar o aproveitamento do espaço em telas menores.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos afetados:
- `core/models.py`: Adicionar campo `general_observations` em `ChecklistSession`.
- `core/views.py`: 
  - Ajustar a view `dashboard` para receber e processar os novos filtros avançados na query.
  - Ajustar `export_dashboard_excel` para receber os mesmos filtros e incluir a nova coluna `Observações Gerais`.
  - Ajustar `checklist_execute` para processar o salvamento do campo `general_observations` no POST de `pause` e `finalize`.
  - Ajustar `export_checklist_excel` para incluir as observações gerais da máquina no cabeçalho do relatório.
- `core/templates/core/dashboard.html`: 
  - Adicionar o painel com os filtros avançados integrados aos filtros de período.
  - Repassar os filtros ativos no link de exportação do Excel consolidado.
- `core/templates/core/checklist_form.html`:
  - Adicionar a seção de Observações Gerais da Máquina ao final do formulário (com suporte a readonly dependendo do status do checklist).
  - Implementar uma janela modal (`#observationModal`) para edição/leitura responsiva das observações dos itens de checklist, acionável no mobile.
- `core/static/core/style.css`:
  - Adicionar estilos de media queries customizados para responsividade mobile da janela modal.

---

## 🚫 5. FORA DE ESCOPO

- Não alterar a máquina de estados principal ou as transições de status do checklist.
- Não refatorar ou modificar as permissões padrão dos usuários.
- Não criar novos apps ou alterar outros models não relacionados ao checklist.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

- Apenas **1 ambiente virtual (`venv`)** na raiz do projeto (já existente).
- Apenas **1 projeto Django** (`checklist_system`) e **1 app principal** (`core`).
- Utilizar migrations incrementais seguras para novos campos de banco de dados (`null=True`, `blank=True`).
- Validação rigorosa de permissões no backend.
- CSRF Token em todos os formulários.
- Registrar adequadamente transições de estado no `ChecklistTimelineLog`.

---

## ⚙️ 7. REGRAS DE NEGÓCIO

- O campo de **Observações Gerais** do checklist é opcional (`null=True`, `blank=True`).
- Só é permitida a edição das observações gerais caso o checklist esteja em um estado editável (`IN_PROGRESS`). Caso contrário, deve ser exibido como somente leitura (`readonly`).
- Os filtros na tela inicial devem poder ser combinados livremente.
- O filtro por "Resumo da NC" deve buscar no texto do nome dos itens do checklist que foram marcados com status Não Conforme (`NC`).
- Ao exportar para Excel, os filtros aplicados na tela devem ser respeitados, gerando um relatório equivalente.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Os filtros de Data, Máquina, Inspetor, Líder, Status e NC funcionam de forma combinada no Dashboard.
- [ ] O link de exportação do Excel consolidado respeita todos os filtros aplicados na tela e inclui a coluna "Observações Gerais".
- [ ] O campo `general_observations` é exibido ao final da página de preenchimento, é salvo corretamente ao pausar ou finalizar, e aparece como somente leitura ao visualizar checklists fechados.
- [ ] O Excel individual do checklist exibe o campo "Obs. Gerais da Máquina" no cabeçalho do documento de forma limpa.
- [ ] A janela modal de observações individuais é amigável em smartphones, cobrindo a tela inteira/usando 95% da largura e permitindo fácil digitação e fechamento.
- [ ] Migrations geradas e executadas sem erros.
- [ ] Todos os testes automatizados existentes e novos passam com sucesso (`python manage.py test`).

---

## ⚠️ 9. RISCOS

- **Duplicação de registros por Join:** Filtrar por itens de NC pode gerar duplicatas de ChecklistSession se não usarmos `.distinct()`.
- **Rompimento de compatibilidade no Banco:** Utilizar campos incompatíveis com MySQL/SQLite. O ORM do Django resolve isso.
- **Conflito de Modais Bootstrap:** Garantir IDs únicos e estrutura correta dos backdrops.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO

1. **Model:** Modificar `ChecklistSession` em `core/models.py` para incluir o campo `general_observations`.
2. **Migrations:** Executar `makemigrations` e `migrate` para atualizar o schema do banco.
3. **Formulário de preenchimento:** Atualizar `checklist_form.html` para incluir a área de "Observações Gerais" e a estrutura do modal responsivo `#observationModal`.
4. **Lógica de Views:**
   - Adicionar o salvamento de `general_observations` em `views.py`.
   - Adicionar suporte a múltiplos parâmetros de filtros na view `dashboard`.
   - Adicionar os filtros e a nova coluna à view `export_dashboard_excel`.
   - Adicionar o campo `general_observations` na view `export_checklist_excel`.
5. **Dashboard HTML:** Adicionar o painel de filtros e ajustar o link do Excel consolidado.
6. **Responsividade CSS:** Adicionar regras no `style.css` para aprimorar o layout mobile do modal de observações.
7. **Validação:** Criar e rodar testes automatizados e manuais.

---

## 🧪 11. TESTES MANUAIS

1. Iniciar um checklist, digitar observações gerais no final, salvar e pausar. Validar se persistem ao retomar.
2. Finalizar o checklist. Acessar a visualização e garantir que o campo de observações gerais está como `readonly`.
3. Aplicar filtros combinados na Dashboard (ex: Máquina X + Líder Y) e conferir a listagem.
4. Digitar uma NC específica no filtro de busca textual e verificar se apenas sessões contendo aquela NC (marcada como NC) são listadas.
5. Clicar em "Exportar Histórico" com os filtros ativos e validar se o Excel gerado reflete a listagem filtrada e possui a nova coluna.
6. Testar o modal mobile simulando a tela de smartphone (ex: 375px) no navegador. Verificar se abre em tela cheia / confortável.
