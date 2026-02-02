from cryptography.fernet import Fernet
import json
import os
from pathlib import Path

class PasswordManager:
    def __init__(self, key_file="data/twfrp.key", db_file="data/users.json"):
        self.key_file = key_file
        self.db_file = db_file
        self._ensure_files()
    
    def _ensure_files(self):
        """確保密鑰和資料庫文件存在"""
        Path("data").mkdir(exist_ok=True)
        
        # 生成密鑰（第一次運行）
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            print(f"✅ 密鑰已生成: {self.key_file}")
            print("⚠️  請妥善保管此文件，丟失將無法解密密碼！")
        
        # 初始化資料庫
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({}, f)
    
    def _get_cipher(self):
        """獲取加密對象"""
        with open(self.key_file, "rb") as f:
            key = f.read()
        return Fernet(key)
    
    def encrypt_password(self, password: str) -> str:
        """加密密碼"""
        cipher = self._get_cipher()
        encrypted = cipher.encrypt(password.encode())
        return encrypted.decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """解密密碼"""
        try:
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"❌ 密碼解密失敗: {e}")
    
    def save_credentials(self, discord_id: int, username: str, password: str):
        """保存加密的帳號密碼"""
        encrypted_pass = self.encrypt_password(password)
        
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
        data[str(discord_id)] = {
            "username": username,
            "password": encrypted_pass
        }
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ 已保存用戶 {discord_id} 的認證信息")
    
    def get_credentials(self, discord_id: int) -> dict:
        """獲取解密後的帳號密碼"""
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
        if str(discord_id) not in data:
            return None
        
        user_data = data[str(discord_id)]
        return {
            "username": user_data["username"],
            "password": self.decrypt_password(user_data["password"])
        }
    
    def remove_credentials(self, discord_id: int):
        """刪除用戶認證信息"""
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
        if str(discord_id) in data:
            del data[str(discord_id)]
            with open(self.db_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"✅ 已刪除用戶 {discord_id} 的認證信息")

# 全局實例
pwd_manager = PasswordManager()