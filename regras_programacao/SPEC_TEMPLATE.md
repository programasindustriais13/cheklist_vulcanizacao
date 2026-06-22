# 🧠 SPEC — [NOME DA FEATURE OU CORREÇÃO]

---

## 📌 1. CONTEXTO

Descreva rapidamente onde isso acontece no sistema:

- **URL(s) envolvidas:**
- **Contexto(s):** (Dashboard, Execução de Checklist, Fluxo de Aprovação, Exportação Excel, Cadastro de Máquinas, Aprovação de Usuários)
- **Perfil(s) afetados:** (Eletricista/Mecânico/Eletromecânico — Inspetor, Lider — Aprovador Turno, Analista/Diretor — Revisão Final, Superusuário)

---

## ❗ 2. PROBLEMA ATUAL

Descreva claramente o problema:

- O que está acontecendo hoje?
- O que está incorreto ou incompleto?
- Existe impacto em produção?

---

## 🎯 3. OBJETIVO

Descreva o resultado esperado de forma direta:

- O que deve passar a acontecer?
- Qual comportamento novo deve existir?

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

Liste o que PODE ser alterado:

### Possíveis arquivos:
- `core/models.py`
- `core/views.py`
- `core/forms.py`
- `core/urls.py`
- `core/checklist_items.py`
- `core/templates/core/`
- `core/static/`
- `checklist_system/settings.py`
- `checklist_system/urls.py`

### Possíveis módulos:
- `core` (models, views, forms, templates, urls)
- `checklist_system` (configuração global)

---

## 🚫 5. FORA DE ESCOPO

O que NÃO pode ser alterado:

- Não alterar funcionalidades não relacionadas ao problema
- Não refatorar o sistema inteiro
- Não criar novos apps sem justificativa forte
- Não alterar estrutura de banco sem migration adequada
- Não alterar o `venv` ou instalar dependências sem atualizar `requirements.txt`

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

Descrever regras específicas da feature:

Exemplo:
- Apenas o inspetor original pode editar o checklist (exceto Analista/Diretor/superusuário)
- Não pode finalizar sem todos os itens preenchidos
- Itens NC obrigam observação preenchida
- Transições de estado devem ser registradas no `ChecklistTimelineLog`

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

A tarefa só é considerada concluída se:

- [ ] Funcionalidade funciona conforme esperado
- [ ] Não quebrou funcionalidades existentes
- [ ] Permissões respeitadas por `User.specialty`
- [ ] Interface compreensível para usuário não técnico (termos em pt-br)
- [ ] Compatível com SQLite e MySQL
- [ ] Sem duplicação de dados ou lógica
- [ ] Testes automatizados passam (`python manage.py test`)

---

## ⚠️ 9. RISCOS

Identifique possíveis riscos:

- Quebra de sessões existentes no banco
- Conflito de IDs de formulário no DOM (quando há múltiplos modais)
- Inconsistência entre SQLite e MySQL
- Duplicação de registros no `ChecklistTimelineLog`
- Problemas de permissão com superusuário vs. specialty

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

⚠️ Deve ser definido ANTES de codar

### Passos:

1. Ler código atual relacionado (`models.py`, `views.py`, `forms.py`, templates)
2. Identificar onde alterar (mínimo de arquivos)
3. Definir mudanças mínimas necessárias
4. Implementar incrementalmente
5. Gerar e aplicar migrations se necessário
6. Rodar `python manage.py test`
7. Testar manualmente o fluxo completo

---

## 🧪 11. TESTES MANUAIS

Descreva passo a passo:

Exemplo para fluxo de checklist:

1. Login como inspetor (Eletricista/Mecânico)
2. Iniciar novo checklist em `/checklist/start/`
3. Preencher itens e pausar
4. Retomar e finalizar
5. Login como Líder e aprovar/reprovar em `/`
6. Login como Analista e revisar em `/`
7. Testar usuário sem permissão tentando acessar tela restrita
8. Testar exportação Excel

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

O agente DEVE informar ao final do processo:

### Arquivos lidos:
- lista de arquivos analisados

### Arquivos alterados:
- lista objetiva com caminho relativo

### Alterações feitas:
- o que mudou em cada arquivo

### Justificativa:
- por que cada alteração foi necessária

---

# 🤖 USO COM SUBAGENTES

## Ordem obrigatória:

### 1. Arquiteto
Deve:
- Ler código atual (`models.py`, `views.py`, `forms.py`, `urls.py`, templates afetados)
- Mapear impacto na máquina de estados e nos perfis de usuário
- Definir plano mínimo (quais arquivos alterar e o quê)

---

### 2. Backend
Deve:
- Implementar apenas o plano aprovado pelo Arquiteto
- Alterar somente o necessário
- Gerar migrations se houver alteração de models
- Não criar novo app nem novo projeto

---

### 3. QA
Deve:
- Rodar `python manage.py test`
- Validar:
  - Duplicações de lógica ou código
  - Permissões por specialty
  - Consistência da máquina de estados
  - Regressões nas demais funcionalidades

---

## 🚨 REGRA DE PARADA

Se detectar:

- Duplicação de código
- Múltiplos ambientes virtuais
- Múltiplos projetos ou apps Django desnecessários
- Implementação paralela fora do plano aprovado

➡️ PARAR imediatamente e corrigir antes de continuar

---

# 🧠 PRINCÍPIO FINAL

> "Alterar o mínimo possível para resolver o problema com segurança."

- Segurança > velocidade
- Clareza > complexidade
- Consistência > criatividade