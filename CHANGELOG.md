# Polly Gomides ESL Website - Changelog
**Data:** 15 de Junho de 2026  
**Status:** Concluído, Integrado e Pronto para Deploy

---

## 🛠️ Modificações Realizadas

### 1. Correção do Erro de Tela Branca (Localhost)
* **Problema:** O site renderizava uma página em branco no `localhost:8000` devido a um trecho corrompido de texto que havia sido colado no `<head>` do arquivo [index.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/index.html). O bug deixava a tag `<script>` do Tailwind CSS aberta e deletou as tags `</head>`, `<body>`, `<header>` e a tag de abertura do menu `<nav>`.
* **Solução:**
  * Removido o bloco de texto corrompido.
  * Reestruturadas as definições das cores customizadas da marca no `tailwind.config` (ex: `brand-orange`, `brand-darkGray`, `brand-lightGray`).
  * Restauradas as tags estruturais `</head>`, `<body>` e `<header>`.
  * Adicionado suporte ao estilo `.text-glow` na seção head.

### 2. Configuração do Repositório Git & GitHub
* **Problema:** A pasta do projeto não era um repositório Git e os arquivos não estavam no repositório GitHub da Polly Gomides.
* **Solução:**
  * Inicializado o repositório local com `git init`.
  * Configurados o nome (`Igor Gomides`) e e-mail de commit localmente para evitar problemas de autoria.
  * Criado o arquivo [.gitignore](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/.gitignore) para ignorar arquivos de cache/temporários do sistema (`*.swp`, `.DS_Store`, `node_modules/`).
  * Adicionada a URL remota HTTPS `https://github.com/igorgomides/pollygomides.git` como `origin`.
  * Renomeada a branch padrão para `main`.
  * Orientado o usuário na geração de um **Personal Access Token (PAT)** clássico do GitHub com permissão `repo` para autenticação segura na hora do push.

### 3. Integração com Banco de Dados via Google Sheets (Apps Script)
* **Problema:** Os formulários de inscrição e de contato eram apenas elementos visuais. Os cliques no botão enviar simulavam sucesso, mas os dados eram perdidos.
* **Solução:**
  * Adicionados atributos `name` a todos os campos dos formulários no HTML (necessário para serialização dos dados).
  * Atualizados os manipuladores de eventos em JavaScript no arquivo [index.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/index.html) (`handleEnrollSubmit` e `handleContactSubmit`) para capturar os dados via `FormData`.
  * Implementado o envio assíncrono via `fetch` direcionado ao atributo `action` de cada formulário.
  * Configurado o modo `mode: 'no-cors'` nas requisições para evitar bloqueios de redirecionamento HTTP gerados pelo Google Apps Script.
  * Adicionado suporte visual com estado temporário de **"Enviando..."** desabilitando o botão de envio para evitar duplicidade.
  * Escrito e fornecido o código em **Google Apps Script** para rodar diretamente na planilha do Google Sheets no Google Drive do usuário (sem depender de serviços pagos de terceiros).
  * Integrada a URL do Web App gerada no script (`/exec`) diretamente no atributo `action` de ambos os formulários no [index.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/index.html).

### 4. Área Administrativa Segura (admin.html)
* **Problema:** A Polly Gomides não tinha um painel administrativo para visualizar as inscrições dos alunos e contatos enviados pelo site sem ter que abrir diretamente a planilha de dados no Google Sheets.
* **Solução:**
  * Desenvolvido o arquivo [admin.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/admin.html) contendo um painel de controle premium com tema escuro (Dark Mode) e design responsivo.
  * Criada uma tela de login (Login Gate) protegida por senha baseada em Apps Script.
  * Implementados indicadores estatísticos em tempo real (total de envios, inscrições e contatos).
  * Criada uma barra de busca e filtros rápidos integrados.
  * Adicionado suporte às 11 colunas da planilha, mapeando os novos campos de fluxo de trabalho (`Payment Confirmed`, `Onboarding Completed`, `Follow-up Needed` e `Internal Notes`).
  * Implementados mini-indicadores (status badges) visuais na tabela para acompanhar o progresso de cada aluno de forma consolidada.
  * Desenvolvido suporte para **editar** os dados de acompanhamento diretamente do site: o painel agora envia atualizações (`action=update`) para o Google Apps Script, que edita a linha correspondente do Google Sheets em tempo real.
  * Adicionado um modal lateral (slide-over) para detalhar as informações de cada aluno, editar notas/status, com atalho para enviar e-mail de resposta instantaneamente.
  * Atualizado o código do Google Apps Script com suporte a leituras (`doGet`) e atualizações de linha (`doPost` com `action=update`).

### 5. Deploy no Railway
* **Status:** O site foi estruturado de forma 100% estática e limpa.
* **Comportamento no Railway:** Ao ler o repositório, o Railway (via Nixpacks/Railpack) identifica automaticamente o arquivo `index.html` na raiz do projeto e implanta um servidor **NGINX** otimizado para servir o site estático com o menor consumo de RAM possível.

### 6. Atualização de Cores (Navy Blue & Orange)
* **Mudança:** Substituição da cor escura carvão/preto original (`brand-darkGray: '#1F2421'`) por uma paleta de azul-marinho profundo (`brand-navy: '#0A192F'`).
* **Solução:**
  * No [index.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/index.html), renomeada a cor e atualizadas todas as classes estruturais (ex: `text-brand-navy`, `bg-brand-navy`).
  * No [admin.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/admin.html), configuramos a paleta `slate` no Tailwind CSS config para usar tons de azul-marinho (variando de `#061626` para o fundo principal até `#F0F4F8` para textos).
  * Atualizado o efeito glassmorphism (`.glass`) para usar azul-marinho translúcido (`rgba(16, 42, 67, 0.45)`).

### 7. Sistema de Review Visual & Feedback Loop
* **Problema:** Necessidade de permitir que a mentora (Polly) revise o site e envie sugestões de alteração de texto/imagens diretamente de forma visual.
* **Solução:**
  * **Modo Review Interativo:** Criado o modo review no front-end (`index.html?review=true`) com realces tracejados (`outline: 2px dashed #FF5A1F`) e fundo dinâmico ao passar o mouse.
  * **Captura de Cliques:** Cliques nos elementos interceptam a ação e abrem um modal com o seletor CSS do elemento (ex: `body > section#home h1`), o texto original, o novo texto sugerido e o comentário.
  * **Botão de Atalho:** Adicionado um link "Revisar Site" no topo direito do painel administrativo.
  * **Nova Aba Dedicada no Google Sheets:** Criamos a aba `Feedbacks` e atualizamos o Google Apps Script para salvar as sugestões nela de forma independente de inscrições e contatos.
  * **Compilador do Agente local ([apply_feedbacks.py](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/apply_feedbacks.py)):** Desenvolvido um script em Python que consome a API do Google Sheets, localiza exatamente os elementos no arquivo local via seletor CSS usando a biblioteca `bs4` (mapeando a linha e coluna de início e buscando a tag de fechamento por pilha), e aplica as alterações diretamente preservando a formatação original do arquivo.

### 8. Gestão Multi-Administradores & Trilha de Auditoria (Audit Trail)
* **Problema:** Necessidade de rastrear quem solicitou cada feedback e quem atualizou o status de CRM de cada aluno.
* **Solução:**
  * **Mapeamento de Senhas:** Atualizado o Apps Script para usar um dicionário `ADMINS` que mapeia senhas específicas para nomes (ex: `Igor` ou `Polly`).
  * **Dropdown de Revisor:** Adicionado no widget de review do site um seletor dropdown permitindo alternar quem está revisando (com preenchimento automático a partir do admin).
  * **Colunas de Auditoria:** Criadas as colunas `Requested By` (Solicitado por) na aba de feedbacks e `Updated By` (Alterado por) em todas as abas. O Apps Script carimba o nome do admin na coluna correspondente sempre que uma mudança é efetuada.
  * **Exibição do Log:** O modal de visualização no [admin.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/admin.html) agora exibe no rodapé o nome de quem solicitou o feedback e de quem realizou a última alteração no CRM do registro.
  * **Resolução de Conflitos de Caracteres no Apps Script:** Criada a função de busca por aba normalizada (`getSheetNormalized`) que remove acentos e espaços de forma a ignorar erros de digitação de nomes de aba (como `Inscrições` vs `Inscricoes`).

### 9. Nova Localização e Política de Atualização do Showcase
* **Mudança:** Definição permanente da localização do portfólio/showcase fora do repositório da aplicação.
* **Solução:**
  * Atualizado o arquivo de configuração local [`.showcase_config.json`](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/.showcase_config.json) com o atributo `update_policy`.
  * Adicionada a instrução de atualização no [README.md](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/README.md) do site principal.
  * Documentada a política de atualização e vinculada de volta ao projeto no [README.md](file:///home/igor-gomides/Documents/Antigravity/MYPORTIFOLIO/showcase/README.md) do showcase externo.

### 10. Teste de Nível de Inglês (CEFR)
* **Solução:**
  * Criado o arquivo [quiz.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/quiz.html) com um teste interativo de nivelamento contendo 28 perguntas de múltipla escolha.
  * O teste avalia gramática, vocabulário e compreensão, exibindo o nível CEFR (A1 a C2) ao final de forma dinâmica.
  * Integração para envio do resultado completo para o WhatsApp da Polly (`+15195021481`) via redirecionamento pré-preenchido (sem exibir o número abertamente no site).
  * Envio automático dos dados do teste (Nome, E-mail, Telefone, Respostas corretas, Tempo de conclusão e Nível obtido) para a planilha "Nivelamentos" do Google Sheets.

### 11. Painel CRM & Google Sheets (Nivelamentos)
* **Solução:**
  * Modificado [admin.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/admin.html) adicionando uma aba de "Nivelamentos" para visualização e busca de todos os testes de nível submetidos pelos alunos.
  * Atualização da integração com o Google Sheets no painel admin para carregar dados das duas abas ("Contatos" e "Nivelamentos").
  * Atualizado o código em [google_apps_script.js](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/google_apps_script.js) para processar envios e retornos seguros do banco de dados na aba de Nivelamentos.

### 12. Fotos de Perfil & Mascote Base
* **Solução:**
  * Download via SMB da nova foto de perfil da Polly (`polly_profile.png`) a partir do Mac do usuário e integração no layout do site.
  * Download via SMB da imagem base do mascote (`Gemini_Generated_Image_pdw50fpdw50fpdw5.png`) para armazenamento no repositório.

### 13. Novo Logotipo com Mascote Integrado
* **Solução:**
  * Geração de um novo logotipo profissional (`polly_logo.jpg`) mesclando a identidade visual da Polly Gomides com a bonequinha de mascote gerada pela IA, onde ela aparece sentada acima do nome.
  * Substituição do logotipo em texto pelo novo logotipo em imagem no cabeçalho das páginas [index.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/index.html) e [quiz.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/quiz.html) com efeito de mesclagem visual (`mix-blend-multiply`).

### 14. Ajuste Visual do Logotipo (Tamanho, Posicionamento e Scroll)
* **Mudança:** Redimensionamento, reposicionamento e alinhamento do logotipo no cabeçalho das páginas [index.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/index.html) e [quiz.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/quiz.html).
* **Solução:**
  * **Aumento da Logo e do Cabeçalho:** Aumentamos o tamanho inicial da logo em 50% (passando de `h-20` (80px) para `h-36` (144px) no desktop, e de `h-16` (64px) para `h-32` (128px) no mobile). Acompanhando esse aumento, a barra de navegação no topo foi expandida para `h-40` (160px) no desktop e `h-36` (144px) no mobile.
  * **Alinhamento Centralizado com o Badge:** Aplicamos uma translação horizontal (`translate-x-20` correspondente a 80px) para que o centro do logotipo alinhe perfeitamente com o centro do badge de destaque "*Cohorts Open for Semester 2, 2026*".
  * **Controle Dinâmico no Scroll (Correção de Transbordo):** Adicionamos transições suaves no scroll. Quando a página é rolada, o cabeçalho encolhe para um tamanho compacto (`h-20` / `h-24`) e a logo reduz para `h-16` / `h-20`, removendo dinamicamente o deslocamento vertical (`translate-y-0`) para evitar que a logo ultrapasse a borda inferior do cabeçalho reduzido.
  * **Ajuste de Padding no Hero:** Expandimos o espaçamento superior da seção hero (`pt-44` / `md:pt-56`) para evitar a sobreposição com o cabeçalho inicial que ficou mais alto.
  
### 15. Novo Painel de Revisão IA Híbrido, Chat & Backups Automáticos
* **Problema:** A aplicação manual via CLI não permitia revisar e refinar as mudanças de forma fluida e corria o risco de timeouts ou estouro do limite de tokens ao reescrever o arquivo HTML de 92 KB inteiro a cada chamada de IA. Além disso, havia um desalinhamento de colunas no Sheets que gerava seletores não encontrados.
* **Solução:**
  * **Mapeamento de Planilha Corrigido:** O script agora lê o seletor CSS correto da coluna `original_text` e a nova sugestão de substituição da coluna `comments` (ou `suggested_text`), resolvendo as falhas de elementos não encontrados.
  * **Servidor Flask Backend ([server.py](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/server.py)):** Criado um servidor leve em segundo plano na porta `5001` (com suporte a fallback de porta) que mantém a sessão de chat ativa.
  * **Assistente IA no Admin Panel:** Adicionado o botão **"Assistente de IA"** na barra de navegação de [admin.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/admin.html) abrindo uma área em split-screen: chat interativo do lado esquerdo e um `<iframe>` contendo a página `index_preview.html` do lado direito.
  * **Processamento Rápido via JSON + BeautifulSoup:** Em vez de gerar o arquivo HTML inteiro pela API (o que causava timeouts), configuramos o Gemini `gemini-2.5-flash` para retornar apenas um objeto JSON com seletores e ações específicas. O servidor faz o merge das alterações em memória de forma imediata usando BeautifulSoup.
  * **Importação Local:** O botão "Importar Planilha" agora aplica os feedbacks instantaneamente via Python sem requisições de rede para a IA.
  * **Salvamento com Backup Duplo:** Ao aprovar visualmente as alterações, o servidor cria cópias históricas com timestamp do `index.html` original e do preview na pasta `backups/`, publica as mudanças oficiais e atualiza os feedbacks no Google Sheets.

### 16. Correção do Deploy de Produção (Railway) e Ajustes de Rotas
* **Problema:** A aplicação web em produção estava fora do ar com o erro *502 Bad Gateway* porque o Railway não instalava as dependências Python (Flask, requests, bs4) devido à falta do arquivo `requirements.txt`, e a rota do painel admin gerava erros de caminho relativo em determinados formatos de URL.
* **Solução:**
  * **requirements.txt:** Criado o arquivo de dependências contendo `Flask`, `requests` e `beautifulsoup4`.
  * **Procfile:** Criado o arquivo de declaração de processo `web: python3 server.py` para instruir o Railway sobre como executar o servidor.
  * **Rotas do Servidor:** Adicionada a rota `/admin` no [server.py](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/server.py) para servir a área de administração de forma limpa, com ou sem a extensão `.html`.
  * **Ajuste de Links:** Atualizados os links do botão "Revisar Site" em [admin.html](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/SITE/admin.html) de `index.html?review=true` para `/index.html?review=true` para garantir que o redirecionamento aponte sempre de forma absoluta à raiz do site, evitando quebras por caminhos relativos indesejados.
