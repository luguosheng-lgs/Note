import asyncio
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import threading
import uuid
import time

# 存储 token 与用户状态的全局字典
tokens = {}
active_websockets = {}

class WebSocketHandler:
    async def handle_connection(websocket, path):
        print("handle_connection")
        # 解析查询参数
        query = urlparse(path).query
        params = parse_qs(query)
        token = params.get('token', [''])[0]
        
        if not token:
            print("Invalid connection: missing token")
            await websocket.close()
            return
        
        print(f"WebSocket connected: token={token}")
        active_websockets[token] = websocket
        
        try:
            # 等待客户端发送消息（根据协议可能需要）
            async for message in websocket:
                print(f"Received message: {message}")
                
                # 此处可以添加消息处理逻辑
                # 例如：await self.handle_message(message, token)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket closed for token: {token}")
        finally:
            if token in active_websockets:
                del active_websockets[token]

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 处理二维码验证请求
        if self.path.startswith('/auth'):
            query = urlparse(self.path).query
            params = parse_qs(query)
            token = params.get('token', [''])[0]
            
            if token and token in tokens:
                tokens[token]['status'] = 'confirmed'
                print(f"QR code scanned for token: {token}")
                
                # 通过 WebSocket 通知客户端
                if token in active_websockets:
                    ws = active_websockets[token]
                    asyncio.run_coroutine_threadsafe(
                        ws.send(json.dumps({
                            'status': 'success',
                            'user_id': tokens[token]['user_id']
                        })), 
                        loop
                    )
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>Login Successful!</h1>")
            else:
                self.send_response(404)
                self.end_headers()
        
        # 提供模拟的二维码页面
        elif self.path == '/qr_page':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html> <body><h1>Scan QR Code to Login</h1><div id='qr-container'></div><script>setTimeout(() => {const token = new URLSearchParams(window.location.search).get('token');if(token) {fetch(`/auth?token=${token}`).then(() => alert('Login successful!')).catch(err => console.error(err));}}, 3000);</script></body></html>")
        else:
            self.send_response(404)
            self.end_headers()

def start_http_server():
    server = HTTPServer(('localhost', 8080), HTTPRequestHandler)
    print("HTTP Server running on http://localhost:8080")
    server.serve_forever()

async def start_websocket_server():
    print("start_websocket_server")
    async with websockets.serve(WebSocketHandler().handle_connection, "localhost", 8666):
        print("WebSocket Server running on ws://localhost:8666")
        await asyncio.Future()  # 永久运行

def simulate_qr_scan(token):
    """模拟手机扫描二维码的操作"""
    time.sleep(2)  # 等待客户端连接
    if token in tokens:
        # 模拟用户扫描二维码
        print(f"Simulating QR scan for token: {token}")
        tokens[token]['status'] = 'confirmed'
        
        # 模拟用户确认登录
        time.sleep(1)
        tokens[token]['status'] = 'success'
        
        # 通过 WebSocket 发送登录成功消息
        if token in active_websockets:
            print("发送登录成功消息")
            asyncio.run_coroutine_threadsafe(
                active_websockets[token].send(json.dumps({
                    'status': 'success',
                    'user_id': tokens[token]['user_id']
                })), 
                loop
            )

if __name__ == "__main__":
    # 创建事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 启动 HTTP 服务器线程
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # 启动 WebSocket 服务器
    ws_server = loop.create_task(start_websocket_server())
    
    # 启动事件循环
    def run_loop():
        loop.run_forever()
    
    ws_thread = threading.Thread(target=run_loop, daemon=True)
    ws_thread.start()
    
    # 用户交互模拟
    try:
        while True:
            cmd = input("\nEnter command:\n1. Generate token\n2. Simulate QR scan\n3. Exit\n> ")
            
            if cmd == '1':
                # 生成新 token（模拟客户端行为）
                token = '14cd4bc4-66c6-4d31-b0d0-794b6c999769'#str(uuid.uuid4())
                user_id = f"user_{uuid.uuid4().hex[:8]}"
                tokens[token] = {'status': 'pending', 'user_id': user_id}
                
                print(f"\nGenerated token: {token}")
                print(f"User ID: {user_id}")
                print(f"QR Code URL: http://localhost:8080/qr_page?token={token}")
                
                # 启动模拟扫描线程
                threading.Thread(target=simulate_qr_scan, args=(token,), daemon=True).start()
            
            elif cmd == '2' and tokens:
                token = list(tokens.keys())[-1]  # 使用最后一个生成的 token
                threading.Thread(target=simulate_qr_scan, args=(token,), daemon=True).start()
                print(f"Simulating QR scan for token: {token}")
            
            elif cmd == '3':
                break
    
    finally:
        loop.call_soon_threadsafe(loop.stop)
        print("Servers stopped")