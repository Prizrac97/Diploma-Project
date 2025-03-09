import os
import re
import hashlib
import base64
from bs4 import BeautifulSoup

def compute_sha256_hash(text):
    digest = hashlib.sha256(text.encode('utf-8')).digest()
    hash_b64 = base64.b64encode(digest).decode('utf-8')
    return f"'sha256-{hash_b64}'"  # Добавлены одинарные кавычки

def extract_style_hashes_from_file(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    hashes = set()
    for style in soup.find_all("style"):
        style_content = style.string  # Используем .string вместо .get_text() для получения точного содержимого
        if style_content:
            hash_value = compute_sha256_hash(style_content)
            hashes.add(hash_value)
    return hashes

def get_all_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def update_https_server_block(csp_hashes, nginx_conf_path='nginx.conf'):
    csp_hashes_str = " ".join(sorted(csp_hashes))
    new_csp_line = f'    add_header Content-Security-Policy "default-src \'self\'; style-src \'self\' {csp_hashes_str}; frame-ancestors \'self\'; form-action \'self\';" always;'
    
    with open(nginx_conf_path, 'r', encoding='utf-8') as f:
        config = f.read()
    
    # Ищем блок server, содержащий "listen 443 ssl"
    https_block_pattern = r'(server\s*\{[^}]*listen\s+443\s+ssl[^}]*\})'
    https_block_match = re.search(https_block_pattern, config, flags=re.DOTALL | re.IGNORECASE)
    
    if not https_block_match:
        print("HTTPS блок не найден в nginx.conf")
        return
    
    https_block = https_block_match.group(1)
    print("Найден HTTPS блок:\n", https_block)
    
    # Полное удаление **всех** строк add_header Content-Security-Policy
    https_block_clean = re.sub(
        r'^\s*add_header\s+Content-Security-Policy\s+.*?$',
        '',
        https_block, flags=re.MULTILINE)

    print("\nHTTPS блок после удаления старых CSP директив:\n", https_block_clean)
    
    # Если есть строка с X-Frame-Options, вставляем новую строку перед ней
    if re.search(r'^\s*add_header\s+X-Frame-Options\s+"SAMEORIGIN"', https_block_clean, flags=re.MULTILINE):
        https_block_updated = re.sub(
            r'(^\s*add_header\s+X-Frame-Options\s+"SAMEORIGIN".*$)',
            new_csp_line + "\n" + r'\1',
            https_block_clean, flags=re.MULTILINE)
    else:
        # Если X-Frame-Options не найден, вставляем перед закрывающей скобкой
        https_block_updated = re.sub(
            r'(\n\s*\})',
            "\n" + new_csp_line + r'\1',
            https_block_clean, flags=re.MULTILINE)
    
    print("\nHTTPS блок после вставки новой CSP директивы:\n", https_block_updated)
    
    updated_config = config.replace(https_block, https_block_updated)
    
    with open(nginx_conf_path, 'w', encoding='utf-8') as f:
        f.write(updated_config)
    
    print("\nnginx.conf успешно обновлён:")
    print(new_csp_line)

if __name__ == '__main__':
    html_directory = "Artisans-Nook"
    html_files = get_all_html_files(html_directory)
    
    if not html_files:
        print(f"В папке '{html_directory}' не найдено HTML-файлов.")
        exit(1)
    
    all_hashes = set()
    for file in html_files:
        file_hashes = extract_style_hashes_from_file(file)
        if file_hashes:
            print(f"Найденные хэши в файле {file}: {file_hashes}")
        all_hashes.update(file_hashes)
    
    if all_hashes:
        update_https_server_block(all_hashes)
    else:
        print("Не найдено блоков <style> для генерации хэшей.")