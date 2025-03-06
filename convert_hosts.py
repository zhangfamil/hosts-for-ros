import requests
import re

def download_and_convert_hosts():
    # 配置参数
    url = "https://raw.githubusercontent.com/REIJI007/Adblock-Rule-Collection/refs/heads/main/ADBLOCK_RULE_COLLECTION_HOST.txt"
    output_file = "hosts.conf"
    
    try:
        # 下载规则文件
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # 定义正则表达式提取域名
        adblock_pattern = re.compile(r"^\|\|([a-z0-9.-]+)\^?$")  # 匹配 ||domain.com^
        hosts_pattern = re.compile(r"^127\.0\.0\.1\s+([a-z0-9.-]+)$")  # 匹配 127.0.0.1 domain.com
        domain_pattern = re.compile(r"^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$")  # 校验域名格式
        
        # 处理每行内容
        processed = set()  # 使用集合自动去重
        for line in response.text.splitlines():
            line = line.strip()
            if not line or line.startswith(("!", "#", "@", "[", "/")):  # 跳过注释和无效行
                continue
            
            # 提取域名
            domain = None
            if adblock_pattern.match(line):  # 处理 Adblock 格式
                domain = adblock_pattern.match(line).group(1)
            elif hosts_pattern.match(line):  # 处理 hosts 格式
                domain = hosts_pattern.match(line).group(1)
            
            # 校验域名格式并添加到集合
            if domain and domain_pattern.match(domain):
                processed.add(f"0.0.0.0 {domain}")
        
        # 写入文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(processed)))  # 按字母排序
        
        print(f"转换完成！已生成 {output_file}，共 {len(processed)} 条记录")
    
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {str(e)}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    download_and_convert_hosts()
