import os
import re
import shutil

# 定义需要提取的模式
IP_PATTERNS = r'IP-CIDR|IP-CIDR6|IP-ASN'

def process_file(file_path):
    """处理单个文件，提取匹配的内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    ip_content = []
    other_content = []

    # 分离出包含IP相关内容和其他内容
    for line in content:
        if re.search(IP_PATTERNS, line):
            ip_content.append(line)
        else:
            other_content.append(line)

    return ip_content, other_content

def write_new_files(file_path, ip_content, other_content):
    """将提取的内容写入新文件"""
    file_dir, file_name = os.path.split(file_path)
    base_name, ext = os.path.splitext(file_name)

    # 写入含有IP信息的文件
    if ip_content:
        with open(os.path.join(file_dir, f"{base_name}_ip{ext}"), 'w', encoding='utf-8') as ip_file:
            ip_file.writelines(ip_content)

    # 写入其他内容的文件
    if other_content:
        with open(os.path.join(file_dir, f"{base_name}_other{ext}"), 'w', encoding='utf-8') as other_file:
            other_file.writelines(other_content)

def process_directory(base_dir):
    """遍历目录并处理符合条件的文件"""
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)

            # 判断文件名是否符合匹配条件
            if '_All' in file and '_Resolve' not in file:
                # 处理文件名包含'_All'且不包含'_Resolve'的文件
                print(f"Processing _All file: {file_path}")
                ip_content, other_content = process_file(file_path)
                write_new_files(file_path, ip_content, other_content)

            elif '_Resolve' in file and '_All' not in file:
                # 处理文件名包含'_Resolve'且不包含'_All'的文件
                print(f"Processing _Resolve file: {file_path}")
                ip_content, other_content = process_file(file_path)
                write_new_files(file_path, ip_content, other_content)

            else:
                # 跳过不符合条件的文件
                print(f"Skipping file: {file_path} (does not match required pattern)")

def main():
    """主函数，启动文件处理流程"""
    base_dir = 'rule/Surge'  # Surge文件夹的路径
    process_directory(base_dir)

if __name__ == '__main__':
    main()
