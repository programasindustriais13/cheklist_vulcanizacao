# 🧠 SPEC — Correção de Layout: Sobreposição do Botão e Logo no Sidebar (Desktop)

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** Todas as páginas internas para usuários autenticados (herdam de `base.html`).
- **Contexto(s):** Dashboard, Execução de Checklist, Fluxo de Aprovação, Fila de Auditoria, Cadastro de Máquinas, Aprovação de Usuários (toda a navegação interna do sistema).
- **Perfil(s) afetados:** Todos os perfis autenticados (Inspetor, Líder, Auditor, Analista, Diretor, Superusuário).

---

## ❗ 2. PROBLEMA ATUAL

- Na visão desktop (PC), o botão de menu flutuante mobile (`.mobile-menu-trigger`) continua visível devido ao uso de `display: flex !important;` na classe global no CSS, que sobrepõe a classe de visibilidade do Bootstrap `d-md-none`.
- Como resultado, este botão hambúrguer é posicionado de forma absoluta/fixa exatamente em cima da logomarca da empresa (`Untitled-2.png`) no cabeçalho do sidebar, cobrindo-a, prejudicando a identidade visual e a usabilidade.

---

## 🎯 3. OBJETIVO

- Ocultar o botão flutuante mobile (`.mobile-menu-trigger`) na visão desktop (PC/resoluções >= 768px).
- Adicionar e posicionar corretamente um botão de menu (hambúrguer) dentro do cabeçalho da sidebar desktop (`sidebar-header-brand`), garantindo que a logomarca e o botão fiquem 100% visíveis, alinhados horizontalmente (lado a lado) e sem nenhuma sobreposição.
- Preservar estritamente o layout e comportamento do mobile (onde o botão flutuante e transparente funciona perfeitamente).

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos a serem modificados:
- `core/templates/core/base.html` (Reestruturar o cabeçalho desktop da sidebar para conter o botão de menu alinhado via Flexbox)
- `core/static/core/style.css` (Adicionar regras específicas de mídia para ocultar o botão flutuante no desktop e estilizar o novo botão do cabeçalho)

---

## 🚫 5. FORA DE ESCOPO

- Não alterar rotas do backend, views, models ou banco de dados.
- Não alterar as permissões de acesso ou links da Sidebar.
- Não modificar o comportamento ou layout responsivo na visão mobile (smartphones).

---

## 🔐 6. REGRAS OBRIGATÓRIAS (CONSTITUTION)

⚠️ Esta implementação DEVE seguir o `constitution.md`:
- ❌ Não criar novo projeto Django.
- ❌ Não criar novo venv.
- ❌ Não duplicar código ou estilos.
- ✅ Reutilizar código existente e estilos corporativos (amarelo `#eac532` e preto `#000000`).

---

## ⚙️ 7. REGRAS DE NEGÓCIO

- O botão flutuante `.mobile-menu-trigger` deve estar visível apenas em telas menores que `768px`.
- No desktop (telas >= `768px`), o cabeçalho da sidebar (`.sidebar-header-brand`) deve exibir a logomarca e o botão de menu (hambúrguer) lado a lado, alinhados horizontalmente e com margens/espaçamento adequados usando classes utilitárias do Bootstrap (Flexbox).
- O novo botão no desktop não deve colidir ou cobrir a logomarca.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Na visão desktop (PC), a logomarca e o botão de menu no cabeçalho da sidebar não se sobrepõem e estão 100% visíveis.
- [ ] O botão flutuante `.mobile-menu-trigger` é ocultado no desktop.
- [ ] Na visão mobile, o layout do botão flutuante transparente permanece inalterado e funcional.
- [ ] A reestruturação utiliza Flexbox (`d-flex justify-content-between align-items-center` ou similar) no desktop.
- [ ] Todos os testes automatizados passam (`python manage.py test`).

---

## ⚠️ 9. RISCOS

- **Regressão na visão mobile**: Qualquer alteração incorreta na classe `.mobile-menu-trigger` pode quebrar o layout mobile.
  - *Mitigação*: Isolar as alterações usando media queries específicas `@media (min-width: 768px)` e `@media (max-width: 767.98px)`.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:
1. **Analizar e Planejar**: Identificar os pontos exatos de colisão em `base.html` e `style.css`.
2. **Reestruturar o HTML (`base.html`)**:
   - Ajustar o container `.sidebar-header-brand` para usar `justify-content-between` e `align-items-center`.
   - Adicionar o botão de menu (hambúrguer) dentro deste container.
3. **Ajustar o CSS (`style.css`)**:
   - Adicionar media query para garantir que o `.mobile-menu-trigger` seja ocultado (`display: none !important`) em resoluções desktop (`>= 768px`).
   - Adicionar regras de estilização para o novo botão do cabeçalho no desktop (se necessário, para combinar com a identidade visual).
4. **Validar**:
   - Executar testes automatizados.
   - Realizar validação visual no desktop e no mobile.

---

## 🧪 11. TESTES MANUAIS

1. Logar no sistema e validar na visão desktop (PC) que a logo Pneus Freedom no topo do menu lateral está visível e ao lado dela há um botão de hambúrguer, ambos bem posicionados e sem sobreposição.
2. Confirmar que o botão flutuante de mobile não aparece no canto superior esquerdo da tela desktop.
3. Redimensionar para mobile (largura < 768px) e validar que o botão flutuante (opacidade 0.6) é exibido no canto superior esquerdo e abre o menu lateral offcanvas ao ser clicado.
4. Rolar a página no mobile e validar que o botão flutuante acompanha o scroll e não sofreu regressões.

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

Serão fornecidos no final:
- Arquivos lidos e alterados.
- Alterações detalhadas feitas nos arquivos.
- Resultados dos testes manuais e automatizados.
