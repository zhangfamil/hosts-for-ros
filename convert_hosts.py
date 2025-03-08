import requests
import re
from typing import Set

def download_file(url: str, timeout: int = 15) -> str:
    """下载指定 URL 的内容"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[错误] 下载失败 ({url}): {str(e)}")
        return ""

def extract_domains(content: str, source_type: str) -> Set[str]:
    """从内容中提取域名 (支持三种格式)"""
    domains = set()
    
    # 定义正则表达式
    adblock_pattern = re.compile(r"^\|\|([a-z0-9.-]+)\^?$")          # 匹配 ||example.com^
    hosts_pattern = re.compile(r"^127\.0\.0\.1\s+([a-z0-9.-]+)")     # 匹配 127.0.0.1 example.com
    domain_pattern = re.compile(r"^([a-z0-9-]+\.)*[a-z0-9-]+\.[a-z]{2,}$")  # 域名验证

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!", "@")):  # 跳过注释行
            continue

        domain = None

        # 根据来源类型解析
        if source_type == "adblock":
            match = adblock_pattern.match(line)
            if match:
                domain = match.group(1).lower()
        elif source_type == "hosts":
            match = hosts_pattern.match(line)
            if match:
                domain = match.group(1).lower()
        elif source_type == "domain-only":  # 新增类型
            if "#" in line:  # 处理行内注释（例如：example.com #注释）
                clean_line = line.split("#")[0].strip()
            else:
                clean_line = line
            if clean_line:
                domain = clean_line.lower()

        # 验证域名格式
        if domain and domain_pattern.match(domain):
            domains.add(domain)

    return domains

def generate_hosts_conf(domains: Set[str], output_file: str = "hosts.conf") -> None:
    """生成 hosts.conf 文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Auto-generated merged blocklist\n")
        f.write("# Total domains: {}\n\n".format(len(domains)))
        f.write("\n".join(f"0.0.0.0 {domain}" for domain in sorted(domains)))

def main():
    # 配置源列表（支持三种类型）
    sources = [
        {
            "url": "https://raw.githubusercontent.com/REIJI007/Adblock-Rule-Collection/main/ADBLOCK_RULE_COLLECTION.txt",
            "type": "adblock"
        },
        {
            "url": "https://adaway.org/hosts.txt",
            "type": "hosts"
        },
        {  # 新增的 anti-AD 规则源
            "url": "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-domains.txt",
            "type": "domain-only"
        }
    ]

    all_domains = set()

    # 处理每个源
    for source in sources:
        print(f"[处理] 正在下载 {source['url']}")
        content = download_file(source["url"])
        if content:
            domains = extract_domains(content, source["type"])
            print(f"  └─ 发现有效域名: {len(domains)} 个")
            all_domains.update(domains)

    # 生成最终文件
    if all_domains:
        generate_hosts_conf(all_domains)
        print(f"\n[完成] 已合并 {len(all_domains)} 个唯一域名到 hosts.conf")
    else:
        print("\n[警告] 未找到有效域名，文件未更新")

if __name__ == "__main__":
    main()
