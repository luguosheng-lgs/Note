import tftpy

def download_file_from_tftp(server_ip, server_port, remote_file, local_file):
    try:
        # 创建TFTP客户端实例
        client = tftpy.TftpClient(server_ip, server_port)
        # 下载文件
        client.download(remote_file, local_file)
        print(f"文件 {remote_file} 成功下载到 {local_file}")
    except Exception as e:
        print(f"下载文件时出错: {e}")

# 使用示例
server_ip = '192.168.0.99'  # 替换为你的TFTP服务器IP地址
server_port = 69  # TFTP默认端口
remote_file = 'TD53S33-3.0.0.22-2023101614.bin'  # 远程文件名
local_file = '555'  # 本地保存的文件名

download_file_from_tftp(server_ip, server_port, remote_file, local_file)