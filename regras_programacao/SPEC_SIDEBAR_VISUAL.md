# 🧠 SPEC — Refatoração de Layout (Sidebar) e Identidade Visual Pneus Freedom

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** Todas as páginas do sistema (via base layout `base.html`, página de login `login.html`, e as rotas de exportação para Excel `/checklist/<id>/export/` e `/dashboard/export/`).
- **Contexto(s):** Dashboard, Execução de Checklist, Fluxo de Aprovação, Fila de Auditoria, Exportação Excel, Cadastro de Máquinas, Aprovação de Usuários.
- **Perfil(s) afetados:** Todos os perfis (Técnicos/Inspetores, Líderes, Auditores, Analistas, Diretores, Superusuários).

---

## ❗ 2. PROBLEMA ATUAL

- O sistema utiliza uma barra de navegação (navbar) superior genérica.
- As cores principais do sistema utilizam paletas azuis padrão do Bootstrap e variáveis genéricas.
- Não há identidade visual da empresa (Pneus Freedom) integrada nas telas de login, navegação ou relatórios em Excel.
- As mídias e arquivos de mídia da empresa não estão configurados corretamente no `settings.py` e `urls.py`.

---

## 🎯 3. OBJETIVO

- **Substituição da Navbar por Sidebar**: Mover toda a navegação para um menu lateral (Sidebar) esquerdo, fixo e expansível em telas grandes (Desktop/Tablet landscape) e comportando-se como menu "hambúrguer" (offcanvas do Bootstrap) em smartphones/smart devices menores.
- **Nova Paleta Corporativa**: Adotar a identidade visual da Pneus Freedom:
  - **Cor Primária**: Amarelo (#eac532) com texto escuro para contraste.
  - **Cor Secundária**: Preto (#000000) e tons de cinza escuro para a Sidebar e contraste.
- **Integração das Logomarcas**:
  - Tela de login com a logo escura (`Untitled-1.png`) centralizada acima do formulário.
  - Topo da Sidebar com a logo dourada/amarela (`Untitled-2.png`).
  - Relatórios Excel exportados com a logo corporativa no cabeçalho e cabeçalhos formatados nas cores corporativas.
- **Configuração de Mídia**: Habilitar a correta exibição e carregamento de arquivos estáticos e de mídia no Django (`settings.py` e `urls.py`).

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Módulos:
- `checklist_system` (configurações)
- `core` (app principal, templates, estáticos)

### Arquivos a serem modificados:
- `checklist_system/settings.py` (Adicionar `MEDIA_URL` e `MEDIA_ROOT`)
- `checklist_system/urls.py` (Adicionar suporte a servir arquivos de mídia no desenvolvimento)
- `core/static/core/style.css` (Atualizar paleta de cores corporativa, adicionar estilos do sidebar e responsividade, botões customizados e tabela de relatórios)
- `core/templates/core/base.html` (Substituir o menu superior por sidebar responsivo offcanvas, ajustar layout geral do container de conteúdo principal)
- `core/templates/core/login.html` (Inserir logo acima do formulário de acesso)
- `core/views.py` (Atualizar as funções `export_checklist_excel` e `export_dashboard_excel` para incluir a logomarca da empresa e aplicar estilo corporativo amarelo e preto)

---

## 🚫 5. FORA DE ESCOPO

- Não modificar nenhuma lógica de controle de acesso (RBAC), nem alterar a máquina de estados do checklist.
- Não reescrever exibições ou criar novos models no banco de dados.
- Não alterar dependências de terceiros sem necessidade (usaremos openpyxl e Pillow que já estão instalados).

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

- ❌ Não duplicar código nem lógica.
- ❌ Não criar novo projeto ou ambiente virtual.
- ✅ Utilizar ORM do Django.
- ✅ Garantir que as permissões dos perfis (`User.specialty` e helpers) sejam preservadas na renderização do menu lateral.
- ✅ Testar compatibilidade tanto com SQLite quanto com MySQL.

---

## ⚙️ 7. REGRAS DE NEGÓCIO

- A Sidebar deve exibir links dependendo estritamente do perfil do usuário autenticado:
  - **Início**: Para todos, exceto perfil 'Auditor'.
  - **Dashboard Analítico**: Visível apenas para Analista, Diretor e Superusuário.
  - **Máquinas**: Visível apenas para Analista, Diretor e Superusuário.
  - **Fila de Auditoria / Histórico de Auditorias**: Visíveis para Auditor, Analista, Diretor e Superusuário.
  - **Novo Checklist**: Exibido como ação destacada para usuários com `can_create_checklist`.
  - **Aprovar Usuários**: Visível para Analista, Diretor e Superusuário.
- Tela de login exibe a logo escura (`Untitled-1.png`) centralizada.
- A Sidebar exibe a logo dourada (`Untitled-2.png`) com fundo escuro.
- O Excel exportado exibe a logo corporativa (redimensionada para altura de 60px) na célula A1, com a primeira linha formatada com preenchimento Preto e texto Amarelo corporativo (ou branco) e cabeçalhos em Amarelo (#eac532) com texto preto.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Sidebar renderizado no lado esquerdo em telas grandes.
- [ ] Sidebar se comporta como offcanvas (menu hambúrguer) em viewports menores que `768px`.
- [ ] Paleta de cores corporativa ativa no sistema (amarelo e preto/cinza escuro).
- [ ] Textos sobre fundo amarelo legíveis (cor preta/escura).
- [ ] Logomarca carregada corretamente na tela de login.
- [ ] Logomarca carregada corretamente na Sidebar.
- [ ] Arquivo Excel gerado inclui a logomarca no cabeçalho sem quebrar e com cores corporativas.
- [ ] Todos os testes automatizados passando (`python manage.py test`).

---

## ⚠️ 9. RISCOS

- **Quebra de layout responsivo**: Em telas menores, o conteúdo principal pode ficar imprensado ou cortado se a sidebar não se ocultar corretamente. Resolvido usando `.offcanvas-md` do Bootstrap 5 e grid responsivo.
- **Contraste de cores inadequado**: Texto em branco sobre fundo amarelo ou amarelo sobre branco. Garantido usando variáveis CSS e regras restritas de cor de texto (e.g. `.btn-primary-custom` com `color: #000000`).
- **Problema de carregamento da imagem no Excel**: Falha se o caminho da imagem no disco estiver incorreto ou se o Pillow falhar. Tratado com tratamento de exceção (`try/except`) e caminho absoluto derivado do `settings.MEDIA_ROOT`.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO

1. **Configuração**:
   - Ajustar `checklist_system/settings.py` para definir `MEDIA_URL` e `MEDIA_ROOT`.
   - Ajustar `checklist_system/urls.py` para servir arquivos de mídia durante o desenvolvimento.
2. **Estilização**:
   - Atualizar `core/static/core/style.css` com as cores corporativas da Pneus Freedom e classes CSS para o sidebar responsivo.
3. **Template Base**:
   - Modificar `core/templates/core/base.html` para incorporar o layout com Sidebar esquerda e offcanvas responsivo, ocultando a navbar superior.
4. **Template de Login**:
   - Atualizar `core/templates/core/login.html` inserindo a imagem da logo.
5. **Funções do Excel**:
   - Importar `openpyxl.drawing.image.Image` em `core/views.py`.
   - Modificar `export_checklist_excel` e `export_dashboard_excel` para carregar a logo de `settings.MEDIA_ROOT` e inseri-la formatada.
6. **Validação**:
   - Executar os testes unitários automatizados.
   - Realizar verificação manual e teste responsivo das páginas.

---

## 🧪 11. TESTES MANUAIS

1. Logar no sistema e verificar se o menu lateral aparece à esquerda em Desktop.
2. Redimensionar o navegador para modo Mobile (Smartphones) e verificar se a barra lateral some e surge o botão "hambúrguer" no topo que abre o menu lateral offcanvas.
3. Deslogar e verificar a logo na tela de Login.
4. Logar como Analista/Diretor e exportar um checklist individual e o histórico geral consolidado em Excel, validando a logo no cabeçalho e a paleta de cores.

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

Serão fornecidos no relatório final:
- Arquivos lidos
- Arquivos alterados
- Descrição detalhada de cada alteração
- Resultado dos testes automatizados e manuais
