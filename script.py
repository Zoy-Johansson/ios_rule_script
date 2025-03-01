import os
import cloudscraper

def fetch_content(url):
    """
    使用 cloudscraper 绕过反爬虫措施获取 URL 内容
    """
    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False
        }
    )
    response = scraper.get(url)
    response.raise_for_status()
    return response.text

def process_adrules():
    """
    处理 https://adrules.top/adrules-surge.conf 文件：
      1. 删除以 '#' 开头的行；
      2. 提取包含 "DOMAIN-KEYWORD" 或 "DOMAIN-WILDCARD" 的行，存入 extra_lines 列表；
      3. 提取包含 "DOMAIN-SUFFIX" 的行，将格式转换为以 '.' 开头（如将 "DOMAIN-SUFFIX,example.com" 转为 ".example.com"）。
    返回两个列表：extra_lines 与 suffix_lines。
    """
    url = "https://adrules.top/adrules-surge.conf"
    content = fetch_content(url)
    lines = content.splitlines()

    extra_lines = []
    suffix_lines = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "DOMAIN-KEYWORD" in line or "DOMAIN-WILDCARD" in line:
            extra_lines.append(line)
        elif "DOMAIN-SUFFIX" in line:
            parts = line.split(",", 1)
            if len(parts) == 2:
                domain = parts[1].strip()
                if not domain.startswith("."):
                    domain = "." + domain
                suffix_lines.append(domain)
    return extra_lines, suffix_lines

def process_file(url):
    """
    下载文件后删除所有以 '#' 开头的行，返回处理后的行列表
    """
    content = fetch_content(url)
    lines = content.splitlines()
    processed = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        processed.append(line)
    return processed

def main():
    # 定义待处理的 URL
    reject_conf_url = "https://ruleset.skk.moe/List/domainset/reject.conf"
    surge2_url = "https://anti-ad.net/surge2.txt"

    # 处理 adrules-surge.conf 文件
    extra_lines, suffix_lines = process_adrules()

    # 处理 reject.conf 和 surge2.txt 文件，删除所有注释行
    processed_reject_conf = process_file(reject_conf_url)
    processed_surge2 = process_file(surge2_url)

    # 合并 DOMAIN-SUFFIX 处理后的内容与其他两个文件的内容
    merged = suffix_lines + processed_reject_conf + processed_surge2
    # 去重（保持原有顺序）
    seen = set()
    merged_unique = []
    for item in merged:
        if item not in seen:
            seen.add(item)
            merged_unique.append(item)

    # 指定输出目录：master/source（保留文件夹内其他文件）
    output_dir = os.path.join("master", "source")
    os.makedirs(output_dir, exist_ok=True)

    # 写入 reject_extra.list 文件（存放 DOMAIN-KEYWORD/DOMAIN-WILDCARD 的行）
    extra_file_path = os.path.join(output_dir, "reject_extra.list")
    with open(extra_file_path, "w", encoding="utf-8") as f:
        for line in extra_lines:
            f.write(line + "\n")

    # 写入 reject.conf 文件（合并后的内容）
    reject_file_path = os.path.join(output_dir, "reject.conf")
    with open(reject_file_path, "w", encoding="utf-8") as f:
        for line in merged_unique:
            f.write(line + "\n")

if __name__ == "__main__":
    main()
