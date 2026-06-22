# 🧠 CONSTITUIÇÃO.md — Sistema de Checklist de Vulcanização

## 🎯 OBJETIVO DO SISTEMA

Sistema Django para gestão do checklist de início de turno de prensas de vulcanização:
- **Dashboard:** Painel principal com histórico de sessões, KPIs e fila de aprovação.
- **Execução de Checklist:** Fluxo guiado de inspeção item a item com estado máquina (Iniciar → Pausar → Retomar → Finalizar).
- **Fluxo de Aprovação:** Aprovação em dois níveis — Líder de Turno → Analista/Diretor.
- **Exportação Excel:** Relatórios detalhados por sessão e consolidado geral.
- **Cadastro de Máquinas:** CRUD de máquinas disponíveis para inspeção.
- **Aprovação de Usuários:** Novos cadastros ficam inativos até aprovação por Analista/Diretor.

O sistema deve ser:
- Seguro e auditável (cada transição de estado registrada no `ChecklistTimelineLog`).
- Consistente e resiliente para uso em tablets compartilhados no chão de fábrica.
- Compatível com produção (MySQL) e desenvolvimento local (SQLite).
- De fácil usabilidade para técnicos e inspetores (UI limpa, termos simples, em pt-br).

---

# 🚨 REGRA GLOBAL CRÍTICA (OBRIGATÓRIA)

## ❗ Execução Controlada de Agentes
- Apenas **UM fluxo de implementação ativo por vez**.
- Subagentes NÃO podem:
  - Criar múltiplos ambientes virtuais.
  - Criar cópias ou duplicatas do projeto.
  - Criar ou duplicar aplicações Django.

### ✅ Estrutura obrigatória:
- Apenas **1 ambiente virtual (`venv`)** na raiz do projeto.
- Apenas **1 projeto Django** (`checklist_system`).
- Apenas **1 app principal** (`core`) contendo toda a lógica de negócio.
- Apenas **1 base de código ativa**.

---

# 🏗️ ARQUITETURA

- Seguir o padrão **Django MVT** (Model-View-Template).
- Separação clara de responsabilidades:
  - `core` — app principal com Models, Views, Forms, Templates e lógica de negócio.
  - `checklist_system` — configurações do projeto Django (`settings.py`, `urls.py` raiz).

### Estrutura de diretórios:
```
checklist_git/
├── checklist_system/      # Configurações (settings, urls raiz, wsgi/asgi)
├── core/                  # App principal
│   ├── models.py          # User, Machine, ChecklistSession, ChecklistTimelineLog, ChecklistItemValue
│   ├── views.py           # Todas as views (auth, CRUD, checklist, aprovação, exportação)
│   ├── forms.py           # RegisterForm, MachineForm, ChecklistStartForm
│   ├── urls.py            # Rotas do app core
│   ├── checklist_items.py # Definição estática dos itens do checklist por seção
│   ├── templates/core/    # Todos os templates HTML
│   └── static/            # Arquivos estáticos (CSS, JS, imagens)
├── venv/                  # Ambiente virtual (NÃO versionar)
├── manage.py
├── db.sqlite3             # Banco de dev (NÃO versionar)
├── requirements.txt
└── Instrucoes.txt         # Registro de alterações e comandos úteis
```

### Regras:
- ❌ **PROIBIDO** lógica de negócio ou queries SQL diretas em templates.
- ❌ **PROIBIDO** lógica de negócio pesada ou decisões complexas diretamente nas views.
- ✅ Lógica deve ficar em:
  - **Models** (propriedades auxiliares, regras simples).
  - **Forms** (validações e salvamento customizado).
  - **Views** (orquestração do fluxo, transições de estado).

---

# 🔐 SEGURANÇA E PERMISSÕES (PRIORIDADE MÁXIMA)

- **Nunca confiar em dados do frontend.** Sempre validar permissões no backend.
- Toda view ou action sensível deve ser protegida com decorators:
  - `@login_required` — Obrigatório em toda view privada.
  - `@machine_management_required` — Acesso a CRUDs de máquinas e aprovação de usuários (Analista, Diretor, superusuário).
  - `can_export_excel` (propriedade do User) — Controla acesso à exportação Excel.
  - `can_create_checklist` (propriedade do User) — Bloqueia Líderes de iniciarem checklists.

### Perfis de usuário (via `User.specialty`):
| Specialty       | Pode iniciar checklist | Pode aprovar (Líder) | Pode revisar (Analista/Diretor) | Pode exportar Excel |
|-----------------|----------------------|---------------------|---------------------------------|---------------------|
| Eletricista     | ✅                   | ❌                  | ❌                              | ❌                  |
| Mecânico        | ✅                   | ❌                  | ❌                              | ❌                  |
| Eletromecânico  | ✅                   | ❌                  | ❌                              | ❌                  |
| Lider           | ❌                   | ✅                  | ❌                              | ❌                  |
| Analista        | ✅                   | ❌                  | ✅                              | ✅                  |
| Diretor         | ✅                   | ❌                  | ✅                              | ✅                  |

### Obrigatório:
- CSRF Token em todos os formulários POST.
- Validar `request.user` contra o `session.inspector` antes de permitir edição.
- Filtros de query robustos para impedir acesso cruzado entre usuários.
- Usuários recém-cadastrados criados com `is_active=False` — aguardam aprovação manual.

---

# 🗄️ BANCO DE DADOS

## Compatibilidade obrigatória:
- **SQLite** (ambiente de desenvolvimento local — `db.sqlite3`).
- **MySQL** (ambiente de produção / servidor real).

### Regras:
- ❌ **Evitar features específicas de banco** que não sejam compatíveis entre SQLite e MySQL.
- ✅ Usar **ORM do Django sempre** para garantir portabilidade.
- ❌ Não usar SQL puro, `.extra()` ou métodos obsoletos.
- **Campos opcionais:** Novos campos em models existentes devem ter `null=True, blank=True` ou `default` definido para não quebrar registros antigos.
- Toda alteração de schema deve gerar migration via `python manage.py makemigrations` antes de aplicar com `migrate`.

---

# ⚙️ REGRAS DE NEGÓCIO CRÍTICAS

## 1. Máquina de Estados do Checklist (`ChecklistSession.status`)

```
NOT_STARTED → IN_PROGRESS → PAUSED ⇄ IN_PROGRESS → AGUARDANDO_LIDER
                                                         ↓          ↓
                                                      APROVADO   REPROVADO_LIDER
                                                                     ↓          ↓
                                                                  APROVADO   REPROVAR_FINAL_REFAZER
                                                                                    ↓
                                                                               IN_PROGRESS (reaberto)
```

Transições válidas:
- `NOT_STARTED` → `IN_PROGRESS`: ao iniciar (não usado atualmente, sessão nasce já `IN_PROGRESS`).
- `IN_PROGRESS` → `PAUSED`: ação `pause` (exige `pause_reason`).
- `PAUSED` → `IN_PROGRESS`: ação `continue`.
- `IN_PROGRESS` | `PAUSED` → `AGUARDANDO_LIDER`: ação `finalize` (todos os itens devem estar preenchidos; NCs exigem observação).
- `AGUARDANDO_LIDER` → `APROVADO`: decisão `approve` do Líder.
- `AGUARDANDO_LIDER` → `REPROVADO_LIDER`: decisão `reject` do Líder.
- `REPROVADO_LIDER` → `APROVADO`: decisão `approve` do Analista/Diretor.
- `REPROVADO_LIDER` → `REPROVAR_FINAL_REFAZER`: decisão `reject` do Analista/Diretor.
- `REPROVAR_FINAL_REFAZER` → `IN_PROGRESS`: ação `reopen` pelo inspetor original.

## 2. Auditoria de Ações
- Toda transição de estado deve gerar um registro em `ChecklistTimelineLog` com `session`, `user`, `action` e opcionalmente `pause_reason`.
- Actions válidas: `START`, `PAUSE`, `CONTINUE`, `FINISH`, `REOPEN`, `APPROVE_LIDER`, `REJECT_LIDER`, `APPROVE_ANALISTA`, `REJECT_ANALISTA`.

## 3. Controle de Checklist Ativo
- Um inspetor só pode ter **UMA** sessão com status `IN_PROGRESS` por vez.
- Se tentar iniciar outro, é redirecionado para o checklist ativo com mensagem de aviso.

## 4. Finalização
- Ao finalizar (`finalize`): todos os itens devem ter status (`C` ou `NC`). Itens `NC` obrigam `observations` preenchidas.
- Erros de validação são exibidos na tela sem perder o progresso já salvo.

## 5. Pausa por Inatividade (Timeout)
- O `django-session-security` monitora inatividade.
- Antes do logout automático, o JS chama `/timeout-pause/` (POST) para salvar e pausar o checklist ativo.
- Essa view busca o checklist pelo `request.user` — nunca aceitar `session_id` do cliente.

## 6. Itens do Checklist
- Definidos estaticamente em `checklist_items.py` (dicionário `CHECKLIST_ITEMS` com seções e listas de itens).
- Ao iniciar uma sessão, os itens são criados/populados no banco via `ChecklistItemValue`.
- As seções válidas são: `HIDRAULICA`, `PNEUMATICA`, `SISTEMA_VULCANIZACAO`, `SISTEMA_VAPOR`, `ESTRUTURA`, `ELETRICA`.

---

# 🎨 UI / UX

- Interface completamente em **Português Brasileiro (pt-br)**.
- Mensagens de erro claras e amigáveis para usuários no chão de fábrica (evitar termos técnicos e stacktraces).
- Utilizar Bootstrap para layout responsivo (tablets e desktops).
- Feedback visual obrigatório via `django.contrib.messages` para todas as ações do usuário.
- NCs (Não Conformidades) devem ser visualmente destacadas (cor diferenciada).

---

# 🧪 TESTES E VALIDAÇÃO

Antes de considerar qualquer alteração como concluída:
- Verificar funcionamento local em `/` (dashboard), `/checklist/start/`, `/checklist/<id>/`.
- Garantir que migrações foram geradas com segurança e não são destrutivas.
- Testar o fluxo completo: Login → Iniciar → Preencher → Pausar → Retomar → Finalizar → Aprovação Líder → Aprovação Analista.
- Testar com dados incorretos e em branco para validar exibição de erros.
- Rodar testes automatizados: `python manage.py test`.

---

# 📦 PROTOCOLO DE DOCUMENTAÇÃO (`Instrucoes.txt`)

- Toda alteração no código-fonte, novas rotas, novos models ou novas bibliotecas devem ser registradas de forma resumida e organizada no arquivo `Instrucoes.txt` na raiz do projeto.

---

# 🤖 ORQUESTRAÇÃO DE SUBAGENTES

1. **Subagente Arquiteto:** Lê o código atual, mapeia impacto e propõe plano mínimo de alteração (sem reescrever nem duplicar código).
2. **Subagente Backend:** Implementa apenas o plano aprovado, mantendo compatibilidade SQLite/MySQL.
3. **Subagente QA:** Valida contra regressões, duplicações de lógica, permissões e consistência geral. Roda os testes automatizados.