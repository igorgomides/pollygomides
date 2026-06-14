# Polly Gomides ESL Website - Changelog
**Data:** 14 de Junho de 2026  
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

### 4. Deploy no Railway
* **Status:** O site foi estruturado de forma 100% estática e limpa.
* **Comportamento no Railway:** Ao ler o repositório, o Railway (via Nixpacks/Railpack) identifica automaticamente o arquivo `index.html` na raiz do projeto e implanta um servidor **NGINX** otimizado para servir o site estático com o menor consumo de RAM possível.
