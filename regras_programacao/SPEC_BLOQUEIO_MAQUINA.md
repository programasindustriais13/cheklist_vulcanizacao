# 🧠 SPEC — Bloqueio de Seleção de Máquina já Inspecionada em Aguardo de Aprovação

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:**
  - `/checklist/start/` (View: `checklist_start`, Template: `checklist_start.html`)
- **Contexto(s):**
  - Execução de Checklist (Inicialização)
- **Perfil(s) afetados:**
  - Eletricista, Mecânico, Eletromecânico (Técnicos/Inspetores), Analistas, Diretores, Superusuários (qualquer perfil que possa criar um checklist).

---

## ❗ 2. PROBLEMA ATUAL

Ao iniciar um novo turno ou checklist, o técnico pode selecionar acidentalmente no dropdown de máquinas uma prensa que ele acabou de inspecionar no mesmo turno, cujo checklist ainda está aguardando aprovação pelo líder. O sistema aceita a criação de uma nova sessão para a mesma máquina, gerando duplicidade de dados e inconsistências.

---

## 🎯 3. OBJETIVO

Impedir que um usuário logado possa iniciar ou selecionar uma máquina caso ele já tenha enviado um checklist para essa mesma máquina e este ainda esteja com o status de pendente (`AGUARDANDO_LIDER` ou `REPROVADO_LIDER`).

Para atingir isso:
1. Filtrar o queryset de máquinas no formulário de início de checklist (`ChecklistStartForm`) para excluir máquinas que possuam checklists pendentes do próprio usuário logado.
2. Validar no backend (método `clean()` do formulário) para impedir o envio caso o usuário tente burlar a interface (ex: enviando um ID de máquina bloqueada via requisição POST modificada).

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Possíveis arquivos:
- `core/forms.py` (para alterar `ChecklistStartForm` e implementar o filtro de queryset e a validação `clean()`)
- `core/views.py` (para passar o `request.user` ao instanciar o formulário na view `checklist_start`)

---

## 🚫 5. FORA DE ESCOPO

- Não alterar outras views ou templates.
- Não refatorar a máquina de estados para outros fluxos.
- Não alterar a tabela `Machine` no banco de dados (nenhuma migração é necessária no model `Machine`, pois a lógica é puramente de filtragem de consultas e validação).

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

⚠️ Esta implementação DEVE seguir o `constitution.md`:
- Apenas 1 ambiente virtual (`venv`).
- Apenas 1 projeto Django (`checklist_system`).
- Apenas 1 app principal (`core`).
- Reutilizar código existente.
- Validar permissões no backend.
- Usar ORM do Django.
- CSRF Token mantido em formulários.

---

## ⚙️ 7. REGRAS DE NEGÓCIO

1. Ao carregar a página de inicialização do checklist (`/checklist/start/`), a lista de máquinas selecionáveis deve conter apenas máquinas que **não** possuam um checklist do próprio usuário logado nos status `AGUARDANDO_LIDER` ou `REPROVADO_LIDER`.
2. No método `clean` do formulário `ChecklistStartForm`, se o usuário submeter uma máquina com checklist pendente feito por ele nos status `AGUARDANDO_LIDER` ou `REPROVADO_LIDER`, o formulário deve falhar com a mensagem: *"Você já realizou uma inspeção nesta máquina que está aguardando a aprovação do Líder."*

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Máquinas com checklists pendentes (`AGUARDANDO_LIDER` ou `REPROVADO_LIDER`) do técnico logado **não aparecem** no dropdown da tela `/checklist/start/`.
- [ ] Submeter manualmente ou via POST direto uma máquina bloqueada retorna o erro de validação *"Você já realizou uma inspeção nesta máquina que está aguardando a aprovação do Líder."*.
- [ ] Máquinas em outros status (como `APROVADO` ou `REPROVAR_FINAL_REFAZER` ou checklists de outros inspetores) **aparecem** normalmente e podem ser selecionadas.
- [ ] Testes automatizados cobrindo esse comportamento passam com sucesso.

---

## ⚠️ 9. RISCOS

- **Instanciação do Form em outros locais:** Se o formulário `ChecklistStartForm` for instanciado em testes ou scripts sem passar o parâmetro `user`, a inicialização não deve falhar (deve aceitar `user=None` e manter o comportamento padrão de listar todas as máquinas).

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

1. **Alterar `core/forms.py`**:
   - Modificar `ChecklistStartForm.__init__` para aceitar um argumento nomeado opcional `user`.
   - Se `user` for fornecido:
     - Obter IDs das máquinas com checklists do usuário logado nos status `AGUARDANDO_LIDER` ou `REPROVADO_LIDER`.
     - Definir `self.fields['machine'].queryset = Machine.objects.exclude(id__in=blocked_ids).order_by('name')`.
     - Armazenar `self.user = user`.
   - Implementar o método `clean` para verificar se a máquina selecionada possui um checklist pendente do mesmo usuário. Em caso positivo, levantar `forms.ValidationError` para o campo `machine`.
2. **Alterar `core/views.py`**:
   - Atualizar a view `checklist_start` para passar `user=request.user` ao instanciar `ChecklistStartForm` (em requisições GET e POST).
3. **Escrever testes em `core/tests.py`**:
   - Criar teste verificando que a máquina some do dropdown quando há checklist pendente.
   - Criar teste validando que tentar submeter via POST a máquina bloqueada retorna erro de formulário.
4. **Rodar testes automatizados**:
   - Executar `python manage.py test`.

---

## 🧪 11. TESTES MANUAIS

1. Logar com um inspetor (ex: Eletricista).
2. Criar um checklist para a `Máquina A`.
3. Preencher todos os campos e finalizar (passa para o status `AGUARDANDO_LIDER`).
4. Ir para `/checklist/start/` de novo e verificar que a `Máquina A` **não aparece** na lista de opções.
5. Criar outra máquina `Máquina B` (ou usar outra existente), iniciar o preenchimento, e garantir que a `Máquina B` aparece normalmente.
6. Tentar burlar a requisição submetendo a `Máquina A` e confirmar que o erro de segurança *"Você já realizou uma inspeção nesta máquina que está aguardando a aprovação do Líder."* é exibido.

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

(Será preenchido no relatório final após a execução)
