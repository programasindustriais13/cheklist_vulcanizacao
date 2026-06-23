# 🧠 SPEC — Visibilidade Restrita de Checklists e Sistema de Duplas (Login Combinado)

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:**
  - `/` (Dashboard / Início)
  - `/checklist/start/` (Iniciar novo checklist)
  - `/checklist/<session_id>/` (Execução de Checklist)
  - `/admin/` (Painel Administrativo)
  - `/checklist/<session_id>/export/` (Exportação de checklist individual para Excel)
  - `/dashboard/export/` (Exportação do histórico consolidado para Excel)
- **Contexto(s):** Dashboard, Execução de Checklist, Cadastro de Usuários (Django Admin), Exportação Excel.
- **Perfil(s) afetados:**
  - Perfis operacionais: Eletricista, Mecânico, Eletromecânico (devem ter visibilidade restrita aos próprios checklists e os de sua dupla).
  - Perfis de gestão: Líder de Turno (pode ver todos para aprovação), Analista/Diretor e Admin (visualização global, gestão e exportações).

---

## ❗ 2. PROBLEMA ATUAL

- Atualmente, técnicos de especialidades diferentes (como um Eletricista e um Mecânico) realizam a inspeção de forma conjunta compartilhando o mesmo tablet física e operacionalmente, mas o sistema só permite associar a sessão a um único usuário logado (`inspector`).
- Não há registro de quem realizou a inspeção conjunta em dupla no banco de dados nem na exportação do Excel.
- Técnicos conseguem visualizar todos os checklists do sistema no Dashboard, quando na verdade deveriam visualizar apenas os de sua própria responsabilidade (checklists criados por eles mesmos ou onde atuaram como co-inspetores/duplas).

---

## 🎯 3. OBJETIVO

- Implementar o **Sistema de Duplas de Turno** no Django Admin, permitindo vincular dois técnicos operacionais.
- Salvar automaticamente no banco de dados (`ChecklistSession.co_inspector`) o parceiro do técnico que iniciou a inspeção se ele possuir uma dupla configurada.
- Exibir os nomes e especialidades de ambos os inspetores no cabeçalho da execução do checklist, nas listagens e filas do Dashboard.
- Restringir a visibilidade de checklists no Dashboard para que usuários de nível operacional vejam apenas os checklists onde constam como inspetor principal ou co-inspetor.
- Ajustar os relatórios em Excel (individual e consolidado) para incluir a informação do co-inspetor.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Possíveis arquivos:
- [models.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/00_backup/06 - Cheklist_git/core/models.py) (Adicionar `partner_user` no User e `co_inspector` no ChecklistSession)
- [views.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/00_backup/06 - Cheklist_git/core/views.py) (Ajustar o queryset principal no dashboard para aplicar restrição de técnicos; salvar `co_inspector` ao iniciar a sessão; ajustar exportações)
- [admin.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/00_backup/06 - Cheklist_git/core/admin.py) (Configurar o campo de dupla no CustomUserAdmin com filtros adequados)
- [templates/core/dashboard.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/00_backup/06 - Cheklist_git/core/templates/core/dashboard.html) (Ajustar as tabelas para exibir inspetor e co-inspetor com especialidades)
- [templates/core/checklist_form.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/00_backup/06 - Cheklist_git/core/templates/core/checklist_form.html) (Exibir no cabeçalho o inspetor e co-inspetor)

---

## 🚫 5. FORA DE ESCOPO

- Não alterar a máquina de estados do checklist (fluxo de aprovações).
- Não remover campos antigos ou alterar regras de preenchimento/validação dos itens de checklist (como obrigatoriedade de obs em NC).
- Não criar novos apps ou alterar outras configurações de segurança de sessão e timeouts.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

⚠️ Esta implementação DEVE seguir o `constitution.md`

### Regras críticas:
- ❌ Não criar múltiplos ambientes (venv2, .venv, etc.)
- ❌ Não duplicar projeto ou apps
- ❌ Não duplicar lógica existente
- ✅ Reutilizar código existente
- ✅ Validar permissões no backend (via `User.specialty` ou `is_superuser`)
- ✅ Usar ORM do Django (nunca SQL direto)
- ✅ CSRF Token em todos os formulários POST
- ✅ Registrar transições no `ChecklistTimelineLog`

---

## ⚙️ 7. REGRAS DE NEGÓCIO

1. **Associação de Duplas**: No perfil de usuário (`User`), o campo `partner_user` (ForeignKey para si mesmo) deve armazenar o parceiro. A alteração deve ser simétrica (se A aponta para B, B deve apontar para A). Apenas técnicos ativos de especialidades operacionais podem ser configurados como duplas.
2. **Sessão em Andamento**: Ao iniciar uma inspeção em `/checklist/start/`, se o usuário possuir um `partner_user` ativo configurado, o campo `co_inspector` da `ChecklistSession` será automaticamente preenchido com esse parceiro.
3. **Visibilidade de Checklists**:
   - Técnicos (Eletricista, Mecânico, Eletromecânico) só visualizam sessões no dashboard onde `inspector = request.user` OU `co_inspector = request.user`.
   - Perfis de gestão (Líder, Analista, Diretor) e superusuários visualizam todas as sessões do período filtrado.
4. **Exibição dos Inspetores**:
   - Onde houver exibição do responsável (cabeçalho da execução do checklist, tabelas do dashboard), mostrar o formato `"João (Mecânico) & Paulo (Eletricista)"` caso haja co-inspetor cadastrado, ou `"João (Mecânico)"` se for individual.
5. **Exportação Excel**:
   - A exportação individual deve concatenar os inspetores no campo "Inspetor(es)".
   - A exportação consolidada do histórico deve ter a coluna "Co-Inspetor" logo após a coluna "Inspetor".

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

A tarefa só é considerada concluída se:
- [ ] Funcionalidade de duplas permite configuração bidirecional simétrica e correta no Django Admin.
- [ ] A tela de início do checklist carrega o parceiro e persiste no campo `co_inspector` automaticamente.
- [ ] A tela de execução do checklist exibe ambos os inspetores no cabeçalho.
- [ ] O dashboard exibe ambos nas colunas de inspetor e filas de aprovação/correção.
- [ ] O isolamento de QuerySet está ativo e técnicos só visualizam checklists de sua autoria ou co-autoria.
- [ ] Relatórios em Excel contêm o co-inspetor conforme as especificações.
- [ ] Testes automatizados passam (`python manage.py test`), incluindo os novos testes que validam esse isolamento de visibilidade.

---

## ⚠️ 9. RISCOS

- **Recursão Infinita no User.save()**: A atualização simétrica do `partner_user` pode causar loop se não houver salvamento com `update_fields` ou uma trava de recursão.
- **Inconsistência de Migrations**: Como modificamos `User` e `ChecklistSession`, precisamos criar uma migração segura para bancos SQLite (dev) e MySQL (prod) aceitando valores nulos (`null=True, blank=True`).
- **Problema em Dados Legados**: Checklists anteriores ao sistema de duplas terão `co_inspector` como `null`. A exibição no frontend e as exportações devem tratar `co_inspector` nulo sem erros.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:

1. **Modificar Models**:
   - Adicionar `partner_user` no model `User`.
   - Adicionar `co_inspector` no model `ChecklistSession`.
   - Implementar método `save()` em `User` para garantir relacionamento simétrico.
2. **Executar Migrations**:
   - Executar `python manage.py makemigrations` e `python manage.py migrate`.
3. **Atualizar Admin**:
   - Ajustar `CustomUserAdmin` para exibir `partner_user` e filtrar a lista de opções para apenas técnicos ativos (excluindo a si mesmo).
4. **Implementar Lógica de Criação de Checklist**:
   - Na view `checklist_start`, preencher `co_inspector` usando o `partner_user` do inspetor atual.
5. **Implementar Lógica de Isolamento**:
   - Na view `dashboard`, ajustar a QuerySet quando `user.is_technician` para filtrar por `Q(inspector=user) | Q(co_inspector=user)`.
6. **Atualizar Views de Exportação Excel**:
   - Ajustar `export_checklist_excel` para concatenar os dois inspetores.
   - Ajustar `export_dashboard_excel` para adicionar a coluna "Co-Inspetor".
7. **Atualizar os Templates**:
   - Atualizar `checklist_form.html` para exibir ambos se `session.co_inspector` existir.
   - Atualizar `dashboard.html` em todas as tabelas relevante para exibir ambos os inspetores.
8. **Criar e Executar Testes**:
   - Escrever testes automatizados no `core/tests.py` validando o isolamento de visibilidade e o preenchimento correto da dupla.
   - Rodar `python manage.py test`.

---

## 🧪 11. TESTES MANUAIS

1. **Configuração de Duplas**:
   - Login no Django Admin. Criar técnico A (Mecânico) e técnico B (Eletricista).
   - Definir técnico B como dupla do técnico A.
   - Verificar se o perfil do técnico B automaticamente passou a apontar para o técnico A.
2. **Criação de Checklist com Dupla**:
   - Login como técnico A. Iniciar uma inspeção.
   - Verificar se na tabela `ChecklistSession` no banco ou no Admin, o `co_inspector` é o técnico B.
   - Verificar se no cabeçalho da execução aparece "Inspetores: A (Mecânico) & B (Eletricista)".
3. **Visibilidade Restrita**:
   - Criar técnico C (Eletromecânico) sem dupla.
   - Técnico C inicia um checklist.
   - Fazer login como técnico C. Verificar se ele **NÃO** vê os checklists de A e B no histórico.
   - Fazer login como técnico A. Verificar se ele vê apenas os checklists onde consta como inspetor ou onde B consta como inspetor (sua dupla).
4. **Exportação Excel**:
   - Exportar checklist individual do turno de A e B e verificar cabeçalho com ambos.
   - Exportar consolidado e validar coluna "Co-Inspetor".

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

O agente deve entregar:
- Arquivos lidos
- Arquivos alterados
- Alterações feitas em cada arquivo
- Justificativa das decisões tomadas
- Resultado dos testes executados
