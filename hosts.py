import requests

def download_and_convert_hosts():
    # 配置参数
    url = "https://adaway.org/hosts.txt"
    output_file = "hosts.conf"
    
    try:
        # 下载 hosts.txt
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 处理每行内容
        processed_lines = []
        for line in response.text.splitlines():
            stripped_line = line.strip()
            
            # 跳过空行和注释行
            if not stripped_line or stripped_line.startswith("#"):
                continue
            
            # 分割行内容
            parts = stripped_line.split()
            if len(parts) < 2 or parts[0] != "127.0.0.1":
                continue
            
            # 提取域名并处理可能的注释
            for domain in parts[1:]:
                # 移除行内注释（例如："domain.com #注释" -> "domain.com"）
                clean_domain = domain.split("#")[0].strip()
                if clean_domain:
                    processed_lines.append(f"0.0.0.0 {clean_domain}")
        
        # 写入文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(processed_lines))
        
        print(f"转换完成！已生成 {output_file}，共 {len(processed_lines)} 条记录")
    
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {str(e)}")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    download_and_convert_hosts()
