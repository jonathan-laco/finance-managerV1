# Sistema de Gerenciamento Financeiro Pessoal

Um sistema completo para gerenciamento de finanças pessoais desenvolvido em Python com Flask, permitindo controle de contas bancárias, transações, categorias, relatórios detalhados e metas financeiras.

## Características

- **Gerenciamento de Contas Bancárias**: Cadastre e gerencie múltiplas contas bancárias
- **Controle de Transações**: Registre receitas e despesas com categorização
- **Categorização**: Organize suas transações em categorias personalizáveis
- **Dashboard**: Visualize resumos e gráficos da sua situação financeira
- **Relatórios**: Gere relatórios detalhados com filtros e exportação
- **Metas Financeiras**: Defina e acompanhe metas para seus objetivos financeiros
- **Tema Claro/Escuro**: Escolha entre tema claro ou escuro conforme sua preferência
- **Layout Personalizável**: Arraste e redimensione os cards do dashboard
- **Responsivo**: Interface adaptável para dispositivos móveis e desktop
- **Área Administrativa**: Gerenciamento de usuários e monitoramento do sistema

## Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 4
- **Banco de Dados**: SQLite (configurável para outros SGBDs)
- **Gráficos**: Chart.js
- **Interface**: AdminLTE 3
- **Ícones**: Font Awesome 5

## Requisitos

- Python 3.6+
- Pip (gerenciador de pacotes Python)
- Navegador web moderno

## Instalação

1. Clone o repositório:
\`\`\`bash
git clone https://github.com/seu-usuario/finance-manager.git
cd finance-manager
\`\`\`

2. Crie um ambiente virtual e ative-o:
\`\`\`bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
\`\`\`

3. Instale as dependências:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Execute o aplicativo:
\`\`\`bash
python run.py
\`\`\`

5. Acesse o sistema no navegador:
\`\`\`
http://localhost:5000
\`\`\`

## Usuário Administrador Padrão

O sistema cria automaticamente um usuário administrador com as seguintes credenciais:
- **Usuário**: admin
- **Senha**: admin123
- **Email**: admin@admin.com

Recomenda-se alterar a senha após o primeiro login.

## Funcionalidades

### Para Usuários Comuns

- **Dashboard**: Visualize resumo financeiro, gráficos e transações recentes
- **Contas Bancárias**: Gerencie múltiplas contas bancárias
- **Transações**: Registre receitas e despesas, com status (confirmada, pendente, cancelada)
- **Categorias**: Organize transações em categorias personalizáveis
- **Relatórios**: Gere relatórios detalhados com filtros e gráficos
- **Metas Financeiras**: Defina metas e acompanhe seu progresso

### Para Administradores

- **Dashboard Admin**: Visualize estatísticas gerais do sistema
- **Gerenciamento de Usuários**: Ative/desative usuários, redefina senhas
- **Logs de Acesso**: Monitore acessos ao sistema
- **Reset de Dados**: Possibilidade de resetar dados de usuários

## Uso do Sistema

1. **Login/Registro**: Crie uma conta ou faça login com suas credenciais
2. **Dashboard**: Visualize sua situação financeira atual
3. **Contas**: Adicione suas contas bancárias
4. **Transações**: Registre suas receitas e despesas
5. **Relatórios**: Analise seus gastos e receitas
6. **Metas**: Defina objetivos financeiros e acompanhe seu progresso

## Observações

- As metas financeiras não influenciam no saldo e não aparecem nos relatórios. Elas servem apenas para acompanhamento de objetivos.
- O sistema utiliza o fuso horário de São Paulo (UTC-3) para todas as operações de data e hora.
- O tema escuro/claro pode ser alternado através do botão na barra superior.
- O modo de tela cheia está disponível para melhor visualização.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Autor

Jonathan Laco
