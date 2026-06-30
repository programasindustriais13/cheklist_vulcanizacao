# 🧠 SPEC — PERFIL DE AUDITOR E CAMADA DE AUDITORIA GERENCIAL

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:**
  - `/` (View: `dashboard` - Redirecionamento para Auditor)
  - `/dashboard/` (View: `analytical_dashboard` - Bloqueada para Auditor)
  - `/machines/` (Máquinas - Bloqueada para Auditor)
  - `/checklist/start/` (Iniciar Checklist - Bloqueada para Auditor)
  - `/users/pending/` (Aprovar Usuários - Bloqueada para Auditor)
  - `/auditor/queue/` (Fila Geral de Inspeções - Nova URL)
  - `/auditor/checklist/<int:session_id>/` (Tela de Auditoria - Nova URL)
  - `/auditor/history/` (Histórico de Auditorias - Nova URL)
- **Contexto(s):** Dashboard, Controle de Acesso (RBAC), Nova Camada de Auditoria, Exportação de Relatórios.
- **Perfil(s) afetados:** Auditor (novo), Analista, Diretor, Líder, Mecânico, Eletricista, Eletromecânico.

---

## ❗ 2. PROBLEMA ATUAL

Hoje o sistema possui perfis operacionais e de liderança, mas não há um perfil focado em Auditoria com capacidade para auditar checklists finalizados ou em andamento e apontar divergências item a item sem interferir no fluxo padrão da máquina de estados do checklist.
- Falta de perfil "Auditor" na base de usuários.
- Falta de restrição de acessos específicos e telas para o Auditor.
- Falta de persistência de dados de auditoria (se o item divergiu, qual a observação do auditor, quem auditou e quando).
- Relatório de exportação de Excel não exibe informações de auditoria.

---

## 🎯 3. OBJETIVO

- Criar o perfil de usuário **'Auditor'** com restrições e permissões correspondentes.
- Bloquear o acesso do Auditor às telas operacionais, de gestão de máquinas, de início de checklist e de aprovação de usuários.
- Garantir que apenas perfis autorizados (Auditor, Analista, Diretor e Superusuário) possam ver telas e resultados de auditoria, bloqueando o acesso de Líderes e Técnicos.
- Adicionar campos de auditoria no `ChecklistSession` e `ChecklistItemValue` de forma segura (retrocompatível).
- Implementar 3 novas telas: Fila Geral de Inspeções, Tela de Execução da Auditoria (com possibilidade de apontar divergência por item + observação obrigatória), e Histórico de Auditorias Realizadas.
- Incluir as informações de auditoria na exportação de planilhas Excel.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Possíveis arquivos:
- `core/models.py` (Adicionar especialidade 'Auditor', campos no `ChecklistSession` e `ChecklistItemValue`)
- `core/views.py` (Novas views de auditoria, filtros, restrição de acesso e alteração na exportação do Excel)
- `core/urls.py` (Adicionar novas rotas para a auditoria)
- `core/templates/core/base.html` (Ajustar menus de navegação conforme o novo perfil)
- `core/templates/core/` (Novos arquivos: `auditor_queue.html`, `checklist_audit.html`, `auditor_history.html`)

---

## 🚫 5. FORA DE ESCOPO

- Não alterar a máquina de estados padrão (`ChecklistSession.status`).
- Não alterar o fluxo padrão de preenchimento e finalização do checklist pelo técnico.
- Não alterar o fluxo padrão de aprovação de dois níveis pelo Líder e Analista/Diretor.
- Não alterar bibliotecas ou pacotes externos.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

- Seguir o padrão Django MVT.
- Não criar novo app ou projeto Django.
- Usar Django ORM para consultas (sem SQL direto).
- Garantir segurança e permissões no backend (decorators e validação de `request.user.specialty` ou `is_superuser`).
- Todas as rotas de auditoria devem ter verificação contra perfis não autorizados (Líder, Mecânico, Eletricista, Eletromecânico).
- Gerar migrações seguras (campos adicionados como nullable/default).

---

## ⚙️ 7. REGRAS DE NEGÓCIO

1. **Restrições do Auditor**:
   - Não pode iniciar checklist (bloquear `/checklist/start/`).
   - Não pode acessar dashboard geral (`/` e `/dashboard/`).
   - Não pode acessar CRUD de máquinas (`/machines/`).
   - Não pode acessar fila de aprovação de usuários (`/users/pending/`).
   - Se tentar acessar, deve ser bloqueado com mensagem de erro ou redirecionado.

2. **Visibilidade da Auditoria**:
   - Apenas Auditores, Analistas, Diretores e Superusuários têm acesso à Fila de Auditoria, Tela de Ação da Auditoria e Histórico de Auditoria.
   - Técnicos (Mecânico, Eletricista, Eletromecânico) e Líderes não visualizam os dados de auditoria, nem menus, nem rotas.

3. **Fluxo de Ação da Auditoria**:
   - Qualquer checklist do sistema pode ser auditado (independente de status operacional).
   - Tela de Ação exibe respostas originais do técnico em modo somente leitura (read-only).
   - Ao lado de cada item, há um botão/toggle para "Apontar Divergência".
   - Se marcar divergência (`auditor_is_divergent = True`), o campo de observação do auditor (`auditor_observation`) torna-se obrigatório.
   - Ao clicar em "Finalizar Auditoria", os dados são salvos no banco. O status de auditoria (`audit_status`) da sessão muda para:
     - `AUDITADO_CONFORME` (se nenhuma divergência foi apontada)
     - `AUDITADO_COM_DIVERGENCIA` (se pelo menos uma divergência foi apontada)
   - `audited_by` e `audited_at` devem ser gravados com o usuário atual e data/hora atual.

4. **Imutabilidade**:
   - O fluxo operacional do checklist segue inalterado.
   - Auditorias antigas são mantidas com `audit_status = 'NAO_AUDITADO'` por padrão.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Perfil 'Auditor' disponível no formulário de cadastro de novos usuários.
- [ ] Auditor autenticado é impedido de acessar `/`, `/dashboard/`, `/machines/`, `/checklist/start/`, `/users/pending/`.
- [ ] Auditor é redirecionado de `/` para `/auditor/queue/`.
- [ ] Usuários com perfis operacionais e líderes são bloqueados ao tentar acessar as telas de auditoria.
- [ ] Fila de Auditoria lista todos os checklists com filtros de Data, Máquina, Status operacional e Técnico.
- [ ] Ação de Auditoria permite salvar observações de divergência, validando campo obrigatório se houver divergência apontada.
- [ ] Tela de Histórico de Auditoria exibe as auditorias finalizadas e o resumo de divergências.
- [ ] Exportação consolidada e de sessão individual no Excel contêm colunas com dados da auditoria (status, auditor, observações).
- [ ] Migrações do banco geradas e aplicadas sem erros.
- [ ] Testes automatizados do sistema executam com sucesso.

---

## ⚠️ 9. RISCOS

- **Quebra de compatibilidade em banco de dados**: Resolvido ao adicionar campos com default apropriado e `null=True, blank=True`.
- **Validação de obrigatoriedade no frontend vs backend**: Se o usuário burlar o JS e enviar uma divergência sem observação, o backend deve validar e retornar erro na tela de auditoria.
- **Redirecionamento infinito**: A rota principal `/` redirecionará o Auditor para `/auditor/queue/`, que por sua vez deve ser acessível por ele.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:

1. **Atualizar `core/models.py`**:
   - Adicionar `'Auditor'` em `User.SPECIALTY_CHOICES`.
   - Adicionar campos `audit_status`, `audited_by`, `audited_at` em `ChecklistSession`.
   - Adicionar campos `auditor_is_divergent`, `auditor_observation` em `ChecklistItemValue`.
   - Gerar e aplicar migrações: `python manage.py makemigrations` e `python manage.py migrate`.

2. **Atualizar `core/views.py`**:
   - Adicionar validações de perfil para Auditor.
   - Bloquear acesso a rotas restritas para o Auditor (adicionar validação ou decorator).
   - Modificar view `dashboard` para redirecionar o Auditor para `/auditor/queue/`.
   - Implementar `auditor_queue` (Fila Geral).
   - Implementar `checklist_audit` (Ação de auditoria, tratamento de formulário POST, validação de observação obrigatória).
   - Implementar `auditor_history` (Histórico de auditorias realizadas).
   - Atualizar views de exportação Excel para incluir as colunas de auditoria.

3. **Atualizar `core/urls.py`**:
   - Mapear novas rotas.

4. **Atualizar `core/templates/core/base.html`**:
   - Ajustar menus de navegação ocultando/exibindo conforme specialty do usuário.

5. **Criar Templates**:
   - `core/templates/core/auditor_queue.html`
   - `core/templates/core/checklist_audit.html`
   - `core/templates/core/auditor_history.html`

6. **Escrever testes unitários em `core/tests.py`** e executar suite de testes.

---

## 🧪 11. TESTES MANUAIS

1. Cadastrar um usuário com perfil 'Auditor'.
2. Aprovar o novo usuário como administrador/analista.
3. Fazer login como Auditor e verificar se é redirecionado para a fila geral de auditoria `/auditor/queue/`.
4. Tentar acessar `/dashboard/`, `/machines/`, `/checklist/start/` direto via URL como Auditor e constatar bloqueio.
5. Iniciar um checklist com um técnico (Mecânico), pausar, retomar, finalizar.
6. Aprovar como Líder.
7. Entrar como Auditor, localizar o checklist na Fila Geral, abrir para Auditoria.
8. Apontar uma divergência em um item, tentar salvar sem observação (deve falhar e exibir erro).
9. Preencher a observação, apontar conformidade em outros itens e finalizar.
10. Verificar que o status mudou para `AUDITADO_COM_DIVERGENCIA`.
11. Acessar o Histórico de Auditorias como Auditor e constatar a presença do checklist auditado.
12. Fazer login como Técnico ou Líder, tentar acessar `/auditor/queue/` e verificar que o acesso é proibido.
13. Exportar relatório em Excel e verificar a presença das colunas de auditoria preenchidas corretamente.
