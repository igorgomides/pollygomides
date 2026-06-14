# Polly Gomides ESL - Website

Este é o repositório da Landing Page do curso de inglês e mentoria ESL de Polly Gomides (Semestre 2, 2026).

## 🚀 Como Executar Localmente
Para rodar o site em seu ambiente local de desenvolvimento, basta abrir um terminal na pasta do projeto e executar um servidor HTTP simples. Exemplos:

* **Usando Python:**
  ```bash
  python3 -m http.server 8000
  ```
* **Usando Node/NPM:**
  ```bash
  npx serve
  ```
Depois, acesse `http://localhost:8000` ou a porta gerada no seu navegador.

---

## 📊 Banco de Dados (Integração com Google Sheets)
O site envia os dados de inscrição e formulário de contato diretamente para o Google Sheets em tempo real.

* **Como funciona:** O código utiliza um **Google Apps Script** publicado como Web App para receber as requisições `POST` em formato JSON e adicionar novas linhas na planilha.
* **Onde atualizar a URL:** Caso precise alterar a planilha de destino, gere uma nova URL no Apps Script e substitua o atributo `action` nos formulários `#enroll-form` e `#contact-form` dentro do `index.html`.

---

## ☁️ Deploy (Railway)
O deploy é feito de forma automática ao realizar um `push` na branch `main` do GitHub. 
O Railway utiliza **Nixpacks** para identificar o arquivo `index.html` na raiz e configurar automaticamente um servidor leve **NGINX** para servir os arquivos estáticos de forma eficiente.

---

## ⚠️ Instruções para Assistentes de IA (AI Coding Assistants)
* **Importante:** Sempre que realizar modificações ou melhorias no código deste projeto, **atualize o arquivo de log/changelog** da conversa ou do repositório para manter o histórico de alterações limpo e atualizado para o usuário.
* **Atualização do Showcase:** O showcase deste projeto foi movido para a pasta de portfólio externa. Toda vez que formos atualizar o showcase, as alterações devem ser gravadas obrigatoriamente na pasta: `/home/igor-gomides/Documents/Antigravity/MYPORTIFOLIO/showcase` (como configurado no arquivo [`.showcase_config.json`](file:///home/igor-gomides/Documents/Antigravity/POLLYGOMIDES/.showcase_config.json) na raiz do projeto).
