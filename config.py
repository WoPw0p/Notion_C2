import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 服务器配置
SERVER_HOST = os.getenv('C2_SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('C2_SERVER_PORT', '8765'))
SERVER_URL = f"ws://{SERVER_HOST}:{SERVER_PORT}"

# Notion配置
NOTION_PAGE_ID = os.getenv('NOTION_PAGE_ID', '')
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')

# 加密配置
# 32字节的密钥用于AES-256
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', os.urandom(32).hex())

# 被控端配置
AGENT_CHECK_INTERVAL = int(os.getenv('AGENT_CHECK_INTERVAL', '60'))  # 秒
AGENT_RETRY_INTERVAL = int(os.getenv('AGENT_RETRY_INTERVAL', '10'))  # 秒

# 文件操作配置
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '104857600'))  # 100MB
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', 'downloads')
SCREENSHOT_PATH = os.getenv('SCREENSHOT_PATH', 'screenshots')

# 创建必要的目录
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(SCREENSHOT_PATH, exist_ok=True)

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'c2.log')

# WebSocket配置
WS_PING_INTERVAL = int(os.getenv('WS_PING_INTERVAL', '30'))  # 秒
WS_PING_TIMEOUT = int(os.getenv('WS_PING_TIMEOUT', '10'))  # 秒
WS_MAX_SIZE = int(os.getenv('WS_MAX_SIZE', '10485760'))  # 10MB

# 安全配置
MAX_FAILED_ATTEMPTS = int(os.getenv('MAX_FAILED_ATTEMPTS', '3'))
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1小时

# 示例.env文件内容（需要创建.env文件并填入实际值）
"""
# Server Configuration
C2_SERVER_HOST=0.0.0.0
C2_SERVER_PORT=8765

# Notion Configuration
NOTION_PAGE_ID=your-notion-page-id
NOTION_API_KEY=your-notion-api-key

# Encryption Configuration
ENCRYPTION_KEY=your-32-byte-encryption-key

# Agent Configuration
AGENT_CHECK_INTERVAL=60
AGENT_RETRY_INTERVAL=10

# File Operation Configuration
MAX_UPLOAD_SIZE=104857600
DOWNLOAD_PATH=downloads
SCREENSHOT_PATH=screenshots

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=c2.log

# WebSocket Configuration
WS_PING_INTERVAL=30
WS_PING_TIMEOUT=10
WS_MAX_SIZE=10485760

# Security Configuration
MAX_FAILED_ATTEMPTS=3
SESSION_TIMEOUT=3600
""" 