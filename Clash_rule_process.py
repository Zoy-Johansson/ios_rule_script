#!/usr/bin/env python3
import os
import subprocess

# 定义 rule/Clash 的根目录
CLASH_DIR = os.path.join("rule", "Clash")

def process_list_file(list_filepath):
    """
    处理一个 .list 文件，将内容分为三类：
    1. DOMAIN 类型：处理以 "DOMAIN," 开头的（但排除 DOMAIN-SUFFIX 和 DOMAIN-KEYWORD）
       与以 "DOMAIN-SUFFIX," 开头的行（将前缀替换为 "+."）。
    2. IP-CIDR 类型：处理以 "IP-CIDR," 或 "IP-CIDR6," 开头的行，
       删除对应前缀以及行尾的 ",no-resolve"（若存在）。
    3. Classical 类型：提取以下两种情况：
       - 以 "DOMAIN-KEYWORD," 开头的行（保留原内容），
       - 或不含 DOMAIN（注意：这里不排除 DOMAIN-KEYWORD，因为已经单独判断）、DOMAIN-SUFFIX、IP-CIDR、IP-CIDR6、IP-ASN 且不以 "#" 开头的内容。
    返回3个列表：domain_lines, ipcidr_lines, classical_lines。
    """
    domain_lines = []
    ipcidr_lines = []
    classical_lines = []

    with open(list_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 处理 DOMAIN-SUFFIX（优先处理）
            if line.startswith("DOMAIN-SUFFIX,"):
                # 去掉 "DOMAIN-SUFFIX," 前缀，并替换为 "+."
                content = line[len("DOMAIN-SUFFIX,"):]
                domain_lines.append(f"+.{content}")
            # 处理以 "DOMAIN," 开头，但排除 DOMAIN-SUFFIX 和 DOMAIN-KEYWORD
            elif line.startswith("DOMAIN,") and not line.startswith("DOMAIN-SUFFIX,") and not line.startswith("DOMAIN-KEYWORD,"):
                content = line[len("DOMAIN,"):]
                domain_lines.append(content)
            # 处理 IP-CIDR 与 IP-CIDR6
            elif line.startswith("IP-CIDR,") or line.startswith("IP-CIDR6,"):
                if line.startswith("IP-CIDR,"):
                    content = line[len("IP-CIDR,"):]
                else:
                    content = line[len("IP-CIDR6,"):]
                # 删除尾部的 ",no-resolve"（如果存在）
                if content.endswith(",no-resolve"):
                    content = content[:-len(",no-resolve")]
                ipcidr_lines.append(content)
            else:
                # 对 classical 类型的处理：
                # 如果行以 "DOMAIN-KEYWORD," 开头，则保留
                if line.startswith("DOMAIN-KEYWORD,"):
                    classical_lines.append(line)
                # 否则，只保留不含以下关键词且不以 '#' 开头的内容
                elif ("DOMAIN-SUFFIX" not in line and
                      "IP-CIDR" not in line and
                      "IP-CIDR6" not in line and
                      "IP-ASN" not in line and
                      not line.startswith("#")):
                    # 此处也排除以 "DOMAIN," 开头的（此类已经在前面处理）
                    if not line.startswith("DOMAIN,"):
                        classical_lines.append(line)
    return domain_lines, ipcidr_lines, classical_lines

def write_file_if_content(filepath, lines):
    """
    如果 lines 不为空，则写入文件并返回 True，否则返回 False
    """
    if lines:
        with open(filepath, 'w', encoding='utf-8') as f:
            for l in lines:
                f.write(l + "\n")
        return True
    return False

def convert_file(rule_type, filepath):
    """
    调用 mihomo 命令将 txt 文件转换为 mrs 文件。
    rule_type: "domain" 或 "ipcidr"
    filepath: 源 txt 文件路径
    生成的 mrs 文件路径为 <filepath>.mrs
    """
    mrs_filepath = filepath + ".mrs"
    cmd = ["mihomo", "convert-ruleset", rule_type, "text", filepath, mrs_filepath]
    try:
        subprocess.run(cmd, check=True)
        print(f"转换成功: {filepath} -> {mrs_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败: {filepath}，错误：{e}")

def process_subfolder(subdir_path, subfolder_name):
    """
    遍历子文件夹中所有 .list 文件，整合内容后生成对应类型文件：
      - {subfolder}_type_domain.txt
      - {subfolder}_type_ipcidr.txt
      - {subfolder}_type_classical.txt
    对 domain 与 ipcidr 文件调用 mihomo 转换生成 .mrs 文件。
    """
    domain_total = []
    ipcidr_total = []
    classical_total = []

    # 遍历子文件夹中所有文件
    for filename in os.listdir(subdir_path):
        if filename.endswith(".list"):
            list_filepath = os.path.join(subdir_path, filename)
            print(f"处理文件: {list_filepath}")
            domain_lines, ipcidr_lines, classical_lines = process_list_file(list_filepath)
            domain_total.extend(domain_lines)
            ipcidr_total.extend(ipcidr_lines)
            classical_total.extend(classical_lines)

    # 生成 DOMAIN 类型文件
    domain_file = os.path.join(subdir_path, f"{subfolder_name}_type_domain.txt")
    if write_file_if_content(domain_file, domain_total):
        convert_file("domain", domain_file)
    else:
        print(f"{domain_file} 无内容，不生成。")

    # 生成 IP-CIDR 类型文件
    ipcidr_file = os.path.join(subdir_path, f"{subfolder_name}_type_ipcidr.txt")
    if write_file_if_content(ipcidr_file, ipcidr_total):
        convert_file("ipcidr", ipcidr_file)
    else:
        print(f"{ipcidr_file} 无内容，不生成。")

    # 生成 Classical 类型文件
    classical_file = os.path.join(subdir_path, f"{subfolder_name}_type_classical.txt")
    if write_file_if_content(classical_file, classical_total):
        print(f"生成 {classical_file} 成功。")
    else:
        print(f"{classical_file} 无内容，不生成。")

def main():
    if not os.path.isdir(CLASH_DIR):
        print(f"目录 {CLASH_DIR} 不存在！")
        return

    # 遍历 rule/Clash 下所有子文件夹
    for subfolder in os.listdir(CLASH_DIR):
        subfolder_path = os.path.join(CLASH_DIR, subfolder)
        if os.path.isdir(subfolder_path):
            print(f"开始处理子文件夹：{subfolder}")
            process_subfolder(subfolder_path, subfolder)

if __name__ == '__main__':
    main()
