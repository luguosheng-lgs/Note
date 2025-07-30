//创建websocket服务器
// 安装依赖：先运行 npm install ws
const WebSocket = require('ws');

// 创建 WebSocket 服务器，监听 8080 端口
const wss = new WebSocket.Server({ port: 8080 });

// 监听客户端连接
wss.on('connection', (ws) => {
  console.log('新的客户端已连接');

  // 向客户端发送欢迎消息
  ws.send('欢迎连接到WebSocket服务器！');

  // 监听客户端消息
  ws.on('message', (message) => {
    console.log(`收到消息: ${message}`);
    
    // 将消息广播给所有客户端
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(`用户说: ${message}`);
      }
    });
  });

  // 监听连接关闭
  ws.on('close', () => {
    console.log('客户端已断开连接');
  });
});

console.log('WebSocket 服务器已启动，监听端口 8080');