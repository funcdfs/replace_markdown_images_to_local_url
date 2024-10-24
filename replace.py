import os
import re
import hashlib
import requests
import sys
from colorama import init, Fore, Style

# 初始化 colorama (跨平台支持)
init(autoreset=True)

# 下载图片的函数
def download_image(url, output_path):
    retries = 3
    for i in range(1, retries + 1):
        print(f"下载尝试 {i}: {url} -> {output_path}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # 抛出HTTPError
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(Fore.GREEN + f"下载成功: {output_path}")
            return True
        except requests.RequestException as e:
            print(Fore.RED + f"下载失败: {url} (尝试 {i}) - {e}")
    print(Fore.RED + f"下载失败，跳过: {url}")
    return False

# 处理 Markdown 文件的函数
def process_markdown_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                print(f"正在处理文件: {file_path}")

                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 使用正则表达式查找 Markdown 文件中的图片链接
                image_links = re.findall(r'!\[.*?\]\((http[^)]+)\)', content)

                # 为该 Markdown 文件所在目录创建一个 `local_images` 文件夹
                image_dir = os.path.join(root, "local_images")
                os.makedirs(image_dir, exist_ok=True)

                for image_url in image_links:
                    # 获取图片的文件扩展名
                    image_ext = image_url.split('.')[-1]

                    # 获取 URL 的 MD5 哈希值
                    image_hash = hashlib.md5(image_url.encode()).hexdigest()

                    # 生成唯一的图片文件名：哈希值 + 原始扩展名
                    image_name = f"{image_hash}.{image_ext}"

                    # 确定图片保存路径
                    image_path = os.path.join(image_dir, image_name)

                    # 检查图片是否已经存在，如果不存在则下载
                    if not os.path.isfile(image_path):
                        print(f"图片不存在，开始下载: {image_url}")
                        if download_image(image_url, image_path):
                            print(Fore.GREEN + f"下载成功: {image_url}")
                        else:
                            print(Fore.RED + f"下载失败，跳过: {image_url}")
                    else:
                        print(Fore.YELLOW + f"图片已存在，跳过下载: {image_path}")

                    # 检查图片是否成功下载
                    if os.path.isfile(image_path):
                        # 替换 Markdown 文件中的图片链接为本地链接
                        local_link = f"![](local_images/{image_name})"

                        # 使用正则表达式替换原始 URL 为本地链接
                        content = re.sub(r'!\[.*?\]\(' + re.escape(image_url) + r'\)', local_link, content)
                        print(Fore.GREEN + f"已成功替换链接: {image_url} -> local_images/{image_name}")
                    else:
                        print(Fore.RED + f"链接替换失败: {image_url}")

                # 将修改后的内容写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

    print(Fore.GREEN + "所有图片链接已处理完毕。")

# 主程序
if __name__ == "__main__":
    # 从命令行参数获取要处理的目录，默认是当前目录
    directory_to_process = sys.argv[1] if len(sys.argv) > 1 else '.'

    process_markdown_files(directory_to_process)