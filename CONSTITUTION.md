# CONSTITUTION.MD - DIRETRIZES DE DESENVOLVIMENTO SEGURO

Este documento define as regras fundamentais, restrições e boas práticas que TODO agente de IA ou desenvolvedor deve seguir rigorosamente ao dar manutenção ou criar novas funcionalidades neste projeto. O sistema está em PRODUÇÃO. Nenhum dado pode ser perdido ou corrompido.

---

## 1. PRINCÍPIO DA NÃO-DESTRUIÇÃO DE DADOS (CRÍTICO)
- **Proibido Destruir Modelos/Campos Existentes**: Você NUNCA deve remover campos de modelos (models.py) ou tabelas existentes que contenham dados de checklist, histórico ou usuários.
- **Migrações Seguras (Django Migrations)**: 
  - Ao adicionar novos campos, eles DEVEM possuir valores padrão (`default=...`) ou permitir valores nulos (`null=True`, `blank=True`) para não quebrar os registros já salvos no banco de dados de produção.
  - Nunca delete arquivos de migrações antigas da pasta `migrations/`.
- **Comandos Proibidos**: Comandos como `flush`, `reset_db`, `drop table` ou qualquer script de deleção em massa sem backup/filtro explícito são estritamente proibidos.

---

## 2. COMPATIBILIDADE E BACKUP DE CÓDIGO
- **Modificações Incrementais**: Altere o código de forma cirúrgica. Não reescreva arquivos inteiros do zero se puder apenas adicionar ou modificar as funções necessárias.
- **Preservação de Regras de Negócio**: As regras de permissão anteriores (Eletricista/Mecânico sem exportação, Líder sem criar checklist, fluxo de aprovação e bloqueio de novos usuários) devem ser mantidas e respeitadas em qualquer nova atualização.
- **Rollback Ready**: Todo código gerado deve ser modular para que, caso ocorra algum erro em produção, a alteração possa ser revertida facilmente sem impactar o restante do sistema.

---

## 3. SEGURANÇA E AMBIENTE DE PRODUÇÃO
- **Configurações Sensíveis**: Nunca exponha chaves secretas (`SECRET_KEY`), senhas de banco de dados ou credenciais em código aberto.
- **Acesso Local vs Produção**: Mantenha o suporte a múltiplos ambientes. O arquivo `settings.py` deve aceitar o `ALLOWED_HOSTS` configurado dinamicamente ou manter as permissões de rede local sem expor o sistema a riscos externos.
- **Testes Antes de Aplicar**: Sempre sugira os comandos de teste (`python manage.py check` ou testes unitários) antes de instruir o usuário a rodar migrações em produção.

---

## 4. FORMATO DE ENTREGA E EXPLICAÇÃO
- Sempre explique quais arquivos serão modificados antes de aplicar as alterações.
- Forneça logs claros ou instruções de comandos necessários (ex: `makemigrations`, `migrate`) após as alterações na estrutura do banco.
