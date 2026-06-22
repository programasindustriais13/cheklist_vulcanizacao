# 🧠 SPEC — [EXEMPLO CONCLUÍDO] CORREÇÃO DO FLUXO DE PAUSA E RETOMADA DE CHECKLIST

> ⚠️ **Esta SPEC é um EXEMPLO de referência de uma tarefa já concluída.**
> Use-a como modelo de preenchimento ao criar novas SPECs a partir do `SPEC_TEMPLATE.md`.

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** `/checklist/<session_id>/`
- **Contexto(s):** Execução de Checklist
- **Perfil(s) afetados:** Eletricista, Mecânico, Eletromecânico (Inspetores)

---

## ❗ 2. PROBLEMA ATUAL

- **O que estava acontecendo?** Ao tentar retomar um checklist pausado (`action=continue`), o sistema exibia um erro 403 para usuários que não eram o inspetor original, mesmo quando eram Analistas ou Diretores com permissão explícita no backend.
- **O que estava incorreto?** A verificação de permissão na view `checklist_execute` bloqueava o acesso antes de verificar se o usuário tinha perfil de Analista/Diretor/superusuário.
- **Impacto em produção:** Analistas não conseguiam acompanhar ou corrigir checklists em andamento.

---

## 🎯 3. OBJETIVO

- A view `checklist_execute` deve permitir que Analistas, Diretores e superusuários visualizem e editem qualquer checklist em andamento ou pausado.
- O inspetor original sempre pode editar seu próprio checklist.
- Usuários com outros perfis devem receber `HttpResponseForbidden`.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos alterados:
- `core/views.py` (ajuste na verificação de permissão de `checklist_execute`)

### Módulos:
- `core`

---

## 🚫 5. FORA DE ESCOPO

- Não alterar a lógica de finalização ou aprovação.
- Não criar novos models ou migrations.
- Não refatorar o restante da view.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

- ✅ Validar permissões no backend via `User.specialty`
- ✅ Usar ORM do Django
- ❌ Não duplicar lógica de permissão
- ✅ Registrar transições no `ChecklistTimelineLog`

---

## ⚙️ 7. REGRAS DE NEGÓCIO

- O inspetor original sempre pode editar seu checklist (se `IN_PROGRESS` ou `PAUSED`).
- Analistas, Diretores e superusuários podem editar qualquer checklist editável.
- Todos os outros perfis (Líder) recebem `HttpResponseForbidden` ao tentar editar.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [x] Analista consegue acessar e editar checklist de outro inspetor
- [x] Inspetor continua conseguindo editar seu próprio checklist
- [x] Líder não consegue editar checklist (recebe 403)
- [x] Testes automatizados passam
- [x] Compatível com SQLite e MySQL

---

## ⚠️ 9. RISCOS

- Nenhum impacto em bank de dados (sem migrations necessárias).
- Risco de regressão no bloco de permissão — validar com testes.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO

### Passos executados:

1. Leu `core/views.py` — função `checklist_execute`
2. Identificou a verificação de `is_editable` e o bloco de permissão logo abaixo
3. Ajustou a condição para incluir `request.user.is_director or request.user.is_analyst or request.user.is_superuser`
4. Rodou `python manage.py test`

---

## 🧪 11. TESTES MANUAIS

1. Login como Analista → acessar `/checklist/<id>/` de outro inspetor → confirmar acesso permitido.
2. Login como Líder → acessar `/checklist/<id>/` de outro inspetor → confirmar `403 Forbidden`.
3. Login como inspetor original → confirmar edição normal.

---

## 📂 12. EVIDÊNCIAS

### Arquivos lidos:
- `core/views.py`
- `core/models.py`

### Arquivos alterados:
- `core/views.py`

### Alterações feitas:
- Condição `if request.user != session.inspector` expandida para excluir Analistas, Diretores e superusuários do bloqueio.

### Justificativa:
- A lógica anterior não contemplava os perfis que têm permissão de supervisão sobre qualquer checklist, causando falso `HttpResponseForbidden`.
