# 一个基于Notion通信的C2简单实现

这是一个基于Notion和WebSocket的C2（Command and Control）通信系统，包含服务端、控制端和被控端三个组件。

## 功能特点

- 使用Notion公共页面作为命令下发通道
- WebSocket实时通信
- AES-CBC加密和Base64编码
- 支持的功能：
  - 命令执行
  - 文件上传/下载
  - 屏幕截图（Windows系统）
  - 键盘记录

## 系统要求

- Python 3.7+
- Windows操作系统（被控端）
- 网络连接

## 安装

1. 克隆仓库：
```bash
git clone <repository_url>
cd c2-system
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 创建配置文件：
创建一个`.env`文件，包含以下配置：
```
C2_SERVER_HOST=0.0.0.0
C2_SERVER_PORT=8765
NOTION_PAGE_ID=your-notion-page-id
AGENT_CHECK_INTERVAL=60
ENCRYPTION_KEY=your-encryption-key
```

## 使用方法

1. 启动服务端：
```bash
python server.py
```

2. 启动控制端：
```bash
python controller.py
```

3. 在目标系统上启动被控端：
```bash
python agent.py
```

## 控制端命令

- `target <client_id>` - 选择目标客户端
- `shell <command>` - 执行shell命令
- `screenshot` - 获取屏幕截图
- `keylogger start/stop` - 启动/停止键盘记录
- `upload <local_path> <remote_path>` - 上传文件
- `download <remote_path>` - 下载文件
- `exit` - 退出控制端

## Notion页面设置

1. 创建一个公共的Notion页面
2. 将页面ID配置到`.env`文件中
3. 在页面中使用特定格式添加命令

## 安全注意事项

- 请勿在生产环境中使用默认的加密密钥
- 确保Notion页面的访问权限设置正确
- 定期更改加密密钥和通信端口

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT License 
