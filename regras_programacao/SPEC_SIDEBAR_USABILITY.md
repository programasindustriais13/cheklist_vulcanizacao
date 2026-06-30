# 🧠 SPEC — Correções de Usabilidade no Sidebar (Desktop e Mobile)

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** Todas as páginas internas para usuários autenticados (herdam do layout `base.html`).
- **Contexto(s):** Navegação e Menu Lateral (Sidebar) em dispositivos Desktop, Tablets e Celulares.
- **Perfil(s) afetados:** Todos os perfis autenticados (Inspetor, Líder, Auditor, Analista, Diretor, Superusuário).

---

## ❗ 2. PROBLEMA ATUAL

- **Sidebar no Desktop**: A Sidebar se comporta como um elemento em fluxo que acompanha a altura do conteúdo principal. Em telas com listas ou dashboards longos, o botão "Sair" fica posicionado no rodapé da Sidebar, fazendo com que o usuário precise rolar toda a página principal até o fim apenas para conseguir deslogar.
- **Botão de Menu no Mobile**: O botão hambúrguer que abre o menu lateral na visão mobile está contido em um cabeçalho estático. Ao rolar a página para ler ou preencher o checklist, o cabeçalho e o botão sobem e somem da tela, exigindo que o usuário volte ao topo do site para navegar para outra seção.

---

## 🎯 3. OBJETIVO

- **Sidebar Desktop Fixa**: Fixar a Sidebar verticalmente na tela (`100vh`) com rolagem própria independente do conteúdo da página, empurrando o botão "Sair" sempre para o limite inferior da viewport, mantendo-o visível a todo momento.
- **Botão Hambúrguer Mobile Flutuante**: Transformar o botão de menu em um botão flutuante (`position: fixed`) com transparência parcial (`opacity: 0.6`) que se destaca e fica sempre acessível no canto superior esquerdo do celular, mudando para opacidade total (`1.0`) em estados de interação (`hover`, `focus`, `active`).

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos a serem modificados:
- `core/templates/core/base.html` (Mapear novas classes de layout e reposicionar o botão de menu mobile)
- `core/static/core/style.css` (Implementar os novos estilos de posicionamento, rolagem e botão flutuante)

---

## 🚫 5. FORA DE ESCOPO

- Não modificar rotas, models ou lógica de backend do Django.
- Não alterar as permissões de visibilidade dos links da Sidebar.
- Não alterar o comportamento do modal de timeout de inatividade.

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

- ❌ Não criar novo app ou novo venv.
- ❌ Não duplicar código ou estilos.
- ✅ Manter a semântica e tags do Bootstrap 5.
- ✅ Utilizar apenas caminhos estáticos existentes.

---

## ⚙️ 7. REGRAS DE NEGÓCIO

- A Sidebar deve ocupar `280px` de largura em telas desktop (min-width `768px`) e o conteúdo principal deve deslocar-se `280px` para a direita de forma fixa.
- O botão "Sair do Sistema" deve ficar sempre posicionado na parte inferior do sidebar visível.
- Caso o menu de navegação exceda a altura da tela, a área de links da Sidebar (`.sidebar-nav`) deve permitir rolagem vertical isolada (`overflow-y: auto`), enquanto a marca do topo e o logout do rodapé permanecem fixos.
- O botão mobile flutuante deve usar as cores de identidade visual (borda amarela `#eac532` e fundo preto `#000000`).

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] A Sidebar permanece fixa à esquerda no Desktop e não rola com o conteúdo principal.
- [ ] O botão "Sair do Sistema" está sempre visível no canto inferior esquerdo da tela em Desktop.
- [ ] Em dispositivos móveis, o botão de menu hambúrguer flutua no canto superior esquerdo com `opacity: 0.6`.
- [ ] O hover/touch no botão mobile altera a opacidade para `1.0` e inverte a cor (fundo amarelo, ícone preto).
- [ ] O clique no botão mobile flutuante abre a Sidebar offcanvas corretamente.
- [ ] Sem quebras de layout nas páginas internas de formulário, dashboard ou auditoria.

---

## ⚠️ 9. RISCOS

- **Sobreposição em formulários**: O botão flutuante mobile no canto esquerdo pode sobrepor textos ou botões de voltar de formulários.
  - *Mitigação*: Posicionar o botão com margens adequadas (`top: 15px; left: 15px;`) e definir transparência (`opacity: 0.6`) para que o conteúdo por baixo permaneça legível.
- **Duplicidade de scroll**: Rolagem na Sidebar e rolagem no conteúdo principal competindo.
  - *Mitigação*: Definir `overflow-y: auto` exclusivamente na área de navegação interna `.sidebar-nav`, mantendo a Sidebar externa sem rolagem geral.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO

### Passo 1: Ajustar base.html
1. Adicionar as classes CSS `.sidebar-fixed-desktop` ao container `.offcanvas-md` da sidebar.
2. Adicionar a classe `.main-content-wrapper` ao container principal do conteúdo à direita.
3. Mover o botão do menu lateral offcanvas para fora do header mobile em `base.html` e atribuir a classe `.mobile-menu-trigger`.
4. Simplificar o cabeçalho mobile (`Mobile Top Header Bar`) para conter apenas o logo e nome da Pneus Freedom centralizados.

### Passo 2: Ajustar style.css
1. Implementar `@media (min-width: 768px)` com regras para `.sidebar-fixed-desktop` e `.main-content-wrapper`.
2. Estilizar a rolagem da lista de navegação `.sidebar-nav` e customizar a barra de rolagem.
3. Definir regras do botão flutuante `.mobile-menu-trigger` com transição de opacidade.

### Passo 3: Testes de Regressão e Validação
1. Validar se os testes automatizados passam.
2. Testar manualmente os comportamentos responsivo e desktop.

---

## 🧪 11. TESTES MANUAIS

1. Logar no sistema como Técnico. Rolar a página de histórico (dashboard) longa e verificar se a Sidebar e o botão "Sair do Sistema" permanecem fixos.
2. Redimensionar para mobile. Rolar um checklist longo e confirmar que o botão hambúrguer no canto superior esquerdo permanece flutuando com transparência e abre a sidebar ao ser clicado.
3. Validar se o hover ou toque no botão do menu mobile altera a opacidade e inverte as cores.

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

Serão fornecidos ao final:
- Arquivos lidos e alterados.
- Lista objetiva com as mudanças exatas de CSS/HTML.
- Resultados dos testes.
