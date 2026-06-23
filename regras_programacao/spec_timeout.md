# 🧠 SPEC — EXPIRAÇÃO ABSOLUTA DE SESSÃO E TIMEOUT (2 HORAS)

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** Todas as URLs do sistema (protegidas por autenticação), especificamente o endpoint `/timeout-pause/`.
- **Contexto(s):** Dashboard, Execução de Checklist, Controle Global de Sessão.
- **Perfil(s) afetados:** Todos os perfis que necessitam de login (Eletricista, Mecânico, Eletromecânico, Líder, Analista, Diretor, Superusuário).

---

## ❗ 2. PROBLEMA ATUAL

Atualmente, o sistema monitora a inatividade física (movimentação de tela/toques) usando a biblioteca `django-session-security`.
- Para o cenário de tablets compartilhados, esse monitoramento de inatividade física não garante a rotatividade e segurança dos acessos, pois um usuário pode manter a sessão aberta indefinidamente se houver movimentação ou toques contínuos, ou o tablet pode ficar travado com a sessão de um técnico anterior ativa.
- Precisamos mudar para uma expiração absoluta baseada no tempo de login (Absolute Session Timeout) de 2 horas.

---

## 🎯 3. OBJETIVO

- Mudar para um tempo de expiração absoluta de sessão de 2 horas (7200 segundos), independentemente de haver atividade ou não.
- Remover ou desativar o monitoramento de inatividade em segundo plano do `django-session-security`.
- Salvar automaticamente qualquer checklist em andamento (`IN_PROGRESS`) como `PAUSED` com a justificativa: `"Pausa automática: Fim do tempo de sessão logada (2h)"`.
- Remover a detecção de inatividade física no frontend e exibir um aviso discreto ou contador nos últimos 5 minutos de sessão.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos modificados:
- `checklist_system/settings.py` (Configuração do tempo de cookie da sessão, desativação do session-security)
- `checklist_system/urls.py` (Remoção da rota `session_security/` se necessário)
- `core/templates/core/base.html` (Remoção do script de inatividade física, inserção do temporizador discreto de tempo absoluto)
- `core/views.py` (Ajustar a justificativa do log de pausa em `timeout_pause_checklist`)
- `core/tests.py` (Adicionar testes automatizados para validar a expiração e o pause automático)

---

## 🚫 5. FORA DE ESCOPO

- Não refatorar a máquina de estados do checklist além da justificativa específica de pausa.
- Não alterar outras permissões de perfis de usuários.
- Não criar novos modelos de banco de dados.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

⚠️ Esta implementação DEVE seguir o `constitution.md`
- ❌ Não criar múltiplos ambientes.
- ❌ Não duplicar projetos ou apps.
- ❌ Não duplicar lógica existente.
- ✅ Reutilizar código existente.
- ✅ Validar permissões no backend.
- ✅ Usar ORM do Django.
- ✅ CSRF Token em todas as requisições de modificação de estado.
- ✅ Registrar transições no `ChecklistTimelineLog`.

---

## ⚙️ 7. REGRAS DE NEGÓCIO

1. **Expiração Absoluta:** O cookie de sessão deve durar exatamente 7200 segundos (`SESSION_COOKIE_AGE = 7200`).
2. **Sem Renovação por Requisição:** A sessão não deve ser revalidada/salva em cada clique (`SESSION_SAVE_EVERY_REQUEST = False`).
3. **Pausa Automática de Checklist:** Se o usuário tiver um checklist `IN_PROGRESS` e a sessão atingir o limite, a view `timeout_pause_checklist` deve ser chamada para pausar o checklist com a justificativa: `"Pausa automática: Fim do tempo de sessão logada (2h)"`.
4. **Contador de Exclusão:** Nos últimos 5 minutos da sessão, um aviso discreto deve ser exibido na tela mostrando os minutos/segundos restantes.
5. **Logout Seguro:** Expirado o tempo (ou 10 segundos antes do limite absoluto de 2h para garantir o processamento da requisição autenticada), o checklist é pausado via AJAX e o usuário é redirecionado para a página de logout.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] A sessão expira rigorosamente 2 horas após o login (absoluta).
- [ ] O frontend não exibe alertas baseados em movimentos do mouse/toques.
- [ ] Um contador de aviso surge na interface quando faltarem 5 minutos para a sessão expirar.
- [ ] Quando o tempo expira, o checklist em andamento é alterado para `PAUSED` e o log de auditoria registra a justificativa correta: `"Pausa automática: Fim do tempo de sessão logada (2h)"`.
- [ ] O usuário é redirecionado para a tela de login.
- [ ] Todos os testes automatizados existentes continuam passando, e novos testes passam com sucesso.

---

## ⚠️ 9. RISCOS

- **Exclusão prematura ou falha do Ajax:** Chamar a rota `/timeout-pause/` depois que o cookie já expirou no backend resultará em um erro `403 Forbidden` ou redirecionamento de login sem salvar o checklist.
  - *Mitigação:* O frontend acionará a rota de pausa 10 segundos antes do limite absoluto de 2 horas (ex: 7190s), garantindo que a requisição seja recebida com a sessão ainda válida.
- **Drift de relógio no cliente:** `setInterval` pode falhar/atrasar se o navegador suspender a aba.
  - *Mitigação:* Usar cálculo de data absoluta (`Date.now() + segundos_restantes * 1000`) para atualizar o contador a cada tick.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:

1. **Fase 1: Configurações Globais (settings.py)**
   - Configurar `SESSION_COOKIE_AGE = 7200`.
   - Configurar `SESSION_SAVE_EVERY_REQUEST = False`.
   - Remover `"session_security.middleware.SessionSecurityMiddleware"` de `MIDDLEWARE`.
   - Remover `"session_security"` de `INSTALLED_APPS`.
   - Remover configurações de inatividade `SESSION_SECURITY_*`.

2. **Fase 2: URLs do Sistema (checklist_system/urls.py)**
   - Remover a inclusão de urls de `session_security`.

3. **Fase 3: Backend (core/views.py)**
   - Ajustar `timeout_pause_checklist` para definir a justificativa correta: `"Pausa automática: Fim do tempo de sessão logada (2h)"`.

4. **Fase 4: Frontend (core/templates/core/base.html)**
   - Remover a inclusão de `session_security/all.html`.
   - Remover a escuta aos eventos `session_security_warn` e `session_security_expired`.
   - Implementar o novo temporizador absoluto usando `request.session.get_expiry_age`.
   - Exibir um aviso discreto (toast ou banner flutuante no canto inferior direito) a partir de 5 minutos antes da expiração.
   - Disparar o request AJAX de pausa automática e redirecionamento de logout 10 segundos antes do fim.

5. **Fase 5: Testes Automatizados (core/tests.py)**
   - Criar novos testes automatizados para verificar que a view `timeout_pause_checklist` realiza a pausa com a mensagem correta.

---

## 🧪 11. TESTES MANUAIS

1. Realizar login com usuário técnico.
2. Iniciar um novo checklist.
3. No console do desenvolvedor do navegador, alterar o valor de `secondsLeft` para `305` segundos para simular a chegada aos últimos 5 minutos.
4. Validar que o aviso discreto aparece na tela com contagem regressiva precisa.
5. Deixar os 5 minutos esgotarem (ou forçar `secondsLeft = 12` e aguardar os 2 segundos).
6. Validar que o checklist ativo foi pausado no banco de dados e que a justificativa do `ChecklistTimelineLog` é exatamente `"Pausa automática: Fim do tempo de sessão logada (2h)"`.
7. Validar que o usuário é redirecionado para a página de login.

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

Serão listados todos os arquivos modificados, as alterações específicas e o resultado da execução dos testes.
