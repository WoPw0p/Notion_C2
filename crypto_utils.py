import base64
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class CryptoUtils:
    def __init__(self, key=None):
        # 如果没有提供密钥，生成一个32字节的随机密钥
        self.key = key if key else os.urandom(32)
        self.iv = os.urandom(16)  # AES-CBC需要一个16字节的IV

    def encrypt(self, data: str) -> str:
        # 将字符串转换为字节
        data_bytes = data.encode('utf-8')
        
        # 添加PKCS7填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data_bytes) + padder.finalize()
        
        # 创建加密器
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 将IV和加密数据组合并进行Base64编码
        combined = self.iv + encrypted_data
        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # 分离IV和加密数据
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # 创建解密器
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # 解密数据
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted.decode('utf-8') 