import requests
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 增强型请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://adrules.top/',
    'DNT': '1',
}

# 创建带重试机制的session
def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET']
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def process_url1(url):
    session = create_session()
    try:
        response = session.get(
            url,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # 添加随机延迟
        time.sleep(1.5)
        
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {str(e)}")
        return []

def process_url(url):
    session = create_session()
    try:
        response = session.get(
            url,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # 添加随机延迟
        time.sleep(1.5)
        
        return [
            line for line in response.text.splitlines()
            if not line.lstrip().startswith('#')
        ]
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {str(e)}")
        return []

# ... 保持main函数不变 ...
