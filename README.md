# 💼 Sistema Financeiro Pessoal e MEI

Bem-vindo ao **Sistema Financeiro Pessoal e MEI**! Este projeto foi cuidadosamente desenvolvido para resolver um problema real: **a dificuldade de gerenciar finanças pessoais e empresariais de forma simples e eficiente**. Seja você um usuário comum ou um Microempreendedor Individual (MEI), este sistema foi pensado para **facilitar sua vida financeira** e trazer mais **organização e clareza** ao seu dia a dia. 🌟

---

## 🎯 Por Que Usar Este Sistema?

Sabemos que lidar com finanças pode ser desafiador, mas com o **Sistema Financeiro Pessoal e MEI**, você terá uma ferramenta poderosa e intuitiva para:

- **Organizar suas finanças** em um só lugar.
- **Acompanhar receitas e despesas** com facilidade.
- **Planejar o futuro financeiro** com metas claras e alcançáveis.
- **Evitar surpresas desagradáveis**, como ultrapassar o limite de faturamento MEI.

Este sistema foi projetado com **carinho e atenção aos detalhes**, para que você possa focar no que realmente importa: **alcançar seus objetivos financeiros**. 💖

---

## ✨ Funcionalidades Que Fazem a Diferença

### 🔑 Administração

- Gerencie usuários: aprove, edite ou exclua contas.
- Configure o sistema: habilite ou desabilite cadastros MEI e permissões de registro.
- Monitore logs de acesso para maior segurança.
- Gere relatórios administrativos detalhados.

### 🏦 Usuário Comum

- Controle suas contas bancárias: adicione, edite e exclua.
- Registre receitas e despesas de forma prática.
- Visualize relatórios financeiros mensais e anuais.
- Crie metas financeiras e acompanhe seu progresso.

### 📊 Usuário MEI

- Separe transações pessoais e empresariais.
- Faça upload de notas fiscais (PDF, JPG, JPEG ou PNG).
- Gere relatórios específicos para MEI com gráficos e tabelas.
- Receba alertas ao se aproximar do limite anual de faturamento de R$ 81.000,00.

### 🌟 Funcionalidades Gerais

- **Relatórios Personalizados**: Imprima ou exporte relatórios financeiros.
- **Modo Claro e Escuro**: Escolha o tema que mais combina com você.
- **Filtros Avançados**: Filtre transações por conta, categoria, tipo e presença de nota fiscal.
- **Gráficos Interativos**: Visualize dados financeiros com gráficos dinâmicos (requer internet para carregar via CDN).

---

## 🚀 Benefícios de Usar o Sistema

### Para Usuários Comuns:

- **Controle Total das Finanças**: Organize suas contas e transações de forma prática.
- **Planejamento Simplificado**: Crie metas financeiras e acompanhe seu progresso.
- **Relatórios Detalhados**: Entenda melhor seus gastos com gráficos e tabelas.

### Para Usuários MEI:

- **Gestão Empresarial Simplificada**: Controle receitas e despesas do CNPJ separadamente.
- **Organização de Notas Fiscais**: Mantenha tudo pronto para auditorias.
- **Relatórios Específicos**: Acompanhe o faturamento e evite ultrapassar limites legais.

### Para Todos:

- **Eficiência**: Pode ser executado em um computador caseiro, sem necessidade de servidores robustos.
- **Segurança**: Controle de acesso com login e senha, além de logs de auditoria.
- **Simplicidade**: Interface amigável e fácil de usar, mesmo para quem não tem experiência com sistemas financeiros.

---

## 🛠️ Como Usar

1. **Login Inicial**:
   - **Administrador**:
     - Usuário: `admin`
     - Senha: `admin123`
   - Após o login, configure o sistema e gerencie usuários.
2. **Usuários**:
   - Cadastre-se (se permitido) ou peça aprovação do administrador.
   - Comece a gerenciar suas contas, transações e metas.
3. **Relatórios**:
   - Acesse relatórios mensais ou anuais e imprima ou exporte para Excel.

---

## 🌐 Ambiente de Execução

⚠️ Este sistema foi projetado para **uso interno**, como em **máquinas locais** ou **redes intranet**. Ele **não é recomendado para exposição direta à internet**, mas precisa de conexão para carregar gráficos via **CDN**.

---

## 🔧 Pontos de Melhoria

Sabemos que todo sistema pode evoluir, e este não é diferente. Algumas áreas do código ainda podem ser **refatoradas** para melhorar a organização e a manutenção. Estamos comprometidos em tornar o sistema cada vez mais eficiente e robusto com o tempo. 💡

---

## 📜 Licença

Este projeto será licenciado sob a [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), permitindo que você o utilize e adapte conforme suas necessidades, com total transparência e liberdade.

---

## 📥 Como Baixar e Instalar

Siga os passos abaixo para configurar o **Sistema Financeiro Pessoal e MEI** no seu ambiente local:

1. **Clone o Repositório**:

   ```bash
   git clone https://github.com/jonathan-laco/finance-managerV1.git
   cd finance-managerV1
   ```

2. **Crie e Ative um Ambiente Virtual**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instale as Dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Banco de Dados**:
   - O projeto já vem configurado com o **SQLite** como banco de dados padrão.
   - O script `seed.py` será executado automaticamente na primeira inicialização para popular o banco com dados iniciais.

---

## 🖥️ Executando o Sistema

### Modo Desenvolvimento

Para rodar o sistema em modo de desenvolvimento, utilize o comando:

```bash
python run.py
```

### Modo Produção

Para rodar o sistema em produção, utilize o **Waitress** (servidor WSGI para Python). Certifique-se de que o Waitress está instalado:

```bash
pip install waitress
```

Em seguida, execute o sistema com:

```bash
waitress-serve --port=8080 run:app
```

### No Linux

No Linux, você pode usar o **Gunicorn** como alternativa ao Waitress. Instale o Gunicorn:

```bash
pip install gunicorn
```

E execute o sistema com:

```bash
gunicorn -w 4 -b 0.0.0.0:8080 run:app
```

---

##Desenvolvido com ❤️ para transformar a maneira como você gerencia suas finanças. Experimente e veja como é fácil alcançar seus objetivos financeiros com o **Sistema Financeiro Pessoal e MEI**! 🌟

**Desenvolvido por Jonathan Laco**

## 🎥 Demonstração do Projeto

Confira a demonstração do **Sistema Financeiro Pessoal e MEI** no YouTube:

[![Demonstração do Projeto](https://img.youtube.com/vi/Ja-9q4DmsPk/0.jpg)](https://youtu.be/Ja-9q4DmsPk)
