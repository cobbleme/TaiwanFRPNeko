import logging
import os
from pathlib import Path
from datetime import datetime

class BotLogger:
    def __init__(self, log_dir="data/logs"):
        self.log_dir = log_dir
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 設定日誌格式
        self.formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 創建主日誌
        self.main_logger = self._setup_logger(
            'bot',
            os.path.join(log_dir, 'bot.log')
        )
        
        # 創建API日誌
        self.api_logger = self._setup_logger(
            'api',
            os.path.join(log_dir, 'api.log')
        )
        
        # 創建帳號日誌
        self.account_logger = self._setup_logger(
            'account',
            os.path.join(log_dir, 'account.log')
        )
        
        # 創建錯誤日誌
        self.error_logger = self._setup_logger(
            'error',
            os.path.join(log_dir, 'error.log'),
            level=logging.ERROR
        )
    
    def _setup_logger(self, name, log_file, level=logging.INFO):
        """設置日誌記錄器"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 文件處理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(self.formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_bind_attempt(self, discord_id, username, success, reason=None):
        """記錄帳號綁定嘗試"""
        if success:
            self.account_logger.info(f"✅ Discord用戶 {discord_id} 成功綁定帳號 {username}")
        else:
            self.account_logger.warning(
                f"❌ Discord用戶 {discord_id} 綁定失敗 - {reason}"
            )
            if reason:
                self.error_logger.warning(f"綁定失敗: {reason}")
    
    def log_api_call(self, method, endpoint, success, response_time=None, error=None):
        """記錄API調用"""
        status = "✅" if success else "❌"
        msg = f"{status} {method} {endpoint}"
        if response_time:
            msg += f" ({response_time:.2f}s)"
        if error:
            msg += f" - {error}"
            self.error_logger.error(msg)
        else:
            self.api_logger.info(msg)
    
    def log_unbind(self, discord_id):
        """記錄解綁操作"""
        self.account_logger.info(f"🔓 Discord用戶 {discord_id} 已解綁")
    
    def log_command(self, discord_id, command, args=""):
        """記錄命令執行"""
        self.main_logger.info(f"💬 {discord_id} 執行: /{command} {args}".strip())
    
    def log_tunnel_check(self, discord_id, tunnel_name, status):
        """記錄隧道檢查"""
        self.main_logger.info(
            f"🔍 {discord_id} 檢查隧道 '{tunnel_name}': {status}"
        )
    
    def log_error(self, title, error_msg, discord_id=None):
        """記錄錯誤"""
        if discord_id:
            self.error_logger.error(f"[{discord_id}] {title}: {error_msg}")
        else:
            self.error_logger.error(f"{title}: {error_msg}")

# 全局實例
logger = BotLogger()
