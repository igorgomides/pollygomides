#!/usr/bin/env python3
import sys
import re
import urllib.request
import urllib.parse
import json
import os
import shutil
from datetime import datetime
from bs4 import BeautifulSoup

API_URL = "https://script.google.com/macros/s/AKfycbzCNEjF50Pjdqg4pshWDpP29_XGRQbFBZnEBaB7vtkwIFydmc5bZOwAyCPWyvwzaiyo/exec"

def find_element_bounds(html, tag_name, start_line, start_col):
    lines = html.splitlines(keepends=True)
    char_offset = 0
    for i in range(start_line - 1):
        if i < len(lines):
            char_offset += len(lines[i])
    char_offset += start_col
    
    self_closing_tags = {'img', 'br', 'hr', 'input', 'link', 'meta'}
    if tag_name.lower() in self_closing_tags:
        idx = char_offset
        while idx < len(html):
            if html[idx] == '>':
                return char_offset, idx + 1
            idx += 1
        return char_offset, char_offset
        
    start_tag_rx = re.compile(rf'^<{tag_name}(\s|>|/)', re.IGNORECASE)
    
    stack = 1
    idx = char_offset + 1
    while idx < len(html):
        if html[idx] == '<':
            if html[idx:].lower().startswith(f'</{tag_name}'):
                stack -= 1
                if stack == 0:
                    end_idx = html.find('>', idx)
                    if end_idx != -1:
                        return char_offset, end_idx + 1
                    else:
                        return char_offset, idx + len(tag_name) + 3
            elif start_tag_rx.match(html[idx:]):
                tag_end = html.find('>', idx)
                if tag_end != -1:
                    is_self_closing = html[tag_end-1:tag_end] == '/' or tag_name.lower() in self_closing_tags
                    if not is_self_closing:
                        stack += 1
        idx += 1
    return char_offset, len(html)

def replace_inner_content(html, start, end, new_content):
    # Find the end of the opening tag (first '>' after start)
    open_tag_end = html.find('>', start)
    if open_tag_end == -1 or open_tag_end >= end:
        return html
        
    # Find the start of the closing tag (last '</' before end)
    close_tag_start = html.rfind('</', start, end)
    if close_tag_start == -1 or close_tag_start <= open_tag_end:
        return html
        
    # Reassemble the HTML
    return html[:open_tag_end + 1] + new_content + html[close_tag_start:]

def replace_img_src(html, start, end, new_src):
    tag_content = html[start:end]
    src_match = re.search(r'src=["\'](.*?)["\']', tag_content, re.IGNORECASE)
    if src_match:
        old_src_part = src_match.group(0)
        quote = tag_content[src_match.start() + 4]
        new_src_part = f'src={quote}{new_src}{quote}'
        new_tag_content = tag_content.replace(old_src_part, new_src_part)
        return html[:start] + new_tag_content + html[end:]
    return html

def parse_feedback_message(message_text):
    sug_match = re.search(r'Sugestão:\s*"(.*?)"(?:\nMotivo:|\n|$)', message_text, re.DOTALL)
    suggested = sug_match.group(1) if sug_match else ""
    
    reason_match = re.search(r'Motivo:\s*"(.*?)"', message_text, re.DOTALL)
    reason = reason_match.group(1) if reason_match else ""
    
    return suggested, reason

def main():
    print("=========================================================")
    print("  AGENTE DE APLICAÇÃO DE FEEDBACK VISUAL - POLLY GOMIDES  ")
    print("=========================================================")
    
    # Get password
    password = ""
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Digite a senha do Painel Administrativo: ").strip()
        
    if not password:
        print("Senha obrigatória!")
        sys.exit(1)
        
    # Fetch database data
    print("\nConectando à planilha do Google Sheets...")
    query = urllib.parse.urlencode({'password': password})
    req_url = f"{API_URL}?{query}"
    
    try:
        req = urllib.request.Request(req_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
        sys.exit(1)
        
    if res_data.get('status') != 'success':
        print(f"Erro de autenticação ou erro no servidor: {res_data.get('message', 'Erro desconhecido')}")
        sys.exit(1)
        
    raw_data = res_data.get('data', [])
    
    # Filter feedbacks
    feedbacks = []
    for item in raw_data:
        if item.get('type') == 'Feedback':
            # Exclude already applied
            if item.get('internal_notes') != 'Aplicado via Agente':
                feedbacks.append(item)
                
    if not feedbacks:
        print("\nNenhum feedback pendente encontrado na planilha! Tudo atualizado. ✨")
        return
        
    print(f"\nEncontrado(s) {len(feedbacks)} feedback(s) pendente(s):")
    
    # Resolve paths relative to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, "index.html")
    preview_file = os.path.join(script_dir, "index_preview.html")
    backups_dir = os.path.join(script_dir, "backups")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, "html.parser")
    updated_count = 0
    approved_feedbacks = []
    
    for fb in feedbacks:
        row_id = fb.get('rowId')
        # The CSS Selector is in the 'original_text' column
        selector = fb.get('original_text', '').strip()
        
        # The replacement content is in the 'comments' column (if filled), otherwise in 'suggested_text'
        suggested_text = fb.get('comments', '').strip()
        if not suggested_text:
            suggested_text = fb.get('suggested_text', '').strip()
            
        reason = fb.get('comments', '').strip()
        requested_by = fb.get('selector', 'Polly').strip()
        
        print(f"\n---------------------------------------------------------")
        print(f"ID da Linha: {row_id}")
        print(f"Solicitado por: {requested_by}")
        print(f"Seletor: {selector}")
        print(f"Texto sugerido: {repr(suggested_text)}")
        if reason:
            print(f"Motivo: {reason}")
            
        # Select element
        el = soup.select_one(selector)
        if not el:
            print(f"⚠️ Elemento não encontrado no index.html com o seletor: {selector}")
            continue
            
        print(f"Elemento HTML encontrado: <{el.name}>")
        
        # Calculate bounds
        start, end = find_element_bounds(html_content, el.name, el.sourceline, el.sourcepos)
        original_outer = html_content[start:end]
        
        # Apply change
        if el.name.lower() == 'img':
            temp_html_content = replace_img_src(html_content, start, end, suggested_text)
        else:
            temp_html_content = replace_inner_content(html_content, start, end, suggested_text)
            
        # Verify if content was updated
        if temp_html_content == html_content:
            print("❌ Falha ao simular alteração no código. (Limite não correspondido).")
            continue
            
        # Output changes preview
        # Show code original vs modified
        modified_outer = temp_html_content[start:start + (end - start) + (len(temp_html_content) - len(html_content))]
        print(f"\n[Código Original]:\n{original_outer}")
        print(f"\n[Código Proposto]:\n{modified_outer}")
        
        # Confirm change
        confirm = input("\nDeseja aceitar este feedback? (s/n): ").strip().lower()
        if confirm in ('s', 'sim', 'y', 'yes'):
            html_content = temp_html_content
            # Update BeautifulSoup soup instance for next queries in loop
            soup = BeautifulSoup(html_content, "html.parser")
            updated_count += 1
            approved_feedbacks.append(fb)
            print("✓ Alteração aceita temporariamente.")
        else:
            print("✗ Alteração rejeitada pelo usuário.")
            
    if updated_count > 0:
        # Save modifications to preview file
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n=========================================================")
        print(f"✓ {updated_count} alteração(ões) salva(s) temporariamente em '{preview_file}'.")
        print("Abra o arquivo 'index_preview.html' no navegador para revisar as mudanças.")
        print("=========================================================")
        
        final_confirm = input("\nDeseja aplicar permanentemente as alterações no 'index.html' principal? (s/n): ").strip().lower()
        if final_confirm in ('s', 'sim', 'y', 'yes'):
            # Create backups directory if not exists
            if not os.path.exists(backups_dir):
                os.makedirs(backups_dir)
                
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backups_dir, f"index_backup_{timestamp}.html")
            
            # Copy current index.html to backup
            try:
                shutil.copy2(index_path, backup_file)
                print(f"✓ Backup criado com sucesso: {backup_file}")
            except Exception as e:
                print(f"⚠️ Erro ao criar backup: {e}")
                sys.exit(1)
                
            # Overwrite index.html with the new content
            try:
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("✓ Arquivo 'index.html' atualizado com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar 'index.html': {e}")
                sys.exit(1)
                
            # Sync back to Google Sheet to mark as "Aplicado via Agente"
            print("\nSincronizando status das alterações aceitas na planilha...")
            for fb in approved_feedbacks:
                row_id = fb.get('rowId')
                print(f"Sincronizando ID {row_id}...")
                post_data = urllib.parse.urlencode({
                    'action': 'update',
                    'password': password,
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
                    print(f"✓ Status do ID {row_id} atualizado para 'Aplicado via Agente'!")
                except Exception as err:
                    print(f"⚠️ Erro ao atualizar status do ID {row_id}: {err}")
            
            # Delete preview file
            if os.path.exists(preview_file):
                os.remove(preview_file)
                print(f"✓ Arquivo temporário '{preview_file}' removido.")
                
            print(f"\n🎉 Sucesso! {updated_count} alteração(ões) aplicada(s) com sucesso em index.html!")
        else:
            print(f"\nAlterações não aplicadas ao 'index.html' principal. O arquivo '{preview_file}' foi mantido para sua revisão.")
    else:
        print("\nNenhuma alteração foi aceita ou aplicada.")

if __name__ == "__main__":
    main()
