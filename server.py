#!/usr/bin/env python3
import os
import re
import sys
import json
import shutil
import requests
import urllib.parse
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

API_URL = "https://script.google.com/macros/s/AKfycbzCNEjF50Pjdqg4pshWDpP29_XGRQbFBZnEBaB7vtkwIFydmc5bZOwAyCPWyvwzaiyo/exec"

# In-memory session state
session_state = {
    "active": False,
    "html_content": "",
    "feedbacks": [],
    "approved_feedbacks": [],
    "chat_history": [],
    "password": ""
}

# Paths resolved relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")
PREVIEW_PATH = os.path.join(SCRIPT_DIR, "index_preview.html")
BACKUPS_DIR = os.path.join(SCRIPT_DIR, "backups")

SYSTEM_INSTRUCTION = (
    "Você é um Agente IA especialista em desenvolvimento web. Seu trabalho é analisar o código HTML de uma página e a solicitação do usuário, e gerar uma lista de modificações estruturadas em formato JSON.\n"
    "Responda EXCLUSIVAMENTE com um objeto JSON válido contendo os seguintes campos:\n"
    "{\n"
    '  "changes": [\n'
    "    {\n"
    '      "selector": "seletor CSS do elemento a ser modificado",\n'
    '      "action": "replace_inner_html" ou "set_attribute",\n'
    '      "attribute": "nome do atributo (obrigatório se action for set_attribute)",\n'
    '      "value": "novo valor/conteúdo a ser aplicado"\n'
    "    }\n"
    "  ],\n"
    '  "explanation": "Breve explicação em português das alterações realizadas."\n'
    "}\n"
    "Regras:\n"
    "1. Escolha seletores CSS precisos e únicos que correspondam exatamente ao elemento que deve ser alterado.\n"
    "2. Se for alterar o texto interno de um elemento complexo com tags filhas, certifique-se de manter as tags filhas ou formatar o 'value' com o HTML interno adequado.\n"
    "3. Retorne APENAS o JSON, sem blocos de código markdown como ```json, sem caracteres extras."
)

def apply_json_changes(html_content, changes):
    soup = BeautifulSoup(html_content, "html.parser")
    for change in changes:
        selector = change.get("selector")
        action = change.get("action")
        value = change.get("value")
        
        if not selector:
            continue
            
        el = soup.select_one(selector)
        if not el:
            print(f"Aviso: Elemento não encontrado para o seletor {selector}")
            continue
            
        if action == "replace_inner_html":
            el.clear()
            if isinstance(value, str) and "<" in value and ">" in value:
                new_content = BeautifulSoup(value, "html.parser")
                el.append(new_content)
            else:
                el.string = value
        elif action == "set_attribute":
            attr = change.get("attribute")
            if attr:
                el[attr] = value
                
    return str(soup)

def apply_sheet_feedbacks(html_content, feedbacks):
    soup = BeautifulSoup(html_content, "html.parser")
    applied_count = 0
    details = []
    
    for fb in feedbacks:
        # The CSS Selector is in the 'original_text' column
        selector = fb.get('original_text', '').strip()
        
        # The replacement content is in the 'comments' column (if filled), otherwise in 'suggested_text'
        suggested_text = fb.get('comments', '').strip()
        if not suggested_text:
            suggested_text = fb.get('suggested_text', '').strip()
        
        if not selector:
            continue
            
        el = soup.select_one(selector)
        if not el:
            details.append(f"⚠️ Seletor '{selector}' não encontrado.")
            continue
            
        if el.name.lower() == 'img':
            el['src'] = suggested_text
            details.append(f"✓ Imagem [{selector}] -> alterado src para '{suggested_text}'")
        else:
            el.clear()
            if "<" in suggested_text and ">" in suggested_text:
                new_content = BeautifulSoup(suggested_text, "html.parser")
                el.append(new_content)
            else:
                el.string = suggested_text
            details.append(f"✓ Elemento [{selector}] -> conteúdo alterado")
        applied_count += 1
        
    explanation = "\n".join(details)
    return str(soup), applied_count, explanation

def call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, "Erro: A variável de ambiente GEMINI_API_KEY não está definida no servidor. Por favor, defina-a e reinicie o servidor."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{SYSTEM_INSTRUCTION}\n\nCódigo HTML Atual:\n```html\n{session_state['html_content']}\n```\n\nSolicitação/Instrução do usuário:\n{prompt}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        res_data = res.json()
        
        response_text = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Strip markdown fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            parsed = json.loads(response_text)
        except Exception as json_err:
            print(f"Erro ao parsear JSON da IA: {response_text}")
            return None, f"A IA não retornou um formato JSON válido: {str(json_err)}"
            
        changes = parsed.get("changes", [])
        explanation = parsed.get("explanation", "Alterações aplicadas.")
        
        # Apply changes using BeautifulSoup
        new_html = apply_json_changes(session_state["html_content"], changes)
        return new_html, explanation
    except Exception as e:
        return None, f"Erro ao chamar a API do Gemini: {str(e)}"

# Route to serve homepage / index
@app.route('/')
def serve_index():
    return send_from_directory(SCRIPT_DIR, 'index.html')

# Serve static files dynamically
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(SCRIPT_DIR, path)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "active": session_state["active"],
        "chat_history": session_state["chat_history"],
        "pending_feedbacks_count": len(session_state["feedbacks"])
    })

@app.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.json or {}
    password = data.get("password")
    
    if not password:
        return jsonify({"status": "error", "message": "Senha do painel administrativo é obrigatória"}), 400
        
    # Fetch database feedbacks to verify password and get latest entries
    query = urllib.parse.urlencode({'password': password})
    req_url = f"{API_URL}?{query}"
    
    try:
        req = urllib.request.Request(req_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro de conexão com o Google Sheets: {str(e)}"}), 500
        
    if res_data.get('status') != 'success':
        return jsonify({"status": "error", "message": f"Falha de autenticação: {res_data.get('message', 'Senha incorreta')}"}), 401
        
    raw_data = res_data.get('data', [])
    feedbacks = [item for item in raw_data if item.get('type') == 'Feedback' and item.get('internal_notes') != 'Aplicado via Agente']
    
    # Read original index.html
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao ler index.html: {str(e)}"}), 500
        
    # Write initial index_preview.html (same as current index.html)
    try:
        with open(PREVIEW_PATH, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao gravar index_preview.html: {str(e)}"}), 500
        
    # Initialize session
    session_state["active"] = True
    session_state["html_content"] = html_content
    session_state["feedbacks"] = feedbacks
    session_state["approved_feedbacks"] = []
    session_state["password"] = password
    session_state["chat_history"] = [
        {
            "role": "agent",
            "text": f"Olá! Sessão iniciada com sucesso. Encontrei {len(feedbacks)} feedback(s) pendente(s) na planilha. Clique em **Importar Feedbacks** para que eu possa aplicá-los ou envie uma mensagem no chat para fazer edições manuais!"
        }
    ]
    
    return jsonify({
        "status": "success",
        "feedbacks_count": len(feedbacks),
        "chat_history": session_state["chat_history"]
    })

@app.route('/api/process_feedbacks_ai', methods=['POST'])
def process_feedbacks_ai():
    if not session_state["active"]:
        return jsonify({"status": "error", "message": "Nenhuma sessão ativa"}), 400
        
    if not session_state["feedbacks"]:
        return jsonify({"status": "error", "message": "Nenhum feedback pendente na planilha"}), 400
        
    session_state["chat_history"].append({
        "role": "user",
        "text": "Importar feedbacks pendentes da planilha e aplicar alterações."
    })
    
    new_html, applied_count, explanation = apply_sheet_feedbacks(session_state["html_content"], session_state["feedbacks"])
    
    # Update state
    session_state["html_content"] = new_html
    session_state["approved_feedbacks"] = list(session_state["feedbacks"])
    
    # Save preview
    try:
        with open(PREVIEW_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao atualizar preview: {str(e)}"}), 500
        
    session_state["chat_history"].append({
        "role": "agent",
        "text": f"Apliquei com sucesso os {applied_count} feedbacks pendentes no arquivo de preview!\n\n**Detalhamento:**\n{explanation}"
    })
    
    return jsonify({
        "status": "success",
        "chat_history": session_state["chat_history"]
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    if not session_state["active"]:
        return jsonify({"status": "error", "message": "Nenhuma sessão ativa"}), 400
        
    data = request.json or {}
    user_prompt = data.get("prompt", "").strip()
    
    if not user_prompt:
        return jsonify({"status": "error", "message": "A mensagem não pode estar vazia"}), 400
        
    session_state["chat_history"].append({
        "role": "user",
        "text": user_prompt
    })
    
    new_html, explanation = call_gemini(user_prompt)
    if not new_html:
        session_state["chat_history"].append({
            "role": "agent",
            "text": f"Erro ao processar alteração: {explanation}"
        })
        return jsonify({"status": "error", "message": explanation, "chat_history": session_state["chat_history"]}), 500
        
    # Update HTML state
    session_state["html_content"] = new_html
    
    # Save preview
    try:
        with open(PREVIEW_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao atualizar preview: {str(e)}"}), 500
        
    session_state["chat_history"].append({
        "role": "agent",
        "text": explanation
    })
    
    return jsonify({
        "status": "success",
        "chat_history": session_state["chat_history"]
    })

@app.route('/api/approve', methods=['POST'])
def approve():
    if not session_state["active"]:
        return jsonify({"status": "error", "message": "Nenhuma sessão ativa"}), 400
        
    # Create backups directory if not exists
    if not os.path.exists(BACKUPS_DIR):
        try:
            os.makedirs(BACKUPS_DIR)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Erro ao criar diretório de backups: {str(e)}"}), 500
            
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup original index.html
    backup_original = os.path.join(BACKUPS_DIR, f"index_backup_{timestamp}.html")
    try:
        shutil.copy2(INDEX_PATH, backup_original)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao fazer backup do index.html: {str(e)}"}), 500
        
    # Backup final preview index before overwrite
    backup_preview = os.path.join(BACKUPS_DIR, f"index_preview_backup_{timestamp}.html")
    try:
        shutil.copy2(PREVIEW_PATH, backup_preview)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao fazer backup do preview: {str(e)}"}), 500
        
    # Overwrite main index.html
    try:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(session_state["html_content"])
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao publicar index.html: {str(e)}"}), 500
        
    # Sync status back to Google Sheets for all approved feedbacks
    sync_errors = []
    for fb in session_state["approved_feedbacks"]:
        row_id = fb.get('rowId')
        post_data = urllib.parse.urlencode({
            'action': 'update',
            'password': session_state["password"],
            'rowId': row_id,
            'payment_confirmed': fb.get('payment_confirmed', 'Não'),
            'onboarding_completed': fb.get('onboarding_completed', 'Não'),
            'follow_up_needed': fb.get('follow_up_needed', 'Não'),
            'internal_notes': 'Aplicado via Agente'
        }).encode('utf-8')
        
        try:
            req_post = urllib.request.Request(API_URL, data=post_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req_post) as post_response:
                pass
        except Exception as err:
            sync_errors.append(f"Row {row_id}: {str(err)}")
            
    # Remove preview file
    if os.path.exists(PREVIEW_PATH):
        try:
            os.remove(PREVIEW_PATH)
        except:
            pass
            
    # Reset session
    session_state["active"] = False
    session_state["html_content"] = ""
    session_state["feedbacks"] = []
    session_state["approved_feedbacks"] = []
    session_state["password"] = ""
    session_state["chat_history"] = []
    
    return jsonify({
        "status": "success",
        "message": "Alterações aplicadas permanentemente!",
        "sync_errors": sync_errors
    })

@app.route('/api/discard', methods=['POST'])
def discard():
    if not session_state["active"]:
        return jsonify({"status": "error", "message": "Nenhuma sessão ativa"}), 400
        
    # Remove preview file
    if os.path.exists(PREVIEW_PATH):
        try:
            os.remove(PREVIEW_PATH)
        except:
            pass
            
    # Reset session
    session_state["active"] = False
    session_state["html_content"] = ""
    session_state["feedbacks"] = []
    session_state["approved_feedbacks"] = []
    session_state["password"] = ""
    session_state["chat_history"] = []
    
    return jsonify({"status": "success", "message": "Alterações descartadas com sucesso."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    print("=========================================================")
    print("  SERVIDOR DE REVISÃO E CHAT COM IA - POLLY GOMIDES      ")
    print("=========================================================")
    print(f"Diretório de trabalho: {SCRIPT_DIR}")
    print("Defina a variável GEMINI_API_KEY antes de usar o chat.")
    print(f"Iniciando servidor na porta {port}: http://localhost:{port}/admin.html")
    print("=========================================================")
    app.run(host='0.0.0.0', port=port, debug=True)
