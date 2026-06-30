# 🧠 SPEC — Reposicionamento do Botão de Menu (Desktop)

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas:** Todas as páginas internas para usuários autenticados (que herdam de `base.html`).
- **Contexto(s):** Dashboard, Execução de Checklist, Fluxo de Aprovação, Fila de Auditoria, Cadastro de Máquinas, Aprovação de Usuários.
- **Perfil(s) afetados:** Todos os perfis autenticados (Eletricista, Mecânico, Eletromecânico, Líder, Auditor, Analista, Diretor, Superusuário).

---

## ❗ 2. PROBLEMA ATUAL

- Na visão desktop (PC), o botão de menu flutuante mobile (`.mobile-menu-trigger`) continua visível no topo esquerdo do site devido à ordem de regras no arquivo CSS. Por estar posicionado como `fixed` em `top: 8px; left: 15px;`, ele é renderizado diretamente sobre a logomarca da Pneus Freedom (que fica no topo esquerdo do sidebar).
- O cabeçalho do sidebar no desktop possui um segundo ícone/botão de menu no lado direito (`.desktop-menu-trigger`) sem borda circular, criando redundância e inconsistência de design.

---

## 🎯 3. OBJETIVO

- Mover o visual do botão de expansão do menu (a "bolinha" circular com os 3 traços) para o lado direito do cabeçalho da sidebar no Desktop, ocupando o lugar do ícone de três traços secundário (`.desktop-menu-trigger`), unificando a ação visual e liberando totalmente a área esquerda para a logomarca.
- Ocultar completamente o botão flutuante mobile (`.mobile-menu-trigger`) na visão desktop (PC/resoluções >= 768px).
- Preservar estritamente o layout e comportamento do mobile (onde o botão flutuante e transparente no topo esquerdo funciona perfeitamente).

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos a serem modificados:
- `core/templates/core/base.html` (Ajustar o botão `.desktop-menu-trigger` removendo classes utilitárias e estilos inline obsoletos)
- `core/static/core/style.css` (Mapear estilos do botão de menu mobile para o desktop no escopo correto de media queries, e isolar a estilização flutuante do mobile apenas para telas pequenas)

---

## 🚫 5. FORA DE ESCOPO

- Não alterar nenhuma rota backend, views, models ou banco de dados.
- Não alterar as permissões de acesso ou lógica de negócio do sistema.
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

- O botão flutuante `.mobile-menu-trigger` deve estar visível e posicionado de forma fixa (`top: 8px; left: 15px`) apenas em telas menores que `768px`.
- No desktop (telas >= `768px`), o cabeçalho da sidebar desktop deve exibir a logomarca no canto esquerdo e o botão de menu circular no canto direito, sem qualquer sobreposição.
- A ação e visual do botão no Desktop devem ser unificados em um único botão de ação principal alinhado à direita.

---

## 🧪 8. CRITÉRIOS DE ACEITAÇÃO

- [ ] Na visão desktop (PC), a logomarca e o botão de menu circular no cabeçalho da sidebar não se sobrepõem, e a logo está 100% legível na esquerda.
- [ ] O botão de menu no cabeçalho da sidebar desktop possui estilo circular idêntico ao mobile (fundo preto, borda amarela, ícone de 3 linhas), porém integrado e alinhado horizontalmente na direita.
- [ ] O botão flutuante `.mobile-menu-trigger` é ocultado no desktop.
- [ ] Na visão mobile, o layout do botão flutuante permanece inalterado, no topo esquerdo e funcional.
- [ ] Todos os testes automatizados passam (`python manage.py test`).

---

## ⚠️ 9. RISCOS

- **Regressão na visão mobile**: Qualquer alteração incorreta na classe `.mobile-menu-trigger` pode quebrar o layout mobile.
  - *Mitigação*: Isolar as regras de estilo de layout mobile usando a media query específica `@media (max-width: 767.98px)`.

---

## 🔍 10. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:
1. **Isolar estilos do botão mobile no CSS (`style.css`)**:
   - Mover a regra principal de `.mobile-menu-trigger` (incluindo `position: fixed`, `display: flex`, etc.) para dentro de uma nova media query `@media (max-width: 767.98px)`. Isso garante que o estilo flutuante e a exibição existam somente no mobile.
2. **Estilizar o botão de menu desktop (`style.css`)**:
   - Sob a media query `@media (min-width: 768px)`, adicionar regras para `.desktop-menu-trigger` e `.desktop-menu-trigger i` aplicando o estilo circular (borda amarela, fundo preto, hover integrado).
3. **Ajustar o HTML em `base.html`**:
   - Localizar `.desktop-menu-trigger` e seu ícone interno. Remover estilos inline e classes redundantes de preenchimento (`p-0 border-0 d-flex...`) para permitir a estilização completa via CSS.
4. **Validar**:
   - Executar os testes automatizados com `python manage.py test`.
   - Utilizar o subagente de navegação para obter capturas de tela e validar visualmente o comportamento em resoluções Desktop e Mobile.

---

## 🧪 11. TESTES MANUAIS

1. Logar no sistema e validar na visão desktop (PC) que a logo Pneus Freedom no topo do menu lateral está visível e livre.
2. Confirmar que no canto superior direito do cabeçalho da sidebar há um botão de menu circular com borda amarela e fundo preto.
3. Confirmar que o botão flutuante mobile não aparece no canto superior esquerdo da tela desktop.
4. Redimensionar para mobile e validar que o botão flutuante é exibido no canto superior esquerdo e abre o menu lateral offcanvas ao ser clicado, sem regressões.

---

## 📂 12. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

Serão fornecidos no final:
- Arquivos lidos e alterados.
- Alterações detalhadas feitas nos arquivos.
- Resultados dos testes manuais e automatizados.
