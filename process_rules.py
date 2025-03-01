import requests
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.93 (KHTML, like Gecko) Chrome/132.93.93.0 Safari/537.93'
}

def process_url1(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    lines = response.text.splitlines()
    
    reject_extra = []
    suffix_lines = []
    
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue
            
        if any(kw in line for kw in ['DOMAIN-KEYWORD', 'DOMAIN-WILDCARD']):
            reject_extra.append(line)
            
        if 'DOMAIN-SUFFIX' in line:
            parts = line.split(',', 2)
            if len(parts) >= 2:
                domain = parts[1].strip()
                suffix_lines.append(f'.{domain}')
    
    with open('source/reject_extra.list', 'w', encoding='utf-8') as f:
        f.write('\n'.join(reject_extra))
    
    return suffix_lines

def process_url(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return [
        line for line in response.text.splitlines()
        if not line.lstrip().startswith('#')
    ]

def main():
    os.makedirs('source', exist_ok=True)
    
    # 处理第一个URL
    surfix_content = process_url1('https://adrules.top/adrules-surge.conf')
    
    # 处理其他URL
    url2_content = process_url('https://ruleset.skk.moe/List/domainset/reject.conf')
    url3_content = process_url('https://anti-ad.net/surge2.txt')
    
    # 合并并去重
    merged = surfix_content + url2_content + url3_content
    unique_content = sorted(list(set(merged)))
    
    # 写入最终文件
    with open('source/reject.conf', 'w', encoding='utf-8') as f:
        f.write('\n'.join(unique_content))

if __name__ == '__main__':
    main()
